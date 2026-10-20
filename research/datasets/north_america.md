# Datasets: North America

Four publishers supply the North American gauges: the U.S. Army Corps of
Engineers (CWMS), the Bureau of Reclamation (RISE), the U.S. Geological
Survey (USGS) and Environment and Climate Change Canada (ECCC). Fetch
scripts: `scripts/fetch/cwms.py`, `rise.py`, `usgs.py`, `eccc.py` (shared
helpers in `na_common.py`, gauge histories in `na_history.json`). Each
processed gauge JSON in `data/processed/` carries its own notes,
`measurement_history` and `public_notes`.

Checked October 15, 2026.

## USACE Corps Water Management System, CWMS (U.S. Army Corps of Engineers)

**What it is.** River stage (water height above a fixed gauge zero) for
seven gauges: Mississippi at St. Louis, Memphis, Helena and Vicksburg; Ohio
at Louisville (McAlpine Dam lower gauge) and Cairo; Missouri at Hermann.
Each row is one reading per day, not a daily mean.

**Where it comes from.** CWMS Data API (CDA),
`https://cwms-data.usace.army.mil/cwms-data/timeseries`, JSON with header
`Accept: application/json;version=2`. No login. Series used:

| Gauge | Office | Series |
|---|---|---|
| mississippi-stlouis | MVS | `St Louis-Mississippi.Stage.Inst.~1Day.0.MVDhist-rev` |
| mississippi-memphis | MVS | `Memphis-Mississippi.Stage.Inst.~1Day.0.MVDhist-rev` |
| mississippi-helena | MVS | `Helena-Mississippi.Stage.Inst.~1Day.0.MVDhist-rev` |
| mississippi-vicksburg | MVK | `Vicksburg.Stage.Inst.1Day.0.DCP-rev` |
| ohio-louisville | LRL | `McAlpine-MLPK2.Stage-Tailwater.Inst.1Day.0.LPMS-comp` |
| ohio-cairo | MVS | `Cairo-Ohio.Stage.Inst.~1Day.0.MVDhist-rev` |
| missouri-hermann | MVS | `Hermann-Missouri.Stage.Inst.~1Day.0.datman-rev` |

Names were confirmed with the catalog endpoint (`/catalog/TIMESERIES`).
Coordinates and gauge zero come from `/locations/<name>`. Requests go one
decade at a time (about 1 second each, 16 to 18 per gauge). The 2020s chunk
for a 160-year gauge is about 0.2 MB of JSON.

**Version and vintage.** No version number. "rev" in a series name means
the district's revised (edited) copy. The public CDA lags the internal
database: on October 15, 2026, the MVS historical files ended September 11,
2026, Louisville September 24, Hermann October 3, and Vicksburg October 14.

**Coverage.** St. Louis 1861, Cairo 1858, Louisville 1875, Helena 1871,
Memphis 1885, Vicksburg 1901, Hermann 1922 (all to 2026). We did not find
a document for Cairo's 1858 start; the earliest NWS entries are an 1871 low
and an 1882 crest. Nearly every
calendar day has a value from the first full decade on (see
`coverage_by_decade` in each JSON). Hermann's 1920s decade is 37% because
the record starts in 1922. CWMS does not say which values are direct
readings and which were filled. Nearly every value carries quality code 0
(never screened), so the file cannot tell us. Vicksburg has 48 values
flagged as replaced (interpolated or graphically estimated, 2011 to 2019,
for example a smooth run from August to November 2019) and Hermann 5; these
are marked `estimated`.

