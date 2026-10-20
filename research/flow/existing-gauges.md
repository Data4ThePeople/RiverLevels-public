# Discharge (flow) next to level: research for all 43 gauges

Checked October 17, 2026. Every "verified" means a real request made that day
returned values (date ranges and sample values below). Nothing in the project
was edited. Distances to proxy stations are straight-line distances between
station coordinates, not river distances, unless marked "river miles".

## How to read this

- **Same gauge**: the discharge series is published for the same station as
  our level series.
- **Proxy**: no open discharge at our gauge; the nearest open daily discharge
  station on the same river is named, with distance and what joins in between.
- **None**: no open daily discharge found at or near the gauge.

Almost every series here is computed, not measured directly. Field crews
measure flow a few times a year (current meter, and since the 1990s acoustic
Doppler, ADCP). Those measurements fit a stage-discharge relation (rating
curve). The daily value is then the day's levels run through the rating.
Exceptions are noted: index-velocity gauges (USGS Cincinnati, Olmsted),
and reservoir inflow, which Reclamation computes from a water budget.

## Summary table

| Gauge | Discharge source and series | Same gauge or proxy | Years | Daily | Verified | License |
|---|---|---|---|---|---|---|
| rhine-maxau | PEGELONLINE `23700200/Q` (15-min, last 31 days); BfG yearbook PDFs (daily tables 1998 to 2025) | same | 31 days by API; yearbook PDFs | 15-min / PDF | yes (API and PDF listing) | PEGELONLINE DL-DE->Zero-2.0; PDFs no license found |
| rhine-kaub | PEGELONLINE `25700100/Q`; BfG yearbook `25700100_WQ.pdf` | same | 31 days by API; PDF daily tables 1998 to 2025 | 15-min / PDF | yes | as above |
| rhine-ruhrort | PEGELONLINE `2770010/Q` | same | 31 days only; BfG yearbook for Ruhrort is W only | 15-min | yes | DL-DE->Zero-2.0 |
| rhine-lobith | Rijkswaterstaat DDL, Grootheid `Q`, ProcesType `meting`, lobith.bovenrijn.tolkamer | same | 1901 to 2026 | single reading to 1970s, then 10-min | yes | CC0 1.0 |
| danube-pfelling | GKD Bayern `fluesse.abfluss` 10078000, Tagesmittelwert | same | 1925-11-01 to 2026-10-17 | daily mean | yes | CC BY 4.0 |
| danube-hofkirchen | GKD Bayern `fluesse.abfluss` 10088003 | same | 1900-11-01 to 2026-10-17 | daily mean | yes | CC BY 4.0 |
| danube-kienstock | eHYD HZB 207357 `file=5` (Q-Tagesmittel) | same | 1978-01-01 to 2023-12-31 | daily mean | yes | CC BY 4.0 |
| elbe-dresden | PEGELONLINE `501060/Q`; BfG yearbook `501060_WQ.pdf` | same | 31 days by API; PDF | 15-min / PDF | yes | DL-DE->Zero-2.0; PDFs no license found |
| elbe-magdeburg | PEGELONLINE `502180/Q`; BfG yearbook `502180_WQ.pdf` | same | as above | 15-min / PDF | yes | as above |
| elbe-wittenberge | PEGELONLINE `503050/Q`; BfG yearbook `503050_WQ.pdf` | same | as above | 15-min / PDF | yes | as above |
| seine-paris | Hub'Eau `obs_elab` QmnJ: F700000109 (1900 to 1965), F700000110 (1966 to 1973), F700000111 (1974 to 1989), F700000102 (1990 on), F700000103 (2006 on, flow station) | same site | 1900-01-02 to 2026-10-16 | daily mean | yes | not stated |
| mississippi-stlouis | USGS 07010000, 00060 stat 00003 | same | 1861-01-01 to 2026-10-16 | daily mean | yes | public domain |
| mississippi-memphis | USGS 07032000, 00060 | same | 1933 to 2026, gap about 1995 to 2014 | daily mean | yes | public domain |
| mississippi-helena | USGS 07047970 (closed 1977); current proxy USGS 07032000 Memphis | proxy for today | Helena 1928 to 1977; Memphis about 72 river miles upstream (82 km straight line) | daily mean | yes | public domain |
| mississippi-vicksburg | CWMS MVK `Vicksburg.Flow.Inst.1Day.0.DCP-rev` (also USGS 07289000 from 2008) | same | 1901-01-02 to 2026-09-13 | one value a day | yes | public domain |
| ohio-cincinnati | USGS 03255000 instantaneous 00060 (index velocity) from 2024-10-16; daily proxy USGS 03277200 Markland Dam | same (2 years) / proxy | 2024 on; Markland 1970 on, about 61 river miles downstream (53 km) | 15-min / daily mean | yes | public domain |
| ohio-louisville | USGS 03294500, 00060 | same | 1928-01-01 to 2026-10-16 | daily mean | yes | public domain |
| ohio-cairo | USGS 03612600 Olmsted (2013 on); USGS 03611500 Metropolis (1928 to 2015) | proxy | Olmsted about 17 river miles upstream (22 km) | daily mean | yes | public domain |
| missouri-bismarck | USGS 06342500, 00060 | same | 1927-10-01 to 2026-10-16 | daily mean | yes | public domain |
| missouri-hermann | USGS 06934500, 00060 (CWMS `Hermann-Missouri.Flow.Inst.~1Day.0.datman-rev` stops 2025-05-18) | same | 1928-10-01 to 2026-10-16 | daily mean | yes | public domain |
| colorado-lake-powell | RISE item 4315 (total release, cfs), 511 (inflow, cfs) | same | release 1963-03-14 on; inflow 1963-03-11 on | daily | yes | public domain |
| colorado-lake-mead | RISE item 6125 (total release, cfs); no inflow in RISE | same | 1934-04-01 on | daily | yes | public domain |
| fraser-shelley | ECCC 08KB001 HYDAT + real-time | same | 1950-05-01 to 2025-10-01 (HYDAT), real-time after | daily mean | yes | OGL-Canada |
| fraser-hope | ECCC 08MF005 | same | 1912-03-01 to 2025-02-24 (HYDAT), real-time after | daily mean | yes | OGL-Canada |
| fraser-mission | ECCC 08MH024 discharge is sparse; proxy Hope 08MF005 | proxy | Mission near-complete 1965 to early 1990s, then about 40 to 100 days a year, last 2024-07-03; Hope 68 km upstream | daily mean | yes | OGL-Canada |
| amazon-tabatinga | ANA HidroSerieHistorica tipoDados=3, 10100000 | same | 1995-01-01 to 2026-05-31 | daily | yes | no license stated |
| amazon-manacapuru | ANA tipoDados=3, 14100000 | same | 1972-01-02 to 2026-04-30 | daily | yes | no license stated |
| amazon-manaus | none at 14990000 ("Sem dados"); proxy ANA 15030000 Jatuarana (Amazon below the Negro) | proxy | Jatuarana 1977-08-26 to 2025-08-31, 43 km downstream | daily | yes | no license stated |
| amazon-obidos | ANA tipoDados=3, 17050001 (plus telemetry `Vazao`, 15-min) | same | 1968-01-01 to 2026-02-28 | daily | yes | no license stated |
| paraguay-ladario | ANA 66825000 only 1964 to 1973; proxy ANA 66800000 Amolar (upstream) or 67100000 Porto Murtinho (downstream) | proxy | Amolar 1967 to 2026-05, 108 km upstream | daily | yes | no license stated |
| paraguay-asuncion | none at DMH; proxy INA a5 series 35887 Puerto Bermejo (BDHI) | proxy | 1910 to 2025-08-31, 203 km downstream | daily mean | yes (2025 values) | no license stated |
| parana-posadas | INA series 26611 (ends 2017-09-08); proxy INA 26684 Yacyretá afluente (2006 on) and 26685 efluente (1994 on) | same to 2017, proxy after | Posadas 1970 to 2017; Yacyretá 85 km downstream | daily mean | yes (Yacyretá) | no license stated |
| parana-corrientes | INA series 26616 (Caudal medio diario) | same | 1904-01-01 to 2026-10-16 | daily mean | yes | no license stated |
| parana-parana | INA series 26626 (2015 on); BDHI Túnel Subfluvial 30123 (2001 to 2026-08-31) | same | 2015-07-21 to 2026-10-16 | daily mean | yes | no license stated |
| parana-rosario | INA series 26631 | same | 2015-07-21 to 2026-10-16 | daily mean | yes | no license stated |
| murray-albury | BoM 409001 discharge ends 1952-03-16; proxy BoM 409017 Doctors Point, ts_id 184020010 | proxy | 1929-11-02 to 2026-10-15, 4 km downstream | daily mean | yes | CC BY 4.0 |
| murray-swanhill | BoM 409204, ts_id 286638010 | same | 1974-11-14 to 2026-10-15 | daily mean | yes | CC BY 4.0 |
| murray-euston | BoM 414203, ts_id 286878010 | same | 1975-08-29 to 2026-10-15 | daily mean | yes | CC BY 4.0 |
| darling-bourke | BoM 425003, ts_id 169509010 | same | 1895-02-02 to 2026-10-15 (mostly 1972 on) | daily mean | yes | CC BY 4.0 |
| mekong-chiangsaen | MRC "Calculated daily discharge", uniqueId 9d561149e4ea4c6a9b8d213b9e767e4d | same | 1960-01-01 to 2026-10-16 | daily | yes | MRC non-commercial, not open |
| mekong-vientiane | MRC Vientiane discharge ends 2006-12-30; proxy MRC 012001 Nong Khai | same to 2006, proxy after | Nong Khai 1969 to 2026-10-16, 13 km downstream | daily | yes | MRC non-commercial |
| mekong-pakse | MRC uniqueId 7f5e461f31154629877a56346b726926 | same | 1923-01-01 to 2026-10-16 | daily | yes | MRC non-commercial |
| mekong-kratie | MRC uniqueId 22a8130e3593419784367fb4f1d864c0 | same | 1924-01-01 to 2026-10-16 | daily (stored hourly copies) | yes | MRC non-commercial |

