"""Concatenate research/datasets/*.md into DATASETS.md at the project root.

Region files start with a level-1 title; it becomes a level-2 heading and
each source section drops one level.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parts = []
for f in sorted((ROOT / "research/datasets").glob("*.md")):
    text = f.read_text().rstrip() + "\n"
    if f.name.startswith("00_"):
        parts.append(text)
        continue
    out = []
    for line in text.splitlines():
        if line.startswith("# "):
            line = "## " + line[2:].replace("Datasets: ", "")
        elif line.startswith("## "):
            line = "### " + line[3:]
        out.append(line)
    parts.append("\n".join(out) + "\n")
(ROOT / "DATASETS.md").write_text("\n".join(parts))
print("wrote DATASETS.md")
