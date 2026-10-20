"""Mekong River Commission (MRC) time-series API: manual daily water level for
four mainstream Mekong gauges.

The station inventory comes from /ts/inventory/timeSeriesList and the data from
/ts/data/timeSeriesCorrectedData/{uniqueId}. We use the "Water Level.Manual"
series (staff gauge, read one to six times per day). If a day has more than one
point we take the mean and say so in the notes.

The API carries no per-point quality flag. It does carry Grades and Notes
intervals. A day is marked estimated when it falls in a Notes interval that says
the data were filled, estimated or interpolated, or in a grade 41 interval
(the grade MRC used for those filled periods). Cambodian Kratie 1975-1979 is
also marked estimated: the record is unbroken through the Khmer Rouge years,
when routine gauge reading is unlikely to have continued, and MRC gives no flag.
"""
from __future__ import annotations

import json
import re

import pandas as pd

from sa_asia_common import RAW, fetch_to, parse_args, session, write_gauge

API = "https://timeseries.api.mrcmekong.org/api/v1"
RAWDIR = RAW / "mrc"
GAUGES = [
    # id, station code, display name
    ("mekong-chiangsaen", "010501", "Chiang Saen"),
    ("mekong-vientiane", "011901", "Vientiane"),
    ("mekong-pakse", "013901", "Pakse"),
    ("mekong-kratie", "014901", "Kratie"),
]
COUNTRY = {"TH": "Thailand", "LA": "Laos", "KH": "Cambodia", "VN": "Vietnam"}
# gauge zero elevations, MRC Annual Flood Report 2006, appendix 2
# (https://archive.iwlearn.org/mrcmekong.org/flood_report/2006/appendix-2.pdf)
ZERO = {"010501": 357.1, "011901": 158.0, "013901": 86.5, "014901": -1.08}
FILL = re.compile(r"\bfill|estimat|interpolat", re.I)
EST_GRADES = {"41"}
LICENSE = ("Not open. MRC's Non-commercial Data Use Licence (version C, 2005) allows non-commercial use "
           "only and no redistribution of data or derived products without MRC's written permission "
           "(https://archive.iwlearn.org/mrcmekong.org/download/spatial/nonCommmercialDataUseLicense.pdf); "
           "no current license text found on portal.mrcmekong.org. Get MRC permission before publishing. "
           "Credit: Mekong River Commission.")


def local_date(ts: pd.Series) -> pd.Series:
    # timestamps carry the station's +07:00 offset; the calendar date is the first 10 chars
    return pd.to_datetime(ts.str[:10])