**Changes over time.** Reading time drifts within the record: St. Louis has
8,357 readings stamped 07:59 instead of 08:00; Helena 4,273 at 08:09. These
are clock-label differences, not different statistics. Vicksburg and
Louisville are stamped at 12:00 UTC (6 a.m. Central Standard Time and 7 a.m.
Eastern Standard Time). Gauge moves, from USGS station histories:
St. Louis read a nonrecording gauge 0.4 mile downstream until May 5, 1934,
then a recorder, at the same datum. Memphis moved about 1.3 miles
downstream (1932 to 1934) at the same datum, and USGS gives a correction of
0.3 ft per 10 ft of stage to match the old Beale Street gauge. Vicksburg
used at least six sites from 1871 to 1977, all on one datum but on a
sloping river; in 1927 the canal gauge read about 2 ft above the bridge
gauge. Vicksburg's median level drops about 10 ft from the 1920s to the
1930s and 1940s; site changes and channel changes may both play a part, and
the Corps file does not say which gauge each year uses. Hermann read a
gauge 480 ft downstream at a datum 0.07 ft lower until September 26, 1930.
Louisville combined several gauges before October 1939 and in 1943 to 1946
(USGS). Louisville's yearly minimum also rises from about 3 to 5 ft before
1923 to about 9 ft from 1923 on; we found no document that explains it.
The Louisville project was Locks and Dam 41 until 1960, when it was renamed
McAlpine; the present dam was built in the 1960s. None of these moves are
adjusted in the data. Each gauge's `measurement_history` has the dates and
sources.

**Suppressed, censored or masked values.** None found. Helena has one
99999 fill value; it is dropped.

**Missing data.** Missing days are simply absent. Louisville has 133 null
values and Vicksburg 5; dropped. CWMS also flags missing or rejected values
in the quality code; none appear in these series.

**Revisions.** The Corps edits recent data after review. We refresh the
whole series on each `--refresh`; there is no pinned vintage. Recent
duplicate readings (March to June 2024, a second reading at 09:00 next to
the 08:00 reading at St. Louis, Memphis and Cairo) look like a load artifact
around the daylight saving change; we keep the 08:00 reading.

**Units and rounding.** Feet above gauge zero. CWMS stores SI and converts,
so values come back as 12.979999999999999; we round to 0.01 ft, the
finest precision in the files.

**Known quirks.**
- The MVS location records for Memphis and Helena have coordinates 0, 0.
  The Vicksburg District (MVK) records for the same gauges have real
  coordinates and gauge zeros, which we use.
- The Louisville series (McAlpine-MLPK2) has no coordinates; we use the LRL
  record McAlpineLWR, "Ohio River at Louisville, KY", which matches USGS
  03294500.
- Gauge zeros are listed in different datums by different offices (NGVD29
  at Memphis, Vicksburg, Louisville and Hermann; NAVD88 at St. Louis,
  Helena and Cairo). The zero itself has not moved because of this; only
  the label of its elevation differs.
- Hermann has two copies; MVDhist-rev stops in December 2020, so we use
  datman-rev.
- USGS extension: where a USGS gauge reports the same zero, we append USGS
  instantaneous readings at the CWMS reading hour after the CWMS record ends,
  marked `provisional`. We check the datum on the overlap: St. Louis
  (07010000, 33 days added, median difference 0.00 ft), Cairo
  (370000089094501, a Corps gauge relayed by USGS, 33 days, 0.00 ft) and
  Hermann (06934500, 8 days, 0.00 ft) pass. Louisville (03294500) differs
  by a median 0.06 ft at 12:00 UTC and is not extended. Memphis (07032000)
  and Vicksburg (07289000) returned no recent gage height, and Helena has
  no USGS gauge.

**Uncertainty.** We found no Corps error bars for stage. Each day has
one reading, so it can miss a crest or trough later that day. How early
readings were taken is in each gauge's `measurement_history`.

**License and attribution.** U.S. federal government work, public domain.
Credit: U.S. Army Corps of Engineers (and U.S. Geological Survey for the
extended days).

## Reclamation Information Sharing Environment, RISE (U.S. Bureau of Reclamation)

**What it is.** Daily reservoir surface elevation for Lake Powell (Glen
Canyon Dam) and Lake Mead (Hoover Dam), in feet above sea level. Each row
is one instantaneous daily value.

**Where it comes from.** RISE API, `https://data.usbr.gov/rise/api/result`
(JSON:API, header `Accept: application/vnd.api+json`), item 508 (Powell,
source database `uchdb2`, Upper Colorado) and item 6123 (Mead, `lchdb2`,
Lower Colorado). No login. Pages of 10,000 rows take about 7 seconds each;
3 pages for Powell, 4 for Mead. The `order=ASC` parameter is ignored; rows
come newest first. Coordinates come from the RISE location record.

**Version and vintage.** Updated daily (catalog `updateFrequency: daily`).
Powell runs to 2026-10-13 and Mead to 2026-10-13 as downloaded.

