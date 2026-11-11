#!/usr/bin/env python3
"""Reel extra "spazio Munnar" (Manuel 11/11): come il riferimento in Drive "Reel voiceover spazio/Riferimenti", ma su
Munnar. Discesa dallo spazio (immagini satellitari vere, tools/space_zoom.py) fino al 2nd Mile View Point
(22RQ+HP7, 10.0417 N 77.0393 E), le colline intorno, poi Manuel:
  "Sono a Munnar, in Kerala, a oltre 1500 metri." (115233, braccia aperte)
  "Dietro di me una piantagione immensa di tè." (115233, l'inquadratura scorre da lui alle colline)
  "Scoprirò l'arte che c'è dietro questo lavoro." (120307)
  "E la storia... nella raccolta del tè che consumiamo tutti i giorni." (120356)
Niente musica (Manuel): solo il suono del movimento (sintetizzato qui, originale) dallo spazio all'arrivo.
Chiusura nuova (Manuel: niente riquadro bianco): sfondo che si sfoca, "Video fuori sul canale" e il logo.
Sottotitoli parola per parola su fascia scura, parola detta in oro (formato dei reel).
    python3 projects/spazio_munnar/build.py          (girato del tè in work/spazio/raw, discesa in work/spazio/sz)
Crediti immagini satellitari (per la descrizione): Sentinel-2 cloudless 2016 by EOX IT Services GmbH (contains
modified Copernicus Sentinel data 2016), CC BY 4.0; Blue Marble, NASA.
"""
import glob, json, math, os, subprocess, sys
import numpy as np, cv2, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from voice_clean import cleaned

WK = f"{ROOT}/work/spazio"
RAW = f"{WK}/raw"
SZ = f"{WK}/sz"
OUT = f"{WK}/out/VociVere_munnar_spazio_1080x1920.mp4"
W, H, FPS, SR = 1080, 1920, 30, 48000
GOLD = (182, 138, 75)
F_CAP = f"{ROOT}/models/Poppins-Medium.ttf"
F_END = f"{ROOT}/assets/fonts/DMSerifDisplay-Regular.ttf"
LOGO = f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png"
GRADE = "eq=contrast=1.04:saturation=1.08"


def clip(n):
    return glob.glob(f"{RAW}/*{n}*.MP4")[0]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)[:400]); print(r.stderr[-1500:]); sys.exit(1)
    return r


# ---------------- montaggio: (clip, inizio nella clip, durata, opzioni) ----------------
T_SPACE = len(glob.glob(f"{SZ}/*.png")) / FPS          # discesa (finisce nel bianco)
T_IN = T_SPACE - 0.22                                    # il girato entra sotto il bianco
# voce: pezzi (clip, da, a, pausa dopo) in fila. La seconda frase è montata dalle parole di Manuel (Manuel 11/11:
# "Scoprirò la storia che si cela dietro la raccolta del tè che consumiamo tutti i giorni"), giunte verificate con
# la trascrizione automatica; i tagli stanno sotto le immagini del tè, così non si vedono.
SPEED = 1.1                                    # tutto il reel a 1.1x alla fine (Manuel 11/11)
SP2 = 1.13 / SPEED                             # seconda frase a 1.13x in totale (Manuel 11/11 v5)
PIECES = [("115233", 11.95, 12.74, 0.0),      # Sono a Munnar,
          ("115233", 12.86, 13.48, 0.0),      # in Kerala,
          ("115233", 13.73, 15.27, 0.03),     # a oltre 1500 metri.
          ("120307", 3.52, 5.28, 0.0, SP2),   # Scoprirò l'arte che si cela dietro
          ("133625", 4.175, 4.295, 0.0, SP2), # il   (da "...raccoglie il tè", Manuel 11/11 v5)
          ("120356", 4.85, 5.15, 0.0, SP2),   # tè
          ("120356", 5.30, 6.62, 0.0, SP2)]   # che consumiamo tutti i giorni.
