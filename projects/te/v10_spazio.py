#!/usr/bin/env python3
"""te v10 (Manuel 11/11, via Insights): la discesa dallo spazio del reel "spazio Munnar" nel lungo, dopo la sigla.

Parte dal lungo v9 consegnato (work/te/v9in/VociVere_te_long_4K.mp4, 6:25.92) e cambia solo i fotogrammi 739-887
(24.633-29.600 s, tra due fotogrammi chiave del v9: il resto si copia senza ricodifica):
- 24.633-27.0: discesa dallo spazio in 16:9 4K (tools/space_zoom.py --size 3840x2160 --fov 48, 2.4 s) sotto
  "Sono a Munnar, in Kerala"; atterra nel bianco delle nuvole su Manuel a braccia aperte (115233, labiale in sincrono:
  la clip nel lungo va a 1.1x) per "a oltre 1500 metri", con lo stesso arrivo del reel;
- 28.10-29.60: le colline (132930, stesso inizio) rifatte senza il vecchio banner, con un avvicinamento leggero;
- etichetta "Munnar, Kerala" come nel v9 (stessi tempi e stile).
Banner "iscriviti" spostato (Manuel 11/11: 5-10 s dopo la sigla): via quello a 24.8 (click tolti dall'audio), nuovo a
BANNER_T con tools/apply_banners.py. Audio: il suono del movimento del reel (sintetizzato) sotto la discesa.
Durata, parlato, sottotitoli e capitoli invariati.
    python3 projects/te/v10_spazio.py   (girato 115233 e 132930 in work/spazio/raw, discesa in work/te/sz4k)
"""
import glob, json, math, os, subprocess, sys
import numpy as np, cv2, soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IN = f"{ROOT}/work/te/v9in/VociVere_te_long_4K.mp4"
V = f"{ROOT}/work/te/v10"
SZ = f"{ROOT}/work/te/sz4k"
OUT = f"{ROOT}/work/te/VociVere_te_long_4K_v10.mp4"
RAW = f"{ROOT}/work/spazio/raw"
W, H, FPS, SR = 3840, 2160, 30, 48000
F0, F1 = 739, 888                       # fotogrammi rifatti: [F0, F1)
F_HILLS = 843                           # taglio Manuel -> colline nel v9
T0 = F0 / FPS
C0 = 11.852                             # 115233: tempo nella clip a T0 (dalla correlazione dell'audio), poi 1.1x
OLD_BANNER, BANNER_T = 24.8, 33.5       # banner iscriviti: vecchio (click da togliere) e nuovo
DEF = "eq=contrast=1.03:saturation=1.05"
X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "38M", "-bufsize", "76M", "-profile:v", "high",
        "-level", "5.1", "-pix_fmt", "yuv420p", "-g", "250", "-keyint_min", "25", "-x264-params", "open_gop=0"]
os.makedirs(V, exist_ok=True)


def clip(k):
    return glob.glob(f"{RAW}/*{k}*.MP4")[0]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode:
        print(" ".join(map(str, cmd))[:600]); print(r.stderr[-2000:]); sys.exit(1)
    return r.stdout


def frames_of(src, ss, n, vf):
    raw = run(["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-i", src, "-frames:v", str(n), "-vf", vf, "-f", "rawvideo",
               "-pix_fmt", "bgr24", "-"])
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    assert len(a) == n, (src, len(a), n)
    return a


def label_ass():
    k = 2.0
    S = lambda v: int(round(v * k))
    p = f"{V}/label.ass"
    with open(p, "w") as f:
        f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Lab,Playfair Display,{S(46)},&H00F2F2F2,&H00FFFFFF,&H00000000,&H80000000,0,-1,0,0,100,100,0.5,0,1,"
                f"{S(1.2)},{S(2.2)},1,{S(70)},{S(70)},{S(64)},1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                "Dialogue: 1,0:00:00.30,0:00:02.90,Lab,,0,0,0,,{\\fad(350,350)}Munnar, Kerala\n")
    return p


def video():
    n = F1 - F0
    desc = sorted(glob.glob(f"{SZ}/*.png"))
    nd = len(desc)
    f_arr = F0 + nd - round(0.22 * FPS)                  # Manuel entra sotto il bianco, come nel reel
    n_man = F_HILLS - f_arr
    man = frames_of(clip("115233"), C0 + 1.1 * (f_arr / FPS - T0), n_man,
                    f"setpts=PTS/1.1,fps={FPS},scale={W}:{H}:flags=lanczos,{DEF}")
    nh = F1 - F_HILLS
    z = f"(1+0.05*t/{nh / FPS:.3f})"
    hills = frames_of(clip("132930"), 0.567, nh, f"fps={FPS},scale={W}:{H}:flags=lanczos,{DEF},"
                      f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame:flags=bicubic,crop={W}:{H}")
    white = cv2.imread(desc[-1]).astype(np.float32)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r",
                            str(FPS), "-i", "-", "-vf", f"ass={label_ass()}:fontsdir={ROOT}/models", *X264,
                            f"{V}/seg.mp4"], stdin=subprocess.PIPE)
    for f in range(F0, F1):
        if f < f_arr:
            fr = cv2.imread(desc[f - F0])
        elif f < F_HILLS:
            fr = man[f - f_arr]
            u = (f - f_arr) / FPS / 0.55
            if u < 1:                                    # arrivo: il bianco si apre sul girato, mosso radiale
                x = fr.astype(np.float32)
                if u < 0.7:
                    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + 0.09 * (1 - u) ** 2)
                    x = 0.55 * x + 0.45 * cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
                wv = (1 - u) ** 1.6
                fr = np.clip(x * (1 - wv) + white * wv, 0, 255).astype(np.uint8)
        else:
            fr = hills[f - F_HILLS]
        enc.stdin.write(np.ascontiguousarray(fr).tobytes())
    enc.stdin.close(); enc.wait()
    print("segmento", n, "fotogrammi; discesa", nd, "arrivo su Manuel al fotogramma", f_arr)
    return f"{V}/seg.mp4", (f_arr - F0) / FPS


