#!/usr/bin/env python3
"""Scritta finale dei lunghi (Manuel 7/11, coir): DM Serif Display, "Voci Vere" in oro, sottotitolo in un riquadro nero
attraversato una volta da sinistra a destra da una luce a cometa che poi si richiude. Scrive i fotogrammi RGBA (png)
da sovrapporre al video, con un velo sfumato in basso per la leggibilità.
    python3 tools/scritta_finale.py <cartella_out> [--w 1920 --h 1080 --dur 6.5]
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT = f"{ROOT}/assets/fonts/DMSerifDisplay-Regular.ttf"
GOLD, WHITE = (182, 138, 75), (245, 245, 245)
L1 = [("Il viaggio di ", 0), ("Voci Vere", 1), (", per dare voce", 0)]
L2 = [("a chi ne ha più bisogno, continua.", 0)]
SUB = "Seguimi per scoprire le prossime storie"


def ease(u):
    return 1 - (1 - max(0.0, min(1.0, u))) ** 3


def alpha(im, k):
    im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * k))); return im


def main(out, W, H, dur, fps=30, fadeout=0.0):
    k = H / 1080
    S = lambda v: int(round(v * k))
    f, fs = ImageFont.truetype(FONT, S(70)), ImageFont.truetype(FONT, S(44))
    os.makedirs(out, exist_ok=True)
    g = np.zeros((H, W, 4), np.uint8); y = np.arange(H)
    g[..., 3] = (np.clip((y - S(470)) / S(330), 0, 1) * 150)[:, None].astype(np.uint8)
    veil = Image.fromarray(g, "RGBA")
    main_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(main_); yy = S(612)
    for segs in (L1, L2):
        w = sum(d.textlength(s, font=f) for s, _ in segs); x = (W - w) / 2
        for s, gg in segs:
            d.text((x, yy), s, font=f, fill=(GOLD if gg else WHITE) + (255,)); x += d.textlength(s, font=f)
        yy += S(92)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(main_.split()[3].filter(ImageFilter.GaussianBlur(S(5))).point(lambda v: int(v * 0.8)))
    main_ = Image.alpha_composite(sh, main_)
    sw = d.textlength(SUB, font=fs)
    bx0, bx1, by0, by1 = int((W - sw) / 2 - S(34)), int((W + sw) / 2 + S(34)), S(828), S(902)
    for i in range(int(round(dur * fps))):
        t = i / fps
        fr = Image.alpha_composite(alpha(veil, ease(t / 0.8)), alpha(main_, ease(t / 0.8)))
        b = ease((t - 0.9) / 0.6)
        if b > 0:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.rectangle([bx0, by0, bx1, by1], fill=(0, 0, 0, int(200 * b)))
            d.text(((W - sw) / 2, by0 + S(13)), SUB, font=fs, fill=WHITE + (int(255 * b),))
            fr = Image.alpha_composite(fr, lay)
        c = (t - 1.7) / 1.3                                    # cometa 1.7-3.0 s, una volta, poi si richiude
        if 0 < c < 1.4:
            head = bx0 + (bx1 - bx0) * ease(min(c, 1))
            tail = (bx1 - bx0) * 0.5 * max(0, 1 - max(0, c - 0.6) / 0.75)
            x0, fade = max(bx0, head - tail), max(0, 1 - max(0, c - 1.0) / 0.4)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for j in range(80):
                u = (j + 1) / 80
                for yb in (by0, by1):
                    d.line([(x0 + (head - x0) * j / 80, yb), (x0 + (head - x0) * u + 1, yb)],
                           fill=(255, 226, 160, int(255 * u ** 1.6 * fade)), width=max(2, S(4)))
            glow = lay.filter(ImageFilter.GaussianBlur(S(5)))
            hd = Image.new("RGBA", (W, H), (0, 0, 0, 0)); h = ImageDraw.Draw(hd)
            for yb in (by0, by1):
                h.ellipse([head - S(14), yb - S(14), head + S(14), yb + S(14)], fill=(255, 245, 215, int(255 * fade)))
            hd = hd.filter(ImageFilter.GaussianBlur(S(7)))
            sweep = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sweep).rectangle([head - S(110), by0 + 3, head, by1 - 3], fill=(255, 225, 170, int(55 * fade)))
            for L in (sweep.filter(ImageFilter.GaussianBlur(S(20))), glow, lay, hd):
                fr = Image.alpha_composite(fr, L)
        if fadeout and t > dur - fadeout:                      # tutto sfuma negli ultimi fadeout s
            fr = alpha(fr, max(0.0, (dur - t) / fadeout))
        fr.save(f"{out}/{i:04d}.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--dur", type=float, default=6.5); ap.add_argument("--fadeout", type=float, default=0.0)
    a = ap.parse_args()
    main(a.out, a.w, a.h, a.dur, fadeout=a.fadeout)
