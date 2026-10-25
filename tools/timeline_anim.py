#!/usr/bin/env python3
"""Linea del tempo animata nello stile "carta nautica" della mappa (tools/route_map.py).

Una linea d'inchiostro si allunga da una data all'altra; ogni data compare a un tempo preciso (agganciato alla
parola del voiceover) con l'anno grande e una didascalia in corsivo; la camera scorre per tenerla in campo.
    python3 tools/timeline_anim.py out.mp4 --events "52 d.C.|l'apostolo Tommaso|secondo la tradizione|3.4;
        1584|padre Giacomo Fenicio|ricostruisce la chiesa|8.0" --dur 10 [--prev "1584"] [--w 3840 --h 2160]
--prev: date già viste in un pezzo precedente, mostrate attenuate a sinistra (continuità tra due grafiche).
"""
import argparse, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = f"{ROOT}/models"
PAPER = np.array([186, 220, 238], np.float32)       # BGR, come la terra della mappa
INK_RGB, GOLD_RGB, PAPER_RGB, SUB_RGB = (58, 46, 38), (182, 138, 75), (238, 220, 186), (120, 86, 40)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def font(name, size, var=None):
    f = ImageFont.truetype(f"{M}/{name}", int(size))
    if var:
        f.set_variation_by_name(var)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--events", required=True); ap.add_argument("--prev", default="")
    ap.add_argument("--dur", type=float, default=8.0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--w", type=int, default=3840); ap.add_argument("--h", type=int, default=2160)
    a = ap.parse_args()
    W, H, fps, D = a.w, a.h, a.fps, a.dur
    s = W / 3840
    prev = [p.strip() for p in a.prev.split(";") if p.strip()]
    ev = []
    for x in a.events.split(";"):
        f = [v.strip() for v in x.split("|")]
        ev.append(dict(year=f[0], cap=f[1], sub=f[2] if len(f) > 3 else "", t=float(f[-1])))
    SP = 1350 * s                                       # distanza tra due date sulla linea
    xs_prev = [-(len(prev) - i) * SP for i in range(len(prev))]
    xs = [i * SP for i in range(len(ev))]

    F = dict(year=font("PlayfairDisplay.ttf", 330 * s, "Bold"), cap=font("PlayfairDisplay.ttf", 104 * s, "SemiBold"),
             sub=font("PlayfairDisplay-Italic.ttf", 80 * s, "Italic"), prev=font("PlayfairDisplay.ttf", 200 * s, "Bold"))
    rng = np.random.default_rng(11)
    tex = cv2.GaussianBlur(rng.standard_normal((H // 8, W // 8)).astype(np.float32), (0, 0), 6)
    tex = cv2.resize(tex / (tex.std() + 1e-6), (W, H))[..., None]
    grain = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.8 * s + 0.3)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = (1 - 0.16 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.70)) ** 2, 0, 1) ** 1.3)[..., None]
    base = PAPER + tex * 3.5
    Y = H * 0.56                                         # quota della linea

    def cam_x(t):
        # la camera segue l'ultima data comparsa (scorrimento morbido), con una lenta deriva continua
        tgt = xs_prev[-1] if prev else -SP * 0.35
        for x, e in zip(xs, ev):
            tgt = tgt + (x - tgt) * ease((t - e["t"] + 0.5) / 1.1)
        return tgt - W * 0.62 + 40 * s * t   # la data nuova a destra, le precedenti visibili a sinistra

    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "slow",
                             "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    for i in range(int(round(D * fps))):
        t = i / fps
        cx = cam_x(t)
        img = base.copy()
        # reticolo leggero che scorre con la camera (stessa carta della mappa)
        step = 240 * s
        off = -cx % step
        for gx in np.arange(off, W, step):
            img[:, int(gx):int(gx) + max(1, int(1.5 * s))] = img[:, int(gx):int(gx) + max(1, int(1.5 * s))] * 0.965
        for gy in np.arange(0, H, step):
            img[int(gy):int(gy) + max(1, int(1.5 * s))] *= 0.965
        pil = Image.fromarray(cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # testi su un livello a parte: l'alfa sfuma davvero
        d = ImageDraw.Draw(lay)
        X = lambda x: x - cx
        # linea: dalle date precedenti fino alla data più recente, che si allunga verso la prossima
        x_start = xs_prev[-1] if prev else -SP * 0.6
        x_end = x_start + (0 - x_start) * ease_out((t - ev[0]["t"] + 0.7) / 0.7)
        if not prev:
            x_end = max(x_end, x_start + 0.3 * SP * ease_out(t / 0.8))
        for k, e in enumerate(ev[1:], 1):
            u = ease_out((t - e["t"] + 0.7) / 0.7)
            if u > 0:
                x_end = xs[k - 1] + (xs[k] - xs[k - 1]) * u
        x0 = (xs_prev[0] if prev else -SP * 0.6) - W
        d.line([(X(x0), Y), (X(x_end), Y)], fill=INK_RGB + (230,), width=int(6 * s))
        # coda tratteggiata verso il futuro
        for k in range(14):
            xa = x_end + 60 * s + k * 70 * s
            d.line([(X(xa), Y), (X(xa + 34 * s), Y)], fill=INK_RGB + (int(120 * (1 - k / 14)),), width=int(4 * s))
        for x, y in zip(xs_prev, prev):
            r = 16 * s
            d.ellipse([X(x) - r, Y - r, X(x) + r, Y + r], fill=PAPER_RGB + (255,), outline=INK_RGB + (150,), width=int(4 * s))
            d.text((X(x), Y - 70 * s), y, font=F["prev"], fill=INK_RGB + (95,), anchor="ms")
        for k, (x, e) in enumerate(zip(xs, ev)):
            pa = ease_out((t - e["t"]) / 0.35)
            if pa <= 0:
                continue
            later = [q["t"] for q in ev[k + 1:]]
            dim = 1 - 0.55 * ease((t - later[0]) / 0.5) if later else 1.0
            pop = 1 + 0.4 * np.sin(np.pi * min(1, (t - e["t"]) / 0.3)) * (1 - min(1, (t - e["t"]) / 0.3))
            r = 26 * s * pa * pop
            d.ellipse([X(x) - r - 10 * s, Y - r - 10 * s, X(x) + r + 10 * s, Y + r + 10 * s],
                      fill=PAPER_RGB + (int(255 * pa),), outline=INK_RGB + (int(255 * pa),), width=int(4 * s))
            d.ellipse([X(x) - r, Y - r, X(x) + r, Y + r], fill=GOLD_RGB + (int(255 * pa),))
            rr = (26 + 80 * ease_out((t - e["t"]) / 0.9)) * s
            ra = 0.6 * (1 - ease((t - e["t"]) / 0.9))
            if ra > 0.01:
                d.ellipse([X(x) - rr, Y - rr, X(x) + rr, Y + rr], outline=GOLD_RGB + (int(255 * ra),), width=int(5 * s))
            # anno che sale leggermente mentre compare; didascalie sotto, un attimo dopo
            ya = Y - 90 * s - 30 * s * (1 - pa)
            d.text((X(x), ya), e["year"], font=F["year"], fill=INK_RGB + (int(255 * pa * dim),), anchor="ms")
            ca = ease_out((t - e["t"] - 0.25) / 0.4) * dim
            if ca > 0:
                d.text((X(x), Y + 150 * s + 20 * s * (1 - ca)), e["cap"], font=F["cap"], fill=INK_RGB + (int(255 * ca),), anchor="mm")
                if e["sub"]:
                    d.text((X(x), Y + 270 * s + 20 * s * (1 - ca)), e["sub"], font=F["sub"],
                           fill=SUB_RGB + (int(255 * ca),), anchor="mm")
        pil = Image.alpha_composite(pil, lay).convert("RGB")
        out = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR).astype(np.float32) * vign + grain * 3.0
        proc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close(); proc.wait()


if __name__ == "__main__":
    main()
