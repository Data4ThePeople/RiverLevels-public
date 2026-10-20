"""Brazil ANA (Agencia Nacional de Aguas) daily river stage.

Historic daily stage comes from the HidroWeb SOAP service HidroSerieHistorica
(tipoDados=1, cm, one row per month with Cota01..Cota31). Each month can appear
at consistency level 2 (consistent, reviewed) and level 1 (raw). We use level 2
where it exists and fall back to level 1, which we mark provisional. After the
historic record ends we extend with the 15-minute telemetry feed
(DadosHidrometeorologicos), averaged to a daily mean and marked provisional.
"""
from __future__ import annotations

import calendar
import datetime as dt
import xml.etree.ElementTree as ET
from collections import defaultdict

import pandas as pd

from sa_asia_common import RAW, fetch_to, parse_args, session, share_by_decade, write_gauge

BASE = "https://telemetriaws1.ana.gov.br/ServiceANA.asmx"
RAWDIR = RAW / "ana"
GAUGES = [
    # id, code, river key, display name
    ("amazon-tabatinga", "10100000", "amazon", "Tabatinga"),
    ("amazon-manacapuru", "14100000", "amazon", "Manacapuru"),
    ("amazon-manaus", "14990000", "amazon", "Manaus"),
    ("amazon-obidos", "17050001", "amazon", "Obidos"),
    ("paraguay-ladario", "66825000", "paraguay", "Ladario"),
]
# CotaNNStatus codes, from the HidroWeb documentation of HidroSerieHistorica:
# 0 blank, 1 real (observed), 2 estimated, 3 doubtful, 4 dry staff (regua seca).
STATUS_EST = {"2"}
DATUM = {
    "14990000": "cm above the Manaus port staff gauge zero, a local arbitrary reference; SGB says to subtract "
                "7.00 m from a reading to refer it to sea level (SGB Amazonas bulletin, 19 May 2017)",
    "17050001": "cm above the staff gauge zero installed 22 Feb 1968, 8.144 m below CPRM benchmark RN4 "
                "(Callede, Guyot et al. 1996)",
    "66825000": "cm above the Ladario staff gauge zero, listed at 82.15 m altitude (Embrapa Pantanal Doc. 14, "
                "1995, citing BRASIL 1974)",
}
LICENSE = ("No license on the HidroWeb service itself. The SNIRH metadata record for the national "
           "hydrometric network allows reproduction of the data provided the source is cited "
           "(https://metadados.snirh.gov.br/geonetwork/srv/api/records/f85dbf06-a869-414c-afc5-bb01869e9156). "
           "Credit: Agencia Nacional de Aguas e Saneamento Basico (ANA), HidroWeb.")


def rows(path, tag):
    root = ET.parse(path).getroot()
    for r in root.iter(tag):
        yield {c.tag: (c.text or "").strip() for c in r}


def fetch(s, code, refresh, today):
    inv = fetch_to(s, RAWDIR / f"inventory_{code}.xml", f"{BASE}/HidroInventario", refresh,
                   params=dict(codEstDE=code, codEstATE=code, tpEst="", nmEst="", nmRio="",
                               codSubBacia="", codBacia="", nmMunicipio="", nmEstado="",
                               sgResp="", sgOper="", telemetrica=""))
    hist = fetch_to(s, RAWDIR / f"hist_stage_{code}.xml", f"{BASE}/HidroSerieHistorica", refresh,
                    params=dict(codEstacao=code, dataInicio="", dataFim="", tipoDados="1",
                                nivelConsistencia=""))
    return inv, hist


