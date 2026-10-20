"""Build simplified map geometry for the viz from Natural Earth (public domain).

Reads data/raw/naturalearth/*.geojson and config/rivers.json, writes
data/build/geo.json: land outlines, lakes, and one polyline set per river.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NE = ROOT / "data/raw/naturalearth"
OUT = ROOT / "data/build/geo.json"


def dp(points, tol):
    """Douglas-Peucker line simplification (iterative)."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        norm = (dx * dx + dy * dy) ** 0.5 or 1e-12
        best, idx = 0.0, None
        for i in range(a + 1, b):
            px, py = points[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / norm
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(points, keep) if k]


def dp_ring(ring, tol):
    """Simplify a closed ring by splitting it in two, since its ends coincide."""
    h = len(ring) // 2
    return dp(ring[: h + 1], tol)[:-1] + dp(ring[h:], tol)


def parts(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return c
    if t == "Polygon":
        return c
    if t == "MultiPolygon":
        return [ring for poly in c for ring in poly]
    raise ValueError(t)


def span(ring):
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def rnd(line):
    out = []
    for x, y in line:
        p = [round(x, 2), round(y, 2)]
        if not out or out[-1] != p:
            out.append(p)
    return out


def clip(line, rule):
    """Split a line where it crosses a latitude; keep runs on the wanted side."""
    if not rule:
        return [line]
    lat, side = rule["lat"], rule["keep"]
    runs, cur = [], []
    for p in line:
        ok = p[1] > lat if side == "north" else p[1] <= lat
        if ok:
            cur.append(p)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def main():
    rivers_cfg = json.loads((ROOT / "config/rivers.json").read_text())
    feats = json.loads((NE / "ne_10m_rivers_lake_centerlines.geojson").read_text())["features"]
    by_num = {}
    for f in feats:
        by_num.setdefault(f["properties"]["rivernum"], []).append(f)

    rivers = {}
    for r in rivers_cfg["rivers"] + rivers_cfg["no_data"]:
        lines = []
        for sel in r["geometry"]:
            hits = by_num.get(sel["rivernum"], [])
            if not hits:
                raise SystemExit(f"{r['id']}: no Natural Earth feature with rivernum {sel['rivernum']}")
            for f in hits:
                for line in parts(f["geometry"]):
                    for run in clip(line, sel.get("clip")):
                        s = rnd(dp(run, 0.02))
                        if len(s) > 1:
                            lines.append(s)
        rivers[r["id"]] = lines

    land = []
    for f in json.loads((NE / "ne_50m_land.geojson").read_text())["features"]:
        for ring in parts(f["geometry"]):
            s = rnd(dp_ring(ring, 0.1))
            if len(s) > 3 and span(s) > 0.6:
                land.append(s)

    lakes = []
    for f in json.loads((NE / "ne_50m_lakes.geojson").read_text())["features"]:
        if f["properties"].get("scalerank", 9) > 1:
            continue
        for ring in parts(f["geometry"]):
            s = rnd(dp_ring(ring, 0.05))
            if len(s) > 3 and span(s) > 0.5:
                lakes.append(s)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"land": land, "lakes": lakes, "rivers": rivers}, separators=(",", ":")))
    n = sum(len(l) for v in rivers.values() for l in v)
    print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size/1e3:.0f} KB, {len(land)} land rings, "
          f"{len(lakes)} lakes, {len(rivers)} rivers ({n} river points)")


if __name__ == "__main__":
    main()
