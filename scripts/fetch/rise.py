"""Bureau of Reclamation RISE API: Lake Powell and Lake Mead daily elevation.

Raw cache: data/raw/rise/<gauge_id>/
  catalog_item.json   RISE catalog item (title, disclaimer, update date)
  location.json       RISE location (coordinates, vertical datum)
  results_p<N>.json   result pages (JSON:API, newest first)
"""
from __future__ import annotations

import datetime as dt
import json

import pandas as pd

from na_common import RAW, need_cache, parse_args, polite_get, session, write_gauge

API = "https://data.usbr.gov/rise/api"
HDR = {"Accept": "application/vnd.api+json"}
CACHE = RAW / "rise"
PAGE = 10000

GAUGES = [
    dict(id="colorado-lake-powell", river="colorado", name="Lake Powell (Glen Canyon Dam)",
         item=508, notes=[
             "Glen Canyon Dam closed its diversion tunnels in March 1963; the record starts "
             "1963-12-28 while the lake was filling. Full pool is 3,700 ft.",
         ]),
    dict(id="colorado-lake-mead", river="colorado", name="Lake Mead (Hoover Dam)",
         item=6123, notes=[
             "Hoover Dam began storing water on 1935-02-01; the record starts 1935-02-02 "
             "while the lake was filling. Full pool is 1,229 ft.",
         ]),
]


def water_year_start(today: dt.date) -> dt.date:
    return dt.date(today.year if today.month >= 10 else today.year - 1, 10, 1)


def download(g: dict, sess) -> None:
    d = CACHE / g["id"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']}")
    item = polite_get(sess, f"{API}/catalog-item/{g['item']}", headers=HDR).json()
    (d / "catalog_item.json").write_text(json.dumps(item, indent=1))
    rec = item["data"]["relationships"]["catalogRecord"]["data"]["id"]
    crec = polite_get(sess, f"https://data.usbr.gov{rec}", headers=HDR).json()
    loc_id = crec["data"]["relationships"]["location"]["data"]["id"]
    loc = polite_get(sess, f"https://data.usbr.gov{loc_id}", headers=HDR).json()
    (d / "location.json").write_text(json.dumps(loc, indent=1))
    for old in d.glob("results_p*.json"):
        old.unlink()
    page, total = 1, None
    while True:
        j = polite_get(sess, f"{API}/result", headers=HDR, params={
            "itemId": g["item"], "itemsPerPage": PAGE, "page": page}).json()
        (d / f"results_p{page}.json").write_text(json.dumps(j))
        total = j["meta"]["totalItems"]
        print(f"    page {page}: {len(j['data'])} of {total}")
        if page * PAGE >= total:
            break
        page += 1


def build(g: dict) -> None:
    d = CACHE / g["id"]
    need_cache(d / "catalog_item.json")
    item = json.loads((d / "catalog_item.json").read_text())["data"]["attributes"]
    loc = json.loads((d / "location.json").read_text())["data"]["attributes"]
    rows = []
    for f in sorted(d.glob("results_p*.json")):
        rows += [x["attributes"] for x in json.loads(f.read_text())["data"]]
    if not rows:
        need_cache(d / "results_p1.json")
    df = pd.DataFrame(rows)
    n_all = len(df)
    df = df.drop_duplicates("_id")  # paging can repeat a row if new data lands mid-download
    notes = list(g["notes"])
    if len(df) != n_all:
        notes.append(f"{n_all - len(df)} repeated result rows across pages removed.")
    types = df["resultAttributes"].map(lambda a: (a or {}).get("resultType")).value_counts().to_dict()
    statuses = df["status"].map(str).value_counts().to_dict()
    df = df[df["resultAttributes"].map(lambda a: (a or {}).get("resultType")) == "observed"]
    n_null = int(df["result"].isna().sum())
    df = df[df["result"].notna()]
    fills = (df["result"] <= 0) | (df["result"] >= 99999)
    n_fill = int(fills.sum())
    df = df[~fills]
    # RISE stamps daily values at 07:00 UTC, which is midnight Mountain Standard Time.
    t = pd.to_datetime(df["dateTime"], utc=True) - pd.Timedelta(hours=7)
    df["date"] = t.dt.strftime("%Y-%m-%d")
    hours = df["dateTime"].str[11:16].value_counts().to_dict()
    if df["date"].duplicated().any():
        raise ValueError(f"{g['id']}: duplicate dates {df.loc[df['date'].duplicated(), 'date'].head().tolist()}")
    df["level"] = df["result"].astype(float)
    # RISE has no per-value approval flag (status is empty) and its disclaimer calls all
    # data provisional unless noted. Reclamation reviews each water year (Oct to Sep) after
    # it ends, so the current water year, and the previous one until six months after it
    # ended, are marked provisional; earlier years measured.
    last = pd.to_datetime(df["date"]).max().date()
    wy = water_year_start(last - dt.timedelta(days=183))
    df["quality"] = ["provisional" if s >= wy.isoformat() else "measured" for s in df["date"]]
    upd = pd.to_datetime(df["updateDate"], utc=True)
    n_rev = int(((upd.notna()) & (pd.to_datetime(df["date"]) < pd.Timestamp(wy))).sum())
    notes += [
        f"RISE result types in the file: {types}; per-value status field: {statuses}. Only "
        "'observed' values kept.",
        f"RISE disclaimer: \"{item.get('disclaimer')}\" No value carries its own approval flag, "
        f"so values from {wy.isoformat()} on (the current water year, plus the previous one "
        "until six months after it ends) are marked provisional and earlier values measured. "
        "This is our rule, not a Reclamation flag.",
        f"{n_rev} of {len(df)} values before {wy.isoformat()} carry a RISE update date. That "
        "looks like bulk reloads, so RISE metadata cannot show which past values were revised.",
        f"Each value is the daily instantaneous elevation ({item.get('parameterTransformation')}, "
        f"{item.get('parameterTimestep')}), stamped at UTC times {hours}; dates are Mountain "
        "Standard Time days.",
        f"Dropped {n_fill} fill or impossible values and {n_null} null values.",
        f"RISE source system: {item.get('sourceCode')}; location vertical datum field: "
        f"{(loc.get('verticalDatum') or {}).get('_id')} (this refers to the location point, "
        "not to the elevation series).",
    ]
    lon, lat = loc["locationCoordinates"]["coordinates"]
    meta = dict(
        id=g["id"], river=g["river"], name=g["name"], country="United States",
        lat=lat, lon=lon, kind="reservoir",
        source="Bureau of Reclamation RISE",
        source_url=f"{API}/result?itemId={g['item']}",
        station_code=f"RISE item {g['item']} ({item.get('sourceCode')} site {item.get('locationSourceCode')})",
        unit="ft", datum="ft above sea level (the RISE series does not state a vertical datum; "
        f"the RISE location record lists {(loc.get('verticalDatum') or {}).get('_id')}; see "
        "measurement_history)",
        daily_stat="single reading", license="Public domain (US federal government work). "
        "Credit: U.S. Bureau of Reclamation.", notes=notes,
    )
    write_gauge(meta, df)


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
