"""Mekong River Commission (MRC) time-series API: daily discharge (parameter
"Discharge", label "Calculated daily discharge", m3/s) at Chiang Saen, Pakse,
Kratie, and Nong Khai for Vientiane.

Series found in /ts/inventory/timeSeriesList, data from
/ts/data/timeSeriesCorrectedData/{uniqueId}. Early years have one point a day
(07:00 local); later years have two (07:00 and 19:00, or 00:00 and 12:00),
which we average. A point that repeats the previous point's value less than
12 hours later is a stored copy, not a new reading, and is dropped first
(Kratie stores the last days hourly this way).

Quality follows mrc.py (level): every series carries approval "Working" for
its whole length, which mrc.py does not use for quality, so days are
measured unless a Notes interval says filled/estimated/interpolated or a
grade 41 interval covers them (estimated). Kratie 1940, 1957 and 1975-1979 are
estimated for the same reason as the Kratie level series: the flow is
computed from that level.
"""
from __future__ import annotations

import json
import re

import pandas as pd

from flow_common import write_flow
from sa_asia_common import RAW, fetch_to, parse_args, session

API = "https://timeseries.api.mrcmekong.org/api/v1"
RAWDIR = RAW / "flow_mrc"
GAUGES = [
    # level id, display name, flow station code, offset note ("" = same station)
    ("mekong-chiangsaen", "Chiang Saen", "010501", ""),
    ("mekong-vientiane", "Vientiane", "012001", "Nong Khai, 13 km downstream"),
    ("mekong-pakse", "Pakse", "013901", ""),
    ("mekong-kratie", "Kratie", "014901", ""),
]
COUNTRY = {"TH": "Thailand", "LA": "Laos", "KH": "Cambodia", "VN": "Vietnam"}
FILL = re.compile(r"\bfill|estimat|interpolat", re.I)
EST_GRADES = {"41"}
LICENSE = ("Not open. MRC's Non-commercial Data Use Licence (version C, 2005) allows non-commercial use "
           "only and no redistribution of data or derived products without MRC's written permission "
           "(https://archive.iwlearn.org/mrcmekong.org/download/spatial/nonCommmercialDataUseLicense.pdf). "
           "Get MRC permission before publishing.")


