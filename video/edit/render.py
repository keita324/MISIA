"""Frame-by-frame renderer for the EDL in edl.py.

usage: python3 render.py WIDE HAND OUT_DIR [--start S --end E] [--scale 0.5]
Renders the [start, end) slice to OUT_DIR/chunk_<start>.mp4 (video only).
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "PressStart2P-Regular.ttf")


# ------------------------------------------------------------------ sources
class Reader:
    """Sequential raw RGB frames at edl.FPS from `path`, starting at `t0` seconds."""

    def __init__(self, path, t0, w, h):
        self.w, self.h = w, h
        self.size = w * h * 3
        self.pad = 0
        if t0 < 0:
            self.pad = int(round(-t0 * edl.FPS))
            t0 = 0
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", path, "-an",
               "-vf", f"fps={edl.FPS},scale={w}:{h}:flags=bicubic", "-f", "rawvideo",
               "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=self.size * 2)
        self.last = Image.new("RGB", (w, h))

    def read(self):
        if self.pad > 0:
            self.pad -= 1
            return self.last
        buf = self.p.stdout.read(self.size)
        if len(buf) == self.size:
            self.last = Image.frombuffer("RGB", (self.w, self.h), buf, "raw", "RGB", 0, 1)
        return self.last  # hold last frame once the source runs out

    def close(self):
        self.p.stdout.close()
        self.p.kill()


# ------------------------------------------------------------------ helpers
def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp_rect(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(4))


def fit_aspect(rect, aspect):
    """Shrink rect around its centre so that w/h == aspect."""
    x, y, w, h = rect
    if w / h > aspect:
        nw = h * aspect
        return (x + (w - nw) / 2, y, nw, h)
    nh = w / aspect
    return (x, y + (h - nh) / 2, w, nh)


def grab(frame, rect, size, scale):
    x, y, w, h = (v * scale for v in rect)
    x = min(max(x, 0), frame.width - w)
    y = min(max(y, 0), frame.height - h)
    return frame.resize(size, Image.BICUBIC, box=(x, y, min(x + w, frame.width), min(y + h, frame.height)))


def sharpen(img):
    return img.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))


# ------------------------------------------------------------------ text
_font_cache = {}


def font(size):
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FONT, size)
    return _font_cache[size]


def draw_pixel_text(canvas, text, pos, size, alpha=1.0, color=(255, 255, 255), glow=True):
    """Draw crisp bitmap text with a dark drop shadow and a soft glow."""
    if alpha <= 0 or not text:
        return
    S = canvas.width / edl.W
    size = max(8, int(round(size * S / 8)) * 8) if S >= 1 else max(8, int(size * S))
    f = font(size)
    lines = text.split("\n")
    lh = int(size * 1.35)
    widths = [f.getbbox(l)[2] if l else 0 for l in lines]
    bw, bh = max(widths), lh * len(lines)
    px, py = pos
    py = py * S
    if px == "center":
        x0 = (canvas.width - bw) / 2
    elif px == "left":
        x0 = 60 * S
    else:
        x0 = px * S - bw / 2
    y0 = py - bh / 2
    layer = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(layer)
    d.fontmode = "1"  # no anti-aliasing: real pixel edges
    for i, line in enumerate(lines):
        lx = x0 if px == "left" else x0 + (bw - widths[i]) / 2
        d.text((int(lx), int(y0 + i * lh)), line, font=f, fill=255)
    a = int(255 * alpha)
    shadow = layer.point(lambda v: int(v * 0.85 * alpha))
    off = max(2, int(size / 10))
    canvas.paste((0, 0, 0), (off, off), shadow)
    if glow:
        g = layer.filter(ImageFilter.GaussianBlur(size * 0.35)).point(lambda v: int(min(255, v * 0.9) * alpha))
        canvas.paste(color, (0, 0), g)
    canvas.paste(color, (0, 0), layer.point(lambda v: int(v * a / 255)))


def typed(text, t, t0, cps=28):
    n = int((t - t0) * cps)
    out, count = [], 0
    for ch in text:
        if ch in " \n":
            out.append(ch)
            continue
        if count >= n:
            break
        out.append(ch)
        count += 1
    return "".join(out)


PIX_DOT = [
    "..####..",
    ".######.",
    "########",
    "########",
    "########",
    "########",
    ".######.",
    "..####..",
]
PIX_PLAY = [
    "##......",
    "####....",
    "######..",
    "########",
    "########",
    "######..",
    "####....",
    "##......",
]


def draw_icon(canvas, pattern, cx, cy, cell, color, alpha):
    if alpha <= 0:
        return
    S = canvas.width / edl.W
    cell = max(1, int(cell * S))
    n = len(pattern)
    x0, y0 = int(cx * S - n * cell / 2), int(cy * S - n * cell / 2)
    d = ImageDraw.Draw(canvas, "RGBA")
    for j, row in enumerate(pattern):
        for i, c in enumerate(row):
            if c == "#":
                d.rectangle([x0 + i * cell + 2, y0 + j * cell + 2, x0 + (i + 1) * cell + 1, y0 + (j + 1) * cell + 1],
                            fill=(0, 0, 0, int(160 * alpha)))
    for j, row in enumerate(pattern):
        for i, c in enumerate(row):
            if c == "#":
                d.rectangle([x0 + i * cell, y0 + j * cell, x0 + (i + 1) * cell - 1, y0 + (j + 1) * cell - 1],
                            fill=color + (int(255 * alpha),))


def render_texts(canvas, t):
    for tx in edl.TEXTS:
        t0, t1 = tx["t0"], tx["t1"]
        if not (t0 <= t < t1):
            continue
        fade = tx.get("fade", 0.0)
        alpha = 1.0
        if fade and t > t1 - fade:
            alpha = (t1 - t) / fade
        kind = tx.get("kind", "text")
        if kind == "rec":
            draw_icon(canvas, PIX_DOT, 150, 950, 7, (230, 20, 30), alpha)
            if t < tx.get("text_until", t1):
                _left_text(canvas, tx["text"], 200, 950, 32, alpha, (235, 30, 40))
        elif kind == "play":
            draw_icon(canvas, PIX_PLAY, 150, 950, 7, (40, 235, 60), alpha)
        else:
            # text simply appears and disappears (no typewriter); type=True opts in
            s = typed(tx["text"], t, t0) if tx.get("type") else tx["text"]
            draw_pixel_text(canvas, s, tx["pos"], tx["size"], alpha)
    return canvas


def _left_text(canvas, text, x, y, size, alpha, color):
    """Left-aligned single line, vertically centred on y."""
    if not text:
        return
    S = canvas.width / edl.W
    size = max(8, int(round(size * S / 8)) * 8) if S >= 1 else max(8, int(size * S))
    f = font(size)
    layer = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(layer)
    d.fontmode = "1"
    d.text((int(x * S), int(y * S - size / 2)), text, font=f, fill=255)
    off = max(2, int(size / 10))
    canvas.paste((0, 0, 0), (off, off), layer.point(lambda v: int(v * 0.85 * alpha)))
    canvas.paste(color, (0, 0), layer.point(lambda v: int(v * alpha)))


def draw_label(canvas, text, pos):
    """Small light box with dark pixel text (reference: BASSLINE BUDDIEZ tag)."""
    S = canvas.width / edl.W
    size = 24 if S >= 1 else max(8, int(24 * S))
    f = font(size)
    lines = text.split("\n")
    lh = int(size * 1.4)
    bw = max(f.getbbox(l)[2] for l in lines) + int(16 * S)
    bh = lh * len(lines) + int(10 * S)
    x, y = int(pos[0] * S - bw / 2), int(pos[1] * S - bh / 2)
    d = ImageDraw.Draw(canvas)
    d.fontmode = "1"
    d.rectangle([x, y, x + bw, y + bh], fill=(232, 232, 232))
    for i, l in enumerate(lines):
        lw = f.getbbox(l)[2]
        d.text((x + (bw - lw) // 2, y + int(6 * S) + i * lh), l, font=f, fill=(30, 30, 30))


# ------------------------------------------------------------------ compositing
def compose(shot, t, frames, out_w, out_h, scale):
    src_scale = scale
    k = ease((t - shot["t0"]) / max(1e-6, shot["t1"] - shot["t0"]))
    S = out_w / edl.W
    if shot["kind"] == "black":
        return Image.new("RGB", (out_w, out_h))
    if shot["kind"] == "single":
        rects = edl.WR if shot["src"] == "W" else edl.HR
        r = lerp_rect(rects[shot["r0"]], rects[shot["r1"]], k * edl.ZOOM_AMOUNT)
        img = grab(frames[shot["src"]], r, (out_w, out_h), src_scale)
        if r[2] < 1500:
            img = sharpen(img)
        if shot.get("dim"):
            img = Image.blend(Image.new("RGB", img.size), img, shot["dim"])
        if shot.get("pip"):
            src, rn, (px, py, pw, ph) = shot["pip"]
            rr = (edl.WR if src == "W" else edl.HR)[rn]
            rr = fit_aspect(rr, pw / ph)
            box = (int(px * S), int(py * S), int(pw * S), int(ph * S))
            p = grab(frames[src], rr, (box[2], box[3]), src_scale)
            d = ImageDraw.Draw(img)
            b = max(1, int(4 * S))
            d.rectangle([box[0] - b, box[1] - b, box[0] + box[2] + b - 1, box[1] + box[3] + b - 1], fill=(240, 240, 240))
            img.paste(p, (box[0], box[1]))
        if shot.get("outro"):
            o0, o1 = shot["outro"]
            if t >= o0:
                img = outro(img, (t - o0) / (o1 - o0))
        return img
    if shot["kind"] == "grid":
        img = Image.new("RGB", (out_w, out_h), (6, 6, 8))
        d = ImageDraw.Draw(img)
        for i, (src, rn, (px, py, pw, ph)) in enumerate(shot["panels"]):
            # stagger panels in, game-menu style (not when continuing a layout)
            if not shot.get("cont") and t < shot["t0"] + 0.12 * i:
                continue
            rr = (edl.WR if src == "W" else edl.HR)[rn]
            # gentle drift inside each panel; none on a continued layout so the
            # panels that stay on screen do not jump at the cut
            z = 0.0 if (shot.get("cont") or shot.get("still")) else k * edl.ZOOM_AMOUNT
            zr = (rr[0] + rr[2] * 0.04 * z, rr[1] + rr[3] * 0.04 * z, rr[2] * (1 - 0.08 * z), rr[3] * (1 - 0.08 * z))
            zr = fit_aspect(zr, pw / ph)
            box = (int(px * S), int(py * S), int(pw * S), int(ph * S))
            p = sharpen(grab(frames[src], zr, (box[2], box[3]), src_scale))
            b = max(1, int(4 * S))
            d.rectangle([box[0] - b, box[1] - b, box[0] + box[2] + b - 1, box[1] + box[3] + b - 1], fill=(235, 235, 235))
            img.paste(p, (box[0], box[1]))
        if shot.get("label"):
            draw_label(img, *shot["label"])
        return img
    raise ValueError(shot["kind"])


def outro(img, x):
    """Picture shrinks, tilts and drops away (reference ending)."""
    x = ease(x)
    W_, H_ = img.size
    s = 1 - 0.82 * x
    small = img.resize((max(2, int(W_ * s)), max(2, int(H_ * s))), Image.BICUBIC)
    small = small.rotate(-12 * x, resample=Image.BICUBIC, expand=True)
    out = Image.new("RGB", (W_, H_))
    cx = W_ / 2 + 0.05 * W_ * x
    cy = H_ / 2 + 0.12 * H_ * x
    out.paste(small, (int(cx - small.width / 2), int(cy - small.height / 2)),
              small.convert("L").point(lambda v: 255))
    if x > 0.85:
        out = Image.blend(out, Image.new("RGB", out.size), (x - 0.85) / 0.15)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wide")
    ap.add_argument("hand")
    ap.add_argument("out")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=edl.DURATION)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--crf", default="16")
    a = ap.parse_args()

    out_w, out_h = int(edl.W * a.scale) // 2 * 2, int(edl.H * a.scale) // 2 * 2
    f0 = int(round(a.start * edl.FPS))
    f1 = int(round(a.end * edl.FPS))
    wr = Reader(a.wide, f0 / edl.FPS, out_w if a.scale < 1 else edl.W, out_h if a.scale < 1 else edl.H)
    hr = Reader(a.hand, f0 / edl.FPS - edl.HAND_OFFSET, wr.w, wr.h)
    os.makedirs(a.out, exist_ok=True)
    out_path = os.path.join(a.out, f"chunk_{f0:06d}.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{out_w}x{out_h}", "-r", str(edl.FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", a.crf,
                            "-pix_fmt", "yuv420p", out_path], stdin=subprocess.PIPE)
    shots = edl.SHOTS
    si = 0
    src_scale = wr.w / edl.W
    for fi in range(f0, f1):
        t = fi / edl.FPS
        frames = {"W": wr.read(), "H": hr.read()}
        while si < len(shots) - 1 and t >= shots[si]["t1"]:
            si += 1
        while si > 0 and t < shots[si]["t0"]:
            si -= 1
        img = compose(shots[si], t, frames, out_w, out_h, src_scale)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = render_texts(img, t)
        enc.stdin.write(img.tobytes())
        if (fi - f0) % 300 == 0:
            print(f"[{a.start:.1f}] t={t:.1f}", flush=True)
    enc.stdin.close()
    enc.wait()
    wr.close()
    hr.close()


if __name__ == "__main__":
    main()