def parse_hist(path):
    """Return {date: (level, consistency, status, n_readings)} preferring consistency 2.

    For each month and consistency level the service may return one row of daily
    means (MediaDiaria=1, time 00:00) and/or one row per reading hour (07:00 and
    17:00, MediaDiaria=0). We use the daily-mean row when present, otherwise the
    mean of the reading rows for that day."""
    by = defaultdict(list)
    for d in rows(path, "SerieHistorica"):
        by[(d["DataHora"][:7], d["NivelConsistencia"])].append(d)
    days = {}  # (date, lvl) -> (value, status, n, kind)
    for (ym, lvl), rs in by.items():
        y, m = int(ym[:4]), int(ym[5:7])
        nd = calendar.monthrange(y, m)[1]
        means = [r for r in rs if r.get("MediaDiaria") == "1"]
        use = means[:1] if means else rs
        if len(means) > 1:
            raise ValueError(f"{path.name}: {len(means)} daily-mean rows for {ym} level {lvl}")
        for i in range(1, nd + 1):
            vals, sts = [], []
            for r in use:
                v = r.get(f"Cota{i:02d}", "")
                if v != "":
                    vals.append(float(v))
                    sts.append(r.get(f"Cota{i:02d}Status", ""))
            if not vals:
                continue
            kind = "daily_mean_row" if means else f"readings_{len(vals)}"
            st = "2" if any(x in STATUS_EST for x in sts) else (sts[0] if sts else "")
            days[(dt.date(y, m, i), lvl)] = (sum(vals) / len(vals), st, len(vals), kind)
    out = {}
    for (day, lvl), v in days.items():
        if lvl == "2" or (day, "2") not in days:
            out[day] = (v[0], lvl, v[1], v[3])
    return out


def fetch_tel(s, code, y0, today, refresh):
    """Telemetry year files, requested one calendar year at a time."""
    paths = []
    for y in range(y0, today.year + 1):
        a = dt.date(y, 1, 1)
        b = min(dt.date(y, 12, 31), today)
        # the current year is always re-downloaded on --refresh; past years too
        paths.append(fetch_to(s, RAWDIR / f"telemetry_{code}_{y}.xml",
                              f"{BASE}/DadosHidrometeorologicos", refresh,
                              params=dict(codEstacao=code, dataInicio=a.strftime("%d/%m/%Y"),
                                          dataFim=b.strftime("%d/%m/%Y")), pause=1.0))
    return paths


def parse_tel(paths):
    recs = []
    for p in paths:
        for d in rows(p, "DadosHidrometereologicos"):
            if d.get("Nivel", "") == "":
                continue
            recs.append((d["DataHora"].strip(), float(d["Nivel"])))
    t = pd.DataFrame(recs, columns=["ts", "level"]).drop_duplicates("ts")
    t["date"] = pd.to_datetime(t["ts"]).dt.date
    g = t.groupby("date")["level"].agg(["mean", "count"]).reset_index()
    return g