def main():
    args = parse_args(__doc__)
    s = session()
    inv = json.loads(fetch_to(s, RAWDIR / "inventory.json", f"{API}/ts/inventory/timeSeriesList",
                              args.refresh).read_text())
    for gid, name, code, offset in GAUGES:
        cand = [x for x in inv if x["stationCode"] == code and x["parameter"] == "Discharge"
                and x["label"] == "Calculated daily discharge"]
        if len(cand) != 1:
            raise SystemExit(f"{gid}: expected one discharge series at {code}, got {len(cand)}")
        ts = cand[0]
        p = fetch_to(s, RAWDIR / f"q_{code}.json", f"{API}/ts/data/timeSeriesCorrectedData/{ts['uniqueId']}",
                     args.refresh, params=dict(sd="1900-01-01T00:00:00.000Z", ed="2100-01-01T00:00:00.000Z"),
                     pause=2.0, timeout=300)
        d = json.loads(p.read_text())
        approvals = sorted({a["LevelDescription"] for a in d.get("Approvals", [])})
        pts = pd.DataFrame([(x["Timestamp"], (x["Value"] or {}).get("Numeric")) for x in d["Points"]],
                           columns=["ts", "flow"])
        n_pts = len(pts)
        # timestamps carry the station's +07:00 offset; the calendar date is the first 10 characters
        pts["t"] = pd.to_datetime(pts["ts"].str[:19])
        pts["date"] = pd.to_datetime(pts["ts"].str[:10])
        empty = pts["flow"].isna()
        zero = pts["flow"] == 0
        neg = pts["flow"] < 0
        zero_dates = sorted(pts.loc[zero, "date"].dt.strftime("%Y-%m-%d"))
        pts = pts[~empty & ~zero & ~neg].reset_index(drop=True)
        # stored copies: same value as the previous point, under 12 hours later
        copy = (pts["flow"] == pts["flow"].shift()) & ((pts["t"] - pts["t"].shift()) < pd.Timedelta(hours=12))
        copy_days = sorted(pts.loc[copy, "date"].dt.strftime("%Y-%m-%d").unique())
        n_copy = int(copy.sum())
        pts = pts[~copy]
        g = pts.groupby("date")["flow"].agg(["mean", "count"]).reset_index()
        multi = g[g["count"] > 1]
        df = pd.DataFrame({"date": g["date"], "flow": g["mean"], "quality": "measured"})

        est = pd.Series(False, index=df.index)
        reasons = []
        for n in d.get("Notes", []):
            if FILL.search(n["NoteText"]):
                a, b = pd.Timestamp(n["StartTime"][:10]), pd.Timestamp(n["EndTime"][:10])
                m = (df["date"] >= a) & (df["date"] <= b)
                est |= m
                reasons.append(f"{a.date()} to {b.date()} ({int(m.sum())} days): note '{n['NoteText'].strip()}'")
        for gr in d.get("Grades", []):
            if gr["GradeCode"] in EST_GRADES:
                a, b = pd.Timestamp(gr["StartTime"][:10]), pd.Timestamp(gr["EndTime"][:10])
                m = (df["date"] >= a) & (df["date"] <= b)
                est |= m
                reasons.append(f"{a.date()} to {b.date()} ({int(m.sum())} days): grade {gr['GradeCode']}")
        if code == "014901":
            for yr in (1940, 1957):
                m = df["date"].dt.year == yr
                est |= m
                reasons.append(f"{yr} ({int(m.sum())} days): Kratie level for {yr} is absent from MRC's 2005 data "
                               "inventory and present now, so it was added or rebuilt later (mrc.py)")
            m = (df["date"] >= "1975-01-01") & (df["date"] <= "1979-12-31")
            est |= m
            reasons.append(f"1975-01-01 to 1979-12-31 ({int(m.sum())} days): Khmer Rouge years; the Kratie level "
                           "record has no gaps when routine reading is unlikely and was not in MRC's 2005 data "
                           "inventory, so it is probably reconstructed (mrc.py)")
        df.loc[est, "quality"] = "estimated"

        removed_on = {n["StartTime"][:10] for n in d.get("Notes", []) if "removed" in n["NoteText"]}
        removed = sorted(set(zero_dates) & removed_on)
        grades = sorted({gr["GradeCode"] for gr in d.get("Grades", [])})
        methods = sorted({m["MethodCode"] for m in d.get("Methods", [])})
        notes = [
            f"MRC labels this series 'Calculated daily discharge': flow computed from the gauge level with a rating "
            f"curve. MRC's own notes on the Kratie series say a point 'was corrected using the equation from the "
            f"rating curves' (MRC time-series API). Method code on this series: {', '.join(methods)}.",
            f"Approval level for the whole series: {', '.join(approvals)}, not final. As for the level series "
            "(mrc.py), approval is not used for quality, because it is the same for every day (MRC time-series API).",
            f"MRC series '{ts['identifier']}' (uniqueId {ts['uniqueId']}). {n_pts} points. "
            f"Days with more than one point after removing stored copies, averaged to a daily mean: {len(multi)}"
            + (f", from {multi['date'].min().date()} on" if len(multi) else "") + ". Before that, one point a day "
            "(MRC time-series API).",
            f"Stored copies dropped (same value as the previous point, under 12 hours later): {n_copy} points on "
            f"{copy_days if copy_days else 'no days'} (MRC time-series API).",
            f"Dropped {int(empty.sum())} empty and {int(neg.sum())} negative points, and {len(zero_dates)} "
            f"point(s) of exactly 0 m3/s, which cannot be real flow on the Mekong mainstream: {zero_dates}"
            + (f"; on {removed} MRC's notes say a point was removed, so 0 marks a removed value"
               if removed else "") + " (MRC time-series API).",
            "The API carries no per-point quality flag. Days marked estimated: "
            + ("; ".join(reasons) if reasons else "none (no fill notes or grade 41 intervals)") + ".",
            f"Grade codes present: {grades}; MRC does not publish their meaning in the API. Intervals other than "
            "-1 and 41 are kept as measured, as in mrc.py (MRC time-series API).",
            "Recent values are stored with long float tails (for example 1552.7615790000004); we round to "
            "0.001 m3/s, which changes no published digit that carries meaning (MRC time-series API).",
        ]
        if d.get("Notes"):
            notes.append("All MRC notes for this series: " + " | ".join(
                f"{n['StartTime'][:10]}: {n['NoteText'].strip()}" for n in d["Notes"]) + " (MRC time-series API).")
        if offset:
            notes.append("MRC's Vientiane flow series ends in 2006, so this is Nong Khai (station 012001), 13 km "
                         "downstream on the Thai bank; the two are not joined (MRC time-series API).")
        meta = {
            "id": gid, "river": "mekong", "name": name,
            "station_name": ts["stationName"], "station_code": code, "country": COUNTRY[ts["countryCode"]],
            "lat": round(ts["latitude"], 6), "lon": round(ts["longitude"], 6),
            "same_station": offset == "", "offset_note": offset, "kind": "river flow",
            "unit": "m3/s" if d.get("Unit") == "m^3/s" else d.get("Unit"),
            "daily_stat": "mixed" if len(multi) else "one reading",
            "source": "Mekong River Commission (MRC) time-series API, Discharge, Calculated daily discharge",
            "source_url": f"{API}/ts/data/timeSeriesCorrectedData/{ts['uniqueId']}",
            "license": LICENSE, "credit": "Mekong River Commission",
            "flag_rule": "MRC has no per-point flag and approval is 'Working' throughout; days are measured except "
                         "fill notes, grade 41 and (Kratie) 1940, 1957 and 1975-1979, which are estimated.",
            "notes": notes,
        }
        write_flow(df, meta, decimals=3)


if __name__ == "__main__":
    main()
