"""USACE Corps Water Management System (CWMS) Data API: Mississippi, Ohio and
Missouri river stages. Optionally extends each record past the public CWMS lag
with USGS instantaneous values, only where the USGS gauge reads on the same
datum (checked on the overlap) and only as provisional values.

Raw cache: data/raw/cwms/<gauge_id>/
  catalog.json        catalog entry with the series extents
  location.json       CWMS location record (coordinates, gauge zero)
  ts_<decade>.json    timeseries values, one file per decade
  usgs_site.rdb       USGS site record for the extension gauge (if any)
  usgs_iv.json        USGS instantaneous gage height for the extension window
"""
from __future__ import annotations

import datetime as dt
import json
from zoneinfo import ZoneInfo

import pandas as pd

from na_common import RAW, need_cache, parse_args, polite_get, session, write_gauge

API = "https://cwms-data.usace.army.mil/cwms-data"
HDR = {"Accept": "application/json;version=2"}
CACHE = RAW / "cwms"
FILL_MIN = 9000.0     # 99999, 9999 and similar placeholders
TODAY = dt.date.today()

GAUGES = [
    dict(id="mississippi-stlouis", river="mississippi", name="St. Louis",
         office="MVS", ts="St Louis-Mississippi.Stage.Inst.~1Day.0.MVDhist-rev",
         loc_office="MVS", loc="St Louis-Mississippi",
         usgs="07010000"),
    dict(id="mississippi-memphis", river="mississippi", name="Memphis",
         office="MVS", ts="Memphis-Mississippi.Stage.Inst.~1Day.0.MVDhist-rev",
         loc_office="MVK", loc="Memphis",
         usgs="07032000"),
    dict(id="mississippi-helena", river="mississippi", name="Helena",
         office="MVS", ts="Helena-Mississippi.Stage.Inst.~1Day.0.MVDhist-rev",
         loc_office="MVK", loc="Helena",
         usgs=None),
    dict(id="mississippi-vicksburg", river="mississippi", name="Vicksburg",
         office="MVK", ts="Vicksburg.Stage.Inst.1Day.0.DCP-rev",
         loc_office="MVK", loc="Vicksburg",
         usgs="07289000"),
    dict(id="ohio-louisville", river="ohio", name="Louisville (McAlpine Dam tailwater)",
         office="LRL", ts="McAlpine-MLPK2.Stage-Tailwater.Inst.1Day.0.LPMS-comp",
         loc_office="LRL", loc="McAlpineLWR",
         usgs="03294500"),
    dict(id="ohio-cairo", river="ohio", name="Cairo",
         office="MVS", ts="Cairo-Ohio.Stage.Inst.~1Day.0.MVDhist-rev",
         loc_office="MVS", loc="Cairo-Ohio",
         usgs="370000089094501"),
    dict(id="missouri-hermann", river="missouri", name="Hermann",
         office="MVS", ts="Hermann-Missouri.Stage.Inst.~1Day.0.datman-rev",
         loc_office="MVS", loc="Hermann-Missouri",
         usgs="06934500"),
]