def whoosh(n, tp, start=0.32):
    """Il suono del movimento del reel (projects/spazio_munnar/build.py), con picco tp s dopo l'inizio."""
    rng = np.random.default_rng(3)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for ch in range(2):
        X = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        X /= np.sqrt(np.maximum(f, 20))
        pink = np.fft.irfft(X, n); pink /= np.abs(pink).max()
        y = np.zeros(n); state = 0.0; hop = 480
        for s0 in range(0, n, hop):
            tt = s0 / SR
            fc = 650 + 4750 * (min(1, max(0, tt / tp)) ** 1.8) if tt < tp else 5400 * math.exp(-(tt - tp) / 0.35) + 300
            a = math.exp(-2 * math.pi * fc / SR)
            seg = pink[s0:s0 + hop]; o = np.empty_like(seg)
            for q in range(len(seg)):
                state = a * state + (1 - a) * seg[q]; o[q] = state
            y[s0:s0 + hop] = o
        env = np.where(t < tp, start + (1 - start) * np.clip(t / tp, 0, 1) ** 1.8, np.exp(-(t - tp) / 0.16))
        env *= np.clip(t / 0.06, 0, 1)
        out[:, ch] = y / (np.abs(y).max() + 1e-9) * env
    sub = np.sin(2 * np.pi * (38 + 30 * np.clip(t / tp, 0, 1)) * t) * np.where(t < tp, 0.2 + 0.8 * np.clip(t / tp, 0, 1) ** 2,
                                                                             np.exp(-(t - tp) / 0.14))
    out += 0.35 * sub[:, None]
    return out / np.abs(out).max()


def lufs(x):
    p = f"{V}/_l.wav"
    sf.write(p, x.astype(np.float32), SR)
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(json.loads(e.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def audio(t_arr):
    raw = run(["ffmpeg", "-v", "error", "-i", IN, "-map", "0:a", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64).copy()
    # via i click del vecchio banner: stesso file di tools/apply_banners.py, guadagno stimato sui click (minimi quadrati)
    c, _ = sf.read(f"{ROOT}/work/banner/banner_iscriviti_click.wav", dtype="float64")
    c = c if c.ndim == 2 else np.repeat(c[:, None], 2, 1)
    i0 = int(round(OLD_BANNER * SR))
    seg = a[i0:i0 + len(c)]
    m = np.abs(c).max(1) > 1e-4
    for ch in range(2):
        g = np.dot(seg[m, ch], c[m, ch]) / np.dot(c[m, ch], c[m, ch])
        before = np.sqrt(np.mean(seg[m, ch] ** 2))
        seg[:, ch] -= g * c[:, ch]
        print(f"click canale {ch}: guadagno {g:.3f}, livello sui click {20 * np.log10(before):.1f} -> "
              f"{20 * np.log10(np.sqrt(np.mean(seg[m, ch] ** 2))):.1f} dB")
    # suono del movimento: dall'inizio della discesa al bianco, 8 dB sotto la voce di "Sono a Munnar..."
    tp = t_arr + 0.2
    wh = whoosh(int((tp + 1.2) * SR), tp)
    voice = lufs(a[int(24.8 * SR):int(27.8 * SR)])
    wh *= 10 ** ((voice - 8 - lufs(wh[:int(tp * SR)])) / 20)
    j0 = int(round(T0 * SR))
    a[j0:j0 + len(wh)] += wh
    peak = np.abs(a).max()
    print(f"voce {voice:.1f} LUFS, picco del mix {20 * np.log10(peak):.1f} dBFS")
    p = f"{V}/audio.wav"
    sf.write(p, a.astype(np.float32), SR, subtype="FLOAT")
    return p


def main():
    if os.environ.get("REUSE") and os.path.exists(f"{V}/seg.mp4"):
        seg, t_arr = f"{V}/seg.mp4", (F0 + len(glob.glob(f"{SZ}/*.png")) - round(0.22 * FPS) - F0) / FPS
    else:
        seg, t_arr = video()
    aud = audio(t_arr)
    lst = f"{V}/list.txt"
    run(["ffmpeg", "-v", "error", "-y", "-i", IN, "-map", "0:v", "-c", "copy", "-frames:v", str(F0), f"{V}/a.mp4"])
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{F1 / FPS:.6f}", "-i", IN, "-map", "0:v", "-c", "copy", f"{V}/c.mp4"])
    open(lst, "w").write("".join(f"file '{V}/{x}'\n" for x in ("a.mp4", "seg.mp4", "c.mp4")))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{V}/video.mp4"])
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/video.mp4", "-i", aud, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "pcm_s24le", f"{V}/nobanner.mov"])
    run(["python3", f"{ROOT}/tools/apply_banners.py", f"{V}/nobanner.mov", OUT, "--iscriviti", str(BANNER_T)])
    print(OUT)


if __name__ == "__main__":
    main()
