"""Edit decision list for song 2, "FAILING IN A COOL WAY".

Timeline time == time in the wide (fixed) camera, whose audio is the master track.
The handheld camera started 100.6 s earlier (audio cross-correlation), so
handheld time = timeline time + 100.6, i.e. HAND_OFFSET = -100.6.
The handheld recording ends at timeline 259.18 s, so only "W" is used after that.

Captions are retimed from the reference (Louis Cole live video of the song):
verse 1 runs 7.92 s later here, verse 2 7.70 s later (measured per section).
"""

OUTPUT_NAME = "failing_in_a_cool_way_edit"
HAND_OFFSET = -100.6
DURATION = 274.0
FPS = 30
W, H = 1920, 1080
ZOOM_AMOUNT = 0.8
MUTE = []

WR = {
    "full":      (0, 0, 1920, 1080),
    "stage":     (100, 200, 1700, 956),
    "keys":      (120, 400, 560, 315),
    "bass":      (330, 300, 720, 405),
    "bass_tight": (420, 340, 512, 288),
    "left2":     (40, 260, 1000, 562),
    "drums":     (800, 460, 512, 288),
    "center":    (960, 340, 560, 315),
    "horns":     (960, 340, 960, 540),
    "saxes":     (1020, 420, 800, 450),
    "shiori":    (1360, 470, 448, 252),
    "towaco":    (956, 480, 448, 252),
    "kotomi":    (1136, 480, 448, 252),
    # portrait crops for the solo layout
    "shiori_p":  (1340, 440, 480, 505),
    "towaco_p":  (940, 440, 480, 505),
    "kotomi_p":  (1120, 440, 480, 505),
}

HR = {
    "full":      (0, 0, 1920, 1080),
    "lower":     (0, 160, 1600, 900),
    "keys":      (0, 420, 560, 315),
    "bass":      (300, 330, 640, 360),
    "left2":     (0, 280, 1100, 619),
    "center":    (900, 380, 720, 405),
    "horns":     (1000, 360, 920, 518),
    "saxes":     (1080, 420, 840, 473),
    "shiori":    (1425, 400, 533, 300),
    "towaco":    (1025, 400, 533, 300),
    "kotomi":    (1200, 400, 533, 300),
    "shiori_p":  (1450, 380, 480, 505),
    "towaco_p":  (1050, 380, 480, 505),
    "kotomi_p":  (1225, 380, 480, 505),
}


def S(t0, t1, src, r0, r1=None, **kw):
    return dict(t0=t0, t1=t1, kind="single", src=src, r0=r0, r1=r1 or r0, **kw)


def GRID(t0, t1, panels, **kw):
    return dict(t0=t0, t1=t1, kind="grid", panels=panels, **kw)


# Inset in the top-left corner (reference uses a small portrait inset here).
PIP_TL = (60, 50, 300, 400)


def SOLO(t0, t1, name, big_src="W"):
    """Reference sax-solo layout: big left panel, small top-right, wide bottom-right."""
    other = "H" if big_src == "W" else "W"
    return GRID(t0, t1, [
        (big_src, name + "_p", (20, 20, 990, 1040)),
        (other, name + "_p", (1290, 50, 380, 430)),
        ("W", "drums", (1050, 560, 840, 470)),
    ])


