"""More YouTube Shorts cuts (1080x1920), each with its own layout.

usage: python3 shorts.py NAME WIDE HAND OUT.mp4 [--scale 0.5]
NAME:
  loop     song 1 intro: one player building loops, full-screen vertical,
           big REC / PLAY and a LOOP counter
  stack    song 1 horn breakdown -> trumpet solo, three stacked 16:9 strips
  karaoke  song 2 verse 1, full-screen vertical with big lyrics
  band     song 1 finale (4:00-4:47), whole band on top + four close-ups
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


# YouTube Shorts covers the top (status bar, search/menu icons), the bottom
# (channel, title, share button) and the right-hand button column, and crops
# about 47 px off each side. Text and faces stay inside this zone.
SAFE_TOP, SAFE_BOTTOM = 280, 1480
LOW_CX = 470            # centre for text below y=1000 (keeps it left of the buttons)
STRIPS3 = [(0, 495, 1080, 355), (0, 860, 1080, 355), (0, 1225, 1080, 355)]


def fit_upper(rect, aspect, anchor=0.35):
    """Like fit_aspect, but when cutting height keep the upper part (faces)."""
    x, y, w, h = rect
    if w / h > aspect:
        nw = h * aspect
        return (x + (w - nw) / 2, y, nw, h)
    nh = w / aspect
    return (x, y + (h - nh) * anchor, w, nh)


def box(c, frame, rect, b, s, border=True):
    x, y, w, h = (int(v * s) for v in b)
    rect = fit_upper(rect, w / h)
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
    """Song titles as large as fit the visible width (Press Start 2P glyphs are square)."""
    return min(72, 900 // len(song))


def title(c, song, s, sub=None):
    """Title block just below the YouTube top bar."""
    shade(c, SAFE_TOP - 20, SAFE_TOP + 200 + (50 if sub else 0), 0.55, s)
    text(c, "LOUIS COLE", ("center", SAFE_TOP + 40), 48)
    text(c, song, ("center", SAFE_TOP + 130), song_size(song), CYAN)
    if sub:
        text(c, sub, ("center", SAFE_TOP + 215), 30, YELLOW)


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
    shade(c, 1150, 1500, 0.6, s)
    if rec:
        # blinking REC
        if int((t - rec[0]) * 2) % 2 == 0:
            icon(c, render.PIX_DOT, 250, 1290, 12, RED, s)
        text(c, "REC", (420, 1290), 64, RED, glow=False)
        text(c, rec[2], (LOW_CX, 1385), 36)
    elif any(a <= t < b for a, b in LOOP_PLAY):
        icon(c, render.PIX_PLAY, 250, 1290, 12, GREEN, s)
        text(c, "PLAY", (440, 1290), 64, GREEN, glow=False)
    # loop counter: how many layers are stacked so far
    n = sum(1 for r in LOOP_REC if t >= r[1])
    d = ImageDraw.Draw(c)
    for i in range(3):
        x0, y0 = int((305 + i * 110) * s), int(1445 * s)
        d.rectangle([x0, y0, x0 + int(90 * s), y0 + int(24 * s)], fill=YELLOW if i < n else (60, 60, 70))
    if n:
        text(c, f"LOOP x{n}", (LOW_CX, 1195), 40, YELLOW)
    for a, b, d in SONG1.COUNTDOWN:
        if a <= t < b:
            text(c, d, ("center", 900), 220, glow=False)
    return c


# ------------------------------------------------------------------ 2. stack
STACK = dict(edl=SONG1, t0=203.4, t1=234.0)
STRIPS = STRIPS3
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
    label = "TRUMPET SOLO" if t >= STACK_TRUMPET else "HORN BREAKDOWN"
    title(c, "F IT UP", s, label)
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
    shade(c, 1140, 1490, 0.55, s)
    for a, b, line in e.VERSE1:
        a, b = a + e.VERSE1_SHIFT, b + e.VERSE1_SHIFT
        if a <= t < b:
            text(c, wrap(line), (LOW_CX, 1315), 60, CYAN)
            break
    return c


# ------------------------------------------------------------------ 4. vocal
# song 1 continued: singing (0:49) -> band walks on (fast-forwarded) ->
# "20 MINUTES LATER" -> band in. Segments: (source start, source end, speed).
# starts right on the first "YEAH" and runs to 60 s:
# 6.8 + 21.6/4 + 2.0 + 45.7 = 59.9 s
VOCAL = dict(edl=SONG1, t0=77.2, t1=153.5, fadein=0.03, segments=[
    (77.2, 84.0, 1),
    (84.0, 105.6, 4),        # FF>> at 4x
    (105.6, 107.6, 1),       # black card, muted
    (107.8, 153.5, 1),
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
VOCAL_STRIPS = STRIPS3
VOCAL_BAND_SETS = [
    [("H", "left2"), ("H", "center"), ("H", "horns")],
    [("W", "keys"), ("H", "bass"), ("W", "horns")],
    [("H", "horns"), ("W", "center"), ("H", "left2")],
    [("H", "full"), ("H", "horns"), ("W", "bass")],
]


VOCAL_FBA = (109.4, 111.8)
# name cards, same timing as the horizontal edit (KAZUHO = keys, IZUSHUN = bass)
VOCAL_SOLO = (131.8, 144.0)
KAZ_W = (130, 420, 440, 300)      # keys player in the wide camera
IZU_H = (380, 440, 480, 330)      # bass player in the handheld camera
NAME_TOP = (0, 495, 1080, 500)
NAME_BOTTOM = (0, 1005, 1080, 500)


def vocal_names(t, f, s):
    c = Image.new("RGB", (int(OW * s), int(OH * s)), (8, 8, 14))
    if t < 135.8:                                    # KAZUHO
        full(c, f["W"], vcrop(345, 600, 600 - 80 * phase(t, 131.8, 135.8)), s)
        c = flash(c, t, 131.8)
        title(c, "F IT UP", s)
        if 133.4 <= t < 135.4:
            shade(c, 1250, 1460, 0.5, s)
            text(c, "KAZUHO", (LOW_CX, 1355), 88, YELLOW)
    elif t < 139.0:                                  # IZUSHUN
        full(c, f["H"], vcrop(615, 690, 640 - 80 * phase(t, 135.8, 139.0)), s)
        c = flash(c, t, 135.8)
        title(c, "F IT UP", s)
        if 136.8 <= t < 138.8:
            shade(c, 1250, 1460, 0.5, s)
            text(c, "IZUSHUN", (LOW_CX, 1355), 88, YELLOW)
    else:                                            # both, stacked
        box(c, f["W"], KAZ_W, NAME_TOP, s)
        box(c, f["H"], IZU_H, NAME_BOTTOM, s)
        c = flash(c, t, 139.0)
        title(c, "F IT UP", s)
        if 139.8 <= t < 142.2:
            text(c, "KAZUHO", ("center", 900), 64, YELLOW)
            shade(c, 960, 1050, 0.6, s)
            text(c, "AND", ("center", 1003), 40)
            text(c, "IZUSHUN", (LOW_CX, 1410), 64, YELLOW)
    return c


def vocal_frame(t, f, s):
    e = SONG1
    c = Image.new("RGB", (int(OW * s), int(OH * s)))
    if VOCAL_CARD[0] <= t < VOCAL_CARD[1]:
        text(c, "20 MINUTES LATER", ("center", 960), 56)
        return c
    if t >= VOCAL_BAND and VOCAL_SOLO[0] <= t < VOCAL_SOLO[1]:
        return vocal_names(t, f, s)
    if t >= VOCAL_BAND:
        # band in: the screen splits into three strips, all changing every 2 bars
        i = int((t - VOCAL_BAND) // 3.2)
        for j, ((src, rn), b) in enumerate(zip(VOCAL_BAND_SETS[i % 4], VOCAL_STRIPS)):
            rects = e.WR if src == "W" else e.HR
            box(c, f[src], rects[rn], b, s)
        c = flash(c, t, VOCAL_BAND, 0.15, 0.7)
        title(c, "F IT UP", s)
        if 119.2 <= t < 120.6:
            text(c, "EVERYONE", ("center", 1040), 72)
        if VOCAL_FBA[0] <= t < VOCAL_FBA[1]:
            # as in the Louis Cole live-session reference at the band entry
            shade(c, 930, 1150, 0.6, s)
            text(c, "FULL BAND\nACTIVATED", ("center", 1040), 72, render.LYRIC_RED, glow=False)
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
            shade(c, 1300, 1470, 0.5, s)
            k = render.edl.W / OW
            size = min(40, 760 // (len(line) + 4))
            lyr = Image.new("RGB", c.size)
            mask = Image.new("L", c.size)
            render.draw_lyric(lyr, line, 1385 * k, size * k, 1.0)
            # draw_lyric centres on the frame; shift it left of the button column
            dx = int((LOW_CX - OW / 2) * s)
            m = lyr.convert("L").point(lambda v: 255 if v > 8 else 0)
            c.paste(lyr.transform(c.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0)), (0, 0),
                    m.transform(c.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0)))
            break
    if VOCAL_FF[0] <= t < VOCAL_FF[1]:
        shade(c, 1250, 1470, 0.5, s)
        text(c, "FF>>", (LOW_CX, 1360), 96, WHITE)
    if 75.1 <= t < 77.1:
        shade(c, 1230, 1480, 0.5, s)
        text(c, "THROAT SLAP\nVOCAL RUN", (LOW_CX, 1355), 56, YELLOW)
    if 77.2 <= t < 77.8 or 77.9 <= t < 78.7:
        text(c, "YEAH", ("center", 1000), 120)
    return c


# ------------------------------------------------------------------ 5. band
# song 1 finale, everyone playing (4:00-4:47): whole band on top, four
# member close-ups below. The highlighted panel cycles every two bars.
BAND = dict(edl=SONG1, t0=238.0, t1=287.0)
BAND_TOP = (0, 495, 1080, 450)
BAND_GRID = [(12, 960, 522, 268), (546, 960, 522, 268), (12, 1240, 522, 268), (546, 1240, 522, 268)]
BAND_LABELS = ["KEYS", "BASS", "HORNS", "DRUMS"]
BAND_HAND_END = 279.0          # handheld footage ends at 283.3; stay on the wide camera after this
BAND_BLACK = (253.9, 254.25)   # short blackout -> drums -> split screen, as in the long edit
BAND_DRUMS = (254.25, 255.6)
BAND_BUDDIEZ = (255.6, 268.6)
BAND_LOVE = (280.2, 281.8)
BAND_KIT = (850, 538, 360, 324)    # drum kit in the handheld camera


def band_frame(t, f, s):
    e = SONG1
    c = Image.new("RGB", (int(OW * s), int(OH * s)), (8, 8, 14))
    if BAND_BLACK[0] <= t < BAND_BLACK[1]:
        return c
    if BAND_DRUMS[0] <= t < BAND_DRUMS[1]:
        full(c, f["H"], vcrop(1030, 690, 520 - 60 * phase(t, *BAND_DRUMS)), s)
        title(c, "F IT UP", s)
        shade(c, 1270, 1450, 0.5, s)
        text(c, "DRUMS", (LOW_CX, 1360), 72, YELLOW)
        return c
    hand_ok = t < BAND_HAND_END
    i = int((t - BAND["t0"]) // 3.2)
    # top: alternate cameras, slow push in
    top_src = "H" if hand_ok and i % 2 else "W"
    top_r = lerp(e.WR["stage"] if top_src == "W" else e.HR["lower"],
                 e.WR["center"] if top_src == "W" else e.HR["center"], 0.25 * phase(t, BAND["t0"] + i * 3.2,
                                                                         BAND["t0"] + (i + 1) * 3.2))
    if t >= BAND_LOVE[0]:
        top_src, top_r = "W", e.WR["full"]
    box(c, f[top_src], top_r, BAND_TOP, s)
    # four close-ups; cameras swap every two bars
    srcs = [("W", "keys"), ("H", "bass"), ("W", "horns_tight"), ("H", "kit")]
    if i % 2:
        srcs = [("H", "keys"), ("W", "bass_tight"), ("H", "horns_tight"), ("H", "kit")]
    hl = 1 if BAND_BUDDIEZ[0] <= t < BAND_BUDDIEZ[1] else i % 4
    d = ImageDraw.Draw(c)
    for j, ((src, rn), b, lab) in enumerate(zip(srcs, BAND_GRID, BAND_LABELS)):
        if not hand_ok:
            src = "W"
        if rn == "kit":   # drummer sits behind the saxes; the handheld sees the kit
            r = BAND_KIT if src == "H" else e.WR["center"]
        else:
            r = (e.WR if src == "W" else e.HR).get(rn, e.WR[rn])
        x, y, w, h = (int(v * s) for v in b)
        if j == hl:
            m = max(2, int(9 * s))
            d.rectangle([x - m, y - m, x + w + m - 1, y + h + m - 1], fill=YELLOW)
        box(c, f[src], r, b, s, border=j != hl)
        # label in the panel's top-left corner (bottom-right is under the buttons)
        text(c, lab, (b[0] + 24 + len(lab) * 13, b[1] + 30), 26, YELLOW if j == hl else WHITE)
    c = flash(c, t, BAND["t0"] + i * 3.2, 0.06, 0.25)
    title(c, "F IT UP", s)
    if BAND_BUDDIEZ[0] <= t < BAND_BUDDIEZ[1]:
        text(c, "BASSLINE BUDDIEZ", ("center", 720), 56, YELLOW)
    if BAND_LOVE[0] <= t < BAND_LOVE[1]:
        c = Image.blend(Image.new("RGB", c.size), c, 0.45)
        text(c, "THEY LOVE IT", ("center", 960), 88)
    return c


RECIPES = {
    "band": (BAND, band_frame),
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
        f"afade=t=in:d={cfg.get('fadein', 0.2)},afade=t=out:st={dur - 0.6}:d=0.6[aout]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", a.wide, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-t", f"{dur:.3f}",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out], check=True)
    os.remove(tmp)


if __name__ == "__main__":
    main()