Count: 27 gauges have a daily discharge series at the same station,
counting the two dam releases (some short: Paraná and Rosario from 2015,
Kienstock to 2023); 10 need a nearby station for all or recent years
(Helena, Cincinnati, Cairo, Mission, Manaus, Ladário, Asunción, Posadas,
Albury, Vientiane); the 6
German federal gauges (Maxau, Kaub, Ruhrort, Dresden, Magdeburg,
Wittenberge) have only 31 days of raw discharge by API plus yearbook PDFs, so
no long open machine-readable daily record. Of the proxies, Manaus and
Ladário are poor matches; we recommend showing no discharge there.

## Per-gauge detail

### Germany, federal waterways (PEGELONLINE, BfG yearbook)

| Gauge | PEGELONLINE Q | Value 2026-10-17 | Long record |
|---|---|---|---|
| rhine-maxau | `stations/b6c6d5c8-.../Q/measurements.json` | 351 m³/s | `dgj-daten.bafg.de/Rhein/Maxau/23700200_WQ.pdf` |
| rhine-kaub | `stations/1d26e504-.../Q` | 479 m³/s | `dgj-daten.bafg.de/Rhein/Kaub/25700100_WQ.pdf` (36 pages: one level page and one discharge page per year, 1998 to 2025) |
| rhine-ruhrort | `stations/c0f51e35-.../Q` | 634 m³/s | yearbook folder has `2770010_W.pdf` only (no Q) |
| elbe-dresden | `stations/70272185-.../Q` | 84.8 m³/s | `Elbe/Dresden/501060_WQ.pdf` |
| elbe-magdeburg | `stations/ccccb57f-.../Q` | 144 m³/s | `Elbe/Magdeburg-Strombrücke/502180_WQ.pdf` |
| elbe-wittenberge | `stations/cbf3cd49-.../Q` | 199 m³/s | `Elbe/Wittenberge/503050_WQ.pdf` |

