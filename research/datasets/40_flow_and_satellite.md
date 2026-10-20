# Datasets: Flow (discharge) and satellite levels

Researched October 17, 2026, after a reviewer suggested DAHITI and the
UW-Madison SAGE discharge database. **Built October 17, 2026** for 37
gauges (34 beside a level gauge, 3 flow-only) from the publishers' APIs;
see "As built" below. SAGE/RivDIS, GRDC-Caravan, GEOGLOWS and DAHITI are
documented here but **not on the page**. Facts were checked by real requests on October 17,
2026 where no account was needed; full notes with URLs are kept with the
research.

Three kinds of data, never mixed on one axis:
- **Measured level** (the rest of this file set): a gauge reading above a
  local zero.
- **Flow (discharge):** how much water passes, almost always computed from
  level through a rating curve. Measured flow and modeled flow are kept
  apart.
- **Satellite level:** height above a model of sea level at the point where
  a satellite track crosses the river, every 10 to 35 days.

## Rules that apply to every flow series

**What a discharge value is.** Discharge is how much water passes the gauge,
in cubic meters per second (m³/s) or cubic feet per second (cfs; 1 cfs is
0.0283 m³/s). Almost no publisher measures it every day. Crews measure flow
a few times a year, and those measurements fix a rating curve: a rule that
turns a level into a flow. Each daily discharge is the day's level put
through the rating in force at the time. So discharge is only as good as
the level and the rating.

**Limits that apply to every rated series.**
- Rating curves are refit as new measurements come in, and riverbeds change.
  Publishers apply shifts between measurements and revise recent months,
  sometimes years. Old values may have been computed with a rating that was
  later replaced.
- The highest and lowest flows are often above or below any flow ever
  measured at the gauge, so the rating is extended beyond its data. Record
  floods and record lows are the least certain values in the series.
- Ice changes the level for a given flow. In winter, publishers estimate
  flow by other means (Bismarck, Shelley).
- Backwater from a dam, a tide or a larger river raises the level without a
  change in flow. At those gauges a simple rating does not work, and the
  publisher uses other methods or publishes no discharge (Manaus, Mission,
  Ladário for most years).
- Where flow comes from a nearby station, the page will say which station and
  how far away, and the two series are not combined.


## Flow at the gauges we already show

One block per publisher. Researched for all 43 gauges.

**PEGELONLINE and BfG (Rhine at Maxau, Kaub, Ruhrort; Elbe at Dresden,
Magdeburg, Wittenberge).**

*Discharge.* PEGELONLINE publishes discharge (Q) every 15 minutes for all six
gauges, computed by the waterways administration from the level with a
discharge table. It keeps only the last 31 days, and the values are raw.
The BfG yearbook (dgj-daten.bafg.de) has checked daily discharge as PDF
tables, one year per page, for about 1998 to 2025, and summary values back
to about 1900; Ruhrort's yearbook file has level only. We found no
machine-readable long daily record that we can republish: the BfG data
service provides it on request, and GRDC holds it but forbids republishing.
No license is stated on the yearbook server. Until then these six gauges would show
no discharge history. Limits: rating curves are revised as the riverbed
changes, which on the Rhine and Elbe has been large (see the level notes on
bed erosion); BfG notes that discharge at Ruhrort cannot be computed below
120 cm right now.


**Rijkswaterstaat (Rhine at Lobith).**

*Discharge.* Same API and location as level, with Grootheid `Q` (m³/s).
One reading a day at 08:00 from 1901, then 10-minute readings in recent
years. Years before 1901 return nothing, so discharge starts 35 years after
level. Values carry the same Kwaliteitswaardecode and Statuswaarde as level;
even 1901 values are marked "Ongecontroleerd" (unchecked), so status alone
does not show which old values were checked. Lobith discharge is computed
from the level with a rating that Rijkswaterstaat updates from regular
measurements. Limits: flood peaks are above most measured flows, so they
are the least certain values. License CC0 1.0.


**GKD Bayern (Danube at Pfelling and Hofkirchen).**

*Discharge.* Same download center as level, with the topic
`fluesse.abfluss` and daily means (`tmw`). Pfelling runs from November 1,
1925, and Hofkirchen from November 1, 1900, both earlier than their level
records. Each day has a mean, and from later years a maximum and minimum.
Values through 2025 are "Geprueft" (checked); 2026 values are "Rohdaten"
(raw) and will change. Discharge is computed from the level with a rating
curve that GKD updates. Limits: ratings are revised as the riverbed
changes; high-flood values are extended beyond measured flows. License CC BY 4.0, credit "Datenquelle: Bayerisches
Landesamt für Umwelt, www.lfu.bayern.de".


**eHYD (Danube at Kienstock).**

*Discharge.* `file=5` of the same eHYD service (Q-Tagesmittel, daily mean,
m³/s), January 1, 1978 to December 31, 2023, with one gap. Computed from
level with a rating ("Pegelschlüssel"), per the station master data, from
1976. Like level, it is yearbook data and ends in 2023. Footnotes say many
months from 1996 to 2023 were computed from filled-in levels. License CC BY
4.0, credit "Datenquelle: ehyd.gv.at".


