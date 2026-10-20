"""Environment and Climate Change Canada (Water Survey of Canada): Fraser River
daily discharge (m3/s). See scripts/fetch/FLOW.md.

Approved daily means (HYDAT) come from the GeoMet OGC API collection
hydrometric-daily-mean. After HYDAT ends, 5-minute real-time discharge from
the Water Office CSV service (parameter 47, about 18 months) plus the GeoMet
hydrometric-realtime collection (about 30 days) for any timestamps the CSV
lacks is averaged into daily means by local standard time day, as HYDAT does.
Mission has no usable discharge series of its own, so it gets Hope's.

Raw cache: data/raw/flow_eccc/<station>/
  station.json        station record (name, coordinates)
  daily_p<N>.json     HYDAT daily means, pages of 10,000
  realtime_p<N>.json  GeoMet real-time readings, pages of 10,000
  wo_<YYYY-MM>.csv    Water Office real-time discharge, one file per month
"""
from __future__ import annotations

import datetime as dt
import io
import json

import pandas as pd

from flow_common import write_flow
from na_common import RAW, need_cache, parse_args, polite_get, session

API = "https://api.weather.gc.ca/collections"
WO = "https://wateroffice.ec.gc.ca/services/real_time_data/csv/inline"
CACHE = RAW / "flow_eccc"
PAGE = 10000
MIN_HOURS = 20   # a real-time day needs readings in at least 20 of its 24 hours

RATING = ("Water Survey of Canada computes discharge from the water level through a "
          "stage-discharge rating curve, checked against periodic field measurements "
          "(Environment and Climate Change Canada).")

GAUGES = [
    dict(id="fraser-shelley", river="fraser", name="Shelley", stn="08KB001", offset="", notes=[
        "River ice in winter changes the level for a given flow, so winter days marked with "
        "the ice symbol (B) are estimated by other means; they are marked estimated here "
        "(Environment and Climate Change Canada).",
        "Discharge at Shelley starts in 1950, decades before the level record shown here, "
        "which starts in 2011 (Environment and Climate Change Canada).",
    ]),
    dict(id="fraser-hope", river="fraser", name="Hope", stn="08MF005", offset="", notes=[
        "HYDAT lists Hope as regulated: its drainage area includes the Nechako River behind "
        "Kenney Dam, although no dam sits on the Fraser main stem (Environment and Climate "
        "Change Canada).",
        "The riverbed at Hope has built up and cut down over the century, so the rating has "
        "been redrawn many times (BC flood flows review).",
    ]),
    dict(id="fraser-mission", river="fraser", name="Mission", stn="08MF005",
         offset="Hope, 68 km upstream", notes=[
             "Mission is tidal and its own discharge record is near-complete only from 1965 to "
             "the early 1990s, so this is the flow at Hope, 68 km upstream (Environment and "
             "Climate Change Canada).",
             "The Harrison River and other tributaries join between Hope and Mission, so flow "
             "at Mission is higher than the flow shown here (Environment and Climate Change "
             "Canada).",
         ]),
]


def save(path, text: str) -> None:
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(text)
    part.rename(path)


def paged(sess, coll: str, params: dict, d, prefix: str) -> None:
    for old in d.glob(f"{prefix}_p*.json"):
        old.unlink()
    offset, n = 0, 1
    while True:
        r = polite_get(sess, f"{API}/{coll}/items", params={
            **params, "f": "json", "limit": PAGE, "offset": offset})
        save(d / f"{prefix}_p{n}.json", r.text)
        got = len(r.json().get("features", []))
        print(f"    {coll} page {n}: {got}")
        if got < PAGE:
            break
        offset += PAGE
        n += 1


