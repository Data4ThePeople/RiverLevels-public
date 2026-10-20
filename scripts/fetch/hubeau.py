"""France Hub'Eau hydrometrie API (no key): daily maximum water level (HIXnJ)
for the Seine at Paris-Austerlitz (four station codes stitched) and Melun.
Licence Ouverte / Etalab 2.0.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session, write_gauge  # noqa: E402

API = "https://hubeau.eaufrance.fr/api/v2/hydrometrie"
RAWDIR = RAW / "hubeau"
# Paris-Austerlitz station codes, each used only inside its own window.
PARIS = [("F700000109", "1900-01-01", "1965-12-31"),
         ("F700000110", "1966-01-01", "1973-12-31"),
         ("F700000111", "1974-01-01", "1989-12-31"),
         ("F700000102", "1990-01-01", "2100-01-01")]
CHECK_ONLY = ["F700000103"]  # post-2006 flow station, used only to check 102's reference
MELUN = "F447000101"
STATIONS = [c for c, _, _ in PARIS] + CHECK_ONLY + [MELUN]
# Sandre nomenclature 512 (methode d'obtention, elaborated data): 0 Mesure, 8 Calcule (automatic
# computation from readings), 10 Expertise (value modified by a hydrologist) -> measured;
# 4 Reconstitue (created by a contributor), 12 Interpolation, 14 Estime, 16 Valeur forcee -> estimated.
# https://api.sandre.eaufrance.fr/referentiels/v1/nsa/512.json
METHOD_MEASURED = {0, 8, 10}
# Sandre 510 (code_statut): 0 sans validation, 4 brute, 8 corrigee, 12 pre-validee, 16 validee.
# Sandre 515 (code_qualification): 30 Estimee -> estimated.
LICENSE = ("Not stated by Hub'Eau or HydroPortail (checked 2026-10-15). French public data usually fall under "
           "Licence Ouverte / Etalab 2.0, but that is unconfirmed for this API; clear before republishing. "
           "Credit: Hub'Eau / HydroPortail (Schapi, Ministere de la Transition ecologique)")


QUALITY_NOTE = ("Quality: code_statut 16 (Donnee validee) with method Mesuree, Calculee or Expertisee "
                "(edited by a hydrologist) -> measured; validated with method Reconstituee, Interpolation, "
                "Estimee or Valeur forcee, or qualification Estimee -> estimated; any status below 16 (raw, "
                "corrected, pre-validated) -> provisional, because the publisher has not validated it. "
                "Qualification Douteuse (doubtful) values are kept and counted in these notes. Hub'Eau dates are UTC.")


def fetch_series(s, code: str) -> list[dict]:
    url = f"{API}/obs_elab?code_entite={code}&grandeur_hydro_elab=HIXnJ&size=20000"
    rows = []
    while url:
        d = get(s, url, pause=0.5).json()
        rows.extend(d["data"])
        url = d.get("next") if d["data"] else None
        if len(rows) > d["count"]:
            raise RuntimeError(f"{code}: paging returned more rows than count")
    if len(rows) != d["count"]:
        raise RuntimeError(f"{code}: got {len(rows)} rows, API count {d['count']}")
    return rows


def frame(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    return df[["code_station", "date_obs_elab", "resultat_obs_elab", "code_statut", "libelle_statut",
               "code_methode", "libelle_methode", "code_qualification", "libelle_qualification"]]


def quality(df: pd.DataFrame) -> pd.Series:
    q = pd.Series("measured", index=df.index)
    q[~df.code_methode.isin(METHOD_MEASURED) | (df.code_qualification == 30)] = "estimated"
    q[df.code_statut != 16] = "provisional"  # 16 = Donnee validee; 4/8/12 are raw/corrected/pre-validated
    return q


def describe_flags(df: pd.DataFrame) -> str:
    parts = []
    for col in ["libelle_statut", "libelle_methode", "libelle_qualification"]:
        parts.append(f"{col.replace('libelle_', '')}: {df[col].value_counts().to_dict()}")
    return "; ".join(parts)


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    meta_path = RAWDIR / "stations.json"
    if args.refresh:
        r = get(s, f"{API}/referentiel/stations?code_station={','.join(STATIONS)}&format=json&size=50")
        meta_path.write_text(json.dumps(r.json()["data"], indent=1, ensure_ascii=False))
        for code in STATIONS:
            rows = fetch_series(s, code)
            (RAWDIR / f"{code}_HIXnJ.json").write_text(json.dumps(rows, ensure_ascii=False))
    require_cache(meta_path)
    st = {m["code_station"]: m for m in json.loads(meta_path.read_text())}
    data = {}
    for code in STATIONS:
        p = RAWDIR / f"{code}_HIXnJ.json"
        require_cache(p)
        data[code] = frame(json.loads(p.read_text()))

    # ---- reference check across the Paris codes
    refs = {c: (st[c]["altitude_ref_alti_station"], st[c]["code_systeme_alti_site"],
                st[c]["date_debut_ref_alti_station"][:10]) for c in STATIONS if c != MELUN}
    alts = {v[0] for v in refs.values()}
    if len(alts) != 1:
        raise SystemExit(f"Paris station references differ: {refs}; do not stitch without an offset")
    a = data["F700000102"].set_index("date_obs_elab")["resultat_obs_elab"]
    b = data["F700000103"].set_index("date_obs_elab")["resultat_obs_elab"]
    ov = (a - b).dropna()
    boundary = []
    pieces, notes_paris = [], []
    for code, lo, hi in PARIS:
        d = data[code]
        dd = d[(d.date_obs_elab >= lo) & (d.date_obs_elab <= hi)].copy()
        out = len(d) - len(dd)
        notes_paris.append(f"{code} ({st[code]['libelle_station']}): {len(dd)} days used "
                           f"{dd.date_obs_elab.min()} to {dd.date_obs_elab.max()}, {out} outside its window dropped. "
                           + describe_flags(dd))
        dd["quality"] = quality(dd)
        pieces.append(dd)
    for (c1, _, h1), (c2, l2, _) in zip(PARIS, PARIS[1:]):
        x = pieces[[p for p, _, _ in PARIS].index(c1)]
        y = pieces[[p for p, _, _ in PARIS].index(c2)]
        boundary.append(f"{c1} last 30 days median {x.resultat_obs_elab.tail(30).median():.0f} mm, "
                        f"{c2} first 30 days median {y.resultat_obs_elab.head(30).median():.0f} mm")
    paris = pd.concat(pieces)
    paris = paris.rename(columns={"date_obs_elab": "date", "resultat_obs_elab": "level"})
    pm = st["F700000102"]
    write_gauge(paris, {
        "id": "seine-paris", "river": "seine", "name": "Paris-Austerlitz", "country": "France",
        "lat": round(pm["latitude_station"], 6), "lon": round(pm["longitude_station"], 6), "kind": "river",
        "source": "Hub'Eau hydrometrie API (Schapi / DRIEAT, HydroPortail)",
        "source_url": f"{API}/obs_elab?code_entite=F700000102&grandeur_hydro_elab=HIXnJ",
        "station_code": "F700000109 (1900-1965), F700000110 (1966-1973), F700000111 (1974-1989), F700000102 (1990-)",
        "unit": "mm", "datum": f"mm above the station reference ({pm['altitude_ref_alti_station']} m, "
                               f"altimetric system code {pm['code_systeme_alti_site']}, NGF-IGN69)",
        "daily_stat": "max",
        "license": LICENSE,
        "notes": [
            "Daily maximum water level (HIXnJ) in millimeters as published. Not converted.",
            "Stitched from four Hub'Eau station codes at the same site (code_site F7000001), each used only "
            "inside its operating window, with no overlap and no offset applied.",
            f"Reference check: all Paris-Austerlitz codes list the same station reference altitude "
            f"({sorted(alts)[0]} m; altimetric system code 3 = NGF-IGN69, except F700000111 which records code "
            f"{st['F700000111']['code_systeme_alti_site']} (unknown) with the same altitude). Reference start dates: "
            + ", ".join(f"{c} {v[2]}" for c, v in refs.items()) + ".",
            f"Overlap check: F700000102 vs F700000103 (2006 on, not used in the series) share {len(ov)} days; "
            f"median difference {ov.median():.0f} mm, 90% of differences within "
            f"{ov.abs().quantile(0.9):.0f} mm.",
            "Boundary check (no shared days, so this compares neighboring months only): " + "; ".join(boundary) + ".",
            "Pre-1966 values come from observer readings (about 7 am, more often in floods), so the "
            "'daily maximum' then is often a single reading.",
            QUALITY_NOTE,
            "The level is influenced by the Suresnes dam downstream and upstream reservoirs (station metadata).",
        ] + notes_paris,
    })

    m = data[MELUN].copy()
    m["quality"] = quality(m)
    mm = st[MELUN]
    m = m.rename(columns={"date_obs_elab": "date", "resultat_obs_elab": "level"})
    write_gauge(m, {
        "id": "seine-melun", "river": "seine", "name": "Melun", "country": "France",
        "lat": round(mm["latitude_station"], 6), "lon": round(mm["longitude_station"], 6), "kind": "river",
        "source": "Hub'Eau hydrometrie API (Schapi / HydroPortail)",
        "source_url": f"{API}/obs_elab?code_entite={MELUN}&grandeur_hydro_elab=HIXnJ",
        "station_code": MELUN, "unit": "mm",
        "datum": f"mm above the station reference ({mm['altitude_ref_alti_station']} m, altimetric system code "
                 f"{mm['code_systeme_alti_site']}, NGF-IGN69; reference valid from {mm['date_debut_ref_alti_station'][:10]})",
        "daily_stat": "max",
        "license": LICENSE,
        "notes": [
            "Daily maximum water level (HIXnJ) in millimeters as published. Not converted.",
            QUALITY_NOTE,
            "Flags in the data: " + describe_flags(m),
            "Station metadata: strongly influenced by the Vives Eaux dam, so no flow is published; height data "
            "described as good quality. Daily observer readings in early years.",
            f"The station reference record starts {mm['date_debut_ref_alti_station'][:10]}; the API gives no "
            "earlier reference, so a pre-2004 datum change cannot be ruled out from metadata alone.",
        ],
    })


if __name__ == "__main__":
    main()
