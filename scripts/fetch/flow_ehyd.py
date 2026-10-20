"""Austria eHYD (Hydrographischer Dienst / BML): daily mean discharge
(Q-Tagesmittel, m3/s) for the Danube at Kienstock (HZB 207357), from the
published yearbook series.

Files: MessstellenExtraData/owf?id=<hzb>&file=1 (station master data, with
footnotes) and file=5 (Q-Tagesmittel). Coordinates from the PegelAktuell
GeoJSON layer used by the eHYD map. Contract: scripts/fetch/FLOW.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session  # noqa: E402
from flow_common import write_flow  # noqa: E402

BASE = "https://ehyd.gv.at/services"
RAWDIR = RAW / "flow_ehyd"
HZB = "207357"
MONTHS = {"Jän": 1, "Feb": 2, "Mrz": 3, "Apr": 4, "Mai": 5, "Jun": 6, "Jul": 7, "Aug": 8,
          "Sep": 9, "Okt": 10, "Nov": 11, "Dez": 12}


def fetch(s, url: str, path: Path, refresh: bool) -> Path:
    if refresh:
        tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_bytes(get(s, url, pause=1).content)
        tmp.replace(path)
    require_cache(path)
    return path


def parse_values(text: str):
    head, body = text.split("Werte:", 1)
    rows, gaps = [], []
    for line in body.strip().splitlines():
        t, v = [x.strip() for x in line.split(";", 1)]
        d = pd.to_datetime(t, format="%d.%m.%Y %H:%M:%S")
        if v in ("Lücke", "L�cke"):
            gaps.append(d)
            continue
        rows.append((d, float(v.replace(",", "."))))
    return head, pd.DataFrame(rows, columns=["date", "flow"]), gaps


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    coords = fetch(s, f"{BASE}/PegelAktuell/json", RAWDIR / "PegelAktuell.json", args.refresh)
    f1 = fetch(s, f"{BASE}/MessstellenExtraData/owf?id={HZB}&file=1", RAWDIR / f"{HZB}_file1.csv", args.refresh)
    f5 = fetch(s, f"{BASE}/MessstellenExtraData/owf?id={HZB}&file=5", RAWDIR / f"{HZB}_file5.csv", args.refresh)
    stamm = f1.read_bytes().decode("latin1")
    head, df, gaps = parse_values(f5.read_bytes().decode("latin1"))
    unit = re.search(r"Einheit:\s*;\[([^\]]+)\]", head).group(1)
    assert unit == "m³/s", unit
    series = re.search(r"Exportzeitreihe:\s*;\((.+?)\)", head).group(1)
    assert ",Abfluss," in series and ",Mit,T," in series, series
    span = re.search(r"Exportzeitraum:\s*;\[([^\]]+)\]", head).group(1)
    q_methods = re.findall(r"^\s+(\d\d\.\d\d\.\d{4})\s+(\d\d\.\d\d\.\d{4})?\s*;\S+/OWF-Q/(.+?)\s*$", stamm, re.M)
    foot = re.findall(r"^\s+(\d\d\.\d\d\.\d{4})\s+(\d\d\.\d\d\.\d{4})?\s*;OWF-Q/(.+?)\s*$", stamm, re.M)
    # Footnotes that say Q was computed from filled-in levels or that data were filled ("ergänzt") mark
    # those months estimated; the footnotes name months, not days, so the whole month is marked.
    # Footnotes that say discharge was affected by ice ("durch Eis beeinflusst") mark those months estimated
    # too, matching how USGS and ECCC label ice-affected days (Eric, October 19, 2026).
    filled, iced, ice, other = set(), set(), [], []
    for a, b, text in foot:
        year = int(a[6:])
        months = [MONTHS[m] for m in re.findall(r"\b(" + "|".join(MONTHS) + r")\b", text)]
        if "ergänzt" in text and months:
            filled.update((year, m) for m in months)
        elif "Eis" in text:
            if not months:
                raise SystemExit(f"ice footnote names no month, decide how to flag it: {a}: {text}")
            iced.update((year, m) for m in months)
            ice.append(f"{year}: {text}")
        else:
            other.append(f"{a}: {text}")
    n_rows = len(df)
    full = pd.date_range(df.date.min(), df.date.max(), freq="D")
    n_missing_days = len(full) - df.date.nunique()
    n_neg = int((df.flow < 0).sum())
    fill = df.flow.abs() >= 99999
    n_fill = int(fill.sum())
    df = df[~fill & (df.flow >= 0)].copy()
    ym = list(zip(df.date.dt.year, df.date.dt.month))
    df["quality"] = ["estimated" if k in filled or k in iced else "measured" for k in ym]
    feats = json.loads(coords.read_text())["features"]
    f = next(x for x in feats if str(x["properties"]["hzbnr"]) == HZB)
    lon, lat = f["geometry"]["coordinates"]
    filled_txt = ", ".join(f"{y}-{m:02d}" for y, m in sorted(filled))
    meta = {
        "id": "danube-kienstock", "river": "danube", "name": "Kienstock",
        "station_name": "Kienstock", "station_code": f"HZB {HZB}",
        "country": "Austria", "lat": round(lat, 6), "lon": round(lon, 6),
        "same_station": True, "offset_note": "", "kind": "river flow", "unit": "m3/s",
        "daily_stat": "mean",
        "source": "eHYD, Hydrographischer Dienst Österreich (BML), yearbook series Q-Tagesmittel; "
                  "station operator via donau",
        "source_url": f"{BASE}/MessstellenExtraData/owf",
        "license": "CC BY 4.0 (Open Government Data Austria, per the INSPIRE metadata record; not shown on "
                   "ehyd.gv.at itself)",
        "credit": "Datenquelle: ehyd.gv.at",
        "flag_rule": "eHYD gives no per-value flag, so values are measured, except whole months whose station "
                     "footnote says discharge was computed from filled-in levels, that data were filled "
                     "('ergänzt'), or that discharge was affected by ice ('durch Eis beeinflusst'); those are "
                     "estimated.",
        "notes": [
            "Discharge at Kienstock is computed from the water level through a rating curve (Pegelschlüssel); "
            "the station master data list these discharge methods (start, end, method): "
            + "; ".join(f"{a} to {b or 'now'}: {t}" for a, b, t in q_methods) + " (eHYD).",
            f"Daily mean discharge from the eHYD yearbook export, series ({series}), period {span}. eHYD "
            "publishes only checked yearbook data, so the series ends with the last published yearbook year, "
            "2023 (eHYD).",
            f"Months marked estimated because a footnote says discharge was computed from filled-in levels or "
            f"from filled data: {len(filled)} ({filled_txt}). The footnotes do not say which days, so every day "
            "of those months is marked (eHYD station master data).",
            "Footnotes say discharge was affected by ice in: " + "; ".join(ice)
            + f". Those {len(iced)} months are marked estimated, like ice-affected days at USGS and ECCC gauges "
            "(eHYD station master data)." if ice else
            "No ice footnotes for discharge (eHYD).",
        ] + ([f"Other discharge footnotes: {'; '.join(other)} (eHYD)."] if other else []) + [
            f"Rows in the file: {n_rows}; calendar days missing between first and last value: {n_missing_days}. "
            f"Gap markers ('Lücke') skipped: {len(gaps)}"
            + (f" ({', '.join(f'{g:%Y-%m-%d}' for g in gaps)}; a marker on the day after the last value only "
               "closes the series)" if gaps else "")
            + f". Fill values dropped: {n_fill}. Negative values dropped: {n_neg} (eHYD).",
            "Coordinates from the eHYD PegelAktuell map layer, WGS84 (eHYD).",
        ],
    }
    write_flow(df[["date", "flow", "quality"]], meta)


if __name__ == "__main__":
    main()
