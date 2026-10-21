"""Instagram video of Lake Mead from the tool itself (dist/index.html), as a 1080x1920 (9:16) MP4.

The page is opened in Chrome on the Lake Mead gauge and played the way the Play button plays it at
"5 years per second": 1,826 days of record per second of video, 30 frames a second. Each frame sets
the tool's own day and calls its own update(), so the lake drawing, the reading and the date are
exactly what the tool shows. The record chart under it is the tool's chart with everything after
the current day masked, so the history builds as the lake plays. The last day holds for 5 seconds.

Everything sits inside the center 1080x1080 square with a margin, since Instagram's editor crops
the video to that square.

Needs Playwright (uses the installed Google Chrome) and an ffmpeg binary: $FFMPEG, ffmpeg on the
PATH, or the imageio-ffmpeg package.

    python scripts/reel.py [gauge] [hold_seconds]
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "posts/world-river-levels/social"
GAUGE = sys.argv[1] if len(sys.argv) > 1 else "colorado-lake-mead"
HOLD = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
FPS = 30
DAYS_PER_SECOND = 1826          # the tool's "5 years per second" speed
CSS_W, CSS_H, SCALE = 675, 1200, 1.6   # 1080x1920

TITLE = "Lake Mead's water level, 1935 to 2026"
SUB = ("Daily readings at Hoover Dam, in feet above sea level, played at five years per second. "
       "Shaded: the years the lake was first filling.")
SOURCE = "Source: U.S. Bureau of Reclamation. 2026 readings are provisional."

# Pulls the pieces of the gauge panel the video needs into one centered column and hides the rest.
SETUP = """([title, sub, source]) => {
  const reel = document.createElement("div"); reel.id = "reel";
  const head = document.createElement("div"); head.className = "rhead";
  const h = document.createElement("p"); h.className = "rtitle"; h.textContent = title;
  const s = document.createElement("p"); s.className = "rsub"; s.textContent = sub;
  head.append(h, s);
  const chart = document.querySelector("#rec").closest(".chartwrap");
  const foot = document.createElement("div"); foot.className = "rfoot";
  const src = document.createElement("span"); src.textContent = source;
  foot.append(src, document.querySelector("footer .brand"));
  reel.append(head, document.querySelector(".readout"), $("xsec"), chart, foot);
  document.body.append(reel);
  const st = document.createElement("style");
  st.textContent = `
    body > *:not(#reel) { display: none !important; }
    #reel { position: fixed; inset: 0; background: var(--page); display: flex; flex-direction: column;
            justify-content: center; gap: 10px; padding: 0 34px; }
    .rtitle { margin: 0; font-size: 31px; font-weight: 700; color: var(--ink); line-height: 1.15; }
    .rsub { margin: 8px 0 0; font-size: 16px; color: var(--ink-2); line-height: 1.4; }
    #reel .readout { margin-top: 2px; }
    #reel .readout .val { font-size: 44px; }
    #reel .readout .date { font-size: 21px; }
    #reel .readout .q { font-size: 14px; }
    #reel #xsec { height: 150px; }
    #reel #rec { height: 200px; cursor: default; }
    .rfoot { display: flex; justify-content: space-between; align-items: center; gap: 10px;
             font-size: 13px; color: var(--muted); margin-top: 4px; }
    .rfoot .brand { white-space: nowrap; flex: none; }
    .rfoot .brand img { height: 16px; }
  `;
  document.head.append(st);
}"""

# The chart with no data, for masking the days that have not played yet. Grid, axis labels, the
# filling shade and thresholds stay; only readings and the average are blanked.
EMPTY = """() => {
  const ser = mainChart.ser, v = ser.v, avg = ser.avg;
  ser.v = new Float64Array(ser.n).fill(NaN); ser.avg = new Float64Array(ser.n).fill(NaN);
  mainChart.draw(); window.__empty = mainChart.img;
  ser.v = v; ser.avg = avg; mainChart.draw();
}"""

FRAME = """(d) => {
  day = d; $("slider").value = Math.round(day - T0); update();
  const rec = $("rec"), c = rec.getContext("2d"), dp = window.devicePixelRatio || 1, ser = mainChart.ser;
  const pw = mainChart.cw - PADL - PADR, i = Math.round(day) - ser.start;
  const x = Math.round((PADL + i / (ser.n - 1) * pw) * dp) + 2 * dp;
  if (x < rec.width) c.putImageData(window.__empty, 0, 0, x, 0, rec.width - x, (mainChart.ch - PADB) * dp);
}"""


def ffmpeg():
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mp4 = OUT / f"{GAUGE}.mp4"
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": CSS_W, "height": CSS_H}, device_scale_factor=SCALE,
                                color_scheme="dark")
        page.goto(f"file://{ROOT / 'dist/index.html'}#{GAUGE}")
        page.wait_for_function("typeof S !== 'undefined' && S && mainChart.img")
        page.evaluate("stop()")
        page.evaluate(SETUP, [TITLE, SUB, SOURCE])
        page.evaluate("drawCharts(); update()")
        page.evaluate(EMPTY)
        t0, t1 = page.evaluate("[T0, T1]")
        step = DAYS_PER_SECOND / FPS
        days = [t0 + k * step for k in range(int((t1 - t0) / step) + 1)]
        if days[-1] < t1:
            days.append(t1)
        frames = []
        for k, d in enumerate(days):
            page.evaluate(FRAME, d)
            f = Path(tmp) / f"{k:05d}.png"
            page.screenshot(path=str(f))
            frames.append(f)
        browser.close()
        shutil.copyfile(frames[-1], OUT / f"{GAUGE}-last-frame.png")
        lines = []
        for f in frames:
            lines += [f"file '{f}'", f"duration {1 / FPS:.6f}"]
        lines[-1] = f"duration {HOLD:.3f}"
        lines.append(f"file '{frames[-1]}'")      # the last duration needs the file repeated
        lst = Path(tmp) / "frames.txt"
        lst.write_text("\n".join(lines) + "\n")
        total = (len(frames) - 1) / FPS + HOLD
        # -t: the repeated last file would otherwise add a second hold.
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-t", f"{total:.2f}", "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "20", "-movflags", "+faststart", str(mp4)], check=True)
    print(f"{mp4.name}: {round(CSS_W * SCALE)}x{round(CSS_H * SCALE)}, {len(frames)} frames, {total:.1f}s "
          f"({HOLD:.0f}s hold), {mp4.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
