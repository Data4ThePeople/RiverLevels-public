"""Australia Bureau of Meteorology (BoM) Water Data Online, KiWIS API: daily
mean water course level for four Murray-Darling gauges.

Series: DMQaQc.Merged.DailyMean.24HR for parameter "Water Course Level".
Quality codes come from the KiWIS getQualityCodes request and BoM's Water Data
Online quality code table:
  10 A  best available            -> measured
  90 B  compromised               -> measured (counted in notes)
  110 C estimate                  -> estimated
  140 E unknown quality           -> measured (counted in notes, share per decade)
  210 F missing or incorrect      -> dropped (counted in notes)
  -1    no value                  -> dropped
"""
from __future__ import annotations

import json

import pandas as pd

from sa_asia_common import RAW, fetch_to, parse_args, session, share_by_decade, write_gauge

API = "https://www.bom.gov.au/waterdata/services"
BASE = dict(service="kisters", type="queryServices", datasource="0", format="json")
RAWDIR = RAW / "bom"
GAUGES = [
    # id, station_no, display name
    ("murray-albury", "409001", "Albury"),
    ("murray-swanhill", "409204", "Swan Hill"),
    ("murray-euston", "414203", "Euston"),
    ("darling-bourke", "425003", "Bourke"),
]
TS_NAME = "DMQaQc.Merged.DailyMean.24HR"
# Euston values sit near 42-52 m, close to Euston Weir's 47.6 m full supply level (MDBA), so they are
# water surface elevations, not local gauge heights. BoM does not name the datum.
DATUM = {"414203": "m, water surface elevation (values near the 47.6 m full supply level of Euston Weir; "
                   "most likely m above the Australian Height Datum, but BoM does not say)"}
QMAP = {10: "measured", 90: "measured", 110: "estimated", 140: "measured"}
LICENSE = ("Creative Commons Attribution 4.0 (CC BY 4.0), per BoM Water Data Online copyright notice. "
           "Credit: Bureau of Meteorology, Water Data Online, with data supplied by the station owner "
           "(see notes).")


def main():
    args = parse_args(__doc__)
    s = session()
    qc = fetch_to(s, RAWDIR / "quality_codes.json", API, args.refresh, params=dict(BASE, request="getQualityCodes"))
    qcodes = {q["key"]: (q["code"], q["description"]) for q in json.loads(qc.read_text())}
    for gid, st, name in GAUGES:
        lst = fetch_to(s, RAWDIR / f"tslist_{st}.json", API, args.refresh, params=dict(
            BASE, request="getTimeseriesList", station_no=st, parametertype_name="Water Course Level",
            ts_name=TS_NAME, returnfields="station_no,station_name,station_latitude,station_longitude,"
                                          "station_id,ts_id,ts_name,ts_unitsymbol,coverage"))
        hdr, *rows = json.loads(lst.read_text())
        rows = [dict(zip(hdr, r)) for r in rows if dict(zip(hdr, r))["ts_name"] == TS_NAME]
        if len(rows) != 1:
            raise ValueError(f"{gid}: expected one {TS_NAME} series, got {rows}")
        ts = rows[0]
        sl = fetch_to(s, RAWDIR / f"station_{st}.json", API, args.refresh, params=dict(
            BASE, request="getStationList", station_no=st,
            returnfields="station_no,station_name,station_id,station_latitude,station_longitude,ca_sta"))
        shdr, *srows = json.loads(sl.read_text())
        sta = [dict(zip(shdr, r)) for r in srows if dict(zip(shdr, r))["station_id"] == ts["station_id"]][0]
        vp = fetch_to(s, RAWDIR / f"values_{ts['ts_id']}.json", API, args.refresh, params=dict(
            BASE, request="getTimeseriesValues", ts_id=ts["ts_id"], **{"from": "1800-01-01"},
            to="2100-01-01", returnfields="Timestamp,Value,Quality Code"), pause=2.0, timeout=300)
        v = json.loads(vp.read_text())[0]
        d = pd.DataFrame(v["data"], columns=v["columns"].split(","))
        d["date"] = pd.to_datetime(d["Timestamp"].str[:10])
        n_all = len(d)
        d = d[d["Value"].notna()]
        code = d["Quality Code"].astype(int)
        n_f = int((code == 210).sum())
        other = sorted(set(code) - set(QMAP) - {210})
        if other:
            raise ValueError(f"{gid}: unmapped quality codes {other}")
        keep = code != 210
        d, code = d[keep].copy(), code[keep]
        d["quality"] = code.map(QMAP)
        # Code E (140) covers the once-daily NSW record before 1991. From 1991 on it
        # marks recent unchecked days, so it counts as provisional.
        late_e = (code == 140) & (d["date"] >= "1991-01-01")
        d.loc[late_e, "quality"] = "provisional"
        d = d.rename(columns={"Value": "level"})
        counts = code.value_counts().sort_index()
        e_dec = share_by_decade(d["date"], code == 140)
        b_dec = share_by_decade(d["date"], code == 90)
        notes = [
            f"BoM series {TS_NAME}, ts_id {ts['ts_id']}, station_id {ts['station_id']} "
            f"(station {ts['station_no']} {ts['station_name']}). Data owner: {sta.get('DATA_OWNER_NAME')}.",
            "Daily mean of the merged quality-controlled level record, aggregated by BoM to a 24-hour "
            "mean. The API does not say how many readings fed each early-year mean; where only one "
            "staff reading a day was taken, the 'mean' is that one reading.",
            f"Quality codes ({ {k: qcodes.get(k, ('?', '?'))[0] + ' ' + qcodes.get(k, ('?', '?'))[1] for k in counts.index} }): "
            f"counts {counts.to_dict()}. Mapping: A (10) and B (90, compromised) -> measured; "
            "C (110, estimate) -> estimated; E (140, unknown quality) -> measured before 1991 and "
            f"provisional from 1991 on ({int(late_e.sum())} days), where it marks recent unchecked readings.",
            f"Unknown-quality code E (140) share of days by decade: {e_dec or 'none'}.",
            f"Compromised code B (90) share of days by decade: {b_dec or 'none'}.",
            f"{n_all - len(d) - n_f} empty timestamps (code -1) and {n_f} values coded F (210, missing or "
            "incorrect) were dropped.",
        ]
        meta = {
            "id": gid, "river": "murray-darling", "name": name, "country": "Australia",
            "lat": float(sta["station_latitude"]), "lon": float(sta["station_longitude"]), "kind": "river",
            "source": "Bureau of Meteorology, Water Data Online (KiWIS API)",
            "source_url": f"http://www.bom.gov.au/waterdata/ (station {st}); {API}",
            "station_code": st, "unit": "m",
            "datum": DATUM.get(st, "m above the local gauge zero (local gauge height; zero elevation "
                                   "not given by the API)"),
            "daily_stat": "mean", "license": LICENSE, "notes": notes,
        }
        write_gauge(d[["date", "level", "quality"]], meta, decimals=3)


if __name__ == "__main__":
    main()
