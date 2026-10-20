"""Rijkswaterstaat Waterwebservices (DDL API): water level (WATHTE, cm NAP) at
Lobith (lobith.bovenrijn.tolkamer), the Rhine where it enters the Netherlands.

One POST per calendar year to OphalenWaarnemingen (ProcesType "meting"). The
raw JSON is cached gzipped per year in data/raw/rws/. Readings are once a day
in the early record and every hour, then every 10 minutes later; they are
aggregated to a daily mean in Dutch winter time (UTC+1, the API's own offset).
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
from eu_common import RAW, parse_args, require_cache, session, write_gauge  # noqa: E402

URL = "https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
LOC = "lobith.bovenrijn.tolkamer"
RAWDIR = RAW / "rws"
FIRST_YEAR = 1866
TODAY = dt.date.today()
FILL = 999999999
# Kwaliteitswaardecode (Aquo domain "KwaliteitsoordeelCode", RWS list
# https://rijkswaterstaatdata.nl/publish/pages/223004/aquo_kwaliteitsoordeelcodes.xlsx):
# 00 normal value, 03 larger spread, 06/07 double-checked value, 90 deviating value approved after
# validation -> measured; 10 interpolated in space, 20 interpolated in time, 25 interpolated in space
# and time -> estimated; 50 implausible value, 99 gap value -> dropped.
# Statuswaarde: Ongecontroleerd (unchecked) -> provisional; Gecontroleerd (checked), Definitief -> as above.
OK_CODES = {"00", "03", "06", "07", "90"}
EST_CODES = {"10", "20", "25"}
DROP_CODES = {"50", "99"}


def body(year: int) -> dict:
    return {"Locatie": {"Code": LOC},
            "AquoPlusWaarnemingMetadata": {"AquoMetadata": {
                "Compartiment": {"Code": "OW"}, "Grootheid": {"Code": "WATHTE"}, "ProcesType": "meting"}},
            "Periode": {"Begindatumtijd": f"{year}-01-01T00:00:00.000+01:00",
                        "Einddatumtijd": f"{year + 1}-01-01T00:00:00.000+01:00"}}


def download(s, year: int, path: Path) -> None:
    for i in range(5):
        try:
            r = s.post(URL, json=body(year), timeout=300)
            if r.status_code == 204 or (r.status_code == 200 and not r.content):
                d = {"Succesvol": True, "WaarnemingenLijst": []}
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
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    time.sleep(1.0)


def readings(path: Path) -> pd.DataFrame:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        d = json.load(f)
    rows = []
    for w in d.get("WaarnemingenLijst") or []:
        a = w["AquoMetadata"]
        assert a["Grootheid"]["Code"] == "WATHTE" and a["Eenheid"]["Code"] == "cm" and a["Hoedanigheid"]["Code"] == "NAP", a
        ml = w["MetingenLijst"]
        per_day = len(ml) / max(1, len({m["Tijdstip"][:10] for m in ml}))
        cadence = "subdaily" if per_day > 1.5 else "daily"
        for m in ml:
            md = m["WaarnemingMetadata"]
            rows.append((m["Tijdstip"], m["Meetwaarde"].get("Waarde_Numeriek"),
                         md.get("Kwaliteitswaardecode"), md.get("Statuswaarde"),
                         a["MeetApparaat"]["Omschrijving"], a["WaardeBepalingsMethode"]["Omschrijving"], cadence))
    return pd.DataFrame(rows, columns=["t", "v", "kwal", "status", "apparaat", "methode", "cadence"])


def main():
    args = parse_args(__doc__)
    RAWDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    years = range(FIRST_YEAR, TODAY.year + 1)
    t0 = time.time()
    for y in years:
        p = RAWDIR / f"lobith_WATHTE_{y}.json.gz"
        if args.refresh:
            download(s, y, p)
        require_cache(p)
    if args.refresh:
        print(f"downloaded {len(years)} years in {time.time() - t0:.0f} s")
    r = pd.concat([readings(RAWDIR / f"lobith_WATHTE_{y}.json.gz") for y in years], ignore_index=True)
    n_all = len(r)
    codes = r.kwal.value_counts().to_dict()
    stat = r.status.value_counts().to_dict()
    unknown = set(codes) - EST_CODES - OK_CODES - DROP_CODES
    if unknown:
        raise ValueError(f"unknown Kwaliteitswaardecode {unknown}: map it before publishing")
    fill = (r.v.isna()) | (r.v.abs() >= FILL) | r.kwal.isin(DROP_CODES)
    n_fill = int(fill.sum())
    r = r[~fill].copy()
    ts = pd.to_datetime(r.t, utc=True) + pd.Timedelta(hours=1)  # UTC+1, the API's offset
    r["date"] = ts.dt.strftime("%Y-%m-%d")
    r["year"] = r.date.str[:4]
    r["series"] = r.apparaat + " / " + r.methode + " / " + r.cadence
    # the same instant can come back twice (year-boundary readings, repeated series)
    before = len(r)
    r = r.drop_duplicates(["series", "t", "v"])
    n_dup = before - len(r)
    if r.duplicated(["series", "t"]).any():
        raise ValueError("same series and timestamp with different values")
    # Some years carry two series at once (1979-1987: unchecked hourly values read off recorder charts
    # plus the checked once-a-day staff reading). Per day, use one series with at least 90% of its usual
    # count: a checked series first, then the most frequent one.
    r["unchecked"] = r.status.eq("Ongecontroleerd")
    # a stray unchecked reading next to a checked one in the same series and day (1979-01-01 and
    # 1981-01-01: an unchecked 00:00 reading beside the checked 08:00 one) is dropped, so the day
    # keeps its checked reading
    has_checked = (~r.unchecked).groupby([r.date, r.series]).transform("any")
    stray = r.unchecked & has_checked & r.cadence.eq("daily")
    n_stray = int(stray.sum())
    r = r[~stray].copy()
    per = r.groupby(["date", "series"]).agg(n=("v", "size"), unchecked=("unchecked", "mean")).reset_index()
    per["year"] = per.date.str[:4]
    per["usual"] = per.groupby(["year", "series"]).n.transform("median")
    per["checked"] = per.unchecked < 0.5
    ok = per[per.n >= 0.9 * per.usual].sort_values(["date", "checked", "usual", "n"],
                                                     ascending=[True, False, False, False])
    pick = ok.drop_duplicates("date")
    all_days = set(per.date)
    thin_days = sorted(all_days - set(pick.date))
    n_thin = len(thin_days)
    n_two = int((ok.groupby("date").size() > 1).sum())
    r = r.merge(pick[["date", "series"]], on=["date", "series"])
    r["est"] = r.kwal.isin(EST_CODES)
    r["prov"] = r.status.eq("Ongecontroleerd")
    g = r.groupby("date").agg(level=("v", "mean"), n=("v", "size"), est=("est", "mean"), prov=("prov", "any"))
    g["year"] = g.index.str[:4]
    singles = r[r.date.isin(g.index[g.n == 1])]
    read_hours = (singles.assign(dec=singles.year.astype(int) // 10 * 10, hm=singles.t.str[11:16])
                  .groupby("dec").hm.agg(lambda x: x.mode().iloc[0]).to_dict())
    g["quality"] = "measured"
    g.loc[g.est > 0.5, "quality"] = "estimated"
    g.loc[g.prov, "quality"] = "provisional"
    g["level"] = g.level.round(1)
    per_day = g.groupby("year").n.median()
    eras, prev = [], None
    for y, n in per_day.items():
        if n != prev:
            eras.append(f"{y}: about {n:g} per day")
            prev = n
    methods = (r.assign(y=r.t.str[:4]).groupby(["apparaat", "methode"]).y.agg(["min", "max"])
               .sort_values("min").reset_index())
    prov = g[g.quality == "provisional"]
    meta = {
        "id": "rhine-lobith", "river": "rhine", "name": "Lobith", "country": "Netherlands",
        "lat": 51.8495, "lon": 6.1024, "kind": "river",
        "source": "Rijkswaterstaat Waterwebservices (DDL API)",
        "source_url": URL + f" (Locatie.Code {LOC}, Grootheid WATHTE, ProcesType meting)",
        "station_code": LOC, "unit": "cm",
        "datum": "cm relative to NAP (Normaal Amsterdams Peil), an absolute national datum, not a local gauge zero",
        "daily_stat": "mixed (see notes)",
        "license": "Rijkswaterstaat open data, CC0 1.0 (public domain dedication). Credit: Rijkswaterstaat",
        "notes": [
            f"Single-reading days: {int((g.n == 1).sum())}; days averaged from several readings: {int((g.n > 1).sum())}.",
            "daily_stat is mixed: in the early record there is one staff-gauge reading per day, so the "
            "daily value is that reading; later readings are hourly and then every 10 minutes, and the "
            "daily value is their mean. Usual clock time of the single daily reading, by decade: "
            + "; ".join(f"{k}s {v}" for k, v in read_hours.items()) + ".",
            "Readings per day by era (median, first year of each change): " + "; ".join(eras) + ".",
            "Days are calendar days in UTC+1 (the offset the API returns), for all years.",
            f"Raw readings: {n_all}. Dropped as fill or gap (value {FILL}, empty, or quality code 99): {n_fill}.",
            f"Identical repeated readings dropped: {n_dup}. On {n_two} days two series overlap (1979 to 1987: "
            "unchecked hourly values read from recorder charts, and the checked once-a-day staff reading); "
            "the checked series is used, and otherwise the more frequent one. "
            f"Unchecked readings dropped because the same series had a checked reading that day: {n_stray}.",
            f"Dropped {n_thin} days with fewer than 90% of the usual readings of any series (partial days)"
            + (f", for example {', '.join(thin_days[:5])}." if n_thin else "."),
            f"Kwaliteitswaardecode counts in the raw readings: {codes}. Codes 10, 20 and 25 mark values "
            "interpolated in space and/or time; a day is marked estimated when more than half its readings carry "
            "one of them. Codes 50 (implausible) and 99 (gap) are dropped.",
            f"Statuswaarde counts: {stat}. 'Ongecontroleerd' (not yet checked) makes the day provisional"
            + (f"; provisional days run {prov.index.min()} to {prov.index.max()}." if len(prov) else "."),
            "Instrument and method periods (first and last year seen): "
            + "; ".join(f"{a} / {m}: {lo} to {hi}" for a, m, lo, hi in methods.itertuples(index=False)) + ".",
            "The API also returns two readings from January 30 and 31, 1865; the series here starts with the "
            "continuous daily record in 1866.",
        ],
    }
    write_gauge(g.reset_index()[["date", "level", "quality"]], meta)


if __name__ == "__main__":
    main()
