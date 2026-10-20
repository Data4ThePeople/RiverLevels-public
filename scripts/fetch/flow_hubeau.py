"""France Hub'Eau hydrometrie API (no key): daily mean flow (QmnJ, L/s) for the
Seine at Paris-Austerlitz, on the same station chain as the level series
(hubeau.py): F700000109, F700000110, F700000111, F700000102 to 2005, then the
Austerlitz flow station F700000103 from 2006 on, where Hub'Eau publishes Paris
flow after 2005. Each station is used only inside its own window. Joined
October 20, 2026, after the independent tie-out found 2006 to 2026 missing.

Every API page is saved raw as data/raw/flow_hubeau/<code>_QmnJ_p<NNN>.json.
Contract: scripts/fetch/FLOW.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session  # noqa: E402
from flow_common import write_flow  # noqa: E402
from hubeau import LICENSE, METHOD_MEASURED, PARIS, describe_flags, frame  # noqa: E402

API = "https://hubeau.eaufrance.fr/api/v2/hydrometrie"
RAWDIR = RAW / "flow_hubeau"
# the level chain, except that from 2006 on flow comes from the Austerlitz flow station F700000103
CHAIN = [(c, lo, hi) for c, lo, hi in PARIS if c != "F700000102"] + [
    ("F700000102", "1990-01-01", "2005-12-31"), ("F700000103", "2006-01-01", "2100-01-01")]
CODES = [c for c, _, _ in CHAIN]
DOUBTFUL = 12  # Sandre 515 code_qualification: 12 Douteuse, 16 Bonne, 20 non qualifiee, 30 Estimee


def write_raw(path: Path, blob: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(blob)
    tmp.replace(path)


def download(s, code: str) -> None:
    for old in RAWDIR.glob(f"{code}_QmnJ_p*.json"):
        old.unlink()
    url = f"{API}/obs_elab?code_entite={code}&grandeur_hydro_elab=QmnJ&size=20000"
    n, i = 0, 0
    while url:
        r = get(s, url, pause=0.5, timeout=300)
        write_raw(RAWDIR / f"{code}_QmnJ_p{i:03d}.json", r.content)
        d = r.json()
        n += len(d["data"])
        url = d.get("next") if d["data"] else None
        i += 1
    if n != d["count"]:
        raise RuntimeError(f"{code}: got {n} rows, API count {d['count']}")


def load(code: str) -> pd.DataFrame:
    pages = sorted(RAWDIR.glob(f"{code}_QmnJ_p*.json"))
    if not pages:
        raise SystemExit(f"missing raw cache for {code} in {RAWDIR}; run with --refresh")
    rows, count = [], None
    for p in pages:
        d = json.loads(p.read_text())
        rows.extend(d["data"])
        count = d["count"]
    if len(rows) != count:
        raise SystemExit(f"{code}: cache has {len(rows)} rows, API count {count}; run with --refresh")
    df = frame(rows)
    assert (pd.DataFrame(rows)["grandeur_hydro_elab"] == "QmnJ").all()
    return df


def quality(df: pd.DataFrame) -> pd.Series:
    """Validated (16) -> measured; validated but reconstructed, interpolated, estimated or forced method, or
    qualification Estimee (30) -> estimated; any status below 16 (raw, corrected, pre-validated) -> provisional.
    Doubtful qualification does not change the class; it is counted in the notes."""
    q = pd.Series("measured", index=df.index)
    q[~df.code_methode.isin(METHOD_MEASURED) | (df.code_qualification == 30)] = "estimated"
    q[df.code_statut != 16] = "provisional"
    return q


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    st_path = RAWDIR / "stations.json"
    if args.refresh:
        r = get(s, f"{API}/referentiel/stations?code_station={','.join(CODES)}&format=json&size=50", timeout=300)
        write_raw(st_path, r.content)
        for code in CODES:
            download(s, code)
    require_cache(st_path)
    st = {m["code_station"]: m for m in json.loads(st_path.read_text())["data"]}
    data = {c: load(c) for c in CODES}

    # overlap: days that more than one chain station publishes
    alld = pd.concat([d[["date_obs_elab", "code_station"]] for d in data.values()])
    per_day = alld.groupby("date_obs_elab").code_station.nunique()
    overlap = per_day[per_day > 1]
    pieces, notes_st = [], []
    for code, lo, hi in CHAIN:
        d = data[code]
        dd = d[(d.date_obs_elab >= lo) & (d.date_obs_elab <= hi)].copy()
        out = d[(d.date_obs_elab < lo) | (d.date_obs_elab > hi)]
        dd["quality"] = quality(dd)
        n_dbt = int((dd.code_qualification == DOUBTFUL).sum())
        notes_st.append(
            f"{code} ({st[code]['libelle_station']}): {len(dd)} days used, {dd.date_obs_elab.min()} to "
            f"{dd.date_obs_elab.max()}; {len(out)} days outside its window dropped"
            + (f" ({out.date_obs_elab.min()} to {out.date_obs_elab.max()})" if len(out) else "")
            + f"; {n_dbt} days qualified doubtful. Flags: {describe_flags(dd)} (Hub'Eau).")
        pieces.append(dd)
    paris = pd.concat(pieces)
    n_raw = len(paris)
    n_nan = int(paris.resultat_obs_elab.isna().sum())
    nan_years = paris[paris.resultat_obs_elab.isna()].date_obs_elab.str[:4].value_counts().sort_index().to_dict()
    n_neg = int((paris.resultat_obs_elab < 0).sum())
    paris = paris[paris.resultat_obs_elab.notna() & (paris.resultat_obs_elab >= 0)]
    # agreement between the two Austerlitz stations on days both publish a flow from 2006 on
    a, b = data["F700000102"], data["F700000103"]
    both = a[a.date_obs_elab >= "2006-01-01"].merge(b, on="date_obs_elab", suffixes=("_102", "_103"))
    both = both[both.resultat_obs_elab_102.notna() & both.resultat_obs_elab_103.notna()]
    rel = (both.resultat_obs_elab_102 / both.resultat_obs_elab_103 - 1) * 100
    join_note = (f"On {len(both)} days from 2006 on that both F700000102 and F700000103 publish a flow, "
                 f"F700000102 differs from F700000103 by a median {rel.median():+.1f}% (5th to 95th percentile "
                 f"{rel.quantile(.05):+.1f}% to {rel.quantile(.95):+.1f}%) (Hub'Eau).") if len(both) else (
                 "F700000102 and F700000103 publish no flow on the same day from 2006 on, so the join could not "
                 "be checked against an overlap (Hub'Eau).")
    dbt = paris[paris.code_qualification == DOUBTFUL]
    dbt_dec = (dbt.date_obs_elab.str[:3] + "0s").value_counts().sort_index().to_dict()
    prov = paris[paris.quality == "provisional"]
    pm = st["F700000102"]
    meta = {
        "id": "seine-paris", "river": "seine", "name": "Paris-Austerlitz",
        "station_name": "La Seine à Paris - Austerlitz",
        "station_code": "F700000109 (1900-1965), F700000110 (1966-1973), F700000111 (1974-1989), "
                        "F700000102 (1990-2005), F700000103 (2006-)",
        "country": "France", "lat": round(pm["latitude_station"], 6), "lon": round(pm["longitude_station"], 6),
        "same_station": True, "offset_note": "", "kind": "river flow", "unit": "L/s",
        "daily_stat": "mixed",
        "source": "Hub'Eau hydrometrie API, obs_elab QmnJ (Schapi / DRIEAT, HydroPortail)",
        "source_url": f"{API}/obs_elab",
        "license": LICENSE.split(" Credit:")[0],
        "credit": "Hub'Eau / HydroPortail (Schapi, Ministère de la Transition écologique)",
        "flag_rule": "Status validated is measured, unless the method is reconstructed, interpolated, estimated or "
                     "forced, or the qualification is estimated, which is estimated; raw, corrected and "
                     "pre-validated are provisional. Doubtful values keep their class and are counted in notes.",
        "notes": [
            "Flow at Paris-Austerlitz is computed from the water level through a rating curve kept by the "
            "regional hydrometry service; Hub'Eau labels these values method 'Calculée' (computed) (Hub'Eau, "
            "HydroPortail).",
            "Hub'Eau publishes a daily mean flow (QmnJ). Before 1966 the level was read by an observer about "
            "once a day (more often in floods), so the early 'daily mean' often rests on one reading (Hub'Eau "
            "station history, as in the level series).",
            "Flow is in liters per second as published (100,000 L/s is 100 m³/s); not converted (Hub'Eau).",
            "The same station codes as the level series are used through 2005, each only inside its window, "
            "with no offset. From 2006 on, Hub'Eau publishes Paris flow mainly under the Austerlitz flow station "
            "F700000103, so the series uses it from January 1, 2006 (Hub'Eau).",
            join_note,
            f"Days published by more than one chain station: {len(overlap)}"
            + (f" ({overlap.index.min()} to {overlap.index.max()}); on those days the station whose window holds "
               "the date wins, as in the level series" if len(overlap) else "") + " (Hub'Eau).",
            f"Days qualified 'Douteuse' (doubtful) by Hub'Eau: {len(dbt)}, by decade {dbt_dec}. They are kept "
            "and keep their status class, because the publisher validated them; the flag says the value may "
            "be off, not that it was estimated (Hub'Eau).",
            (f"Provisional (not yet validated) days: {len(prov)}, {prov.date_obs_elab.min()} to "
             f"{prov.date_obs_elab.max()} (Hub'Eau).") if len(prov) else "No provisional days (Hub'Eau).",
            "Paris flow is influenced by four large reservoir lakes upstream, which Hub'Eau says reduce flood "
            "peaks, so recent flows differ from natural flows (Hub'Eau).",
            f"Rows in window: {n_raw}. Empty values dropped: {n_nan}"
            + (f" (by year {nan_years}; these rows carry no status either)" if n_nan else "")
            + f". Negative values dropped: {n_neg} (Hub'Eau).",
        ] + notes_st,
    }
    df = paris.rename(columns={"date_obs_elab": "date", "resultat_obs_elab": "flow"})
    write_flow(df[["date", "flow", "quality"]], meta)


if __name__ == "__main__":
    main()