SHOTS = [
    # intro
    S(0.0, 11.8, "W", "full", "stage", fadein=1.2),
    S(11.8, 15.0, "H", "horns", "saxes"),
    S(15.0, 19.0, "W", "center", "center"),
    S(19.0, 25.5, "H", "center", "horns", pip=("W", "keys", PIP_TL)),
    # verse 1
    S(25.5, 28.7, "W", "bass", "bass_tight", pip=("H", "saxes", PIP_TL)),
    S(28.7, 31.9, "H", "left2", "bass", pip=("W", "horns", PIP_TL)),
    S(31.9, 35.1, "W", "horns", "saxes", pip=("H", "bass", PIP_TL)),
    S(35.1, 38.3, "H", "bass", "bass", pip=("W", "center", PIP_TL)),
    S(38.3, 41.5, "W", "stage", "full"),
    S(41.5, 44.7, "H", "center", "center"),
    S(44.7, 47.9, "W", "keys", "keys"),
    S(47.9, 50.5, "H", "saxes", "horns"),
    # build
    S(50.5, 53.7, "W", "full", "stage"),
    S(53.7, 56.5, "H", "horns", "horns"),
    S(56.5, 62.0, "W", "stage", "full"),        # "(we ran out of camera angles)"
    # riff
    S(62.0, 65.2, "H", "lower", "full"),
    S(65.2, 68.4, "W", "horns", "saxes"),
    S(68.4, 72.0, "H", "saxes", "saxes"),
    S(72.0, 73.4, "W", "full", "full"),
    S(73.4, 77.0, "W", "bass", "bass_tight"),   # IZUSHUN
    S(77.0, 80.2, "H", "horns", "horns"),
    S(80.2, 83.4, "W", "left2", "left2"),
    S(83.4, 88.0, "W", "full", "stage"),
    # verse 2
    S(88.0, 91.2, "H", "center", "center"),
    S(91.2, 94.4, "W", "bass", "bass_tight"),
    S(94.4, 97.6, "H", "horns", "saxes"),
    S(97.6, 100.8, "W", "keys", "keys"),
    S(100.8, 104.0, "H", "bass", "bass"),
    S(104.0, 107.2, "W", "center", "center"),
    S(107.2, 110.4, "H", "saxes", "saxes"),
    S(110.4, 113.6, "W", "stage", "full"),
    S(113.6, 116.8, "H", "left2", "left2"),
    S(116.8, 120.0, "W", "horns", "saxes"),
    S(120.0, 123.2, "H", "bass", "bass"),
    S(123.2, 127.0, "W", "full", "stage"),
    # riser -> big riff
    S(127.0, 130.2, "W", "stage", "full"),
    S(130.2, 133.4, "H", "full", "lower"),
    S(133.4, 136.6, "W", "drums", "drums"),
    S(136.6, 139.5, "H", "center", "center"),
    S(139.5, 141.1, "W", "full", "full"),
    S(141.1, 144.3, "H", "horns", "horns"),
    S(144.3, 148.0, "W", "saxes", "horns"),
    S(148.0, 152.0, "W", "full", "full"),
    S(152.0, 155.2, "H", "left2", "left2"),
    S(155.2, 158.4, "W", "horns", "saxes"),
    S(158.4, 162.0, "H", "bass", "bass"),
    S(162.0, 164.0, "W", "full", "full"),
    S(164.0, 167.2, "H", "saxes", "saxes"),
    S(167.2, 174.5, "W", "bass", "bass_tight", pip=("H", "horns", (60, 50, 420, 236))),
    S(174.5, 177.0, "W", "full", "full", dim=0.6),
    S(177.0, 180.2, "H", "full", "lower"),
    S(180.2, 183.4, "W", "horns", "saxes"),
    S(183.4, 187.0, "H", "center", "saxes"),
    # sax solos: SHIORI 3:07, TOWACO 3:36, KOTOMI 3:54, until 4:06
    SOLO(187.0, 199.0, "shiori", "W"),
    S(199.0, 203.0, "H", "shiori", "shiori"),
    S(203.0, 207.0, "W", "saxes", "shiori"),
    SOLO(207.0, 216.0, "shiori", "H"),
    S(216.0, 222.0, "H", "towaco", "towaco"),
    SOLO(222.0, 230.0, "towaco", "W"),
    S(230.0, 234.0, "W", "saxes", "towaco"),
    S(234.0, 238.0, "W", "kotomi", "kotomi"),
    SOLO(238.0, 243.0, "kotomi", "H"),
    S(243.0, 246.0, "H", "saxes", "kotomi"),
    # everyone back in
    S(246.0, 249.2, "W", "full", "stage"),
    S(249.2, 252.4, "H", "horns", "horns"),
    S(252.4, 255.5, "W", "left2", "left2"),
    S(255.5, 257.5, "W", "full", "full"),
    S(257.5, 259.0, "H", "center", "center"),   # handheld ends at 259.18
    S(259.0, 262.2, "W", "stage", "full"),
    S(262.2, 265.0, "W", "horns", "saxes"),
    S(265.0, 267.5, "W", "center", "center"),
    S(267.5, DURATION, "W", "full", "full", fadeout=3.0),
]

# ---------------------------------------------------------------- text
CYAN = (90, 235, 240)
LYR_Y = 960
LYR = dict(pos=("center", LYR_Y), size=32, color=CYAN, glow=False)

