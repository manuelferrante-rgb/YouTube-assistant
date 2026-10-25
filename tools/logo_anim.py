#!/usr/bin/env python3
"""Animazione del logo Voci Vere (fine sigla), ~1.4 s di animazione + tenuta.

    python3 tools/logo_anim.py out.mp4 --bg frame.png [--w 3840 --h 2160 --dur 2.9]
Sequenza (tempi in secondi dall'inizio della clip, in EVENTS per gli effetti sonori):
  0.00  V, tratto sinistro: si stampa (bam), con scossa
  0.13  V, tratto destro: si stampa (bam)
  0.28  O, C, I battute veloci
  0.64  VERE si rivela in oro con una luce che la attraversa
  1.00  linee e onda sonora si aprono dal centro, poi il payoff
Lo sfondo è il fotogramma dato, sfocato e scurito, con un lento avvicinamento.
"""
import argparse, os, subprocess
import numpy as np, cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGO = f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png"
FPS = 30
T_V1, T_V2, T_OCI, T_VERE, T_LINES, T_PAY = 0.0, 0.13, (0.28, 0.35, 0.42), 0.64, 1.0, 1.25
EVENTS = [(T_V1, "stamp"), (T_V2, "stamp"), *[(t, "tick") for t in T_OCI], (T_VERE - 0.05, "shimmer")]
GOLD = np.array([75, 138, 182], np.float32) / 255  # #B68A4B in BGR

# colonne delle lettere e fasce nel file del logo (1052x359)
TOP = (24, 176); MID = (184, 275); PAY = (280, 338)
V1 = (23, 167); V1_MID = 95; O, C, I = (167, 318), (322, 454), (457, 500)
VERE = (534, 1030); BARS = (440, 615)


def ease_out(x):
    x = np.clip(x, 0, 1)
    return 1 - (1 - x) ** 3