**Hub'Eau (Seine at Paris).**

*Discharge.* `obs_elab` with `grandeur_hydro_elab=QmnJ` (daily mean flow), in
liters per second. Same historical stations as level: F700000109 (1900 to
1965), F700000110 (1966 to 1973), F700000111 (1974 to 1989), F700000102
(1990 on), and the dedicated flow station F700000103 at Austerlitz (2006 on).
Each value has a status (raw, pre-validated, validated), a method
(calculated, expert-reviewed, reconstructed) and a qualification (good,
doubtful). Before 1955, about three in four values are qualified "doubtful."
Recent days are raw. Limits: Paris flow is regulated by upstream lake
reservoirs, which hold back winter floods and raise summer low flows, so
recent flows are not natural (dates to be added from a source). License not stated.


**USGS NWIS (St. Louis, Memphis, Louisville, Bismarck, Hermann; Helena to
1977).**

*Discharge.* Parameter 00060, daily mean (statistic 00003), cfs. St. Louis
from 1861, Louisville from 1928, Bismarck from 1927, Hermann from 1928,
Memphis from 1933 with no values from about 1995 to 2014. USGS flags each day
A (approved) or P (provisional), with "e" for estimated. About 10% of
Bismarck's days are estimated, mostly winter days with ice. USGS computes
discharge from the level with a rating curve, adjusted by "shifts" after
each field measurement (usually every 6 to 8 weeks), and approves a year of
data some months after it ends. Cincinnati has only 15-minute discharge from
an index-velocity meter since October 2024. For Cairo the plan is Olmsted
(03612600, about 17 river miles upstream, from 2013); for Cincinnati,
Markland Dam (03277200, about 61 river miles downstream, from 1970); for
Helena after 1977, Memphis (about 72 river miles upstream). Limits:
on the Mississippi the same level can carry different flows on a rising and
falling river, and the earliest St. Louis values rest on few field
measurements (how USGS built the 1861 to 1930s record is not yet sourced). The legacy service is being retired; the new
API (api.waterdata.usgs.gov) returns the same values. Public domain, credit
U.S. Geological Survey.


**USACE CWMS (Vicksburg).**

*Discharge.* `MVK:Vicksburg.Flow.Inst.1Day.0.DCP-rev`, cfs, one value a day
from January 2, 1901, to September 13, 2026, the same family and reading
time as the level series. Quality code 0 (not screened) throughout, so the
Corps file gives no approval status. USGS 07289000 has daily means at
Vicksburg from 2008 and could check the overlap. Limits: same as level
(several gauge sites before 1977), plus the rating questions above. Public
domain, credit U.S. Army Corps of Engineers.


**RISE (Lake Powell, Lake Mead).**

*Discharge.* A lake has no river flow at the gauge, so the plan is to show release: the
daily average flow let through the dam. Lake Powell (Glen Canyon Dam) item
4315, from March 14, 1963; Lake Mead (Hoover Dam) item 6125, from April 1,
1934; both cfs, updated daily, provisional like the elevation series. The
release is set by dam operators under the river's operating rules, so it
reflects decisions, not just weather. Reclamation also publishes a computed
inflow for Lake Powell (item 511), not a gauged one; it swings widely from
day to day. RISE has no inflow for Lake Mead. USGS gauges just below Glen
Canyon Dam (Lees Ferry, 09380000) measure the released water independently.
Public domain, credit U.S. Bureau of Reclamation.


**ECCC Water Survey of Canada (Fraser at Shelley and Hope; Mission).**

*Discharge.* Same HYDAT and real-time services as level, field `DISCHARGE`,
m³/s. Shelley from 1950 (longer than its level record, which starts in 2011),
Hope from 1912. HYDAT is approved and runs to 2025; later days are real-time
and provisional. Each day can carry a symbol: B (ice conditions), E
(estimated), A (partial day). At Shelley about a third of days in recent
decades carry the ice symbol, because winter ice changes the level for a
given flow. Mission is tidal and has discharge only for 1965 to the early
1990s and scattered days after, so for Mission the plan is to show Hope's flow, 68 km
upstream, and say that tributaries in between add to it. Open Government
Licence - Canada.


**ANA HidroWeb (Tabatinga, Manacapuru, Óbidos; Ladário 1964 to 1973).**

*Discharge.* Same `HidroSerieHistorica` service as level, with
`tipoDados=3`, m³/s. Tabatinga from 1995, Manacapuru from 1972, Óbidos from
1968. Checked ("consistido") values run through 2023; later months are raw
and end in early to mid 2026. Each day has a status: real, estimated or
doubtful. ANA publishes no discharge at Manaus, where the Rio Negro is
backed up by the Solimões, and Ladário has discharge only for 1964 to
1973, so these two gauges would show none. Limits: on these large, flat rivers the
same level gives different flows on the rise and the fall, so ratings are
uncertain, especially at record highs and lows. License: none stated by ANA.


**INA (Paraná at Corrientes, Paraná, Rosario; Posadas to 2017).**

