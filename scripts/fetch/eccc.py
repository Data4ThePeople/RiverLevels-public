"""Environment and Climate Change Canada (Water Survey of Canada) hydrometric
data: Fraser River water level.

Archived daily means (HYDAT) come from the GeoMet OGC API collection
hydrometric-daily-mean. After HYDAT ends, we average 5-minute real-time
readings into daily means (by local standard time day, as HYDAT does). The
readings come from the Water Office real-time CSV service (about 18 months,
with an approval column) plus the GeoMet hydrometric-realtime collection
(about 30 days) for any timestamps the CSV lacks. A day is 'measured' if all
its readings are approved 'Final', otherwise 'provisional'.

Raw cache: data/raw/eccc/<gauge_id>/
  station.json        station record (coordinates, vertical datum)
  daily_p<N>.json     archived daily means, pages of 10,000
  realtime_p<N>.json  GeoMet real-time readings, pages of 10,000
  wo_<YYYY-MM>.csv    Water Office real-time readings, one file per month
"""
from __future__ import annotations

import datetime as dt
import io
import json

import pandas as pd

from na_common import RAW, need_cache, parse_args, polite_get, session, write_gauge

API = "https://api.weather.gc.ca/collections"
WO = "https://wateroffice.ec.gc.ca/services/real_time_data/csv/inline"
CACHE = RAW / "eccc"
PAGE = 10000
MIN_HOURS = 20   # a real-time day needs readings in at least 20 of its 24 hours

SYMBOLS = {"B": "ice conditions (backwater)", "E": "estimated", "A": "partial day",
           "D": "dry", "R": "revised"}

GAUGES = [
    dict(id="fraser-shelley", river="fraser", name="Shelley", stn="08KB001", notes=[
        "Upper Fraser above Prince George; no dam on the Fraser main stem upstream.",
    ]),
    dict(id="fraser-hope", river="fraser", name="Hope", stn="08MF005", notes=[
        "No dam on the Fraser main stem, but HYDAT lists the station as regulated: the "
        "drainage area includes about 14,000 square km behind Kenney Dam on the Nechako.",
        "Channel change: 35 rating curves since 1912; the bed built up about 1920 to the "
        "1940s, cut down from the 1950s to 1980s, then built up again (BC flood flows "
        "review), so equal levels do not always mean equal flow.",
    ]),
    dict(id="fraser-mission", river="fraser", name="Mission", stn="08MH024", notes=[
        "Tidal at all flows (WSC), so daily means mix river flow and tide, and low flow "
        "readings depend on the tide cycle.",
        "The BC flood flows review gives a geodetic conversion of +0.073 m before 1987 and "
        "+0.043 m after, which suggests a 0.03 m change in the station datum in 1987; "
        "whether HYDAT adjusted earlier values is not stated.",
    ]),
]


def paged(sess, coll: str, params: dict, d, prefix: str) -> None:
    for old in d.glob(f"{prefix}_p*.json"):
        old.unlink()
    offset, n = 0, 1
    while True:
        j = polite_get(sess, f"{API}/{coll}/items", params={
            **params, "f": "json", "limit": PAGE, "offset": offset}).json()
        (d / f"{prefix}_p{n}.json").write_text(json.dumps(j))
        got = len(j.get("features", []))
        print(f"    {coll} page {n}: {got}")
        if got < PAGE:
            break
        offset += PAGE
        n += 1