def main():
    args = parse_args(__doc__)
    s = session()
    today = dt.date.today()
    if not args.refresh:
        # offline rebuild: the newest cached telemetry year defines "today"
        cached = sorted(RAWDIR.glob("telemetry_*_*.xml"))
        if cached:
            today = dt.date(max(int(p.stem.split("_")[-1]) for p in cached), 12, 31)
    for gid, code, river, name in GAUGES:
        inv, hist = fetch(s, code, args.refresh, today)
        meta_inv = next(rows(inv, "Table"))
        h = parse_hist(hist)
        hist_last = max(h)
        y0 = hist_last.year - 1  # one year of overlap to check the telemetry datum
        if code == "14990000":
            y0 = 2001  # ANA inventory: Manaus telemetry since 2001-06; use the full overlap for the join check
        tel = parse_tel(fetch_tel(s, code, y0, today, args.refresh))

        notes = []
        # overlap check between historic and telemetry
        ov = tel[tel["date"].isin(h.keys())].copy()
        if len(ov):
            ov["hist"] = [h[d][0] for d in ov["date"]]
            ov["lvl"] = [h[d][1] for d in ov["date"]]
            diff = ov["mean"] - ov["hist"]
            notes.append(
                f"Datum check: {len(ov)} days where both the historic series and telemetry have a value "
                f"({ov['date'].min()} to {ov['date'].max()}); telemetry daily mean minus historic value: "
                f"median {diff.median():+.1f} cm, mean {diff.mean():+.1f} cm, "
                f"5th-95th percentile {diff.quantile(.05):+.1f} to {diff.quantile(.95):+.1f} cm. "
                f"A median near zero means the two share the same gauge zero.")
        tel_ext = tel[tel["date"] > hist_last].copy()
        # partial days: a telemetry day with fewer than 75% of the readings the gauge usually sends per day
        # (median over the 61 days around it) is a mean of part of the day, often because readings arrive late
        tel_ext = tel_ext.sort_values("date").reset_index(drop=True)
        usual = tel_ext["count"].rolling(61, center=True, min_periods=1).median()
        short = tel_ext["count"] < 0.75 * usual
        short_days = sorted(str(d) for d in tel_ext.loc[short, "date"])
        tel_ext = tel_ext[~short]

        recs = []
        n_est = n_doubt = n_dry = n_prov = 0
        kinds = defaultdict(int)
        for day, (v, lvl, st, kind) in sorted(h.items()):
            q = "measured" if lvl == "2" else "provisional"
            if st == "2":
                q = "estimated"
                n_est += 1
            if st == "3":
                n_doubt += 1
            if st == "4":
                n_dry += 1
            kinds[kind] += 1
            recs.append((day, v, q))
        for _, r in tel_ext.iterrows():
            recs.append((r["date"], r["mean"], "provisional"))
        df = pd.DataFrame(recs, columns=["date", "level", "quality"])
        df["date"] = pd.to_datetime(df["date"])

        lvl2_last = max((d for d, v in h.items() if v[1] == "2"), default=None)
        lvl1 = sum(1 for v in h.values() if v[1] == "1")
        notes += [
            "Historic series: ANA HidroSerieHistorica, tipoDados=1 (stage). Where a month exists at "
            "consistency level 2 (consistent, reviewed by ANA) we use it; otherwise level 1 (raw) and mark "
            f"it provisional. Last level-2 date: {lvl2_last}. Level-1 days used: {lvl1}.",
            f"Per-day status codes from ANA (CotaNNStatus): {n_est} days flagged 2 'estimated' are marked "
            f"estimated; {n_doubt} days flagged 3 'doubtful' and {n_dry} days flagged 4 'dry staff gauge' "
            "are kept as published with their consistency-level quality.",
            "Daily value: ANA's daily-mean row where published (normally the mean of the 07:00 and 17:00 "
            f"staff readings); otherwise the mean of the reading rows for that day. Days by source row: "
            f"{dict(sorted(kinds.items()))}.",
            f"Historic record ends {hist_last}. Days after that come from the ANA telemetry feed "
            f"(DadosHidrometeorologicos, mostly 15-minute readings), averaged to a daily mean "
            f"({len(tel_ext)} days, marked provisional). Telemetry days with fewer than 12 readings: "
            f"{int((tel_ext['count'] < 12).sum())}. Dropped as partial days (fewer than 75% of the readings "
            f"the gauge usually sends per day, the median over the 61 days around it): {len(short_days)}"
            + (f", most recent {', '.join(short_days[-5:])}" if short_days else "") + ".",
            "No fill values found in this series; ANA leaves missing days blank.",
        ]
        est_dec = share_by_decade(df["date"], df["quality"] == "estimated")
        if est_dec:
            notes.append(f"Share of days marked estimated by decade: {est_dec}.")
        meta = {
            "id": gid, "river": river, "name": name, "country": "Brazil",
            "lat": float(meta_inv["Latitude"]), "lon": float(meta_inv["Longitude"]), "kind": "river",
            "source": "Agencia Nacional de Aguas e Saneamento Basico (ANA), HidroWeb web service",
            "source_url": f"https://www.snirh.gov.br/hidroweb/serieshistoricas (station {code}); {BASE}",
            "station_code": code, "unit": "cm",
            "datum": DATUM.get(code, "cm above the local staff gauge zero (ANA does not publish the zero's "
                                     "elevation in this service)"),
            "daily_stat": "mean",
            "license": LICENSE, "notes": notes,
        }
        if meta_inv.get("Altitude"):
            meta["notes"].append(f"ANA inventory altitude for the station: {meta_inv['Altitude']} m "
                                 "(station altitude, not the gauge zero).")
        write_gauge(df, meta, decimals=1)


if __name__ == "__main__":
    main()