# Gauge-specific notes from the location records and the research.
EXTRA_NOTES = {
    "mississippi-stlouis": [
        "Gauge at the foot of Market Street, river mile 179.6 above the Ohio. "
        "Gauge zero 379.58 ft NAVD88 per the CWMS location record and the USGS "
        "site record for 07010000.",
        "A second CWMS series (datman-rev) holds the same gauge; MVDhist-rev "
        "was used because it is the Mississippi Valley Division historical file.",
    ],
    "mississippi-memphis": [
        "Record low in this file: -11.97 ft on 2023-10-17 (08:00 reading). The "
        "National Weather Service lists -12.06 ft that day, which is likely the "
        "lowest instantaneous value rather than the morning reading.",
        "USGS: staff gauge 1,000 ft downstream from September 1932 to December "
        "1934, then a recorder below Harahan Bridge from 1934-12-22, about 1.3 "
        "miles below the old Beale Street gauge, at the same datum.",
        "The MVS location record for Memphis-Mississippi has no coordinates "
        "(0, 0). Lat/lon and the gauge zero (183.91 ft NGVD29) come from the "
        "MVK (Vicksburg District) location record for the same gauge. USGS "
        "07032000 lists 184.03 ft NAVD88 for the same zero.",
    ],
    "mississippi-helena": [
        "The MVS location record for Helena-Mississippi has no coordinates "
        "(0, 0). Lat/lon and the gauge zero (141.51 ft NAVD88) come from the "
        "MVK location record for the same gauge. The Corps changed the listed "
        "zero from 141.70 ft NGVD29 to 141.51 ft NAVD88 on 2024-07-30; the NWS "
        "still lists 141.70 ft NGVD29.",
        "Reading times: 4,273 days are stamped 08:09 instead of 08:00.",
        "No USGS gage-height series at Helena, so the record ends at the CWMS "
        "public lag.",
    ],
    "mississippi-vicksburg": [
        "USGS lists at least six gauge sites at Vicksburg since 1871, all on the "
        "same datum but on a sloping water surface; in 1927 the Corps canal gauge "
        "read about 2 ft above the bridge gauge. The median level drops about "
        "10 ft from the 1920s to the 1930s and 1940s; site changes and channel "
        "changes may both play a part, and the file does not say which gauge "
        "each year uses.",
        "Gauge zero 46.23 ft NGVD29 per the CWMS MVK location record "
        "(USGS 07289000 lists 46.22 ft NGVD29).",
    ],
    "ohio-louisville": [
        "Series is the McAlpine Locks and Dam lower (tailwater) gauge as kept by "
        "the Louisville District LPMS. The LRL location record for this series "
        "(McAlpine-MLPK2) has no coordinates; lat/lon and gauge zero come from the "
        "LRL record McAlpineLWR (Ohio River at Louisville, KY), which matches "
        "USGS 03294500.",
        "Gauge zero 373.18 ft NGVD29 (374.00 ft on the Ohio River datum, per USGS). "
        "The gauge sits below McAlpine Locks and Dam (Locks and Dam 41 until 1960; "
        "the present dam was built in the 1960s). USGS says various combinations "
        "of gauges near Louisville were used before October 1939 and in 1943 to 1946.",
        "Observed in the data, cause not documented: the yearly minimum rises from "
        "about 3 to 5 ft before 1923 to about 9 ft from 1923 on. Do not compare "
        "low-water readings across 1923 without checking.",
    ],
    "ohio-cairo": [
        "Gauge zero 270.03 ft NAVD88 per the CWMS location record. Cairo stage "
        "also reflects Mississippi River backwater at the confluence.",
    ],
    "missouri-hermann": [
        "Series is datman-rev (MVS data management, 1922 to present). The "
        "MVDhist-rev copy of this gauge stops in December 2020.",
        "Gauge zero 481.56 ft NGVD29 per the CWMS location record; USGS "
        "06934500 lists 481.50 ft NAVD88 for the same zero.",
        "Flow at Hermann is regulated by the six Missouri River mainstem dams "
        "upstream (Fort Peck closed 1937, Garrison 1953, Gavins Point 1955).",
        "USGS: before September 26, 1930 readings came from a nonrecording gauge "
        "480 ft downstream at a datum 0.07 ft lower; not adjusted here.",
    ],
}


# ---------------------------------------------------------------- download