*Discharge.* Same a5 API as level, variable 40 (daily mean flow), m³/s:
Corrientes from 1904, Paraná and Rosario only from July 2015, Posadas 1970
to September 2017. INA labels the per-reading series as computed from a
rating curve ("curva de gasto"). Posadas sits in the Yacyretá reservoir; for
recent years the plan would be Yacyretá's inflow or outflow, 85 km downstream.
No per-value quality flags. Asunción has no discharge series; the nearest
is the Paraguay at Puerto Bermejo, 203 km downstream, which lags by months.
License: none stated.


**BoM Water Data Online (Swan Hill, Euston, Bourke; Albury via Doctors
Point).**

*Discharge.* Same KiWIS service, parameter "Water Course Discharge," series
`DMQaQc.Merged.DailyMean.24HR`, m³/s. Swan Hill from 1974, Euston from 1975,
Bourke mostly from 1972. Albury's own discharge record stops in 1952; the plan is
Doctors Point (409017), 4 km downstream, from 1929. Quality codes: A (best
available), B (compromised), C (estimate), E (unknown). More than half of
Doctors Point's days are E. The Murray is regulated by Hume Dam and weirs,
so flows reflect releases. CC BY 4.0, credit Bureau of Meteorology and the
station owner.


**MRC (Chiang Saen, Pakse, Kratie; Vientiane to 2006).**