# v5 (Manuel 11/11): torna "l'arte"; "dietro il tè" montato da tre clip. Giunzioni provate con la trascrizione
# (audio pulito e accelerato) su una griglia di tagli: "dietro" finisce a 5.28 (prima della "qu" di "questo"), il "tè"
# parte a 4.85 (nella chiusura della t). Manuel voleva la seconda frase a 1.15x: a 1.15x "dietro" si impasta (anche
# nella frase originale senza tagli), a 1.13x resta chiara, quindi 1.13x in totale (SP2 sopra l'1.1x di tutto il reel).
# "dietro la raccolta" tolto: la giunzione "dietro|(nel)la" non veniva pulita in nessuna prova
# Manuel 11/11: nessun silenzio da "Sono a Munnar" in poi (pause dentro le frasi tolte, jump cut sul girato)
A0 = 11.80                                     # 115233 entra un attimo prima della voce (braccia che si aprono)
CAPS = [
    [("Sono", 0, 12.00), ("a", 0, 12.17), ("Munnar,", 0, 12.25)],
    [("in", 1, 12.88), ("Kerala,", 1, 12.97)],
    [("a", 2, 13.75), ("oltre", 2, 13.85), ("1.500", 2, 14.17), ("metri.", 2, 14.97)],
    [("Scoprirò", 3, 3.56), ("l'arte", 3, 4.15)],
    [("che", 3, 4.47), ("si", 3, 4.63), ("cela", 3, 4.79)],
    [("dietro", 3, 5.11), ("il", 4, 4.19), ("tè", 5, 4.90)],
    [("che", 6, 5.31), ("consumiamo", 6, 5.43)],
    [("tutti", 6, 5.99), ("i", 6, 6.15), ("giorni.", 6, 6.23)],
]
PIECES = [p if len(p) == 5 else p + (1.0,) for p in PIECES]
SHOTS, PT = [], []


def layout():
    t = T_IN + (PIECES[0][1] - A0)
    for c, a, b, g, sp in PIECES:
        PT.append(t)
        t += (b - a) / sp + g
    end_v = t
    P = PIECES
    SHOTS[:] = [
        dict(c="115233", a=A0, d=PT[1] - T_IN, cx=0.50, push=(1.12, 1.0, 0.8)),        # arrivo su Manuel
        dict(c="115233", a=P[1][1], d=PT[2] - PT[1], cx=0.50),
        dict(c="115233", a=P[2][1], d=PT[3] - PT[2], cx=0.50),
        dict(c="120307", a=P[3][1], d=piece_t(3, 4.45) - PT[3], cx=0.56, sp=SP2),       # "Scoprirò l'arte"
        dict(c="135033", a=1.0, d=piece_t(3, 5.10) - piece_t(3, 4.45), cx=0.50, push=(1.0, 1.04, 1.0)),  # "che si cela"
        dict(c="135012", a=4.0, d=PT[6] - piece_t(3, 5.10), cx=0.50, push=(1.0, 1.05, 1.3)),  # "dietro il tè"
        dict(c="120356", a=P[6][1], d=end_v - PT[6], cx=0.56, sp=SP2),                   # "che consumiamo tutti i giorni"
        dict(c="120356", a=P[6][2], d=2.3, cx=0.56, close=True),                        # chiusura
    ]
    t = T_IN
    for s in SHOTS:
        s["t"] = t
        t += s["d"]
    return t


def piece_t(i, x):
    return PT[i] + (x - PIECES[i][1]) / PIECES[i][4]


