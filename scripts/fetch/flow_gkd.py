"""Bavarian GKD (Gewaesserkundlicher Dienst Bayern): daily mean discharge
(fluesse.abfluss, Tagesmittelwert, m3/s) for the Danube at Pfelling and
Hofkirchen. CC BY 4.0.

Download flow as in gkd_bayern.py: POST /de/downloadcenter/enqueue_download
with zr=gesamt, wertart=tmw, which returns a token URL; poll <token>&dl=1 until
it redirects (302) to a zip. Contract: scripts/fetch/FLOW.md.
"""
from __future__ import annotations

import json
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session, utm_to_latlon  # noqa: E402
from flow_common import write_flow  # noqa: E402
from gkd_bayern import parse  # noqa: E402

BASE = "https://www.gkd.bayern.de"
RAWDIR = RAW / "flow_gkd"
GAUGES = {
    "danube-pfelling": {"code": "10078000", "name": "Pfelling",
                        "page": f"{BASE}/de/fluesse/abfluss/kelheim/pfelling-10078000"},
    "danube-hofkirchen": {"code": "10088003", "name": "Hofkirchen",
                          "page": f"{BASE}/de/fluesse/abfluss/passau/hofkirchen-10088003"},
}
FLAG = {"Geprueft": "measured", "Rohdaten": "provisional"}


def download(s, code: str, dest: Path) -> None:
    get(s, f"{BASE}/de/fluesse/abfluss", pause=1)  # session cookie
    r = s.post(f"{BASE}/de/downloadcenter/enqueue_download", timeout=120,
               headers={"X-Requested-With": "XMLHttpRequest"},
               data={"zr": "gesamt", "beginn": "", "ende": "", "email": "", "geprueft": 0,
                     "wertart": "tmw", "t": json.dumps({code: ["fluesse.abfluss"]}), "f": ""})
    r.raise_for_status()
    link = r.json()["deeplink"]
    for _ in range(60):  # the zip is built server side; usually 20 to 40 s
        time.sleep(4)
        r = s.get(link + "&dl=1", allow_redirects=False, timeout=120)
        if r.status_code == 302:
            z = get(s, r.headers["Location"], timeout=300)
            tmp = dest.with_suffix(dest.suffix + ".part")
            tmp.write_bytes(z.content)
            zipfile.ZipFile(tmp).testzip()
            tmp.replace(dest)
            return
    raise RuntimeError(f"GKD zip for {code} not ready after 4 minutes")


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    for gid, g in GAUGES.items():
        path = RAWDIR / f"{g['code']}_abfluss_tmw_gesamt.zip"
        if args.refresh:
            download(s, g["code"], path)
        require_cache(path)
        raw, m = parse(path)
        flags = raw["Prüfstatus"].fillna("(empty)").value_counts().to_dict()
        # a day with no Pruefstatus is unchecked by definition: provisional, counted in notes
        no_flag = raw["Prüfstatus"].isna()
        no_flag_days = raw.loc[no_flag, "Datum"].astype(str).tolist()
        raw.loc[no_flag, "Prüfstatus"] = "Rohdaten"
        unknown = set(raw["Prüfstatus"]) - set(FLAG)
        if unknown:
            raise ValueError(f"{gid}: unknown Pruefstatus {unknown}")
        n_rows = len(raw)
        n_missing = int(raw["Mittelwert"].isna().sum())
        df = pd.DataFrame({"date": pd.to_datetime(raw["Datum"], format="%Y-%m-%d"),
                           "flow": raw["Mittelwert"], "quality": raw["Prüfstatus"].map(FLAG)}).dropna(subset=["flow"])
        n_neg = int((df.flow < 0).sum())
        df = df[df.flow >= 0]
        assert "UTM Zone 32N" in m["crs"], m
        lat, lon = utm_to_latlon(m["east"], m["north"], 32)
        prov = df[df.quality == "provisional"]
        has_minmax = [c for c in raw.columns if c not in ("Datum", "Mittelwert", "Prüfstatus")]
        meta = {
            "id": gid, "river": "danube", "name": g["name"],
            "station_name": g["name"], "station_code": g["code"],
            "country": "Germany", "lat": lat, "lon": lon,
            "same_station": True, "offset_note": "", "kind": "river flow", "unit": "m3/s",
            "daily_stat": "mean",
            "source": "Bayerisches Landesamt für Umwelt, Gewässerkundlicher Dienst Bayern (GKD), "
                      "download center, Abfluss Tagesmittelwerte",
            "source_url": f"{BASE}/de/downloadcenter/enqueue_download",
            "license": "CC BY 4.0",
            "credit": "Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de",
            "flag_rule": "GKD Pruefstatus 'Geprueft' (checked) is measured and 'Rohdaten' (raw) is provisional. "
                         "An empty Pruefstatus is provisional. GKD has no estimated flag.",
            "notes": [
                f"Discharge at {g['name']} is computed by GKD from the water level through a rating curve "
                "(Abflusskurve) that GKD updates from field measurements; ratings are revised as the riverbed "
                "changes, and the highest flood values lie beyond measured flows (GKD Bayern).",
                f"Pruefstatus counts in the file: {flags}"
                + (f"; raw (provisional) days run {prov.date.min():%Y-%m-%d} to {prov.date.max():%Y-%m-%d}"
                   if len(prov) else "") + " (GKD Bayern)."
                + (f" Days with an empty Pruefstatus, marked provisional because GKD has not marked them checked: "
                   f"{len(no_flag_days)} ({', '.join(no_flag_days[:5])})." if no_flag_days else ""),
                f"Rows in the file: {n_rows}. Rows with an empty daily mean dropped: {n_missing}. Negative values "
                f"dropped: {n_neg}. The current, unfinished day is published in its own file and left out "
                "(GKD Bayern).",
                f"The file also gives these daily columns, not used here: {', '.join(has_minmax)} (GKD Bayern).",
                f"Coordinates converted from ETRS89 / UTM 32N ({m['east']:.0f} E, {m['north']:.0f} N) in the file "
                f"header; database query time printed in the file: {m.get('queried')} (GKD Bayern).",
            ],
        }
        write_flow(df, meta)


if __name__ == "__main__":
    main()
