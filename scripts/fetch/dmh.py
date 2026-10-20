"""Paraguay DMH (Direccion de Meteorologia e Hidrologia, DINAC) river stage at
Asuncion, scraped from the public HTML table at
https://www.meteorologia.gov.py/nivel-rio/vermas_convencional.php?code=2000086218&page=N

The table shows 15 days per page, newest first, about 3,000 pages back to 1904.
Every page is cached in data/raw/dmh/ and the scrape is resumable: rerunning
only fetches pages that are not cached yet. Pages are fetched one at a time
with a pause between them. In October 2026 each page took about 1 second with
this script (a requests session that keeps the site's cookie); with plain curl
the same pages took about 77 seconds. A full scrape took about 90 minutes.
Use --max-minutes to bound a session; --max-minutes 0 rebuilds from cache only.

Because new days are added at the top, page boundaries shift over time. A row
can show up on two cached pages; identical repeats are dropped and a date with
two different values is a hard failure.

The processed file is written only when the cache reaches the oldest page
(a page with no rows), unless --allow-partial is given.

--refresh is ignored for old pages on purpose (the archive does not change);
it only re-downloads page 1.
"""
from __future__ import annotations

import re
import time

import pandas as pd

from sa_asia_common import RAW, get, parse_args, session, write_gauge

URL = "https://www.meteorologia.gov.py/nivel-rio/vermas_convencional.php"
CODE = "2000086218"
RAWDIR = RAW / "dmh"
ROW = re.compile(r"<tr><td[^>]*><span>(\d{2}-\d{2}-\d{4})</span></td><td[^>]*><span>([^<]*)</span>")
LICENSE = ("Paraguay DMH-DINAC public web page; no license stated. Credit Direccion de Meteorologia e "
           "Hidrologia (DMH-DINAC). Clear reuse terms before publishing.")


def extra(p):
    p.add_argument("--max-minutes", type=float, default=30.0, help="stop scraping after this long")
    p.add_argument("--allow-partial", action="store_true", help="write processed file from a partial cache")
    p.add_argument("--pause", type=float, default=0.5, help="seconds between requests")


def page_path(n):
    return RAWDIR / f"asuncion_page_{n:05d}.html"


def parse_page(text):
    return [(d, v) for d, v in ROW.findall(text)]


def scrape(s, args):
    RAWDIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    n = 1
    fetched = 0
    while True:
        p = page_path(n)
        if p.exists() and not (args.refresh and n == 1):
            if not parse_page(p.read_text(encoding="utf-8")):
                return True  # cached end marker
            n += 1
            continue
        if (time.time() - t0) / 60 > args.max_minutes:
            print(f"dmh: stopping after {args.max_minutes} min; {fetched} pages fetched this run, next page {n}")
            return False
        t = time.time()
        r = get(s, URL, params=dict(code=CODE, page=n), pause=args.pause, timeout=300)
        tmp = p.with_suffix(".part")
        tmp.write_text(r.text, encoding="utf-8")
        tmp.replace(p)
        fetched += 1
        rows = parse_page(r.text)
        print(f"dmh: page {n} {len(rows)} rows {rows[0][0] if rows else '-'} "
              f"({time.time() - t:.0f}s)", flush=True)
        if not rows:
            return True
        n += 1


def build(complete, args):
    pages = sorted(RAWDIR.glob("asuncion_page_*.html"))
    recs = []
    for p in pages:
        recs += parse_page(p.read_text(encoding="utf-8"))
    d = pd.DataFrame(recs, columns=["date", "raw"]).drop_duplicates()
    n_rows = len(d)
    d["date"] = pd.to_datetime(d["date"], format="%d-%m-%Y")
    num = d["raw"].str.replace("m", "", regex=False).str.replace(",", ".", regex=False).str.strip()
    d["level"] = pd.to_numeric(num, errors="coerce")
    bad = d["level"].isna()
    n_bad = int(bad.sum())
    d = d[~bad]
    if d["date"].duplicated().any():
        dups = d[d["date"].duplicated(keep=False)].sort_values("date")
        raise ValueError(f"dmh: conflicting values for the same date:\n{dups.head(10)}")
    span = f"{d['date'].min().date()} to {d['date'].max().date()}"
    notes = [
        f"Scraped from {len(pages)} cached HTML pages of the DMH table ({n_rows} distinct rows, {span}).",
        "DMH publishes one 'nivel del dia' per day with no quality flag, so every value is marked measured.",
        f"Dropped {n_bad} rows whose level was not a number." if n_bad else "No non-numeric or fill values found.",
    ]
    if not complete:
        notes.append("PARTIAL: the scrape had not reached the oldest page when this file was built.")
    meta = {
        "id": "paraguay-asuncion", "river": "paraguay", "name": "Asuncion", "country": "Paraguay",
        # coordinates: DMH does not publish them on this page; these are the station coordinates
        # INA's a5 catalog lists for DMH-DINAC station 2000086218 (INA station 157).
        "lat": -25.27207, "lon": -57.64869, "kind": "river",
        "source": "Direccion de Meteorologia e Hidrologia (DMH-DINAC), Paraguay, web table",
        "source_url": f"{URL}?code={CODE}", "station_code": CODE, "unit": "m",
        "datum": "m above the local gauge zero at the Port of Asuncion (zero elevation not published)",
        "daily_stat": "single reading", "license": LICENSE, "notes": notes,
    }
    write_gauge(d[["date", "level"]].assign(quality="measured"), meta, decimals=2)


def main():
    args = parse_args(__doc__, extra)
    s = session()
    complete = scrape(s, args)
    if complete or args.allow_partial:
        build(complete, args)
    else:
        print("dmh: cache incomplete; processed file not written (use --allow-partial)")


if __name__ == "__main__":
    main()