- URL pattern: `https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/<uuid>/Q/measurements.json?start=P31D`.
- PEGELONLINE keeps only 31 days of raw, unchecked values. hyd1d (our level
  history) has water level only.
- The BfG yearbook (Deutsches Gewässerkundliches Jahrbuch) PDFs have daily
  discharge tables for each year from about 1998 to 2025 and main values
  back to about 1900, but they are PDFs, one table per year. Parsing them is
  possible but fragile. We found no license on `dgj-daten.bafg.de`.
- Longer checked daily series: BfG data service by email
  (Datenstelle-M1@bafg.de), terms not known. GRDC has these series but forbids
  republishing. The project notes already flag Ruhrort: discharge cannot be
  computed below 120 cm right now.

### Netherlands (Rijkswaterstaat)

- rhine-lobith: `POST https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen`
  with `Grootheid: {Code: "Q"}`, `Compartiment: OW`, `ProcesType: meting`,
  Locatie `lobith.bovenrijn.tolkamer`. Unit m3/s, Hoedanigheid NVT.
- Verified: 145 readings for October 14, 2026 (10-minute, 621.36 m³/s at
  midnight, status Ongecontroleerd, code 00). 1901: one reading a day at
  08:00 (2,035 m³/s on 1901-01-01). Years 1866 to 1900 return no data, so
  discharge starts in 1901, 35 years after level.
- Flags: same Kwaliteitswaardecode and Statuswaarde as level
  (`OpdrachtgevendeInstantie: ONXXREG_AFVOER`). 1901 values also show
  "Ongecontroleerd", so status alone does not mark old values as checked.
- License: CC0 1.0.

### Bavaria (GKD)

- Same download center as the level fetch, with `t={"<code>": ["fluesse.abfluss"]}`
  instead of `fluesse.wasserstand`, `wertart=tmw`, `zr=gesamt`.
- danube-pfelling 10078000: "Tageswerte Abfluss [m³/s]", mean, max, min,
  Prüfstatus. 1925-11-01 to 2026-10-17. Geprueft through 2025-12-31,
  Rohdaten from 2026-01-01 (147 m³/s on 2026-10-16). Discharge starts 17
  months before our level series (1927-04-04).
- danube-hofkirchen 10088003: 1900-11-01 to 2026-10-17 (about 45,700 rows),
  Geprueft through 2025, Rohdaten 2026. Discharge starts 25 years before our
  level series (1925-11-01).
- License CC BY 4.0, credit "Datenquelle: Bayerisches Landesamt für Umwelt,
  www.lfu.bayern.de".

### Austria (eHYD)

- danube-kienstock 207357: `https://ehyd.gv.at/services/MessstellenExtraData/owf?id=207357&file=5`.
  Header: `Exportzeitreihe: (10001016,Abfluss,I,Mit,T,...)`, unit m³/s,
  1978-01-01 to 2023-12-31, 16,802 daily rows, one "Lücke" gap row besides
  the end marker. Station master data (`file=1`) lists discharge from 1976 by
  "Pegelschlüssel" (rating curve). Discharge starts 2 years after level. Other
  files: 3/4 monthly low and high levels, 6/7 monthly low and high discharge,
  8 a monthly series.