*Discharge.* Same time-series API, parameter "Discharge" ("Calculated daily
discharge"), m³/s: Chiang Saen from 1960, Pakse from 1923, Kratie from 1924.
Vientiane's series ends in 2006; Nong Khai, 13 km downstream, runs to 2026.
All series carry approval level "Working," not final. Kratie repeats each
daily value hourly; we keep one per day. Limits: none documented by MRC in the series
metadata; Kratie and Pakse carry notes we have not read. Upstream dams
change dry-season flows (dates to be sourced). MRC Non-commercial
Data Use Licence, not open. Not shown on the page from October 19, 2026,
because the license requires MRC's written permission to republish.

## As built (October 17, 2026)

Flow was downloaded October 17, 2026, two days after the level cache, so
flow can run two days past the level at the same gauge. Fetch scripts:
`scripts/fetch/flow_*.py`; contract and station choices:
`scripts/fetch/FLOW.md`. Each flow file's JSON keeps every bookkeeping note
(counts by publisher code, rows dropped); the page shows only the
plain-language notes. Shares below are of the days with a value.

| Gauge | Flow station | Kind | Record | Days | Measured / provisional / estimated | Unit |
|---|---|---|---|---|---|---|
| amazon-manacapuru | Manacapuru (same station) | river flow | 1972-01-02 to 2026-04-30 | 19,731 | 95% / 4% / 1% | m3/s |
| amazon-obidos | Óbidos (same station) | river flow | 1968-01-01 to 2026-02-28 | 20,858 | 96% / 4% / 1% | m3/s |
| amazon-tabatinga | Tabatinga (same station) | river flow | 1995-01-01 to 2026-05-31 | 11,452 | 89% / 8% / 3% | m3/s |
| colorado-lake-mead | Lake Mead Hoover Dam and Powerplant Daily Lake/Reservoir Release - Total-cfs Time Series Data (same station) | dam release | 1934-04-01 to 2026-10-16 | 33,802 | 99% / 1% / 0% | cfs |
| colorado-lake-powell | Lake Powell Glen Canyon Dam and Powerplant Daily Lake/Reservoir Release - Total-cfs Time Series Data (same station) | dam release | 1963-03-14 to 2026-10-16 | 23,228 | 98% / 2% / 0% | cfs |
| danube-hofkirchen | Hofkirchen (same station) | river flow | 1900-11-01 to 2026-10-16 | 46,006 | 99% / 1% / 0% | m3/s |
| danube-kienstock | Kienstock (same station) | river flow | 1978-01-01 to 2023-12-31 | 16,801 | 86% / 0% / 14% | m3/s |
| danube-pfelling | Pfelling (same station) | river flow | 1925-11-01 to 2026-10-16 | 36,874 | 99% / 1% / 0% | m3/s |
| darling-bourke | DARLING@BOURKE TOWN (same station) | river flow | 1895-02-02 to 2026-10-16 | 19,967 | 98% / 1% / 1% | m3/s |
| fraser-hope | FRASER RIVER AT HOPE (same station) | river flow | 1912-03-01 to 2026-10-16 | 41,839 | 95% / 1% / 4% | m3/s |
| fraser-mission | FRASER RIVER AT HOPE (Hope, 68 km upstream) | river flow | 1912-03-01 to 2026-10-16 | 41,839 | 95% / 1% / 4% | m3/s |
| fraser-shelley | FRASER RIVER AT SHELLEY (same station) | river flow | 1950-05-01 to 2026-10-16 | 27,922 | 59% / 1% / 40% | m3/s |
| lena-kyusyur | Lena at Kyusyur (same station) | river flow | 1936-01-01 to 2026-01-17 | 32,701 | 91% / 9% / 0% | m3/s |
| mekong-chiangsaen | Chiang Saen (same station) | river flow | 1960-01-01 to 2026-10-16 | 24,395 | 100% / 0% / 0% | m3/s |
| mekong-kratie | Kratie (same station) | river flow | 1924-01-01 to 2026-10-16 | 37,339 | 93% / 0% / 7% | m3/s |
| mekong-pakse | Pakse (same station) | river flow | 1923-01-01 to 2026-10-16 | 37,878 | 100% / 0% / 0% | m3/s |
| mekong-vientiane | Nong Khai (Nong Khai, 13 km downstream) | river flow | 1969-01-01 to 2026-10-16 | 21,105 | 100% / 0% / 0% | m3/s |
| mississippi-helena | MISSISSIPPI RIVER AT HELENA, AR (same station) | river flow | 1928-01-01 to 1977-09-29 | 18,170 | 100% / 0% / 0% | cfs |
| mississippi-memphis | MISSISSIPPI RIVER AT MEMPHIS, TN (same station) | river flow | 1933-01-01 to 2026-10-16 | 26,951 | 100% / 0% / 0% | cfs |
| mississippi-stlouis | Mississippi River at St. Louis, MO (same station) | river flow | 1861-01-01 to 2026-10-16 | 60,186 | 100% / 0% / 0% | cfs |
| mississippi-vicksburg | Mississippi River @ Vicksburg, MS (same station) | river flow | 1901-01-02 to 2026-10-16 | 45,939 | 100% / 0% / 0% | cfs |
| missouri-bismarck | MISSOURI RIVER AT BISMARCK, ND (same station) | river flow | 1927-10-01 to 2026-10-16 | 36,024 | 89% / 1% / 11% | cfs |
| missouri-hermann | Missouri River at Hermann, MO (same station) | river flow | 1928-10-01 to 2026-10-16 | 35,806 | 98% / 0% / 2% | cfs |
| murray-albury | MURRAY @ DOCTORS PNT (Doctors Point, 4 km downstream) | river flow | 1929-11-02 to 2026-10-16 | 32,662 | 77% / 21% / 2% | m3/s |
| murray-euston | MURRAY @ EUSTON (same station) | river flow | 1975-08-29 to 2026-10-16 | 18,675 | 93% / 1% / 5% | m3/s |
| murray-swanhill | MURRAY @ SWAN HILL (same station) | river flow | 1974-11-14 to 2026-10-16 | 18,965 | 94% / 2% / 4% | m3/s |
| ob-salekhard | Ob at Salekhard (same station) | river flow | 1936-01-01 to 2025-12-10 | 32,792 | 77% / 23% / 0% | m3/s |
| ohio-cairo | OHIO RIVER AT OLMSTED, IL (Olmsted, about 17 river miles upstream) | river flow | 2013-03-01 to 2026-10-16 | 4,965 | 62% / 15% / 24% | cfs |
| ohio-cincinnati | OHIO RIVER AT MARKLAND DAM NEAR WARSAW, KY (Markland Dam, about 61 river miles downstream) | river flow | 1970-05-01 to 2026-10-16 | 20,618 | 97% / 2% / 2% | cfs |
| ohio-louisville | OHIO RIVER AT LOUISVILLE, KY (same station) | river flow | 1928-01-01 to 2026-10-16 | 36,063 | 95% / 1% / 3% | cfs |
| parana-corrientes | Corrientes (same station) | river flow | 1904-01-01 to 2026-10-16 | 43,684 | 100% / 0% / 0% | m3/s |
| parana-parana | Paraná (same station) | river flow | 2015-07-21 to 2026-10-16 | 2,926 | 100% / 0% / 0% | m3/s |
| parana-posadas | Posadas (same station) | river flow | 1970-01-01 to 2017-09-08 | 17,342 | 100% / 0% / 0% | m3/s |
| parana-rosario | Rosario (same station) | river flow | 2015-07-21 to 2026-10-16 | 2,941 | 100% / 0% / 0% | m3/s |
| rhine-lobith | Lobith (Bovenrijn, Tolkamer) (same station) | river flow | 1901-01-01 to 2026-10-16 | 45,942 | 14% / 86% / 0% | m3/s |
| seine-paris | La Seine à Paris - Austerlitz (same station) | river flow | 1900-01-02 to 2026-03-16 | 39,992 | 99% / 1% / 0% | L/s |
| yenisei-igarka | Yenisey at Igarka (same station) | river flow | 1936-01-01 to 2026-01-31 | 30,402 | 76% / 24% / 0% | m3/s |

**On the page.** Each gauge with flow shows a dial (lowest to highest daily
value on record) that moves with the playback date, and a separate daily
flow chart with its own axis, 12-month average (same 300-of-365 rule) and
completeness strip. Flow and level are never on one axis. Flow-only gauges
(Ob, Yenisei, Lena) are hollow green rings on green rivers. Where the flow
station is not the level gauge, the title names it and its distance. Bourke's
flow chart starts January 1, 1972, like its level chart.

**Findings from the fetch (not all are in the per-publisher text above).**
- USGS: Memphis has no flow from September 30, 1994 to September 30, 2014.
  St. Louis has none from October 1861 to September 1862, Bismarck none in
  its first winter (November 1927 to March 1928). Bismarck is about 11%
  estimated overall but 26% to 30% per decade since the 1990s (ice). Olmsted
  (Cairo) is 24% estimated. Markland's 289 "A:R" days (approved, revised)
  are measured. No numeric ice code appeared; ice days arrive as "e".
- CWMS Vicksburg flow now runs to October 16, 2026. On that day it read
  457,525 cfs against USGS 07289000's provisional 476,000 cfs (3.9% lower);
  the full overlap from 2008 was not compared.
- RISE: release is downloaded a decade at a time (full requests time out).
  Lake Mead's release record starts April 1, 1934, before the lake stored
  water. One zero-release day is kept.
- ECCC: about 40% of Shelley's days in each decade from the 1950s to the
  2010s carry the ice symbol (27% in the 2020s so far). Hope has no data
  from February 25 to March 17, 2025, between HYDAT and real-time.
- Rijkswaterstaat Lobith: one reading a day 1901 to 1988, RWS's own 24-hour
  mean for most of 1989 to 2003, hourly from late 1996, 10-minute from 2013;
  the rating label changes in 2003 and 2017. From November 27, 2025 one
  10-minute series marked checked reads about 20% of the live series (276
  against 1,325 m3/s at 795 cm), so series are chosen by rating, newest
  first, never by status. Every day before May 1, 2003 is unchecked, so 86%
  of the series is provisional. In the cold winters of 1917, 1929, 1940,
  1947, 1954 and 1963 flow departs from the usual level-flow relation;
  ice is a guess, not sourced, and is not on the page. Readings coded 99
  ("gap") are dropped even when they carry a value (decided October 19,
  2026). After that, September 29 and 30, 2026 have fewer than 90% of their
  usual readings and are left out, so the record low is 553 m3/s on October
  1, 2026 (provisional).
- Hub'Eau Paris: F700000102 has near-complete flow only through 2005; after
  that flow moved to F700000103, which is not joined, so 2006 on is sparse
  (20% to 65% of days per decade). Last value March 16, 2026; 752 empty rows
  from 2024 to 2026 dropped. 25,285 days are qualified "doubtful" (70% to
  85% per decade before 1990); they keep their status label.
- eHYD Kienstock: no gap (the research note's "one gap" is the end marker).
  74 whole months from 1996 to 2016, plus October 2023 (75 in all), are estimated, because
  station footnotes say flow was computed from filled-in levels. A choice:
  the footnotes name months, not days. The 10 months whose footnote says
  flow was affected by ice (January and December 1997, eight months of
  2005) are estimated too, matching USGS and ECCC ice days (decided October
  19, 2026): 2,597 estimated days in all.
- BoM: Doctors Point (Albury's flow) is code E on 100% of 2010s days and 87%
  of 2020s days, so the "E from 1991 is provisional" rule makes 6,854 days
  provisional. The rule was built on Albury's level, where E returns only on
  scattered recent days; at Doctors Point it may mean something else. Open
  question for BoM. Bourke's flow has 1895, then nothing until about 1972.
- ANA: no flow month exists at both consistency levels. Some days have a
  value but a blank or 0 status (Tabatinga 60, Manacapuru 400, Obidos 184,
  mostly raw 2024 to 2026); they keep their level's label. The
  `MetodoObtencaoVazoes` code list was not found.
- INA: daily series are labeled "medicion directa"; per-reading series at
  Corrientes and Posadas say "curva de gasto" (rating curve). Corrientes has
  no flow from August 19, 2021 to August 9, 2024; Parana and Rosario are
  mostly empty from mid-2022 to late 2024. INA's metadata counts differ
  slightly from what the observations endpoint returns (Posadas 17,350 vs.
  17,342), unexplained.
- MRC: Kratie's hourly copies of the daily value occur only on October 14
  and 15, 2026 (dropped). From 2008 to 2012 on, the four stations have two
  real readings a day, averaged (`mixed`). 18 readings of exactly 0 m3/s are
  dropped (MRC notes say "a discharge data point was removed" on some of
  those dates). Kratie flow 1940, 1957 and 1975 to 1979 is marked estimated,
  matching the Kratie level rule, because the flow is computed from it.
- ArcticGRO: coordinates from its discharge metadata PDF (Table 1, updated
  February 27, 2023). Yenisei and Lena flow are from the station closest to
  ArcticGRO's sampling site. The blank flag covers the Ob 2000 to 2021 and
  the Yenisei 2006 to 2017 (provisional). The Yenisei's 2,502 missing days
  from 1963 to 1979 are almost all November to May, so winter and yearly
  averages for those years would be skewed. Lena: 2012, 2013 and 2015 are
  all P; 2016 to 2020 P mostly June to October; 2014 and 2021 all A.

**Notes removed for lack of a checked source** (October 17, 2026): dam and
weir regulation at Doctors Point, Swan Hill, Euston and Bourke (had been
attributed to the Murray-Darling Basin Authority without a page checked);
dams on the Ob and Yenisei; Yacyreta at Posadas; "no large tributary"
between Vientiane and Nong Khai; rise-and-fall rating effects on the Amazon.
Each needs a source before it goes back on the page.

## Global Runoff Data Centre, GRDC (BfG, Koblenz): not usable on the page

**What it is.** The main global archive of measured daily and monthly river
flow, supplied by national services. Flow only, no water level.

**License and attribution.** The downloaded values may not be redistributed
"in part or total ... to the general public (incl. distribution via
Internet)," and are "released only for research purposes." "Analysis and
further processing ... as well as the use of statistical data products is
permitted" with credit. The terms say nothing about charts; a chart from
which a reader can read the monthly or yearly values is very likely
redistribution in part. We use GRDC only as a check, unless grdc@bafg.de
agrees in writing. The GRDC-Caravan extension below is the open exception:
a subset that national services allowed GRDC to share under CC BY 4.0.

**Where nothing open exists.** China (no historical downloads; data treated
as confidential), India (Indus and Ganga-Brahmaputra basin data classified),
Pakistan (daily press releases only), the Niger Basin Authority (no public
access policy found), SIEREM (refers requests to national services) and
Russia's water cadastre (moved into a closed government system). For those
rivers the open options are old monthly records in SAGE/RivDIS, modeled
flow, or satellite level.

## Global River Discharge Database (SAGE, UW-Madison), mostly RivDIS v1.1

**What it is.** Monthly mean river flow in cubic meters per second at about
3,100 listed stations. Each file has one row per year with 12 monthly means
and an annual mean. Our target stations all come from RivDIS (Vorosmarty,
Fekete and Tucker), which was typed in from UNESCO's published yearbooks of
national flow records. This is flow, not water level.

**Where it comes from.** One tab-delimited text file per station, no login:
`https://sage.nelson.wisc.edu/riverdata/station_table_formated.php?pointid=<PointID>`.
Station list: `keysearch.php?numfiles=50&startnum=<N>` (75 pages). Station
reliability flags: RivDIS `STATION.DAT` at ORNL DAAC (open). Files are a few
kilobytes each.

**Version and vintage.** The site is the 1999 CPEP data set (Coe and
Olejniczak), built on "RivDis2.0," USGS and Brazil's DNAEE (now ANEEL).
RivDIS v1.1 was released in 1998 (doi:10.3334/ORNLDAAC/199). No update date,
no version on the site, no sign of upkeep. Values are frozen.

**Coverage.** Station records run from 3 to 116 years. Median end year 1984;
nearly every record ends before 2000. Our gauges: Kinshasa 1903 to 1983,
Brazzaville 1984 to 2002, Koulikoro 1907 to 1990, Niamey 1929 to 1991, Aswan
1869 to 1984, Dongola 1912 to 1984, Volgograd 1879 to 1984, Komsomolsk 1933
to 1984, Farakka 1949 to 1973, Keban 1937 to 1972. RivDIS does not say which
months were estimated by the national services. River flow is not measured
directly most days: it is computed from water level through a rating curve
that is checked now and then by field measurement.

**Changes over time.** Dams change what the numbers mean: Aswan after the
High Dam (1964 to 1970), Volgograd after 1958, Keban after 1974. The Aswan
series after 1964 is controlled release, not natural flow.

**Suppressed, censored or masked values.** None known.

**Missing data.** -9999 marks a missing month. A year with any missing month
has a -9999 annual mean. Missing years have no row.

**Revisions.** None; the archive is frozen. ArcticGRO's newer Roshydromet
data differ from SAGE by more than 5% in a few months (Yenisei June 1983 is
10,700 in SAGE and 106,873 in ArcticGRO), which points to typing errors
rather than revisions.

**Units and rounding.** m3/s, three or four significant figures, as typed
from the yearbooks. The annual mean is SAGE's own average of the 12 months.

**Known quirks.**
- Kinshasa April 1903 reads 3,280 between 32,410 and 34,970: a dropped digit.
- Khartoum (Blue Nile) is labeled 1976 to 2046. The years are wrong. Do not use.
- RivDIS flags Staritsa (Volga) and Paksay (Ganges) "Bogus Discharge," and
  Brazzaville "Second station in the same cell."
- PointIDs are not unique across sources: 75 PointIDs belong to two stations
  (one RivDIS, one ANEEL). Always check the station name in the file header.
- The site says 3,681 stations; the index lists 3,125 entries.
- Some RivDIS entries have a blank Source field (Komsomolsk on the Amur).

**Uncertainty.** RivDIS gives no error bars; its guide cites 5% to 10% as
typical for river gauging, "but the actual accuracy depends significantly on
local conditions." Early records, ice periods and floods are less certain.

**License and attribution.** No license on SAGE. CPEP: "The data are freely
available." NASA's RivDIS record points to NASA's open data policy. The
values came from UNESCO's open publication, not from a GRDC download, so
GRDC's no-redistribution terms do not apply to them in our reading. Credit:
"Vorosmarty, C.J., B.M. Fekete and B.A. Tucker (1998), Global River
Discharge, 1807-1991, V1.1 (RivDIS), ORNL DAAC; via the SAGE Global River
Discharge Database, University of Wisconsin-Madison." Ask SAGE for written
confirmation before launch.

## Discharge Dataset (Arctic Great Rivers Observatory, ArcticGRO)

**What it is.** Daily mean river flow in m3/s for the Ob at Salekhard, the
Yenisei at Igarka and the Lena at Kyusyur, measured by Roshydromet, Russia's
weather and water service. Each row is one day with a flag.

**Where it comes from.** https://arcticgreatrivers.org/discharge/ . The
xlsx files are embedded in the page as base64 (the page is about 32 MB);
we decode them. File names carry the version, for example
`Ob_Salekhard_Version_20260810.xlsx` (about 850 KB). No login.

**Version and vintage.** Version 20260810. Each update gets a new date code
and the old one is archived. Updates replace provisional values with
certified ones.

**Coverage.** 1936 to December 2025 (Ob) or January 2026 (Yenisei, Lena).
Certified ("A") values: Ob to 2008, Yenisei to 2005, Lena to 2021. Later
values are blank-flagged or provisional ("P"). Russian provisional values
are estimated by the Arctic and Antarctic Research Institute from water
level, ice thickness and past rating curves; winter values are redone after
the ice breaks up.

**Changes over time.** Dams upstream (Novosibirsk on the Ob; Krasnoyarsk and
others on the Yenisei and Angara) change the seasonal pattern from the 1950s
on.

**Suppressed, censored or masked values.** None.

**Missing data.** Rows with "NA" for value and flag: Ob 60 days (2000),
Yenisei 2,502 days (mostly 1963 to 1979), Lena 43 days (1962). Lena also has
146 rows with no value in late 2024 to 2025.

**Revisions.** Yes: provisional and blank-flagged values get replaced. Pin
the version code and refresh in full.

**Units and rounding.** m3/s, three significant figures as published.

**Known quirks.** The blank flag is not explained in the metadata; we treat
it as provisional. Lena has both A and P values in 2012 to 2021.

**Uncertainty.** None published. Winter flow under ice is the least certain.

**License and attribution.** "ArcticGRO data are free to use by anyone for
any purpose. We only ask that you credit ArcticGRO." Credit: "The Arctic
Great Rivers Observatory. 2026. Discharge Dataset, Version 20260810. Data
from Roshydromet."

## GRDC-Caravan extension (Farber et al. 2025, GRDC)

**What it is.** Daily river flow for 5,356 gauges in 25 countries whose
national services let GRDC share data openly. We use the Orange at
Vioolsdrif (South Africa) and the upper Zambezi at Katima Mulilo (Namibia).
Measured by the national services.

**Where it comes from.** Zenodo record 15349031 (version 0.6, May 6, 2025),
`GRDC_Caravan_extension_csv.zip` (8.8 GB). Single files can be pulled from
the zip with HTTP range requests. No login.

**Version and vintage.** v0.6. Fixed release.

**Coverage.** 1950 to 2023 (Caravan cuts every record at 1950). Vioolsdrif
1950-01-02 to 2023-05-19, 52 complete years. Katima Mulilo to 2021-06-21, 58
complete years.

**Changes over time.** The Orange is heavily dammed (Gariep 1971, Vanderkloof
1977) and partly diverted.

**Suppressed, censored or masked values.** Rounding acts like masking at low
flow (next item).

**Missing data.** Empty streamflow cells. Not filled.

**Revisions.** None within a version.

**Units and rounding.** Flow is stored as mm per day over the basin area,
rounded to 0.01 mm/day. Convert with area (km2) x mm/day / 86.4 = m3/s. At
Vioolsdrif one step is about 91 m3/s, and 11,684 days read exactly zero
(below about 45 m3/s). Use monthly means and say so. At Katima Mulilo one
step is about 39 m3/s.

**Known quirks.** The area used is Caravan's delineated basin (786,037 km2 at
Vioolsdrif), not the official one.

**Uncertainty.** None published.

**License and attribution.** CC BY 4.0. Credit "GRDC-Caravan (Farber et al.,
2025), data from the Department of Water and Sanitation, South Africa, and
the Ministry of Agriculture, Water and Land Reform, Namibia, via the Global
Runoff Data Centre."

