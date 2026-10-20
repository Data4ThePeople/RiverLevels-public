# Flow (discharge) fetch contract

One script per publisher, named `scripts/fetch/flow_<publisher>.py`. Each
downloads raw responses into `data/raw/flow_<publisher>/`, then calls
`flow_common.write_flow(df, meta)` once per gauge, which validates and writes
`data/processed/flow/<id>.csv` (`date,flow,quality`) and `<id>.json`.
Background and API details: `research/flow/existing-gauges.md` and
`research/flow/global-sources.md`; limits: `DATASETS.md`, "Flow (discharge)
and satellite levels".

## Rules

- Run from the project root: `.uvenv/bin/python scripts/fetch/flow_<x>.py`,
  `--refresh` to download again. Use `session()` from one of the
  `*_common.py` helpers (it records the download date for the partial-day
  rule). With the raw cache present, no network calls.
- Save every raw response unparsed before parsing it; write to `.part`, then
  rename.
- One value per calendar day, in the unit as published (`cfs`, `m3/s`,
  `L/s`). No conversion, no smoothing, no gap filling. Where the publisher
  gives several values a day, take the plain mean of the day and set
  `daily_stat` to `mean` (or `mixed` if early years have one reading).
- `quality`: `measured`, `provisional` (raw, unapproved) or `estimated`
  (publisher says estimated or filled, including USGS "e" and ice-estimated
  days). If the publisher has no flags, use `measured` and say so in
  `flag_rule`. Drop missing and fill values and say how many in `notes`.
- Never join two stations into one series. One gauge, one station.
- `id` is the level gauge id it sits beside, or a new `<river>-<place>` id
  for a flow-only gauge.

## meta fields (all required, exact types; write_flow rejects anything else)

| Field | Type | Meaning |
|---|---|---|
| id | str | level gauge id (e.g. `mississippi-stlouis`) or new flow-only id (`ob-salekhard`) |
| river | str | river id in `config/rivers.json` (`ob`, `yenisei`, `lena` for the new ones) |
| name | str | display name of the gauge it sits beside (e.g. `Albury`) |
| station_name | str | the flow station's own name as the publisher gives it |
| station_code | str | publisher's station/series code |
| country | str | |
| lat, lon | float | the flow station's coordinates, WGS84 |
| same_station | bool | true if the flow is measured at the level gauge itself |
| offset_note | str | "" when same_station; otherwise plain words, e.g. `Doctors Point, 4 km downstream` |
| kind | str | `river flow` or `dam release` |
| unit | str | `cfs`, `m3/s` or `L/s` |
| daily_stat | str | `mean`, `one reading` or `mixed` |
| source | str | publisher and product |
| source_url | str | base URL actually called |
| license | str | |
| credit | str | |
| flag_rule | str | one or two sentences: publisher codes to measured/provisional/estimated |
| notes | list[str] | plain sentences for readers, each naming its source in parentheses: how flow is computed (rating curve), ice, dams, the offset station, dropped values |

write_flow adds `first_date`, `last_date`, `n_days`, `coverage_by_decade`.

## Example

```python
meta = {"id": "murray-albury", "river": "murray-darling", "name": "Albury",
        "station_name": "Murray River at Doctors Point", "station_code": "409017",
        "country": "Australia", "lat": -36.12, "lon": 146.93, "same_station": False,
        "offset_note": "Doctors Point, 4 km downstream", "kind": "river flow",
        "unit": "m3/s", "daily_stat": "mean",
        "source": "Bureau of Meteorology, Water Data Online (KiWIS API)",
        "source_url": "https://www.bom.gov.au/waterdata/services", "license": "CC BY 4.0",
        "credit": "Bureau of Meteorology; data from WaterNSW",
        "flag_rule": "BoM codes A and B are measured, C estimated, E measured before 1991 and provisional from 1991 on; F dropped.",
        "notes": ["Albury's own flow record stops in 1952, so this is Doctors Point, 4 km downstream (BoM)."]}
write_flow(df, meta)   # df: date, flow, quality
```

## Assignments

| id | Publisher script | Station / series |
|---|---|---|
| mississippi-stlouis | flow_usgs | USGS 07010000, 00060 daily mean |
| mississippi-memphis | flow_usgs | USGS 07032000 |
| mississippi-helena | flow_usgs | USGS 07047970 (ends 1977) |
| ohio-louisville | flow_usgs | USGS 03294500 |
| ohio-cairo | flow_usgs | USGS 03612600 Olmsted, about 17 river miles upstream |
| ohio-cincinnati | flow_usgs | USGS 03277200 Markland Dam, about 61 river miles downstream |
| missouri-bismarck | flow_usgs | USGS 06342500 |
| missouri-hermann | flow_usgs | USGS 06934500 |
| mississippi-vicksburg | flow_cwms | `MVK:Vicksburg.Flow.Inst.1Day.0.DCP-rev` |
| colorado-lake-powell | flow_rise | RISE item 4315, total release (kind `dam release`) |
| colorado-lake-mead | flow_rise | RISE item 6125, total release (kind `dam release`) |
| fraser-shelley | flow_eccc | 08KB001 |
| fraser-hope | flow_eccc | 08MF005 |
| fraser-mission | flow_eccc | 08MF005 Hope, 68 km upstream |
| rhine-lobith | flow_rws | RWS Grootheid Q |
| danube-pfelling | flow_gkd | GKD fluesse.abfluss 10078000 |
| danube-hofkirchen | flow_gkd | GKD fluesse.abfluss 10088003 |
| danube-kienstock | flow_ehyd | eHYD 207357 file=5 |
| seine-paris | flow_hubeau | QmnJ, same station chain as level (F700000109/110/111/102); F700000103 not joined |
| murray-albury | flow_bom | 409017 Doctors Point, 4 km downstream |
| murray-swanhill | flow_bom | ts 286638010 |
| murray-euston | flow_bom | ts 286878010 |
| darling-bourke | flow_bom | ts 169509010 |
| amazon-tabatinga | flow_ana | 10100000, tipoDados=3 |
| amazon-manacapuru | flow_ana | 14100000 |
| amazon-obidos | flow_ana | 17050001 |
| parana-corrientes | flow_ina | INA 26616 |
| parana-parana | flow_ina | INA 26626 |
| parana-rosario | flow_ina | INA 26631 |
| parana-posadas | flow_ina | INA 26611 (ends 2017) |
| mekong-chiangsaen | flow_mrc | MRC discharge series |
| mekong-pakse | flow_mrc | MRC discharge series |
| mekong-kratie | flow_mrc | MRC discharge series (hourly copies of the daily value: keep one) |
| mekong-vientiane | flow_mrc | Nong Khai 012001, 13 km downstream |
| ob-salekhard | flow_arcticgro | ArcticGRO Ob at Salekhard (flow only) |
| yenisei-igarka | flow_arcticgro | ArcticGRO Yenisei at Igarka (flow only) |
| lena-kyusyur | flow_arcticgro | ArcticGRO Lena at Kyusyur (flow only) |

No flow: Manaus, Ladário, Asunción, and the six German federal gauges
(Maxau, Kaub, Ruhrort, Dresden, Magdeburg, Wittenberge).
