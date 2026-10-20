# River discharge (flow) for rivers with no open level record

Research date: October 17, 2026. Every fact is tagged:

- **[verified]**: a request worked today; the URL is given.
- **[documented]**: taken from a publisher's document; the URL is given.
- **[unknown]**: could not be confirmed.

Raw downloads are in the session scratchpad under `dl/` and are not in the
repo. No project files were edited. No accounts were created.

## Short answer

1. The SAGE "Global River Discharge Database" is not RivDIS alone. It is the
   CPEP River Discharge Data Set (Coe and Olejniczak, 1999, UW-Madison). It
   combines RivDIS (Vorosmarty et al., UNESCO), USGS and Brazil's ANEEL/DNAEE
   records. It holds monthly means only, and almost all of its records end
   before 2000 (median end year 1984). For our rivers it is a free, no-login
   source of monthly history that stops in the 1970s or 1980s.
2. The only open, measured, daily, current flow records for our target rivers
   are ArcticGRO's Ob, Yenisei and Lena series (Roshydromet, 1936 to 2025 or
   2026, "free to use by anyone for any purpose").
3. GRDC-Caravan (CC BY 4.0) adds open, measured, daily flow for the Orange at
   Vioolsdrif and the upper Zambezi at Katima Mulilo, 1950 to 2023. Its values
   are rounded so coarsely that the Orange series is not usable day by day
   (see below).
4. For the Niger, Congo, Nile, Volga, Amur, Yangtze, Yellow, Ganges,
   Brahmaputra, Indus, Irrawaddy, Tigris and Euphrates, nothing measured and
   open runs to the present. The open choices are old monthly measured data
   (SAGE/RivDIS, ending 1970s to 2004) or modeled flow (GEOGLOWS, CC BY 4.0,
   daily 1940 to 2026; GloFAS, free account, daily 1979 to 2026).
5. Modeled flow is far off at several of these gauges. GEOGLOWS gives the
   Niger at Niamey an average of 2,844 m3/s; the measured average in RivDIS is
   901 m3/s, so the model is 216% higher. The Nile at Dongola: model 21,066,
   measured 2,622 (703% higher). The Congo at Kinshasa: model 63,470,
   measured about 40,190 (58% higher). Model values should not be presented as
   measurements, and probably should not be shown as absolute flow at all.

## 1. SAGE "Global River Discharge Database"

**What it is.** [verified] The page says: "a compilation of monthly mean river
discharge data for over 3,500 sites worldwide. The data sources are RivDis2.0,
the United States Geological Survey, Brazilian National Department of Water
and Electrical Energy, and HYDAT-Environment Canada ... All data is in m3/s."
It also says "The database contains 3,681 stations."
https://sage.nelson.wisc.edu/riverdata/index.php

[documented] It is the old CPEP River Discharge Data Set: "Coe, Michael T. and
Nick Olejniczak (1999) CPEP River Discharge Data Set. Climate, People, and
Environment Program, University of Wisconsin, Madison." The CPEP readme gives
the same source list (RivDis2.0, USGS, Brazilian DNAEE) and says "The data are
freely available from our web site."
https://data.ornldaac.earthdata.nasa.gov/public/safari2k/hydrology/river_discharge_cpep/comp/cpep_discharge_readme.pdf

**RivDIS, the main non-US source.** [documented] "Global River Discharge,
1807-1991, V. 1.1 (RivDIS)", Vorosmarty, Fekete and Tucker, 1998, ORNL DAAC,
doi:10.3334/ORNLDAAC/199. 1,018 stations, monthly, mean record 21.5 years,
"derived from the published UNESCO archives for river discharge and checked
against information obtained from the Global Runoff Center in Koblenz."
Version 1.0 (949 stations) was published by UNESCO's International
Hydrological Programme in 1996. The UNESCO records were keypunched twice,
compared, checked against GRDC records, and plotted to find outliers. Each
station has a RELIABLE flag (0 suspect, 1 reliable) and a REASON. The ORNL
guide says "Future Modifications and Plans: None at this time."
https://data.ornldaac.earthdata.nasa.gov/public/global_hydroclimatology/rivdis/comp/rivdis_guide.pdf

