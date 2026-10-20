"""German federal waterway gauges (Rhine, Elbe): BfG hyd1d daily mean water
levels, extended with recent PEGELONLINE 15-minute data aggregated to daily means.

hyd1d: https://hyd1d.bafg.de/downloads/df.gauging_data_latest.RDS (R data
frame: gauging_station, date, w = daily mean in cm above gauge zero).
PEGELONLINE REST API v2: station metadata (coordinates, gauge zero) and the
last ~31 days of 15-minute W values. Each refresh saves its PEGELONLINE pull
under a dated file name; all saved pulls are merged, so the recent record grows
with every refresh. The gap between the end of hyd1d and the oldest saved pull
is left as a gap.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd
import pyreadr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eu_common import RAW, get, parse_args, require_cache, session, write_gauge  # noqa: E402

HYD1D_URL = "https://hyd1d.bafg.de/downloads/df.gauging_data_latest.RDS"
PO = "https://www.pegelonline.wsv.de/webservices/rest-api/v2"
HDIR = RAW / "hyd1d"
PDIR = RAW / "pegelonline"
VALIDATED_THROUGH = 2025  # hyd1d: years up to here are validated, later years are raw (provisional)
MIN_VALUES_PER_DAY = 90   # of 96 quarter hours, for a PEGELONLINE daily mean
GAUGES = {
    "rhine-maxau": ("MAXAU", "23700200", "rhine", "Maxau"),
    "rhine-kaub": ("KAUB", "25700100", "rhine", "Kaub"),
    "rhine-ruhrort": ("RUHRORT", "2770010", "rhine", "Duisburg-Ruhrort"),
    "elbe-dresden": ("DRESDEN", "501060", "elbe", "Dresden"),
    "elbe-magdeburg": ("MAGDEBURG-STROMBRUECKE", "502180", "elbe", "Magdeburg-Strombrücke"),
    "elbe-wittenberge": ("WITTENBERGE", "503050", "elbe", "Wittenberge"),
}


def load_hyd1d() -> pd.DataFrame:
    p = HDIR / "df.gauging_data_latest.RDS"
    require_cache(p)
    df = list(pyreadr.read_r(str(p)).values())[0]
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df


def po_daily(number: str) -> tuple[pd.DataFrame, list[str]]:
    files = sorted(PDIR.glob(f"{number}_W_*.json"))
    frames = []
    for i, f in enumerate(files):  # later pulls win where pulls overlap
        d = pd.DataFrame(json.loads(f.read_text()))
        if len(d):
            d["pull"] = i
            frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["date", "level", "n"]), [f.name for f in files]
    m = pd.concat(frames).sort_values("pull").drop_duplicates("timestamp", keep="last")
    t = pd.to_datetime(m.timestamp, utc=True) + pd.Timedelta(hours=1)  # MEZ (UTC+1), German hydrological day
    m["date"] = t.dt.strftime("%Y-%m-%d")
    g = m.groupby("date").value.agg(["mean", "size"]).rename(columns={"mean": "level", "size": "n"})
    g = g[g.n >= MIN_VALUES_PER_DAY].reset_index()
    g["level"] = g.level.round(0)  # whole cm, as hyd1d does for its own PEGELONLINE-based days
    return g, [f.name for f in files]


def main():
    args = parse_args(__doc__)
    HDIR.mkdir(parents=True, exist_ok=True)
    PDIR.mkdir(parents=True, exist_ok=True)
    s = session()
    side = HDIR / "download_info.json"
    if args.refresh:
        r = get(s, HYD1D_URL, timeout=600)
        (HDIR / "df.gauging_data_latest.RDS").write_bytes(r.content)
        side.write_text(json.dumps({"url": HYD1D_URL, "last_modified": r.headers.get("Last-Modified"),
                                    "bytes": len(r.content)}, indent=1))
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
        for _, number, _, _ in GAUGES.values():
            st = get(s, f"{PO}/stations/{number}.json?includeTimeseries=true").json()
            (PDIR / f"{number}_station.json").write_text(json.dumps(st, indent=1, ensure_ascii=False))
            w = get(s, f"{PO}/stations/{number}/W/measurements.json?start=P31D").json()
            (PDIR / f"{number}_W_{stamp}.json").write_text(json.dumps(w))
    require_cache(side)
    info = json.loads(side.read_text())
    hy = load_hyd1d()
    for gid, (hname, number, river, name) in GAUGES.items():
        stp = PDIR / f"{number}_station.json"
        require_cache(stp)
        st = json.loads(stp.read_text())
        ts = next(t for t in st["timeseries"] if t["shortname"] == "W")
        gz = ts["gaugeZero"]
        h = hy[hy.gauging_station == hname][["date", "w"]].rename(columns={"w": "level"})
        n_na = int(h.level.isna().sum())
        h = h.dropna()
        h["quality"] = "measured"
        h.loc[h.date.str[:4].astype(int) > VALIDATED_THROUGH, "quality"] = "provisional"
        hy_last = h.date.max()
        p, pulls = po_daily(number)
        p = p[p.date > hy_last].copy()
        p["quality"] = "provisional"
        df = pd.concat([h, p[["date", "level", "quality"]]], ignore_index=True)
        gap = ""
        if len(p):
            gap_days = (pd.Timestamp(p.date.min()) - pd.Timestamp(hy_last)).days - 1
            gap = (f"Gap left unfilled between the end of hyd1d ({hy_last}) and the first PEGELONLINE day "
                   f"({p.date.min()}): {gap_days} days.")
        full = pd.date_range(h.date.min(), hy_last)
        notes = [
            f"{h.date.min()} to {hy_last}: BfG hyd1d daily mean W (station {hname}), file "
            f"{info['url']} (Last-Modified {info['last_modified']}).",
            f"hyd1d values through {VALIDATED_THROUGH} are marked measured (validated by the WSV/BfG); "
            f"values from {VALIDATED_THROUGH + 1} are means of PEGELONLINE raw data, not validated, and marked "
            "provisional (df.gauging_data help page). hyd1d has no per-value flag.",
            f"Missing days inside the hyd1d span: {len(full) - len(h)}; empty values dropped: {n_na}.",
            f"After hyd1d: PEGELONLINE 15-minute raw W (WASSERSTAND ROHDATEN), daily mean over MEZ days "
            f"(UTC+1), rounded to whole cm as hyd1d does, only days with at least {MIN_VALUES_PER_DAY} of 96 values; "
            f"all marked provisional. "
            f"{len(p)} days from {len(pulls)} saved pull(s): {', '.join(pulls)}.",
        ] + ([gap] if gap else []) + [
            f"Gauge zero from PEGELONLINE station metadata: {gz['value']} {gz['unit']} (DHHN2016), valid from "
            f"{gz['validFrom']}. hyd1d levels are relative to the gauge zero in force at the time. "
            + ("The 2019-11-01 date, shared by most WSV gauges, marks the switch from DHHN92 to DHHN2016, not a "
               "physical change, and does not change W." if gz["validFrom"] == "2019-11-01" else
               "This date differs from the 2019-11-01 height-system switch seen at most WSV gauges; the reason "
               "was not found. The datum-step scan (hyd1d_stepscan.py) shows no step at that date."),
            "Coordinates and river km from PEGELONLINE station metadata "
            f"(km {st.get('km')}, agency {st.get('agency')})." + (f" Station remark: {st['remark']}" if st.get("remark") else ""),
        ]
        meta = {
            "id": gid, "river": river, "name": name, "country": "Germany",
            "lat": round(st["latitude"], 6), "lon": round(st["longitude"], 6), "kind": "river",
            "source": "BfG hyd1d + PEGELONLINE (WSV)",
            "source_url": f"{HYD1D_URL} ; {PO}/stations/{number}/W/measurements.json",
            "station_code": f"PEGELONLINE {number} (uuid {st['uuid']}); hyd1d {hname}",
            "unit": "cm", "datum": f"cm above gauge zero ({gz['value']} m NHN, DHHN2016)",
            "daily_stat": "mean",
            "license": "PEGELONLINE part: DL-DE->Zero-2.0 (WSV). hyd1d part: no data license stated by the BfG "
                       "(see research/datasets/europe.md); clear before republishing.",
            "notes": notes,
        }
        write_gauge(df, meta)


if __name__ == "__main__":
    main()