def shot_video(i, s):
    p = f"{WK}/shot_{i}.mkv"
    n = int(round(s["d"] * FPS))
    cw = "ih*9/16"
    if "pan" in s:
        c0, c1, ta, tb = s["pan"]
        u = f"min(1,max(0,(t-{ta})/{tb - ta}))"
        cx = f"({c0}+({c1}-{c0})*({u})*({u})*(3-2*({u})))"
    else:
        cx = str(s.get("cx", 0.5))
    sp = s.get("sp", 1.0)
    vf = [f"setpts=PTS/{sp}", f"fps={FPS}", f"crop={cw}:ih:'max(0,min(iw-ow,iw*{cx}-ow/2))':0", f"scale={W}:{H}:flags=lanczos", GRADE]
    if "push" in s:
        z0, z1, T = s["push"]
        z = f"({z0}+({z1}-{z0})*(1-pow(1-min(1\\,t/{T})\\,3)))"
        vf.append(f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame:flags=bicubic,crop={W}:{H}")
    vf += ["tpad=stop_mode=clone:stop_duration=3", f"trim=end_frame={n}", "setpts=PTS-STARTPTS", "format=yuv420p"]
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['d'] * sp + 1:.3f}", "-i", clip(s["c"]), "-an",
         "-vf", ",".join(vf), "-frames:v", str(n), "-c:v", "libx264", "-crf", "10", "-preset", "veryfast", p])
    return p


def base_video():
    parts = [f"{WK}/space.mkv"]
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{SZ}/%04d.png", "-frames:v",
         str(int(round(T_IN * FPS))), "-c:v", "libx264", "-crf", "10", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         parts[0]])
    for i, s in enumerate(SHOTS):
        parts.append(shot_video(i, s))
    lst = f"{WK}/parts.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    out = f"{WK}/base.mkv"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    return out


# ---------------- grafica sopra (sottotitoli, arrivo, chiusura) ----------------
def caption_img(words, k):
    f = ImageFont.truetype(F_CAP, 66)
    sp = f.getlength(" ")
    ws = [f.getlength(w) for w, _ in words]
    tw = sum(ws) + sp * (len(words) - 1)
    padx, bh = 34, 104
    im = Image.new("RGBA", (int(tw + 2 * padx), bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, bh - 1], radius=22, fill=(10, 10, 10, 150))
    x = padx
    for j, (w, _) in enumerate(words):
        col = GOLD + (255,) if j == k else (255, 255, 255, 255)
        d.text((x, bh / 2 + 2), w, font=f, fill=col, anchor="lm")
        x += ws[j] + sp
    return np.array(im)