"RivDis2.0" is named by SAGE and CPEP but no release document for it was
found. [unknown] SAGE has a few series labeled RivDIS that run past 1991
(Brazzaville 1984 to 2002, Malanville 1976 to 2004), so SAGE holds some data
beyond RivDIS v1.1.

**Where the numbers came from.** [documented] UNESCO's published archives
(the "Discharge of Selected Rivers of the World" series), which national
hydrological services supplied. The ORNL guide does not name the agencies
station by station. For the Russian rivers the agency is Roshydromet (our
comparison with ArcticGRO below matches most months to within 1%).

**Station count.** [verified] The full index (75 pages of
`keysearch.php?numfiles=50&startnum=N`) lists 3,125 entries, not 3,681. Only
2,037 PointIDs are unique, because RivDIS and ANEEL reuse the same numbers
(75 PointIDs point to two different stations). Sources as labeled: USGS 1,980,
RivDIS 963, ANEEL 122, blank 60. No entry is labeled HYDAT.

**Time step and period.** [verified] Monthly means only. End years: median
1984; 59% of entries end by 1990; all but a handful end before 2000. RivDIS
entries: median end 1982, 99% end by 1991.

**Units.** [verified] m3/s. Files carry Year, Jan to Dec, and "Avg Annual".
Missing months are -9999.

**Maintained?** [verified, by inference] No sign of upkeep. Footer copyright
2021; no version or update date; the station list is frozen at 1999-era
content; broken values remain (below).

**How to download.** [verified] No login. Tab-delimited text per station:
`https://sage.nelson.wisc.edu/riverdata/station_table_formated.php?pointid=<PointID>`
(served as `<PointID>.txt`, `Content-Type: text/tab-separated-values`).
Example worked today: pointid=1534 (Congo at Kinshasa, 1903 to 1983).
Search: `keysearch.php?keyword=<text>`. HTML view:
`station_table.php?qual=256&filenum=<entry>`. The full RivDIS package from
ORNL needs a free NASA Earthdata login (the zip redirects to
urs.earthdata.nasa.gov); the station table `STATION.DAT` is open.
https://data.ornldaac.earthdata.nasa.gov/public/global_hydroclimatology/rivdis/comp/STATION.DAT

**License.** No license text on the SAGE pages [verified]. CPEP readme: "The
data are freely available" [documented]. NASA's catalog entry for RivDIS
points to NASA's data use policy [verified, CMR record for rivdis_199]. That
policy makes NASA-mission data CC0 but says data from non-NASA sources carry
the source's terms [documented,
https://www.earthdata.nasa.gov/learn/use-data/data-use-policy]. RivDIS itself
was published by UNESCO as an open technical document. Plain reading: no
document restricts republishing RivDIS values; credit Vorosmarty et al. and
SAGE/CPEP.

**Overlap with GRDC.** [documented] Yes, heavy. RivDIS was checked against
GRDC records and differences were resolved, so most RivDIS station-months
will also be in GRDC. But the RivDIS values came from UNESCO's published
yearbooks, not from a GRDC download. GRDC's terms bind people who download
from GRDC ("The redistribution of the downloaded data ... is not allowed").
They are a contract with GRDC users, and RivDIS was not obtained under them.
GRDC also says "All hydrological data remain property of the owner," meaning
the national services. Our reading, which is not legal advice: the GRDC terms
do not reach values we take from RivDIS or SAGE, and the national services
released these values through UNESCO for open publication. The safest
credit line names the national service, UNESCO/RivDIS and SAGE.

**Quality checks we ran today.**
- Monthly SAGE values for the Ob (Salekhard), Yenisei (Igarka) and Lena
  (Kyusyur) vs. monthly means of ArcticGRO daily data: 539 of 588, 400 of 503
  and 555 of 586 overlapping months agree within 1%; the median difference is
  0.07% to 0.10%. A few months are badly off: Yenisei June 1983 is 10,700 in
  SAGE and 106,873 in ArcticGRO (a dropped digit); Lena October 1970 is 2,300
  vs. 14,348. [verified]
