"""Shared helpers for the South America, Australia and Mekong fetch scripts
(ana.py, ina.py, dmh.py, bom.py, mrc.py). Writes the processed CSV + JSON pair
described in README.md."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

from downloaded import drop_partial_days, mark_session

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
# BoM rejects non-browser agents, so every source gets a browser token plus our id.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "Data4ThePeople-RiverLevels/0.1 (+https://www.data4thepeople.com)")
QUALITIES = ("measured", "provisional", "estimated")
HISTORY_FILE = Path(__file__).resolve().parent / "sa_asia_history.json"


def parse_args(doc: str, extra=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=doc)
    p.add_argument("--refresh", action="store_true", help="download raw files again")
    if extra:
        extra(p)
    return p.parse_args()


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return mark_session(s)


def get(s: requests.Session, url: str, *, pause: float = 0.5, tries: int = 4, **kw) -> requests.Response:
    """GET with a polite pause and simple retry on network errors and 5xx."""
    kw.setdefault("timeout", 180)
    last = None
    for i in range(tries):
        try:
            r = s.get(url, **kw)
            if r.status_code < 500:
                r.raise_for_status()
                time.sleep(pause)
                return r
            last = requests.HTTPError(f"{r.status_code} for {r.url}")
        except requests.RequestException as e:
            last = e
        time.sleep(5 * (i + 1))
    raise last


def fetch_to(s: requests.Session, path: Path, url: str, refresh: bool, **kw) -> Path:
    """Download url to path unless cached (and not refreshing). Writes atomically."""
    if path.exists() and not refresh:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    r = get(s, url, **kw)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(r.content)
    tmp.replace(path)
    return path


def coverage_by_decade(df: pd.DataFrame) -> list[dict]:
    d = pd.to_datetime(df["date"])
    first, last = d.min(), d.max()
    out = []
    for dec in range(first.year // 10 * 10, last.year // 10 * 10 + 10, 10):
        lo = max(first, pd.Timestamp(f"{dec}-01-01"))
        hi = min(last, pd.Timestamp(f"{dec + 9}-12-31"))
        ndays = (hi - lo).days + 1
        sel = df[(d >= lo) & (d <= hi)]
        q = sel["quality"].value_counts()
        out.append({
            "decade": dec,
            "share_days": round(len(sel) / ndays, 4),
            "share_measured": round(q.get("measured", 0) / ndays, 4),
            "share_estimated": round(q.get("estimated", 0) / ndays, 4),
            "share_provisional": round(q.get("provisional", 0) / ndays, 4),
        })
    return out


def history() -> dict:
    """Hand-curated, sourced measurement history and reader notes per gauge."""
    return json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else {}


def write_gauge(df: pd.DataFrame, meta: dict, decimals: int) -> dict:
    """Validate and write data/processed/<id>.csv and .json. df has date, level, quality."""
    gid = meta["id"]
    df = df[["date", "level", "quality"]].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = drop_partial_days(df, gid)
    dup = df["date"].duplicated(keep=False)
    if dup.any():
        raise ValueError(f"{gid}: duplicate dates {sorted(df.loc[dup, 'date'].unique())[:10]}")
    if df["level"].isna().any():
        raise ValueError(f"{gid}: NaN levels")
    bad = set(df["quality"]) - set(QUALITIES)
    if bad:
        raise ValueError(f"{gid}: bad quality values {bad}")
    df = df.sort_values("date").reset_index(drop=True)
    df["level"] = df["level"].round(decimals)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / f"{gid}.csv", index=False, float_format=f"%.{max(decimals, 1)}f",
              lineterminator="\n")
    keys = ["id", "river", "name", "country", "lat", "lon", "kind", "source", "source_url",
            "station_code", "unit", "datum", "daily_stat"]
    out = {k: meta[k] for k in keys}
    out.update({
        "first_date": df["date"].iloc[0],
        "last_date": df["date"].iloc[-1],
        "n_days": int(len(df)),
        "coverage_by_decade": coverage_by_decade(df),
        "license": meta["license"],
        "notes": meta.get("notes", []),
    })
    hist = history().get(gid, {})
    out["measurement_history"] = meta.get("measurement_history", []) + hist.get("measurement_history", [])
    out["public_notes"] = hist.get("public_notes", meta.get("public_notes", ""))
    (PROCESSED / f"{gid}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    q = df["quality"].value_counts(normalize=True)
    print(f"{gid}: {out['first_date']}..{out['last_date']} n={len(df)} "
          f"measured={q.get('measured', 0):.3f} prov={q.get('provisional', 0):.3f} "
          f"est={q.get('estimated', 0):.3f}")
    return out


def share_by_decade(dates: pd.Series, mask: pd.Series) -> dict:
    """Share of rows with mask True, per decade, for notes."""
    d = pd.to_datetime(dates)
    dec = (d.dt.year // 10) * 10
    g = mask.groupby(dec).mean()
    return {int(k): round(float(v), 3) for k, v in g.items() if v > 0}
