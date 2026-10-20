"""Rijkswaterstaat Waterwebservices (DDL API): discharge (Grootheid Q, m3/s) at
Lobith (lobith.bovenrijn.tolkamer), the Rhine where it enters the Netherlands.

One POST per calendar year to OphalenWaarnemingen (ProcesType "meting"). The
raw response bytes are cached gzipped per year in data/raw/flow_rws/. Readings
are once a day (08:00) in the early record and every 10 minutes later; days
with several readings get the plain mean, in Dutch winter time (UTC+1, the
API's own offset). Contract: scripts/fetch/FLOW.md.
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, parse_args, require_cache, session  # noqa: E402
from flow_common import write_flow  # noqa: E402

URL = "https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
LOC = "lobith.bovenrijn.tolkamer"
RAWDIR = RAW / "flow_rws"
FIRST_YEAR = 1901  # 1866 to 1900 return no discharge (checked 2026-10-17)
TODAY = dt.date.today()
FILL = 999999999
# Same code lists as rws_lobith.py (Aquo "KwaliteitsoordeelCode"):
# 00, 03, 06, 07, 90 -> measured; 10, 20, 25 (interpolated) -> estimated; 50, 99 -> dropped.
# Statuswaarde Ongecontroleerd (unchecked) -> provisional; Gecontroleerd / Definitief -> as above.
OK_CODES = {"00", "03", "06", "07", "90"}
EST_CODES = {"10", "20", "25"}
DROP_CODES = {"50", "99"}
# WaardeBepalingsMethode, newest rating relation first
RATING_RANK = {"other:F230": 0, "other:F216": 1, "other:F006": 2}


def body(year: int) -> dict:
    return {"Locatie": {"Code": LOC},
            "AquoPlusWaarnemingMetadata": {"AquoMetadata": {
                "Compartiment": {"Code": "OW"}, "Grootheid": {"Code": "Q"}, "ProcesType": "meting"}},
            "Periode": {"Begindatumtijd": f"{year}-01-01T00:00:00.000+01:00",
                        "Einddatumtijd": f"{year + 1}-01-01T00:00:00.000+01:00"}}


def download(s, year: int, path: Path) -> None:
    for i in range(5):
        try:
            r = s.post(URL, json=body(year), timeout=300)
            if r.status_code == 204 or (r.status_code == 200 and not r.content):
                break
            if r.status_code < 500:
                d = r.json()
                if d.get("Succesvol") or "Geen gegevens" in str(d.get("Foutmelding", "")):
                    break
                raise RuntimeError(f"{year}: {str(d)[:300]}")
        except Exception as e:  # network errors and 5xx: back off and retry
            if i == 4:
                raise
            print(f"  {year}: retry after {e!r}"[:200])
        time.sleep(10 * (i + 1))
    tmp = path.with_suffix(path.suffix + ".part")
    with gzip.open(tmp, "wb") as f:
        f.write(r.content)  # raw bytes as returned (empty for "no data")
    tmp.replace(path)
    time.sleep(1.0)


def readings(path: Path) -> pd.DataFrame:
    with gzip.open(path, "rb") as f:
        blob = f.read()
    d = json.loads(blob) if blob.strip() else {}
    rows = []
    for w in d.get("WaarnemingenLijst") or []:
        a = w["AquoMetadata"]
        assert a["Grootheid"]["Code"] == "Q" and a["Eenheid"]["Code"] == "m3/s", a
        ml = w["MetingenLijst"]
        per_day = len(ml) / max(1, len({m["Tijdstip"][:10] for m in ml}))
        cadence = "subdaily" if per_day > 1.5 else "daily"
        for m in ml:
            md = m["WaarnemingMetadata"]
            rows.append((m["Tijdstip"], m["Meetwaarde"].get("Waarde_Numeriek"),
                         md.get("Kwaliteitswaardecode"), md.get("Statuswaarde"),
                         a["MeetApparaat"]["Omschrijving"], a["WaardeBepalingsMethode"]["Omschrijving"],
                         a["WaardeBepalingsMethode"]["Code"], a["WaardeBewerkingsMethode"]["Code"],
                         a["BemonsteringsSoort"]["Code"], cadence))
    return pd.DataFrame(rows, columns=["t", "v", "kwal", "status", "apparaat", "methode", "rating", "bewerking",
                                       "soort", "cadence"])


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    years = range(FIRST_YEAR, TODAY.year + 1)
    for y in years:
        p = RAWDIR / f"lobith_Q_{y}.json.gz"
        if args.refresh or not p.exists():
            if not args.refresh:
                raise SystemExit(f"missing raw cache {p}; run with --refresh")
            download(s, y, p)
        require_cache(p)
    r = pd.concat([readings(RAWDIR / f"lobith_Q_{y}.json.gz") for y in years], ignore_index=True)
    n_all = len(r)
    codes = r.kwal.value_counts().to_dict()
    stat = r.status.value_counts().to_dict()
    unknown = set(codes) - EST_CODES - OK_CODES - DROP_CODES
    if unknown:
        raise ValueError(f"unknown Kwaliteitswaardecode {unknown}: map it before publishing")
    fill = r.v.isna() | (r.v.abs() >= FILL) | r.kwal.isin(DROP_CODES)
    n_fill = int(fill.sum())
    r = r[~fill].copy()
    neg = r.v < 0
    n_neg = int(neg.sum())
    r = r[~neg].copy()
    ts = pd.to_datetime(r.t, utc=True) + pd.Timedelta(hours=1)  # UTC+1, the API's offset
    r["date"] = ts.dt.strftime("%Y-%m-%d")
    unknown_rating = set(r.rating) - set(RATING_RANK)
    if unknown_rating:
        raise ValueError(f"unknown WaardeBepalingsMethode {unknown_rating}: rank it before publishing")
    r["series"] = r.rating + " / " + r.bewerking + " / " + r.soort + " / " + r.cadence
    before = len(r)
    r = r.drop_duplicates(["series", "t", "v"])
    n_dup = before - len(r)
    if r.duplicated(["series", "t"]).any():
        raise ValueError("same series and timestamp with different values")
    r["unchecked"] = r.status.eq("Ongecontroleerd")
    per = r.groupby(["date", "series"]).agg(n=("v", "size"), unchecked=("unchecked", "mean"),
                                            rating=("rating", "first"), bewerking=("bewerking", "first"),
                                            soort=("soort", "first"), cadence=("cadence", "first")).reset_index()
    per["year"] = per.date.str[:4]
    per["usual"] = per.groupby(["year", "series"]).n.transform("median")
    # Where several series cover a day, use one, in this order: the newest rating relation (F230 'Q-f relatie
    # (2018)', then F216, then F006); within it raw readings every 10 minutes or hour, then a single daily
    # reading, then RWS's own 24-hour mean (GEM24H); within those the live series (BemonsteringsSoort SB)
    # first. Status is not used to choose: in late 2025 a series marked checked reads about 20% of the live
    # series and of what the level implies.
    per["r_rank"] = per.rating.map(RATING_RANK)
    per["k_rank"] = 2
    per.loc[per.bewerking.eq("NVT") & per.cadence.eq("daily"), "k_rank"] = 1
    per.loc[per.bewerking.eq("NVT") & per.cadence.eq("subdaily"), "k_rank"] = 0
    per["s_rank"] = (per.soort != "SB").astype(int)
    ok = per[per.n >= 0.9 * per.usual].sort_values(["date", "r_rank", "k_rank", "s_rank", "n"],
                                                     ascending=[True, True, True, True, False])
    pick = ok.drop_duplicates("date")
    thin_days = sorted(set(per.date) - set(pick.date))
    n_two = int((ok.groupby("date").size() > 1).sum())
    used = pick.groupby("series").date.agg(["min", "max", "size"]).sort_values("min")
    gem_days = int(pick.bewerking.eq("GEM24H").sum())
    r = r.merge(pick[["date", "series"]], on=["date", "series"])
    r["est"] = r.kwal.isin(EST_CODES)
    r["prov"] = r.unchecked
    g = r.groupby("date").agg(flow=("v", "mean"), n=("v", "size"), gem=("bewerking", lambda x: (x == "GEM24H").any()), est=("est", "mean"), prov=("prov", "any"))
    g["year"] = g.index.str[:4]
    g["quality"] = "measured"
    g.loc[g.est > 0.5, "quality"] = "estimated"
    g.loc[g.prov, "quality"] = "provisional"
    per_day = g.groupby("year").n.median()
    eras, prev = [], None
    for y, n in per_day.items():
        if n != prev:
            eras.append(f"{y}: about {n:g} per day")
            prev = n
    methods = (r.assign(y=r.t.str[:4]).groupby(["apparaat", "methode"]).y.agg(["min", "max"])
               .sort_values("min").reset_index())
    mixed = ((g.n == 1) & ~g.gem).any() and ((g.n > 1) | g.gem).any()
    checked = g[~g.prov]
    meta = {
        "id": "rhine-lobith", "river": "rhine", "name": "Lobith",
        "station_name": "Lobith (Bovenrijn, Tolkamer)", "station_code": LOC,
        "country": "Netherlands", "lat": 51.8495, "lon": 6.1024,
        "same_station": True, "offset_note": "", "kind": "river flow", "unit": "m3/s",
        "daily_stat": "mixed" if mixed else ("one reading" if (g.n == 1).all() else "mean"),
        "source": "Rijkswaterstaat Waterwebservices (DDL API), Grootheid Q (Debiet), ProcesType meting",
        "source_url": URL,
        "license": "CC0 1.0 (Rijkswaterstaat open data)",
        "credit": "Rijkswaterstaat",
        "flag_rule": ("Statuswaarde 'Ongecontroleerd' (unchecked) is provisional. Otherwise Kwaliteitswaardecode "
                      "10, 20 or 25 (interpolated) on more than half a day's readings is estimated, and the rest "
                      "measured; codes 50 and 99 are dropped."),
        "notes": [
            "Flow at Lobith is computed from the water level through a rating relation that Rijkswaterstaat "
            "updates from flow measurements. Series through 2003 are labeled 'Debiet uit afvoerkromme (Q/H- of "
            "Q/HH-relatie)', discharge from a stage-discharge curve; from 2003 'Debiet uit Q-f relatie', with a "
            "new relation labeled '(2018)' used from 2017 (Rijkswaterstaat).",
            "Instrument and method periods, first and last year seen: "
            + "; ".join(f"{a} / {m}: {lo} to {hi}" for a, m, lo, hi in methods.itertuples(index=False))
            + " (Rijkswaterstaat).",
            "The discharge record starts in 1901; the API returns nothing for 1866 to 1900, so flow starts 35 "
            "years after the level record (Rijkswaterstaat).",
            f"Status counts in the raw readings: {stat}. 'Ongecontroleerd' (unchecked) makes a day provisional. "
            + (f"Days marked checked: {len(checked)}, all between {checked.index.min()} and {checked.index.max()}; "
               f"every earlier day, back to 1901, is labeled unchecked, so the status does not show which old "
               "values were checked (Rijkswaterstaat)." if len(checked) else
               "No day carries a checked status (Rijkswaterstaat)."),
            f"Quality code counts in the raw readings: {codes} (Rijkswaterstaat).",
            "Readings per day by era (median, first year of each change): " + "; ".join(eras)
            + ". Days with one reading use that reading; days with several use their plain mean, in UTC+1 "
            "(Rijkswaterstaat).",
            "Series used, by period (rating code / processing / sampling kind / cadence: first day, last day, "
            "days): " + "; ".join(f"{k}: {a} to {b}, {n}" for k, (a, b, n) in used.iterrows())
            + f". Where several series cover a day, the newest rating relation is used, then raw readings over "
            f"a single reading over RWS's own 24-hour mean (GEM24H), then the live series (sampling kind SB). "
            f"Status is not used to choose, because in late 2025 a series marked checked reads about 20% of the "
            f"live series and of what the level implies. Days that use RWS's GEM24H daily mean, because no "
            f"readings are published: {gem_days} (Rijkswaterstaat API, our processing).",
            f"Raw readings: {n_all}. Dropped as fill or gap (empty, {FILL}, or code 50 or 99): {n_fill}. "
            f"Dropped as negative: {n_neg}. Identical repeated readings dropped: {n_dup}. Days where two series "
            f"overlap: {n_two}. Days dropped because no series had "
            f"at least 90% of its usual readings: {len(thin_days)} (Rijkswaterstaat API, our processing).",
            "Flood peaks are above most flows ever measured at Lobith, so the rating is extended there and "
            "peaks are the least certain values (Rijkswaterstaat).",
        ],
    }
    write_flow(g.reset_index()[["date", "flow", "quality"]], meta)


if __name__ == "__main__":
    main()