def download(g: dict, sess) -> None:
    d = CACHE / g["id"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']}")
    st = polite_get(sess, f"{API}/hydrometric-stations/items",
                    params={"f": "json", "STATION_NUMBER": g["stn"]}).json()
    (d / "station.json").write_text(json.dumps(st, indent=1))
    paged(sess, "hydrometric-daily-mean", {"STATION_NUMBER": g["stn"], "sortby": "DATE"}, d, "daily")
    paged(sess, "hydrometric-realtime", {"STATION_NUMBER": g["stn"], "sortby": "DATETIME"}, d, "realtime")
    # Water Office real-time CSV service keeps about 18 months of 5-minute data,
    # with an approval column; fetch it month by month.
    for old in d.glob("wo_*.csv"):
        old.unlink()
    today = dt.date.today()
    m = (pd.Timestamp(today) - pd.DateOffset(months=19)).to_period("M")
    while m <= pd.Timestamp(today).to_period("M"):
        start = f"{m.start_time:%Y-%m-%d} 00:00:00"
        end = f"{m.end_time:%Y-%m-%d} 23:59:59"
        r = polite_get(sess, WO, params={"stations[]": g["stn"], "parameters[]": "46",
                                         "start_date": start, "end_date": end})
        (d / f"wo_{m}.csv").write_text(r.text)
        print(f"    water office {m}: {max(r.text.count(chr(10)) - 1, 0)} rows")
        m += 1


def load(d, prefix: str) -> pd.DataFrame:
    rows = []
    for f in sorted(d.glob(f"{prefix}_p*.json")):
        rows += [x["properties"] for x in json.loads(f.read_text())["features"]]
    return pd.DataFrame(rows)


def load_unit_values(d) -> pd.DataFrame:
    """5-minute water levels: Water Office CSV first, GeoMet real-time for any gaps."""
    parts = []
    for f in sorted(d.glob("wo_*.csv")):
        txt = f.read_text(encoding="utf-8-sig")
        if txt.count("\n") < 1:
            continue
        w = pd.read_csv(io.StringIO(txt), dtype=str)
        w.columns = [c.strip().split("/")[0].strip() for c in w.columns]
        if w.empty:
            continue
        parts.append(pd.DataFrame({
            "utc": pd.to_datetime(w["Date"], utc=True), "level": pd.to_numeric(w["Value"]),
            "approval": w["Approval"].fillna(""), "symbol": w["Symbol"].fillna(""),
            "src": "wateroffice"}))
    wo = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["utc", "level", "approval", "symbol", "src"])
    geo = load(d, "realtime")
    if not geo.empty:
        geo = geo[geo["LEVEL"].notna()]
        geo = pd.DataFrame({"utc": pd.to_datetime(geo["DATETIME"], utc=True),
                            "level": geo["LEVEL"].astype(float),
                            "approval": "Provisional (GeoMet real-time)",
                            "symbol": geo["LEVEL_SYMBOL_EN"].fillna(""), "src": "geomet"})
        geo = geo[~geo["utc"].isin(set(wo["utc"]))]
    out = pd.concat([x for x in (wo, geo) if len(x)], ignore_index=True) if (len(wo) or len(geo)) else wo
    out = out[out["level"].notna()].drop_duplicates("utc").sort_values("utc")
    return out