def download(g: dict, sess) -> None:
    d = CACHE / g["id"]
    d.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {g['id']}")
    r = polite_get(sess, f"{API}/catalog/TIMESERIES", headers=HDR, params={
        "office": g["office"], "like": g["ts"].replace("~", "\\~").replace(".", "\\."),
        "page-size": 50, "include-extents": "true"})
    cat = [e for e in r.json().get("entries", []) if e["name"] == g["ts"]]
    if not cat:
        # the regex form failed; fall back to a plain prefix search
        r = polite_get(sess, f"{API}/catalog/TIMESERIES", headers=HDR, params={
            "office": g["office"], "like": g["ts"].split(".")[0] + ".*",
            "page-size": 500, "include-extents": "true"})
        cat = [e for e in r.json().get("entries", []) if e["name"] == g["ts"]]
    if not cat:
        raise SystemExit(f"{g['ts']} not in CWMS catalog for {g['office']}")
    (d / "catalog.json").write_text(json.dumps(cat[0], indent=1))
    first_year = int(cat[0]["extents"][0]["earliest-time"][:4])

    r = polite_get(sess, f"{API}/locations/{g['loc']}", headers=HDR,
                   params={"office": g["loc_office"], "unit": "EN"})
    (d / "location.json").write_text(json.dumps(r.json(), indent=1))

    for old in d.glob("ts_*.json"):
        old.unlink()
    for dec in range(first_year // 10 * 10, TODAY.year // 10 * 10 + 10, 10):
        begin = f"{dec}-01-01T00:00:00Z"
        end = min(dt.date(dec + 10, 1, 1), TODAY + dt.timedelta(days=1)).isoformat() + "T00:00:00Z"
        values, page, meta = [], None, None
        while True:
            p = {"office": g["office"], "name": g["ts"], "begin": begin, "end": end,
                 "unit": "EN", "page-size": 10000}
            if page:
                p["page"] = page
            j = polite_get(sess, f"{API}/timeseries", headers=HDR, params=p).json()
            meta = meta or {k: v for k, v in j.items() if k not in ("values", "page", "next-page")}
            values += j.get("values") or []
            page = j.get("next-page")
            if not page:
                break
        meta["values"] = values
        (d / f"ts_{dec}.json").write_text(json.dumps(meta))
        print(f"    {dec}s: {len(values)} values")

    if g["usgs"]:
        r = polite_get(sess, "https://waterservices.usgs.gov/nwis/site/", params={
            "format": "rdb", "sites": g["usgs"], "siteOutput": "expanded", "siteStatus": "all"})
        (d / "usgs_site.rdb").write_text(r.text)
        start = (TODAY - dt.timedelta(days=120)).isoformat()
        r = polite_get(sess, "https://waterservices.usgs.gov/nwis/iv/", params={
            "format": "json", "sites": g["usgs"], "parameterCd": "00065",
            "startDT": start, "endDT": TODAY.isoformat(), "siteStatus": "all"})
        (d / "usgs_iv.json").write_text(r.text)


# ---------------------------------------------------------------- quality

def cwms_quality(code: int) -> str | None:
    """Map a CWMS quality code to our quality, or None to drop the value.

    CWMS packs quality into bits (CWMS Data Quality documentation): bit 0
    screened; bits 1-4 validity (okay, missing, questionable, rejected);
    bits 5-6 range; bit 7 value changed; bits 8-10 replacement cause (none,
    automatic, interactive, manual, restored); bits 11-14 replacement method
    (none, linear interpolation, explicit change, missing, graphical); bit 31
    protected. Code 0 means "not screened", which is what nearly every value
    in these historical files carries. Any replaced value counts as estimated.
    """
    if code is None:
        return "measured"
    u = int(code) & 0xFFFFFFFF
    if u & (1 << 2) or u & (1 << 4):   # missing or rejected
        return None
    cause = (u >> 8) & 0b111
    method = (u >> 11) & 0b1111
    if (u >> 7) & 1 or cause or method:
        return "estimated"
    return "measured"


# ---------------------------------------------------------------- build

def load_cwms(g: dict, notes: list[str]):
    d = CACHE / g["id"]
    files = sorted(d.glob("ts_*.json"))
    if not files:
        need_cache(d / "ts_XXXX.json")
    rows, tzname, units = [], None, None
    for f in files:
        j = json.loads(f.read_text())
        tzname = tzname or j.get("time-zone")
        units = units or j.get("units")
        rows += j["values"]
    tz = ZoneInfo(tzname or "US/Central")
    df = pd.DataFrame(rows, columns=["t", "v", "q"])
    n_raw = len(df)
    df = df.drop_duplicates()  # decade chunks share no boundary values, but be safe
    if len(df) != n_raw:
        notes.append(f"{n_raw - len(df)} exact duplicate rows across request chunks removed.")
    n_null = int(df["v"].isna().sum())
    df = df[df["v"].notna()]
    fills = df["v"] >= FILL_MIN
    n_fill = int(fills.sum())
    df = df[~fills]
    df["quality"] = [cwms_quality(q) for q in df["q"]]
    n_drop_q = int(df["quality"].isna().sum())
    df = df[df["quality"].notna()]
    ts = pd.to_datetime(df["t"], unit="ms", utc=True).dt.tz_convert(tz)
    df["date"] = ts.dt.strftime("%Y-%m-%d")
    df["hour"] = ts.dt.strftime("%H:%M")
    qc = df["q"].value_counts().to_dict()
    notes.append(f"CWMS quality codes in the file: {dict(sorted((int(k), int(v)) for k, v in qc.items()))}. "
                 "Code 0 means the value was never screened; CWMS carries no approved/provisional "
                 "flag for these historical files, so unflagged values are 'measured'. Values "
                 "flagged as replaced (interpolated, manually changed or graphically estimated) "
                 f"are 'estimated': {int((df['quality'] == 'estimated').sum())} days.")
    notes.append(f"Dropped {n_fill} fill values (>= {FILL_MIN:g}, such as 99999) and "
                 f"{n_null} null values; {n_drop_q} values flagged missing or rejected.")
    # Some files hold two readings on one local date (March to April 2024 at
    # MVS gauges: 08:00 plus 09:00). Keep the reading at the gauge's usual
    # hour and drop the extra one; anything else is a hard failure.
    hours = df["hour"].value_counts()
    top = hours.index[0]
    dup = df["date"].duplicated(keep=False)
    extra = dup & (df["hour"] != top) & df["date"].isin(df.loc[dup & (df["hour"] == top), "date"])
    if extra.any():
        ex = df[extra]
        notes.append(f"{int(extra.sum())} days in {ex['date'].min()} to {ex['date'].max()} have a "
                     f"second reading (at {', '.join(sorted(ex['hour'].unique()))}) besides the "
                     f"{top} reading; kept the {top} reading and dropped the extra one.")
        df = df[~extra]
    dup = df["date"].duplicated(keep=False)
    if dup.any():
        raise ValueError(f"{g['id']}: {int(dup.sum())} rows share a local date, e.g. "
                         f"{df.loc[dup, ['date', 'hour', 'v']].head(6).to_dict('records')}")
    hours = df["hour"].value_counts()
    utc = pd.to_datetime(df["t"], unit="ms", utc=True).dt.strftime("%H:%M").value_counts()
    notes.append(f"One instantaneous reading per day (not a daily mean). In the file's time zone "
                 f"({tzname}): " + ", ".join(f"{h} on {n} days" for h, n in hours.iloc[:4].items())
                 + "; in UTC: " + ", ".join(f"{h} on {n} days" for h, n in utc.iloc[:4].items()) + ".")
    df = df.rename(columns={"v": "level"})
    return df[["date", "level", "quality", "hour"]], units, top, tzname or "US/Central"


def usgs_extension(g: dict, base: pd.DataFrame, read_hour: str, tzname: str, notes: list[str]) -> pd.DataFrame:
    """USGS IV values at the CWMS reading hour, after the CWMS record ends.

    Appended only when the overlap shows the same datum (median difference
    within 0.05 ft over at least 10 shared days). Always marked provisional.
    """
    d = CACHE / g["id"]
    if not g["usgs"]:
        return base.iloc[0:0]
    need_cache(d / "usgs_iv.json")
    j = json.loads((d / "usgs_iv.json").read_text())
    series = j["value"]["timeSeries"]
    vals = []
    for s in series:
        nodata = s["variable"].get("noDataValue")
        for block in s["values"]:
            for v in block["value"]:
                x = float(v["value"])
                if nodata is not None and x == nodata:
                    continue
                vals.append((v["dateTime"], x, ",".join(v.get("qualifiers", []))))
    if not vals:
        notes.append(f"USGS {g['usgs']} returned no recent gage height; no extension.")
        return base.iloc[0:0]
    iv = pd.DataFrame(vals, columns=["dt", "level", "qual"]).drop_duplicates("dt")
    t = pd.to_datetime(iv["dt"], utc=True).dt.tz_convert(ZoneInfo(tzname))
    iv["date"] = t.dt.strftime("%Y-%m-%d")
    iv["hour"] = t.dt.strftime("%H:%M")
    iv = iv[iv["hour"] == read_hour]
    m = base.merge(iv, on="date", suffixes=("_cwms", "_usgs"))
    if len(m) < 10:
        notes.append(f"USGS {g['usgs']}: only {len(m)} days overlap at {read_hour}; "
                     "datum check not possible, no extension.")
        return base.iloc[0:0]
    diff = (m["level_usgs"] - m["level_cwms"])
    med, mad = float(diff.median()), float(diff.abs().max())
    if abs(med) > 0.05:
        notes.append(f"USGS {g['usgs']} differs from CWMS by a median {med:+.2f} ft over "
                     f"{len(m)} overlapping days at {read_hour}; not the same datum or "
                     "a different reading method, so no extension.")
        return base.iloc[0:0]
    ext = iv[iv["date"] > base["date"].max()].copy()
    if ext.empty:
        return ext
    ext["quality"] = "provisional"
    notes.append(f"Extended {len(ext)} days ({ext['date'].min()} to {ext['date'].max()}) past "
                 f"the CWMS public lag with USGS {g['usgs']} instantaneous gage height at "
                 f"{read_hour} local, the CWMS reading hour. Same datum: over {len(m)} "
                 f"overlapping days the median difference was {med:+.2f} ft (largest "
                 f"{mad:.2f} ft). USGS marks these values provisional, and so do we.")
    return ext[["date", "level", "quality", "hour"]]


def build(g: dict) -> None:
    d = CACHE / g["id"]
    need_cache(d / "location.json")
    loc = json.loads((d / "location.json").read_text())
    notes: list[str] = []
    df, units, read_hour, tzname = load_cwms(g, notes)
    if units != "ft":
        raise ValueError(f"{g['id']}: unexpected units {units}")
    ext = usgs_extension(g, df, read_hour, tzname, notes) if g["usgs"] else df.iloc[0:0]
    full = pd.concat([df, ext], ignore_index=True)
    lat, lon = loc.get("latitude"), loc.get("longitude")
    if not lat or not lon:
        raise ValueError(f"{g['id']}: location has no coordinates")
    zero = loc.get("elevation")
    vd = loc.get("vertical-datum")
    notes += EXTRA_NOTES.get(g["id"], [])
    notes.append("Levels are rounded to 0.01 ft: the API converts from stored meters and "
                 "returns float noise such as 12.979999999999999.")
    meta = dict(
        id=g["id"], river=g["river"], name=g["name"], country="United States",
        lat=round(float(lat), 6), lon=round(float(lon), 6), kind="river",
        source="USACE CWMS Data API" + (" + USGS NWIS (provisional extension)" if len(ext) else ""),
        source_url=f"{API}/timeseries?office={g['office']}&name={g['ts']}",
        station_code=f"{g['office']}:{g['ts']}",
        unit="ft",
        datum=f"ft above gauge zero ({zero:.2f} ft {vd})" if zero else "ft above gauge zero",
        daily_stat="single reading",
        license="Public domain (US federal government work). Credit: U.S. Army Corps of Engineers"
                + (", U.S. Geological Survey." if len(ext) else "."),
        notes=notes,
    )
    write_gauge(meta, full, ndp=2)


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
