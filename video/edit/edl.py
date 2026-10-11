"""Edit decision list for the "F IT UP" cover video.

Timeline time == time in the wide (fixed) camera, whose audio is the master track.
The handheld camera started 11.92 s later (measured by audio cross-correlation),
so handheld time = timeline time - HAND_OFFSET.

Text timing mirrors the reference (Louis Cole Live 2019, first song), mapped onto
this band's performance by comparing the two audio tracks section by section.
"""

HAND_OFFSET = 11.92
DURATION = 287.8
FPS = 30
W, H = 1920, 1080

# Crop rectangles (x, y, w, h) in source pixels. Every rect is 16:9.
# Wide camera is on a tripod, so these hold for the whole song.
WR = {
    "full":      (0, 0, 1920, 1080),
    "stage":     (120, 200, 1600, 900),
    # intro: single performer at the centre keyboard
    "solo_med":  (560, 330, 800, 450),
    "solo_tight": (690, 380, 576, 324),
    "solo_hands": (700, 470, 480, 270),
    # full band (from ~84 s)
    "keys":      (40, 380, 640, 360),     # Kazuho, far left
    "keys_tight": (130, 440, 448, 252),
    "bass":      (300, 320, 720, 405),    # Izushun
    "bass_tight": (420, 360, 512, 288),
    "left2":     (0, 300, 960, 540),      # keys + bass two-shot
    "center":    (780, 330, 800, 450),
    "horns":     (920, 380, 1000, 562),   # horn section, right side
    "horns_tight": (1080, 420, 720, 405),
    "horns_far": (1400, 440, 512, 288),
    "trumpet":   (1190, 380, 560, 315),   # trumpet solo (KAESUKE)
    "trumpet_tight": (1260, 420, 432, 243),
    "drums":     (860, 430, 560, 315),
}

# Handheld camera framing drifts, so its rects are chosen per section.
HR = {
    "full":      (0, 0, 1920, 1080),
    "lower":     (0, 160, 1600, 900),
    # intro (performer roughly centre)
    "solo_a":    (520, 300, 960, 540),
    "solo_b":    (600, 260, 800, 450),
    "solo_face": (680, 220, 640, 360),
    "voc_a":     (560, 180, 1040, 585),
    "voc_face":  (760, 200, 720, 405),
    # band section
    "keys":      (0, 500, 720, 405),
    "bass":      (180, 380, 880, 495),
    "bass_tight": (300, 420, 640, 360),
    "left2":     (0, 340, 1200, 675),
    "center":    (760, 380, 880, 495),
    "horns":     (880, 400, 1040, 585),
    "horns_tight": (1100, 460, 800, 450),
}


def S(t0, t1, src, r0, r1=None, **kw):
    """Single full-frame shot. r1 enables a slow push/pull between rects."""
    return dict(t0=t0, t1=t1, kind="single", src=src, r0=r0, r1=r1 or r0, **kw)


def BLACK(t0, t1):
    return dict(t0=t0, t1=t1, kind="black")


def GRID(t0, t1, panels, **kw):
    """Multi panel layout. panels: list of (src, rect_name, (x, y, w, h) on screen)."""
    return dict(t0=t0, t1=t1, kind="grid", panels=panels, **kw)