- Congo at Kinshasa, April 1903: 3,280 m3/s between 32,410 (March) and
  34,970 (May). Almost certainly a dropped digit. [verified]
- Blue Nile at Khartoum is labeled 1976 to 2046 (71 years). The years are
  wrong; the true span is unknown. Do not use. [verified]
- Volga at Staritsa: RivDIS flags it "Bogus Discharge" (mean 154 m3/s on a
  river that carries about 8,000). Ganges at Paksay (Hardinge Bridge) also
  "Bogus Discharge". Congo at Brazzaville flagged "Second station in the
  same cell". [verified, STATION.DAT]

### SAGE stations for our target rivers [all verified by download today]

| River | Station (PointID) | Years | Complete years | Notes |
|---|---|---|---|---|
| Congo | Kinshasa (1534) | 1903 to 1983 | 81 of 81 | Mean 40,193 m3/s. April 1903 typo |
| Congo | Brazzaville (947) | 1984 to 2002 | 18 of 19 | Opposite bank of Kinshasa; flagged suspect only for location |
| Niger | Koulikoro, Mali (61) | 1907 to 1990 | 83 of 84 | |
| Niger | Niamey (15) | 1929 to 1991 | 55 of 63 | Mean 901 |
| Niger | Malanville, Benin (1466) | 1976 to 2004 | 19 of 29 | |
| Nile | Aswan Dam (1487) | 1869 to 1984 | 114 of 116 | After 1964 the High Dam controls the flow |
| Nile | Dongola, Sudan (76) | 1912 to 1984 | 73 of 73 | Above Lake Nasser |
| White Nile | Malakal (1226) | 1912 to 1982 | 71 of 71 | |
| Zambezi | Matundo-Cais, Mozambique (1213) | 1976 to 1979 | 4 | Too short |
| Orange | Vioolsdrif (1459) | 1964 to 1986 | 9 of 23 | |
| Volga | Volgograd dam (817) | 1879 to 1984 | 87 of 106 | Dam from 1958 |
| Ob | Salekhard (835) | 1930 to 1984 | 55 of 55 | ArcticGRO is better |
| Yenisei | Igarka (880) | 1936 to 1984 | 49 of 49 | ArcticGRO is better |
| Lena | Kusur/Kyusyur (930) | 1935 to 1984 | 50 of 50 | ArcticGRO is better |
| Amur | Komsomolsk (932) | 1933 to 1984 | 52 of 52 | Source field blank; PointID is in RivDIS |
| Yangtze | Datong (903) | 1976 to 1979 | 4 | Too short |
| Yellow | Sanmenxia (901) | 1976 to 1979 | 4 | Too short |
| Ganges | Farakka, India (863) | 1949 to 1973 | 21 of 25 | |
| Brahmaputra | Bahadurabad (865) | 1969 to 1975 | 5 of 7 | |
| Brahmaputra | Pandu, India (883) | 1956 to 1979 | 8 of 24 | |
| Indus | Attock (849); Kotri (831) | 1973 to 1979 | 7; 4 | Too short |
| Tigris | Baghdad (813); Mosul (812) | 1968 to 1972; 1964 to 1972 | 3; 7 | Too short |
| Euphrates | Keban, Turkey (801) | 1937 to 1972 | 36 of 36 | Before Keban Dam (1974) |
| Irrawaddy | none | | | |

## 2. Other sources

### ArcticGRO (Arctic Great Rivers Observatory)

- Measured. Daily mean discharge, m3/s. [verified]
- Ob at Salekhard (Roshydromet 11801): 1936-01-01 to 2025-12-10. Flag A
  (certified) 1936 to 2008; blank flag 2000 to 2021; P (provisional) 2022 to
  2025; 60 NA days in 2000. [verified]
- Yenisei at Igarka (9803): 1936-01-01 to 2026-01-31. A to 2005; blank 2006
  to 2017; P from 2018; 2,502 NA days, mostly 1963 to 1979. [verified]
