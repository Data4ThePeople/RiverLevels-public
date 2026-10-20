"""Argentina INA alert system a5 API: daily mean discharge (variable 40,
"Caudal medio diario", m3/s) on the Parana at Posadas, Corrientes, Parana and
Rosario.

Observations come from /a5/obs/puntual/series/{id}/observaciones in 20-year
chunks, one value per day stamped at local midnight. INA publishes no
per-value quality flag, so every value is marked measured.
"""
from __future__ import annotations

import json

import pandas as pd

from flow_common import write_flow
from sa_asia_common import RAW, fetch_to, parse_args, session

API = "https://alerta.ina.gob.ar/a5"
RAWDIR = RAW / "flow_ina"
GAUGES = [
    # id, flow series id, rating-curve (variable 4) series id at the same station or None, name
    ("parana-posadas", 26611, 863, "Posadas"),
    ("parana-corrientes", 26616, 868, "Corrientes"),
    ("parana-parana", 26626, None, "Parana"),
    ("parana-rosario", 26631, None, "Rosario"),
]
CHUNKS = [(y, y + 19) for y in range(1880, 2040, 20)]
TZ = "America/Argentina/Buenos_Aires"
LICENSE = ("No license is stated on the INA API or site (alerta.ina.gob.ar); clear reuse terms with INA "
           "before publishing.")
GAUGE_NOTES = {
    "parana-posadas": [
        "INA's flow series for Posadas ends on September 8, 2017 (INA a5 API).",
    ],
    "parana-parana": [
        "INA's daily flow series for Parana starts only in July 2015 (INA a5 API).",
    ],
    "parana-rosario": [
        "INA's daily flow series for Rosario starts only in July 2015 (INA a5 API).",
    ],
}


def main():
    args = parse_args(__doc__)
    s = session()
    for gid, sid, rating_sid, name in GAUGES:
        mp = fetch_to(s, RAWDIR / f"series_{sid}.json", f"{API}/obs/puntual/series/{sid}", args.refresh)
        meta_s = json.loads(mp.read_text())
        st = meta_s["estacion"]
        if meta_s["var"]["id"] != 40:
            raise SystemExit(f"{gid}: series {sid} is variable {meta_s['var']['id']}, expected 40")
        unit = meta_s["unidades"]["abrev"]
        if unit != "m^3/s":
            raise SystemExit(f"{gid}: unexpected unit {unit}")
        rating = None
        if rating_sid:
            rp = fetch_to(s, RAWDIR / f"series_{rating_sid}.json", f"{API}/obs/puntual/series/{rating_sid}",
                          args.refresh)
            rating = json.loads(rp.read_text())
            if rating["estacion"]["id"] != st["id"]:
                raise SystemExit(f"{gid}: rating series {rating_sid} is at another station")
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
        # the API pads gaps with rows that have no id and no value; real rows have an id
        n_dup = int(d["id"].notna().sum() - d.loc[d["id"].notna(), "id"].nunique())
        d = d[d["id"].isna() | ~d["id"].duplicated()]
        n_raw = int(d["id"].notna().sum())
        empty = d["valor"].isna()
        n_empty_id, n_pad = int((empty & d["id"].notna()).sum()), int((empty & d["id"].isna()).sum())
        neg = d["valor"].notna() & (d["valor"] < 0)
        d = d[~empty & ~neg].copy()
        local = pd.to_datetime(d["timestart"], utc=True).dt.tz_convert(TZ)
        d["date"] = local.dt.date
        g = d.groupby("date")["valor"].agg(["mean", "count", "nunique"]).reset_index()
        multi = g[g["count"] > 1]
        if (multi["nunique"] > 1).any():
            raise SystemExit(f"{gid}: days with two different daily means: {multi['date'].tolist()[:5]}")
        df = pd.DataFrame({"date": pd.to_datetime(g["date"]), "flow": g["mean"], "quality": "measured"})
        hours = local.dt.strftime("%H:%M").value_counts().head(3).to_dict()
        lon, lat = st["geom"]["coordinates"]
        notes = [
            f"INA series {sid}, variable '{meta_s['var']['nombre']}' (daily mean flow), station {st['nombre']} "
            f"(INA station {st['id']}, Prefectura Naval Argentina code {st['id_externo']}) (INA a5 API).",
        ]
        if rating:
            notes.append(
                f"INA's per-reading flow series at this station (series {rating_sid}, variable "
                f"'{rating['var']['nombre']}') is labeled as computed from a rating curve "
                f"('{rating['procedimiento']['nombre']}'), so these daily means rest on the gauge level put "
                f"through a rating curve. The daily series itself is labeled "
                f"'{meta_s['procedimiento']['nombre']}', which looks like a default label (INA a5 API).")
        else:
            notes.append(
                f"INA labels this daily series '{meta_s['procedimiento']['nombre']}' and gives no per-reading "
                "series here; on the Parana INA's flow series elsewhere are labeled as computed from a rating "
                "curve ('Curva de gasto'), and we did not find how this one is computed (INA a5 API).")
        notes += [
            "INA publishes no per-value quality flag, so every value is marked measured, including the most "
            "recent days, which INA may still correct (INA a5 API).",
            f"{n_raw} values with an id; rows repeated across download chunks: {n_dup}. Dropped "
            f"{n_empty_id} empty values and {int(neg.sum())} negative values; the API "
            f"also returns {n_pad} empty placeholder rows for missing days, which are "
            f"not in this file. Days stored twice with the same value, kept once: {len(multi)}. Most common local "
            f"timestamps: {hours} (INA a5 API).",
        ] + GAUGE_NOTES.get(gid, [])
        gap = df["date"].diff().dt.days
        gaps = [f"{(df['date'][i - 1] + pd.Timedelta(days=1)).date()} to {(df['date'][i] - pd.Timedelta(days=1)).date()}"
                for i in gap[gap > 30].index]
        if gaps:
            notes.append(f"Gaps longer than 30 days with no value: {'; '.join(gaps)} (INA a5 API).")
        meta = {
            "id": gid, "river": "parana", "name": name,
            "station_name": st["nombre"], "station_code": f"INA series {sid} / PNA {st['id_externo']}",
            "country": "Argentina", "lat": round(lat, 6), "lon": round(lon, 6),
            "same_station": True, "offset_note": "", "kind": "river flow", "unit": "m3/s",
            "daily_stat": "mean",
            "source": "Instituto Nacional del Agua (INA) alert system a5 API, variable 40 (Caudal medio diario)",
            "source_url": f"{API}/obs/puntual/series/{sid}/observaciones",
            "license": LICENSE,
            "credit": "Instituto Nacional del Agua (INA); gauge read by Prefectura Naval Argentina",
            "flag_rule": "INA publishes no quality flags, so every value is marked measured.",
            "notes": notes,
        }
        write_flow(df, meta)


if __name__ == "__main__":
    main()
