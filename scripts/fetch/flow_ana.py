"""Brazil ANA daily discharge (flow) for Tabatinga, Manacapuru and Obidos.

HidroWeb SOAP service HidroSerieHistorica with tipoDados=3: one row per month
with Vazao01..Vazao31 and Vazao01Status..Vazao31Status, m3/s. A month can
appear at consistency level 2 (consistido, reviewed) and level 1 (bruto, raw).
As in ana.py for level: level 2 wins over level 1 day by day; level 1 days are
provisional; status 2 (estimated) days are estimated whatever the level.
Historic series only; the telemetry feed is not used for flow.
"""
from __future__ import annotations

import calendar
import datetime as dt
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

import pandas as pd

from flow_common import write_flow
from sa_asia_common import RAW, fetch_to, parse_args, session

BASE = "https://telemetriaws1.ana.gov.br/ServiceANA.asmx"
RAWDIR = RAW / "flow_ana"
GAUGES = [
    # id, code, river key, display name of the level gauge
    ("amazon-tabatinga", "10100000", "amazon", "Tabatinga"),
    ("amazon-manacapuru", "14100000", "amazon", "Manacapuru"),
    ("amazon-obidos", "17050001", "amazon", "Obidos"),
]
# VazaoNNStatus codes, same list as CotaNNStatus (HidroWeb documentation of
# HidroSerieHistorica): 0 blank, 1 real, 2 estimated, 3 doubtful, 4 dry staff.
STATUS_EST = {"2"}
LICENSE = ("No license on the HidroWeb service itself. The SNIRH metadata record for the national "
           "hydrometric network allows reproduction of the data provided the source is cited "
           "(https://metadados.snirh.gov.br/geonetwork/srv/api/records/f85dbf06-a869-414c-afc5-bb01869e9156).")


def rows(path, tag):
    root = ET.parse(path).getroot()
    for r in root.iter(tag):
        yield {c.tag: (c.text or "").strip() for c in r}


def parse_hist(path):
    """Return ({date: (flow, level, status)}, stats). Level 2 wins over level 1."""
    by = defaultdict(list)
    for d in rows(path, "SerieHistorica"):
        by[(d["DataHora"][:7], d["NivelConsistencia"])].append(d)
    days, methods, mean_rows, blank_status_vals = {}, Counter(), Counter(), 0
    for (ym, lvl), rs in by.items():
        means = [r for r in rs if r.get("MediaDiaria") == "1"]
        mean_rows[(lvl, len(means), len(rs))] += 1
        if len(rs) != 1 or len(means) != 1:
            raise SystemExit(f"{path.name}: {ym} level {lvl}: expected one daily-mean row, got {len(rs)} rows")
        r = rs[0]
        methods[r.get("MetodoObtencaoVazoes", "")] += 1
        y, m = int(ym[:4]), int(ym[5:7])
        for i in range(1, calendar.monthrange(y, m)[1] + 1):
            v = r.get(f"Vazao{i:02d}", "")
            if v == "":
                continue
            st = r.get(f"Vazao{i:02d}Status", "")
            if st in ("", "0"):
                blank_status_vals += 1
            days[(dt.date(y, m, i), lvl)] = (float(v), st)
    out = {}
    n_both = 0
    for (day, lvl), (v, st) in days.items():
        if lvl == "2":
            out[day] = (v, lvl, st)
            n_both += (day, "1") in days
        elif (day, "2") not in days:
            out[day] = (v, lvl, st)
    stats = dict(methods=dict(methods), n_months=sum(methods.values()), n_both=n_both,
                 blank_status_vals=blank_status_vals,
                 months_by_level={k: sum(1 for (_, l) in by if l == k) for k in sorted({l for _, l in by})})
    return out, stats


def main():
    args = parse_args(__doc__)
    s = session()
    for gid, code, river, name in GAUGES:
        inv = fetch_to(s, RAWDIR / f"inventory_{code}.xml", f"{BASE}/HidroInventario", args.refresh,
                       params=dict(codEstDE=code, codEstATE=code, tpEst="", nmEst="", nmRio="",
                                   codSubBacia="", codBacia="", nmMunicipio="", nmEstado="",
                                   sgResp="", sgOper="", telemetrica=""))
        hist = fetch_to(s, RAWDIR / f"hist_flow_{code}.xml", f"{BASE}/HidroSerieHistorica", args.refresh,
                        params=dict(codEstacao=code, dataInicio="", dataFim="", tipoDados="3",
                                    nivelConsistencia=""))
        st_inv = next(rows(inv, "Table"))
        h, stats = parse_hist(hist)

        recs, counts = [], Counter()
        for day, (v, lvl, st) in sorted(h.items()):
            q = "measured" if lvl == "2" else "provisional"
            if st in STATUS_EST:
                q = "estimated"
            counts[st or "blank"] += 1
            recs.append((day, v, q))
        df = pd.DataFrame(recs, columns=["date", "flow", "quality"])
        lvl2_last = max((d for d, v in h.items() if v[1] == "2"), default=None)
        lvl1_days = sum(1 for v in h.values() if v[1] == "1")
        meth = stats["methods"]
        notes = [
            "ANA computes daily flow from the gauge's daily level with a rating curve (curva-chave) fitted to "
            "field flow measurements; the service's method field MetodoObtencaoVazoes is 1 on "
            f"{meth.get('1', 0)} of {stats['n_months']} month rows (other codes: "
            f"{ {k: v for k, v in meth.items() if k != '1'} or 'none'}). We read code 1 as the rating curve, "
            "but ANA's code list was not found, so that reading is not confirmed (ANA HidroSerieHistorica).",
            f"Where a month exists at consistency level 2 (consistido, reviewed by ANA) we use it; otherwise "
            f"level 1 (raw), marked provisional. Last level-2 day: {lvl2_last}. Level-1 days used: {lvl1_days}. "
            f"Days present at both levels, level 2 kept: {stats['n_both']} (ANA HidroSerieHistorica).",
            f"Per-day status codes on the days kept: {dict(sorted(counts.items()))}. Status 2 (estimated) is "
            "marked estimated; status 3 (doubtful) is kept with its consistency-level quality (ANA).",
            f"Days with a value but status 0 or blank: {stats['blank_status_vals']}; kept with their "
            "consistency-level quality (ANA).",
            "Missing days are blank in ANA's rows and are not in this file; no fill values found (ANA).",
        ]
        meta = {
            "id": gid, "river": river, "name": name,
            "station_name": st_inv["Nome"].title(), "station_code": code, "country": "Brazil",
            "lat": float(st_inv["Latitude"]), "lon": float(st_inv["Longitude"]),
            "same_station": True, "offset_note": "", "kind": "river flow", "unit": "m3/s",
            "daily_stat": "mean",
            "source": "Agencia Nacional de Aguas e Saneamento Basico (ANA), HidroWeb HidroSerieHistorica (tipoDados=3)",
            "source_url": f"{BASE}/HidroSerieHistorica",
            "license": LICENSE,
            "credit": "Agencia Nacional de Aguas e Saneamento Basico (ANA), HidroWeb; station operated by SGB-CPRM"
                      if st_inv.get("OperadoraSigla") == "SGB-CPRM" else
                      "Agencia Nacional de Aguas e Saneamento Basico (ANA), HidroWeb",
            "flag_rule": "Consistency level 2 (consistido) is measured and level 1 (raw) provisional; "
                         "day status 2 (estimated) is estimated at either level.",
            "notes": notes,
        }
        write_flow(df, meta)


if __name__ == "__main__":
    main()
