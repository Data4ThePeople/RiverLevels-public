"""Build dist/index.html: one self-contained page with map geometry and every
gauge's daily record packed inside it.

Each series is stored as int32 day-to-day deltas (gzip, base64) and unpacked in
the browser with DecompressionStream. Nothing is precomputed for display:
record highs and lows are found in the browser from the same daily values.
"""
import argparse
import base64
import shutil
import re
import gzip
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
DAY0 = date(1800, 1, 1)
GAP = -2**31
SCALE = {"cm": 10, "ft": 100, "m": 1000, "mm": 1}
QCODE = {"measured": 0, "provisional": 1, "estimated": 2}


def pack(gid, unit, cfg):
    df = pd.read_csv(PROC / f"{gid}.csv", dtype={"date": str, "quality": str})
    # documented datum adjustments, applied at build time only (the processed file stays as published)
    for adj in cfg.get("adjustments", {}).get(gid, []):
        mask = df["date"] < adj["before"]
        df.loc[mask, "level"] = df.loc[mask, "level"] + adj["add"]
        print(f"{gid}: added {adj['add']} to {int(mask.sum())} days before {adj['before']}")
    start_from = cfg.get("display_from", {}).get(gid)
    if start_from:
        df = df[df["date"] >= start_from["date"]].reset_index(drop=True)
    return pack_series(df, "level", SCALE[unit], gid)


def pack_series(df, col, scale, gid):
    """Pack one daily series (level or flow) as gzip+base64 int32 deltas plus quality runs."""
    if df["date"].duplicated().any():
        raise SystemExit(f"{gid}: duplicate dates {df.loc[df['date'].duplicated(), 'date'].tolist()[:5]}")
    bad = set(df["quality"]) - set(QCODE)
    if bad:
        raise SystemExit(f"{gid}: unknown quality codes {bad}")
    if df[col].isna().any():
        raise SystemExit(f"{gid}: empty {col} values")
    days = (pd.to_datetime(df["date"]) - pd.Timestamp(DAY0)).dt.days.to_numpy()
    if (np.diff(days) <= 0).any():
        raise SystemExit(f"{gid}: dates not strictly increasing")
    start, n = int(days[0]), int(days[-1] - days[0] + 1)
    ints = np.round(df[col].to_numpy() * scale).astype(np.int64)
    if np.abs(ints).max() >= 2**31 - 1:
        raise SystemExit(f"{gid}: value out of int32 range")
    full = np.full(n, GAP, dtype=np.int64)
    idx = days - start
    # deltas between consecutive valid days; gap days carry the GAP marker
    deltas = np.diff(np.concatenate([[0], ints]))
    full[idx] = deltas
    blob = base64.b64encode(gzip.compress(full.astype("<i4").tobytes(), 9, mtime=0)).decode()
    q = np.full(n, 0, dtype=np.int8)
    q[idx] = df["quality"].map(QCODE).to_numpy()
    runs, i = [], 0
    while i < n:
        j = i
        while j + 1 < n and q[j + 1] == q[i]:
            j += 1
        if q[i]:
            runs.append([i, j, int(q[i])])
        i = j + 1
    return start, n, scale, blob, runs


FLOW = PROC / "flow"
FLOW_SCALE = 100  # 0.01 of the unit; finer than any publisher's precision
UNIT_LONG = {"cfs": "Cubic feet per second", "m3/s": "Cubic meters per second"}


TECH = re.compile(r"[{}\[\]]|Rows in |rows repeated|values with an id|query time|columns, not used|days used|Status counts|code counts")


def reader_notes(notes):
    """Flow JSON notes mix plain sentences with fetch bookkeeping (counts by code, rows dropped).
    The page shows the plain sentences; the bookkeeping stays in the processed JSON."""
    return [n for n in notes if not TECH.search(n)]


def reader_license(text):
    """License text for readers: drop our own to-do sentences ("clear ... before publishing")."""
    return re.sub(r";?\s*[Cc]lear [^.;]*before (re)?publishing\.?", ".", text).replace("..", ".").strip()


