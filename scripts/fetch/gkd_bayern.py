"""Bavarian GKD (Gewaesserkundlicher Dienst Bayern): daily mean water level for
Danube gauges Hofkirchen and Pfelling. CC BY 4.0.

Download flow (no key, no email): POST /de/downloadcenter/enqueue_download with
zr=gesamt, wertart=tmw (daily values), which returns a token URL; poll
<token>&dl=1 until it redirects (302) to a zip on download.gkd.bayern.de.
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session, utm_to_latlon, write_gauge  # noqa: E402

BASE = "https://www.gkd.bayern.de"
RAWDIR = RAW / "gkd_bayern"
GAUGES = {
    "danube-hofkirchen": {"code": "10088003", "name": "Hofkirchen",
                          "page": f"{BASE}/de/fluesse/wasserstand/passau/hofkirchen-10088003"},
    "danube-pfelling": {"code": "10078000", "name": "Pfelling",
                        "page": f"{BASE}/de/fluesse/wasserstand/kelheim/pfelling-10078000"},
}
FLAG = {"Geprueft": "measured", "Rohdaten": "provisional"}


def download(s, code: str, dest: Path) -> None:
    get(s, f"{BASE}/de/fluesse/wasserstand", pause=1)  # session cookie
    r = s.post(f"{BASE}/de/downloadcenter/enqueue_download", timeout=120,
               headers={"X-Requested-With": "XMLHttpRequest"},
               data={"zr": "gesamt", "beginn": "", "ende": "", "email": "", "geprueft": 0,
                     "wertart": "tmw", "t": json.dumps({code: ["fluesse.wasserstand"]}), "f": ""})
    r.raise_for_status()
    link = r.json()["deeplink"]
    for _ in range(60):  # the zip is built server side; usually 20 to 40 s
        time.sleep(4)
        r = s.get(link + "&dl=1", allow_redirects=False, timeout=120)
        if r.status_code == 302:
            z = get(s, r.headers["Location"], timeout=300)
            zipfile.ZipFile(io.BytesIO(z.content)).testzip()
            dest.write_bytes(z.content)
            return
    raise RuntimeError(f"GKD zip for {code} not ready after 4 minutes")


def parse(path: Path):
    frames, header = [], None
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if not name.endswith(".csv"):
                continue
            # a file named <code>_<DD.MM.YYYY>_tmw_0.csv holds only the current, unfinished day
            if re.search(r"(^|/)\d+_\d\d\.\d\d\.\d{4}_tmw", name):
                continue
            blob = zf.read(name)
            try:  # the site says ISO 8859-1, but the files arrive as UTF-8 with a BOM
                text = blob.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = blob.decode("latin1")
            lines = text.splitlines()
            start = next(i for i, l in enumerate(lines) if l.startswith("Datum;"))
            if header is None:
                header = lines[:start]
            df = pd.read_csv(io.StringIO("\n".join(lines[start:])), sep=";", decimal=",")
            frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    meta = {}
    for l in header:
        parts = [p.strip().strip('"') for p in l.split(";")]
        if parts[0] == "Ostwert:":
            meta["east"], meta["north"] = float(parts[1]), float(parts[3])
            meta["crs"] = parts[4] if len(parts) > 4 else ""
        elif parts[0] == "Pegelnullpunktshöhe:":
            meta["pnp"] = re.sub(r"(\d),(\d)", r"\1.\2", parts[1])
        elif parts[0] == "Datenbankabfrage:":
            meta["queried"] = parts[1]
    return df, meta


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    for gid, g in GAUGES.items():
        path = RAWDIR / f"{g['code']}_tmw_gesamt.zip"
        if args.refresh:
            download(s, g["code"], path)
        require_cache(path)
        raw, m = parse(path)
        flags = raw["Prüfstatus"].value_counts().to_dict()
        unknown = set(flags) - set(FLAG)
        if unknown:
            raise ValueError(f"{gid}: unknown Pruefstatus {unknown}")
        n_missing = int(raw["Mittelwert"].isna().sum())
        df = pd.DataFrame({"date": raw["Datum"], "level": raw["Mittelwert"],
                           "quality": raw["Prüfstatus"].map(FLAG)}).dropna(subset=["level"])
        assert "UTM Zone 32N" in m["crs"], m
        lat, lon = utm_to_latlon(m["east"], m["north"], 32)
        prov = df[df.quality == "provisional"]
        notes = [
            "Daily mean (Tagesmittelwert) of the water level in cm above gauge zero, from the GKD "
            "download center (Gesamtzeitraum, Tageswerte).",
            f"Quality from the GKD Pruefstatus column: 'Geprueft' (checked) -> measured, 'Rohdaten' "
            f"(raw) -> provisional. Counts in the file: {flags}.",
            f"Provisional (Rohdaten) days run from {prov.date.min()} to {prov.date.max()}." if len(prov) else
            "No provisional days.",
            f"Rows with an empty daily mean dropped: {n_missing}. No fill values (such as -999) found.",
            "The current, unfinished day is published in its own file and is left out.",
            f"Gauge zero as stated in the file header: {m['pnp']}. It is a single current value; the file "
            "does not list earlier gauge zeros, so a past datum change would not be visible here.",
            f"Coordinates converted from ETRS89 / UTM 32N ({m['east']:.0f} E, {m['north']:.0f} N) in the file header.",
            f"GKD database query time printed in the file: {m.get('queried')}.",
        ]
        meta = {
            "id": gid, "river": "danube", "name": g["name"], "country": "Germany",
            "lat": lat, "lon": lon, "kind": "river",
            "source": "Bayerisches Landesamt für Umwelt, Gewässerkundlicher Dienst Bayern (GKD)",
            "source_url": g["page"], "station_code": g["code"], "unit": "cm",
            "datum": f"cm above gauge zero ({m['pnp']})", "daily_stat": "mean",
            "license": "CC BY 4.0. Required credit: Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de",
            "notes": notes,
        }
        write_gauge(df, meta)


if __name__ == "__main__":
    main()