- Same yearbook lag as level: nothing after 2023. Footnotes say discharge
  in many months 1996 to 2023 was computed from filled-in levels.
- License CC BY 4.0 (OGD Austria). Credit "Datenquelle: ehyd.gv.at".

### France (Hub'Eau)

- seine-paris: `https://hubeau.eaufrance.fr/api/v2/hydrometrie/obs_elab?code_entite=<station>&grandeur_hydro_elab=QmnJ`
  (daily mean flow). Values are in liters per second (102,039 = 102 m³/s).
- Stations: F700000109 1900-01-02 to 1965 (23,993 days, all "Donnée validée",
  method "Calculée"; of the first 20,000 days, 15,080 are qualified
  "Douteuse", doubtful), F700000110 1966 to 1973 (2,920), F700000111 1974
  to 1989 (5,842), F700000102 1990 to 2026-10-16 (7,989 days, with gaps,
  18 doubtful), F700000103 the flow station from 2006-01-28 to 2026-10-16
  (7,567 days; 6,554 validated, 995 pre-validated, recent days "Donnée brute").
- Recommended stitch: 109, 110, 111, then 102 to January 2006, then 103.
  The overlap 2006 to 2026 between 102 and 103 should be compared before
  choosing.
- Verified: F700000103 2026-10-16 = 85,698 L/s (raw, not qualified).
- License: not stated (same as level).

### United States (USGS NWIS and CWMS)

USGS URL pattern (legacy, still answering):
`https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=<site>&parameterCd=00060&statCd=00003&startDT=...&endDT=...`.
The new USGS Water Data API also answered:
`https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?monitoring_location_id=USGS-07010000&parameter_code=00060&statistic_id=00003&time=2026-10-10/2026-10-16`
(returns `approval_status` "Provisional", unit ft^3/s). USGS has said the
legacy services will be retired; a new fetch should use the new API.

| Gauge | Site | Record | Value 2026-10-16 | Flags in record |
|---|---|---|---|---|
| mississippi-stlouis | 07010000 | 1861-01-01 on, 60,186 days, essentially complete | 218,000 cfs (P) | A 59,903; A:e 144; P 139 |
| mississippi-memphis | 07032000 | 1933-01-01 on, 26,951 days; no values about 1995 to 2014 | 387,000 cfs (P) | A 26,840; A:e 31; P 80 |
| mississippi-helena | 07047970 (closed) | 1928-01-01 to 1977-09-29 | n/a (1977-09-29: 416,000 A) | |
| mississippi-vicksburg | 07289000 | 2008-01-01 on | 476,000 cfs (P) | |
| ohio-cincinnati | 03255000 iv only | 2024-10-16 on, 15-min | 80,600 cfs at 08:00 EDT Oct 17 (P) | |
| ohio-cincinnati proxy | 03277200 Markland Dam | 1970-05-01 on | 97,600 cfs (P) | |
| ohio-louisville | 03294500 | 1928-01-01 on, 36,063 days | 100,000 cfs (P) | |
| ohio-cairo proxy | 03612600 Olmsted | 2013-03-01 on | 150,000 cfs (P) | |
| ohio-cairo older proxy | 03611500 Metropolis | 1928-04-01 to 2015-01-12 | n/a | |
| missouri-bismarck | 06342500 | 1927-10-01 on, 36,024 days | 13,000 cfs (P) | A 31,929; A:e 3,757 (about 10%, mostly winter ice); P 240; P:e 98 |
| missouri-hermann | 06934500 | 1928-10-01 on, 35,806 days | 74,800 cfs (P) | |

CWMS (`https://cwms-data.usace.army.mil/cwms-data/timeseries?office=<o>&name=<ts>&begin=...&end=...`,
header `Accept: application/json;version=2`):
- mississippi-vicksburg: `MVK:Vicksburg.Flow.Inst.1Day.0.DCP-rev`, 1901-01-02
  to 2026-09-13, cfs, quality code 0 throughout the samples. Same family as
  the level series, so one reading a day stamped 12:00 UTC. 1901-01-02:
  362,000 cfs; 2026-09-13: 293,920 cfs. This is the long record at
  Vicksburg; USGS starts in 2008.
- mississippi-helena: no Flow series in MVS, MVK or MVM. MVK has
  `Arkansas City.Flow.Inst.1Day.0.DCP-rev` (1952 to 2026-09-13), but that is
  about 110 river miles downstream, below the White and Arkansas rivers, so
  Memphis is the better proxy (the St. Francis River joins between).
- missouri-hermann: `MVS:Hermann-Missouri.Flow.Inst.~1Day.0.datman-rev`
  1928-10-01 to 2025-05-18. Use USGS instead (current).
- ohio-louisville: `LRL:McAlpine-MLPK2.Flow-Total.Inst.0.0.LPMS-comp` (hourly
  dam outflow, 2012 on). USGS 03294500 is the long record.
- ohio-cincinnati: `LRL:Cincinnati.Flow.Inst.15Minutes.0.USGS-rev` is a copy of
  the USGS instantaneous series (2025 on).