# ---------------------------------------------------------------- shots
SHOTS = [
    BLACK(0.0, 7.6),
    S(7.6, 10.2, "W", "full", "stage"),
    # music starts 10.2 -- loop building section
    S(10.2, 13.5, "W", "solo_med", "solo_tight"),
    S(13.5, 17.8, "H", "solo_a", "solo_b"),
    S(17.8, 22.0, "W", "solo_tight", "solo_med"),
    S(22.0, 27.0, "W", "solo_hands", "solo_tight"),
    S(27.0, 30.4, "H", "lower", "solo_a"),
    S(30.4, 33.7, "W", "full", "stage"),
    S(33.7, 37.5, "W", "solo_tight", "solo_med"),
    S(37.5, 41.0, "H", "solo_b", "solo_a"),
    S(41.0, 44.5, "W", "solo_med", "solo_tight"),
    S(44.5, 48.5, "H", "solo_a", "solo_b"),
    # vocal section
    S(48.5, 55.0, "W", "solo_med", "solo_tight"),
    S(55.0, 61.5, "H", "voc_a", "voc_face"),
    S(61.5, 65.0, "W", "full", "stage"),
    S(65.0, 71.5, "H", "voc_a", "voc_face"),
    S(71.5, 75.0, "W", "solo_tight", "solo_med"),
    S(75.0, 77.2, "H", "voc_face", "voc_face"),
    S(77.2, 79.5, "W", "full", "full"),
    S(79.5, 84.0, "H", "voc_face", "voc_a"),
    # band walks on -> "FF>>" section
    S(84.0, 86.5, "W", "full", "stage"),
    S(86.5, 89.0, "H", "full", "lower"),
    S(89.0, 91.5, "W", "left2", "bass"),
    S(91.5, 94.0, "H", "lower", "full"),
    S(94.0, 96.5, "W", "horns", "horns_tight"),
    S(96.5, 99.0, "H", "full", "lower"),
    S(99.0, 105.6, "W", "stage", "full"),
    BLACK(105.6, 107.8),
    S(107.8, 109.4, "H", "full", "full"),
    # full band
    S(109.4, 112.6, "H", "lower", "full"),
    S(112.6, 115.8, "W", "horns", "horns_tight"),
    S(115.8, 119.0, "H", "bass", "bass_tight"),
    S(119.0, 122.2, "W", "full", "full"),
    S(122.2, 125.4, "W", "keys", "keys_tight"),
    S(125.4, 128.6, "H", "horns", "horns_tight"),
    S(128.6, 131.8, "W", "bass", "bass_tight"),
    # break -- name cards
    S(131.8, 135.8, "W", "keys", "keys_tight"),
    S(135.8, 139.0, "H", "bass", "bass_tight"),
    S(139.0, 144.0, "W", "left2", "left2"),
    S(144.0, 147.2, "H", "full", "lower"),
    S(147.2, 150.4, "W", "horns", "horns_tight"),
    S(150.4, 153.6, "H", "bass", "bass_tight"),
    S(153.6, 156.8, "W", "full", "stage"),
    S(156.8, 159.4, "H", "horns", "horns_tight"),
    GRID(159.4, 166.4, [
        ("W", "horns", (40, 30, 860, 484)),
        ("H", "center", (940, 60, 620, 349)),
        ("W", "keys", (150, 610, 440, 248)),
        ("H", "bass", (700, 470, 520, 560)),
        ("W", "center", (1300, 470, 520, 560)),
    ]),
    S(166.4, 167.8, "W", "full", "full"),
    S(167.8, 169.8, "W", "bass", "bass_tight"),
    S(169.8, 171.8, "H", "bass_tight", "bass_tight"),
    S(171.8, 178.2, "W", "horns", "horns_tight",
      pip=("H", "bass", (40, 820, 340, 191))),
    S(178.2, 181.4, "H", "horns_tight", "horns"),
    S(181.4, 184.6, "W", "full", "stage"),
    S(184.6, 187.8, "H", "keys", "keys"),
    S(187.8, 191.0, "W", "center", "center"),
    S(191.0, 194.2, "H", "bass", "bass_tight"),
    S(194.2, 197.4, "W", "horns", "horns_tight"),
    S(197.4, 200.6, "H", "full", "lower"),
    S(200.6, 204.0, "W", "full", "stage"),
    # horn breakdown -- two panels, right panel cuts around
    GRID(204.0, 207.2, [("W", "horns", (35, 25, 990, 557)), ("H", "bass", (1065, 135, 820, 905))], still=True),
    GRID(207.2, 210.4, [("W", "horns", (35, 25, 990, 557)), ("H", "center", (1065, 135, 820, 905))], cont=True),
    GRID(210.4, 213.6, [("W", "horns", (35, 25, 990, 557)), ("W", "keys", (1065, 135, 820, 905))], cont=True),
    GRID(213.6, 216.8, [("W", "horns", (35, 25, 990, 557)), ("H", "bass_tight", (1065, 135, 820, 905))], cont=True),
    GRID(216.8, 220.0, [("H", "horns", (35, 25, 990, 557)), ("W", "center", (1065, 135, 820, 905))], cont=True),
    GRID(220.0, 225.5, [("H", "horns", (35, 25, 990, 557)), ("W", "bass", (1065, 135, 820, 905))], cont=True),
    S(225.5, 229.0, "W", "full", "full"),
    S(229.0, 233.0, "W", "trumpet", "trumpet_tight",
      pip=("H", "bass", (40, 820, 340, 191))),
    S(233.0, 238.0, "H", "horns_tight", "horns"),
    GRID(238.0, 249.0, [
        ("H", "horns_tight", (50, 30, 420, 700)),
        ("W", "horns", (550, 30, 860, 430)),
        ("H", "center", (560, 520, 720, 520)),
        ("W", "keys", (1350, 470, 400, 560)),
    ]),
    S(249.0, 252.2, "H", "center", "center"),
    S(252.2, 253.9, "W", "left2", "bass"),
    # short blackout -> drums -> split screen (as in the reference)
    BLACK(253.9, 254.25),
    S(254.25, 255.6, "W", "drums", "drums"),
    GRID(255.6, 268.6, [
        ("W", "horns", (30, 30, 860, 560)),
        ("H", "horns", (990, 40, 780, 400)),
        ("W", "keys", (180, 660, 520, 380)),
        ("H", "bass", (900, 520, 560, 500)),
        ("W", "bass_tight", (1480, 520, 400, 520)),
    ], label=("BASSLINE\nBUDDIEZ", (1500, 470))),
    S(268.6, 270.4, "H", "horns_tight", "horns"),
    S(270.4, 272.0, "W", "horns", "horns_tight"),
    S(272.0, 276.4, "W", "stage", "full"),
    S(276.4, 279.2, "H", "center", "center"),
    S(279.2, 282.0, "H", "full", "full", dim=0.55),
    S(282.0, DURATION, "W", "full", "full", outro=(286.0, DURATION)),
]