def pack_flow(gid, cfg):
    """Flow beside a gauge, or None. Hub'Eau publishes L/s; shown as m3/s (display only)."""
    if not (FLOW / f"{gid}.json").exists():
        return None
    m = json.loads((FLOW / f"{gid}.json").read_text())
    df = pd.read_csv(FLOW / f"{gid}.csv", dtype={"date": str, "quality": str})
    start_from = cfg.get("display_from", {}).get(gid)
    if start_from:  # same start as the level chart (Bourke: 1895, then nothing until 1972)
        df = df[df["date"] >= start_from["date"]].reset_index(drop=True)
    unit, scale = m["unit"], FLOW_SCALE
    if unit == "L/s":
        df["flow"] = df["flow"] / 1000
        unit, scale = "m3/s", 1000
    start, n, scale, blob, runs = pack_series(df, "flow", scale, gid + " flow")
    return {
        "unit": unit, "unit_long": UNIT_LONG[unit], "kind": m["kind"], "station_name": m["station_name"],
        "same_station": m["same_station"], "offset_note": m["offset_note"], "lat": m["lat"], "lon": m["lon"],
        "source": m["source"], "license": reader_license(m["license"]), "credit": m["credit"], "flag_rule": m["flag_rule"],
        "notes": reader_notes(m["notes"]), "first_date": (pd.Timestamp(DAY0) + pd.Timedelta(days=start)).strftime("%Y-%m-%d"),
        "last_date": m["last_date"], "start": start, "n": n, "scale": scale, "data": blob, "qruns": runs,
    }


def as_list(v):
    if v is None:
        return []
    return [v] if isinstance(v, str) else list(v)


def history_item(h):
    """Normalize one measurement-history fact to {text, url}."""
    if isinstance(h, str):
        return {"text": h, "url": ""}
    text = h.get("text") or h.get("fact") or ""
    if h.get("date") and not text.startswith(str(h["date"])):
        text = f"{h['date']}: {text}"
    url = h.get("url") or h.get("source_url") or h.get("source") or ""
    return {"text": text, "url": url if str(url).startswith(("http://", "https://")) else ""}


UNIT_WORD = {"cm": "Centimeters", "ft": "Feet", "m": "Meters"}


def short_datum(m, unit):
    """One plain line for the chart subtitle; the full datum text goes in About this record."""
    d = m["datum"]
    if "NAP" in d:
        return "Centimeters above the Dutch sea level datum (NAP)"
    if m["kind"] == "reservoir":
        return "Feet above sea level"
    if "water surface elevation" in d:
        return "Meters above sea level (most likely; the publisher does not say)"
    return f"{UNIT_WORD[unit]} above this gauge's local zero point, not the river's depth"


PAGE_URL = "https://data4thepeople.github.io/RiverLevels-public/"
POST_URL = "https://www.data4thepeople.com/p/world-river-levels"
REPO_URL = "https://github.com/Data4ThePeople/RiverLevels-public"
# the publishers behind every gauge on the page, by agency (the per-gauge source lines name the exact API)
AGENCIES = [
    "Bundesanstalt für Gewässerkunde (BfG), hyd1d, and PEGELONLINE (WSV), Germany",
    "Bayerisches Landesamt für Umwelt, Gewässerkundlicher Dienst Bayern (GKD)",
    "Rijkswaterstaat Waterwebservices, Netherlands",
    "eHYD, Hydrographischer Dienst Österreich",
    "Hub'Eau hydrométrie (Schapi), France",
    "U.S. Army Corps of Engineers, CWMS",
    "U.S. Bureau of Reclamation, RISE",
    "U.S. Geological Survey, NWIS",
    "Environment and Climate Change Canada, Water Survey of Canada",
    "Agência Nacional de Águas e Saneamento Básico (ANA), Brazil, HidroWeb",
    "Instituto Nacional del Agua (INA), Argentina",
    "Dirección de Meteorología e Hidrología (DMH-DINAC), Paraguay",
    "Bureau of Meteorology, Australia, Water Data Online",
    "Arctic Great Rivers Observatory (ArcticGRO), Discharge Dataset",
]