- ohio-cairo: only river forecast center series (`LMRFCShef`), not observed.
- mississippi-stlouis: Corps has only rating copies and forecasts from 2002;
  use USGS.

License: U.S. federal government work, public domain.

### Reservoirs (RISE)

URL pattern: `https://data.usbr.gov/rise/api/result?itemId=<id>&itemsPerPage=...&dateTime[after]=YYYY-MM-DD`
(header `Accept: application/vnd.api+json`). Without the date filter, items
511 and 4315 timed out twice; with it they answered in under half a second.

| Item | What | Record | Value |
|---|---|---|---|
| 4315 | Lake Powell, Glen Canyon Dam total release, cfs, daily average | 1963-03-14 to 2026-10-15 | 6,613.29 (Oct 15) |
| 507 | Powell powerplant release, cfs | 1963-12-28 on | 6,613.29 (all release went through the plant) |
| 4391, 4392 | Powell spillway and bypass release, cfs | 2004-06-03 on | |
| 511 | Powell inflow, cfs, daily average | 1963-03-11 to 2026-10-15 | 8,418 (Oct 13), 13,188 (Oct 14), 21,407 (Oct 15) |
| 512 | Powell unregulated inflow, cfs | 1963-06-29 on | 20,012 (Oct 15) |
| 6125 | Lake Mead, Hoover Dam total release, cfs | 1934-04-01 to 2026-10-16 | 7,480.2 (Oct 16) |
| 6122 | Mead total release, acre-feet | 1934-04-01 on | |
| (none) | Mead inflow | not in RISE | |

Independent USGS gauges near the dams: 09380000 Colorado River at Lees Ferry
(below Glen Canyon Dam, 1921-10-01 on; 6,590 cfs on Oct 16, close to the
RISE release), 09421500 below Hoover Dam (1934-04-01 to 2026-02-05, no
recent values), 09404200 above Diamond Creek in the Grand Canyon (1983 on;
7,780 cfs Oct 16), the closest measured flow into Lake Mead.

What discharge means here: neither lake has a river gauge in the usual sense.
- Release is water let through the dam (turbines, plus bypass and spillway
  when used). It is set by operators under the river's operating rules, so it
  shows management decisions more than weather.
- Powell inflow is computed by Reclamation, not gauged at the lake. RISE does
  not say how; Reclamation's usual method is a water budget (change in
  storage plus release plus evaporation). That makes daily inflow noisy, as
  the jump from 8,418 to 21,407 cfs in three days shows. It is better
  summed to months or years.
- Mead has no inflow series in RISE at all.

Recommendation: show release at both lakes. It is the only series published
at both, from the same API, with the same daily average, back to 1963 and
1934. Label it "release from the dam," not "river flow," and explain that
the lake level moves with the difference between what comes in and what is
released. Powell inflow can go in the notes as a monthly figure if wanted.

### Canada (ECCC)

URL pattern: `https://api.weather.gc.ca/collections/hydrometric-daily-mean/items?f=json&STATION_NUMBER=<stn>&sortby=DATE`
(HYDAT, approved) and `hydrometric-realtime` (provisional, 5-minute, about
30 days), or the wateroffice real-time CSV our level fetch already uses.
Field `DISCHARGE` in m³/s with `DISCHARGE_SYMBOL_EN`.

- fraser-shelley 08KB001: discharge 1950-05-01 to 2025-10-01 in HYDAT (our
  level starts 2011). Of the last 10,000 days with discharge, 3,782 carry
  "Ice Conditions" (winter), 67 "Estimated", 26 "Partial Day". Real-time
  2026-10-17 12:05 UTC: 822 m³/s.
- fraser-hope 08MF005: 1912-03-01 to 2025-02-24 in HYDAT; real-time
  1,770 m³/s. Of the last 10,000 days: 183 estimated, 74 ice, 103 partial.
- fraser-mission 08MH024: discharge is published only in parts: near-complete
  from 1965-05-01 to the early 1990s, then about 40 to 100 days a year (2013
  to 2023), last value 2024-07-03. Real-time has level only. Mission is tidal.
  Proxy: Hope, 68 km upstream; the Harrison River and other tributaries join
  between, so Hope flow is lower than Mission flow.
- License: Open Government Licence - Canada.

### Brazil (ANA)

URL pattern: `https://telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroSerieHistorica?codEstacao=<code>&dataInicio=&dataFim=&tipoDados=3&nivelConsistencia=`
(one row per month with Vazao01..Vazao31 and Vazao01Status..; same parser
as the level series). Recent days: `DadosHidrometeorologicos` (telemetry,
field `Vazao`).

