"""Bureau of Reclamation RISE API: daily total release (cfs) from Glen Canyon
Dam (Lake Powell, item 4315) and Hoover Dam (Lake Mead, item 6125). See
scripts/fetch/FLOW.md.

Raw cache: data/raw/flow_rise/<gauge_id>/
  catalog_item.json         RISE catalog item (title, units, disclaimer)
  location.json             RISE location (coordinates)
  results_<decade>_p<N>.json   result pages, one decade per request window
"""
from __future__ import annotations

import datetime as dt
import json

import pandas as pd

from flow_common import write_flow
from na_common import RAW, need_cache, parse_args, polite_get, session

API = "https://data.usbr.gov/rise/api"
HDR = {"Accept": "application/vnd.api+json"}
CACHE = RAW / "flow_rise"
PAGE = 10000
TODAY = dt.date.today()

RELEASE = ("This is water released through the dam (turbines, plus bypass tubes and spillways "
           "when used), not river flow at a gauge. Dam operators set it under the river's "
           "operating rules, so it reflects management decisions as much as weather "
           "(Bureau of Reclamation).")

GAUGES = [
    dict(id="colorado-lake-powell", river="colorado", name="Lake Powell (Glen Canyon Dam)",
         item=4315, credit="U.S. Bureau of Reclamation, Upper Colorado Basin Region", notes=[
             RELEASE,
             "Glen Canyon Dam closed its diversion tunnels in March 1963, so the release record "
             "starts while the lake was filling (Bureau of Reclamation).",
             "Reclamation reports release as a daily average computed from powerplant and outlet "
             "records; RISE does not say how it is measured. USGS gauge 09380000 at Lees Ferry, "
             "below the dam, measures the released water independently (Bureau of Reclamation, "
             "USGS).",
         ]),
    dict(id="colorado-lake-mead", river="colorado", name="Lake Mead (Hoover Dam)",
         item=6125, credit="U.S. Bureau of Reclamation, Lower Colorado Basin Region", notes=[
             RELEASE,
             "The release record starts in April 1934, before Hoover Dam began storing water in "
             "February 1935 (Bureau of Reclamation).",
             "RISE does not say how release is measured; it is reported as a daily average "
             "(Bureau of Reclamation).",
         ]),
]


def water_year_start(day: dt.date) -> dt.date:
    return dt.date(day.year if day.month >= 10 else day.year - 1, 10, 1)


def save(path, text: str) -> None:
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(text)
    part.rename(path)


