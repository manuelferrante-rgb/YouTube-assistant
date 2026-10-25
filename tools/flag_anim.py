#!/usr/bin/env python3
"""Bandiera che sventola (grafica generata, niente stock): stoffa con onde, pieghe e luce.

    python3 tools/flag_anim.py out.mp4 --kind ldf|udf [--w 1080 --h 1920 --dur 3]
ldf: rossa con falce, martello e stella bianchi (stile bandiera CPI(M) in Kerala).
udf: tricolore del Congresso (zafferano, bianco, verde), senza simboli inventati.
"""
import argparse, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

FONT_SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FPS = 30


def cloth(kind, fw, fh):
    im = Image.new("RGB", (fw, fh))
    d = ImageDraw.Draw(im)
    if kind == "ldf":
        d.rectangle([0, 0, fw, fh], fill=(196, 22, 28))
        f = ImageFont.truetype(FONT_SYM, int(fh * 0.55))
        d.text((fw * 0.30, fh * 0.52), "☭", font=f, fill=(250, 250, 250), anchor="mm")
        # stella a cinque punte sopra il simbolo
        cx, cy, r = fw * 0.30, fh * 0.16, fh * 0.07
        pts = []
        for i in range(10):
            a = -np.pi / 2 + i * np.pi / 5
            rr = r if i % 2 == 0 else r * 0.4
            pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
        d.polygon(pts, fill=(250, 250, 250))
    else:
        for i, c in enumerate([(255, 153, 51), (250, 250, 250), (19, 136, 8)]):
            d.rectangle([0, fh * i / 3, fw, fh * (i + 1) / 3], fill=c)
    return np.asarray(im).astype(np.float32) / 255


def render(out, kind, W, H, dur, bg=(14, 14, 18), fill=False):
    if fill:   # primo piano: la stoffa riempie lo schermo, centrata sul simbolo
        fh = int(H * 1.12); fw = int(fh * 1.5)
        focus = 0.30 if kind == "ldf" else 0.5
        offx = focus * fw - W / 2
    else:
        fw, fh = int(W * 1.05), int(W * 1.05 * 2 / 3)
        offx = 0.0
    tex = cloth(kind, fw, fh)
    oy = (H - fh) / 2
    X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    u = (X + offx) / fw if fill else X / W    # 0 all'asta, 1 al bordo libero
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
                             "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = 1 - 0.45 * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.6 - 0.2, 0, 1)
    bgimg = (np.array(bg, np.float32) / 255)[None, None, :] * vign[..., None]
    for n in range(int(dur * FPS)):
        t = n / FPS
        amp = (0.45 + 0.55 * u) if fill else u ** 1.3   # l'onda cresce allontanandosi dall'asta
        ph = 2 * np.pi * (1.6 * u - 0.9 * t)
        ph2 = 2 * np.pi * (2.7 * u - 1.4 * t + 0.3 * Y / H)
        dy = (0.030 * H * np.sin(ph) + 0.010 * H * np.sin(ph2)) * amp
        dx = -0.012 * W * (1 - np.cos(ph)) * amp
        # coordinate nella stoffa
        sx = (X - dx + offx) if fill else (X - dx) / W * fw
        sy = (Y - oy - dy)
        inside = (sx >= 0) & (sx < fw - 1) & (sy >= 0) & (sy < fh - 1)
        col = cv2.remap(tex, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT)
        # luce: pendenza dell'onda -> pieghe chiare e scure
        slope = (np.cos(ph) * 1.6 + 0.35 * np.cos(ph2) * 2.7) * amp
        shade = np.clip(1 + 0.22 * slope, 0.55, 1.35)[..., None]
        frame = np.where(inside[..., None], col * shade, bgimg)
        proc.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
    proc.stdin.close(); proc.wait()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--kind", default="ldf")
    ap.add_argument("--w", type=int, default=1080); ap.add_argument("--h", type=int, default=1920)
    ap.add_argument("--dur", type=float, default=3.0); ap.add_argument("--fill", action="store_true")
    a = ap.parse_args()
    render(a.out, a.kind, a.w, a.h, a.dur, fill=a.fill)
