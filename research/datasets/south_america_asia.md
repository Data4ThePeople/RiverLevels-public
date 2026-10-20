# Datasets: South America, Australia and the Mekong

Five publishers supply these gauges: Brazil's water agency (ANA), Argentina's
National Water Institute (INA), Paraguay's weather and hydrology office
(DMH-DINAC), Australia's Bureau of Meteorology (BoM) and the Mekong River
Commission (MRC). Fetch scripts: `scripts/fetch/ana.py`, `ina.py`, `dmh.py`,
`bom.py`, `mrc.py` (shared helpers in `sa_asia_common.py`, sourced gauge
histories and reader notes in `sa_asia_history.json`). Each processed gauge
JSON in `data/processed/` carries its own notes, `measurement_history` and
`public_notes`.

Checked October 15, 2026.

## HidroWeb stage series and telemetry (ANA, Brazil)

**What it is.** Daily river stage (water height above a local staff gauge
zero, in cm) for Amazon/Solimoes at Tabatinga, Manacapuru and Obidos, Rio
Negro at Manaus, and the Paraguay River at Ladario. Each row in our file is
one day.

**Where it comes from.** ANA's SOAP web service
`https://telemetriaws1.ana.gov.br/ServiceANA.asmx`, no login, XML.
`HidroSerieHistorica?codEstacao=<code>&tipoDados=1` returns the whole stage
history in one call (2 to 11 MB). Each row is one month with columns
`Cota01..Cota31` and a status per day (`Cota01Status..`). Months can appear
up to three times per consistency level: one row of daily means
(`MediaDiaria=1`, time 00:00) and one row per reading hour (07:00 and 17:00).
`DadosHidrometeorologicos` returns telemetry (mostly 15-minute readings) for a
date range; we ask one calendar year at a time (about 5 to 8 seconds each).
`HidroInventario` gives coordinates and station periods.

**Version and vintage.** No version number. Each month carries a consistency
level: 1 = raw ("bruto"), 2 = consistent, meaning reviewed by ANA
("consistido"). On October 15, 2026, level 2 ran to December 2023 for
Tabatinga, Manacapuru, Obidos and Ladario, and to December 2014 for Manaus,
whose historic file stops there. Level 1 runs to early or mid 2026. When ANA
reviews a period, level 2 values appear next to the level 1 values; we refresh
the whole series each time.

**Coverage.** Manaus 1902, Ladario 1900, Manacapuru 1972, Obidos 1968,
Tabatinga 1982, all to October 2026. Almost every day has a value
(`coverage_by_decade`). Obidos has no data for 1969. Our rule: level 2 value
if it exists for that day, else level 1 (marked `provisional`). After the
historic file ends we add the telemetry daily mean (`provisional`). ANA flags
individual days as estimated with status 2; we mark those `estimated`. The
share is small except Manacapuru in the 1990s (13%) and Tabatinga in the
2000s (7%). ANA's guidance on consistency says doubtful values are marked and
filled values are marked, and that daily means should preferably come from 24
hourly readings; for these staff gauges the daily value is the mean of the
07:00 and 17:00 readings. ANA does not say how it fills an estimated day.

**Changes over time.** Manaus switches from the reviewed staff gauge series to
telemetry on January 1, 2015 (the staff series ends December 30, 2014; December
31 has a single telemetry reading and is dropped as a partial day). On 2,274 days in 2005 to 2014 that have both,
telemetry minus staff gauge has a median of 0 cm, and every year's median is
between -1.2 and 0 cm, so the join is continuous. Telemetry at the other four
gauges agrees with the raw staff series to within 1 cm on a typical day. At
Obidos, an older 1927 to 1948 gauge used a different zero (likely 77 cm
higher); our file starts with the current gauge in 1968.

**Suppressed, censored or masked values.** None. Negative values are real
readings below the gauge zero (Tabatinga, Obidos, Ladario).

**Missing data.** Missing days are blank in the monthly rows. No fill values
(such as 99999) were found. Per-day status codes: 0 blank, 1 real, 2
estimated, 3 doubtful, 4 dry staff gauge. This legend comes from HidroWeb
export headers as quoted by third-party tools, not from an ANA page we could
read. Codes 3 and 4 appear on up to a few dozen raw days per gauge (235 doubtful days at Ladario); we keep those values as
published.

**Revisions.** Level 1 values are replaced by level 2 values after review,
usually a year or more later. Telemetry can be revised after field visits that
re-level the gauges (SGB bulletin, 2017).

**Units and rounding.** Whole centimeters in the historic series. Telemetry
daily means are rounded to 0.1 cm.

