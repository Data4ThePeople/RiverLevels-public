"""Shared helpers for the European fetch scripts (hyd1d/PEGELONLINE, RWS, GKD,
eHYD, Hub'Eau). Writes the processed CSV + JSON pair described in README.md."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import pandas as pd
import requests

from downloaded import drop_partial_days, mark_session

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
UA = "Data4ThePeople-RiverLevels/0.1 (+https://www.data4thepeople.com)"
QUALITIES = ("measured", "provisional", "estimated")


def parse_args(doc: str) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=doc)
    p.add_argument("--refresh", action="store_true", help="download raw files again")
    return p.parse_args()


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = UA
    return mark_session(s)


def get(s: requests.Session, url: str, *, pause: float = 0.5, tries: int = 4, **kw) -> requests.Response:
    """GET with a polite pause and simple retry on network errors and 5xx."""
    kw.setdefault("timeout", 120)
    for i in range(tries):
        try:
            r = s.get(url, **kw)
            if r.status_code < 500:
                r.raise_for_status()
                time.sleep(pause)
                return r
        except requests.RequestException:
            if i == tries - 1:
                raise
        time.sleep(5 * (i + 1))
    r.raise_for_status()
    return r


def need(path: Path, refresh: bool) -> bool:
    """True if the raw file must be downloaded."""
    if refresh or not path.exists():
        return True
    return False


def require_cache(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"missing raw cache {path}; run with --refresh")


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
    """Hand-curated, sourced measurement history and reader notes per gauge (eu_history.json)."""
    p = Path(__file__).resolve().parent / "eu_history.json"
    return json.loads(p.read_text()) if p.exists() else {}


def write_gauge(df: pd.DataFrame, meta: dict) -> dict:
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
    df["level"] = df["level"].astype(float) + 0.0  # turn -0.0 into 0.0
    df = df.sort_values("date").reset_index(drop=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / f"{gid}.csv", index=False, float_format="%.1f", lineterminator="\n")
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
          f"measured={q.get('measured', 0):.3f} prov={q.get('provisional', 0):.3f} est={q.get('estimated', 0):.3f}")
    return out


def utm_to_latlon(e: float, n: float, zone: int) -> tuple[float, float]:
    """Inverse UTM on GRS80/WGS84 (ETRS89 treated as WGS84, sub-meter for mapping)."""
    a, f = 6378137.0, 1 / 298.257222101
    k0, e2 = 0.9996, f * (2 - f)
    ep2 = e2 / (1 - e2)
    x, y = e - 500000.0, n
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2**2 / 64 - 5 * e2**3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    p1 = (mu + (3 * e1 / 2 - 27 * e1**3 / 32) * math.sin(2 * mu)
          + (21 * e1**2 / 16 - 55 * e1**4 / 32) * math.sin(4 * mu)
          + (151 * e1**3 / 96) * math.sin(6 * mu) + (1097 * e1**4 / 512) * math.sin(8 * mu))
    c1 = ep2 * math.cos(p1) ** 2
    t1 = math.tan(p1) ** 2
    n1 = a / math.sqrt(1 - e2 * math.sin(p1) ** 2)
    r1 = a * (1 - e2) / (1 - e2 * math.sin(p1) ** 2) ** 1.5
    d = x / (n1 * k0)
    lat = p1 - (n1 * math.tan(p1) / r1) * (
        d**2 / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * ep2) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * ep2 - 3 * c1**2) * d**6 / 720)
    lon = (d - (1 + 2 * t1 + c1) * d**3 / 6
           + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * ep2 + 24 * t1**2) * d**5 / 120) / math.cos(p1)
    lon0 = math.radians((zone - 1) * 6 - 180 + 3)
    return round(math.degrees(lat), 6), round(math.degrees(lon0 + lon), 6)