# Audio is muted while these ranges are on screen (the "20 MINUTES LATER" card).
MUTE = [(105.7, 107.7)]

# How far a zoom travels from r0 towards r1 (1.0 = all the way).
ZOOM_AMOUNT = 0.8

# ---------------------------------------------------------------- intro / vocals
# Times of the keyboard-playing parts, read from the footage (hands on keys).
REC = [
    (10.2, 23.3, "KEYBOARD PART"),
    (25.8, 38.2, "KEYBOARD PART 2"),
    (38.2, 44.4, "BASS"),
]
PLAY = [
    (23.3, 25.8, {}),
    (44.4, 48.5, {"fade": 1.2}),
]
COUNTDOWN = [(35.2, 36.0, "4"), (36.0, 36.8, "3"), (36.8, 37.6, "2"), (37.6, 38.2, "1")]

# Lyrics as shown in the Louis Cole live-session reference (reference time).
# This performance runs 6.2 s behind that recording all the way through.
LYRIC_SHIFT = 6.22
LYRICS = [
    (45.5, 46.5, "IF LIFE IS ASKING,"),
    (46.5, 47.25, "HERE'S WHAT'S UP:"),
    (47.25, 48.0, "I WOULD RATHER"),
    (48.0, 48.75, "F--- IT UP"),
    (49.0, 49.75, "EASY, SAFE, AND"),
    (49.75, 50.5, "DREAMS WITH DUST"),
    (50.5, 51.5, "I WOULD RATHER"),
    (51.5, 52.25, "F--- IT UP"),
    (52.25, 53.0, "IF LIFE IS ASKING,"),
    (53.0, 54.0, "HERE'S WHAT'S UP:"),
    (54.0, 54.75, "I WOULD RATHER"),
    (54.75, 55.5, "F--- IT UP"),
    (55.75, 56.5, "EASY, SAFE, AND"),
    (56.5, 57.25, "DREAMS WITH DUST"),
    (57.25, 58.0, "I WOULD RATHER"),
    (58.0, 58.75, "F--- IT UP"),
    (59.0, 60.25, "I DON'T KNOW WHAT I'M DOING"),
    (60.25, 61.5, "BUT I WANT TO LIVE"),
    (62.25, 63.5, "I DON'T KNOW WHAT I'M DOING"),
    (63.5, 65.0, "BUT I WANT TO-O-O-O LIVE"),
    (65.75, 66.75, "I DON'T KNOW WHAT I'M DOING"),
    (66.75, 68.25, "BUT I WANT TO LIVE"),
    (72.25, 73.25, "IF LIFE IS ASKING,"),
    (73.25, 74.0, "HERE'S WHAT'S UP:"),
    (74.0, 74.75, "I WOULD RATHER"),
    (74.75, 75.5, "F--- IT UP"),
    (75.75, 76.5, "EASY, SAFE, AND"),
    (76.5, 77.25, "DREAMS WITH DUST"),
    (77.25, 78.0, "I WOULD RATHER"),
    (78.0, 79.75, "F--- IT UUUUUUUU..."),
    (79.75, 84.5, "UUUUUUUU..."),
]

