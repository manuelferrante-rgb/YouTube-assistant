#!/usr/bin/env python3
"""Tre varianti della sigla Voci Vere (16:9) da far scegliere a Manuel: come entra il logo, grafica, effetti.

    python3 projects/sigla_studio/varianti.py [A|B|C ...]
A "Pulita": tagli netti sui pezzi, stacco al nero, logo che si mette a fuoco, un solo colpo morbido.
B "Pellicola": bande cinema, grana, dissolvenze brevi, il logo rivelato da una lama di luce, nessun colpo.
C "Onda": un'onda sonora oro segue la voce di Manuel sopra i pezzi e si chiude nell'icona del logo.
"""
import os, subprocess, sys
import numpy as np, cv2, soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from sfx import sfx_file

W, H, FPS, SR = 1920, 1080, 30, 48000
S = f"{ROOT}/assets/sigla"
OUT = f"{ROOT}/work/sigla_studio"
os.makedirs(OUT, exist_ok=True)
PIECES = ["01_strada_tuktuk.mp4", "02_marari_pescatori.mp4", "03_marari_pescatore.mp4", "04_kerala_chai.mp4",
          "05_marari_folla.mp4", "06_marari_mare.mp4"]
FRASE, FA, FB = f"{S}/frase_sigla_manuel.m4a", 1.70, 5.75
V0 = 0.30                     # inizio della frase nella sigla
T_VOCI = V0 + 4.88 - FA       # attacco di "Voci" (3.48 s)
DUR = 6.0
GOLD = np.array([75, 138, 182], np.float32) / 255     # BGR


def frames(path, n, start=0.05):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start}", "-i", path, "-frames:v", str(n), "-vf",
                          f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255
    if len(a) < n:
        a = np.concatenate([a, np.repeat(a[-1:], n - len(a), 0)])
    return a


def logo(width):
    """Logo chiaro, bordi puliti (alfa ricostruita), diviso in testo / onda / payoff."""
    im = cv2.imread(f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3]
    good = ((a > 0.9) & (im[..., :3].mean(2) > 0.35)).astype(np.float32)
    num = cv2.GaussianBlur(im[..., :3] * good[..., None], (0, 0), 3)
    den = cv2.GaussianBlur(good, (0, 0), 3)[..., None]
    im[..., :3] = np.where(den > 1e-3, num / np.maximum(den, 1e-3), im[..., :3])
    k = width / im.shape[1]
    im = cv2.resize(im, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC if k > 1 else cv2.INTER_AREA)
    al = cv2.GaussianBlur(im[..., 3], (0, 0), max(0.7, 0.9 * k))
    im[..., 3] = np.clip((al - 0.5) * 2.2 + 0.5, 0, 1)
    rows = (im[..., 3] > 0.15).any(1)
    bands, s = [], None
    for i, v in enumerate(rows):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s > 3: bands.append((s, i))
            s = None
    return np.clip(im, 0, 1), bands


def over(dst, rgb, a, x, y):
    h, w = a.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sa = a[y0 - y:y1 - y, x0 - x:x1 - x, None]
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - sa) + rgb[y0 - y:y1 - y, x0 - x:x1 - x] * sa


def ease(u):
    u = np.clip(u, 0, 1)
    return 1 - (1 - u) ** 3


def voice():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", FRASE, "-af", f"atrim={FA}:{FB},asetpts=PTS-STARTPTS,"
                          "highpass=f=80,loudnorm=I=-16:TP=-2", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def mix(events, out_wav):
    """events: (array o nome sfx, tempo, guadagno)."""
    buf = np.zeros((int(DUR * SR) + SR, 2), np.float32)
    for src, t, g in events:
        x = src if isinstance(src, np.ndarray) else sf.read(sfx_file(src), dtype="float32")[0]
        if x.ndim == 1: x = np.stack([x, x], 1)
        i = int(t * SR); n = min(len(x), len(buf) - i)
        buf[i:i + n] += x[:n] * g
    buf = buf[:int(DUR * SR)]
    fade = int(0.4 * SR); buf[-fade:] *= np.linspace(1, 0, fade)[:, None]
    buf *= 0.95 / max(1e-6, np.abs(buf).max())
    sf.write(out_wav, buf, SR)


