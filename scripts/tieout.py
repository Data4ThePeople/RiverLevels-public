"""Tie-out: every number the page shows for each gauge, recomputed from
data/processed with pandas, compared with what headless Chrome renders.

Checks per gauge: record low and high (value and date), latest value and date,
first year, years missing more than 5% of days, count of years.
Writes research/tieout.md and exits nonzero on any mismatch.
"""
import html
from decimal import Decimal, ROUND_HALF_UP
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
DEC = {"cm": 0, "ft": 1, "m": 2}


def fmt_date(d):
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def fmt_val(v, unit):
    # round half away from zero on the decimal value, as the browser's toLocaleString does
    q = Decimal(repr(round(float(v), 6))).quantize(Decimal(1).scaleb(-DEC[unit]), rounding=ROUND_HALF_UP)
    if q == 0:
        q = abs(q)
    return f"{q:,.{DEC[unit]}f} {unit}"


def fmt_flow(v, unit):
    """Mirror of the page's fmtFlow: 0 decimals from 100, 1 from 10, else 2; half away from zero."""
    dec = 0 if v >= 100 or v == 0 else 1 if v >= 10 else 2
    q = Decimal(repr(round(float(v), 6))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    return f"{q:,.{dec}f} " + ("m³/s" if unit == "m3/s" else unit)


def thin_years(df):
    first_day, last_day = df["d"].iloc[0], df["d"].iloc[-1]
    have = df.groupby(df["d"].dt.year).size()
    years = range(first_day.year, last_day.year + 1)
    thin = 0
    for y in years:
        a = max(first_day, pd.Timestamp(y, 1, 1))
        b = min(last_day, pd.Timestamp(y, 12, 31))
        if have.get(y, 0) / ((b - a).days + 1) < 0.95:
            thin += 1
    return thin, len(years), first_day.year


def flow_frame(gid):
    m = json.loads((ROOT / f"data/processed/flow/{gid}.json").read_text())
    df = pd.read_csv(ROOT / f"data/processed/flow/{gid}.csv", dtype={"date": str})
    sf = json.loads((ROOT / "config/rivers.json").read_text()).get("display_from", {}).get(gid)
    if sf:
        df = df[df["date"] >= sf["date"]].reset_index(drop=True)
    unit = m["unit"]
    if unit == "L/s":
        df["flow"] = df["flow"] / 1000
        unit = "m3/s"
    df["d"] = pd.to_datetime(df["date"])
    return m, df, unit


def flow_texts(gid):
    """What the page should say about a flow series: record line and low/high."""
    m, df, unit = flow_frame(gid)
    lo, hi = df.loc[df["flow"].idxmin()], df.loc[df["flow"].idxmax()]
    thin, n, y0 = thin_years(df)
    noun = "release" if m["kind"] == "dam release" else "flow"
    rec = f"Record starts in {y0}. " + (f"{thin} of {n} years are missing more than 5% of days. " if thin
                                         else "Every year has readings on at least 95% of days. ")
    stats = (f"Lowest daily {noun}: {fmt_flow(lo.flow, unit)} on {fmt_date(lo.d)}{qtag(lo)}. "
             f"Highest: {fmt_flow(hi.flow, unit)} on {fmt_date(hi.d)}{qtag(hi)}.")
    return m, df, unit, rec, stats


def expected_flow_only(gid):
    m, df, unit, rec, stats = flow_texts(gid)
    last = df.iloc[-1]
    return {"stats": stats, "roVal": fmt_flow(last.flow, unit), "roDate": fmt_date(last.d),
            "flag": rec + "Flow is computed from level, so the highest and lowest flows are the least certain. See About this record, below."}


def expected_flow_beside(gid):
    m, df, unit, rec, stats = flow_texts(gid)
    tail = "The release is set by the dam's operators." if m["kind"] == "dam release" else \
        "Flow is computed from level, so the highest and lowest flows are the least certain."
    return {"fFlag": rec + tail, "fStats": stats}


def qtag(row):
    return {"provisional": " (provisional)", "estimated": " (estimated)"}.get(row.quality, "")


def expected(gid, cfg):
    m = json.loads((ROOT / f"data/processed/{gid}.json").read_text())
    df = pd.read_csv(ROOT / f"data/processed/{gid}.csv", dtype={"date": str})
    for adj in cfg.get("adjustments", {}).get(gid, []):
        df.loc[df["date"] < adj["before"], "level"] += adj["add"]
    if gid in cfg.get("display_from", {}):
        df = df[df["date"] >= cfg["display_from"][gid]["date"]]
    unit = m["unit"]
    if unit == "mm":
        df["level"] = df["level"] / 1000
        unit = "m"
    df["d"] = pd.to_datetime(df["date"])
    sf = cfg.get("stats_from", {}).get(gid)
    rec = df[df["date"] >= sf["date"]] if sf else df
    lo, hi = rec.loc[rec["level"].idxmin()], rec.loc[rec["level"].idxmax()]
    last = df.iloc[-1]
    # years missing more than 5% of days; first and last year count only days inside the record
    first_day, last_day = df["d"].iloc[0], df["d"].iloc[-1]
    have = df.groupby(df["d"].dt.year).size()
    thin = 0
    years = range(first_day.year, last_day.year + 1)
    for y in years:
        a = max(first_day, pd.Timestamp(y, 1, 1))
        b = min(last_day, pd.Timestamp(y, 12, 31))
        days = (b - a).days + 1
        if have.get(y, 0) / days < 0.95:
            thin += 1
    return {
        "stats": f"Lowest daily reading{' ' + sf['label'] if sf else ''}: {fmt_val(lo.level, unit)} on {fmt_date(lo.d)}{qtag(lo)}. "
                 f"Highest: {fmt_val(hi.level, unit)} on {fmt_date(hi.d)}{qtag(hi)}.",
        "roVal": fmt_val(last.level, unit),
        "roDate": fmt_date(last.d),
        "flag": f"Record starts in {first_day.year}. "
                + (f"{thin} of {len(years)} years are missing more than 5% of days. " if thin
                   else "Every year has readings on at least 95% of days. ")
                + "Older readings are less certain. See About this record, below.",
    }


def rendered(gid):
    out = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--window-size=1200,780",
                          "--virtual-time-budget=6000", "--dump-dom",
                          f"file://{ROOT}/dist/index.html#{gid}"],
                         capture_output=True, text=True, timeout=90).stdout
    got = {}
    for key in ("stats", "roVal", "roDate", "flag", "fFlag", "fStats"):
        mm = re.search(rf'id="{key}"[^>]*>(.*?)</', out, re.S)
        got[key] = html.unescape(mm.group(1)).strip() if mm else None
    return got