def json_ld(rivers, gauges):
    """Dataset + WebApplication JSON-LD for the page, counted from what the page shows, so Google
    Dataset Search sees the same gauges, dates and sources as the reader."""
    firsts = [g["first_date"] for g in gauges.values()] + [g["flow"]["first_date"] for g in gauges.values() if g["flow"]]
    lasts = [g["last_date"] for g in gauges.values()] + [g["flow"]["last_date"] for g in gauges.values() if g["flow"]]
    sources = AGENCIES
    countries = sorted({g["country"] for g in gauges.values()})
    author = {"@type": "Person", "name": "Eric Pachman", "url": "https://www.data4thepeople.com/authors/eric-pachman"}
    publisher = {"@type": "Organization", "name": "Data 4 The People", "url": "https://data4thepeople.com"}
    n_g, n_r, n_c = len(gauges), len(rivers), len(countries)
    dataset = {
        "@type": "Dataset", "@id": PAGE_URL + "#dataset",
        "name": f"World River Levels: daily water level and flow at {n_g} gauges on {n_r} rivers",
        "description": (f"Daily water level and river flow records for {n_g} gauges on {n_r} rivers in {n_c} countries, "
                        f"from {min(firsts)} to {max(lasts)}, gathered from public government records. A water level is "
                        "the height of the water above a fixed mark at the gauge, called the gauge zero, not the depth "
                        "of the river. Each daily value is labeled measured, provisional or estimated, using the "
                        "publisher's own flags where they exist. Gaps are left as gaps, and values are stored in the "
                        "units each agency publishes."),
        "url": PAGE_URL, "sameAs": REPO_URL, "subjectOf": {"@type": "WebPage", "url": POST_URL},
        "license": "https://www.data4thepeople.com/terms-of-use", "isAccessibleForFree": True,
        "creator": author, "publisher": publisher, "inLanguage": "en-US",
        "temporalCoverage": f"{min(firsts)}/{max(lasts)}",
        "spatialCoverage": {"@type": "Place", "name": "Rivers in " + ", ".join(countries[:-1]) + " and " + countries[-1]},
        "variableMeasured": [
            {"@type": "PropertyValue", "name": "Water level above gauge zero", "unitText": "cm, mm, m or ft, as published"},
            {"@type": "PropertyValue", "name": "River flow (discharge)", "unitText": "m3/s, L/s or cfs, as published"}],
        "isBasedOn": sources,
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/zip",
                          "contentUrl": REPO_URL + "/archive/refs/heads/main.zip"}],
        "creditText": "Data 4 The People, from public records of the agencies listed in the dataset's sources",
    }
    app = {
        "@type": "WebApplication", "@id": PAGE_URL + "#tool", "name": "World River Levels", "url": PAGE_URL,
        "applicationCategory": "ReferenceApplication", "operatingSystem": "Web browser",
        "browserRequirements": "Requires JavaScript", "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "about": {"@id": PAGE_URL + "#dataset"}, "creator": publisher,
        "description": f"A free interactive map of daily river levels and flow at {n_g} gauges on {n_r} rivers, "
                       "with a slider and Play button to move through each gauge's record.",
    }
    return json.dumps({"@context": "https://schema.org", "@graph": [dataset, app]},
                      ensure_ascii=False).replace("</", "<\\/")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "dist/index.html", help="output file")
    args = ap.parse_args()
    cfg = json.loads((ROOT / "config/rivers.json").read_text())
    # rivers whose publisher requires permission to republish stay out of the page (config "excluded")
    cfg["rivers"] = [r for r in cfg["rivers"] if r["id"] not in cfg.get("excluded", {})]
    geo = json.loads((ROOT / "data/build/geo.json").read_text())
    gauges, missing = {}, []
    for r in cfg["rivers"]:
        for gid in r["gauges"]:
            if r.get("flow_only"):
                f = pack_flow(gid, cfg)
                if f is None:
                    missing.append(gid)
                    continue
                gauges[gid] = {
                    "name": cfg["flow_names"][gid], "country": cfg["flow_countries"][gid],
                    "lat": f["lat"], "lon": f["lon"], "kind": "flow", "flow_only": True,
                    "unit": f["unit"], "datum": f["unit_long"], "source": f["source"],
                    "first_date": f["first_date"], "last_date": f["last_date"], "start": f["start"], "n": f["n"],
                    "scale": f["scale"], "data": f["data"], "qruns": f["qruns"], "thresholds": [],
                    "public_notes": f["notes"], "breaks": cfg.get("breaks", {}).get(gid, []), "stats_from": None,
                    "history": [{"text": "How flow is labeled: " + f["flag_rule"], "url": ""}],
                    "flow": None, "flow_station": f["station_name"], "license": f["license"], "credit": f["credit"],
                }
                continue
            if not (PROC / f"{gid}.json").exists():
                missing.append(gid)
                continue
            m = json.loads((PROC / f"{gid}.json").read_text())
            start, n, scale, blob, runs = pack(gid, m["unit"], cfg)
            first_date = pd.Timestamp(DAY0) + pd.Timedelta(days=start)
            unit = m["unit"]
            if unit == "mm":  # display only: Hub'Eau publishes mm; show meters
                unit, scale = "m", 1000
            gauges[gid] = {
                "name": m["name"], "country": m["country"], "lat": m["lat"], "lon": m["lon"],
                "kind": m["kind"], "unit": unit, "datum": short_datum(m, unit), "source": m["source"],
                "first_date": first_date.strftime("%Y-%m-%d"), "last_date": m["last_date"],
                "start": start, "n": n, "scale": scale, "data": blob, "qruns": runs,
                "thresholds": cfg.get("thresholds", {}).get(gid, []),
                "public_notes": as_list(cfg.get("public_notes_override", {}).get(gid) or m.get("public_notes"))
                                + as_list(cfg.get("extra_notes", {}).get(gid))
                                + as_list((cfg.get("display_from", {}).get(gid) or {}).get("note")),
                "breaks": cfg.get("breaks", {}).get(gid, []),
                "stats_from": cfg.get("stats_from", {}).get(gid),
                "history": [{"text": "Reference point: " + m["datum"] + ".", "url": ""}]
                           + [history_item(h) for h in m.get("measurement_history", [])],
                "flow_only": False, "flow": pack_flow(gid, cfg),
            }
    rivers = [{k: r[k] for k in ("id", "name", "region", "about")}
              | {"gauges": [g for g in r["gauges"] if g in gauges], "flow_only": bool(r.get("flow_only"))}
              for r in cfg["rivers"]]
    rivers = [r for r in rivers if r["gauges"]]
    no_data = [{k: r[k] for k in ("id", "name", "note")} for r in cfg["no_data"]]
    keep = {r["id"] for r in rivers} | {r["id"] for r in no_data}
    geo["rivers"] = {k: v for k, v in geo["rivers"].items() if k in keep}
    payload = json.dumps({"geo": geo, "rivers": rivers, "no_data": no_data, "gauges": gauges},
                         separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "viz/template.html").read_text().replace("/*DATA*/", payload)
    for key, name in (("LOGO_DARK", "d4tp-text-dark.svg"), ("LOGO_LIGHT", "d4tp-text-light.svg")):
        svg = base64.b64encode((ROOT / "viz/logo" / name).read_bytes()).decode()
        html = html.replace(f"/*{key}*/", "data:image/svg+xml;base64," + svg)
    # shaded relief, made by scripts/relief.py: a separate file next to the page, so the map draws
    # first and the relief (about 2 MB) arrives after it
    html = html.replace("/*JSONLD*/", json_ld(rivers, gauges))
    html = html.replace("/*RELIEF*/", "relief.jpg")
    html = html.replace("/*RELIEF_META*/null", (ROOT / "viz/relief.json").read_text())
    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    shutil.copyfile(ROOT / "viz/relief.jpg", out.parent / "relief.jpg")
    nflow = sum(1 for g in gauges.values() if g["flow"] or g["flow_only"])
    print(f"wrote {out}: {out.stat().st_size/1e6:.2f} MB, {len(rivers)} rivers, {len(gauges)} gauges, {nflow} with flow")
    if missing:
        print("missing processed gauges:", ", ".join(missing))


if __name__ == "__main__":
    main()
