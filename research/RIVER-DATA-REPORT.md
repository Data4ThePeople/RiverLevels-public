# River water level data: what we can include

Research date: October 15, 2026. Four research agents checked sources by
making real requests. "Verified" means a request returned data today.
Raw downloads from the research are in the session scratchpad, not the repo.

## The short answer

Long, measured, daily water level records that a script can download today
exist for about 14 major rivers. They cluster in North America, South
America, Europe, Australia and the Mekong. Africa, China, India, Pakistan and
Russia have no open long level records. For those rivers the options are
satellite readings (every 10 to 35 days, mostly from 2002 or 2016), measured
flow instead of level, or modeled flow.

Every gauge reading is a height above a fixed local reference point (the
gauge zero). It is not the depth of the river, and it can go negative. Kaub
on the Rhine read -6 cm on October 1, 2026.

## Recommended rivers (measured, in-situ water level)

| # | River | Best gauges and level record | Source (key needed?) | Story |
|---|---|---|---|---|
| 1 | Rhine | Kaub 1969 to 2026; Lobith (NL) 1866 to 2026; Maxau, Duisburg-Ruhrort, Dusseldorf 1960 to 2026 | BfG hyd1d file + PEGELONLINE (no key); Rijkswaterstaat API (no key) | Freight route, record low in 2026, fuel barge costs |
| 2 | Mississippi | St. Louis 1861; Memphis 1885; Helena 1871; Vicksburg 1901; all to Sep/Oct 2026 | US Army Corps CWMS API (no key) | Grain barges, record lows 2022 to 2024 (Memphis -11.97 ft, Oct 17, 2023) |
| 3 | Ohio | Cairo 1858; Louisville 1875 | CWMS (no key) | Coal and fuel barges, 1937 flood |
| 4 | Colorado (reservoirs) | Lake Mead elevation 1935 to 2026; Lake Powell 1963 to 2026 | Bureau of Reclamation RISE API (no key) | Water for about 40 million people; data shows 2026 lows below 2022 (provisional) |
| 5 | Missouri | Bismarck 1897; Hermann 1922 | USGS, CWMS (no key) | Dam releases set Mississippi barge depth |
| 6 | Fraser | Hope 1912 to Feb 2025 | Environment Canada API (no key) | Salmon, Vancouver flood risk |
| 7 | Amazon / Rio Negro | Manaus 1902 to 2026 (join at 2015); Obidos 1968; Tabatinga 1982; Manacapuru 1972 | Brazil ANA web service (no key) | River highway; record lows 2023 and 2024 |
| 8 | Parana | Rosario 1884 to Oct 14, 2026, no missing years; Corrientes, Parana, Posadas 1901 | Argentina INA API (no key) | Grain exports; 2021 to 2022 low |
| 9 | Paraguay | Ladario 1900 to 2026; Asuncion 1904 to 2026 | ANA (no key); Paraguay DMH (web page scrape) | Landlocked Paraguay's route to sea; 2024 record low |
| 10 | Danube | Hofkirchen 1925 to 2026, no gaps; Pfelling 1927; Kienstock (AT) 1976 to 2023 | Bavarian GKD (no key, CC BY 4.0); Austria eHYD | Shipping, hydropower, Budapest water |
| 11 | Elbe | Dresden, Magdeburg, Wittenberge 1960 to 2026 | BfG hyd1d (no key) | Hamburg shipping; record low at Magdeburg Aug 2026 |
| 12 | Seine | Paris-Austerlitz 1900 to 2026 (daily maximum, four station codes to join) | Hub'Eau API (no key) | Paris water, 1910 flood |
| 13 | Murray-Darling | Albury 1885 to 2026; Swan Hill 1974; Bourke 1972 | Australia BoM API (no key) | Irrigation, Millennium Drought, fish kills |
| 14 | Mekong | Vientiane 1923; Chiang Saen, Pakse, Luang Prabang 1960; Kratie 1933; all to Oct 15, 2026 | Mekong River Commission API (no key, license not open) | Fisheries, upstream dams, 2019 to 2020 lows |