- Lena at Kyusyur (3821): 1936-01-01 to 2026-01-17. A to 2021; P from 2012;
  146 days with no value in late 2024 to 2025. [verified]
- Provisional Russian values are estimated by AARI from stage, ice thickness
  and old rating curves, and winter values are revised after the ice goes out
  (June to July). The meaning of a blank flag is not documented. [documented,
  discharge metadata PDF linked from the page]
- Access: open, no login. The data sit inside the page
  https://arcticgreatrivers.org/discharge/ (32 MB HTML) as base64 xlsx files
  named like `Ob_Salekhard_Version_20260810.xlsx`. We decoded all 17 today.
  [verified]
- Version: "Discharge Dataset, Version 20260810"; each update gets a new date
  code and old versions are archived. [verified]
- License: "ArcticGRO data are free to use by anyone for any purpose. We only
  ask that you credit ArcticGRO." https://arcticgreatrivers.org/data/ [verified]
- Volga and Amur are not covered (they do not drain to the Arctic).

### R-ArcticNET v4.0 (University of New Hampshire)

- Measured. Monthly. Pan-Arctic only (no Volga, no Amur). Russian series were
  updated by the State Hydrological Institute to about 1990. [documented,
  http://www.r-arcticnet.sr.unh.edu/v4.0/abstract.html]
- Open text files, no login (`v4.0/AllData/index.html`, `data/Discharge_ms.txt`).
  [verified, index page loaded]
- License: none stated. [unknown]
- Superseded by ArcticGRO for Ob, Yenisei and Lena.

### Russia's water cadastre (AIS GMVO, gmvo.skniivh.ru)

- The site now says it has been taken out of service and moved into a closed
  government system that needs a cryptographic client to enter. [verified]
- No open Volga or Amur discharge after 1984 was found.

### GRDC (Global Runoff Data Centre)

- Measured. Daily and monthly. The main archive for our rivers. Free, through
  a web form, with terms accepted at download. [documented,
  https://grdc.bafg.de/data/data_portal/]
- Terms (exact): "All hydrological data remain property of the owner and are
  released only for research purposes. Commercial use of the original data is
  not allowed. The redistribution of the downloaded data either in part or
  total to unauthorized persons, third parties or to the general public
  (incl. distribution via Internet) is not allowed. Analysis and further
  processing of hydrological data as well as the use of statistical data
  products is permitted with an appropriate reference to the source of data
  as: 'The Global Runoff Data Centre, 56068 Koblenz, Germany'." [verified,
  portal page today]
- Policy guidelines: data users agree "that the data received are not
  transferred to third parties without the written consent of the GRDC," and
  the user declaration forbids transfer "to the general public (e.g. by
  electronic media)." [documented,
  https://grdc.bafg.de/downloads/policy_guidelines.pdf]
