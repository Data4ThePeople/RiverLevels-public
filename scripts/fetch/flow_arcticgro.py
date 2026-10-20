"""ArcticGRO (Arctic Great Rivers Observatory) Discharge Dataset: daily mean
discharge, m3/s, measured by Roshydromet, for the Ob at Salekhard, the
Yenisei at Igarka and the Lena at Kyusyur. These are flow-only gauges: we
have no level record there.

The xlsx files are embedded in https://arcticgreatrivers.org/discharge/ as
base64 data URLs (the page is about 32 MB). We cache the page, decode each
file and cache it too, under the name the page gives it (which carries the
version code). The station table (coordinates) is in ArcticGRO's discharge
metadata PDF, linked from the page and cached here as well.

Flags: "A" (certified) is measured; "P" (provisional) is provisional; a blank
flag is provisional too, because the metadata does not explain it. Rows with
no value ("NA" or blank) are dropped and counted.
"""
from __future__ import annotations

import base64
import html
import io
import re

import pandas as pd

from flow_common import write_flow
from sa_asia_common import RAW, fetch_to, parse_args, session

PAGE_URL = "https://arcticgreatrivers.org/discharge/"
META_PDF_ID = "1wy-HWgRQPKEbP16sC2eHq3EWT9v4zJOb"  # "discharge metadata" link on the page
META_PDF_URL = f"https://drive.google.com/uc?export=download&id={META_PDF_ID}"
RAWDIR = RAW / "flow_arcticgro"
LICENSE = ("Free to use: \"ArcticGRO data are free to use by anyone for any purpose. We only ask that you "
           "credit ArcticGRO.\" (https://arcticgreatrivers.org/data/)")
# id, river, file prefix, station code, display name, lat, lon (ArcticGRO discharge metadata PDF,
# updated 2023-02-27, Table 1), river notes
GAUGES = [
    ("ob-salekhard", "ob", "Ob_Salekhard", "11801", "Salekhard", 66.63, 66.60,
     []),
    ("yenisei-igarka", "yenisei", "Yenisei_Igarka", "9803", "Igarka", 67.43, 86.48,
     ["The ArcticGRO sampling site on the Yenisei is not at Igarka; ArcticGRO gives discharge for the station "
      "closest to it (ArcticGRO discharge metadata)."]),
    ("lena-kyusyur", "lena", "Lena_Kyusyur", "3821", "Kyusyur", 70.68, 127.39,
     ["The ArcticGRO sampling site on the Lena is not at Kyusyur; ArcticGRO gives discharge for the station "
      "closest to it (ArcticGRO discharge metadata)."]),
]
FLAG_Q = {"A": "measured", "P": "provisional", "": "provisional"}


def decode(page: str, prefix: str):
    """Return (file name, xlsx bytes) for the file whose download name starts with prefix."""
    m = re.search(re.escape(prefix) + r"_Version_(\d{8})\.xlsx", page)
    if not m:
        raise SystemExit(f"{prefix}: no embedded xlsx found in the page")
    fname = m.group(0)
    j = page.rfind("base64,", 0, m.start())
    end = page.find("&#39;", j)
    return fname, m.group(1), base64.b64decode(page[j + 7:end])