def end_layers():
    f = ImageFont.truetype(F_END, 84)
    txt = "Video fuori sul canale"
    tw = f.getlength(txt)
    t = Image.new("RGBA", (W, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.text((W / 2 + 2, 72), txt, font=f, fill=(0, 0, 0, 120), anchor="mm")
    t = t.filter(ImageFilter.GaussianBlur(4))
    d = ImageDraw.Draw(t)
    d.text((W / 2, 70), txt, font=f, fill=(255, 255, 255, 255), anchor="mm")
    # filo d'oro sotto la scritta
    d.line([(W / 2 - 70, 132), (W / 2 + 70, 132)], fill=GOLD + (255,), width=3)
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    lw = int(W * 0.66)
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    return np.array(t), np.array(lg)


def over(dst, src, x, y, alpha=1.0):
    h, w = src.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = s[..., 3:4] / 255 * alpha
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + s[..., :3][..., ::-1] * a


def compose(base, total):
    caps = []
    for ws in CAPS:
        ts = [piece_t(i, x) for _, i, x in ws]
        caps.append(([(w, x) for w, _, x in ws], ts))
    cap_end = []
    for i, (ws, ts) in enumerate(caps):
        nxt = caps[i + 1][1][0] if i + 1 < len(caps) else None
        last_t = ts[-1] + 0.45
        cap_end.append(min(nxt, last_t + 0.4) if nxt else last_t)
    cache = {}
    tl, lg = end_layers()
    sc = [s for s in SHOTS if s.get("close")][0]
    t_close = sc["t"]
    arr = SHOTS[0]["t"]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "slow",
                            "-pix_fmt", "yuv420p", f"{WK}/comp.mkv"], stdin=subprocess.PIPE)
    n = int(round(total * FPS))
    white_last = cv2.imread(sorted(glob.glob(f"{SZ}/*.png"))[-1]).astype(np.float32)
    for i in range(n):
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        t = i / FPS
        # arrivo: il bianco delle nuvole si apre sul girato, con un mosso radiale che si spegne
        if arr <= t < arr + 0.55:
            u = (t - arr) / 0.55
            k = 1 + 0.09 * (1 - u) ** 2
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, k)
            fr = 0.55 * fr + 0.45 * cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT) if u < 0.7 else fr
            wv = (1 - u) ** 1.6
            fr = fr * (1 - wv) + white_last * wv
        # chiusura: sfocatura e velo che salgono, poi scritta e logo
        if t >= t_close:
            u = t - t_close
            b = min(1.0, u / 0.5)
            b = b * b * (3 - 2 * b)
            if b > 0:
                sig = 0.5 + 26 * b
                fr = cv2.GaussianBlur(fr, (0, 0), sig)
                fr *= (1 - 0.45 * b)
            ta = min(1, max(0, (u - 0.15) / 0.5))
            dy = int(18 * (1 - ta) ** 2)
            over(fr, tl, 0, int(H * 0.325) + dy, ta)
            la = min(1, max(0, (u - 0.45) / 0.6))
            if la > 0:
                s = 1.04 - 0.04 * (la * la * (3 - 2 * la))
                l2 = cv2.resize(lg, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
                over(fr, l2, (W - l2.shape[1]) // 2, int(H * 0.47) - (l2.shape[0] - lg.shape[0]) // 2, la)
        # sottotitoli
        for j, (ws, ts) in enumerate(caps):
            if ts[0] - 0.04 <= t < cap_end[j]:
                k = max(q for q in range(len(ts)) if ts[q] - 0.04 <= t)
                key = (j, k)
                if key not in cache:
                    cache[key] = caption_img(ws, k)
                im = cache[key]
                over(fr, im, (W - im.shape[1]) // 2, 1290)
                break
        enc.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    return f"{WK}/comp.mkv"


# ---------------- audio ----------------
def lufs_of(x):
    p = f"{WK}/_l.wav"
    sf.write(p, x.astype(np.float32), SR)
    e = run(["ffmpeg", "-hide_banner", "-i", p, "-af", "loudnorm=print_format=json", "-f", "null", "-"]).stderr
    return float(json.loads(e.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def whoosh(total):
    """Suono del movimento: aria che sale (rumore rosa filtrato che si apre), corpo basso, picco nelle nuvole,
    poi coda d'aria all'arrivo. Sintetizzato qui."""
    rng = np.random.default_rng(3)
    n = int(round(total * SR))
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    tp = T_IN - 0.05                                        # picco: si buca il bianco
    for ch in range(2):
        w = rng.standard_normal(n)
        X = np.fft.rfft(w)
        f = np.fft.rfftfreq(n, 1 / SR)
        X /= np.sqrt(np.maximum(f, 20))                        # rosa
        pink = np.fft.irfft(X, n)
        pink /= np.abs(pink).max()
        # filtro passa-basso che si apre col tempo (frame da 10 ms)
        y = np.zeros(n)
        hop = 480
        state = 0.0
        for s0 in range(0, n, hop):
            tt = s0 / SR
            fc = 180 + 5200 * (min(1, max(0, tt / tp)) ** 2.2) if tt < tp else 5400 * math.exp(-(tt - tp) / 0.35) + 300
            a = math.exp(-2 * math.pi * fc / SR)
            seg = pink[s0:s0 + hop]
            o = np.empty_like(seg)
            for q in range(len(seg)):
                state = a * state + (1 - a) * seg[q]
                o[q] = state
            y[s0:s0 + hop] = o
        env = np.where(t < tp, (np.clip(t / tp, 0, 1)) ** 2.6, np.exp(-(t - tp) / 0.16))
        env *= np.clip(t / 0.25, 0, 1)
        out[:, ch] = y / (np.abs(y).max() + 1e-9) * env
    # corpo basso che sale e un colpo morbido all'arrivo
    sub = np.sin(2 * np.pi * (38 + 30 * np.clip(t / tp, 0, 1)) * t) * np.where(t < tp, np.clip(t / tp, 0, 1) ** 3,
                                                                             np.exp(-(t - tp) / 0.14))
    out += 0.35 * sub[:, None]
    # piccolo soffio sul logo
    tl = SHOTS[-1]["t"] + 0.45
    m = (t > tl) & (t < tl + 1.0)
    out[m] += 0.05 * rng.standard_normal((m.sum(), 2)) * np.sin(np.pi * (t[m] - tl) / 1.0)[:, None] ** 2
    return out / np.abs(out).max()


def audio(total):
    n = int(round(total * SR))
    voice = np.zeros((n, 2))
    # i pezzi consecutivi con la stessa velocità si uniscono prima e si accelerano insieme (atempo, tono invariato)
    groups = []
    for i, (c, a, b, g, sp) in enumerate(PIECES):
        src = cleaned(clip(c), f"{WK}/voce")
        x, sr = sf.read(src, dtype="float64")
        assert sr == SR
        x = x if x.ndim == 1 else x.mean(1)
        seg = x[int(a * SR):int(b * SR)].copy()
        fl = int(0.005 * SR)
        seg[:fl] *= np.linspace(0, 1, fl); seg[-fl:] *= np.linspace(1, 0, fl)
        if groups and groups[-1][1] == sp and sp != 1.0 and PIECES[i - 1][3] == 0:
            groups[-1][2].append(seg)
        else:
            groups.append([PT[i], sp, [seg]])
    for t0, sp, segs in groups:
        seg = np.concatenate(segs)
        if sp != 1.0:
            sf.write(f"{WK}/_s.wav", seg.astype(np.float32), SR, subtype="FLOAT")
            run(["ffmpeg", "-v", "error", "-y", "-i", f"{WK}/_s.wav", "-af", f"atempo={sp:.6f}", "-c:a", "pcm_f32le",
                 f"{WK}/_t.wav"])
            seg = sf.read(f"{WK}/_t.wav", dtype="float64")[0]
        t0 = int(round(t0 * SR))
        voice[t0:t0 + len(seg)] += seg[:n - t0, None]
    voice *= 10 ** ((-16 - lufs_of(voice)) / 20)
    wh = whoosh(total)
    wh *= 10 ** ((-19 - lufs_of(wh[:int((T_IN + 1) * SR)])) / 20)
    mix = voice + wh
    p = f"{WK}/mix.wav"
    sf.write(f"{WK}/mix_pre.wav", mix.astype(np.float32), SR, subtype="FLOAT")
    m = json.loads(run(["ffmpeg", "-hide_banner", "-i", f"{WK}/mix_pre.wav", "-af",
                        "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"]).stderr
                   .split("[Parsed_loudnorm")[-1].split("\n", 1)[1])
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{WK}/mix_pre.wav", "-af",
         f"volume={-14 - float(m['input_i']):.2f}dB,alimiter=limit=0.89:attack=2:release=60:level=false:latency=1",
         "-ar", str(SR), "-c:a", "pcm_s16le", p])
    return p


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    total = layout()
    print(f"discesa {T_SPACE:.2f} s, girato da {T_IN:.2f} s, totale {total:.2f} s")
    base = base_video() if "--reuse" not in sys.argv or not os.path.exists(f"{WK}/base.mkv") else f"{WK}/base.mkv"
    comp = f"{WK}/comp.mkv" if "--audio" in sys.argv else compose(base, total)
    mix = audio(total)
    run(["ffmpeg", "-v", "error", "-y", "-i", comp, "-i", mix, "-filter_complex",
         f"[0:v]setpts=PTS/{SPEED},fps={FPS}[v];[1:a]atempo={SPEED}[a]", "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", f"{total / SPEED:.3f}", OUT])
    print(OUT)


if __name__ == "__main__":
    main()
