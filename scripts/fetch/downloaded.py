"""Download dates and the partial-day rule.

Every session made by the shared helpers records today's date in
data/raw/.downloaded/<script>.txt whenever a request returns data. When a
gauge is written, any day on or after that date is dropped: the download
happened during that day, so a mean of its readings covers only part of it.
With the raw cache in place no request is made and the recorded date stays
the date of the last real download.
"""
import datetime as dt
import sys
from pathlib import Path

import pandas as pd

MARKS = Path(__file__).resolve().parents[2] / "data" / "raw" / ".downloaded"


def _script() -> str:
    return Path(sys.argv[0]).stem


def mark_session(s):
    def hook(r, *args, **kwargs):
        if r.ok:
            MARKS.mkdir(parents=True, exist_ok=True)
            (MARKS / f"{_script()}.txt").write_text(dt.date.today().isoformat() + "\n")
        return r
    s.hooks["response"].append(hook)
    return s


def download_date() -> str:
    p = MARKS / f"{_script()}.txt"
    if not p.exists():
        raise SystemExit(f"no download date recorded in {p}; run with --refresh or write the date of the raw cache there")
    return p.read_text().strip()


def drop_partial_days(df: pd.DataFrame, gid: str) -> pd.DataFrame:
    cut = download_date()
    keep = df["date"].astype(str) < cut
    n = int((~keep).sum())
    if n:
        print(f"  {gid}: dropped {n} day(s) on or after the download date {cut}")
    return df[keep]