def download(stn: str, sess) -> None:
    d = CACHE / stn
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {stn}")
    r = polite_get(sess, f"{API}/hydrometric-stations/items",
                   params={"f": "json", "STATION_NUMBER": stn})
    save(d / "station.json", r.text)
    paged(sess, "hydrometric-daily-mean", {"STATION_NUMBER": stn, "sortby": "DATE"}, d, "daily")
    paged(sess, "hydrometric-realtime", {"STATION_NUMBER": stn, "sortby": "DATETIME"}, d, "realtime")
    for old in d.glob("wo_*.csv"):
        old.unlink()
    today = dt.date.today()
    m = (pd.Timestamp(today) - pd.DateOffset(months=19)).to_period("M")
    while m <= pd.Timestamp(today).to_period("M"):
        r = polite_get(sess, WO, params={
            "stations[]": stn, "parameters[]": "47",
            "start_date": f"{m.start_time:%Y-%m-%d} 00:00:00",
            "end_date": f"{m.end_time:%Y-%m-%d} 23:59:59"})
        save(d / f"wo_{m}.csv", r.text)
        print(f"    water office {m}: {max(r.text.count(chr(10)) - 1, 0)} rows")
        m += 1


def load(d, prefix: str) -> pd.DataFrame:
    rows = []
    for f in sorted(d.glob(f"{prefix}_p*.json")):
        rows += [x["properties"] for x in json.loads(f.read_text())["features"]]
    return pd.DataFrame(rows)


def load_unit_values(d) -> pd.DataFrame:
    parts = []
    for f in sorted(d.glob("wo_*.csv")):
        txt = f.read_text(encoding="utf-8-sig")
        if txt.count("\n") < 1:
            continue
        w = pd.read_csv(io.StringIO(txt), dtype=str)
        w.columns = [c.strip().split("/")[0].strip() for c in w.columns]
        if w.empty:
            continue
        if set(w["Parameter"].unique()) != {"47"}:
            raise SystemExit(f"{f}: parameter is not 47 (discharge)")
        parts.append(pd.DataFrame({
            "utc": pd.to_datetime(w["Date"], utc=True), "flow": pd.to_numeric(w["Value"]),
            "approval": w["Approval"].fillna(""), "symbol": w["Symbol"].fillna(""),
            "src": "wateroffice"}))
    cols = ["utc", "flow", "approval", "symbol", "src"]
    wo = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=cols)
    geo = load(d, "realtime")
    if not geo.empty:
        geo = geo[geo["DISCHARGE"].notna()]
        geo = pd.DataFrame({"utc": pd.to_datetime(geo["DATETIME"], utc=True),
                            "flow": geo["DISCHARGE"].astype(float),
                            "approval": "Provisional (GeoMet real-time)",
                            "symbol": geo["DISCHARGE_SYMBOL_EN"].fillna(""), "src": "geomet"})
        geo = geo[~geo["utc"].isin(set(wo["utc"]))]
    keep = [x for x in (wo, geo) if len(x)]
    out = pd.concat(keep, ignore_index=True) if keep else wo
    return out[out["flow"].notna()].drop_duplicates("utc").sort_values("utc")


def hydat_quality(sym: str) -> str:
    s = sym.strip()
    if s in ("B", "E") or s.startswith("Ice") or s.startswith("Estimated"):
        return "estimated"
    return "measured"


