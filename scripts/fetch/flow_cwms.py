"""USACE Corps Water Management System (CWMS) Data API: daily flow at
Vicksburg (MVK:Vicksburg.Flow.Inst.1Day.0.DCP-rev, cfs). See scripts/fetch/FLOW.md.

Raw cache: data/raw/flow_cwms/<gauge_id>/
  catalog.json        catalog entry with the series extents
  location.json       CWMS location record (coordinates)
  ts_<decade>.json    timeseries values, one file per decade
"""
from __future__ import annotations

import datetime as dt
import json
from zoneinfo import ZoneInfo

import pandas as pd

from cwms import cwms_quality
from flow_common import write_flow
from na_common import RAW, need_cache, parse_args, polite_get, session

API = "https://cwms-data.usace.army.mil/cwms-data"
HDR = {"Accept": "application/json;version=2"}
CACHE = RAW / "flow_cwms"
TODAY = dt.date.today()

GAUGES = [
    dict(id="mississippi-vicksburg", river="mississippi", name="Vicksburg", office="MVK",
         ts="Vicksburg.Flow.Inst.1Day.0.DCP-rev", loc_office="MVK", loc="Vicksburg", notes=[
             "Flow is computed from the Vicksburg water level through a rating curve; the "
             "Corps file does not describe the rating or how it changed (USACE).",
             "USGS lists at least six gauge sites at Vicksburg since 1871, and the file does "
             "not say which site each year uses (USGS).",
             "On the lower Mississippi the same level can carry different flows on a rising "
             "and a falling river, so single-rating flows are least certain in floods (USGS).",
         ]),
]


def save(path, text: str) -> None:
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(text)
    part.rename(path)


def download(g: dict, sess) -> None:
    d = CACHE / g["id"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']}")
    r = polite_get(sess, f"{API}/catalog/TIMESERIES", headers=HDR, params={
        "office": g["office"], "like": g["ts"].split(".")[0] + ".*",
        "page-size": 500, "include-extents": "true"})
    cat = [e for e in r.json().get("entries", []) if e["name"] == g["ts"]]
    if not cat:
        raise SystemExit(f"{g['ts']} not in CWMS catalog for {g['office']}")
    save(d / "catalog.json", json.dumps(cat[0], indent=1))
    first_year = int(cat[0]["extents"][0]["earliest-time"][:4])
    r = polite_get(sess, f"{API}/locations/{g['loc']}", headers=HDR,
                   params={"office": g["loc_office"], "unit": "EN"})
    save(d / "location.json", r.text)
    for old in d.glob("ts_*.json"):
        old.unlink()
    for dec in range(first_year // 10 * 10, TODAY.year // 10 * 10 + 10, 10):
        begin = f"{dec}-01-01T00:00:00Z"
        end = min(dt.date(dec + 10, 1, 1), TODAY + dt.timedelta(days=1)).isoformat() + "T00:00:00Z"
        pages, page = [], None
        while True:
            p = {"office": g["office"], "name": g["ts"], "begin": begin, "end": end,
                 "unit": "EN", "page-size": 10000}
            if page:
                p["page"] = page
            r = polite_get(sess, f"{API}/timeseries", headers=HDR, params=p)
            pages.append(r.json())
            page = pages[-1].get("next-page")
            if not page:
                break
        # one file per decade holding every raw page response, unparsed
        save(d / f"ts_{dec}.json", json.dumps(pages))
        print(f"    {dec}s: {sum(len(x.get('values') or []) for x in pages)} values")


def build(g: dict) -> None:
    d = CACHE / g["id"]
    need_cache(d / "location.json")
    loc = json.loads((d / "location.json").read_text())
    files = sorted(d.glob("ts_*.json"))
    if not files:
        need_cache(d / "ts_XXXX.json")
    rows, tzname, units = [], None, set()
    for f in files:
        for j in json.loads(f.read_text()):
            tzname = tzname or j.get("time-zone")
            if j.get("units"):
                units.add(j["units"])
            rows += j.get("values") or []
    if units != {"cfs"}:
        raise SystemExit(f"{g['id']}: unexpected units {units}")
    df = pd.DataFrame(rows, columns=["t", "v", "q"]).drop_duplicates()
    n_null = int(df["v"].isna().sum())
    df = df[df["v"].notna()]
    qc = {int(k): int(v) for k, v in df["q"].value_counts().items()}
    df["quality"] = [cwms_quality(q) for q in df["q"]]
    n_bad = int(df["quality"].isna().sum())
    df = df[df["quality"].notna()]
    neg = df["v"] < 0
    n_neg = int(neg.sum())
    df = df[~neg]
    tz = ZoneInfo(tzname or "US/Central")
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["date"] = ts.dt.tz_convert(tz).dt.strftime("%Y-%m-%d")
    utc_hours = ts.dt.strftime("%H:%M").value_counts().to_dict()
    if df["date"].duplicated().any():
        raise SystemExit(f"{g['id']}: two values on one local date "
                         f"{df.loc[df['date'].duplicated(), 'date'].head().tolist()}")
    df["flow"] = df["v"].astype(float)
    notes = list(g["notes"]) + [
        f"One reading a day, not a daily mean, stamped at UTC {utc_hours}; dates are days in the "
        f"file's time zone ({tzname}) (USACE).",
        f"CWMS quality codes: {qc}. Code 0 means the value was never screened, so the Corps file "
        "gives no approved or provisional status; those values are marked measured (USACE).",
        f"Dropped {n_null} empty values, {n_bad} flagged missing or rejected, and {n_neg} "
        "negative values (USACE).",
        "Flows are rounded to whole cfs: the API converts from stored metric values and returns "
        "float noise such as 545725.0657 (USACE).",
    ]
    meta = {
        "id": g["id"], "river": g["river"], "name": g["name"],
        "station_name": loc.get("public-name") or loc.get("name") or g["loc"],
        "station_code": f"{g['office']}:{g['ts']}", "country": "United States",
        "lat": round(float(loc["latitude"]), 6), "lon": round(float(loc["longitude"]), 6),
        "same_station": True, "offset_note": "",
        "kind": "river flow", "unit": "cfs", "daily_stat": "one reading",
        "source": "U.S. Army Corps of Engineers, CWMS Data API",
        "source_url": f"{API}/timeseries",
        "license": "Public domain (U.S. federal government work)",
        "credit": "U.S. Army Corps of Engineers, Vicksburg District",
        "flag_rule": "CWMS quality 0 (not screened, nearly every value) is measured; values "
                     "flagged as replaced are estimated; missing or rejected values are dropped.",
        "notes": notes,
    }
    write_flow(df[["date", "flow", "quality"]], meta, decimals=0)


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
