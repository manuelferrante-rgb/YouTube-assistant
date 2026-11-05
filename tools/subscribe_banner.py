#!/usr/bin/env python3
"""Banner dei lunghi (Manuel 5/11), piccoli, in basso al centro, mai sopra i sottotitoli:
- "iscriviti": appena dopo la sigla, quando Manuel inizia a parlare. Il cursore clicca ISCRIVITI (diventa ISCRITTO),
  la campanella (si riempie e oscilla) e Hype (si accende).
- "like": a metà video, in un punto calmo. Il cursore clicca Mi piace (pollice pieno) e Commenta.
Ogni click ha il suo piccolo suono (click di mouse sintetico, banner_<tipo>_click.wav, stessa durata del banner).

    python3 tools/subscribe_banner.py out_dir iscriviti|like --w 3840
Scrive out_dir/banner_<tipo>_<W>.mov (RGBA, qtrle, 30 fps) e out_dir/banner_<tipo>_click.wav.
"""
import argparse, math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT = f"{ROOT}/models/VVTitolo-PoppinsExtraBold.ttf"
FONT_M = f"{ROOT}/models/Poppins-Medium.ttf"
AVATAR = f"{ROOT}/assets/brand/avatar_youtube.png"
FPS = 30
KIND = {"iscriviti": dict(dur=4.9, clicks=(1.45, 2.25, 3.05), width=0.27),
        "like": dict(dur=3.9, clicks=(1.35, 2.15), width=0.21)}
GOLD = (182, 138, 75)
RED = (204, 0, 0)
INK = (30, 30, 30, 255)


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def pulse(t, tc):
    """Rimpicciolisce di poco l'elemento cliccato (pressione) per 0.12 s attorno al click."""
    return 1 - 0.1 * max(0.0, 1 - abs(t - tc) / 0.12)