def download(g: dict, sess) -> None:
    d = CACHE / g["id"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']}")
    r = polite_get(sess, f"{API}/catalog-item/{g['item']}", headers=HDR)
    save(d / "catalog_item.json", r.text)
    item = r.json()
    rec = item["data"]["relationships"]["catalogRecord"]["data"]["id"]
    crec = polite_get(sess, f"https://data.usbr.gov{rec}", headers=HDR).json()
    loc_id = crec["data"]["relationships"]["location"]["data"]["id"]
    r = polite_get(sess, f"https://data.usbr.gov{loc_id}", headers=HDR)
    save(d / "location.json", r.text)
    first_year = int(item["data"]["attributes"]["temporalStartDate"][:4])
    for old in d.glob("results_*.json"):
        old.unlink()
    # Without a date filter the full request times out, so ask one decade at a time.
    for dec in range(first_year // 10 * 10, TODAY.year // 10 * 10 + 10, 10):
        page = 1
        while True:
            r = polite_get(sess, f"{API}/result", headers=HDR, params={
                "itemId": g["item"], "itemsPerPage": PAGE, "page": page,
                "dateTime[after]": f"{dec - 1}-12-31", "dateTime[before]": f"{dec + 10}-01-02"})
            save(d / f"results_{dec}_p{page}.json", r.text)
            j = r.json()
            total = j["meta"]["totalItems"]
            print(f"    {dec}s page {page}: {len(j['data'])} of {total}")
            if page * PAGE >= total:
                break
            page += 1


def build(g: dict) -> None:
    d = CACHE / g["id"]
    need_cache(d / "catalog_item.json")
    item = json.loads((d / "catalog_item.json").read_text())["data"]["attributes"]
    loc = json.loads((d / "location.json").read_text())["data"]["attributes"]
    if item.get("parameterUnit") != "cfs":
        raise SystemExit(f"{g['id']}: unexpected unit {item.get('parameterUnit')}")
    rows = []
    for f in sorted(d.glob("results_*_p*.json")):
        rows += [x["attributes"] for x in json.loads(f.read_text())["data"]]
    if not rows:
        need_cache(d / "results_XXXX_p1.json")
    df = pd.DataFrame(rows).drop_duplicates("_id")  # decade windows overlap by a day
    rtype = df["resultAttributes"].map(lambda a: (a or {}).get("resultType"))
    types = rtype.value_counts().to_dict()
    df = df[rtype == "observed"]
    n_null = int(df["result"].isna().sum())
    df = df[df["result"].notna()]
    bad = (df["result"] < 0) | (df["result"] >= 999999)
    n_bad = int(bad.sum())
    df = df[~bad]
    # RISE stamps daily values at 07:00 UTC, which is midnight Mountain Standard Time.
    t = pd.to_datetime(df["dateTime"], utc=True) - pd.Timedelta(hours=7)
    df["date"] = t.dt.strftime("%Y-%m-%d")
    hours = df["dateTime"].str[11:16].value_counts().to_dict()
    if df["date"].duplicated().any():
        raise SystemExit(f"{g['id']}: duplicate dates {df.loc[df['date'].duplicated(), 'date'].head().tolist()}")
    df["flow"] = df["result"].astype(float)
    n_zero = int((df["flow"] == 0).sum())
    # Same rule as the level series (rise.py): no per-value approval flag, so the
    # current water year, and the previous one until six months after it ends,
    # are provisional; earlier years measured.
    last = pd.to_datetime(df["date"]).max().date()
    wy = water_year_start(last - dt.timedelta(days=183)).isoformat()
    df["quality"] = ["provisional" if s >= wy else "measured" for s in df["date"]]
    notes = list(g["notes"]) + [
        f"RISE disclaimer: \"{item.get('disclaimer')}\" No value carries its own approval flag, "
        f"so values from {wy} on are marked provisional and earlier values measured. This is "
        "our rule, the same as for the lake level, not a Reclamation flag (Bureau of Reclamation).",
        f"Each value is the daily {item.get('parameterTransformation')} release, stamped at UTC "
        f"{hours}; dates are Mountain Standard Time days (Bureau of Reclamation).",
        f"RISE result types: {types}; only observed values kept. Dropped {n_null} empty and "
        f"{n_bad} negative or fill values; {n_zero} days with zero release are kept "
        "(Bureau of Reclamation).",
    ]
    lon, lat = loc["locationCoordinates"]["coordinates"]
    meta = {
        "id": g["id"], "river": g["river"], "name": g["name"],
        "station_name": item["itemTitle"],
        "station_code": f"RISE item {g['item']} ({item.get('sourceCode')} site "
                        f"{item.get('locationSourceCode')})",
        "country": "United States", "lat": float(lat), "lon": float(lon),
        "same_station": True, "offset_note": "",
        "kind": "dam release", "unit": "cfs", "daily_stat": "mean",
        "source": "U.S. Bureau of Reclamation, RISE (Reclamation Information Sharing Environment)",
        "source_url": f"{API}/result",
        "license": "Public domain (U.S. federal government work)",
        "credit": g["credit"],
        "flag_rule": f"RISE has no per-value flags; values from {wy} (the current water year, "
                     "plus the previous one until six months after it ends) are provisional, "
                     "earlier values measured.",
        "notes": notes,
    }
    write_flow(df[["date", "flow", "quality"]], meta)


def main() -> None:
    args = parse_args(__doc__)
    gauges = [g for g in GAUGES if not args.only or g["id"] in args.only]
    if args.refresh:
        sess = session()
        for g in gauges:
            download(g, sess)
    for g in gauges:
        build(g)


if __name__ == "__main__":
    main()