# ---------------------------------------------------------------- text
# style: "center" / "bottomleft" / "rec" / "play" / "label"
TEXTS = [
    dict(t0=1.4, t1=7.2, text="2026", pos=("center", 540), size=56),
    dict(t0=10.4, t1=13.4, text="F IT UP\nBY: LOUIS COLE", pos=("left", 760), size=40),
    # REC (red) only while the singer is actually playing the keyboard,
    # PLAY (green) while he is at the laptop / walking to the mic
    *[dict(t0=a, t1=b, kind="rec", text=x) for a, b, x in REC],
    *[dict(t0=a, t1=b, kind="play", **kw) for a, b, kw in PLAY],
    # 4-3-2-1 countdown before the bass part (reference 0:29-0:32, +6.2 s)
    *[dict(t0=a, t1=b, text=d, pos=("center", 500), size=112, glow=False)
      for a, b, d in COUNTDOWN],
    dict(t0=49.1, t1=50.8, text="LOUIS COLE", pos=("center", 520), size=64, fadein=0.15, fade=0.5),
    *[dict(t0=a + LYRIC_SHIFT, t1=b + LYRIC_SHIFT, kind="lyric", text=x) for a, b, x in LYRICS],
    dict(t0=75.1, t1=77.1, text="THROAT SLAP VOCAL RUN", pos=("center", 800), size=40),
    dict(t0=77.2, t1=77.8, text="YEAH", pos=("center", 540), size=56),
    dict(t0=77.9, t1=78.7, text="YEAH", pos=("center", 540), size=56),
    dict(t0=86.6, t1=105.5, text="FF>>", pos=("center", 900), size=44),
    dict(t0=105.7, t1=107.7, text="20 MINUTES LATER", pos=("center", 540), size=44),
    dict(t0=119.2, t1=120.6, text="EVERYONE", pos=("center", 420), size=48),
    dict(t0=133.4, t1=135.4, text="KAZUHO", pos=("center", 200), size=48),
    dict(t0=136.8, t1=138.8, text="IZUSHUN", pos=("center", 200), size=48),
    dict(t0=139.8, t1=142.2, text="KAZUHO\nAND\nIZUSHUN", pos=("center", 470), size=48),
    dict(t0=167.9, t1=169.7, text="IZUSHUN", pos=("center", 800), size=48),
    dict(t0=169.9, t1=171.7, text="BASS FILL APPROVED", pos=("center", 520), size=44),
    dict(t0=229.4, t1=232.6, text="KAESUKE", pos=("center", 780), size=48),
    dict(t0=204.2, t1=216.6, text="HORN BREAKDOWN", pos=(530, 640), size=32, fade=1.4),
    dict(t0=280.2, t1=281.8, text="THEY LOVE IT", pos=("center", 760), size=48),
]
