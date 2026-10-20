# Fetch scripts

One script per data source. Each one downloads raw data into
`data/raw/<source>/`, then writes clean daily files into `data/processed/`.
Run with:

```
.uvenv/bin/python scripts/fetch/<source>.py            # uses cached raw files
.uvenv/bin/python scripts/fetch/<source>.py --refresh  # downloads again
```

The raw cache is the fallback for the live demo: every script must rebuild its
processed files from `data/raw/` with no network.

## Output contract (every source)

`data/processed/<gauge_id>.csv`, gauge ids like `rhine-kaub`:

```
date,level,quality
1969-11-01,312.0,measured
```

- `date` is YYYY-MM-DD, one row per day that has a value, sorted. A duplicate
  date is a hard failure (raise, do not drop).
- `level` is in the gauge's native unit as published (cm, ft, m). No
  conversion, no smoothing, no gap filling.
- `quality` is `measured`, `provisional` (raw or not yet approved),
  or `estimated` (the publisher filled or estimated it). Use the publisher's
  own flags; if it has none, `measured` and say so in notes.
- Drop fill values (99999, -999, etc.) and say how many in notes.

`data/processed/<gauge_id>.json`:

```
{
  "id": "rhine-kaub", "river": "rhine", "name": "Kaub", "country": "Germany",
  "lat": 50.0854, "lon": 7.7650, "kind": "river" | "reservoir",
  "source": "BfG hyd1d + PEGELONLINE", "source_url": "...", "station_code": "...",
  "unit": "cm", "datum": "cm above gauge zero (67.669 m NHN)",
  "daily_stat": "mean" | "max" | "single reading" | "mixed (see notes)",
  "first_date": "...", "last_date": "...", "n_days": 0,
  "coverage_by_decade": [{"decade": 1970, "share_days": 0.99,
                          "share_measured": 0.99, "share_estimated": 0.0,
                          "share_provisional": 0.0}],
  "license": "...", "notes": ["..."]
}
```

`coverage_by_decade` shares are of the calendar days in that decade (or the
part of it inside the record), so gaps show up as a share below 1.