| Gauge | Code | Days | First | Last | Consistido (level 2) | Status codes |
|---|---|---|---|---|---|---|
| amazon-tabatinga | 10100000 | 11,452 | 1995-01-01 | 2026-05-31 | through 2023-12 | 1 real 11,052; 2 estimated 340 |
| amazon-manacapuru | 14100000 | 19,731 | 1972-01-02 | 2026-04-30 | through 2023-12 | 1: 19,141; 2: 186; 3 doubtful: 4 |
| amazon-manaus | 14990000 | none | | | | "Sem dados para esta estação" |
| amazon-obidos | 17050001 | 20,858 | 1968-01-01 | 2026-02-28 | through 2023-12 | 1: 20,556; 2: 118 |
| paraguay-ladario | 66825000 | 3,653 | 1964-01-01 | 1973-12-31 | all | |
| Manaus proxy | 15030000 Jatuarana | 17,477 | 1977-08-26 | 2025-08-31 | | |
| Ladário proxy | 66800000 Amolar | 19,295 | 1967-11-16 | 2026-05-31 | | |
| Ladário proxy | 67100000 Porto Murtinho | 22,858 | 1963-11-01 | 2026-05-31 | | |

- Telemetry check for Oct 10 to 16, 2026: Óbidos had a `Vazao` on all 672
  readings (93,189 m³/s at 23:45 on Oct 16); Manacapuru on 158 of 672;
  Tabatinga on 14 of 664; Manaus and Ladário none.
- Manaus is on the Rio Negro just above where it meets the Solimões. The
  Negro there is backed up by the Solimões, so level alone cannot give flow,
  which is likely why ANA publishes none. Jatuarana, 43 km downstream, is on
  the Amazon below the meeting and carries both rivers, so it is not the
  Negro's flow. Manacapuru (67 km upstream on the Solimões) is a different
  river. We recommend showing no discharge at Manaus.
- Ladário: discharge only 1964 to 1973. The Pantanal makes the
  level-to-flow relation loop (the same level gives different flows on the
  rise and the fall). Amolar is 108 km upstream, Forte Coimbra 66970000
  (1969 to 1981 only) 104 km downstream, Porto Murtinho 302 km downstream.
