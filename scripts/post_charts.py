"""Static charts for posts/world-river-levels, drawn from data/processed only.

House style follows the Data 4 The People dark charts (Sulfur project plot_style.py):
surface #181A1B, ink #BBBDC0. Level is the page's dark-mode blue, flow its dark-mode orange,
thresholds its dark-mode red. Other years are gray, so no chart relies on more than one hue.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data/processed"
OUT = ROOT / "posts/world-river-levels/images"

SURFACE, INK, INK_DIM, MUTED, GRID = "#181A1B", "#BBBDC0", "#8A9098", "#6B7178", "#2A2D2F"
LEVEL, FLOW, THRESH, FILL = "#3987e5", "#e08a1e", "#e66767", "#26292b"
CREDIT = "Built by Data 4 The People"

mpl.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK_DIM, "ytick.color": INK_DIM,
    "axes.edgecolor": GRID, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.grid": False, "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11, "text.parse_math": False, "figure.dpi": 160, "savefig.dpi": 160,
})


def ap(t):
    """AP-style short date: Oct. 14, Sept. 15, May 3."""
    m = {1: "Jan.", 2: "Feb.", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "Aug.", 9: "Sept.",
         10: "Oct.", 11: "Nov.", 12: "Dec."}[t.month]
    return f"{m} {t.day}"


def long_date(t):
    return f"{t:%B} {t.day}"


def titleblock(fig, title, subtitle, y=0.965):
    fig.text(0.03, y, title, color=INK, fontsize=17, fontweight="bold", va="top", ha="left")
    fig.text(0.03, y - 0.36 / fig.get_figheight(), subtitle, color=INK_DIM, fontsize=11, va="top", ha="left",
             linespacing=1.45)


def credit(fig, source):
    fig.text(0.03, 0.02, source, color=MUTED, fontsize=8.5, ha="left", va="bottom", linespacing=1.4)
    fig.text(0.97, 0.02, CREDIT, color=MUTED, fontsize=8.5, ha="right", va="bottom")


def grid_y(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)


def load(gid, flow=False):
    d = pd.read_csv(PROC / ("flow" if flow else "") / f"{gid}.csv", parse_dates=["date"])
    return d.rename(columns={"flow": "v", "level": "v"})


def annual_min(d, min_days=330, keep_last=True):
    d = d.assign(y=d["date"].dt.year)
    a = d.groupby("y")["v"].agg(["size", "min"])
    last = a.index.max()
    return a[(a["size"] >= min_days) | ((a.index == last) & keep_last)]["min"]


def kaub():
    d = load("rhine-kaub")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.08, right=0.80, top=0.80, bottom=0.12)
    for yr, color, lw, z in [(2018, MUTED, 1.4, 2), (2022, INK_DIM, 1.4, 2), (2026, LEVEL, 2.4, 4)]:
        s = d[(d["date"] >= f"{yr}-07-01") & (d["date"] <= f"{yr}-10-31")].set_index("date")["v"]
        s = s.reindex(pd.date_range(f"{yr}-07-01", min(pd.Timestamp(f"{yr}-10-31"), s.index.max())))
        x = s.index.map(lambda t: t.replace(year=2000))
        ax.plot(x, s.values, color=color, lw=lw, zorder=z)
        last = s.dropna()
        lx, ly = last.index[-1].replace(year=2000), last.iloc[-1]
        if yr == 2026:
            ax.scatter([lx], [ly], s=40, color=LEVEL, zorder=5, edgecolor=SURFACE, linewidth=1.5)
            ax.annotate(f"2026: {ly:.0f} cm\non {ap(last.index[-1])}", (lx, ly), xytext=(8, -2), textcoords="offset points",
                        color=INK, fontsize=10.5, va="center")
            gap = s[s.isna()]
            if len(gap):
                gx = gap.index.map(lambda t: t.replace(year=2000))
                ax.annotate(f"2026: no published\nreadings, {ap(gap.index[0])}\nto {ap(gap.index[-1])}",
                            (gx[len(gx) // 2], -36), color=INK_DIM, fontsize=9.5, ha="center", va="bottom")
        else:
            # 2018 is labeled at its end, 2022 at its peak, clear of the 2026 label
            if yr == 2018:
                ax.annotate(str(yr), (lx, ly), xytext=(5, 0), textcoords="offset points", color=color,
                            fontsize=10.5, va="center", annotation_clip=False)
            else:
                pt = last.idxmax()
                ax.annotate(str(yr), (pt.replace(year=2000), last[pt]), xytext=(0, 6), textcoords="offset points",
                            color=color, fontsize=10.5, ha="center", va="bottom")
    lo = d.loc[d["v"].idxmin()]
    ax.scatter([lo["date"].replace(year=2000)], [lo["v"]], s=30, color=INK, zorder=6)
    ax.annotate(f"Record low: {lo['v']:.0f} cm on {ap(lo['date'])}, {lo['date'].year}", (lo["date"].replace(year=2000), lo["v"]),
                xytext=(0, -12), textcoords="offset points", color=INK, fontsize=10, ha="center", va="top")
    for yv, lab in [(150, "150 cm: about\nwhat a full\nload needs"), (77, "77 cm: official\nlow-water\nmark"),
                    (40, "40 cm: many\nbarges find it\nuneconomical")]:
        ax.axhline(yv, color=THRESH, lw=1.1, ls=(0, (4, 3)), zorder=3)
        ax.text(pd.Timestamp("2000-11-09"), yv, lab, color=THRESH, fontsize=9, va="center", ha="left",
                clip_on=False)
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
    fig.savefig(OUT / "01-kaub.png")
    plt.close(fig)


def lobith():
    lvd, fld = load("rhine-lobith"), load("rhine-lobith", flow=True)
    lv, fl = annual_min(lvd), annual_min(fld)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.95, top=0.80, bottom=0.10, hspace=0.34)
    for ax, s, color, unit, fmt in [(a1, lv, LEVEL, "cm above NAP", "{:,.0f} cm"),
                                     (a2, fl, FLOW, "m³/s", "{:,.0f} m³/s")]:
        ax.plot(s.index, s.values, color=color, lw=1.6)
        ax.scatter([s.index[-1]], [s.iloc[-1]], s=36, color=color, zorder=5, edgecolor=SURFACE, linewidth=1.5)
        ax.annotate("2026: " + fmt.format(s.iloc[-1]), (s.index[-1], s.iloc[-1]), xytext=(-8, -14),
                    textcoords="offset points", color=INK, fontsize=10, ha="right")
        ax.set_ylabel(unit, color=INK_DIM)
        grid_y(ax)
    a1.set_title("Lowest daily water level each year", loc="left", color=INK, fontsize=12, fontweight="bold")
    a2.set_title("Lowest daily flow each year (flow record starts in 1901)", loc="left", color=INK, fontsize=12,
                 fontweight="bold")
    a1.set_ylim(600, 1100)
    a2.set_ylim(0, 1700)
    a2.set_xlim(1860, 2030)
    titleblock(fig, "At Lobith, the river's low level fell much more than its low flow",
               "The Rhine at Lobith, Netherlands, where it enters from Germany. 2026 runs through "
               + (f"{long_date(lvd['date'].max())}." if lvd['date'].max() == fld['date'].max() else
                  f"{long_date(lvd['date'].max())} for level\nand {long_date(fld['date'].max())} for flow.")
               + "\nRecent readings, and all flow before May 2003, are unchecked by Rijkswaterstaat.")
    credit(fig, "Source: Rijkswaterstaat Waterwebservices. Years with fewer than 330 days of data are left out, "
                "except 2026.")
    fig.savefig(OUT / "02-lobith.png")
    plt.close(fig)


def colorado():
    fig, axes = plt.subplots(2, 1, figsize=(10, 8.4))
    fig.subplots_adjust(left=0.10, right=0.95, top=0.80, bottom=0.10, hspace=0.40)
    for ax, gid, name, fill_end, fill_lab, ylim in [
            (axes[0], "colorado-lake-powell", "Lake Powell", "1980-06-22", "Filling, 1963 to 1980", (3350, 3750)),
            (axes[1], "colorado-lake-mead", "Lake Mead", "1941-07-01", "Filling,\n1935 to\n1941", (650, 1250))]:
        d = load(gid).dropna(subset=["v"])
        ax.axvspan(d["date"].min(), pd.Timestamp(fill_end), color=FILL, zorder=0)
        ax.text(d["date"].min() + pd.Timedelta(days=200), ylim[0] + 15, fill_lab, color=INK_DIM, fontsize=9.5,
                va="bottom")
        ax.plot(d["date"], d["v"], color=LEVEL, lw=1.3)
        after = d[d["date"] >= fill_end]
        lo = after.loc[after["v"].idxmin()]
        ax.axhline(lo["v"], color=INK_DIM, lw=0.9, ls=(0, (2, 3)))
        ax.scatter([lo["date"]], [lo["v"]], s=36, color=LEVEL, zorder=5, edgecolor=SURFACE, linewidth=1.5)
        ax.annotate(f"Low since filling:\n{lo['v']:,.2f} ft on {ap(lo['date'])}, {lo['date'].year}",
                    (lo["date"], lo["v"]), xytext=(-8, -30), textcoords="offset points", color=INK, fontsize=10,
                    ha="right", va="top")
        ax.set_title(name + ", water surface (ft above sea level)", loc="left", color=INK, fontsize=12,
                     fontweight="bold")
        ax.set_ylim(*ylim)
        ax.set_xlim(pd.Timestamp("1934-01-01"), pd.Timestamp("2028-01-01"))
        ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        grid_y(ax)
    titleblock(fig, "Lake Powell and Lake Mead fell to their lowest levels since they were filling",
               "Daily water surface elevation of the two largest reservoirs on the Colorado River.\n"
               "Shaded: the years each lake was first filling. Readings since October 1, 2025 are provisional.")
    credit(fig, "Source: U.S. Bureau of Reclamation (RISE). Filling ends when Lake Mead rose to a maximum in July 1941 "
                "and when Lake Powell first filled on June 22, 1980, per Reclamation.")
    fig.savefig(OUT / "03-colorado.png")
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    kaub()
    lobith()
    colorado()
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("0*.png"))))
