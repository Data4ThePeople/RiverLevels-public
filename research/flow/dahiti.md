# DAHITI (DGFI-TUM): research notes for RiverLevels

Research date: October 17, 2026. No account was created. No API key was used.

Labels used below:
- **Verified**: a request made today returned it. URL given.
- **Documented**: the publisher's page or method paper says so. URL given.
- **Unknown**: could not find out without an account, or not stated anywhere I found.

Raw files from today's requests are in
`/private/tmp/claude-501/-Users-ericpachman-PycharmProjects-RiverLevels/de443af6-058d-4eb2-90cd-2b23bdab8cba/scratchpad/dahiti/`
(station lists, `general.jsonl` with one line per target station) and
`.../scratchpad/ex/` (26 example series and their mission tables).

---

## 1. What it is

**Product.** DAHITI is a database of water surface heights for lakes, reservoirs
and rivers measured by radar altimeter satellites. A radar altimeter looks
straight down and times the echo, so it only measures water where its ground
track crosses the water. (Documented,
https://dahiti.dgfi.tum.de/en/products/water-level-altimetry/)

**Other products.** The menu lists surface area, water occurrence and land-water
masks, volume variation, hypsometry, bathymetry, water level from hypsometry,
river discharge, water surface slope and river tides. (Verified, menu on
https://dahiti.dgfi.tum.de/en/1405/)
- Surface area: "for lakes and reservoirs", 210 series worldwide. (Documented,
  https://dahiti.dgfi.tum.de/en/products/surface-area/)
- Discharge: none of the 1,361 river stations on our target rivers has
  discharge. Across all 19,596 stations listed for Africa, Asia and Europe, the
  "Discharge" badge is grayed out on every one. (Verified, station lists at
  https://dahiti.dgfi.tum.de/en/virtual-stations/africa/ , /asia/ , /europe/)
- Water surface slope comes from ICESat-2 (IRIS v2.6, October 2018 to May 2024)
  and is a per-reach average, not a time series. (Documented,
  https://dahiti.dgfi.tum.de/en/products/water-surface-slope/)
- For our rivers, water level is the only usable product.

**Size.** 31,427 water level series worldwide. Africa 3,119, Asia 3,177,
Europe 13,322 (this count includes Russia). (Documented, product page above.)
The public lists I downloaded today show 3,115, 3,167 and 13,314. (Verified.)

**Units and height reference.**
- Meters. (Documented, product page, sample file headers.)
- The heights are "normal heights": the satellite measures height above the
  ellipsoid (a smooth math model of the Earth's shape), and DAHITI subtracts a
  geoid model (a model of where mean sea level would sit under the land) so the
  numbers act like height above sea level. (Documented, Schwatke et al. 2015,
  section 2, https://hess.copernicus.org/articles/19/4345/2015/)
- Geoid model: EIGEN-6C4 for software version 6.0. (Documented, product page.)
  The 2015 paper used EIGEN-6C3stat. Every target station today reports
  software version 8.0 (1,257 of 1,361) or no version (104). (Verified, station
  pages.) Which geoid version 8.0 uses: **unknown**. The product page only
  describes version 6.0.
- Example: Niger station 1405 in Mali ranges from 251.06 m to 255.39 m.
  (Verified, https://dahiti.dgfi.tum.de/en/1405/)

**Virtual station.** A "target" or "virtual station" is the spot where one
satellite track (sometimes two) crosses the river. All measurements along that
crossing on one pass are reduced to one height for that pass. For rivers, each
station lists the mission and pass number it uses; most use a single pass.
(Verified, the "Altimeter Data" table on each station's water level page, for
example https://dahiti.dgfi.tum.de/en/1510/water-level-altimetry/) The 2015
paper says the crossing point can shift by up to 1 km between passes because
the orbit drifts slightly. (Documented, 2015 paper, section 4.3.4.)

**Missions.** The missions seen today in the 26 example stations, with the year
each one's data begins at our stations (Verified, station water level pages and
series dates; cycle lengths Documented in 2015 paper Table 1):

| Mission | Repeat | First data at our stations | Notes |
|---|---|---|---|
| Topex/Poseidon | about 10 days | 1995 | Only 2 points (1995, 1999) at Brahmaputra 318 |
| ERS-2 | 35 days | 1995 | Niger 1525 (Nigeria) has 1995 to 2016 |
| Envisat | 35 days | 2002 | Ends 2010 when its orbit changed |
| Jason-1 | about 10 days | January 2002 | Same track later used by Jason-2, Jason-3, Sentinel-6A |
| Jason-2 | about 10 days | July 2008 | Most long current records start here |
| SARAL/AltiKa | 35 days | 2013 | Same track as Envisat; ends 2016 |
| Sentinel-3A | 27 days | April 2016 | Spacing in our sample is exactly 27.0 days |
| Sentinel-3B | 27 days | late 2018 | Inferred from the cluster of 2018 start dates (not checked per station) |
| Jason-3, Sentinel-6A | about 10 days | continue the Jason-2 track | |
| SWOT (KaRIn) | varies | 2023 | Nile 10185 and many 2023 Nile, Niger, Congo starts |

How many missions are combined: varies by station, from 1 (Orange 11824 uses
only Sentinel-3A) to 5 (Brahmaputra 318). (Verified.) The method is designed to
combine several tracks and missions with a Kalman filter (a method that blends
measurements while weighting each by its stated error). (Documented, 2015
paper, section 3.)

**Time step.** One value per satellite pass, not a fixed calendar step. In our
examples the median spacing is 9.9 days on Jason tracks, 27 days on Sentinel-3,
and 35 days on Envisat/ERS-2. Where two tracks cross the same station the
spacing is shorter (Congo 629: 17.5 days). (Verified, series at
`https://dahiti.dgfi.tum.de/en/<id>/water-level-altimetry/`.)

**Typical uncertainty.**
- Publisher's general statement: "between few centimeters for large lakes and
  few decimeters for small rivers." (Documented, product page.)
- Method paper validation against river gauges in the Amazon: root-mean-square
  differences (a typical size of the error) of 8 to 114 cm for rivers, 4 to 36
  cm for lakes. (Documented, 2015 paper abstract.) The Madeira River case: 19.4
  cm. (Documented, section 4.3.3.)
- Each data point has an "error" or "wse_u" value in meters. (Documented, API
  page https://dahiti.dgfi.tum.de/en/api/doc/v2/download-water-level/ ;
  Verified in the public chart data.) These are formal errors from the filter
  and are far smaller than the real error. Median per-point error in our 26
  examples ranges from 0.3 cm (Brahmaputra 318, Ganges 1569) to 7 cm (Nile
  10185). Some points show 0.000 m. Compare the 8 to 114 cm from the gauge
  comparison. (Verified, then compared with Documented.)

**Outlier removal.** Before the filter: thresholds on latitude (to trim the
track to the river), on height, on along-track scatter, and on radar
backscatter, plus a regression test along each track that drops points that do
not match a flat water surface. After the filter: the same regression test on
the finished time series drops whole passes. The thresholds are set by hand for
each water body. (Documented, 2015 paper, sections 3.1 and 3.3.)

**Ice.** Points affected by ice can be rejected using backscatter (strength of
the radar echo). At Lake Athabasca they kept only echoes between 10 and 18 dB.
(Documented, 2015 paper, sections 3.1 and 4.3.2.) For our Siberian rivers I
found no station-level statement. The series do include winter values: Lena
8877 has 46 January points and Ob 9096 has 54. (Verified.) Whether winter
heights are the water surface or the ice surface: **unknown**. Yenisei 13811
shows January to March medians about 4 m above summer, which could be ice jams
or ice effects; not checked.

**River width limits.** No minimum width is stated. The 2015 paper tested rivers
from about 10 km wide (Amazon) down to "a few hundred metres" (Jiparana), and
says land in the radar footprint is the largest problem for small rivers.
(Documented, 2015 paper, sections 4.1 and 4.3.4.) Exact limit: **unknown**.

**Delay.** Real-time data can give values 1 to 2 days after a pass (Documented,
product page). Our target stations mostly end in late August to early October
2026. (Verified.) The station page for 1405 says last update April 28, 2026,
even though its record ended in 2016. (Verified.)

---

## 2. Access

- **API version 2** at `https://dahiti.dgfi.tum.de/api/v2/<endpoint>/`, GET or
  POST. Endpoints: download-water-level, download-surface-area,
  download-discharge, list-targets, get-target-info, get-nearest-target,
  get-nearest-river, and others. Formats: JSON (default), CSV, ASCII, NetCDF.
  (Documented, https://dahiti.dgfi.tum.de/en/api/doc/v2/)
- **API version 1** was deprecated and set to shut off July 1, 2024.
  (Documented, banner on every page.)
- **Key required.** Every endpoint I tried without a key returned HTTP 403,
  `{"code": 403, "message": "Permission Denied (No `api_key` found!)!"}`.
  (Verified today: list-targets, get-target-info, download-water-level.)
- **How to get a key.** Free registration (name, email, organization, country,
  and a short note on why you want the data), then "My Profile", "Request/Renew
  API-Key". The key is a 64-character hex string. (Documented,
  https://dahiti.dgfi.tum.de/en/register/ and
  https://dahiti.dgfi.tum.de/en/frequently-asked-questions/api-key/)
- **Rate limits.** **Unknown.** Not stated. The FAQ has a hidden, unfinished
  entry about download limits (`/frequently-asked-questions/limit-downloads/`
  returns 404). Station pages were slow today (several seconds each).
- **A ready-made download script** (Python, API v2) is offered.
  (Documented, https://dahiti.dgfi.tum.de/en/tools/scripts/)
- **What is open without an account.** Verified today:
  - Station lists by continent with ID, name, longitude, latitude and which
    products exist: `https://dahiti.dgfi.tum.de/en/virtual-stations/<continent>/`
  - Each station's info page: type, country, period, number of points,
    min/max/average height, software version:
    `https://dahiti.dgfi.tum.de/en/<id>/`
  - Each station's mission and pass table:
    `https://dahiti.dgfi.tum.de/en/<id>/water-level-altimetry/`
  - The chart on that page loads the full series (date, value, uncertainty)
    from `/en/<id>/water-level-altimetry/download/chart/echarts/` with no login.
    I used it to check 27 stations. The site says the data "can be downloaded
    after a short registration process", so a build should not rely on this
    route. Register and use the API.

---

## 3. License and terms

On the registration page, under "Licence" (Verified today,
https://dahiti.dgfi.tum.de/en/register/):

> All data sets provided by "Database for Hydrological Time Series for Inland
> Waters" (DAHITI) are maintained and created by the "Deutsches Geodätisches
> Forschungsinstitut der Technischen Universität München" (DGFI-TUM) and are
> licensed under a Creative Commons Attribution 4.0 License.

The words say "Attribution 4.0", but the link goes to
https://creativecommons.org/licenses/by-nc/4.0/ (Attribution-NonCommercial), and
the badge is the CC BY-NC 4.0 image. The badge itself links to the BY-NC 3.0
page. (Verified, page source.) Read it as **CC BY-NC 4.0**.

Under "Terms of Use" on the same page:

> All products are distributed in the hope that they will be useful, but
> DGFI-TUM provides the data "as is" without warranty, expressed or implied, as
> to the use or appropriateness of the data and products, and there are no
> warranties of merchantability or fitness for a particular purpose or use.
> It is only allowed to use DAHITI products for free by private persons,
> educational institutions and non-profit organizations.
> It is not allowed to use DAHITI products for commercial purposes
> If you are using products of DAHITI for your own work you agree to cite the
> used products as it is described on the associated product page.

**What this means for us.** Republishing values in a public chart is allowed
under CC BY-NC with credit, if the use is not commercial. The terms add that free
use is only for private persons, schools and universities, and nonprofits. If Data 4
The People is run through a company or makes money from posts, ask
DGFI-TUM in writing first. Contact: Christian Schwatke,
christian.schwatke@tum.de (Documented, site footer). Whether a free public
post from a small business counts as "commercial": **unknown**, ask them.

**Citation required** (Documented, product page):
Schwatke C., Dettmering D., Bosch W., and Seitz F.: DAHITI - an innovative
approach for estimating water level time series over inland waters using
multi-mission satellite altimetry. Hydrol. Earth Syst. Sci., 19, 4345-4364,
doi:10.5194/hess-19-4345-2015, 2015.

---

## 4. Coverage for the rivers we lack

Method: I matched station names on the Africa, Asia and Europe lists (with
spelling variants such as Zambesi, Enisey, Huang-he, Yarlung Tsangpo, Padma,
Jamuna, Lualaba, Dicle, Firat), then read each station's info page (1,361
pages). All but one are typed "River"; the one "Reservoir" is the Three Gorges
Dam station on the Yangtze. "Current" means the record ends in 2025 or 2026.
Tributaries were left out except as noted. (Verified today, station pages
`https://dahiti.dgfi.tum.de/en/<id>/`.)

The listed start date can mislead. Brahmaputra 318 is listed from 1995 but has
one point in 1995, one in 1999, and then starts for real in 2008. Nile 10185 is
listed 2002 to 2026 but has no data from mid-2016 to 2023. (Verified, series.)
Treat any "from 2002" record as possibly broken in 2016, when SARAL left the
Envisat track.

| River | Stations (current) | Earliest start (any) | Best long, current station | Its record | Near a city |
|---|---|---|---|---|---|
| Niger | 168 (121) | 1995, ERS-2; 4 stations, end 2010 to 2016 | 1510 Niger, River, Mali (-5.74, 13.76), Jason track 224 | Jan 2002 to Sep 2026, 667 pts | Bamako: 9259, 23 km, 2008 to 2026 (598 pts). Niamey: 48672, 2 km, only from 2023. Nigeria: 1525 near Onitsha, 1995 to 2016 |
| Congo | 116 (85) | 2002, Envisat, ends 2016 | 12370 Congo, River, DRC (21.30, 2.09) | Jul 2008 to Sep 2026, 618 pts | Kinshasa: 33901, 35 km, 2016 to 2026. Mbandaka: 629, 24 km, 2002 to 2016 |
| Nile (main stem 97, Blue Nile 125, White Nile 23) | 245 (234) | 2002 | 10184 Nile, River, Sudan (32.87, 16.51), north of Khartoum | Jul 2008 to Aug 2026, 611 pts | Juba: 967, 8 km, 2008 to 2026 (510 pts). Cairo: nearest 104 km, from 2016. Lake Nasser is a lake target, not counted |
| Zambezi | 59 (56) | 2002, ends 2010 to 2016 | 975 Zambezi, River, Mozambique (33.63, -16.22) | Sep 2008 to Sep 2026, 574 pts | Tete: 975 is 8 km away. Victoria Falls: 16144, 17 km, from 2018 |
| Orange | 28 (28) | April 2016, Sentinel-3A only | 11824 Orange, River, South Africa (26.63, -30.66) | Apr 2016 to Oct 2026, 137 pts, every 27 days | Aliwal North, about 8 km. Upington: 18762, 43 km, from 2018 |
| Volga | 38 (37) | 2002 (1657, ends 2010) | 9178 Volga, River, Russia (49.19, 53.23) | Jul 2008 to Sep 2026, 621 pts | Samara 61 km. Volgograd: 14842, 30 km, from 2016 |
| Ob | 82 (79) | 2002 (13601 Vampugol, gap 2010 to 2016) | 9096 Ob, River (84.87, 52.39), upper Ob near Biysk | Jul 2008 to Sep 2026, 604 pts | Novosibirsk: 15140, 2 km, from 2018. Salekhard: 38663, 11 km, from 2016 |
| Yenisei | 5 (3) | 2002 (1672, ends 2016) | 13811 Yenisey, River (92.06, 58.60) | May 2016 to Oct 2026, 123 pts | About 290 km downstream of Krasnoyarsk. Thin coverage |
| Lena | 28 (23) | 2002, ends 2016 | 8877 Lena, River (128.25, 63.57), downstream of Yakutsk | Jul 2008 to Aug 2026, 492 pts (gap of 595 days) | Yakutsk: nearest 170 km |
| Amur | 81 (81) | 2008 | 9207 Amur, River (127.31, 50.49) | Jul 2008 to Sep 2026, 566 pts | Blagoveshchensk 29 km. Khabarovsk: 16997, 12 km, from 2018 |
| Yangtze | 75 (74) | 2002 (7757 near Zhenjiang, ends 2016) | 9185 Yangtze, River (115.09, 30.26), between Wuhan and Jiujiang | Aug 2008 to Sep 2026, 510 pts | Wuhan: 15723, 15 km, from 2018. 13287 near Jingzhou, 2008 to 2026 |
| Yellow | 35 (32) | 2002, ends 2016 | 1778 Yellow, River (115.17, 35.42), lower river | Jul 2008 to Aug 2026, 628 pts | Zhengzhou: 14174, 25 km, from 2016. Lanzhou: nearest 78 km, from 2019 |
| Mekong (upper, north of 17.5 N) | 43 (21); 3 in China | 2002 | 1422 Mekong, River, Laos (101.76, 19.93) | Feb 2002 to Sep 2026, 634 pts | About 40 km from Luang Prabang, where the MRC gauge is: a direct check is possible. China: 9268 (2008 to 2020), 13824 (2016 to 2026) |
| Ganges | 97 incl. 5 Padma (65) | 1995 (13031, ends 2016) | 1569 Ganges, River, Bangladesh (89.25, 23.93) | Jan 2002 to Sep 2026, 610 pts | Varanasi: 1683, 12 km, 2008 to 2026 (321 pts). Patna: 13062, 7 km, from 2016 |
| Brahmaputra | 71 incl. 27 Yarlung Tsangpo (42) | listed 1995, real 2002 | 319 Brahmaputra, River, India (91.03, 26.21) | Jan 2002 to Sep 2026, 716 pts (not checked for gaps) | About 70 km west of Guwahati. Guwahati: 10861, 13 km, from 2016. Bahadurabad: 10883, 2 km, from 2016 |
| Indus | 55 (38) | 2002, ends 2016 | 3230 Indus, River, Pakistan (68.17, 27.17) | Jul 2008 to Sep 2026, 624 pts | About 70 km southwest of Sukkur. Sukkur: 14582, 2 km, from 2016 |
| Irrawaddy | 37 (26) | 2002 | 12372 Irrawaddy, River, Myanmar (95.82, 21.91) | Apr 2002 to Sep 2026, 580 pts | Mandalay 28 km |
| Tigris | 26 (25) | 2002 (1134, ends 2010) | 12396 Tigris, River, Iraq (43.76, 34.52) | Jul 2008 to Sep 2026, 618 pts | Tikrit about 12 km. Baghdad: 18958, 16 km, from 2018. Mosul: 24487, 8 km, from 2016 |
| Euphrates | 32 (32) | 2008 | 8975 Euphrates, River, Syria (40.94, 34.52) | Jul 2008 to Sep 2026, 625 pts | Near Abu Kamal and Al-Qaim, Syria-Iraq border. Ramadi: 24452, 4 km, from 2016 |

**Compared with the October 15 report.** That report said "satellite from 2016"
for the Yangtze, Yellow, Ganges, Brahmaputra and Indus, and "mostly from 2016 to
2019" for the Volga, Amur, Tigris, Euphrates and Irrawaddy. DAHITI has a
current station starting in mid-2008 on a 10-day Jason track on every target
river except the Orange (2016) and Yenisei (2016). For the Niger, Mekong,
Ganges, Brahmaputra and Irrawaddy it has current stations from early 2002. The
earlier report's "from 2002" for the Congo, Niger and Orange holds for the Congo
and Niger. For the Orange it does not: DAHITI starts there in 2016.

---

## 5. Why satellite level does not match gauge level

1. **Different zero.** DAHITI gives height above a geoid model (roughly sea
   level), in meters. Gauges give height above a local gauge zero. The two
   differ by a fixed amount that is usually unknown. (Documented, 2015 paper,
   section 4.2: "the comparison between water levels from altimetry and in situ
   data over rivers shows in most cases remaining offsets.") Only the ups and
   downs can be compared, not the numbers.
2. **Different place.** "Almost no altimeter satellite track crosses the river
   at the location of a gauging station", and the river's slope adds an offset.
   (Documented, same section.) Two DAHITI stations on one river cannot be
   compared directly either; each is at its own height on the slope.
3. **Sparse sampling.** One value every 10, 27 or 35 days. A flood peak or a
   low that lasts a week can fall between passes. Record highs and lows will be
   missed or understated. Gaps of months to years occur (Verified: maximum gaps
   of 30 days to 9 years in our 26 examples).
4. **Mission changes.** Jumping from one mission to the next, or one tracker
   setting to another, can shift the level. DAHITI corrects mission biases and
   uses one tracker setting per target to avoid this, but says "additional
   retracker offsets will occur". (Documented, 2015 paper, section 2.) Records
   that switch track (Envisat to Sentinel-3 at Ob 13601) mix two crossing
   points, about 2 km or more apart.
5. **Breaks around 2010 and 2016.** Envisat changed orbit in October 2010, and
   SARAL left the same track in 2016. Many "from 2002" records end there or jump
   to a new mission after a gap. (Verified in series; orbit change Documented,
   2015 paper, section 4.3.3.)
6. **Error bars understate the real error.** Per-point errors are a few
   centimeters or less; gauge comparisons show 8 cm to over 1 m on rivers.
7. **Ice.** Winter values exist on Siberian rivers. Whether they are trustworthy
   is unknown.
8. **Reprocessing.** Each file carries a software version, and whole series are
   reprocessed when the software changes (version 6.0 described, version 8.0 in
   use). Whether old values change on reprocessing: **unknown**, but likely.
   Pin a download date.

---

## Draft DATASETS.md section

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

---

## Open questions

- Is Data 4 The People "commercial" under DAHITI's terms? Ask DGFI-TUM.
- API rate limits: not stated.
- Geoid used by software version 8.0: not stated.
- Whether winter values on frozen rivers are reliable: not stated per station.
- Gaps inside the long records for stations not in the 26 examples (for
  example Brahmaputra 319, Niger 1404) were not checked.