def build(g: dict) -> None:
    d = CACHE / g["id"]
    need_cache(d / "station.json")
    st = json.loads((d / "station.json").read_text())["features"][0]
    notes = list(g["notes"])

    daily = load(d, "daily")
    if daily.empty:
        need_cache(d / "daily_p1.json")
    if daily["DATE"].duplicated().any():
        raise ValueError(f"{g['id']}: duplicate HYDAT dates")
    n_null = int(daily["LEVEL"].isna().sum())
    daily = daily[daily["LEVEL"].notna()].copy()
    sym = daily["LEVEL_SYMBOL_EN"].fillna("")
    sym_counts = {k: int(v) for k, v in daily["LEVEL_SYMBOL_EN"].fillna("none").value_counts().items()}
    daily["quality"] = "measured"
    daily.loc[sym.str.contains("Estimated|^E$", regex=True), "quality"] = "estimated"
    daily = daily.rename(columns={"DATE": "date", "LEVEL": "level"})
    last_hydat = daily["date"].max()
    notes.append(f"Archived daily means (HYDAT): {daily['date'].min()} to {last_hydat}. Rows "
                 f"with no water level (discharge only or blank): {n_null}. Level symbols: "
                 f"{sym_counts}. Estimated (E) -> estimated. Ice (B), partial day (A) and other "
                 "symbols keep 'measured' but are counted here; ice can raise winter levels.")

    rt = load_unit_values(d)
    rt_daily = pd.DataFrame(columns=["date", "level", "quality"])
    if not rt.empty:
        # HYDAT days are local standard time days; BC stations are UTC-8 all year.
        lst = rt["utc"] - pd.Timedelta(hours=8)
        rt["date"] = lst.dt.strftime("%Y-%m-%d")
        rt["hour"] = lst.dt.hour
        rt["final"] = rt["approval"].str.startswith("Final")
        agg = rt.groupby("date").agg(level=("level", "mean"), hours=("hour", "nunique"),
                                     final=("final", "all"))
        agg["level"] = agg["level"].round(3)
        full = agg[agg["hours"] >= MIN_HOURS]
        # Datum check on days that are in both HYDAT and the real-time record.
        both = full.join(daily.set_index("date")["level"].rename("hydat"), how="inner")
        if len(both):
            dd = both["level"] - both["hydat"]
            notes.append(
                f"Datum check: on {len(both)} days found in both HYDAT and the real-time record, "
                f"our daily mean of the 5-minute readings minus the HYDAT daily mean was median "
                f"{dd.median():+.3f} m (range {dd.min():+.3f} to {dd.max():+.3f}).")
            if abs(dd.median()) > 0.02:
                raise ValueError(f"{g['id']}: real-time and HYDAT disagree by {dd.median():+.3f} m")
        else:
            notes.append("Datum check not possible: no day is in both HYDAT and the real-time "
                         "record. We assume the real-time level uses the same station datum as "
                         "HYDAT but have not verified it.")
        new = full[full.index > last_hydat]
        dropped = agg[(agg["hours"] < MIN_HOURS) & (agg.index > last_hydat)]
        rt_daily = pd.DataFrame({"date": new.index, "level": new["level"].values,
                                 "quality": ["measured" if f else "provisional" for f in new["final"]]})
        sym = rt["symbol"].fillna("").replace("", "none").value_counts().to_dict()
        appr = rt["approval"].value_counts().to_dict()
        src = rt["src"].value_counts().to_dict()
        notes.append(
            f"After HYDAT ends: 5-minute real-time readings ({rt['utc'].min():%Y-%m-%d} to "
            f"{rt['utc'].max():%Y-%m-%d} UTC; rows by source {src}) averaged into "
            f"{len(rt_daily)} daily means by local standard time day. A day counts only with "
            f"readings in at least {MIN_HOURS} of its 24 hours; {len(dropped)} days left out. "
            f"Approval of the readings: {appr}. A day whose readings are all 'Final' is "
            "'measured', otherwise 'provisional'. Symbols: " + str(sym) + ".")
        first_rt = rt_daily["date"].min() if len(rt_daily) else None
        if first_rt and first_rt > (pd.Timestamp(last_hydat) + pd.Timedelta(days=1)).strftime("%Y-%m-%d"):
            notes.append(f"No data from the day after {last_hydat} to the day before {first_rt}: "
                         "reviewed daily means are not yet published for that period, and the "
                         "Water Office real-time service only keeps about 18 months.")
    df = pd.concat([daily[["date", "level", "quality"]], rt_daily], ignore_index=True)
    lon, lat = st["geometry"]["coordinates"]
    p = st["properties"]
    meta = dict(
        id=g["id"], river=g["river"], name=g["name"], country="Canada",
        lat=round(lat, 6), lon=round(lon, 6), kind="river",
        source="Environment and Climate Change Canada, Water Survey of Canada (HYDAT + real-time)",
        source_url=f"https://wateroffice.ec.gc.ca/report/historical_e.html?stn={g['stn']}",
        station_code=g["stn"], unit="m",
        datum=f"m above station datum ({p.get('VERTICAL_DATUM')})",
        daily_stat="mean",
        license="Open Government Licence - Canada. Contains information licensed under the "
                "Open Government Licence - Canada (Environment and Climate Change Canada).",
        notes=notes + [f"Station: {p.get('STATION_NAME')}, status {p.get('STATUS_EN')}, "
                       f"vertical datum field: {p.get('VERTICAL_DATUM')}."],
    )
    meta["notes"].append("Levels rounded to 0.001 m (the published precision); the API returns "
                         "float noise such as 2.318000078201294.")
    write_gauge(meta, df, ndp=3)


def main() -> None:
    args = parse_args(__doc__)
    gauges = [g for g in GAUGES if not args.only or g["id"] in args.only]
    if args.refresh:
        sess = session()
        for g in gauges:
            download(g, sess)
    for g in gauges:
        build(g)


if __name__ == "__main__":
    main()
