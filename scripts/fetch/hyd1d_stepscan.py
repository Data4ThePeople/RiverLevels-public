"""Datum-step scan for the hyd1d gauges (report only, writes nothing).

For each gauge, take the daily difference W(gauge) - W(neighbor) for two or
more neighbors on the same river. A gauge-zero change at the gauge shows up as
a sudden, lasting shift in the difference against every neighbor on the same
date; a change at a neighbor shows against that neighbor only. Flow changes
also move the difference, so the scan compares the 12-month median before and
after each month boundary and reports shifts of 15 cm or more that are the
largest within +-12 months. Uses the cached RDS in data/raw/hyd1d/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pyreadr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW  # noqa: E402

PAIRS = {
    "MAXAU": ["PLITTERSDORF", "SPEYER", "PHILIPPSBURG"],
    "KAUB": ["BINGEN", "OESTRICH", "SANKT GOAR", "KOBLENZ"],
    "RUHRORT": ["DUESSELDORF", "WESEL", "REES"],
    "DRESDEN": ["PIRNA", "MEISSEN", "SCHOENA"],
    "MAGDEBURG-STROMBRUECKE": ["MAGDEBURG-BUCKAU", "MAGDEBURG-ROTHENSEE", "BARBY", "ROGAETZ"],
    "WITTENBERGE": ["MUEGGENDORF", "SCHNACKENBURG", "TANGERMUENDE", "LENZEN"],
    # control: Koeln, Bonn and Rees all shift about +100 cm in Nov 1979, so Koeln shows it against
    # Duesseldorf (+104) but not against Bonn, and the all-neighbor rule does not flag it.
    "KOELN": ["BONN", "DUESSELDORF"],
}
THRESH = 15


def shift_series(d: pd.Series) -> pd.Series:
    m = d.resample("MS").median()
    out = {}
    for i in range(12, len(m) - 12):
        out[m.index[i]] = m.iloc[i:i + 12].median() - m.iloc[i - 12:i].median()
    return pd.Series(out)


def peaks(s: pd.Series) -> list[pd.Timestamp]:
    a = s.abs()
    return [t for t, v in s.items()
            if abs(v) >= THRESH and a[t - pd.DateOffset(months=12):t + pd.DateOffset(months=12)].max() == abs(v)]


def near(s: pd.Series, t: pd.Timestamp) -> float | None:
    w = s[t - pd.DateOffset(months=1):t + pd.DateOffset(months=1)].dropna()
    return None if w.empty else float(w.loc[w.abs().idxmax()])


def main():
    df = list(pyreadr.read_r(str(RAW / "hyd1d" / "df.gauging_data_latest.RDS")).values())[0]
    df["date"] = pd.to_datetime(df["date"])
    W = df.pivot(index="date", columns="gauging_station", values="w")
    for g, nbrs in PAIRS.items():
        print(f"\n{g}")
        sh = {}
        for n in nbrs:
            if n not in W:
                print(f"  {n}: not in hyd1d")
                continue
            d = (W[g] - W[n]).dropna()
            sh[n] = shift_series(d)
            print(f"  vs {n:22s} {d.index.min().date()}..{d.index.max().date()}  median diff first 3 y "
                  f"{d.iloc[:1096].median():.0f}, last 3 y {d.iloc[-1096:].median():.0f}; candidate shifts: "
                  f"{[(t.strftime('%Y-%m'), round(sh[n][t])) for t in peaks(sh[n])]}")
        cands = sorted({t for s in sh.values() for t in peaks(s)})
        consistent = []
        for t in cands:
            vals = {n: near(s, t) for n, s in sh.items()}
            vals = {n: v for n, v in vals.items() if v is not None}
            if len(vals) >= 2 and all(abs(v) >= 10 for v in vals.values()) and len({v > 0 for v in vals.values()}) == 1:
                consistent.append((t.strftime("%Y-%m"), {n: round(v) for n, v in vals.items()}))
        # collapse runs of adjacent months
        out, last = [], None
        for t, v in consistent:
            if last is None or (pd.Period(t, "M") - pd.Period(last, "M")).n > 2:
                out.append((t, v))
            last = t
        print(f"  STEP CANDIDATES (same sign, >= 10 cm, against every neighbor with data): {out or 'none'}")


if __name__ == "__main__":
    main()
