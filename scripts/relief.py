"""Reproject Natural Earth's 1:50m shaded relief (SR_50M, public domain) into the map's Equal Earth
plane and save it as viz/relief.jpg, which build_viz.py embeds and the page draws over the land
with a hard-light blend: mid-gray leaves the land as it is, darker shades it, lighter lights it.
The shading is set here, so the browser only draws one image (no large canvas, which phones cap).

Download once: https://naciscdn.org/naturalearth/50m/raster/SR_50M.zip, unzipped into
data/raw/naturalearth_relief/. The output covers 85N to 60S, the same band the world view shows."""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/raw/naturalearth_relief/SR_50M.tif"
OUT = ROOT / "viz/relief.jpg"
WIDTH = 8000  # output pixels across the world
A1, A2, A3, A4, M = 1.340264, -0.081106, 0.000893, 0.003796, np.sqrt(3) / 2
NORTH, SOUTH = 85.0, -60.0
BLUR = 0  # Gaussian sigma in output pixels; 0 keeps the relief sharp (Eric found a blur too soft when zoomed in)


def proj_y(lat):
    t = np.arcsin(M * np.sin(np.radians(lat)))
    return -t * (A1 + A2 * t**2 + t**6 * (A3 + A4 * t**2))


def blur(a, sigma):
    """Separable Gaussian blur in floating point, edges padded by reflection."""
    r = int(3 * sigma)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    for axis in (0, 1):
        p = np.pad(a, [(r, r) if i == axis else (0, 0) for i in (0, 1)], mode="reflect")
        n = a.shape[axis]
        a = sum(w * (p[i:i + n] if axis == 0 else p[:, i:i + n]) for i, w in enumerate(k))
    return a


def main():
    Image.MAX_IMAGE_PIXELS = None
    src = np.asarray(Image.open(SRC).convert("L"), dtype=np.float32)
    sh, sw = src.shape
    x_max = np.pi / (M * A1)  # proj(180, 0)
    y0, y1 = proj_y(NORTH), proj_y(SOUTH)
    height = round(WIDTH * (y1 - y0) / (2 * x_max))
    xs = np.linspace(-x_max, x_max, WIDTH, endpoint=False) + x_max / WIDTH
    ys = np.linspace(y0, y1, height, endpoint=False) + (y1 - y0) / height / 2
    # invert y = -t(A1 + A2 t^2 + A3 t^6 + A4 t^8) for t by Newton's method
    t = -ys.copy()
    for _ in range(8):
        f = t * (A1 + A2 * t**2 + t**6 * (A3 + A4 * t**2)) + ys
        df = A1 + 3 * A2 * t**2 + t**6 * (7 * A3 + 9 * A4 * t**2)
        t -= f / df
    lat = np.degrees(np.arcsin(np.sin(t) / M))
    df = A1 + 3 * A2 * t**2 + t**6 * (7 * A3 + 9 * A4 * t**2)
    lon = np.degrees(xs[None, :] * M * df[:, None] / np.cos(t)[:, None])
    inside = np.abs(lon) <= 180
    # source grid: 1/30 degree cells, first cell centered at 179.983W, 89.983N
    col = np.clip(((lon + 180) * 30).astype(int), 0, sw - 1)
    row = np.clip(((90 - lat) * 30).astype(int), 0, sh - 1)[:, None].repeat(WIDTH, 1)
    out = src[row, col]
    flat = float(np.bincount(src.astype(np.uint8).ravel()).argmax())  # the tone of level ground
    out[~inside] = flat
    if BLUR:
        out = blur(out, BLUR)
    # one gray layer for the browser's hard-light blend: 128 leaves the land as it is, darker
    # shades it, lighter lights it. Kept light so river lines stay the strongest thing on the map.
    d = out - flat
    g = 128 + np.where(d < 0, np.maximum(-85, 1.6 * d), np.minimum(90, 2.2 * d))
    g[~inside] = 128
    Image.fromarray(np.round(g).astype(np.uint8), "L").save(OUT, quality=85, optimize=True, progressive=True)
    meta = {"x0": float(-x_max), "x1": float(x_max), "y0": float(y0), "y1": float(y1)}
    (ROOT / "viz/relief.json").write_text(json.dumps(meta))
    print(f"wrote {OUT.relative_to(ROOT)} {WIDTH}x{height}, {OUT.stat().st_size / 1e6:.2f} MB; {meta}")


if __name__ == "__main__":
    main()