def main():
    args = parse_args(__doc__)
    s = session()
    inv_p = fetch_to(s, RAWDIR / "inventory.json", f"{API}/ts/inventory/timeSeriesList", args.refresh)
    inv = json.loads(inv_p.read_text())
    for gid, code, name in GAUGES:
        cand = [x for x in inv if x["stationCode"] == code and x["parameter"] == "Water Level"
                and x["label"] == "Manual"]
        if len(cand) != 1:
            raise ValueError(f"{gid}: expected one manual water level series, got {len(cand)}")
        ts = cand[0]
        p = fetch_to(s, RAWDIR / f"wl_manual_{code}.json",
                     f"{API}/ts/data/timeSeriesCorrectedData/{ts['uniqueId']}", args.refresh,
                     params=dict(sd="1900-01-01T00:00:00.000Z", ed="2100-01-01T00:00:00.000Z"),
                     pause=2.0, timeout=300)
        d = json.loads(p.read_text())
        pts = pd.DataFrame([(x["Timestamp"], (x["Value"] or {}).get("Numeric")) for x in d["Points"]],
                           columns=["ts", "level"])
        n_pts = len(pts)
        empty = pts["level"].isna()
        fill_vals = pts["level"].notna() & ((pts["level"] <= -99) | (pts["level"] >= 999))
        pts = pts[~empty & ~fill_vals].copy()
        pts["date"] = local_date(pts["ts"])
        # 0.00 readings inside a day that also has a reading more than 1 m away are placeholders;
        # drop them before averaging, or the daily mean is halved (Kratie 2006-01-01: 8.47 and 0.00)
        day_max = pts.groupby("date")["level"].transform(lambda v: v.abs().max())
        day_n = pts.groupby("date")["level"].transform("size")
        sub_zero = (pts["level"] == 0) & (day_n > 1) & (day_max > 1)
        sub_zero_days = sorted({str(x.date()) for x in pts.loc[sub_zero, "date"]})
        pts = pts[~sub_zero]
        g = pts.groupby("date")["level"].agg(["mean", "count"]).reset_index()
        df = pd.DataFrame({"date": g["date"], "level": g["mean"], "quality": "measured"})
        multi = int((g["count"] > 1).sum())
        # isolated exact zeros: a 0.00 day more than 1 m from both neighbors is a placeholder
        prev, nxt = df["level"].shift(1), df["level"].shift(-1)
        zero = (df["level"] == 0) & ((prev - df["level"]).abs() > 1) & ((nxt - df["level"]).abs() > 1)
        zero_days = [str(x.date()) for x in df.loc[zero, "date"]]
        df = df[~zero].reset_index(drop=True)

        est = pd.Series(False, index=df.index)
        est_reasons = []
        for n in d.get("Notes", []):
            if FILL.search(n["NoteText"]):
                a, b = pd.Timestamp(n["StartTime"][:10]), pd.Timestamp(n["EndTime"][:10])
                m = (df["date"] >= a) & (df["date"] <= b)
                est |= m
                est_reasons.append(f"{a.date()} to {b.date()} ({int(m.sum())} days): note '{n['NoteText'].strip()}'")
        for gr in d.get("Grades", []):
            if gr["GradeCode"] in EST_GRADES:
                a, b = pd.Timestamp(gr["StartTime"][:10]), pd.Timestamp(gr["EndTime"][:10])
                m = (df["date"] >= a) & (df["date"] <= b)
                est |= m
                est_reasons.append(f"{a.date()} to {b.date()} ({int(m.sum())} days): grade {gr['GradeCode']}")
        if code == "014901":
            # MRC's 2005 data inventory lists Kratie daily water level as 1934-39, 1941-56,
            # 1958-74, 1980-2002; the API now has full 1940 and 1957, so those were added later.
            for yr in ("1940", "1957"):
                m = df["date"].dt.year == int(yr)
                est |= m
                est_reasons.append(f"{yr} ({int(m.sum())} days): absent from MRC's 2005 data inventory "
                                   "(archive.iwlearn.org/mrcmekong.org/spatial/meta_html/HydrologicalData.pdf), "
                                   "present now, so added or reconstructed later")
            m = (df["date"] >= "1975-01-01") & (df["date"] <= "1979-12-31")
            est |= m
            est_reasons.append(f"1975-01-01 to 1979-12-31 ({int(m.sum())} days): Khmer Rouge period, "
                               "record has no gaps in years when routine reading is unlikely, and MRC's 2005 "
                               "data inventory had no Kratie water level for 1975-79, so the values were "
                               "added later and are probably reconstructed; MRC gives no per-point flag "
                               "and no method. Their day-to-day "
                               "variability is similar to 1970-1974 and 1980-1984, so we cannot tell "
                               "filled days from real ones")
        df.loc[est, "quality"] = "estimated"
        step_note = []
        if code == "010501":
            # station moved on 1993-12-15 (Cochrane et al. 2014, HESS 18:4529); check for the step
            lv = df.set_index("date")["level"]
            before = lv["1993-12-06":"1993-12-15"].mean()
            after = lv["1993-12-16":"1993-12-25"].mean()
            step_note.append(
                f"Datum step: the gauge moved on 1993-12-15 (Cochrane et al. 2014 report a 0.62 m "
                f"correction is needed to compare later values with earlier ones). In this API series the "
                f"mean of 1993-12-16..25 minus the mean of 1993-12-06..15 is {after - before:+.2f} m, a jump "
                f"in the dry season, so the series appears NOT corrected. We publish it as is; compare "
                f"levels across 1993 only after removing the step.")

        grades = sorted({gr["GradeCode"] for gr in d.get("Grades", [])})
        other_grades = [f"{gr['StartTime'][:10]}..{gr['EndTime'][:10]} grade {gr['GradeCode']}"
                        for gr in d.get("Grades", []) if gr["GradeCode"] not in {"-1"} | EST_GRADES]
        notes = [
            f"MRC series '{ts['identifier']}' (uniqueId {ts['uniqueId']}), interval '{ts['interval']}', "
            f"method {', '.join(sorted({m['MethodCode'] for m in d.get('Methods', [])}))}, "
            f"approval level {', '.join(sorted({a['LevelDescription'] for a in d.get('Approvals', [])}))}.",
            f"{n_pts} points. Days with more than one point, averaged to a daily mean: {multi}.",
            f"Dropped {int(empty.sum())} empty points and {int(fill_vals.sum())} fill values (<= -99 or >= 999). "
            f"Dropped {len(zero_days)} isolated 0.00 daily values more than 1 m from both neighboring days "
            f"(placeholders): {zero_days}. "
            f"Dropped 0.00 readings inside a day that also had a reading more than 1 m away, before averaging, "
            f"on {len(sub_zero_days)} days: {sub_zero_days}.",
            "The API carries no per-point quality flag. Days marked estimated: " +
            ("; ".join(est_reasons) if est_reasons else "none (no fill notes or grade 41 intervals)") + ".",
            f"Grade codes present: {grades}. MRC does not publish the meaning of its grade codes in the API. "
            f"Grade intervals other than -1 (default) and 41 are kept as measured; their notes describe typo "
            f"corrections or cross-checks against neighbor gauges: {other_grades if other_grades else 'none'}.",
            "Values are stored in the API as floats with long tails (for example 6.576172678319064), which "
            "comes from a datum conversion; we round to 3 decimals (1 mm).",
            "All MRC notes for this series: " + " | ".join(
                f"{n['StartTime'][:10]}..{n['EndTime'][:10]}: {n['NoteText'].strip()}" for n in d.get("Notes", [])),
        ] + step_note
        meta = {
            "id": gid, "river": "mekong", "name": name, "country": COUNTRY[ts["countryCode"]],
            "lat": round(ts["latitude"], 6), "lon": round(ts["longitude"], 6), "kind": "river",
            "source": "Mekong River Commission (MRC) time-series API",
            "source_url": f"https://portal.mrcmekong.org/time-series/ ({ts['locationIdentifier']}); "
                          f"{API}/ts/data/timeSeriesCorrectedData/{ts['uniqueId']}",
            "station_code": code, "unit": d.get("Unit", "m"),
            "datum": f"m above the local gauge zero; MRC's 2006 flood report lists the zero at {ZERO[code]} m above "
                     "mean sea level (reference datum not named there)",
            "daily_stat": "mixed (see notes)" if multi else "single reading",
            "license": LICENSE, "notes": notes,
        }
        write_gauge(df, meta, decimals=3)


if __name__ == "__main__":
    main()
