# Datasets: European river levels

Written 2026-10-15 for the RiverLevels build. One section per source. Fetch
scripts are in `scripts/fetch/`; each gauge's processed JSON repeats the key
notes, a sourced `measurement_history`, and short `public_notes`.

Gauges covered here: rhine-maxau, rhine-kaub, rhine-ruhrort, elbe-dresden,
elbe-magdeburg, elbe-wittenberge (hyd1d + PEGELONLINE); rhine-lobith
(Rijkswaterstaat); danube-hofkirchen, danube-pfelling (GKD Bayern);
danube-kienstock (eHYD); seine-paris, seine-melun (Hub'Eau).

A general trap for all of them: a gauge reading is the water surface measured
against a fixed mark (the gauge zero), usually set below the riverbed. It is
not the depth of the river. Gauge zeros differ from place to place, so levels
cannot be compared between gauges, and a reading can go below zero.

## hyd1d gauging data (Bundesanstalt für Gewässerkunde, BfG)

**What it is.** A data frame shipped with the BfG's hyd1d R package. Each row
is one gauge and one day: `gauging_station`, `date`, and `w`, the daily mean
water level in cm above the gauge zero. It holds 70 federal gauges on the
Rhine and Elbe.

**Where it comes from.** https://hyd1d.bafg.de/downloads/df.gauging_data_latest.RDS,
an R `.RDS` file of about 2.2 MB, no login. Read with `pyreadr`. Package page:
https://cran.r-project.org/package=hyd1d. Help page for the data:
https://hyd1d.bafg.de/reference/df.gauging_data.html. The code repository moved
from GitHub to https://gitlab.opencode.de/bafg-bund/hyd1d in version 0.5.5.

**Version and vintage.** Our copy has HTTP Last-Modified Tue, 11 Aug 2026
04:43 GMT and runs to 2026-08-10 for every gauge. The package (0.5.5, published
2026-08-19) adds one validated year per release; the NEWS file lists validated
imports for 2022, 2023, 2024 and 2025. Between releases a daily job is meant to
append recent days from PEGELONLINE, but this file stopped at August 10, 2026.

**Coverage.** 1960-01-01 to 2026-08-10 for most gauges; Kaub starts
1969-11-01. Our six gauges have no missing days inside that span. The help page
says data from 1960-01-01 to 2025-12-31 "are validated and were queried from
(WISKI7)-database". Days after 2025-12-31 are "continuously collected from"
PEGELONLINE and "are not officially validated." The repository script that
builds those days takes the plain mean of the 15-minute raw values for the day
and rounds it to whole cm (data-raw/daily_pegelonline2gauging_data.R). There
is no gap filling described. We mark 1960 to 2025 as measured and 2026 as
provisional.

**Changes over time.** Gauge zeros are set by the waterway administration.
The values are relative to the gauge zero in force at the time, and the file
carries no record of past zero changes. Our neighbor comparison
(`scripts/fetch/hyd1d_stepscan.py`) compares each gauge with two to four
neighbors on the same river and flags lasting shifts of 15 cm or more. It found
no gauge-zero step at Maxau, Kaub, Ruhrort, Dresden, Magdeburg-Strombrücke or
Wittenberge. As a control it does find the known step of about 100 cm in
November 1979 when Köln is compared with Düsseldorf; the same jump shows at
Bonn and Rees, so Köln, Bonn and Rees should all be left out or corrected.
Shifts that do appear at Magdeburg (20 to 50 cm against Barby and Rothensee)
follow river flow rather than a single date. Maxau's relation to its neighbors
drifts by 10 to 20 cm around 2001 to 2004 and then returns, which looks like
riverbed change, not a datum change.

Riverbed erosion changes what a level means over time:

- Lower Rhine: a federal waterway working group found the official equivalent
  low-water level (GlW) fell by up to 8 cm from 2002 to 2012 at gauges from
  Mainz to Düsseldorf, and that the low-water level at Kaub fell about 45 cm
  since the 1930s at the same flow, even though the bed there is largely rock
  (https://izw.baw.de/publikationen/vzb_dokumente_oeffentlich/0/Frei-fliessende-Rhein_2014.pdf).
  From GlW 2012 to GlW 2022, Düsseldorf and Ruhrort fell 6 cm and Emmerich
  10 cm (https://www.ccr-zkr.org/12030100-en.html). The Ruhrort to Emmerich
  reach also sank from coal and salt mining
  (https://izw.baw.de/publikationen/kolloquien/0/vortrag_luellau.pdf). We did
  not find a sourced rate in cm per year for these gauges.
- Elbe: the bed between Mühlberg and the Saale mouth still drops by up to
  about 2 cm a year in places, and sediment has been added since the
  mid-1990s to slow it
  (https://www.gesamtkonzept-elbe.de/Webs/Projektseite/GkElbe2020/DE/Projekte/Erosionsstrecke/Erosionsstrecke.html).
  The BfG gives up to about 2 cm a year and about 2 m from 1898 to 2004 at the
  worst spots, including near Magdeburg (https://doi.bafg.de/KLIWAS/2014/Kliwas_Binnenelbe.pdf).
  The fastest lowering at gauges from Dresden to Magdeburg, about 3 cm a year,
  came around 1890 to 1904 (https://izw.baw.de/publikationen.php?file=mitteilungsblaetter/0/mb74_Glazik.pdf).

So a record low today and a record low in the 1960s are not the same flow.

**Suppressed, censored or masked values.** None found.

**Missing data.** No missing-value code. No empty values for our six gauges.
The file ends 2026-08-10 and the PEGELONLINE window starts 31 days before
each download, so August 11 to September 14, 2026 is missing. We leave it as a
gap.

**Revisions.** Yes. Raw recent days are replaced each year when the validated
year is imported. We refresh the whole file.

**Units and rounding.** cm above gauge zero. Most values are whole cm; some
years (1994 to 2016) carry decimals. Provisional days are rounded to whole cm.

**Known quirks.** Raw 2026 values are not screened: Schnackenburg (not one of
our gauges) shows 3,361 cm on 2026-06-23, which is impossible. Our six gauges
show no such spikes in 2026 (largest day-to-day change 143 cm at Ruhrort
during the February flood). A HEAD request to the RDS returns HTTP 400; GET
works.

**Uncertainty.** The help page gives no error bars.

**License and attribution.** The package code is GPL (>= 2). We found no data
license for the gauging data. We checked the help page, the hyd1d website
(its imprint link returned 404 on 2026-10-15), the CRAN page, the GitLab
project (no LICENSE file; the API reports `license: None`), the README,
inst/CITATION (which cites Weber et al. 2023, Ecohydrology & Hydrobiology,
doi:10.1016/j.ecohyd.2023.04.001) and REFERENCES.bib ("Provided by
Bundesanstalt für Gewässerkunde, Koblenz, Germany"). No Zenodo or DOI record
for the dataset was found. The 2026 part comes from PEGELONLINE and so is
DL-DE->Zero-2.0, but the license of the validated 1960 to 2025 part is not
stated. **Clear with the BfG (Datenstelle M1) before publishing the validated
series.** Suggested credit meanwhile: "WSV, provided by the Bundesanstalt für
Gewässerkunde (BfG), hyd1d."

## PEGELONLINE REST API v2 (Wasserstraßen- und Schifffahrtsverwaltung des Bundes, WSV)

**What it is.** Live 15-minute water levels for federal waterway gauges. Each
measurement is a timestamp and a value in cm above gauge zero. Station
metadata give coordinates, river km, and the gauge zero.

**Where it comes from.** https://www.pegelonline.wsv.de/webservices/rest-api/v2,
no key. We call `/stations/{number}.json?includeTimeseries=true` and
`/stations/{number}/W/measurements.json?start=P31D`. Docs:
https://www.pegelonline.wsv.de/webservice/dokuRestapi.

**Version and vintage.** API v2; breaking changes get a new URL version. Data
are live. Each of our refreshes saves its pull under a dated file name and all
saved pulls are merged, so the recent record grows with each refresh.

**Coverage.** Only the last 31 days ("Es können Daten für die letzten 31 Tage
bezogen werden"). Our first pull covers 2026-09-14 to 2026-10-15. We keep only
MEZ days (UTC+1, the German hydrological day) with at least 90 of 96
quarter-hour values, so the partial first and last days drop out. All values
are marked provisional.

**Changes over time.** The `gaugeZero` for most WSV gauges is listed as valid
from 2019-11-01, the date the height system switched from DHHN92 to DHHN2016
(https://www.hamburg-port-authority.de/fileadmin/user_upload/Gewaesserkundliche_Information_2020.pdf).
That moved the gauge zero in m NHN by a few millimeters to centimeters but did
not change the readings. Maxau is the exception (valid from 2017-07-18; reason
not found). The help page still says DHHN92, which looks out of date.

**Suppressed, censored or masked values.** None.

**Missing data.** Missing quarter hours are simply absent.

**Revisions.** The 31-day window is raw data and is not revised in the API.
The checked values appear later in hyd1d.

**Units and rounding.** cm, whole numbers. We round daily means to whole cm,
as hyd1d does.

**Known quirks.** Station numbers are not the same as hyd1d names
(Duisburg-Ruhrort 2770010 is RUHRORT in hyd1d). The PEGELONLINE station
remark for Ruhrort says discharge cannot be computed below 120 cm right now.

**Uncertainty.** "Bei den heruntergeladenen Daten handelt es sich um
ungeprüfte Rohdaten ... können Ausreißer, Messfehler oder andere
Unregelmäßigkeiten enthalten." (https://pegelonline.wsv.de/gast/hilfe)

**License and attribution.** DL-DE->Zero-2.0 per the terms of use (Stand
21.05.2024, https://www.pegelonline.wsv.de/gast/nutzungsbedingungen). No
attribution required; we credit "WSV, PEGELONLINE" anyway.

## Waterwebservices / DDL API (Rijkswaterstaat)

**What it is.** Dutch national water data. For Lobith (`lobith.bovenrijn.tolkamer`)
we pull water height (`WATHTE`, ProcesType `meting`) in cm relative to NAP,
the national datum. Each reading carries a quality code
(Kwaliteitswaardecode) and a status (Statuswaarde).

**Where it comes from.** POST to
https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen,
no key, one request per calendar year (161 requests). Docs:
https://rijkswaterstaatdata.nl/waterdata/ and
https://github.com/Rijkswaterstaat/WaterWebservices. Limit: 160,000 readings
per request (about 3 years of 10-minute data). The raw JSON is about 7 to
14 MB per modern year; we store it gzipped (6 MB total).

**Version and vintage.** The current services went live on 5 December 2025.
Data run to the time of the request.

**Coverage.** 1866-01-01 to 2026-10-14, every day present. The API also
returns two readings from January 30 and 31, 1865, which we leave out. Lobith
levels "worden al gemeten sinds 1866" (https://edepot.wur.nl/505109). What a
day means changes:

- 1866 to 1934: one staff-gauge reading a day, usually at 08:40.
- 1935 to 1985: one reading a day from a float gauge chart, read by eye
  (08:40, then 08:00 from the 1950s).
- 1979 to 1987: unchecked hourly chart readings exist alongside the checked
  daily reading; we use the checked daily one. 1986 has only the hourly ones.
- 1987 onward: automatic float gauge, hourly values until 2010, every 10
  minutes from 2011. We average them to a daily mean.

So `daily_stat` is "mixed": 43,800 single-reading days and 14,900 averaged
days. A single morning reading misses peaks inside the day.

**Changes over time.** NAP is checked by precise leveling every 25 to 40
years (https://www.rijkswaterstaat.nl/zakelijk/open-data/normaal-amsterdams-peil/geschiedenis-nap).
A 2005 benchmark correction of about 2 cm in the western Netherlands appears
only in secondary documents; we did not verify it in an RWS source. Gauge
relocations at Lobith: not found. The Rhine bed erosion described above
affects Lobith too: its official equivalent low-water level is 733 cm + NAP
for 2023 to 2031 (https://www.ccr-zkr.org/12030100-en.html).

**Suppressed, censored or masked values.** None.

**Missing data.** 999999999 (or 999999) is the fill code when data are
missing, and quality code 99 marks a gap. We dropped 10 such readings. We drop
days with fewer than 90% of the usual readings for their series (one day:
today's partial day).

**Revisions.** Yes. Status moves from Ongecontroleerd (unchecked) to
Gecontroleerd (checked) to Definitief after periodic checks, including
re-leveling of the station height. No stated delay. We refresh every year.

**Units and rounding.** cm relative to NAP, whole cm per reading; daily means
are rounded to 0.1 cm.

**Known quirks.** Quality codes from the Aquo list
(https://rijkswaterstaatdata.nl/publish/pages/223004/aquo_kwaliteitsoordeelcodes.xlsx):
00 normal; 03 larger spread; 10, 20, 25 interpolated in space and/or time;
50 implausible; 90 deviating value approved after validation; 99 gap. Only 00,
25 and 99 occur at Lobith (7,297 readings with 25). We mark a day estimated if
more than half its readings are 10, 20 or 25 (no day reaches that), and
provisional if any reading is Ongecontroleerd. Provisional days: most of 1986,
parts of 1979 to 1987, and recent months. Two series often overlap in the same
year; the script picks one per day.

**Uncertainty.** Not stated.

**License and attribution.** CC0: "Op de inhoud van de WaterWebservices is de
Creative Commons zero verklaring (CC0) van toepassing." Credit
"Rijkswaterstaat" anyway.

## Gewässerkundlicher Dienst Bayern, GKD (Bayerisches Landesamt für Umwelt)

**What it is.** Bavarian state hydrology portal. Daily values per gauge:
date, daily mean, daily max, daily min, and a check status (Prüfstatus). We use
the daily mean water level in cm above gauge zero for Hofkirchen (10088003) and
Pfelling (10078000) on the Danube. Both gauges are run by the federal waterway
office (WSA Donau MDK).

**Where it comes from.** https://www.gkd.bayern.de, no login and no email
needed. The script POSTs to `/de/downloadcenter/enqueue_download` with
`zr=gesamt` (whole period) and `wertart=tmw` (daily values) and an AJAX header,
then polls the returned token link until it redirects to a zip on
download.gkd.bayern.de (20 to 40 seconds). The zip has one CSV for everything
up to the end of last year, one for this year, one for the current month, and
one for the current, unfinished day (which we skip).

**Version and vintage.** Live database; each file header prints its query
time. Downloaded 2026-10-15.

**Coverage.** Hofkirchen 1925-11-01 to 2026-10-14, Pfelling 1927-04-04 to
2026-10-14, with no missing days. Values through 2025-12-31 are "Geprueft"
(checked); from 2026-01-01 they are "Rohdaten" (raw). Both gauges switch on
the same date, which suggests a yearly check. Daily values are means of all
readings in the day ("Tagesmittelwerte aus allen über einen Tag erfassten
Messwerten").

**Changes over time.** The file states only the current gauge zero (Hofkirchen
299.58 m NHN, Pfelling 308.12 m NHN, both DHHN2016), not past ones. Comparing
the two gauges, the gap between them widens by about 20 cm over 1964 to 1966
at similar flows; we could not tell which gauge changed or why, and flag it.
Barrages upstream (Straubing, Geisling) and riverbed change could affect the
level; dates and effects not found. Hofkirchen sits on the free-flowing stretch
between Straubing and Vilshofen.

**Suppressed, censored or masked values.** None.

**Missing data.** None in our two series. No fill codes seen.

**Revisions.** Raw 2026 values will be replaced when checked. Refresh the
whole series.

**Units and rounding.** cm, published with two decimals but whole numbers in
practice. The download page says ISO 8859-1; the files we got are UTF-8 with
a byte-order mark and decimal commas.

**Known quirks.** "Der Wasserstand entspricht nicht der Wassertiefe! Er
bezieht sich auf den Pegelnullpunkt, der unterhalb der Gewässersohle liegt."
Individual date ranges in the web form are limited to 5 years; "Gesamtzeitraum"
avoids that.

**Uncertainty.** "Rohdaten können Ausreißer bzw. fehlerhafte Werte enthalten."
No error bars given.

**License and attribution.** CC BY 4.0
(https://www.gkd.bayern.de/de/impressum). Required credit: "Datenquelle:
Bayerisches Landesamt für Umwelt, www.lfu.bayern.de".

## eHYD (Hydrographischer Dienst Österreich, BMLUK)

**What it is.** Austria's published hydrology archive. For Kienstock on the
Danube (HZB 207357, run by viadonau) we use "W-Tagesmittel": daily mean water
level in cm above gauge zero.

**Where it comes from.** https://ehyd.gv.at/services/MessstellenExtraData/owf?id=207357&file=2
(daily mean level, a semicolon text file in Latin-1) and `file=1` (station
master data). Coordinates come from https://ehyd.gv.at/services/PegelAktuell/json.
No login.

**Version and vintage.** eHYD holds history only "bis zum aktuell
veröffentlichten Jahrbuch"
(https://www.bmluk.gv.at/themen/wasser/wasser-oesterreich/hydrographie/der-weg-zu-den-daten/Datenbestand_Bezug.html).
The yearbook runs years behind: the 2019 yearbook is dated November 2023.

**Coverage.** 1976-01-01 to 2023-12-31, no missing days. The file ends with a
row dated 2024-01-01 reading "Lücke" (gap). All values come from the checked
yearbook; there is no per-value flag, so all are marked measured.

**Changes over time.** From the station master data: gauge zero 194.00 m above
the Adriatic datum since 1974-01-01 with no change listed; staff gauge read by
hand from 1974; float recorder with paper chart 1976 to 1997, digitized from
1997; pressure sensor with logger from 2002; remote transmission from 2009;
station coordinates updated in 2010 (about 115 m); river km recalculated in
2018. The Altenwörth plant downstream (1976) and Melk plant upstream (1982)
may affect levels; effect not found.

**Suppressed, censored or masked values.** None.

**Missing data.** "Lücke" marks a gap. One at the end of the file.

**Revisions.** Yearbook values are final. New years arrive when a yearbook is
published.

**Units and rounding.** Whole cm.

**Known quirks.** Footnotes say discharge in many months from 1996 to 2023 was
computed "nach ergänzten Wasserständen" (from filled-in water levels), so some
level values were filled, but the level series does not say which days. We
keep them as measured and say so.

**Uncertainty.** Not stated.

**License and attribution.** CC BY 4.0 under Open Government Data Austria, per
the INSPIRE metadata record
(https://inspire-geoportal.ec.europa.eu/srv/api/records/55e494dd-e0af-4806-95d6-86e30dde0504).
We did not find this text on ehyd.gv.at itself. Required credit: "Datenquelle:
ehyd.gv.at", linked to https://ehyd.gv.at.

## Hub'Eau hydrométrie (Office français de la biodiversité / Schapi, data from PHyC)

**What it is.** French national hydrometry API. The `obs_elab` endpoint gives
elaborated daily series. We use HIXnJ, the daily maximum of instantaneous water
height, for Paris-Austerlitz and Melun on the Seine. Each row has the value, a
status, a method and a quality code.

**Where it comes from.** https://hubeau.eaufrance.fr/api/v2/hydrometrie/obs_elab
and `/referentiel/stations`, no key. Docs:
https://hubeau.eaufrance.fr/page/api-hydrometrie. Page size up to 20,000 with
cursor paging.

**Version and vintage.** API v2.0.1. HIXnJ was added 19/06/2025. Elaborated
data were recalculated and reloaded on 18/03/2024.

**Coverage.** Paris-Austerlitz is stitched from four station codes at the same
site, each used only inside its own window, with no overlapping days:
F700000109 (1900 to 1965), F700000110 (1966 to 1973), F700000111 (1974 to
1989), F700000102 (1990 on). All four list the same zero, 25.92 m. Codes 109,
110 and 102 give altimetric system 3 (NGF-IGN69); 111 gives 0 (unknown) with
the same altitude. F700000102 and the flow station F700000103 share 7,501 days
since 2006 with a median difference of 0 mm, which supports one reference. The
code switches fall on January 1, and the API has no value for December 31 and
January 1 at each switch (1965/66, 1973/74, 1989/90), so those two days are
gaps. We applied no
offset. Melun (F447000101) runs 1900 to 2026 but has no values from 1984-01-01
to 2005-10-01.

Status and method by period:

- Paris 1900 to 1989: validated; method "Mesurée" or "Calculée" (measured).
- Paris 1990 to 2019: validated, method "Expertisée" (edited by a
  hydrologist), which we count as measured.
- Paris 2020 on: mostly raw or pre-validated (provisional). Since 2020
  F700000102 is a backup gauge with unvalidated data.
- Melun before 1984: "Donnée corrigée" (corrected, not validated), so
  provisional. This is 83% of the Melun record.

Before 1966 the Paris values come from an observer reading at 7 am, more often
in floods, so the "daily maximum" is often one reading.

**Changes over time.** Reservoirs upstream change low and high water at Paris:
Pannecière (1949), Seine (1966), Marne (1974), Aube (1990). The Suresnes dam
downstream holds the level up until about 3 to 3.3 m at Austerlitz. Melun is
"fortement influencé" by the Vives Eaux dam, especially in the 2016 flood while
it was being rebuilt. Melun's current reference (36.01 m) is valid from
2004-10-01; older references are not listed.

**Suppressed, censored or masked values.** None.

**Missing data.** Missing days are absent. See gaps above.

**Revisions.** Yes; status moves from brute (4) to corrigée (8) to
pré-validée (12) to validée (16) (Sandre list 510), and the 2024 reload shows
whole histories can be recalculated. Refresh everything.

**Units and rounding.** Millimeters ("mm pour les hauteurs d'eau"). We keep mm.
Dates are UTC.

**Known quirks.** Method codes (Sandre list 512,
https://api.sandre.eaufrance.fr/referentiels/v1/nsa/512.json): 0 Mesuré,
4 Reconstitué, 8 Calculé, 10 Expertisé, 12 Interpolation, 14 Estimé,
16 Valeur forcée. We count 0, 8 and 10 as measured, the rest as estimated (none
occur in our data). Quality codes (list 515): 12 Douteuse (doubtful),
16 Non qualifiée, 20 Bonne, 30 Estimée. Doubtful values are kept and counted
in the gauge notes (17 at Paris, 31 at Melun).

**Uncertainty.** Station quality class for the pre-1966 Paris code is 12
(uncertain). No error bars.

**License and attribution.** Not stated. The Hub'Eau pages, the API spec
(`license: {}`), the data.gouv.fr record and HydroPortail's legal notice give
no license. French public data usually fall under Licence Ouverte / Etalab 2.0,
but we could not confirm it for this API. **Clear before publishing.** Credit
"Hub'Eau / HydroPortail".