def main():
    cfg = json.loads((ROOT / "config/rivers.json").read_text())
    cfg["rivers"] = [r for r in cfg["rivers"] if r["id"] not in cfg.get("excluded", {})]
    flow_only = {g for r in cfg["rivers"] if r.get("flow_only") for g in r["gauges"]}
    gids = [g for r in cfg["rivers"] for g in r["gauges"]]
    rows, bad, nflow = [], 0, 0
    for gid in gids:
        if gid in flow_only:
            exp = expected_flow_only(gid)
        else:
            exp = expected(gid, cfg)
            if (ROOT / f"data/processed/flow/{gid}.json").exists():
                exp |= expected_flow_beside(gid)
        nflow += gid in flow_only or "fStats" in exp
        got = rendered(gid)
        diffs = [k for k in exp if exp[k] != got[k]]
        bad += bool(diffs)
        rows.append((gid, exp, got, diffs))
        print(("MISMATCH " if diffs else "ok       ") + gid, *(f"\n   {k}: page={got[k]!r}\n   {' ' * len(k)}  calc={exp[k]!r}" for k in diffs))
    lines = ["# Tie-out: page vs. recompute", "",
             f"{len(gids)} gauges checked ({nflow} with flow), {bad} with mismatches. Generated by `scripts/tieout.py`.", "",
             "| gauge | latest | record low and high | completeness |", "|---|---|---|---|"]
    for gid, exp, got, diffs in rows:
        mark = "" if not diffs else " **MISMATCH: " + ", ".join(diffs) + "**"
        lines.append(f"| {gid}{mark} | {exp['roVal']}, {exp['roDate']} | {exp['stats']} | {exp['flag'].split(' Older')[0]} |")
    (ROOT / "research/tieout.md").write_text("\n".join(lines) + "\n")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