## GEOGLOWS retrospective simulation v2 (ECMWF / GEOGLOWS)

**What it is.** Modeled daily mean flow, m3/s, for about 7 million river
reaches, from ERA5 weather reanalysis run through a routing model. Not a
measurement.

**Where it comes from.** REST API, no key:
`https://geoglows.ecmwf.int/api/v2/retrospectivedaily/<river_id>?format=csv`
(about 1 MB per reach). `getriverid?lat=&lon=` returns the nearest reach,
which is often a side channel; pick the reach with the largest mean.

**Version and vintage.** Model version 2. The record is extended as new
ERA5 data arrive; it ran to September 30, 2026 today.

**Coverage.** January 1, 1940 to about two weeks ago. Every value is model
output.

**Changes over time.** The weather input (ERA5) uses fewer observations
before about 1979, so early decades are less constrained.

**Suppressed, censored or masked values.** None.

**Missing data.** None.

**Revisions.** A new model version replaces all values.

**Units and rounding.** m3/s, published to three significant figures.

**Known quirks.** The nearest reach to a gauge is often a side channel (15
m3/s at Kinshasa). The service went down twice under our requests; space
requests out. The model does not reproduce how dams and irrigation are run.

**Uncertainty.** Large at our gauges: from 26% below to 703% above the
measured average. Show only as change relative to the model's own average,
labeled modeled, and never on the same axis as measured flow.

