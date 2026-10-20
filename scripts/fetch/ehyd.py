"""Austria eHYD (Hydrographischer Dienst / BML): daily mean water level for the
Danube at Kienstock (HZB 207357), from the published yearbook series.

Files: MessstellenExtraData/owf?id=<hzb>&file=1 (station master data) and
file=2 (W-Tagesmittel, daily mean level). Coordinates from the PegelAktuell
GeoJSON layer used by the eHYD map.
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session, write_gauge  # noqa: E402

BASE = "https://ehyd.gv.at/services"
RAWDIR = RAW / "ehyd"
GAUGES = {"danube-kienstock": {"hzb": "207357", "name": "Kienstock", "river": "danube"}}


def read_text(p: Path) -> str:
    return p.read_bytes().decode("latin1")


def parse_values(text: str):
    head, body = text.split("Werte:", 1)
    rows, gaps = [], 0
    for line in body.strip().splitlines():
        t, v = [x.strip() for x in line.split(";", 1)]
        if v in ("Lücke", "L�cke"):
            gaps += 1
            continue
        rows.append((pd.to_datetime(t, format="%d.%m.%Y %H:%M:%S"), float(v.replace(",", "."))))
    df = pd.DataFrame(rows, columns=["date", "level"])
    return head, df, gaps


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    coords_path = RAWDIR / "PegelAktuell.json"
    if args.refresh:
        coords_path.write_bytes(get(s, f"{BASE}/PegelAktuell/json", pause=1).content)
    require_cache(coords_path)
    feats = json.loads(coords_path.read_text())["features"]
    for gid, g in GAUGES.items():
        files = {k: RAWDIR / f"{g['hzb']}_file{k}.csv" for k in (1, 2)}
        if args.refresh:
            for k, p in files.items():
                p.write_bytes(get(s, f"{BASE}/MessstellenExtraData/owf?id={g['hzb']}&file={k}", pause=1).content)
        for p in files.values():
            require_cache(p)
        stamm = read_text(files[1])
        head, df, gaps = parse_values(read_text(files[2]))
        unit = re.search(r"Einheit:\s*;\[(\w+)\]", head).group(1)
        span = re.search(r"Exportzeitraum:\s*;\[([^\]]+)\]", head).group(1)
        pnp = re.findall(r"^\s+(\d\d\.\d\d\.\d{4})\s+;(\d+,\d+)\s*$",
                         stamm.split("Pegelnullpunkt:")[1].split("Bundesmeldenetz")[0], re.M)
        pnp_txt = "; ".join(f"{float(h.replace(',', '.')):.2f} m above Adriatic (m ü.A.) from {d}" for d, h in pnp)
        messart = re.findall(r"^\s+(\d\d\.\d\d\.\d{4})\s+(\d\d\.\d\d\.\d{4})?\s*;\S+/OWF-W/(.+?)\s*$", stamm, re.M)
        foot = re.findall(r"^\s+(\d\d\.\d\d\.\d{4})\s+(\d\d\.\d\d\.\d{4})?\s*;OWF-(\w+)/(.+?)\s*$", stamm, re.M)
        filled_q = [f"{a[6:]}: {t}" for a, b, par, t in foot if par in ("Q", "WT") and "ergänzt" in t]
        w_notes = [f"{a}: {t}" for a, b, par, t in foot if par == "W"]
        f = next(x for x in feats if str(x["properties"]["hzbnr"]) == g["hzb"])
        lon, lat = f["geometry"]["coordinates"]
        fill = df["level"].abs() >= 9999
        n_fill = int(fill.sum())
        df = df[~fill].copy()
        # the series is dated at 00:00 of each day; the export ends with a gap marker on the next day
        df["quality"] = "measured"
        meta = {
            "id": gid, "river": g["river"], "name": g["name"], "country": "Austria",
            "lat": round(lat, 6), "lon": round(lon, 6), "kind": "river",
            "source": "eHYD, Hydrographischer Dienst Österreich (BML); station operator via donau",
            "source_url": f"{BASE}/MessstellenExtraData/owf?id={g['hzb']}&file=2",
            "station_code": f"HZB {g['hzb']}", "unit": unit,
            "datum": f"cm above gauge zero ({pnp_txt})", "daily_stat": "mean",
            "license": "CC BY 4.0 (Open Government Data Austria, per the INSPIRE metadata record; not shown on "
                       "ehyd.gv.at itself). Required credit: Datenquelle: ehyd.gv.at (linked to https://ehyd.gv.at)",
            "notes": [
                f"Daily mean water level (W-Tagesmittel) from the eHYD yearbook export, period {span}. "
                "eHYD publishes only checked yearbook (Hydrographisches Jahrbuch) data, so the series ends "
                "with the last published yearbook year.",
                "eHYD gives no per-value quality flag; every value is marked measured.",
                f"Gap markers ('Lücke') skipped: {gaps}. Fill values dropped: {n_fill}.",
                "Station master data list these level methods (start, end, method): "
                + "; ".join(f"{a} to {b or 'now'}: {t}" for a, b, t in messart) + ".",
                "Footnotes on discharge and water temperature say that in some months they were computed "
                "from supplemented (filled) water levels, for example: " + "; ".join(filled_q[:6])
                + f" ({len(filled_q)} such footnotes in all). The level series itself carries no flag for "
                "these days, so they stay marked measured.",
            ] + ([f"Footnotes on the level series: {'; '.join(w_notes)}."] if w_notes else []) + [
                "Coordinates from the eHYD PegelAktuell map layer (WGS84).",
            ],
        }
        write_gauge(df, meta)


if __name__ == "__main__":
    main()