def back_out(x, s=2.2):
    x = np.clip(x, 0, 1)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def build(out, bg, W, H, dur=2.9):
    vertical = H > W
    logo = cv2.imread(LOGO, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    lw = int(W * (0.66 if vertical else 0.42))
    k = lw / logo.shape[1]
    lh = int(round(logo.shape[0] * k))
    L = cv2.resize(logo, (lw, lh), interpolation=cv2.INTER_CUBIC)
    rgb, A = np.clip(L[..., :3], 0, 1), np.clip(L[..., 3], 0, 1)
    X = lambda c: int(round(c * k))
    yy, xx = np.mgrid[0:lh, 0:lw]

    def region(x0, x1, y0=TOP[0], y1=TOP[1]):
        return ((xx >= X(x0)) & (xx < X(x1)) & (yy >= X(y0)) & (yy < X(y1))).astype(np.float32)

    m_v1l = region(V1[0], V1_MID); m_v1r = region(V1_MID, V1[1])
    m_oci = [region(*O), region(*C), region(*I)]
    m_vere = region(*VERE)
    m_mid = region(0, 1052, *MID); m_bars = m_mid * region(*BARS, *MID); m_lines = m_mid - m_bars
    m_pay = region(0, 1052, *PAY)
    cx_mid = X(527)

    glow_src = cv2.GaussianBlur(A * m_vere, (0, 0), max(2, lw / 90))

    # sfondo
    b = cv2.imread(bg).astype(np.float32) / 255
    b = cv2.resize(b, (W, H), interpolation=cv2.INTER_AREA)
    b = cv2.GaussianBlur(b, (0, 0), W / 70)
    gray = b.mean(2, keepdims=True)
    b = (gray + 0.6 * (b - gray)) * 0.55
    vy, vx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.45 * (((vx - W / 2) / (W / 2)) ** 2 + ((vy - H / 2) / (H / 2)) ** 2) / 2
    b *= vig[..., None]

    x0, y0 = (W - lw) // 2, (H - lh) // 2 - (int(H * 0.04) if vertical else 0)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(round(dur * FPS))
    for i in range(n):
        t = i / FPS
        # sfondo con lento avvicinamento
        z = 1 + 0.035 * t / dur
        M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]])
        frame = cv2.warpAffine(b, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        alpha = np.zeros((lh, lw), np.float32)
        color = rgb.copy()
        # V: due colpi
        for m, ts in ((m_v1l, T_V1), (m_v1r, T_V2)):
            if t >= ts:
                alpha += m * A
        # O C I battute
        for m, ts in zip(m_oci, T_OCI):
            if t >= ts:
                alpha += m * A * ease_out((t - ts) / 0.05)
        # VERE: rivelazione da sinistra con luce sul bordo
        wv = X(VERE[1]) - X(VERE[0])
        if t >= T_VERE:
            pr = ease_out((t - T_VERE) / 0.45)
            edge = X(VERE[0]) + pr * (wv * 1.25) - 0.12 * wv
            soft = 0.12 * wv
            reveal = np.clip((edge - xx) / soft + 0.5, 0, 1)
            alpha += m_vere * A * reveal
            band = np.exp(-0.5 * ((xx - edge) / (0.05 * wv)) ** 2) * (pr < 1)
            color = color + (m_vere * band)[..., None] * 0.9
        # linee che si aprono dal centro e barre dell'onda
        if t >= T_LINES:
            pl = ease_out((t - T_LINES) / 0.35)
            half = pl * (lw / 2)
            alpha += m_lines * A * (np.abs(xx - cx_mid) <= half)
            pb = (t - T_LINES) / 0.3
            dist = np.abs(xx - cx_mid) / max(1, X(BARS[1]) - cx_mid)
            gro = back_out(np.clip(pb - 0.5 * dist, 0, 1))
            puls = 1 - 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t + dist * 6)) * (pb > 1.5)
            sy = np.clip(gro * puls, 0, 1.3)
            cy = X((MID[0] + MID[1]) / 2)
            ys = np.clip(cy + (yy - cy) / np.maximum(sy, 1e-3), 0, lh - 1).astype(np.int32)
            bars_a = (A * m_bars)[ys, xx] * (sy > 0.01)
            alpha += bars_a
        if t >= T_PAY:
            pp = ease_out((t - T_PAY) / 0.4)
            dy = int((1 - pp) * lh * 0.05)
            pay = np.roll(A * m_pay, dy, axis=0) * pp
            alpha += pay
        alpha = np.clip(alpha, 0, 1)

        # scossa e spinta sui due colpi della V
        sx = sy_ = 0.0; sc = 1.0
        for ts in (T_V1, T_V2):
            if t >= ts:
                e = np.exp(-(t - ts) / 0.07)
                sx += 0.010 * W * e * np.sin(2 * np.pi * 21 * (t - ts))
                sy_ += 0.006 * W * e * np.cos(2 * np.pi * 17 * (t - ts))
                sc += 0.07 * np.exp(-(t - ts) / 0.05)
        # fine: dissolvenza del logo
        fade = np.clip((dur - t) / 0.25, 0, 1)
        alpha *= fade

        Ml = np.float32([[sc, 0, x0 + sx + lw / 2 * (1 - sc)], [0, sc, y0 + sy_ + lh / 2 * (1 - sc)]])
        a_full = cv2.warpAffine(alpha, Ml, (W, H), flags=cv2.INTER_LINEAR)
        c_full = cv2.warpAffine(np.clip(color, 0, 1.5), Ml, (W, H), flags=cv2.INTER_LINEAR)
        frame = frame * (1 - a_full[..., None]) + c_full * a_full[..., None]
        # bagliore oro dietro VERE
        if t >= T_VERE:
            g = np.exp(-max(0.0, t - T_VERE - 0.4) / 0.35) * 0.8 + 0.2
            gl = cv2.warpAffine(glow_src * g * fade, Ml, (W, H), flags=cv2.INTER_LINEAR)
            frame = frame + gl[..., None] * GOLD * 0.9
        # lampo bianco breve sui colpi
        for ts in (T_V1, T_V2):
            if 0 <= t - ts < 0.07:
                frame = frame + 0.10 * (1 - (t - ts) / 0.07)
        p.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--bg", required=True)
    ap.add_argument("--w", type=int, default=3840); ap.add_argument("--h", type=int, default=2160)
    ap.add_argument("--dur", type=float, default=2.9)
    a = ap.parse_args()
    build(a.out, a.bg, a.w, a.h, a.dur)