def build(g: dict) -> None:
    d = CACHE / g["stn"]
    need_cache(d / "station.json")
    st = json.loads((d / "station.json").read_text())["features"][0]
    p = st["properties"]
    notes = [RATING] + list(g["notes"])

    daily = load(d, "daily")
    if daily.empty:
        need_cache(d / "daily_p1.json")
    if daily["DATE"].duplicated().any():
        raise SystemExit(f"{g['id']}: duplicate HYDAT dates")
    n_null = int(daily["DISCHARGE"].isna().sum())
    daily = daily[daily["DISCHARGE"].notna()].copy()
    neg = daily["DISCHARGE"] < 0
    n_neg = int(neg.sum())
    daily = daily[~neg]
    sym = daily["DISCHARGE_SYMBOL_EN"].fillna("")
    sym_counts = {k: int(v) for k, v in sym.replace("", "none").value_counts().items()}
    daily["quality"] = [hydat_quality(s) for s in sym]
    daily = daily.rename(columns={"DATE": "date", "DISCHARGE": "flow"})
    last_hydat = daily["date"].max()
    notes.append(
        f"Approved daily means (HYDAT) run from {daily['date'].min()} to {last_hydat}. Discharge "
        f"symbols: {sym_counts}. Ice conditions (B) and estimated (E) are marked estimated; "
        "partial day (A) and other symbols stay measured. Skipped "
        f"{n_null} HYDAT days with no discharge and {n_neg} negative values (Environment and "
        "Climate Change Canada).")

    rt = load_unit_values(d)
    rt_daily = pd.DataFrame(columns=["date", "flow", "quality"])
    if not rt.empty:
        lst = rt["utc"] - pd.Timedelta(hours=8)   # BC stations are UTC-8 standard time
        rt["date"] = lst.dt.strftime("%Y-%m-%d")
        rt["hour"] = lst.dt.hour
        rt["flagged"] = rt["symbol"].str.strip().isin(["B", "E"])
        agg = rt.groupby("date").agg(flow=("flow", "mean"), hours=("hour", "nunique"),
                                     flagged=("flagged", "any"))
        full = agg[agg["hours"] >= MIN_HOURS]
        both = full.join(daily.set_index("date")["flow"].rename("hydat"), how="inner")
        if len(both):
            ratio = both["flow"] / both["hydat"] - 1
            notes.append(
                f"Check: on {len(both)} days in both HYDAT and the real-time record, our daily "
                f"mean of the 5-minute readings differed from the approved HYDAT value by a "
                f"median of {ratio.median():+.1%} (range {ratio.min():+.1%} to {ratio.max():+.1%}), "
                "so real-time values may shift when approved (Environment and Climate Change "
                "Canada).")
        new = full[full.index > last_hydat]
        dropped = agg[(agg["hours"] < MIN_HOURS) & (agg.index > last_hydat)]
        rt_daily = pd.DataFrame({
            "date": new.index, "flow": new["flow"].round(3).values,
            "quality": ["estimated" if f else "provisional" for f in new["flagged"]]})
        rsym = rt["symbol"].replace("", "none").value_counts().to_dict()
        appr = rt["approval"].value_counts().to_dict()
        notes.append(
            f"After HYDAT ends: 5-minute real-time readings ({rt['utc'].min():%Y-%m-%d} to "
            f"{rt['utc'].max():%Y-%m-%d} UTC) averaged into {len(rt_daily)} daily means by local "
            f"standard time day. A day needs readings in at least {MIN_HOURS} of its 24 hours; "
            f"{len(dropped)} days left out. All real-time days are provisional, or estimated if "
            f"any reading has symbol B or E. Approval of the readings: {appr}; symbols: {rsym} "
            "(Environment and Climate Change Canada).")
        first_rt = rt_daily["date"].min() if len(rt_daily) else None
        nxt = (pd.Timestamp(last_hydat) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        if first_rt and first_rt > nxt:
            notes.append(f"No data from {nxt} to the day before {first_rt}: approved daily means "
                         "are not yet published for that period and the real-time service keeps "
                         "only about 18 months (Environment and Climate Change Canada).")
    df = pd.concat([daily[["date", "flow", "quality"]], rt_daily], ignore_index=True)
    lon, lat = st["geometry"]["coordinates"]
    meta = {
        "id": g["id"], "river": g["river"], "name": g["name"],
        "station_name": p["STATION_NAME"], "station_code": g["stn"], "country": "Canada",
        "lat": round(float(lat), 6), "lon": round(float(lon), 6),
        "same_station": g["offset"] == "", "offset_note": g["offset"],
        "kind": "river flow", "unit": "m3/s", "daily_stat": "mean",
        "source": "Environment and Climate Change Canada, Water Survey of Canada "
                  "(HYDAT daily means + real-time)",
        "source_url": f"{API}/hydrometric-daily-mean/items",
        "license": "Open Government Licence - Canada",
        "credit": "Contains information licensed under the Open Government Licence - Canada "
                  "(Environment and Climate Change Canada)",
        "flag_rule": "HYDAT (approved) days are measured, except symbols B (ice) and E "
                     "(estimated), which are estimated; real-time days are provisional.",
        "notes": notes + [f"Station status: {p.get('STATUS_EN')} (Environment and Climate "
                          "Change Canada)."],
    }
    write_flow(df, meta, decimals=3)


def main() -> None:
    args = parse_args(__doc__)
    gauges = [g for g in GAUGES if not args.only or g["id"] in args.only]
    if args.refresh:
        sess = session()
        for stn in dict.fromkeys(g["stn"] for g in gauges):
            download(stn, sess)
    for g in gauges:
        build(g)


if __name__ == "__main__":
    main()
