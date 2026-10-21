"""Animated GIF of the Kaub chart (posts/world-river-levels/images/01-kaub.png) for social posts.

2018, 2022 and 2026 draw in together from July 1 to October 31 over about eight seconds, then the
finished chart holds. Same data, colors and labels as kaub() in post_charts.py. Labels show only
real daily readings, never a value between two days.

    python scripts/animate.py [seconds] [hold_seconds]
"""
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from post_charts import (FILL, INK, INK_DIM, LEVEL, MUTED, ROOT, SURFACE, THRESH, ap, credit, grid_y, load,
                         titleblock)

OUT = ROOT / "posts/world-river-levels/social"
SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
HOLD = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
FRAME_MS = 80            # GIF timing is in hundredths of a second
WIDTH_PX = 1200
YEARS = [(2018, MUTED, 1.4, 2), (2022, INK_DIM, 1.4, 2), (2026, LEVEL, 2.4, 4)]


def series(d, yr):
    s = d[(d["date"] >= f"{yr}-07-01") & (d["date"] <= f"{yr}-10-31")].set_index("date")["v"]
    s = s.reindex(pd.date_range(f"{yr}-07-01", min(pd.Timestamp(f"{yr}-10-31"), s.index.max())))
    x = np.array([mdates.date2num(t.replace(year=2000)) for t in s.index])
    return s, x


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = load("rhine-kaub")
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=WIDTH_PX / 10)
    fig.subplots_adjust(left=0.08, right=0.80, top=0.80, bottom=0.12)
    for yv, lab in [(150, "150 cm: about\nwhat a full\nload needs"), (77, "77 cm: official\nlow-water\nmark"),
                    (40, "40 cm: many\nbarges find it\nuneconomical")]:
        ax.axhline(yv, color=THRESH, lw=1.1, ls=(0, (4, 3)), zorder=3)
        ax.text(pd.Timestamp("2000-11-09"), yv, lab, color=THRESH, fontsize=9, va="center", ha="left", clip_on=False)
    ax.set_xlim(pd.Timestamp("2000-07-01"), pd.Timestamp("2000-10-31"))
    ax.set_ylim(-40, 270)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%B"))
    ax.set_ylabel("cm above the gauge zero", color=INK_DIM)
    grid_y(ax)
    titleblock(fig, "The Rhine at Kaub fell to its lowest level on record this fall",
               "Daily water level at Kaub, Germany, July 1 to October 31, in centimeters above the gauge zero.\n"
               "Not the depth of the river. The daily record starts in 1969. 2026 readings are provisional.")
    credit(fig, "Source: German Federal Waterways and Shipping Administration (PEGELONLINE) and Federal Institute of "
                "Hydrology (BfG).\nLines: 150 cm, Reuters (Aug. 24, 2026); 77 cm, CCNR equivalent low water level for 2023 to "
                "2031; 40 cm, Bloomberg (Aug. 15, 2022).")

    ss = []
    for yr, color, lw, z in YEARS:
        s, x = series(d, yr)
        line, = ax.plot([], [], color=color, lw=lw, zorder=z)
        tip = ax.annotate("", (x[0], 0), xytext=(5, 0), textcoords="offset points", color=INK if yr == 2026 else color,
                          fontsize=10.5, va="center", annotation_clip=False, zorder=7)
        ss.append(dict(yr=yr, s=s, x=x, y=s.values, line=line, tip=tip, color=color))
    s26 = ss[2]
    dot = ax.scatter([], [], s=40, color=LEVEL, zorder=5, edgecolor=SURFACE, linewidth=1.5)
    gap = s26["s"][s26["s"].isna()]
    gx = [mdates.date2num(t.replace(year=2000)) for t in gap.index]
    gap_text = ax.annotate(f"2026: no published\nreadings, {ap(gap.index[0])}\nto {ap(gap.index[-1])}",
                           (gx[len(gx) // 2], -36), color=INK_DIM, fontsize=9.5, ha="center", va="bottom", visible=False)
    lo = d.loc[d["v"].idxmin()]
    lox = mdates.date2num(lo["date"].replace(year=2000))
    lo_dot = ax.scatter([lox], [lo["v"]], s=30, color=INK, zorder=6, visible=False)
    lo_text = ax.annotate(f"Record low: {lo['v']:.0f} cm on {ap(lo['date'])}, {lo['date'].year}", (lox, lo["v"]),
                          xytext=(0, -12), textcoords="offset points", color=INK, fontsize=10, ha="center", va="top",
                          visible=False)
    clock = ax.text(0.02, 0.95, "", transform=ax.transAxes, color=INK_DIM, fontsize=15, fontweight="bold",
                    ha="left", va="center")
    x0, x1 = mdates.date2num(pd.Timestamp("2000-07-01")), max(s["x"][-1] for s in ss)

    def draw(cursor, final=False):
        for s in ss:
            keep = s["x"] <= cursor
            s["line"].set_data(s["x"][keep], s["y"][keep])
            seen = np.where(keep & ~np.isnan(s["y"]))[0]
            tip = s["tip"]
            if not len(seen):
                tip.set_text("")
                continue
            i = seen[-1]
            done = i == len(s["y"]) - 1 or s["x"][-1] <= cursor
            if final and s["yr"] == 2022:   # the static chart labels 2022 at its peak
                j = int(np.nanargmax(s["y"]))
                tip.xy = (s["x"][j], s["y"][j]); tip.set_text("2022")
                tip.set_position((0, 6)); tip.set_ha("center"); tip.set_va("bottom")
            elif s["yr"] == 2026:
                tip.xy = (s["x"][i], s["y"][i])
                tip.set_position((8, -2))
                when = ap(s["s"].index[i])
                tip.set_text(f"2026: {s['y'][i]:.0f} cm\non {when}")
                dot.set_offsets([[s["x"][i], s["y"][i]]])
            else:
                tip.xy = (s["x"][i], s["y"][i])
                tip.set_text(str(s["yr"]) if (final or done) else f"{s['yr']}: {s['y'][i]:.0f} cm")
        gap_text.set_visible(final or cursor >= gx[-1])
        low = final or cursor >= lox
        lo_dot.set_visible(low); lo_text.set_visible(low)
        day = mdates.num2date(min(cursor, x1))
        clock.set_text("" if final else f"{day:%B} {day.day}")
        fig.canvas.draw()
        return Image.frombuffer("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB").copy()

    n = int(round(SECONDS * 1000 / FRAME_MS))
    frames = [draw(x0 + (x1 - x0) * i / (n - 1)) for i in range(n)]
    last = draw(x1, final=True)
    plt.close(fig)

    # One palette, taken from the finished chart, so colors do not shimmer between frames.
    pal = last.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames] + [pal]
    path = OUT / "01-kaub.gif"
    q[0].save(path, save_all=True, append_images=q[1:], duration=[FRAME_MS] * n + [int(HOLD * 1000)], loop=0,
              optimize=False, disposal=1)
    last.save(OUT / "01-kaub-final-frame.png")
    print(f"{path.name}: {len(q)} frames, {last.size[0]}x{last.size[1]}, {n * FRAME_MS / 1000:.1f}s + {HOLD:.0f}s hold, "
          f"{path.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
