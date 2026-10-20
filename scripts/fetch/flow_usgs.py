"""USGS NWIS daily mean discharge (parameter 00060, statistic 00003, cfs) for
the Mississippi, Ohio and Missouri gauges. See scripts/fetch/FLOW.md.

Raw cache: data/raw/flow_usgs/<site>/
  site.rdb   USGS site record (name, coordinates)
  dv.rdb     daily values, full period of record
"""
from __future__ import annotations

import datetime as dt
import io

import pandas as pd

from flow_common import write_flow
from na_common import RAW, need_cache, parse_args, polite_get, session

DV = "https://waterservices.usgs.gov/nwis/dv/"
SITE = "https://waterservices.usgs.gov/nwis/site/"
CACHE = RAW / "flow_usgs"

RATING = ("USGS computes daily discharge from the gauge's water level through a rating curve "
          "(stage-discharge relation), adjusted by shifts after each field measurement, and "
          "approves a year of data some months after it ends (USGS).")

GAUGES = [
    dict(id="mississippi-stlouis", river="mississippi", name="St. Louis", site="07010000",
         offset="", notes=[
             "How USGS built the earliest St. Louis flows (1861 to the 1930s) is not documented "
             "in the daily-values file; they rest on few field measurements (USGS).",
         ]),
    dict(id="mississippi-memphis", river="mississippi", name="Memphis", site="07032000",
         offset="", notes=[]),
    dict(id="mississippi-helena", river="mississippi", name="Helena", site="07047970",
         offset="", notes=[
             "USGS stopped publishing flow at Helena in 1977; this record ends then (USGS).",
         ]),
    dict(id="ohio-louisville", river="ohio", name="Louisville", site="03294500",
         offset="", notes=[]),
    dict(id="ohio-cairo", river="ohio", name="Cairo", site="03612600",
         offset="Olmsted, about 17 river miles upstream", notes=[
             "There is no USGS daily flow at Cairo, so this is the Ohio River at Olmsted, about "
             "17 river miles upstream, which starts in 2013 (USGS).",
         ]),
    dict(id="ohio-cincinnati", river="ohio", name="Cincinnati", site="03277200",
         offset="Markland Dam, about 61 river miles downstream", notes=[
             "USGS has only 15-minute flow at Cincinnati itself, from October 2024, so this is "
             "the Ohio River at Markland Dam, about 61 river miles downstream, from 1970 (USGS).",
             "Markland is just below a lock and dam; flow passing it is set partly by how the "
             "U.S. Army Corps of Engineers operates the dam (USGS, USACE).",
         ]),
    dict(id="missouri-bismarck", river="missouri", name="Bismarck", site="06342500",
         offset="", notes=[
             "River ice in winter changes the level for a given flow, so USGS estimates "
             "winter flow by other means; those days are marked estimated (USGS).",
             "Flow has been regulated by Garrison Dam, about 75 miles upstream, since "
             "November 1953 (USGS).",
         ]),
    dict(id="missouri-hermann", river="missouri", name="Hermann", site="06934500",
         offset="", notes=[]),
]


def read_rdb(text: str) -> pd.DataFrame:
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    return pd.read_csv(io.StringIO("\n".join([lines[0]] + lines[2:])), sep="\t", dtype=str)


def save(path, text: str) -> None:
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(text)
    part.rename(path)


def download(g: dict, sess) -> None:
    d = CACHE / g["site"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']} ({g['site']})")
    r = polite_get(sess, SITE, params={"format": "rdb", "sites": g["site"],
                                       "siteOutput": "expanded", "siteStatus": "all"})
    save(d / "site.rdb", r.text)
    r = polite_get(sess, DV, params={
        "format": "rdb", "sites": g["site"], "parameterCd": "00060", "statCd": "00003",
        "startDT": "1800-01-01", "endDT": dt.date.today().isoformat(), "siteStatus": "all"})
    save(d / "dv.rdb", r.text)


def quality(cd: str) -> str:
    if "e" in cd or "ice" in cd.lower():
        return "estimated"
    if cd.startswith("P"):
        return "provisional"
    if cd.startswith("A"):
        return "measured"
    raise SystemExit(f"unknown USGS code {cd!r}")


def build(g: dict) -> None:
    d = CACHE / g["site"]
    need_cache(d / "dv.rdb")
    site = read_rdb((d / "site.rdb").read_text()).iloc[0]
    raw = read_rdb((d / "dv.rdb").read_text())
    vcols = [c for c in raw.columns if c.endswith("_00060_00003")]
    if len(vcols) != 1:
        raise SystemExit(f"{g['id']}: expected one 00060 daily series, found {vcols}")
    vc = vcols[0]
    df = raw[["datetime", vc, vc + "_cd"]].copy()
    df.columns = ["date", "value", "cd"]
    df = df[df["value"].notna()]
    num = pd.to_numeric(df["value"], errors="coerce")
    nonnum = df.loc[num.isna(), "value"].value_counts().to_dict()
    df["flow"] = num
    df = df[df["flow"].notna()]
    neg = df["flow"] < 0
    n_neg = int(neg.sum())
    df = df[~neg]
    df["cd"] = df["cd"].fillna("")
    codes = df["cd"].value_counts().to_dict()
    df["quality"] = [quality(c) for c in df["cd"]]
    same = g["offset"] == ""
    notes = [RATING] + g["notes"] + [
        f"USGS approval codes: {codes}. A (approved) is measured, P (provisional) is "
        "provisional, and any code with e (estimated) or an ice code is estimated (USGS).",
        f"Skipped {sum(nonnum.values())} days with no number (codes such as Ice or Eqp: "
        f"{nonnum or 'none'}) and {n_neg} negative values (USGS).",
    ]
    meta = {
        "id": g["id"], "river": g["river"], "name": g["name"],
        "station_name": site["station_nm"].strip(), "station_code": f"USGS {g['site']}",
        "country": "United States",
        "lat": float(site["dec_lat_va"]), "lon": float(site["dec_long_va"]),
        "same_station": same, "offset_note": g["offset"],
        "kind": "river flow", "unit": "cfs", "daily_stat": "mean",
        "source": "U.S. Geological Survey, NWIS daily values (00060, statistic 00003)",
        "source_url": DV,
        "license": "Public domain (U.S. federal government work)",
        "credit": "U.S. Geological Survey",
        "flag_rule": "USGS code A is measured and P provisional; any code with e (estimated) "
                     "or an ice code is estimated.",
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
