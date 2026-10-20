"""Shared writer for flow (discharge) series. Every flow_*.py script calls
write_flow(); it validates the contract in scripts/fetch/FLOW.md, applies the
partial-day rule and writes data/processed/flow/<id>.csv and .json.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from downloaded import drop_partial_days
from sa_asia_common import coverage_by_decade

PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed" / "flow"
QUALITIES = ("measured", "provisional", "estimated")
UNITS = ("cfs", "m3/s", "L/s")
KINDS = ("river flow", "dam release")
STATS = ("mean", "one reading", "mixed")
META = {
    "id": str, "river": str, "name": str, "station_name": str, "station_code": str,
    "country": str, "lat": float, "lon": float, "same_station": bool, "offset_note": str,
    "kind": str, "unit": str, "daily_stat": str, "source": str, "source_url": str,
    "license": str, "credit": str, "flag_rule": str, "notes": list,
}


def write_flow(df: pd.DataFrame, meta: dict, decimals: int | None = None) -> dict:
    """df has columns date, flow, quality. decimals rounds flow only to strip
    float noise from a unit conversion done by the publisher's API."""
    gid = meta.get("id", "?")
    extra, missing = set(meta) - set(META), set(META) - set(meta)
    if extra or missing:
        raise SystemExit(f"{gid}: meta extra {sorted(extra)}, missing {sorted(missing)}")
    for k, t in META.items():
        v = meta[k]
        ok = (isinstance(v, (int, float)) and not isinstance(v, bool)) if t is float else isinstance(v, t)
        if not ok:
            raise SystemExit(f"{gid}: {k} must be {t.__name__}")
    for k, allowed in (("unit", UNITS), ("kind", KINDS), ("daily_stat", STATS)):
        if meta[k] not in allowed:
            raise SystemExit(f"{gid}: {k} {meta[k]!r} not in {allowed}")
    if meta["same_station"] != (meta["offset_note"] == ""):
        raise SystemExit(f"{gid}: offset_note must be empty exactly when same_station is true")
    if not all(isinstance(n, str) and n for n in meta["notes"]):
        raise SystemExit(f"{gid}: notes must be non-empty strings")

    df = df[["date", "flow", "quality"]].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = drop_partial_days(df, gid)
    if df["date"].duplicated().any():
        raise SystemExit(f"{gid}: duplicate dates {df.loc[df['date'].duplicated(), 'date'].tolist()[:5]}")
    bad = set(df["quality"]) - set(QUALITIES)
    if bad:
        raise SystemExit(f"{gid}: unknown quality values {bad}")
    if df["flow"].isna().any():
        raise SystemExit(f"{gid}: empty flow values; drop them and say how many in notes")
    if (df["flow"] < 0).any():
        raise SystemExit(f"{gid}: negative flow on {df.loc[df['flow'] < 0, 'date'].tolist()[:5]}; explain in notes and drop")
    df = df.sort_values("date").reset_index(drop=True)
    if decimals is not None:
        df["flow"] = df["flow"].round(decimals)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / f"{gid}.csv", index=False, lineterminator="\n")
    out = dict(meta)
    out["first_date"], out["last_date"], out["n_days"] = df["date"].iloc[0], df["date"].iloc[-1], int(len(df))
    out["coverage_by_decade"] = coverage_by_decade(df)
    (PROCESSED / f"{gid}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    q = df["quality"].value_counts().to_dict()
    print(f"{gid}: {out['first_date']}..{out['last_date']} n={len(df)} {q}")
    return out
