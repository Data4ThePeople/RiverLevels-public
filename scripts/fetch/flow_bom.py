"""Australia Bureau of Meteorology (BoM) Water Data Online, KiWIS API: daily
mean water course discharge (m3/s) for four Murray-Darling gauges. Albury's own
discharge record stops in 1952, so its flow comes from Doctors Point (409017),
4 km downstream.

Series: DMQaQc.Merged.DailyMean.24HR for parameter "Water Course Discharge".
Quality codes as in bom.py:
  10 A  best available            -> measured
  90 B  compromised               -> measured (counted in notes)
  110 C estimate                  -> estimated
  140 E unknown quality           -> measured before 1991, provisional from 1991 on
  210 F missing or incorrect      -> dropped (counted in notes)
  -1    no value                  -> dropped
Contract: scripts/fetch/FLOW.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flow_common import write_flow  # noqa: E402
from sa_asia_common import RAW, fetch_to, parse_args, session, share_by_decade  # noqa: E402

API = "https://www.bom.gov.au/waterdata/services"
BASE = dict(service="kisters", type="queryServices", datasource="0", format="json")
RAWDIR = RAW / "flow_bom"
TS_NAME = "DMQaQc.Merged.DailyMean.24HR"
PARAM = "Water Course Discharge"
QMAP = {10: "measured", 90: "measured", 110: "estimated", 140: "measured"}
RATING = ("BoM publishes discharge that the station owner computes from the water level through a rating "
          "curve, checked by field flow measurements (Bureau of Meteorology).")
GAUGES = [
    # id, display name, flow station_no, expected ts_id, offset note, gauge-specific notes
    ("murray-albury", "Albury", "409017", "184020010", "Doctors Point, 4 km downstream", [
        "Discharge at the Albury gauge (409001) stops on March 16, 1952, so this series is the Murray at "
        "Doctors Point (409017), about 4 km downstream; the two are not joined (Bureau of Meteorology).",
    ]),
    ("murray-swanhill", "Swan Hill", "409204", "286638010", "", []),
    ("murray-euston", "Euston", "414203", "286878010", "", []),
    ("darling-bourke", "Bourke", "425003", "169509010", "", []),
]
CHUNK_FROM, CHUNK_TO = 1890, 2030
LICENSE = "CC BY 4.0 (BoM Water Data Online copyright notice)"


def main():
    args = parse_args(__doc__)
    s = session()
    qc = fetch_to(s, RAWDIR / "quality_codes.json", API, args.refresh, params=dict(BASE, request="getQualityCodes"))
    qcodes = {q["key"]: (q["code"], q["description"]) for q in json.loads(qc.read_text())}
    for gid, name, st, want_ts, offset, extra in GAUGES:
        lst = fetch_to(s, RAWDIR / f"tslist_{st}.json", API, args.refresh, params=dict(
            BASE, request="getTimeseriesList", station_no=st, parametertype_name=PARAM,
            ts_name=TS_NAME, returnfields="station_no,station_name,station_latitude,station_longitude,"
                                          "station_id,ts_id,ts_name,ts_unitsymbol,coverage"))
        hdr, *rows = json.loads(lst.read_text())
        rows = [dict(zip(hdr, r)) for r in rows if dict(zip(hdr, r))["ts_name"] == TS_NAME]
        if len(rows) != 1:
            raise ValueError(f"{gid}: expected one {TS_NAME} series, got {rows}")
        ts = rows[0]
        if ts["ts_id"] != want_ts:
            raise ValueError(f"{gid}: ts_id {ts['ts_id']} differs from the assigned {want_ts}")
        if ts["ts_unitsymbol"] != "cumec":
            raise ValueError(f"{gid}: unit {ts['ts_unitsymbol']}")
        sl = fetch_to(s, RAWDIR / f"station_{st}.json", API, args.refresh, params=dict(
            BASE, request="getStationList", station_no=st,
            returnfields="station_no,station_name,station_id,station_latitude,station_longitude,ca_sta"))
        shdr, *srows = json.loads(sl.read_text())
        sta = [dict(zip(shdr, r)) for r in srows if dict(zip(shdr, r))["station_id"] == ts["station_id"]][0]
        # the full record in one request times out (504), so ask for ten years at a time
        parts = []
        for y0 in range(CHUNK_FROM, CHUNK_TO, 10):
            vp = fetch_to(s, RAWDIR / f"values_{ts['ts_id']}_{y0}.json", API, args.refresh, params=dict(
                BASE, request="getTimeseriesValues", ts_id=ts["ts_id"], **{"from": f"{y0}-01-01T00:00:00"},
                to=f"{y0 + 9}-12-31T23:59:59", returnfields="Timestamp,Value,Quality Code"),
                pause=2.0, timeout=300)
            v = json.loads(vp.read_text())[0]
            parts.append(pd.DataFrame(v["data"], columns=v["columns"].split(",")))
        d = pd.concat(parts, ignore_index=True)
        if d["Timestamp"].duplicated().any():
            raise ValueError(f"{gid}: chunk boundaries returned the same timestamp twice")
        d["date"] = pd.to_datetime(d["Timestamp"].str[:10])
        n_all = len(d)
        d = d[d["Value"].notna()]
        n_empty = n_all - len(d)
        code = d["Quality Code"].astype(int)
        other = sorted(set(code) - set(QMAP) - {210})
        if other:
            raise ValueError(f"{gid}: unmapped quality codes {other}")
        n_f = int((code == 210).sum())
        neg = d["Value"].astype(float) < 0
        n_neg = int((neg & (code != 210)).sum())
        keep = (code != 210) & ~neg
        d, code = d[keep].copy(), code[keep]
        d["quality"] = code.map(QMAP)
        late_e = (code == 140) & (d["date"] >= "1991-01-01")
        d.loc[late_e, "quality"] = "provisional"
        d = d.rename(columns={"Value": "flow"})
        counts = code.value_counts().sort_index()
        e_dec = share_by_decade(d["date"], code == 140)
        b_dec = share_by_decade(d["date"], code == 90)
        owner = sta.get("DATA_OWNER_NAME") or "the station owner"
        notes = [RATING] + extra + [
            f"BoM series {TS_NAME}, ts_id {ts['ts_id']}, station {ts['station_no']} {ts['station_name']}; "
            f"data owner {owner} (Bureau of Meteorology).",
            "Daily mean of the merged quality-controlled record, computed by BoM over 24 hours; the API does not "
            "say how many readings fed each early-year mean (Bureau of Meteorology).",
            "Quality codes ("
            + "; ".join(f"{k} {qcodes.get(k, ('?', '?'))[0]} {qcodes.get(k, ('?', '?'))[1]}" for k in counts.index)
            + f"): counts {counts.to_dict()}. A and B (compromised) are measured, C (estimate) estimated, and E "
            f"(unknown quality) measured before 1991 and provisional from 1991 on ({int(late_e.sum())} days), "
            "where it marks recent unchecked values (Bureau of Meteorology).",
            f"Share of days with code E (unknown quality) by decade: {e_dec or 'none'}; with code B "
            f"(compromised): {b_dec or 'none'} (Bureau of Meteorology).",
            f"Dropped: {n_empty} empty timestamps, {n_f} values coded F (missing or incorrect) and {n_neg} "
            "negative values (Bureau of Meteorology).",
        ]
        meta = {
            "id": gid, "river": "murray-darling", "name": name,
            "station_name": ts["station_name"], "station_code": st,
            "country": "Australia",
            "lat": float(sta["station_latitude"]), "lon": float(sta["station_longitude"]),
            "same_station": offset == "", "offset_note": offset, "kind": "river flow", "unit": "m3/s",
            "daily_stat": "mean",
            "source": "Bureau of Meteorology, Water Data Online (KiWIS API)",
            "source_url": API, "license": LICENSE,
            "credit": f"Bureau of Meteorology; data from {owner}",
            "flag_rule": "BoM codes A and B are measured, C estimated, E measured before 1991 and provisional "
                         "from 1991 on; F dropped.",
            "notes": notes,
        }
        write_flow(d[["date", "flow", "quality"]], meta, decimals=3)


if __name__ == "__main__":
    main()