def encode(name, gen, events):
    p = f"{OUT}/sigla_{name}.mp4"
    wav = f"{OUT}/sigla_{name}.wav"
    mix(events, wav)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
                             p], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        proc.stdin.write((np.clip(gen(f / FPS, f), 0, 1) * 255).astype(np.uint8).tobytes())
    proc.stdin.close(); proc.wait()
    print(p)


# pezzi: 6 x 0.53 s fino a poco prima di "Voci"
SEG = (T_VOCI - 0.15) / len(PIECES)
PF = [frames(f"{S}/{p}", int(SEG * FPS) + 8) for p in PIECES]


def piece_at(t, push=0.05):
    i = min(int(t / SEG), len(PIECES) - 1)
    fr = PF[i][min(int((t - i * SEG) * FPS), len(PF[i]) - 1)]
    z = 1 + push * (t - i * SEG) / SEG
    M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]])
    return cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT), i


LOGO, BANDS = logo(int(W * 0.40))
LH, LW = LOGO.shape[:2]
LX, LY = (W - LW) // 2, (H - LH) // 2
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.55 * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.7 - 0.25, 0, 1))[..., None]


# ---------- A: pulita ----------
def gen_A(t, f):
    if t < T_VOCI - 0.15:
        fr, _ = piece_at(t)
        return fr
    bg = np.zeros((H, W, 3), np.float32) + np.array([16, 14, 12], np.float32) / 255
    bg = bg * VIGN
    u = (t - (T_VOCI - 0.05)) / 0.6
    if u > 0:
        e = ease(u)
        s = 1.04 - 0.04 * e
        sig = max(0.01, 8 * (1 - e))
        rgb, al = LOGO[..., :3], LOGO[..., 3] * np.clip(u * 1.6, 0, 1)
        # payoff e onda entrano dopo il testo
        y_t = BANDS[0][1] + 2
        late = np.clip((t - (T_VOCI + 0.55)) / 0.5, 0, 1)
        mask = np.ones_like(al); mask[y_t:] = late
        al = al * mask
        if sig > 0.3:
            rgb = cv2.GaussianBlur(rgb, (0, 0), sig); al = cv2.GaussianBlur(al, (0, 0), sig)
        M = np.float32([[s, 0, LW / 2 * (1 - s)], [0, s, LH / 2 * (1 - s)]])
        rgb = cv2.warpAffine(rgb, M, (LW, LH)); al = cv2.warpAffine(al, M, (LW, LH))
        glow = cv2.GaussianBlur(al, (0, 0), 30) * 0.35 * (1 - 0.6 * e)
        bg[LY:LY + LH, LX:LX + LW] += glow[..., None] * GOLD
        over(bg, rgb, al, LX, LY)
    return bg