def icon_bell(s, filled, angle):
    img = Image.new("RGBA", (int(s * 2.4), int(s * 2.4)), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    o = s * 1.2
    body = [(o - s * 0.55, o + s * 0.45), (o - s * 0.45, o - s * 0.15), (o - s * 0.3, o - s * 0.5),
            (o, o - s * 0.62), (o + s * 0.3, o - s * 0.5), (o + s * 0.45, o - s * 0.15), (o + s * 0.55, o + s * 0.45)]
    if filled:
        g.polygon(body, fill=INK)
    else:
        g.line(body + [body[0]], fill=INK, width=max(2, int(s * 0.13)), joint="curve")
    g.rounded_rectangle([o - s * 0.68, o + s * 0.4, o + s * 0.68, o + s * 0.56], radius=s * 0.07, fill=INK)
    g.ellipse([o - s * 0.15, o + s * 0.56, o + s * 0.15, o + s * 0.84], fill=INK)
    g.ellipse([o - s * 0.1, o - s * 0.82, o + s * 0.1, o - s * 0.62], fill=INK)
    return img.rotate(angle, center=(o, o - s * 0.7), resample=Image.BICUBIC)


def icon_bolt(s, on):
    img = Image.new("RGBA", (int(s * 2.4), int(s * 2.4)), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    o = s * 1.2
    p = [(0.15, -0.9), (-0.45, 0.1), (-0.02, 0.1), (-0.2, 0.9), (0.45, -0.15), (0.03, -0.15), (0.2, -0.9)]
    p = [(o + x * s, o + y * s) for x, y in p]
    if on:
        g.polygon(p, fill=(255, 255, 255, 255))
    else:
        g.polygon(p, fill=INK)
    return img


def icon_thumb(s, filled):
    img = Image.new("RGBA", (int(s * 2.4), int(s * 2.4)), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    o = s * 1.2
    w = max(2, int(s * 0.13))
    palm = [(o - s * 0.35, o - s * 0.05), (o - s * 0.05, o - s * 0.75), (o + s * 0.12, o - s * 0.78),
            (o + s * 0.15, o - s * 0.15), (o + s * 0.62, o - s * 0.15), (o + s * 0.7, o + s * 0.0),
            (o + s * 0.55, o + s * 0.7), (o - s * 0.35, o + s * 0.7)]
    cuff = [o - s * 0.75, o - s * 0.08, o - s * 0.45, o + s * 0.72]
    if filled:
        g.polygon(palm, fill=INK); g.rectangle(cuff, fill=INK)
    else:
        g.line(palm + [palm[0]], fill=INK, width=w, joint="curve"); g.rectangle(cuff, outline=INK, width=w)
    return img


def icon_comment(s, filled):
    img = Image.new("RGBA", (int(s * 2.4), int(s * 2.4)), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    o = s * 1.2
    w = max(2, int(s * 0.13))
    box = [o - s * 0.75, o - s * 0.6, o + s * 0.75, o + s * 0.4]
    tail = [(o - s * 0.35, o + s * 0.35), (o - s * 0.55, o + s * 0.8), (o + s * 0.05, o + s * 0.35)]
    if filled:
        g.rounded_rectangle(box, radius=s * 0.22, fill=INK); g.polygon(tail, fill=INK)
        for dx in (-0.35, 0, 0.35):
            g.ellipse([o + (dx - 0.08) * s, o - 0.18 * s, o + (dx + 0.08) * s, o - 0.02 * s], fill=(255, 255, 255, 255))
    else:
        g.rounded_rectangle(box, radius=s * 0.22, outline=INK, width=w); g.line(tail, fill=INK, width=w)
    return img


def cursor(s):
    img = Image.new("RGBA", (int(s * 1.2), int(s * 1.6)), (0, 0, 0, 0))
    g = ImageDraw.Draw(img)
    p = [(0.08, 0.05), (0.08, 1.2), (0.36, 0.93), (0.56, 1.42), (0.74, 1.34), (0.55, 0.86), (0.95, 0.86)]
    g.polygon([(x * s, y * s) for x, y in p], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(2, int(s * 0.07)))
    return img


def paste_center(dst, img, cx, cy, scale=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
    dst.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def pill_button(g, cx, cy, w, h, fill, text, font, tcol):
    g.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=h // 2, fill=fill)
    tw = g.textlength(text, font=font)
    g.text((cx - tw / 2, cy - h * 0.36), text, font=font, fill=tcol)


def frame(kind, t, W):
    cfg = KIND[kind]
    dur, clicks = cfg["dur"], cfg["clicks"]
    H = int(W * (0.25 if kind == "iscriviti" else 0.3))
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    alpha = min(ease(t / 0.35), 1 - ease((t - (dur - 0.4)) / 0.4))
    if alpha <= 0:
        return im
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(pill)
    px0, py0, px1, py1 = int(W * 0.02), int(H * 0.2), int(W * 0.98), int(H * 0.9)
    ph = py1 - py0
    cy = (py0 + py1) // 2
    sh = max(2, int(ph * 0.05))
    g.rounded_rectangle([px0 + sh, py0 + sh, px1 + sh, py1 + sh], radius=ph // 2, fill=(0, 0, 0, 70))   # ombra
    g.rounded_rectangle([px0, py0, px1, py1], radius=ph // 2, fill=(255, 255, 255, 245))
    targets = []
    if kind == "iscriviti":
        # foto profilo del canale YouTube (Manuel 5/11: assets/brand/avatar_youtube.png, ritagliata dal profilo)
        r = int(ph * 0.38)
        lx = px0 + int(ph * 0.5)
        av = Image.open(AVATAR).convert("RGBA").resize((2 * r, 2 * r), Image.LANCZOS)
        pill.alpha_composite(av, (lx - r, cy - r))
        nx = lx + r + int(ph * 0.2)
        g.text((nx, cy - ph * 0.2), "Voci Vere", font=ImageFont.truetype(FONT, int(ph * 0.25)), fill=(17, 17, 17, 255))
        # ISCRIVITI -> ISCRITTO
        done = t >= clicks[0]
        p = pulse(t, clicks[0])
        bx = int(W * 0.565)
        bw_, bh_ = int(W * 0.21 * p), int(ph * 0.56 * p)
        pill_button(g, bx, cy, bw_, bh_, (225, 225, 225, 255) if done else RED + (255,), "ISCRITTO" if done else "ISCRIVITI",
                    ImageFont.truetype(FONT, int(bh_ * 0.42)), (80, 80, 80, 255) if done else (255, 255, 255, 255))
        targets.append((bx + W * 0.03, cy + ph * 0.05))
        # campanella
        cx2 = int(W * 0.745)
        ring = t - clicks[1]
        ang = 22 * math.sin(ring * 2 * math.pi * 4) * math.exp(-ring * 3.5) if ring >= 0 else 0
        paste_center(pill, icon_bell(ph * 0.3, ring >= 0, ang), cx2, cy, pulse(t, clicks[1]))
        targets.append((cx2 + ph * 0.05, cy + ph * 0.12))
        # Hype: pillola con il fulmine, si accende (oro) al click
        on = t >= clicks[2]
        p = pulse(t, clicks[2])
        hx = int(W * 0.87)
        hw, hh = int(W * 0.17 * p), int(ph * 0.56 * p)
        g.rounded_rectangle([hx - hw // 2, cy - hh // 2, hx + hw // 2, cy + hh // 2], radius=hh // 2,
                            fill=(GOLD + (255,)) if on else (236, 236, 236, 255))
        f_h = ImageFont.truetype(FONT, int(hh * 0.4))
        tw, bw0 = g.textlength("Hype", font=f_h), hh * 0.42
        x0 = hx - (bw0 + hh * 0.08 + tw) / 2
        paste_center(pill, icon_bolt(hh * 0.32, on), x0 + bw0 / 2, cy)
        g.text((x0 + bw0 + hh * 0.08, cy - hh * 0.36), "Hype", font=f_h, fill=(255, 255, 255, 255) if on else INK)
        targets.append((hx + W * 0.01, cy + ph * 0.08))
    else:
        f_t = ImageFont.truetype(FONT, int(ph * 0.24))
        for i, (txt, icon) in enumerate((("Mi piace", icon_thumb), ("Commenta", icon_comment))):
            on = t >= clicks[i]
            cx = int(W * (0.29 if i == 0 else 0.73))
            ic = icon(ph * 0.26, on)
            tw = g.textlength(txt, font=f_t)
            ix = cx - tw / 2 - ph * 0.22
            paste_center(pill, ic, ix, cy, pulse(t, clicks[i]))
            g.text((ix + ph * 0.36, cy - ph * 0.19), txt, font=f_t, fill=INK)
            targets.append((ix + ph * 0.05, cy + ph * 0.1))
    # cursore: entra da destra in basso, clicca i bersagli uno dopo l'altro, esce
    pts = [(W * 1.05, H * 1.25)] + targets + [(W * 1.1, H * 1.3)]
    times = [0.7] + list(clicks) + [dur - 0.35]
    cp = None
    for i in range(len(pts) - 1):
        t0 = times[i] + (0.22 if i > 0 else 0.0)                     # resta un attimo sul bersaglio dopo il click
        t1 = times[i + 1] - (0.1 if i + 1 < len(pts) - 1 else 0.0)
        if times[i] <= t < t0:
            cp = pts[i]
        elif t0 <= t < t1:
            e = ease((t - t0) / (t1 - t0))
            cp = (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * e, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * e)
        elif t1 <= t < times[i + 1]:
            cp = pts[i + 1]
    if cp:
        cs = 0.86 if min(abs(t - c) for c in clicks) < 0.07 else 1.0
        pill.alpha_composite(cursor(ph * 0.42 * cs), (int(cp[0]), int(cp[1])))
    if alpha < 1:
        pill.putalpha(pill.getchannel("A").point(lambda v: int(v * alpha)))
    im.alpha_composite(pill, (0, int((1 - alpha) * H * 0.35)))
    return im


def click_wav(kind, path):
    """Un click di mouse sintetico (pressione + rilascio) per ogni click del cursore."""
    import soundfile as sf
    sr, cfg = 48000, KIND[kind]
    y = np.zeros(int(cfg["dur"] * sr), np.float32)
    rng = np.random.default_rng(7)
    for tc in cfg["clicks"]:
        for off, amp in ((-0.03, 0.6), (0.035, 0.35)):
            n = int(0.006 * sr)
            burst = rng.standard_normal(n) * np.exp(-np.linspace(0, 9, n))
            tone = np.sin(2 * np.pi * 3200 * np.arange(n) / sr) * np.exp(-np.linspace(0, 12, n))
            s = np.diff(np.concatenate([[0], (0.6 * burst + 0.4 * tone) * amp]))   # secco, senza tonfo
            i = int((tc + off) * sr)
            y[i:i + n] += s.astype(np.float32)
    y *= 0.7 / max(1e-6, np.abs(y).max())
    sf.write(path, np.stack([y, y], 1), sr, subtype="PCM_16")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir"); ap.add_argument("kind", choices=list(KIND)); ap.add_argument("--w", type=int, default=3840)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    BW = int(a.w * KIND[a.kind]["width"]) // 2 * 2
    frames = f"{a.out_dir}/banner_{a.kind}_frames_{a.w}"
    os.makedirs(frames, exist_ok=True)
    for i in range(int(round(KIND[a.kind]["dur"] * FPS))):
        frame(a.kind, i / FPS, BW).save(f"{frames}/{i:04d}.png")
    out = f"{a.out_dir}/banner_{a.kind}_{a.w}.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{frames}/%04d.png", "-c:v", "qtrle",
                    "-pix_fmt", "argb", out], check=True)
    click_wav(a.kind, f"{a.out_dir}/banner_{a.kind}_click.wav")
    print(out)