**Coverage.** Powell 1963-12-28 on, Mead 1935-02-02 on, both with a value
on every day (share 1.0 in every decade). Both records begin while the lake
was filling: Mead's first value is 670.0 ft, more than 500 ft below full
pool. RISE does not say which values are direct readings.

**Changes over time.** Not documented in RISE. We found no record of how
or where Reclamation measures either lake's elevation, or of instrument
changes. Glen Canyon Dam began storing water upstream of Mead in March 1963,
which changed Mead's inflow.

**Suppressed, censored or masked values.** None.

**Missing data.** None in the period of record.

**Revisions.** The catalog disclaimer reads: "Data are provisional and
subject to revision unless otherwise noted." The per-value `status` field is
empty for every row, so RISE gives no row-level approval. Nearly all rows
carry an update date, which looks like bulk reloads, so RISE cannot show
which past values were revised. Our rule: values from October 1, 2025 on
(the current water year, plus the previous one until six months after it
ends) are `provisional`; earlier values `measured`. That puts the 2026
record lows (Powell 3,516.62 ft on September 15, 2026; Mead 1,037.60 ft on
October 9, 2026) in the provisional set.

**Units and rounding.** Feet, to 0.01 ft (earlier years often to 0.1 ft).
The series metadata gives no vertical datum. The RISE location record lists
EGM96 for Powell and "USGS 1912" for Mead; those fields describe the
location point. Reclamation's 2001 Lake Mead sedimentation survey says
Mead elevations use the dam's 1935 construction survey datum (add 0.55 ft
for NGVD29), and a Reclamation and Park Service dataset puts NAVD88 about
2 ft away. A USGS map service lists Reclamation's Powell elevations as
NGVD29, with NAVD88 about 2.91 ft higher. So the two lakes are not on the
same datum, and neither is on NAVD88. Sources are in `measurement_history`.

**Known quirks.** Daily values are stamped 07:00 UTC, which is midnight
Mountain Standard Time; we use the Mountain day. A RISE text search for
"Lake Mead elevation" returns 8,926 catalog items, most not about Mead, so
the item ids must be pinned.

**Uncertainty.** Not published by RISE.

**License and attribution.** U.S. federal government work, public domain.
Credit: U.S. Bureau of Reclamation.

## National Water Information System, NWIS (U.S. Geological Survey)

**What it is.** Daily mean gage height (parameter 00065, statistic 00003)
for the Missouri River at Bismarck, ND (06342500) and the Ohio River at
Cincinnati, OH (03255000), in feet above the gauge datum.

**Where it comes from.** `https://waterservices.usgs.gov/nwis/dv/`
(tab-separated RDB), and `/nwis/site/` for coordinates and datum. No login.
Both downloads take under 5 seconds. USGS plans to retire this legacy
service in favor of `api.waterdata.usgs.gov`; the script may need to move.

**Version and vintage.** Each value carries an approval code: A (approved)
or P (provisional), with an extra "e" when USGS estimated the value. USGS
revises provisional values until it approves them.

**Coverage.** Bismarck 1897-04-05 to 2026-10-14 (45,755 days); Cincinnati
1987-10-01 to 2026-10-14 (13,302 days). Bismarck's 1920s decade has values
on 74% of days and its 1980s on 93%. Cincinnati is missing 17% of days in
the 1990s. Bismarck has 14 estimated days; Cincinnati none.

**Changes over time.** Bismarck has an unadjusted datum break. USGS
Water-Supply Paper 1309 says the recorder datum was lowered 4.24 ft to the
present datum on October 1, 1934; before that, readings (a chain gauge
2,100 ft upstream until October 17, 1928, then the recorder) were on a
datum 4.24 ft higher. The daily values are not adjusted: the yearly
minimum jumps from -2.9 ft in 1934 to +2.4 ft in 1935. From April 1936 to
September 1937 a wire-weight gauge at a datum 0.47 ft lower was used. Do
not compare Bismarck levels across 1934 without adding 4.24 ft to the
earlier values; our files leave them as published. Garrison Dam, about 75
miles upstream, has regulated flow since November 1953. Cincinnati is held
up at low flow by Markland Locks and Dam (operating from 1963, per the
NWS), before this record starts; the NWS lists four gauge moves at
Cincinnati from 1858 to 1947, all before this file.