def main():
    args = parse_args(__doc__)
    s = session()
    page_p = fetch_to(s, RAWDIR / "discharge_page.html", PAGE_URL, args.refresh, timeout=600)
    fetch_to(s, RAWDIR / "discharge_metadata.pdf", META_PDF_URL, args.refresh)
    page = page_p.read_text(errors="replace")
    cite = re.search(r"The Arctic Great Rivers Observatory\.\s*(\d{4})\.\s*Discharge\s+Dataset,\s*Version\s*(\d{8})",
                     html.unescape(re.sub(r"\s+", " ", page[max(0, page.find("Suggested Citation")):][:2000])))
    if not cite:
        raise SystemExit("suggested citation not found in the page")
    cite_year, cite_version = cite.groups()
    for gid, river, prefix, code, name, lat, lon, river_notes in GAUGES:
        fname, version, blob = decode(page, prefix)
        if version != cite_version:
            raise SystemExit(f"{gid}: file version {version} differs from the citation's {cite_version}")
        xp = RAWDIR / fname
        if args.refresh or not xp.exists():
            tmp = xp.with_suffix(".xlsx.part")
            tmp.write_bytes(blob)
            tmp.replace(xp)
        raw = pd.read_excel(xp, dtype=str, keep_default_na=False)
        n_rows = len(raw)
        flow = pd.to_numeric(raw["discharge"], errors="coerce")
        nodata = flow.isna()
        nodata_text = raw.loc[nodata, "discharge"].replace("", "(blank)").value_counts().to_dict()
        nodata_months = raw.loc[nodata, "date"].str[5:7].value_counts().sort_index().to_dict()
        nodata_years = raw.loc[nodata, "date"].str[:4].value_counts().sort_index().to_dict()
        ok = raw[~nodata]
        if set(ok["station_code"]) != {code}:
            raise SystemExit(f"{gid}: station codes {set(ok['station_code'])}, expected {code}")
        bad_flags = set(ok["flag"]) - set(FLAG_Q)
        if bad_flags:
            raise SystemExit(f"{gid}: unknown flags {bad_flags}")
        df = pd.DataFrame({"date": pd.to_datetime(ok["date"]), "flow": flow[~nodata],
                           "quality": ok["flag"].map(FLAG_Q)})
        yrs = ok.groupby("flag")["date"].agg(lambda x: f"{x.min()[:4]} to {x.max()[:4]}").to_dict()
        counts = ok["flag"].replace("", "blank").value_counts().to_dict()
        y = ok["date"].str[:4]
        both = sorted({yr for yr in y[ok["flag"] == "A"]} & {yr for yr in y[ok["flag"] == "P"]})
        notes = [
            f"Daily mean flow measured by Roshydromet at {name} (station {code}), published by ArcticGRO in "
            f"{fname} (ArcticGRO Discharge Dataset, Version {version}).",
            "Flow at these Russian gauges is computed from the water level through stage-discharge relations "
            "(rating curves), with winter correction coefficients that depend on water level and ice thickness; "
            "this is how the Arctic and Antarctic Research Institute (AARI) estimates the provisional values "
            "(ArcticGRO discharge metadata). The metadata does not describe the method for certified values.",
            "Winter flows depend on correction coefficients for ice, and provisional winter values are updated "
            "at the end of ice conditions in June or July (ArcticGRO discharge metadata).",
            f"Flags on the days kept: {counts}. Years by flag: "
            f"{ {('blank' if k == '' else k): v for k, v in yrs.items()} } (ArcticGRO).",
            "\"A\" is certified by Roshydromet (measured here) and \"P\" provisional (ArcticGRO discharge metadata)."
            + (" A blank flag is not explained in the metadata, so we mark those days provisional."
               if "blank" in counts else ""),
            f"Dropped {int(nodata.sum())} of {n_rows} rows with no value ({nodata_text}), by year: {nodata_years}; "
            f"by month: {nodata_months} (ArcticGRO).",
            "Values are published to about three significant figures (ArcticGRO).",
        ]
        last_a = y[ok["flag"] == "A"].max()
        early_p = y[(ok["flag"] == "P") & (y <= last_a)].value_counts().sort_index().to_dict()
        if early_p:
            pm = ok.loc[(ok["flag"] == "P") & (y <= last_a) & y.isin(both), "date"].str[5:7]
            notes.append(f"Provisional days in years up to the last certified year ({last_a}), by year: {early_p}. "
                         f"In years that mix both flags ({', '.join(both)}), the provisional days fall mostly in "
                         f"months {sorted(pm.value_counts().head(5).index)} (ArcticGRO).")
        notes += river_notes
        meta = {
            "id": gid, "river": river, "name": name,
            "station_name": f"{ok['river'].iloc[0]} at {ok['station_name'].iloc[0]}", "station_code": code,
            "country": "Russia", "lat": lat, "lon": lon, "same_station": True, "offset_note": "",
            "kind": "river flow", "unit": "m3/s", "daily_stat": "mean",
            "source": f"Arctic Great Rivers Observatory (ArcticGRO), Discharge Dataset, Version {version}; "
                      "data from Roshydromet",
            "source_url": PAGE_URL,
            "license": LICENSE,
            "credit": f"The Arctic Great Rivers Observatory. {cite_year}. Discharge Dataset, Version {version}. "
                      "Data from Roshydromet.",
            "flag_rule": "ArcticGRO flag A (certified) is measured, P is provisional, and a blank flag, which the "
                         "metadata does not explain, is provisional.",
            "notes": notes,
        }
        write_flow(df, meta)


if __name__ == "__main__":
    main()