Model average compared with the measured average at the same place (rough
check; the periods differ, and some measured records are short):

| Gauge | Model vs. measured average |
|---|---|
| Nile at Dongola | 703% higher |
| Zambezi at Katima Mulilo | 228% higher |
| Niger at Niamey | 216% higher |
| Indus at Kotri | 158% higher |
| Orange at Vioolsdrif | 104% higher |
| Congo at Kinshasa | 58% higher |
| Yangtze at Datong | 48% higher (4 measured years) |
| Ganges at Farakka | 35% higher |
| Amur at Komsomolsk | 15% higher |
| Volga at Volgograd | 6% lower |
| Ob at Salekhard | 8% lower |
| Lena at Kyusyur | 12% lower |
| Tigris at Baghdad | 23% lower (5 measured years) |
| Yenisei at Igarka | 26% lower |

**License and attribution.** CC BY 4.0. Credit "GEOGLOWS ECMWF Streamflow
Service, retrospective simulation v2."

## DAHITI satellite river levels (DGFI-TUM, Technical University of Munich)

**What it is.** Water surface height at "virtual stations," the points where a
satellite's path crosses a river. Each row is one satellite pass: a date, a
height in meters above a model of sea level, and the publisher's error
estimate for that pass. It is a height above a sea-level model, not a gauge
reading and not a depth.