**Known quirks.** The XML schema root is named `http://MRCS/`. Duplicate month
rows (daily-mean row plus per-hour rows) must be collapsed, or every day
appears two or three times. Tabatinga has several one-day jumps of 3 to 4 m
in 1989 to 1992 (for example 990 cm for three days in July 1992) that look
like transcription errors; kept as published. The Manaus gauge zero is a
local reference; SGB says to subtract 7.00 m to refer a reading to sea level.

**Uncertainty.** ANA publishes no error bars.

**License and attribution.** No license on the service itself. The SNIRH
metadata record for the national network allows reproduction of the data
provided the source is cited
(https://metadados.snirh.gov.br/geonetwork/srv/api/records/f85dbf06-a869-414c-afc5-bb01869e9156).
Credit: "Agencia Nacional de Aguas e Saneamento Basico (ANA), HidroWeb."

## Alert system a5 API, Prefectura gauges (INA, Argentina)

**What it is.** Daily stage of the Parana River in meters above each gauge's
zero at Posadas, Corrientes, Parana and Rosario. The staff gauges belong to
the Prefectura Naval Argentina (coast guard); INA hosts the series.

**Where it comes from.** `https://alerta.ina.gob.ar/a5/obs/puntual/series/<id>/observaciones?timestart=...&timeend=...`,
JSON, no token. Series metadata, coordinates and gauge zero from
`/a5/obs/puntual/series?estacion_id=<id>&var_id=2`. We request 20-year
chunks; a full gauge takes about 15 seconds. Each chunk asks for one extra
day, because the API keeps a value only if its own end time falls inside the
request, so a daily value for December 31 (ending January 1 at 03:00 UTC)
was lost at chunk boundaries until October 20, 2026 (flow at Corrientes,
Parana and Rosario was missing December 31, 2019); repeats are dropped by id.
Each reading is assigned to its local calendar date in Argentina, using the
time zone America/Argentina/Buenos_Aires with its historical daylight saving
rules; a fixed UTC-3 would move some days in 1974, 1988 to 1993 and 2007 to
2009.

**Version and vintage.** No version. Values update daily; the last value on
October 15, 2026 was October 14.

**Coverage.** Rosario 1884, Posadas and Corrientes 1901, Parana 1902, all to
October 2026. Most decades have a value on 98% to 100% of days; Parana's
first decade has 90%. INA publishes no flag for filled or estimated values,
so everything is marked `measured`.

**Changes over time.** Before 2014 to 2016 there is one value a day. After
that some days have two to eight readings (Rosario 1,285 days, Corrientes
1,793); we average them and round the mean to 0.01 m, the precision INA
publishes, so `daily_stat` is "mixed". A mean that ends in exactly 5 mm
(such as 5.255 m) can round either way, because computers do not store such
decimals exactly; the difference is never more than 0.01 m. Timestamps are 07:00
local through the 1970s, 06:00 in the 1980s, 04:00 in the 2000s and 00:00
in the 2020s. The uniform early hour looks like a loading convention, not a
documented reading hour. Yacyreta dam, downstream of Posadas, has held a
reservoir there since 1994, raised in steps to 83 m by February 2011, so
Posadas levels before and after are not comparable.

**Suppressed, censored or masked values.** None found.

**Missing data.** Missing days have no row. No fill values found.

**Revisions.** INA can overwrite values (each observation has a
`timeupdate`); we refresh the full series.

**Units and rounding.** Meters to two decimals (1 cm). Daily means of
several readings are rounded back to two decimals (changed October 17,
2026; before that they were stored to 0.001 m, finer than the gauge is
read).

**Known quirks.** Gauge zeros are tied to different national reference systems
(IGN, IGM, MOP). INA's 2024 report says Corrientes' zero is uncertain (41.95,
42.01 or 42.39 m depending on the document). Posadas has no published zero.
Rosario's early record was affected by a gradually sinking gauge; Antico et
al. (2020) corrected it, and it is not stated whether INA's copy includes the
correction. INA does have a station for Asuncion (station 157, DMH-DINAC
network), but its series is not public, so Asuncion comes from DMH. INA's
nearest public long Paraguay River series is Puerto Pilcomayo (series 55,
1910 on), across the river from Asuncion; we did not use it.

**Uncertainty.** Not published.

**License and attribution.** No license, terms of use or citation statement
found on the a5 site or its README. Credit "Instituto Nacional del Agua (INA)
and Prefectura Naval Argentina." Clear reuse terms before publishing.

## Nivel del rio, Asuncion web table (DMH-DINAC, Paraguay)

**What it is.** One daily level ("nivel del dia") for the Paraguay River at
Asuncion, in meters above the gauge zero.

**Where it comes from.** HTML page
`https://www.meteorologia.gov.py/nivel-rio/vermas_convencional.php?code=2000086218&page=N`,
15 days per page, newest first, roughly 3,000 pages back to 1904. No API or
download. The page's date-range form is commented out and the `desde`/`hasta`
parameters return no rows. We cache every page in `data/raw/dmh/` and the
script resumes where it stopped.

**Version and vintage.** No version. Page boundaries shift by one row each day
as new values are added at the top; the script drops identical repeats and
fails on a date with two different values.

**Coverage.** January 1, 1904 to October 15, 2026: 2,988 pages with data at the
October 15 download (pages shift by one row a day, so the count grows), 44,815 days. Every decade has a value on more than 99% of days. No
quality flags; every value is `measured`.

**Changes over time.** Not documented.

**Suppressed, censored or masked values.** None. Values below zero are real
(for example -1.02 m in September 2024).

**Missing data.** Not documented; gaps show up as missing dates.

**Revisions.** Unknown.

**Units and rounding.** Meters to two decimals, printed with an "m" suffix.

**Known quirks.** With curl each page past page 1 took about 77 seconds to
answer; with a Python requests session (keeping the cookie from page 1) each
took about 1 second, so the full scrape took about 90 minutes over two runs.
`--refresh` re-downloads only page 1; older pages are treated as fixed. Coordinates are not on the page; we use the ones INA lists for the
same DMH station code.

**Uncertainty.** Not published.

**License and attribution.** None stated. Credit "Direccion de Meteorologia
e Hidrologia (DMH-DINAC), Paraguay." Clear reuse terms before publishing.

## Water Data Online, KiWIS API (Bureau of Meteorology, Australia)

**What it is.** Daily mean water course level for the Murray at Albury, Swan
Hill and Euston and the Darling at Bourke, in meters.

**Where it comes from.**
`https://www.bom.gov.au/waterdata/services?service=kisters&type=queryServices&datasource=0&format=json&request=...`.
No login, but BoM rejects requests without a browser-like User-Agent.
`getTimeseriesList` finds the series `DMQaQc.Merged.DailyMean.24HR` for
parameter "Water Course Level"; `getTimeseriesValues` with
`returnfields=Timestamp,Value,Quality Code` returns the whole record in one
call (0.3 to 2.3 MB). `getStationList` gives coordinates and the data owner.

**Version and vintage.** No version. "DMQaQc.Merged" is not defined on any
BoM page we found; BoM's Water Data Online info sheet says the published
series combine validated data and provisional raw data, so this is most
likely that combined series. Data owners (WaterNSW for Albury and Bourke;
Victoria's Department of Energy, Environment and Climate Action for Swan Hill
and Euston) can revise history.

**Coverage.** Albury 1885, Swan Hill 1974, Euston 1975, Bourke 1895 (one year)
then 1972, all to October 13, 2026. Quality codes, from `getQualityCodes`
and BoM's WDTF quality code list: 10 = A "best available", 90 = B
"compromised", 110 = C "estimate", 140 = E "unknown", 210 = F "missing or
incorrect". We map A and B to `measured`, C to `estimated`, and drop F.
E is `measured` before 1991 and `provisional` from 1991 on (changed October
17, 2026). Before 1991 E covers the once-daily record. After that it comes
back on recent days that have not been checked: Albury 76 days (2 in 1998,
8 in 2015, 12 in 2017, 54 in 2026), Bourke 190 days (120 from June 16 to
October 13, 2026, one run of 64 days from October 11 to December 13, 1995,
and 6 single days from 2011 to 2022). Swan Hill and Euston have none. Its
share per decade is still reported in each gauge's notes. Estimated (C) values
are 27% of Swan Hill's and 32% of Euston's days in the 1970s, and a few
percent after that. Albury's values are nearly all E before 1990; Bourke's
are E from 1972 to 1988. BoM's reference station documentation maps NSW's
"daily, accumulated or spot data" code to E and calls its NSW mappings
"provisional only," so E there likely means a once-daily manual reading
rather than a bad value.

**Changes over time.** Albury has one value a day through 1975 (mostly
09:00), then several a day from 1976, consistent with a recorder. Swan Hill
and Euston start with several readings a day. Bourke has nothing from 1896 to
mid-1972. Dams and weirs: Hume Dam (1936, enlarged 1961) and Dartmouth Dam
(1979) upstream of Albury; Euston Weir (1937) at Euston; Torrumbarry Weir
(1924) upstream of Swan Hill; Bourke weir (1897, rebuilt 1941).

**Suppressed, censored or masked values.** None. No F-coded values in these
four series. Timestamps with no value (code -1) are dropped: 28,156 at
Bourke, mostly the 1896 to 1972 gap.

**Missing data.** Missing days appear as a null value with code -1.

**Revisions.** Recent values can be provisional and replaced; we refresh the
full series.

**Units and rounding.** Meters to three decimals. Albury, Swan Hill and
Bourke are local gauge heights. Euston values are water surface elevations
(42 to 52 m), most likely meters above the Australian Height Datum, which BoM
does not state.

**Known quirks.** Station 414203 (Euston) has two station entries about 2.7 km
apart; the daily mean series is on station_id 2877981. Some station lists
return blank coordinates for one of a pair.

**Uncertainty.** Not published beyond the quality codes.

**License and attribution.** Creative Commons Attribution 4.0
(https://www.bom.gov.au/water/about/waterDataOnline/); the Water Data Online
footer still says "Creative Commons Attribution Australia." BoM asks users to
check the data owners' preferences. Credit "Bureau of Meteorology, Water Data
Online; data from WaterNSW / Victorian Department of Energy, Environment and
Climate Action."

## Time-series API (Mekong River Commission)

**Not shown on the page.** Left out from October 19, 2026 because MRC's
license requires written permission to republish (see "Sources that need
permission are left out" in the rules above). The section stays as the
record of what was fetched and how.

**What it is.** Water level in meters above each gauge's zero at Chiang Saen
(Thailand), Vientiane (Laos), Pakse (Laos) and Kratie (Cambodia), from the
"Water Level.Manual" series (staff gauge, read one to six times a day).

**Where it comes from.** Inventory:
`https://timeseries.api.mrcmekong.org/api/v1/ts/inventory/timeSeriesList`
(1.1 MB JSON, coordinates included). Data:
`.../ts/data/timeSeriesCorrectedData/<uniqueId>?sd=...&ed=...`, one call per
series (2 to 4 MB). No login for the API; the MRC portal needs a free account
to download.

**Version and vintage.** AQUARIUS system, approval level "Working" for the
whole record of all four series (not formally approved). Updated daily.

**Coverage.** Vientiane 1923, Kratie 1933, Pakse 1960, Chiang Saen 1960, all
to October 15, 2026. Vientiane is missing 1940 to 1941, 1945 to 1946 and 1953
to 1959. About 7,000 days per gauge have more than one reading; we use the
daily mean. There is no per-point quality flag. The API does carry Grades and
Notes intervals. We mark as `estimated` any interval whose note says the data
were filled, estimated or interpolated, and grade 41 intervals (MRC used
grade 41 for the November 2024 gaps filled from telemetry at Chiang Saen and
Kratie). At Kratie we also mark 1940, 1957 and 1975 to 1979 as estimated: MRC's
2005 data inventory had no Kratie water level for those years, and the API now
has complete values with no explanation. Their day-to-day variability looks
like the years around them, so we cannot tell filled days from real ones.

**Changes over time.** Chiang Saen moved on December 15, 1993; Cochrane et al.
(2014) say a 0.62 m correction is needed to compare later and earlier values.
The API series jumps about +0.45 m overnight on December 16, 1993, in the dry
season, so it appears not corrected. We publish it as is and flag it. Chinese
dams upstream (Manwan filled 1992, Xiaowan 2010, Nuozhadu 2014) changed dry
and wet season levels at Chiang Saen and below.

**Suppressed, censored or masked values.** None.

**Missing data.** Missing days have no point. We drop isolated 0.00 values
that sit more than 1 m from both neighboring days (two at Chiang Saen, one at
Pakse, two at Kratie); these are placeholders, not readings.

**Revisions.** MRC edits history (the Notes record typo fixes and a 2022
replacement of Pakse data with backup manual records). We refresh in full.

**Units and rounding.** Meters. Values come with long float tails (for example
6.576172678319064), likely from a datum conversion; we round to 1 mm. Gauge
zeros from MRC's 2006 flood report: Chiang Saen 357.1 m, Vientiane 158.0 m,
Pakse 86.5 m, Kratie -1.08 m above mean sea level (reference not named there;
JICA gives Ko Lak datum for Vientiane).

**Known quirks.** Grade codes 11, 21 and 31 appear on short intervals whose
notes describe typo fixes or checks against neighbor gauges; MRC does not
publish what the codes mean. Sources disagree on Vientiane's start (1913 in a
2008 flood report, 1923 in the inventory and API).

**Uncertainty.** The API summary says "The accuracy and reliability of this
data is not guaranteed."

**License and attribution.** Not open. MRC's 2005 Non-commercial Data Use
Licence allows non-commercial use only and no redistribution of data or
derived products without written permission
(https://archive.iwlearn.org/mrcmekong.org/download/spatial/nonCommmercialDataUseLicense.pdf).
No current license text was found on the portal. Get MRC permission before
publishing charts built from these values. Credit "Mekong River Commission."
