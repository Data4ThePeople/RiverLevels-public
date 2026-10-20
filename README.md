# World River Levels

Daily water level and flow at river gauges around the world, by Data 4 The
People. Live page: https://data4thepeople.github.io/RiverLevels-public/

- The page: `dist/index.html`, built by `scripts/build_viz.py` from
  `viz/template.html`, `config/rivers.json` and `data/processed/`.
- Sources, quality rules and known limits: [DATASETS.md](DATASETS.md).
- Map: Natural Earth coastlines, lakes and rivers, and Natural Earth's 1:50m
  shaded relief (public domain). `scripts/relief.py` reprojects the relief into
  `viz/relief.jpg`, which the page loads after the map draws.
- Fetch scripts: `scripts/fetch/`. Raw downloads are not in this repo; the
  scripts fetch them again.

The Mekong River Commission's data is not included, because its license
requires written permission to republish. The MRC fetch scripts are here,
but their output is not.