**Suppressed, censored or masked values.** None. USGS can publish text
codes instead of numbers (Ice, Eqp, Bkw); none appear in these two series.

**Missing data.** Missing days are absent from the file.

**Revisions.** Provisional values change; we refresh the full series.

**Units and rounding.** Feet to 0.01 ft. Gauge datum 1,619.64 ft NAVD88
(Bismarck; 1,618.28 ft NGVD29 in the 2004 USGS report) and 428.05 ft NAVD88 (Cincinnati) per the USGS site record.

**Known quirks.** The Cincinnati stage record kept by the National Weather
Service and the Corps starts in 1858; the USGS daily file only starts in
1987.

**Uncertainty.** USGS states datum accuracy in the site record (0.01 ft at
Bismarck, 0.05 ft at Cincinnati). Early "daily means" may rest on one or
two staff readings a day.

**License and attribution.** U.S. federal government work, public domain.
Credit: U.S. Geological Survey.

## Water Survey of Canada hydrometric data (Environment and Climate Change Canada)

**What it is.** Daily mean water level in meters above the station datum
for the Fraser River at Shelley (08KB001), Hope (08MF005) and Mission
(08MH024).

**Where it comes from.** Archived daily means (HYDAT) from the GeoMet OGC
API, `https://api.weather.gc.ca/collections/hydrometric-daily-mean/items`.
After HYDAT ends, 5-minute real-time readings from the Water Office
service `https://wateroffice.ec.gc.ca/services/real_time_data/csv/inline`
(about 18 months kept, with an approval column), plus
`hydrometric-realtime` (about 30 days) for any missing timestamps. Station
coordinates and datum from `hydrometric-stations`. No login. About 1.5
minutes for all three stations.

**Version and vintage.** HYDAT is released in batches, so reviewed data lag by months. On October
15, 2026 the daily means ended 2025-10-01 at Shelley, 2025-02-24 at Hope
and 2025-03-04 at Mission.

**Coverage.** Hope water level from 1912; Mission from 1969; Shelley water
level only from 2011 (discharge goes back further, but level does not).
The 1990s have values on only 75% of days at Hope and 58% at Mission. Our
real-time daily means start March 15, 2025, so a gap of about three weeks
remains at Hope (February 25 to March 14, 2025) and ten days at Mission.

**Changes over time.** See `measurement_history` for station moves and
datum changes from WSC station records.

**Suppressed, censored or masked values.** None.

**Missing data.** Rows with discharge and no level are dropped (22,523 at
Shelley, mostly before 2011). WSC symbols: E (estimated, no measured data
that day) is mapped to `estimated`; A (partial day; WSC says the daily mean
was estimated despite gaps in the readings), B (ice conditions), D (dry)
and R (revised) stay `measured` and are counted in each gauge's notes. Only
A and E appear in these level series.

**Revisions.** Real-time data are provisional until WSC finalizes them.
A real-time day is `measured` only when every reading that day is approved
"Final", otherwise `provisional`. We checked our averaging at Shelley, the
one station where the real-time record overlaps HYDAT: on 201 shared days
our daily means matched HYDAT with a median difference of 0.000 m (range
-0.007 to +0.001 m). Hope and Mission have no overlap, so their real-time
datum is assumed, not checked.

**Units and rounding.** Meters to 0.001 m. The API returns float noise
(2.318000078201294); we round to 0.001 m.

**Known quirks.** All three stations use an assumed datum: an arbitrary
local zero, not sea level. Mission is tidal at all flows, so its daily mean
mixes river flow and the tide. A BC government review gives a geodetic
conversion at Mission of +0.073 m before 1987 and +0.043 m after, which
suggests a 0.03 m datum change in 1987 that may not be adjusted. Hope's
channel has built up and cut down over the decades (35 rating curves since
1912), and HYDAT lists Hope as regulated because Kenney Dam on the Nechako
holds back part of the basin. Hope has no level data for 1994 and 1995 and
only 92 days in 1940. The GeoMet API refused connections once during testing
and worked on retry.

**Uncertainty.** We found no published error bars for WSC daily water level.

**License and attribution.** Open Government Licence - Canada. "Contains
information licensed under the Open Government Licence - Canada."
