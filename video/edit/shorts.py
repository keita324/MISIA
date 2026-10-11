"""More YouTube Shorts cuts (1080x1920), each with its own layout.

usage: python3 shorts.py NAME WIDE HAND OUT.mp4 [--scale 0.5]
NAME:
  loop     song 1 intro: one player building loops, full-screen vertical,
           big REC / PLAY and a LOOP counter
  stack    song 1 horn breakdown -> trumpet solo, three stacked 16:9 strips
  karaoke  song 2 verse 1, full-screen vertical with big lyrics
  vocal    song 1 continued after "loop": singing -> FF>> (4x) -> 20 MINUTES LATER
           -> band in, which splits the screen into three strips
WIDE/HAND are the two cameras of that song (song 1 for loop/stack, song 2 for karaoke).
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SONG1 = render.load_edl(os.path.join(HERE, "edl.py"))
SONG2 = render.load_edl(os.path.join(HERE, "edl_song2.py"))

OW, OH = 1080, 1920
FPS = 30
WHITE, CYAN, YELLOW, PINK, RED, GREEN = ((255, 255, 255), (90, 235, 240), (255, 220, 60),
                                         (255, 110, 190), (235, 30, 40), (40, 235, 60))


# ------------------------------------------------------------------ helpers
def text(c, s, pos, size, color=WHITE, alpha=1.0, glow=True):
    """Pixel text in 1080x1920 coordinates (draw_pixel_text works in a 1920-wide space)."""
    k = render.edl.W / OW
    x = pos[0] if isinstance(pos[0], str) else pos[0] * k
    render.draw_pixel_text(c, s, (x, pos[1] * k), size * k, alpha, color=color, glow=glow)


def vcrop(cx, cy, h, aspect=9 / 16):
    w = h * aspect
    return (cx - w / 2, cy - h / 2, w, h)


def lerp(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(len(a)))


def phase(t, t0, t1):
    return render.ease((t - t0) / (t1 - t0))


def full(c, frame, rect, s):
    img = render.grab(frame, rect, c.size, frame.width / 1920)
    c.paste(render.sharpen(img), (0, 0))


def box(c, frame, rect, b, s, border=True):
    x, y, w, h = (int(v * s) for v in b)
    rect = render.fit_aspect(rect, w / h)
    img = render.sharpen(render.grab(frame, rect, (w, h), frame.width / 1920))
    if border:
        e = max(1, int(5 * s))
        ImageDraw.Draw(c).rectangle([x - e, y - e, x + w + e - 1, y + h + e - 1], fill=(235, 235, 235))
    c.paste(img, (x, y))


def shade(c, y0, y1, strength=0.65, s=1.0):
    """Darken a horizontal band so text stays readable on full-bleed video."""
    y0, y1 = int(y0 * s), int(y1 * s)
    band = c.crop((0, y0, c.width, y1))
    c.paste(Image.blend(band, Image.new("RGB", band.size), strength), (0, y0))


def flash(c, t, t_cut, dur=0.1, amount=0.55):
    if t_cut <= t < t_cut + dur:
        return Image.blend(c, Image.new("RGB", c.size, WHITE), amount)
    return c


def icon(c, pattern, cx, cy, cell, color, s):
    k = render.edl.W / OW
    render.draw_icon(c, pattern, cx * k, cy * k, cell * k, color, 1.0)


def song_size(song):
    """Song titles as large as fit the 1080 width (Press Start 2P glyphs are square)."""
    return min(72, 1000 // len(song))


def title(c, song, s):
    shade(c, 0, 250, 0.55, s)
    text(c, "LOUIS COLE", ("center", 70), 48)
    text(c, song, ("center", 170), song_size(song), CYAN)


# ------------------------------------------------------------------ 1. loop
# song 1, one performer at the centre keyboard
LOOP = dict(edl=SONG1, t0=10.0, t1=49.0)
# (start, end, src, centre-x, centre-y, height at start, height at end)
LOOP_SHOTS = [
    (10.0, 14.0, "W", 900, 560, 1000, 860),
    (14.0, 19.0, "W", 880, 600, 620, 460),     # REC: push in on hands
    (19.0, 23.3, "H", 1000, 520, 1000, 900),
    (23.3, 25.8, "W", 880, 560, 900, 900),     # PLAY: at the laptop
    (25.8, 31.0, "W", 880, 600, 560, 440),     # REC
    (31.0, 35.2, "H", 1000, 500, 900, 1000),
    (35.2, 38.2, "W", 900, 560, 900, 760),     # countdown
    (38.2, 44.4, "W", 880, 600, 620, 480),     # REC bass
    (44.4, 49.0, "H", 1000, 520, 1000, 1060),
]
# REC only while he plays the keyboard (same timing as the horizontal edit)
LOOP_REC = SONG1.REC
LOOP_PLAY = [(a, b) for a, b, _ in SONG1.PLAY]


def loop_frame(t, f, s):
    c = Image.new("RGB", (int(OW * s), int(OH * s)))
    for a, b, src, cx, cy, h0, h1 in LOOP_SHOTS:
        if a <= t < b:
            h = h0 + (h1 - h0) * phase(t, a, b)
            full(c, f[src], vcrop(cx, cy, h), s)
            c = flash(c, t, a)
            break
    title(c, "F IT UP", s)
    rec = next((r for r in LOOP_REC if r[0] <= t < r[1]), None)
    shade(c, 1560, 1920, 0.6, s)
    if rec:
        # blinking REC
        if int((t - rec[0]) * 2) % 2 == 0:
            icon(c, render.PIX_DOT, 300, 1660, 12, RED, s)
        text(c, "REC", (480, 1660), 64, RED, glow=False)
        text(c, rec[2], ("center", 1770), 36)
    elif any(a <= t < b for a, b in LOOP_PLAY):
        icon(c, render.PIX_PLAY, 300, 1660, 12, GREEN, s)
        text(c, "PLAY", (500, 1660), 64, GREEN, glow=False)
    # loop counter: how many layers are stacked so far
    n = sum(1 for r in LOOP_REC if t >= r[1])
    d = ImageDraw.Draw(c)
    for i in range(3):
        x0, y0 = int((390 + i * 110) * s), int(1850 * s)
        d.rectangle([x0, y0, x0 + int(90 * s), y0 + int(24 * s)], fill=YELLOW if i < n else (60, 60, 70))
    if n:
        text(c, f"LOOP x{n}", ("center", 1500), 40, YELLOW)
    for a, b, d in SONG1.COUNTDOWN:
        if a <= t < b:
            text(c, d, ("center", 900), 220, glow=False)
    return c


# ------------------------------------------------------------------ 2. stack
STACK = dict(edl=SONG1, t0=203.4, t1=234.0)
STRIPS = [(0, 250, 1080, 540), (0, 810, 1080, 540), (0, 1370, 1080, 540)]
# every 3.2 s (two bars) the three strips get a new set of shots
STACK_SETS = [
    [("W", "horns"), ("H", "bass"), ("W", "keys")],
    [("W", "horns_tight"), ("H", "center"), ("W", "bass")],
    [("H", "horns"), ("W", "center"), ("H", "bass_tight")],
    [("W", "horns"), ("W", "drums"), ("W", "keys_tight")],
]
STACK_TRUMPET = 228.6       # trumpet solo: all three strips on the trumpet


def stack_frame(t, f, s):
    e = SONG1
    c = Image.new("RGB", (int(OW * s), int(OH * s)), (8, 8, 14))
    trumpet = [("W", "horns"), ("W", "trumpet"), ("H", "horns_tight")]

    def shots_at(tt):
        if tt >= STACK_TRUMPET:
            return trumpet, STACK_TRUMPET
        i = int((tt - STACK["t0"]) // 3.2)
        return STACK_SETS[i % len(STACK_SETS)], STACK["t0"] + i * 3.2

    shots, cut = shots_at(t)
    prev, _ = shots_at(max(STACK["t0"], cut - 0.01))
    for j, b in enumerate(STRIPS):
        # strips change one after another, top to bottom
        src, rn = prev[j] if t < cut + 0.1 * j else shots[j]
        rects = e.WR if src == "W" else e.HR
        r = rects[rn]
        if t >= STACK_TRUMPET + 0.1 and j == 1:
            r = lerp(e.WR["trumpet"], e.WR["trumpet_tight"], phase(t, STACK_TRUMPET, STACK["t1"]))
        box(c, f[src], r, b, s)
    text(c, "LOUIS COLE", ("center", 55), 44)
    text(c, "F IT UP", ("center", 135), song_size("F IT UP"), CYAN)
    label = "TRUMPET SOLO" if t >= STACK_TRUMPET else "HORN BREAKDOWN"
    text(c, label, ("center", 218), 30, YELLOW)
    return c


# ------------------------------------------------------------------ 3. karaoke
KARAOKE = dict(edl=SONG2, t0=24.6, t1=51.0)
KARA_SHOTS = [
    (24.6, 28.7, "W", 690, 520, 900, 760),    # bass
    (28.7, 31.9, "W", 1300, 560, 760, 640),   # horns
    (31.9, 35.1, "W", 420, 560, 700, 600),    # keys
    (35.1, 38.3, "W", 1240, 520, 640, 560),   # flute / centre
    (38.3, 41.5, "W", 690, 520, 760, 640),
    (41.5, 44.7, "W", 1580, 640, 560, 480),   # saxes right
    (44.7, 47.9, "W", 1170, 640, 620, 520),
    (47.9, 51.0, "W", 960, 540, 1000, 1080),  # pull out to the band
]


def wrap(s, n=13):
    out, line = [], ""
    for w in s.split():
        if line and len(line) + 1 + len(w) > n:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    out.append(line)
    return "\n".join(out)


def karaoke_frame(t, f, s):
    e = SONG2
    c = Image.new("RGB", (int(OW * s), int(OH * s)))
    for a, b, src, cx, cy, h0, h1 in KARA_SHOTS:
        if a <= t < b:
            full(c, f[src], vcrop(cx, cy, h0 + (h1 - h0) * phase(t, a, b)), s)
            break
    title(c, "FAILING IN A COOL WAY", s)
    shade(c, 1260, 1760, 0.55, s)
    for a, b, line in e.VERSE1:
        a, b = a + e.VERSE1_SHIFT, b + e.VERSE1_SHIFT
        if a <= t < b:
            text(c, wrap(line), ("center", 1510), 60, CYAN)
            break
    return c


# ------------------------------------------------------------------ 4. vocal
# song 1 continued: singing (0:49) -> band walks on (fast-forwarded) ->
# "20 MINUTES LATER" -> band in. Segments: (source start, source end, speed).
VOCAL = dict(edl=SONG1, t0=49.0, t1=121.0, segments=[
    (49.0, 84.0, 1),
    (84.0, 105.6, 4),        # FF>> at 4x
    (105.6, 107.6, 1),       # black card, muted
    (107.8, 121.0, 1),
])
VOCAL_FF = (84.0, 105.6)
VOCAL_CARD = (105.6, 107.6)
VOCAL_BAND = 109.4
# (start, end, src, centre-x, centre-y, height at start, height at end)
VOCAL_SHOTS = [
    (49.0, 55.0, "W", 1040, 600, 760, 640),
    (55.0, 61.5, "H", 1100, 620, 820, 700),
    (61.5, 65.0, "W", 1040, 560, 1000, 900),
    (65.0, 71.5, "H", 1100, 600, 760, 620),
    (71.5, 75.0, "W", 1040, 600, 700, 600),
    (75.0, 77.2, "H", 1100, 560, 560, 500),   # vocal run: tight
    (77.2, 79.5, "W", 1040, 560, 1000, 1000),
    (79.5, 84.0, "H", 1100, 600, 640, 760),
    (107.8, 109.4, "H", 960, 540, 1080, 1080),
]
VOCAL_STRIPS = [(0, 280, 1080, 540), (0, 840, 1080, 540), (0, 1380, 1080, 540)]
VOCAL_BAND_SETS = [
    [("H", "left2"), ("H", "center"), ("H", "horns")],
    [("W", "keys"), ("H", "bass"), ("W", "horns")],
    [("H", "horns"), ("W", "center"), ("H", "left2")],
    [("H", "full"), ("H", "horns"), ("W", "bass")],
]


def vocal_frame(t, f, s):
    e = SONG1
    c = Image.new("RGB", (int(OW * s), int(OH * s)))
    if VOCAL_CARD[0] <= t < VOCAL_CARD[1]:
        text(c, "20 MINUTES LATER", ("center", 960), 56)
        return c
    if t >= VOCAL_BAND:
        # band in: the screen splits into three strips, all changing every 2 bars
        i = int((t - VOCAL_BAND) // 3.2)
        for j, ((src, rn), b) in enumerate(zip(VOCAL_BAND_SETS[i % 4], VOCAL_STRIPS)):
            rects = e.WR if src == "W" else e.HR
            box(c, f[src], rects[rn], b, s)
        c = flash(c, t, VOCAL_BAND, 0.15, 0.7)
        text(c, "LOUIS COLE", ("center", 70), 48)
        text(c, "F IT UP", ("center", 170), song_size("F IT UP"), CYAN)
        if 119.2 <= t < 120.6:
            text(c, "EVERYONE", ("center", 1110), 72)
        return c
    if VOCAL_FF[0] <= t < VOCAL_FF[1]:
        # fast-forward: pan across the stage as the band walks on
        k = (t - VOCAL_FF[0]) / (VOCAL_FF[1] - VOCAL_FF[0])
        full(c, f["H"], vcrop(500 + 900 * k, 540, 1080), s)
    else:
        for a, b, src, cx, cy, h0, h1 in VOCAL_SHOTS:
            if a <= t < b:
                full(c, f[src], vcrop(cx, cy, h0 + (h1 - h0) * phase(t, a, b)), s)
                c = flash(c, t, a, 0.06, 0.35)
                break
    title(c, "F IT UP", s)
    if 49.1 <= t < 50.8:
        a = min(1.0, (t - 49.1) / 0.15, (50.8 - t) / 0.5)
        text(c, "LOUIS COLE", ("center", 900), 96, alpha=a)
    for a, b, line in SONG1.LYRICS:
        a, b = a + SONG1.LYRIC_SHIFT, b + SONG1.LYRIC_SHIFT
        if a <= t < b and not VOCAL_FF[0] <= t < VOCAL_FF[1]:   # no lyrics under FF>>
            shade(c, 1600, 1840, 0.5, s)
            k = render.edl.W / OW
            size = min(40, 900 // (len(line) + 4))
            render.draw_lyric(c, line, 1720 * k, size * k, 1.0)
            break
    if VOCAL_FF[0] <= t < VOCAL_FF[1]:
        shade(c, 1600, 1920, 0.5, s)
        text(c, "FF>>", ("center", 1740), 96, WHITE)
    if 75.1 <= t < 77.1:
        shade(c, 1560, 1840, 0.5, s)
        text(c, "THROAT SLAP\nVOCAL RUN", ("center", 1700), 56, YELLOW)
    if 77.2 <= t < 77.8 or 77.9 <= t < 78.7:
        text(c, "YEAH", ("center", 1000), 120)
    return c


RECIPES = {
    "vocal": (VOCAL, vocal_frame),
    "loop": (LOOP, loop_frame),
    "stack": (STACK, stack_frame),
    "karaoke": (KARAOKE, karaoke_frame),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=RECIPES)
    ap.add_argument("wide")
    ap.add_argument("hand")
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="21")
    a = ap.parse_args()
    cfg, frame_fn = RECIPES[a.name]
    e, T0, T1 = cfg["edl"], cfg["t0"], cfg["t1"]
    s = a.scale
    ow, oh = int(OW * s) // 2 * 2, int(OH * s) // 2 * 2
    segments = cfg.get("segments", [(T0, T1, 1)])
    tmp = a.out + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", a.crf,
                            "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    dur = sum((b - a_) / sp for a_, b, sp in segments)
    u = 0.0
    for a0, a1, speed in segments:
        wr = render.Reader(a.wide, a0, 1920, 1080)
        hr = render.Reader(a.hand, a0 - e.HAND_OFFSET, 1920, 1080)
        n = int(round((a1 - a0) / speed * FPS))
        for i in range(n):
            t = a0 + i * speed / FPS
            for _ in range(speed - 1):   # fast-forward: skip frames
                wr.read()
                hr.read()
            img = frame_fn(t, {"W": wr.read(), "H": hr.read()}, s)
            if u > dur - 0.6:
                img = Image.blend(Image.new("RGB", img.size), img, max(0.0, (dur - u) / 0.6))
            if img.size != (ow, oh):
                img = img.resize((ow, oh))
            enc.stdin.write(img.tobytes())
            u += 1 / FPS
        wr.close()
        hr.close()
    enc.stdin.close()
    enc.wait()
    # audio: same segments, fast parts sped up (pitch kept) and quieter, mute ranges silenced
    parts, labels = [], []
    for i, (a0, a1, speed) in enumerate(segments):
        f = f"[1:a]atrim={a0}:{a1},asetpts=PTS-STARTPTS"
        if speed == 4:
            f += ",atempo=2,atempo=2,volume=0.5"
        if any(m0 < a1 and a0 < m1 for m0, m1 in getattr(e, "MUTE", [])):
            f += ",volume=0"
        parts.append(f + f"[a{i}]")
        labels.append(f"[a{i}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(segments)}:v=0:a=1," \
        f"afade=t=in:d=0.2,afade=t=out:st={dur - 0.6}:d=0.6[aout]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", a.wide, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-t", f"{dur:.3f}",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out], check=True)
    os.remove(tmp)


if __name__ == "__main__":
    main()