# ---------- B: pellicola ----------
GRAIN = [np.random.default_rng(i).normal(0, 0.035, (H // 2, W // 2)).astype(np.float32) for i in range(8)]


def film(fr, f, bars=True):
    g = cv2.resize(GRAIN[f % 8], (W, H))[..., None]
    gray = fr.mean(2, keepdims=True)
    fr = (gray + 0.8 * (fr - gray)) * 0.95 + 0.02 + g
    fr = fr * VIGN
    if bars:
        bh = int((H - W / 2.39) / 2)
        fr[:bh] = 0; fr[H - bh:] = 0
    return fr


def gen_B(t, f):
    if t < T_VOCI - 0.15:
        fr, i = piece_at(t, push=0.03)
        # dissolvenza breve verso il pezzo successivo
        tl = (i + 1) * SEG - t
        if tl < 0.12 and i + 1 < len(PIECES):
            nx = PF[i + 1][0]
            a = 1 - tl / 0.12
            fr = fr * (1 - a) + nx * a
        return film(fr, f)
    last = PF[-1][-1]
    bg = cv2.GaussianBlur(last, (0, 0), 25) * 0.35
    u = (t - (T_VOCI - 0.15)) / 0.9
    edge = -0.15 + ease(u) * 1.35                           # lama di luce da sinistra a destra
    X = np.arange(LW, dtype=np.float32)[None, :] / LW
    reveal = np.clip((edge - X) / 0.12, 0, 1)
    band = np.exp(-((X - edge) / 0.05) ** 2) * (1 - np.clip(u - 0.8, 0, 1) * 5)
    rgb = np.clip(LOGO[..., :3] * (1 + 1.4 * band[..., None]) + 0.35 * band[..., None], 0, 1)
    al = LOGO[..., 3] * reveal
    y_t = BANDS[0][1] + 2
    late = np.clip((t - (T_VOCI + 0.7)) / 0.6, 0, 1)
    al[y_t:] *= late
    over(bg, rgb, al, LX, LY)
    return film(bg, f)


# ---------- C: onda ----------
VX = voice()
ENV = np.array([np.sqrt(np.mean(VX[int(i * SR / FPS):int((i + 1) * SR / FPS)] ** 2) + 1e-9)
                for i in range(int(len(VX) / SR * FPS) + 2)])
ENV = np.nan_to_num(ENV, nan=0.0)
ENV = ENV / ENV.max()
N_BARS = 48


def bars_img(t, f, width, height, amp_scale):
    img = np.zeros((height, width), np.float32)
    k = int((t - V0) * FPS)
    e = ENV[k] if 0 <= k < len(ENV) else 0.02
    xs = np.linspace(0, width, N_BARS + 2)[1:-1]
    bw = max(2, int(width / N_BARS * 0.35))
    rng = np.random.default_rng(f)
    for j, x in enumerate(xs):
        shape = np.exp(-((j - N_BARS / 2) / (N_BARS / 3.2)) ** 2)
        hgt = height * (0.05 + amp_scale * e * shape * (0.6 + 0.4 * rng.random()))
        cv2.rectangle(img, (int(x - bw / 2), int(height / 2 - hgt / 2)), (int(x + bw / 2), int(height / 2 + hgt / 2)), 1.0, -1)
    return cv2.GaussianBlur(img, (0, 0), 1.0)


def gen_C(t, f):
    t_close = T_VOCI - 0.1
    if t < t_close:
        fr, _ = piece_at(t)
        fr = fr * 0.85
        bh, bw_ = int(H * 0.16), int(W * 0.62)
        b = bars_img(t, f, bw_, bh, 0.9) * np.clip((t - V0) / 0.3, 0, 1)
        glow = cv2.GaussianBlur(b, (0, 0), 8) * 0.6
        rgbb = np.ones((bh, bw_, 3), np.float32) * GOLD * 1.6
        over(fr, rgbb, np.clip(b + glow, 0, 1), (W - bw_) // 2, int(H * 0.70))
        return fr
    bg = np.zeros((H, W, 3), np.float32) + np.array([16, 14, 12], np.float32) / 255
    bg = bg * VIGN
    u = (t - t_close) / 0.35                                 # l'onda si stringe nell'icona del logo
    y_t0, y_t1 = BANDS[0]; y_w0, y_w1 = BANDS[1]
    if u < 1:
        e = ease(u)
        bw_ = int(W * 0.62 * (1 - e) + LW * 0.18 * e)
        bh = int(H * 0.16 * (1 - e) + (y_w1 - y_w0) * e)
        cy = int(H * 0.70 + bh / 2) * (1 - e) + (LY + (y_w0 + y_w1) / 2) * e
        b = bars_img(t, f, max(8, bw_), max(8, bh), 0.9)
        rgbb = np.ones(b.shape + (3,), np.float32) * GOLD * 1.6
        over(bg, rgbb, b, (W - b.shape[1]) // 2, int(cy - b.shape[0] / 2))
        return bg
    # poi il logo: prima onda e linee, poi VOCI VERE che si stringe dal largo, poi il payoff
    v = t - (t_close + 0.35)
    al = LOGO[..., 3].copy(); rgb = LOGO[..., :3]
    mid = al.copy(); mid[:y_w0] = 0; mid[y_w1:] = 0
    over(bg, rgb, mid, LX, LY)
    txt = al.copy(); txt[y_t1 + 2:] = 0
    e = ease(v / 0.45)
    sx = 1.25 - 0.25 * e
    M = np.float32([[sx, 0, LW / 2 * (1 - sx)], [0, 1, 0]])
    tr = cv2.warpAffine(rgb, M, (LW, LH)); ta = cv2.warpAffine(txt, M, (LW, LH)) * np.clip(v / 0.25, 0, 1)
    over(bg, tr, ta, LX, LY)
    pay = al.copy(); pay[:y_w1 + 2] = 0
    over(bg, rgb, pay * np.clip((v - 0.5) / 0.5, 0, 1), LX, LY)
    return bg


if __name__ == "__main__":
    which = sys.argv[1:] or ["A", "B", "C"]
    VO = (VX, V0, 1.0)
    if "A" in which:
        encode("A_pulita", gen_A, [VO, ("riser_long", T_VOCI - 2.6, 0.12), ("boom", T_VOCI - 0.05, 0.35),
                                   ("shimmer", T_VOCI + 0.2, 0.10)])
    if "B" in which:
        encode("B_pellicola", gen_B, [VO, ("whoosh_rev", T_VOCI - 0.75, 0.22), ("shimmer", T_VOCI, 0.22)])
    if "C" in which:
        encode("C_onda", gen_C, [VO, ("whoosh_rev", T_VOCI - 0.8, 0.18), ("hit", T_VOCI + 0.25, 0.22)])


# ---------- D: scelta di Manuel (23/10) ----------
# immagini con il look della B (grana, colori un po' spenti, dissolvenze) ma a tutto schermo 16:9 (niente bande),
# l'onda della C che entra solo da "Questo è" e si chiude nell'icona del logo su "Voci", logo su sfondo sfocato (B),
# suono della A.
T_QUESTO = V0 + 3.98 - FA          # attacco di "Questo è" (2.58 s)


def gen_D(t, f):
    t_close = T_VOCI - 0.1
    if t < t_close:
        fr, i = piece_at(t, push=0.03)
        tl = (i + 1) * SEG - t
        if tl < 0.12 and i + 1 < len(PIECES):
            a = 1 - tl / 0.12
            fr = fr * (1 - a) + PF[i + 1][0] * a
        fr = film(fr, f, bars=False)
        if t >= T_QUESTO - 0.1:
            k = np.clip((t - (T_QUESTO - 0.1)) / 0.25, 0, 1)
            bh, bw_ = int(H * 0.16), int(W * 0.62)
            b = bars_img(t, f, bw_, bh, 0.9) * k
            glow = cv2.GaussianBlur(b, (0, 0), 8) * 0.6
            rgbb = np.ones((bh, bw_, 3), np.float32) * GOLD * 1.6
            over(fr, rgbb, np.clip(b + glow, 0, 1), (W - bw_) // 2, int(H * 0.70))
        return fr
    bg = film(cv2.GaussianBlur(PF[-1][-1], (0, 0), 25) * 0.4, f, bars=False)
    u = (t - t_close) / 0.35
    y_t0, y_t1 = BANDS[0]; y_w0, y_w1 = BANDS[1]
    if u < 1:
        e = ease(u)
        bw_ = int(W * 0.62 * (1 - e) + LW * 0.18 * e)
        bh = int(H * 0.16 * (1 - e) + (y_w1 - y_w0) * e)
        cy = int(H * 0.70 + bh / 2) * (1 - e) + (LY + (y_w0 + y_w1) / 2) * e
        b = bars_img(t, f, max(8, bw_), max(8, bh), 0.9)
        rgbb = np.ones(b.shape + (3,), np.float32) * GOLD * 1.6
        over(bg, rgbb, b, (W - b.shape[1]) // 2, int(cy - b.shape[0] / 2))
        return bg
    v = t - (t_close + 0.35)
    al = LOGO[..., 3].copy(); rgb = LOGO[..., :3]
    mid = al.copy(); mid[:y_w0] = 0; mid[y_w1:] = 0
    over(bg, rgb, mid, LX, LY)
    txt = al.copy(); txt[y_t1 + 2:] = 0
    e = ease(v / 0.45)
    sx = 1.25 - 0.25 * e
    M = np.float32([[sx, 0, LW / 2 * (1 - sx)], [0, 1, 0]])
    tr = cv2.warpAffine(rgb, M, (LW, LH)); ta = cv2.warpAffine(txt, M, (LW, LH)) * np.clip(v / 0.25, 0, 1)
    over(bg, tr, ta, LX, LY)
    pay = al.copy(); pay[:y_w1 + 2] = 0
    over(bg, rgb, pay * np.clip((v - 0.5) / 0.5, 0, 1), LX, LY)
    return bg


if __name__ == "__main__" and "D" in sys.argv[1:]:
    encode("D_scelta", gen_D, [(VX, V0, 1.0), ("riser_long", T_VOCI - 2.6, 0.12), ("boom", T_VOCI - 0.05, 0.35),
                               ("shimmer", T_VOCI + 0.2, 0.10)])