**Where it comes from.** https://dahiti.dgfi.tum.de . Data through the DAHITI
API version 2 (`https://dahiti.dgfi.tum.de/api/v2/download-water-level/`) in
JSON, CSV, ASCII or NetCDF. Needs a free account and an API key; without a key
the API returns HTTP 403. Station lists and station info pages are public.
Each series is small (100 to 700 rows).

**Version and vintage.** Each file names a software version; our stations are
on version 8.0. The publisher describes version 6.0 on its product page and
does not publish a change log. Most stations update within weeks of each pass;
our stations end between late August and early October 2026. We pin the
download date and keep the raw files.

**Coverage.** 2002 to 2026 at best, 2008 to 2026 on most of our rivers, 2016
to 2026 on the Orange and Yenisei. A few stations reach back to 1995. Every
value is a measurement from one satellite pass; the publisher does not fill
gaps. Several passes or missions can be blended into one series with a Kalman
filter, which weights each measurement by its error. One value every 10 days
on Jason-series tracks (2002 or 2008 on), every 27 days on Sentinel-3 (2016
on), every 35 days on Envisat, ERS-2 and SARAL (1995 to 2016).

**Changes over time.** The satellite changes over time. On the main 10-day
track, Jason-1 (2002 to 2009) was followed by Jason-2 (2008), Jason-3 and
Sentinel-6A. Envisat records break in October 2010 when its orbit changed, and
SARAL records on the same track end in 2016. Some stations jump from one
mission to another with a gap of years and a shift in where the track crosses
the river. The publisher corrects for known differences between missions, but
small offsets can remain at each change.

