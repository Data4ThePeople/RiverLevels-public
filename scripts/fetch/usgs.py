"""USGS National Water Information System: daily mean gage height (parameter
00065, statistic 00003) for Missouri River at Bismarck and Ohio River at
Cincinnati.

Raw cache: data/raw/usgs/<gauge_id>/
  site.rdb   USGS site record (coordinates, gauge datum)
  dv.rdb     daily values, full period of record
"""
from __future__ import annotations

import datetime as dt
import io

import pandas as pd

from na_common import RAW, need_cache, parse_args, polite_get, session, write_gauge

DV = "https://waterservices.usgs.gov/nwis/dv/"
SITE = "https://waterservices.usgs.gov/nwis/site/"
CACHE = RAW / "usgs"

GAUGES = [
    dict(id="missouri-bismarck", river="missouri", name="Bismarck", site="06342500", notes=[
        "DATUM BREAK: USGS Water-Supply Paper 1309 says the recorder datum was lowered "
        "4.24 ft to the present datum on 1934-10-01; before that (chain gauge to "
        "1928-10-17, then the recorder) readings were on a datum 4.24 ft higher. The "
        "daily values are not adjusted: yearly minimums jump from -2.9 ft in 1934 to "
        "+2.4 ft in 1935. Also April 1936 to September 1937 used mostly a wire-weight "
        "gauge at a datum 0.47 ft lower. Do not compare levels across 1934 without "
        "adding 4.24 ft to the earlier values (we leave them as published).",
        "Flow has been regulated by Garrison Dam (Lake Sakakawea), about 75 miles "
        "upstream, since November 1953. Lake Oahe begins downstream; whether its "
        "backwater reaches the gauge was not found in USGS reports.",
    ]),
    dict(id="ohio-cincinnati", river="ohio", name="Cincinnati", site="03255000", notes=[
        "USGS daily gage height starts 1987-10-01. The older Cincinnati stage record (from "
        "1858) is kept by the National Weather Service and the Army Corps and is not part "
        "of this file.",
        "Cincinnati lies in the pool of Markland Locks and Dam (operating from 1963, per "
        "the NWS), which holds normal pool at about 25.4 ft, so low-water stage is set by "
        "the dam for the whole of this file.",
    ]),
]


def read_rdb(text: str) -> pd.DataFrame:
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    df = pd.read_csv(io.StringIO("\n".join([lines[0]] + lines[2:])), sep="\t", dtype=str)
    return df


def download(g: dict, sess) -> None:
    d = CACHE / g["id"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']}")
    r = polite_get(sess, SITE, params={"format": "rdb", "sites": g["site"],
                                       "siteOutput": "expanded", "siteStatus": "all"})
    (d / "site.rdb").write_text(r.text)
    r = polite_get(sess, DV, params={
        "format": "rdb", "sites": g["site"], "parameterCd": "00065", "statCd": "00003",
        "startDT": "1800-01-01", "endDT": dt.date.today().isoformat(), "siteStatus": "all"})
    (d / "dv.rdb").write_text(r.text)


def build(g: dict) -> None:
    d = CACHE / g["id"]
    need_cache(d / "dv.rdb")
    site = read_rdb((d / "site.rdb").read_text()).iloc[0]
    raw = read_rdb((d / "dv.rdb").read_text())
    vcols = [c for c in raw.columns if c.endswith("_00065_00003")]
    notes = list(g["notes"])
    parts = []
    for vc in vcols:
        p = raw[["datetime", vc, vc + "_cd"]].dropna(subset=[vc])
        p.columns = ["date", "value", "cd"]
        p["ts_id"] = vc.split("_")[0]
        parts.append(p)
    df = pd.concat(parts, ignore_index=True)
    if len(vcols) > 1:
        notes.append(f"{len(vcols)} USGS time series in the file ({', '.join(vcols)}).")
    num = pd.to_numeric(df["value"], errors="coerce")
    nonnum = df.loc[num.isna(), "value"].value_counts().to_dict()
    df["level"] = num
    df = df[df["level"].notna()]
    fills = df["level"] <= -999
    n_fill = int(fills.sum())
    df = df[~fills]
    cd = df["cd"].fillna("")
    df["quality"] = "measured"
    df.loc[cd.str.startswith("P"), "quality"] = "provisional"
    df.loc[cd.str.contains("e"), "quality"] = "estimated"
    codes = cd.value_counts().to_dict()
    notes += [
        f"USGS approval codes in the file: {codes}. A (approved) -> measured, P (provisional) "
        "-> provisional, any code with 'e' (estimated by USGS) -> estimated, even if approved.",
        f"Non-numeric value codes skipped (equipment, ice and similar): {nonnum or 'none'}. "
        f"Dropped {n_fill} fill values.",
        "Daily mean of the gauge's readings for the day, as computed by USGS. In early years "
        "the 'daily mean' may rest on one or two staff-gauge readings a day; see "
        "measurement_history.",
        "Legacy waterservices.usgs.gov endpoint; USGS plans to retire it in favor of "
        "api.waterdata.usgs.gov, so this URL may need to change.",
    ]
    lat, lon = float(site["dec_lat_va"]), float(site["dec_long_va"])
    alt, datum = site.get("alt_va", "").strip(), site.get("alt_datum_cd", "").strip()
    meta = dict(
        id=g["id"], river=g["river"], name=g["name"], country="United States",
        lat=lat, lon=lon, kind="river", source="USGS NWIS daily values",
        source_url=f"https://waterdata.usgs.gov/monitoring-location/USGS-{g['site']}/",
        station_code=f"USGS {g['site']}", unit="ft",
        datum=f"ft above gauge datum ({alt} ft {datum})" if alt else "ft above gauge datum",
        daily_stat="mean",
        license="Public domain (US federal government work). Credit: U.S. Geological Survey.",
        notes=notes + [f"USGS station name: {site['station_nm']}."],
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