Second tier, usable with limits: Magdalena (Colombia, 1960s to 2026, CC
BY-SA), Red River of the North (1901 to 2026, flood story), Loire and Rhone
(1900s to 2026), St. Lawrence (Montreal 1913 to 2010 plus 2020 on, gap),
Columbia (dam pools from 1960), Oder and Vistula (about 1970s to 2025).

## Rivers with no open long level record

| River | What exists |
|---|---|
| Nile | Flow to 1984 (no republishing allowed); Lake Nasser satellite from 1992; Roda Nilometer yearly lows 622 to 1284 AD (downloadable) |
| Congo, Niger, Orange | Flow only, mostly ending decades ago; satellite from 2002 |
| Zambezi | Lake Kariba satellite every 10 days from 1992 (needs free account, not tested) |
| Yangtze, Yellow | China publishes live readings only; satellite from 2016 |
| Ganges, Brahmaputra, Indus | India restricts the data; Bangladesh needs registration; satellite from 2016 |
| Ob, Yenisei, Lena | Measured flow 1936 to 2026 (open); no level |
| Volga, Amur, Tigris, Euphrates, Irrawaddy | Satellite only, mostly from 2016 to 2019 |

The main global flow archive (GRDC) forbids republishing its raw values, so
it can only be used as a check.

## Caveats that affect the build

1. Gauge zeros are local, so levels cannot be compared between gauges. The
   cross-section should show each gauge against its own range (its record
   low to its record high), not as a depth.
2. Gauge zeros move. Koln has an uncorrected step of about 1 m on
   November 1, 1979. Linz moved in 1939 and 1959. Leave out or correct.
3. Riverbeds wear down. On the lower Rhine, low-water readings have dropped
   for decades at the same flow. Kaub is the most stable Rhine gauge.
4. Dams. Much of the Colorado, Columbia, Upper Mississippi and Missouri is a
   chain of reservoirs. Several Parana and Murray gauges sit below dams.
5. Data ends at different dates. Army Corps public data lags about a month
   (mid-September 2026). The BfG Rhine file ends August 10, 2026, and the
   live German feed only holds the last 31 days, so August 11 to
   September 13, 2026 at Kaub is not covered yet.
6. Possibly filled years. Cambodian Mekong gauges (Kratie, Stung Treng) show
   complete daily values for 1975 to 1979 with no flag. Treat as likely
   filled.
7. Licenses. Clear before publishing: Mekong River Commission (not open),
   BfG hyd1d (no data license stated), Argentina INA, Brazil ANA and
   Paraguay DMH (not stated). Open: USGS, Army Corps, Reclamation (public
   domain), Environment Canada (OGL), Bavaria (CC BY 4.0), Colombia (CC
   BY-SA), Australia BoM (CC BY), PEGELONLINE (DL-DE Zero).

## The Rhine and diesel question

What the data shows: Kaub fell below 78 cm on July 10, 2026, reached a
daily mean of 16 cm on August 10 (below the October 2018 record of 25 cm),
went negative for the first time on record in late September, and read
-6 cm on October 1. The industry treats 78 cm as the point where barges
load much lighter, and about 40 cm as the point where many stop being worth
running.

What is documented: oil-product barge rates at their highest since tracking
began in 2012 (Argus, July 30, 2026); freight from the Dutch ports to
Karlsruhe about 10 times January's rate (Platts, October 7, 2026); Swiss
heating oil up 8% in September. In 2018 Germany released federal fuel stocks
for the southern states.

What is not documented: that the Rhine is a main driver of Europe-wide diesel
prices in 2026. The trade press names Middle East supply disruption, the
Russian export ban and low European stocks first, and calls the Rhine a
compounding factor for inland regions.