- Method field `MetodoObtencaoVazoes` is 1 for nearly all months (rating
  curve, "curva-chave"; ANA's code list should be confirmed).
- License: none stated on the service (same as level).

### Argentina and Paraguay (INA a5)

URL pattern: `https://alerta.ina.gob.ar/a5/obs/puntual/series/<id>/observaciones?timestart=...&timeend=...`,
metadata with `date_range` at `/a5/obs/puntual/series/<id>`. Variable 40
"Caudal medio diario" (daily mean); variable 4 "Caudal" with procedure
"Curva de gasto" (from the rating curve) is the per-reading series.

| Gauge | Series | Record | Value 2026-10-15 |
|---|---|---|---|
| parana-posadas | 26611 (var 40); 863 (var 4, curva de gasto, 1901 to 2017) | 1970-01-01 to 2017-09-08 | none after 2017 |
| Posadas proxy | 26684 Yacyretá afluente (inflow to the reservoir Posadas sits in) | 2006-01-01 to 2026-10-16 | 40,000 m³/s |
| Posadas proxy | 26685 Yacyretá efluente (dam outflow) | 1994-07-24 to 2026-10-16 | 38,700 m³/s |
| parana-corrientes | 26616 (var 40); 868 (var 4, 1910 on) | 1904-01-01 to 2026-10-16, 43,715 values | 25,598.5 m³/s |
| parana-parana | 26626 (var 40) | 2015-07-21 to 2026-10-16, 2,927 values | 17,293 m³/s |
| Paraná alternative | 30123 Túnel Subfluvial (BDHI, under 1 km away) | 2001-05-01 to 2026-08-31, 9,198 values | none in October |
| parana-rosario | 26631 (var 40) | 2015-07-21 to 2026-10-16, 2,942 values | 19,001.1 m³/s |
| paraguay-asuncion | none (INA station 157 has no discharge series; DMH publishes level only) | | |
| Asunción proxy | 35887 Paraguay at Puerto Bermejo (BDHI) | 1910-01-01 to 2025-08-31, 37,339 values | 2,557 m³/s on 2025-08-25 (loaded Feb 2026) |

- Posadas sits in the Yacyretá reservoir, so its level is held by the dam;
  Yacyretá inflow and outflow (85 km downstream) are the relevant flows.
- On October 15, 2026, Yacyretá outflow was 38,700 m³/s and Corrientes
  25,599 m³/s, even though Corrientes is downstream and the Paraguay River
  joins in between. This could be a flood wave that had not yet reached
  Corrientes, or a problem with one series. We did not resolve it.
- Puerto Bermejo is 203 km downstream of Asunción; the Pilcomayo joins just
  below Asunción and the Bermejo near Puerto Bermejo, so this is a rough
  proxy.
- No per-value quality flags. License: none stated (same as level).

### Australia (BoM)

URL pattern: `https://www.bom.gov.au/waterdata/services?service=kisters&type=queryServices&datasource=0&format=json&request=getTimeseriesValues&ts_id=<id>&from=...`,
parameter type "Water Course Discharge", series `DMQaQc.Merged.DailyMean.24HR`
(the same naming as our level series), unit cumec (m³/s).

| Gauge | ts_id | Record | Quality counts (A best / B compromised / C estimate / E unknown) |
|---|---|---|---|
| murray-albury 409001 | 145565010 | 1908-01-02 to 1952-03-16 only | A 15,929 / C 152 / E 48 |
| Albury proxy 409017 Doctors Point | 184020010 | 1929-11-02 to 2026-10-15 (153.5 m³/s, code E) | A 10,267 / B 3,876 / C 765 / E 17,753 |
| murray-swanhill 409204 | 286638010 | 1974-11-14 to 2026-10-15 (126.6) | A 17,729 / B 49 / C 808 / E 378 |
| murray-euston 414203 | 286878010 | 1975-08-29 to 2026-10-15 (138.5) | A 17,378 / B 46 / C 983 / E 267 |
| darling-bourke 425003 | 169509010 | 1895-02-02 to 2026-10-15 (1.98), 19,966 days, mostly 1972 on | A 9,955 / B 4,023 / C 232 / E 5,756 |

- Albury: discharge at the Albury gauge stopped in 1952. Doctors Point is
  4 km downstream, below Hume Dam's releases and above the Kiewa River.
  More than half of Doctors Point's days are quality E (unknown).
- Euston is a weir pool; its level is held by the weir, so discharge there
  tells more about the river than level does.
- License: CC BY 4.0, credit BoM and the station owner (NSW, Victoria).

### Mekong (MRC)

URL pattern: `https://timeseries.api.mrcmekong.org/api/v1/ts/data/timeSeriesCorrectedData/<uniqueId>?sd=...&ed=...`;
series found in `/ts/inventory/timeSeriesList` with `parameter: "Discharge"`,
label "Calculated daily discharge", unit m^3/s.

| Gauge | uniqueId | Record | Value 2026-10-16 07:00 local |
|---|---|---|---|
| mekong-chiangsaen 010501 | 9d561149e4ea4c6a9b8d213b9e767e4d | 1960-01-01 to 2026-10-16, 24,396 days (every day) | 1,570 |
| mekong-vientiane 011901 | 6b2a32b7aaaa4ca7929d54e2fc82b886 | 1913-01-01 to 2006-12-31, 34,333 days | none |
| Vientiane proxy 012001 Nong Khai | 25697afb7f344a55a45f9ca9e463398d | 1969-01-01 to 2026-10-16, 21,107 days | 3,083 |
| mekong-pakse 013901 | 7f5e461f31154629877a56346b726926 | 1923-01-01 to 2026-10-16, 37,881 days | 7,375 |
| mekong-kratie 014901 | 22a8130e3593419784367fb4f1d864c0 | 1924-01-01 to 2026-10-16, 37,348 days | 12,348 |

- Approval level for all: 800 "Working" (not final). Grade codes seen:
  -1, 11, 21, 31, 41 (meanings to be checked against MRC's grade list).
  Kratie has 8 notes and Pakse 2 attached to the series (not read).
- Kratie stores the daily value repeated hourly (12 identical values, then a
  new one), so a fetch must collapse to one value per local day.
- Nong Khai is 13 km downstream of Vientiane, with no large tributary in
  between.
- License: MRC Non-commercial Data Use Licence (not open), same as level.

## Draft DATASETS.md "Discharge" subsections

Each block would sit inside the existing publisher section, after
"License and attribution."

---

**Rules that apply to every discharge series** (for "Rules that apply to
every gauge")

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
- Where we show flow from a nearby station, the page says which station and
  how far away, and the two series are not combined.

---

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
No license is stated on the yearbook server. For now these six gauges show
no discharge history. Limits: rating curves are revised as the riverbed
changes, which on the Rhine and Elbe has been large (see the level notes on
bed erosion); BfG notes that discharge at Ruhrort cannot be computed below
120 cm right now.

---

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

---

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

---

**eHYD (Danube at Kienstock).**

*Discharge.* `file=5` of the same eHYD service (Q-Tagesmittel, daily mean,
m³/s), January 1, 1978 to December 31, 2023, with one gap. Computed from
level with a rating ("Pegelschlüssel"), per the station master data, from
1976. Like level, it is yearbook data and ends in 2023. Footnotes say many
months from 1996 to 2023 were computed from filled-in levels. License CC BY
4.0, credit "Datenquelle: ehyd.gv.at".

---

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

---

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
an index-velocity meter since October 2024. For Cairo we show Olmsted
(03612600, about 17 river miles upstream, from 2013); for Cincinnati,
Markland Dam (03277200, about 61 river miles downstream, from 1970); for
Helena after 1977, Memphis (about 72 river miles upstream). Limits:
on the Mississippi the same level can carry different flows on a rising and
falling river, and the earliest St. Louis values rest on few field
measurements (how USGS built the 1861 to 1930s record is not yet sourced). The legacy service is being retired; the new
API (api.waterdata.usgs.gov) returns the same values. Public domain, credit
U.S. Geological Survey.

---

**USACE CWMS (Vicksburg).**

*Discharge.* `MVK:Vicksburg.Flow.Inst.1Day.0.DCP-rev`, cfs, one value a day
from January 2, 1901, to September 13, 2026, the same family and reading
time as the level series. Quality code 0 (not screened) throughout, so the
Corps file gives no approval status. USGS 07289000 has daily means at
Vicksburg from 2008 and could check the overlap. Limits: same as level
(several gauge sites before 1977), plus the rating questions above. Public
domain, credit U.S. Army Corps of Engineers.

---

**RISE (Lake Powell, Lake Mead).**

*Discharge.* A lake has no river flow at the gauge, so we show release: the
daily average flow let through the dam. Lake Powell (Glen Canyon Dam) item
4315, from March 14, 1963; Lake Mead (Hoover Dam) item 6125, from April 1,
1934; both cfs, updated daily, provisional like the elevation series. The
release is set by dam operators under the river's operating rules, so it
reflects decisions, not just weather. Reclamation also publishes a computed
inflow for Lake Powell (item 511), not a gauged one; it swings widely from
day to day. RISE has no inflow for Lake Mead. USGS gauges just below Glen
Canyon Dam (Lees Ferry, 09380000) measure the released water independently.
Public domain, credit U.S. Bureau of Reclamation.

---

**ECCC Water Survey of Canada (Fraser at Shelley and Hope; Mission).**

*Discharge.* Same HYDAT and real-time services as level, field `DISCHARGE`,
m³/s. Shelley from 1950 (longer than its level record, which starts in 2011),
Hope from 1912. HYDAT is approved and runs to 2025; later days are real-time
and provisional. Each day can carry a symbol: B (ice conditions), E
(estimated), A (partial day). At Shelley about a third of days in recent
decades carry the ice symbol, because winter ice changes the level for a
given flow. Mission is tidal and has discharge only for 1965 to the early
1990s and scattered days after, so for Mission we show Hope's flow, 68 km
upstream, and say that tributaries in between add to it. Open Government
Licence - Canada.

---

**ANA HidroWeb (Tabatinga, Manacapuru, Óbidos; Ladário 1964 to 1973).**

*Discharge.* Same `HidroSerieHistorica` service as level, with
`tipoDados=3`, m³/s. Tabatinga from 1995, Manacapuru from 1972, Óbidos from
1968. Checked ("consistido") values run through 2023; later months are raw
and end in early to mid 2026. Each day has a status: real, estimated or
doubtful. ANA publishes no discharge at Manaus, where the Rio Negro is
backed up by the Solimões, and Ladário has discharge only for 1964 to
1973, so these two gauges show none. Limits: on these large, flat rivers the
same level gives different flows on the rise and the fall, so ratings are
uncertain, especially at record highs and lows. License: none stated by ANA.

---

**INA (Paraná at Corrientes, Paraná, Rosario; Posadas to 2017).**

*Discharge.* Same a5 API as level, variable 40 (daily mean flow), m³/s:
Corrientes from 1904, Paraná and Rosario only from July 2015, Posadas 1970
to September 2017. INA labels the per-reading series as computed from a
rating curve ("curva de gasto"). Posadas sits in the Yacyretá reservoir; for
recent years we would show Yacyretá's inflow or outflow, 85 km downstream.
No per-value quality flags. Asunción has no discharge series; the nearest
is the Paraguay at Puerto Bermejo, 203 km downstream, which lags by months.
License: none stated.

---

**BoM Water Data Online (Swan Hill, Euston, Bourke; Albury via Doctors
Point).**

*Discharge.* Same KiWIS service, parameter "Water Course Discharge," series
`DMQaQc.Merged.DailyMean.24HR`, m³/s. Swan Hill from 1974, Euston from 1975,
Bourke mostly from 1972. Albury's own discharge record stops in 1952; we use
Doctors Point (409017), 4 km downstream, from 1929. Quality codes: A (best
available), B (compromised), C (estimate), E (unknown). More than half of
Doctors Point's days are E. The Murray is regulated by Hume Dam and weirs,
so flows reflect releases. CC BY 4.0, credit Bureau of Meteorology and the
station owner.

---

**MRC (Chiang Saen, Pakse, Kratie; Vientiane to 2006).**

*Discharge.* Same time-series API, parameter "Discharge" ("Calculated daily
discharge"), m³/s: Chiang Saen from 1960, Pakse from 1923, Kratie from 1924.
Vientiane's series ends in 2006; Nong Khai, 13 km downstream, runs to 2026.
All series carry approval level "Working," not final. Kratie repeats each
daily value hourly; we keep one per day. Limits: none documented by MRC in the series
metadata; Kratie and Pakse carry notes we have not read. Upstream dams
change dry-season flows (dates to be sourced). MRC Non-commercial
Data Use Licence, not open.

## Not checked or open questions

- No completeness count per decade for Vicksburg CWMS flow or INA beyond
  the date ranges and value counts.
- BoM, MRC grade code and ANA `MetodoObtencaoVazoes` meanings should be
  confirmed against each publisher's code lists.
- Corrientes versus Yacyretá on October 15, 2026 (see INA).
- Whether the BfG data service would release long daily discharge for the
  six German federal gauges under an open license.
- Powell inflow method: RISE does not document it.
- Paris reservoir dates and upstream Mekong dam dates still need a source.
- Powell inflow "water budget" method is Reclamation's usual practice, not
  confirmed in RISE metadata.
