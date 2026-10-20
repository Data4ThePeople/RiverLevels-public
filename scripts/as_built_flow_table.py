"""Rewrite the "As built" flow table in research/datasets/40_flow_and_satellite.md from
data/processed/flow/*.json, so the table can never drift from the data (it was hand-typed
until October 20, 2026, when the Kienstock share had gone stale)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "research/datasets/40_flow_and_satellite.md"
HEAD = "| Gauge | Flow station | Kind | Record | Days | Measured / provisional / estimated | Unit |"


def pct(x):
    return f"{100 * x:.0f}%" if round(100 * x) or x == 0 else f"{100 * x:.1f}%"


def main():
    rows = []
    excluded = json.loads((ROOT / "config/rivers.json").read_text()).get("excluded", {})
    for p in sorted((ROOT / "data/processed/flow").glob("*.json")):
        m = json.loads(p.read_text())
        if m["river"] in excluded:
            continue
        import pandas as pd
        q = pd.read_csv(p.with_suffix(".csv"))["quality"].value_counts(normalize=True)
        share = " / ".join(pct(q.get(k, 0.0)) for k in ("measured", "provisional", "estimated"))
        where = "same station" if m["same_station"] else m["offset_note"]
        rows.append(f"| {m['id']} | {m['station_name']} ({where}) | {m['kind']} | {m['first_date']} to "
                    f"{m['last_date']} | {m['n_days']:,} | {share} | {m['unit']} |")
    s = DOC.read_text()
    i = s.index(HEAD)
    j = s.index("\n\n", i)
    s = s[:i] + HEAD + "\n|---|---|---|---|---|---|---|\n" + "\n".join(rows) + s[j:]
    DOC.write_text(s)
    print(f"wrote {len(rows)} rows to {DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