# (reference on, reference off, text)
VERSE1 = [
    (17.8, 19.4, "I LIKE MY FREAKY SECRETS"),
    (19.4, 21.0, "I LIKE TO STAY UP LATE"),
    (21.0, 22.1, "I LIKE TO SEARCH THE NET"),
    (22.1, 23.3, "FOR BAD PICTURES"),
    (23.3, 24.0, "OF YOUR FACE"),
    (24.2, 25.3, "I LIKE IT WHEN YOU TOUCH ME"),
    (25.8, 26.9, "LIKE I'M YOUR UGLY FRIEND"),
    (27.4, 29.2, "I LIKE TO WRITE YOU F----D UP MESSAGES"),
    (29.2, 30.4, "WITHOUT PRESSING SEND"),
    (30.6, 31.8, "I USED TO BAG YOUR GROCERIES"),
    (32.2, 33.4, "I USED TO SMASH YOUR EGGS"),
    (33.8, 34.9, "GO HOME AND WORK"),
    (34.9, 36.1, "TO HUNT AND KILL"),
    (36.1, 36.7, "MY FATE"),
    (37.0, 38.1, "I LIKE IT WHEN YOU FAIL"),
    (38.6, 39.7, "I LIKE THAT THAT'S OK"),
    (40.1, 41.3, "I LIKE THAT I AM FAILING"),
    (41.7, 42.9, "BUT IN A COOLER WAY"),
]
VERSE2 = [
    (94.5, 95.7, "YOU KNOW I DON'T RESPECT YOU"),
    (96.1, 97.3, "BECAUSE YOUR MUSIC SUCKS"),
    (97.7, 98.9, "NOBODY REALLY HEARS YOU"),
    (99.1, 99.8, "JUST DESPERATE"),
    (99.8, 100.5, "TO GET F----D"),
    (100.9, 101.4, "I CAME FROM"),
    (101.4, 102.3, "NOTHING TO SOMETHING"),
    (102.4, 103.0, "UNLESS IT'S"),
    (103.0, 103.6, "MONEY YOU MEANT"),
    (104.0, 104.5, "I CAME FROM"),
    (104.5, 105.4, "SOMETHING TO NOTHING"),
    (105.5, 106.4, "DISCUSSING HOW TO"),
    (106.4, 107.0, "PAY THE RENT"),
    (107.1, 108.3, "I USED TO BAG YOUR GROCERIES"),
    (108.7, 109.9, "I USED TO SMASH YOUR EGGS"),
    (110.2, 111.3, "GO HOME AND WORK"),
    (111.3, 112.5, "TO HUNT AND KILL"),
    (112.5, 113.1, "MY FATE"),
    (113.4, 114.5, "I LIKE IT WHEN YOU FAIL"),
    (115.0, 116.2, "I LIKE THAT THAT'S OK"),
    (116.5, 117.7, "I LIKE THAT I AM FAILING"),
    (118.1, 119.2, "BUT IN A COOLER WAY"),
]
VERSE1_SHIFT = 7.92
VERSE2_SHIFT = 7.70

NAME = dict(pos=(515, 960), size=40)   # name inside the big left solo panel

TEXTS = [
    dict(t0=1.0, t1=11.8, text="FAILING IN A COOL WAY\nBY: LOUIS COLE", pos=("left", 960), size=32),
    *[dict(t0=a + VERSE1_SHIFT, t1=b + VERSE1_SHIFT, text=s, **LYR) for a, b, s in VERSE1],
    dict(t0=56.6, t1=60.2, text="(we ran out of camera angles)", pos=("center", 460), size=32),
    dict(t0=73.6, t1=76.4, text="IZUSHUN", pos=("center", 840), size=44),
    *[dict(t0=a + VERSE2_SHIFT, t1=b + VERSE2_SHIFT, text=s, **LYR) for a, b, s in VERSE2],
    # sax solos
    dict(t0=187.2, t1=199.0, text="SHIORI", **NAME),
    dict(t0=187.2, t1=199.0, text="GROOVE ZONE", pos=(1480, 505), size=16, glow=False),
    dict(t0=207.0, t1=216.0, text="SHIORI", **NAME),
    dict(t0=207.0, t1=216.0, text="GROOVE ZONE", pos=(1480, 505), size=16, glow=False),
    dict(t0=216.2, t1=219.6, text="TOWACO", pos=("center", 900), size=44),
    dict(t0=222.0, t1=230.0, text="TOWACO", **NAME),
    dict(t0=222.0, t1=230.0, text="GROOVE ZONE", pos=(1480, 505), size=16, glow=False),
    dict(t0=223.2, t1=225.0, text="SO HD", pos=("center", 500), size=128),
    dict(t0=234.2, t1=237.6, text="KOTOMI", pos=("center", 900), size=44),
    dict(t0=238.0, t1=243.0, text="KOTOMI", **NAME),
    dict(t0=238.0, t1=243.0, text="GROOVE ZONE", pos=(1480, 505), size=16, glow=False),
    dict(t0=266.6, t1=267.8, text="YEAH", pos=("center", 600), size=32),
]
