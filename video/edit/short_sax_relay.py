"""YouTube Shorts cut (1080x1920): the song-2 sax solo relay as a 3-player game.

usage: python3 short_sax_relay.py WIDE HAND OUT.mp4 [--scale 0.5]

Layout (top to bottom): title, the whole horn section (16:9), a close-up of the
current soloist, then "PLAYER n" and three progress blocks.
When everyone comes back in (4:06) the lower panel shows the whole band.
Times are song-2 timeline times (wide camera), see edl_song2.py.
"""
import argparse
import os
import subprocess
import sys

os.environ.setdefault("EDL", "edl_song2.py")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

edl = render.edl
T0, T1 = 187.0, 249.0          # 3:07 solo starts ... band back in at 4:06, + outro
OW, OH = 1080, 1920

YELLOW, CYAN, PINK, WHITE = (255, 220, 60), (90, 235, 240), (255, 110, 190), (255, 255, 255)

# soloist close-ups in the fixed camera: (centre x, centre y, height)
# players 1-3 = SHIORI, TOWACO, KOTOMI (names are not shown in the Short)
PLAYERS = [
    dict(t0=187.0, t1=216.0, n=1, color=YELLOW, c=(1580, 690, 420)),
    dict(t0=216.0, t1=234.0, n=2, color=CYAN, c=(1170, 700, 420)),
    dict(t0=234.0, t1=246.0, n=3, color=PINK, c=(1360, 690, 420)),
]
CLEAR_AT = 246.0

# top panel: alternate the two cameras every 4 bars (6.4 s at 150 bpm)
TOP_SHOTS = [("W", "horns"), ("H", "saxes")]
TOP_BOX = (40, 330, 1000, 562)
SOLO_BOX = (40, 940, 1000, 760)


def player_at(t):
    for p in PLAYERS:
        if p["t0"] <= t < p["t1"]:
            return p
    return None


def solo_rect(p, t, aspect):
    cx, cy, h = p["c"]
    # slow push-in over the player's turn
    k = render.ease((t - p["t0"]) / (p["t1"] - p["t0"])) * edl.ZOOM_AMOUNT
    h = h * (1 - 0.18 * k)
    w = h * aspect
    return (cx - w / 2, cy - h / 2, w, h)


def framed(canvas, img, box, s):
    x, y, w, h = (int(v * s) for v in box)
    b = max(1, int(5 * s))
    ImageDraw.Draw(canvas).rectangle([x - b, y - b, x + w + b - 1, y + h + b - 1], fill=(235, 235, 235))
    canvas.paste(img, (x, y))


def text(canvas, s, pos, size, color=WHITE, alpha=1.0, glow=True):
    # draw_pixel_text scales by canvas.width / edl.W, so convert to its 1920-wide space
    k = edl.W / OW
    x = pos[0] if isinstance(pos[0], str) else pos[0] * k
    render.draw_pixel_text(canvas, s, (x, pos[1] * k), size * k, alpha, color=color, glow=glow)


def compose(t, frames, s):
    c = Image.new("RGB", (int(OW * s), int(OH * s)), (8, 8, 14))
    src_scale = frames["W"].width / edl.W

    # title
    text(c, "LOUIS COLE", ("center", 80), 56)
    text(c, "FAILING IN A COOL WAY", ("center", 165), 28, CYAN, glow=False)
    text(c, "SAX SOLO RELAY", ("center", 250), 40, YELLOW)

    clear = t >= CLEAR_AT
    # top panel
    if clear:
        src, rn = "W", "full"
    else:
        src, rn = TOP_SHOTS[int((t - T0) // 6.4) % 2]
    rects = edl.WR if src == "W" else edl.HR
    bw, bh = int(TOP_BOX[2] * s), int(TOP_BOX[3] * s)
    top = render.grab(frames[src], render.fit_aspect(rects[rn], bw / bh), (bw, bh), src_scale)
    framed(c, render.sharpen(top), TOP_BOX, s)

    # soloist / ending panel
    bw, bh = int(SOLO_BOX[2] * s), int(SOLO_BOX[3] * s)
    p = player_at(t)
    if p:
        r = solo_rect(p, t, bw / bh)
    else:  # stage clear: whole band
        r = render.fit_aspect(edl.WR["stage"], bw / bh)
    solo = render.sharpen(render.grab(frames["W"], r, (bw, bh), src_scale))
    framed(c, solo, SOLO_BOX, s)

    if p:
        dt = t - p["t0"]
        # flash at each hand-over
        if dt < 0.12 and p["n"] > 1:
            c = Image.blend(c, Image.new("RGB", c.size, WHITE), 0.6)
        if dt < 1.6:
            text(c, f"PLAYER {p['n']}", ("center", 1320), 84, p["color"])
        text(c, f"PLAYER {p['n']}", ("center", 1790), 52, p["color"])
    else:
        text(c, "ALL PLAYERS", ("center", 1790), 44)

    # progress blocks
    d = ImageDraw.Draw(c)
    for i, q in enumerate(PLAYERS):
        done = t >= q["t0"]
        x0 = int((360 + i * 130) * s)
        y0 = int(1860 * s)
        col = q["color"] if done else (60, 60, 70)
        d.rectangle([x0, y0, x0 + int(100 * s), y0 + int(24 * s)], fill=col)

    # fade out
    if t > T1 - 0.8:
        c = Image.blend(Image.new("RGB", c.size), c, max(0.0, (T1 - t) / 0.8))
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wide")
    ap.add_argument("hand")
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="18")
    a = ap.parse_args()
    s = a.scale
    ow, oh = int(OW * s) // 2 * 2, int(OH * s) // 2 * 2
    wr = render.Reader(a.wide, T0, edl.W, edl.H)
    hr = render.Reader(a.hand, T0 - edl.HAND_OFFSET, edl.W, edl.H)
    tmp = a.out + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{ow}x{oh}", "-r", str(edl.FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", a.crf,
                            "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    n = int(round((T1 - T0) * edl.FPS))
    for i in range(n):
        t = T0 + i / edl.FPS
        img = compose(t, {"W": wr.read(), "H": hr.read()}, s)
        if img.size != (ow, oh):
            img = img.resize((ow, oh))
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    wr.close()
    hr.close()
    dur = T1 - T0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ss", str(T0), "-t", str(dur), "-i", a.wide,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", f"afade=t=in:d=0.3,afade=t=out:st={dur - 0.8}:d=0.8",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out], check=True)
    os.remove(tmp)


if __name__ == "__main__":
    main()
