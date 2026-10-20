"""Shared helpers for the North America fetch scripts (cwms, rise, usgs, eccc).

Every script downloads raw files into data/raw/<source>/ and rebuilds
data/processed/<gauge_id>.csv and .json from those raw files only, so the
processed output is the same with or without network access.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import time
from pathlib import Path

import pandas as pd
import requests

from downloaded import drop_partial_days, mark_session

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
USER_AGENT = "Data4ThePeople-RiverLevels/0.1 (+https://www.data4thepeople.com)"
QUALITIES = ("measured", "provisional", "estimated")

_last_request = [0.0]


def parse_args(description: str) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--refresh", action="store_true",
                   help="download raw files again (default: use the cache)")
    p.add_argument("--only", nargs="*", help="gauge ids to build (default: all)")
    return p.parse_args()


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return mark_session(s)


def polite_get(sess: requests.Session, url: str, *, params=None, headers=None,
               timeout: int = 300, pause: float = 1.0, tries: int = 5) -> requests.Response:
    """GET with a pause between requests and backoff on errors."""
    for attempt in range(tries):
        wait = pause - (time.time() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.time()
        try:
            r = sess.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            return r
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            if attempt == tries - 1:
                raise
            back = 5 * 2 ** attempt
            print(f"    retry {attempt + 1} after {back}s: {e}")
            time.sleep(back)
    raise RuntimeError("unreachable")


def need_cache(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing raw cache {path}. Run with --refresh first.")


def coverage_by_decade(df: pd.DataFrame) -> list[dict]:
    """Shares of calendar days (inside the record) with a value, by quality."""
    d = pd.to_datetime(df["date"])
    first, last = d.min().date(), d.max().date()
    out = []
    for dec in range(first.year // 10 * 10, last.year // 10 * 10 + 10, 10):
        lo = max(first, dt.date(dec, 1, 1))
        hi = min(last, dt.date(dec + 9, 12, 31))
        ndays = (hi - lo).days + 1
        sub = df[(d.dt.year >= dec) & (d.dt.year < dec + 10)]
        q = sub["quality"].value_counts()
        out.append({
            "decade": dec,
            "share_days": round(len(sub) / ndays, 4),
            "share_measured": round(q.get("measured", 0) / ndays, 4),
            "share_estimated": round(q.get("estimated", 0) / ndays, 4),
            "share_provisional": round(q.get("provisional", 0) / ndays, 4),
        })
    return out


def fmt_level(x: float, ndp: int | None) -> str:
    if ndp is not None:
        x = round(x, ndp)
    s = repr(float(x))
    return s


def write_gauge(meta: dict, df: pd.DataFrame, ndp: int | None = None) -> dict:
    """Validate and write data/processed/<id>.csv and .json.

    df has columns date (YYYY-MM-DD str), level (float), quality (str).
    ndp rounds level to that many decimals (only to strip float noise from a
    unit conversion done by the publisher's API; see the notes per gauge).
    """
    df = df[["date", "level", "quality"]].copy()
    df["date"] = df["date"].astype(str)
    df = drop_partial_days(df, meta["id"])
    dups = df["date"][df["date"].duplicated()]
    if len(dups):
        raise ValueError(f"{meta['id']}: duplicate dates {list(dups[:10])}")
    bad = set(df["quality"]) - set(QUALITIES)
    if bad:
        raise ValueError(f"{meta['id']}: unknown quality values {bad}")
    if df["level"].isna().any():
        raise ValueError(f"{meta['id']}: NaN level")
    for s in df["date"]:
        dt.date.fromisoformat(s)  # raises on a malformed date
    df = df.sort_values("date").reset_index(drop=True)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    lines = ["date,level,quality"]
    lines += [f"{r.date},{fmt_level(r.level, ndp)},{r.quality}" for r in df.itertuples()]
    (PROCESSED / f"{meta['id']}.csv").write_text("\n".join(lines) + "\n")

    keys = ["id", "river", "name", "country", "lat", "lon", "kind", "source",
            "source_url", "station_code", "unit", "datum", "daily_stat"]
    missing = [k for k in keys if k not in meta]
    if missing:
        raise ValueError(f"{meta['id']}: metadata missing {missing}")
    out = {k: meta[k] for k in keys}
    out["first_date"] = df["date"].iloc[0]
    out["last_date"] = df["date"].iloc[-1]
    out["n_days"] = int(len(df))
    out["coverage_by_decade"] = coverage_by_decade(df)
    out["license"] = meta["license"]
    out["notes"] = meta.get("notes", [])
    # Disclosure of how the record was made: list of {"date", "fact", "source_url"}.
    hfile = Path(__file__).with_name("na_history.json")
    hall = json.loads(hfile.read_text()) if hfile.exists() else {}
    meta = {**hall.get(meta["id"], {}), **meta}
    hist = meta.get("measurement_history")
    if not hist:
        raise ValueError(f"{meta['id']}: measurement_history missing from na_history.json")
    for h in hist:
        if set(h) != {"date", "fact", "source_url"}:
            raise ValueError(f"{meta['id']}: bad measurement_history entry {h}")
    out["measurement_history"] = hist
    if not meta.get("public_notes"):
        raise ValueError(f"{meta['id']}: public_notes missing")
    out["public_notes"] = meta["public_notes"]
    (PROCESSED / f"{meta['id']}.json").write_text(json.dumps(out, indent=2) + "\n")
    q = df["quality"].value_counts()
    print(f"  {meta['id']}: {out['first_date']}..{out['last_date']} n={len(df)} "
          + " ".join(f"{k}={q.get(k, 0)}" for k in QUALITIES))
    return out


def days_in_year(y: int) -> int:
    return 366 if calendar.isleap(y) else 365