- What "no redistribution" covers: the downloaded values themselves, "in
  part or total." Analysis and "statistical data products" are allowed with
  the credit line. Nothing in the terms speaks to charts. Our reading: a
  chart or table that lets a reader recover the monthly or daily values is
  redistribution in part; a published statistic (for example, "the 2023
  annual mean was 12% below the 1961 to 1990 mean") is an allowed analysis.
  Annual means for every year of a record are a gray zone. The terms also say
  "only for research purposes"; journalism is not named. To publish GRDC
  monthly or annual series as a chart, ask GRDC in writing (grdc@bafg.de).
  [interpretation]

### GRDC-Caravan (Farber et al., 2025)

- Measured (GRDC daily data from countries with open licenses), CC BY 4.0.
  Zenodo record 15349031, version 0.6, May 6, 2025. [verified, Zenodo API]
- 5,356 gauges in 25 countries, 1950 to 2023. No Asia. African countries:
  South Africa (434 gauges), Namibia (51), Liberia (9). [verified, from
  `attributes_other_grdc.csv`, read from the 8.8 GB zip by HTTP range request]
- Per-country license table inside the zip: South Africa DWS "Free to use",
  Namibia "Free to use", both "personal communication". [verified]
- Target gauges in it: Orange at Vioolsdrif (GRDC 1159100), 1950-01-02 to
  2023-05-19, 52 complete years; upper Zambezi at Katima Mulilo, Namibia
  (GRDC 1291100), to 2021-06-21, 58 complete years. Also Orange at Upington,
  Prieska, Aliwal North and others. [verified]
- Big quirk: streamflow is stored in mm per day of runoff over the basin,
  rounded to 0.01 mm/day, in both the CSV and netCDF files (73 distinct values
  in the whole Vioolsdrif series; 11,684 days are exactly 0.0). At Vioolsdrif
  (786,037 km2) one step of 0.01 mm/day is about 91 m3/s, and every day below
  about 45 m3/s reads as zero. At Katima Mulilo one step is about 39 m3/s
  against a mean of about 1,249. [verified]
- Caravan starts at 1950 by design, so older GRDC years are cut off.
- Core Caravan and the CAMELS family (US, GB, BR, CL, AUS, CH, IND and
  others) cover small catchments and none of our target mainstems.
  CAMELS-IND covers peninsular India only (no Ganges, Brahmaputra or Indus).
  [documented, https://essd.copernicus.org/articles/17/461/2025/]

### GSIM (Global Streamflow Indices and Metadata)

- Indices (monthly, seasonal, yearly means and extremes) computed from daily
  data for more than 30,000 stations, including GRDC. CC BY-SA 3.0 on
  PANGAEA (doi:10.1594/PANGAEA.887470). [documented]
- Ends around 2016. Built partly from GRDC data under GRDC terms, so the
  republishing status for GRDC-sourced stations is not clear even with the
  PANGAEA license. Not tested. [unknown]

### SIEREM (HydroSciences Montpellier)

- Holds the old ORSTOM archive for Africa (Niger, Congo and others), monthly.
  The data policy says SIEREM "cannot be considered a data provider"; the data
  belong to the national African services, and requests go to them. Metadata
  need registration and a signed user declaration. The site says it had no
  data update in 2025. [verified,
  http://www.hydrosciences.fr/sierem/produits/index.asp?frame=politique]

### Niger Basin Authority (Niger-HYCOS)

- No public download or access policy found. WHYCOS treats data as owned by
  the member countries. Request only. [unknown / documented via WMO HYCOS
  pages]

### SO HYBAM (Congo)

- Publishes research on the Brazzaville-Kinshasa series back to 1902; the new
  site's catalog is a JavaScript app and no download for Congo discharge
  was found. [unknown]

### South Africa DWS (Orange)

- The verified-data service returned HTTP 403 to every request from here,
  including with a browser user agent. [verified, failed]
  `https://www.dws.gov.za/Hydrology/Verified/HyData.aspx?Station=D8H003100&DataType=Daily...`
- License on the DWS site not found. GRDC-Caravan lists DWS data as "Free to
  use". [unknown on DWS site]

### China, Ministry of Water Resources

- Live readings only on the national hydrological information system; no
  historical download. A 2026 ESSD preprint says its authors scraped daily
  values and could not release them because of national data confidentiality
  rules. [documented,
  https://essd.copernicus.org/preprints/essd-2026-426/essd-2026-426-AR1.pdf]
- The annual China River Sediment Bulletin gives annual runoff at main
  stations (Datong, Lijin and others). Annual totals only; license not
  stated; not tested. [unknown]

### India-WRIS / Central Water Commission

- Data for the Indus and Ganga-Brahmaputra-Meghna basins (rivers that flow
  into Pakistan and Bangladesh) are classified. Release is "for specific
  purpose / study only" after user checks and a secrecy undertaking. Current
  rules are in the 2018 Hydro-Meteorological Data Dissemination Policy. The CWC
  PDF returned HTTP 401 today. Not publishable. [documented via 2014 Lok Sabha
  answer and secondary sources; policy PDF unknown]

### Pakistan WAPDA

- Daily Tarbela and Mangla inflows are published in press releases and PMD
  web sheets, one day or one month at a time. No historical archive or
  license found. [documented via PMD sheets; unknown for archive]

### Bangladesh (Brahmaputra at Bahadurabad, Ganges at Hardinge Bridge)

- BWDB discharge needs registration or purchase (from the earlier level
  research). Not tested. [unknown]

### Turkey DSI (Tigris and Euphrates)

- DSI publishes streamflow yearbooks, but no download was found today.
  [unknown]

### DFO River Watch (satellite-based)

- Satellite-derived: passive microwave signal from a 10 km pixel, converted to
  m3/s with a rating built from about 10 years of gauge data or, at most
  sites, from the WBM water balance model (1998 to 2011). So most values are
  "satellite scaled by a model." 335 stations, daily, from about 1998.
  [documented,
  https://floodobservatory.colorado.edu/wiki/DischargeFromSpace_background]
- Old download pages now return 404 while the site moves to a wiki. An older
  DFO page gave the license as CC BY-NC-SA 4.0 (non-commercial). Current
  license and download path unknown. [unknown]

### NASA SWOT (satellite)

- SWOT L2 HR RiverSP, Version D: water surface elevation, slope, width and
  discharge per river reach, from December 2022 (science orbit from mid 2023).
  Passes every 21 days at a given reach, so not daily. Needs a free NASA
  Earthdata login. NASA data are open (CC0 unless marked). [documented,
  https://podaac.jpl.nasa.gov/dataset/SWOT_L2_HR_RiverSP_D] Not tested.
- Too short for a long-record chart.

### GEOGLOWS (modeled)

- Modeled: ERA5 reanalysis run through a routing model, about 7 million
  reaches, daily from January 1, 1940. Retrospective runs to September 30,
  2026 at Kinshasa. [verified,
  `https://geoglows.ecmwf.int/api/v2/retrospectivedaily/<river_id>?format=csv`]
- Access: open REST API, no key.
  `getriverid?lat=&lon=` returns the nearest reach, which is often a small
  side channel: at Kinshasa the nearest reach averaged 15 m3/s. We had to scan
  nearby reaches and take the largest mean. [verified]
- License: CC BY 4.0. [verified, https://registry.opendata.aws/geoglows-v2/]
- Accuracy at our gauges: see the comparison table below.

### GloFAS reanalysis (modeled)

- Modeled. Daily, 1979-01-01 to 2026-10-14, 0.05 degree grid, version 4.0.
  Now served by the Copernicus Early Warning Data Store (EWDS), dataset
  `cems-glofas-historical`; needs a free ECMWF account. [verified, EWDS
  catalog API]
- License: CEMS-FLOODS terms. Users may reproduce, distribute, communicate to
  the public and adapt, with the notice "Generated using Copernicus Emergency
  Management Service information [Year]" (or "Contains modified ..."). Data are
  "for information purposes only." [verified, license PDF linked from the
  catalog]
- Not downloaded (needs account).

## Modeled vs. measured averages (GEOGLOWS)

Method: for each gauge we looked up GEOGLOWS reaches on a grid around the
gauge (`getriverid`), pulled each reach's annual averages (`annualaverages`,
1940 to 2024), and kept the reach with the largest mean. "Measured" is the
mean of all complete months in the measured record named, so the periods
differ; this is a rough check, not a tie-out. The GEOGLOWS service went down
twice during these requests (it returned an ECMWF "Service not available"
page), so some gauges have no model value. [verified, today]

| Gauge | Measured mean m3/s (source, years) | GEOGLOWS mean m3/s, 1940 to 2024 (reach) | Model vs. measured |
|---|---|---|---|
| Congo, Kinshasa | 40,193 (SAGE, 1903 to 1983) | 63,470 (130788370) | 58% higher |
| Niger, Koulikoro | 1,412 (SAGE, 1907 to 1990) | 2,144 (140634171) | 52% higher |
| Niger, Niamey | 901 (SAGE, 1929 to 1991) | 2,844 (140612297) | 216% higher |
| Niger, Malanville | 1,191 (SAGE, 1976 to 2004) | 3,005 (140619693) | 152% higher |
| Nile, Dongola | 2,622 (SAGE, 1912 to 1984) | 21,066 (160434905) | 703% higher |
| Zambezi, Katima Mulilo | 1,249 (GRDC-Caravan, 1950 to 2021) | 4,097 (120726050) | 228% higher |
| Orange, Vioolsdrif | 226 (GRDC-Caravan, 1950 to 2023) | 461 (120527095) | 104% higher |
| Volga, Volgograd | 8,087 (SAGE, 1879 to 1984) | 7,587 (280446356) | 6% lower |
| Ob, Salekhard | 12,917 (ArcticGRO, 1940 to 2024) | 11,823 (310403248) | 8% lower |
| Yenisei, Igarka | 19,735 (ArcticGRO, 1940 to 2024) | 14,689 (320249092) | 26% lower |
| Brahmaputra, Bahadurabad | 18,648 (SAGE, 1969 to 1975 only) | 25,873 (441113702) | 39% higher |
| Indus, Kotri | 2,626 (SAGE, 1973 to 1979 only) | 6,777 (441117829) | 158% higher |
| Lena, Kyusyur | 17,259 (ArcticGRO, 1940 to 2024) | 15,148 (340073882) | 12% lower |
| Amur, Komsomolsk | 9,739 (SAGE, 1933 to 1984) | 11,177 (410731375) | 15% higher |
| Yangtze, Datong | 25,032 (SAGE, 1976 to 1979 only) | 37,167 (420836036) | 48% higher (short measured record) |
| Ganges, Farakka | 12,037 (SAGE, 1949 to 1973) | 16,238 (441076576) | 35% higher |
| Tigris, Baghdad | 1,122 (SAGE, 1968 to 1972 only) | 869 (291285525) | 23% lower |
| Yellow, Lijin | none open | 3,579 (420799941) | not checked |
| Irrawaddy, Pyay | none open | 17,654 (430503252) | not checked |
| Euphrates, Hit | not downloaded | 657 (291222221) | not checked |

The largest gaps are at gauges below big wetlands, reservoirs or irrigation
systems (the Nile below the Sudd, the Niger below its inner delta in Mali,
the Indus at Kotri, the Zambezi below the Barotse floodplain). We did not
test why. The model is closest on the Volga, Ob, Lena and Amur. Plain reading: for
the African and South Asian rivers, GEOGLOWS can at most show whether a year
was wetter or drier than the model's own normal. It should never be placed
on the same axis as measured flow.

## 3. Recommendation by river

Measured, open and current exists only for the three Siberian rivers. For the
rest, the honest options are a measured monthly record that ends decades ago,
or a modeled series that should be labeled as such and, given the biases
above, shown only as change relative to its own average.

| River | Best source and gauge | Type | Time step | Years | License status |
|---|---|---|---|---|---|
| Ob | ArcticGRO, Salekhard (Roshydromet 11801) | Measured (provisional from 2022) | Daily | 1936 to Dec 2025 | Open: "free to use by anyone for any purpose" |
| Yenisei | ArcticGRO, Igarka (9803) | Measured (provisional from 2018; 1963 to 1979 mostly missing) | Daily | 1936 to Jan 2026 | Open |
| Lena | ArcticGRO, Kyusyur (3821) | Measured (certified to 2021; provisional after) | Daily | 1936 to Jan 2026 | Open |
| Orange | GRDC-Caravan, Vioolsdrif (GRDC 1159100) | Measured | Daily, but rounded to about 91 m3/s steps; use monthly means | 1950 to May 2023 | CC BY 4.0 (DWS "free to use"). Better: DWS D8H003 directly, if reachable from a South African connection |
| Zambezi | GRDC-Caravan, Katima Mulilo, Namibia (GRDC 1291100), upper Zambezi only | Measured | Daily (steps of about 39 m3/s) | 1950 to Jun 2021 | CC BY 4.0 (Namibia "free to use"). Nothing open below Victoria Falls or Kariba |
| Congo | SAGE/RivDIS, Kinshasa (1534) then Brazzaville (947) | Measured | Monthly | 1903 to 1983, plus 1984 to 2002 at Brazzaville | No license stated; published openly by UNESCO/RivDIS and CPEP ("freely available"). Nothing open after 2002 |
| Niger | SAGE/RivDIS, Koulikoro (61) for the long view; Niamey (15) 1929 to 1991 | Measured | Monthly | 1907 to 1990 | Same as Congo. Nothing open after 1991 (Malanville to 2004) |
| Nile | SAGE/RivDIS, Dongola (76) 1912 to 1984; Aswan (1487) 1869 to 1984 | Measured | Monthly | 1869 to 1984 | Same as Congo. Nothing open after 1984. GEOGLOWS averages 703% above measured here |
| Volga | SAGE/RivDIS, Volgograd dam (817) | Measured | Monthly | 1879 to 1984 | Same as Congo. Nothing open after 1984 |
| Amur | SAGE/RivDIS, Komsomolsk (932) | Measured | Monthly | 1933 to 1984 | Same as Congo. Nothing open after 1984 |
| Yangtze | No open measured series (SAGE has 4 years). Modeled only: GEOGLOWS at Datong | Modeled | Daily | 1940 to 2026 | CC BY 4.0. China restricts gauge data |
| Yellow | No open measured series (4 years). Modeled only: GEOGLOWS near Lijin | Modeled | Daily | 1940 to 2026 | CC BY 4.0. Model cannot know diversions that dried the delta in the 1990s |
| Ganges | SAGE/RivDIS, Farakka (863) 1949 to 1973; otherwise modeled | Measured, old | Monthly | 1949 to 1973 | Same as Congo. Indian data now classified |
| Brahmaputra | Nothing usable (5 to 15 years in SAGE). Modeled only | Modeled | Daily | 1940 to 2026 | CC BY 4.0 |
| Indus | Nothing usable (7 years). Modeled only, and the model cannot know canal withdrawals | Modeled | Daily | 1940 to 2026 | CC BY 4.0 |
| Irrawaddy | Nothing measured and open. Modeled only | Modeled | Daily | 1940 to 2026 | CC BY 4.0 |
| Tigris | Nothing usable (Baghdad 1968 to 1972). Modeled only | Modeled | Daily | 1940 to 2026 | CC BY 4.0 |
| Euphrates | SAGE/RivDIS, Keban, Turkey (801), before the dams | Measured, old | Monthly | 1937 to 1972 | Same as Congo |

Where the table says "Same as Congo": SAGE and RivDIS state no license.
CPEP says the data are "freely available," UNESCO published RivDIS v1.0, and
NASA hosts v1.1 under its open data policy. No document we found forbids
republishing. We recommend crediting "Vorosmarty, Fekete and Tucker (1998),
RivDIS v1.1, via the UW-Madison SAGE Global River Discharge Database (Coe and
Olejniczak, 1999)" and the national agency where known. An email to SAGE
(webmaster@nelson.wisc.edu) asking for written confirmation would remove the
doubt and costs little.

Recommendation: add flow for Ob, Yenisei and Lena now (measured, daily,
open, current). Add Orange and upper Zambezi as monthly means from
GRDC-Caravan. For the other rivers, show the SAGE/RivDIS monthly record as a
clearly dated historical layer ("measured flow, 1903 to 1983"), and do not
fill the recent decades with model output on the same chart. If a recent
view is needed, use GEOGLOWS as a separate, labeled "modeled" series shown as
percent of its own long-term average, because its absolute values are far
from the measured ones at several of these gauges.

## Draft DATASETS.md sections

### Global River Discharge Database (SAGE, UW-Madison), mostly RivDIS v1.1

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

### Discharge Dataset (Arctic Great Rivers Observatory, ArcticGRO)

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

### GRDC-Caravan extension (Farber et al. 2025, GRDC)

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

### GEOGLOWS retrospective simulation v2 (ECMWF / GEOGLOWS)

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
measured average (table above). Show only as change relative to the model's
own average, labeled modeled.

**License and attribution.** CC BY 4.0. Credit "GEOGLOWS ECMWF Streamflow
Service, retrospective simulation v2."