**Suppressed, censored or masked values.** Passes judged bad are removed, not
flagged. Removal uses height limits, echo strength (also used to drop ice), and
a test for points that do not fit a flat water surface. Limits are set by hand
for each station. Nothing is top-coded or rounded beyond millimeters.

**Missing data.** Gaps are simply absent rows. Short gaps are passes that were
removed. Long gaps, up to several years, come from mission changes. A listed
start date can be a stray early point: Brahmaputra 318 is listed from 1995 but
starts for real in 2008.

**Revisions.** Whole series are reprocessed when the software changes. We
refresh the whole series and record the download date and software version.

**Units and rounding.** Meters, to the millimeter (API JSON carries more
digits). Real accuracy on rivers is about 10 cm to 1 m, so the published
precision is far finer than the real accuracy.

**Known quirks.** The height is above a sea-level model (EIGEN-6C4 in version
6.0; version 8.0 not stated). It differs from any gauge zero by an unknown
fixed amount, and from the next station upstream by the river's slope, so only
the rise and fall at one station is meaningful. Station names repeat ("Niger,
River" is 167 stations); use the ID. Spellings vary (Zambesi, Zambezi,
Zambeze). Winter values on Siberian rivers may be affected by ice.

**Uncertainty.** The publisher says accuracy ranges from a few centimeters on
large lakes to a few decimeters on small rivers. Its method paper found errors
of 8 to 114 cm on Amazon rivers compared with gauges. The per-pass error in the
files is much smaller (often under 3 cm, sometimes 0) and should not be shown
as an error bar on its own.

**License and attribution.** CC BY-NC 4.0 (Attribution-NonCommercial; the
registration page's text says "Attribution 4.0" but links to the NonCommercial
license). The terms of use allow free use only by private persons, schools and
universities, and nonprofits, and forbid commercial use. Confirm in writing
with DGFI-TUM (christian.schwatke@tum.de) before publishing. Credit: "DAHITI,
DGFI-TUM," and cite Schwatke et al. (2015), Hydrology and Earth System Sciences
19, 4345-4364, doi:10.5194/hess-19-4345-2015.
