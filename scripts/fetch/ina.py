"""Argentina INA (Instituto Nacional del Agua) alert system a5 API: daily river
stage on the Parana, read by the Prefectura Naval Argentina (PNA) gauges.

Observations come from /a5/obs/puntual/series/{id}/observaciones in 20-year
chunks. Most days have one reading; since 2016 some days have two to eight.
We take the daily mean of the readings on each local (Argentina) calendar day.
INA publishes no per-value quality flag, so every value is marked measured.
"""
from __future__ import annotations

import json

import pandas as pd

from sa_asia_common import RAW, fetch_to, parse_args, session, write_gauge

API = "https://alerta.ina.gob.ar/a5"
RAWDIR = RAW / "ina"
GAUGES = [
    # id, series id, station id, river key, name
    ("parana-posadas", 14, 14, "parana", "Posadas"),
    ("parana-corrientes", 19, 19, "parana", "Corrientes"),
    ("parana-parana", 29, 29, "parana", "Parana"),
    ("parana-rosario", 34, 34, "parana", "Rosario"),
]
CHUNKS = [(y, y + 19) for y in range(1880, 2040, 20)]
TZ = "America/Argentina/Buenos_Aires"
LICENSE = ("INA alert system (alerta.ina.gob.ar); data from Prefectura Naval Argentina gauges. "
           "No license is stated on the API or site. Credit INA and Prefectura Naval Argentina; "
           "clear reuse terms before publishing.")


def main():
    args = parse_args(__doc__)
    s = session()
    for gid, sid, est, river, name in GAUGES:
        mp = fetch_to(s, RAWDIR / f"series_{sid}_meta.json", f"{API}/obs/puntual/series", args.refresh,
                      params=dict(estacion_id=est, var_id=2))
        rows = [r for r in json.loads(mp.read_text())["rows"] if r["id"] == sid]
        meta_s = rows[0]
        st = meta_s["estacion"]
        recs = []
        for a, b in CHUNKS:
            p = fetch_to(s, RAWDIR / f"obs_{sid}_{a}_{b}.json",
                         f"{API}/obs/puntual/series/{sid}/observaciones", args.refresh,
                         # the API keeps a value only if its own timeend falls inside the request, so a daily value
                         # stamped Dec 31 (timeend Jan 1, 03:00 UTC) needs a day of overlap; repeats are dropped by id
                         params=dict(timestart=f"{a}-01-01T00:00:00Z", timeend=f"{b + 1}-01-02T00:00:00Z"),
                         pause=1.0)
            recs += json.loads(p.read_text())
        d = pd.DataFrame(recs)
        d = d.drop_duplicates("id")
        n_raw = len(d)
        bad = d["valor"].isna() | (d["valor"].abs() > 90)
        n_bad = int(bad.sum())
        d = d[~bad]
        local = pd.to_datetime(d["timestart"], utc=True).dt.tz_convert(TZ)
        d["date"] = local.dt.date
        g = d.groupby("date")["valor"].agg(["mean", "count"]).reset_index()
        multi = g[g["count"] > 1]
        df = pd.DataFrame({"date": pd.to_datetime(g["date"]), "level": g["mean"], "quality": "measured"})
        hours = local.dt.strftime("%H:%M").groupby((local.dt.year // 10) * 10).agg(
            lambda x: x.value_counts().index[0])
        cero = st.get("cero_ign")
        datum = (f"m above the local gauge zero (cero de escala); INA lists the zero at {cero} m IGN "
                 "(Argentine national vertical datum)" if cero is not None else
                 "m above the local gauge zero (cero de escala); INA does not list the zero's elevation")
        notes = [
            f"INA series {sid} ('{meta_s['procedimiento']['nombre']}', variable '{meta_s['var']['nombre']}'), "
            f"station {st['nombre']} (INA station {st['id']}, PNA code {st['id_externo']}), owner {st['propietario']}.",
            "INA publishes no per-value quality flag, so every value is marked measured. This includes the "
            "most recent days, which INA may still correct.",
            f"{n_raw} raw observations. Days with more than one reading (averaged to a daily mean): {len(multi)}, "
            f"from {multi['date'].min()} to {multi['date'].max()}. Before that each day has a single reading."
            if len(multi) else f"{n_raw} raw observations, one per day.",
            f"Most common local timestamp by decade: {hours.to_dict()}. These are the times INA stored; "
            "the uniform 07:00 before 1980 looks like a loading convention, not a documented reading hour.",
            f"Dropped {n_bad} empty or impossible values (absolute value over 90 m)." if n_bad else
            "No fill values found.",
            f"INA alert thresholds for this gauge: alert {st.get('nivel_alerta')} m, evacuation "
            f"{st.get('nivel_evacuacion')} m, low water {st.get('nivel_aguas_bajas')} m.",
        ]
        lon, lat = st["geom"]["coordinates"]
        meta = {
            "id": gid, "river": river, "name": name, "country": "Argentina",
            "lat": round(lat, 6), "lon": round(lon, 6), "kind": "river",
            "source": "Instituto Nacional del Agua (INA) alert system a5 API; Prefectura Naval Argentina gauges",
            "source_url": f"{API}/obs/puntual/series/{sid}/observaciones",
            "station_code": f"INA series {sid} / PNA {st['id_externo']}",
            "unit": "m", "datum": datum,
            "daily_stat": "mixed (see notes)" if len(multi) else "single reading",
            "license": LICENSE, "notes": notes,
        }
        # INA publishes readings to 1 cm; a mean of several readings is rounded back to 1 cm.
        write_gauge(df, meta, decimals=2)


if __name__ == "__main__":
    main()
