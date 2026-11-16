#!/usr/bin/env python3
"""fortkochi (NGO): Ashwasa Bhavan (Veli, Fort Kochi) e Raksha (Kochangadi, Kochi), girato il 13/11.

    python3 projects/fortkochi/build.py long [--preview]
Girato in work/fortkochi/raw (Drive "Kochi NGO" 1J2VdasjXPmTi9OTbMbNYrBbV9_BH3EZc, rclone), voiceover e camera in
work/fortkochi/vo ("Voice Over + Camera"). Copione: copioni/fortkochi_testi.md, "COPIONE v3" + "VOICEOVER REGISTRATI"
+ "CORREZIONI E CAMERA" (Copy 16/11). Girato e scelte: projects/fortkochi/girato.md; decisioni di Manuel: brief.md.
Stesso motore di coir (projects/coir/build.py), con il montato a 23.976 fps come il girato (DOC_FPS, Manuel 16/11:
fluidità). Musica originale fatta da Montaggio (projects/fortkochi/musica.py, Manuel 16/11), poca e bassa.
Bambini di Ashwasa: clip già sfocate da tools/face_blur.py (work/fortkochi/blur). 0039 ruotata di 180° (work/fortkochi/rot),
solo la parte centrale con la sala (Manuel 16/11).
"""
import glob, json, os, subprocess, sys
os.environ.setdefault("DOC_FPS", "24000/1001")
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, dur_of, ts, FPS
from sigla import sigla_d
from voice_clean import cleaned

PREVIEW = "--preview" in sys.argv
WORK = f"{ROOT}/work/fortkochi"
R = f"{WORK}/raw"
OUT = f"{WORK}/out"
VOCE = f"{WORK}/voce2"
AUD = f"{ROOT}/projects/fortkochi/audio"
VOF = f"{WORK}/vo/vo.m4a"            # "Via Privata Flumendosa.m4a": i 18 VO
CORR = f"{WORK}/vo/corr.m4a"         # "Correzioni": blocchi 1, 4, 8
CAM = f"{WORK}/vo/IMG_9082.MOV"      # i 6 pezzi in camera (4K 30 fps)
CHIUSURA = f"{ROOT}/assets/voce/chiusura_vocivere.m4a"
os.makedirs(OUT, exist_ok=True); os.makedirs(VOCE, exist_ok=True)
DEF = "eq=contrast=1.03:saturation=1.05"
MUS = 0.075                          # musica sotto il VO: bassa, costante


def C(k):
    m = glob.glob(f"{R}/DJI_20261113*_{k}_D.MP4")
    assert len(m) == 1, (k, m)
    return m[0]


def B(k):
    """Clip con i volti dei bambini sfocati (tools/face_blur.py, controllate fotogramma per fotogramma)."""
    p = f"{WORK}/blur/{k}_blur.mp4"
    assert os.path.exists(p), p
    return p


ROT = f"{WORK}/rot/0039r.mp4"        # camminata dentro Raksha ruotata di 180°: sala 7.4-11.6


def _words():
    out = {}
    d = json.load(open(f"{WORK}/tr/interviste.json"))
    for k, w in d.items():
        out[os.path.basename(C(k))] = [(x[0], x[1]) for x in w]
    cam = json.load(open(f"{WORK}/tr/cam.json"))["cam.wav"]
    out[os.path.basename(CAM)] = [(w, t) for s in cam for w, t in s["words"]]
    return out


WORDS = _words()


def words_of(src):
    return WORDS.get(os.path.basename(src), [])


# ---------------- voce allo stesso livello (da projects/coir/build.py) ----------------
VOICE_LUFS = -18.0
FLOOR_DB = -60.0               # fondo nelle pause più basso del coir (Manuel 16/11: niente ventilatori o ronzii)


def _pcm(path, af="anull", ch=1):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", str(ch), "-ar", "48000",
                                         "-af", af, "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)


def _lufs(path, a=None, b=None):
    pre = ["-ss", str(a), "-t", str(b - a)] if a is not None else []
    out = subprocess.run(["ffmpeg", "-hide_banner", *pre, "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(json.loads(out.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def leveled(src):
    """Voce pulita (RNNoise) a -18 LUFS con guadagno fisso; il fondo della clip (stanza, ventilatore) tenuto a -60 dB e
    chiuso nelle pause (gate -30 dB). Stessi tempi della clip (labiale invariato)."""
    out = f"{VOCE}/liv_{os.path.splitext(os.path.basename(src))[0]}.wav"
    if os.path.exists(out):
        return out
    cv = cleaned(src, VOCE)
    gv = VOICE_LUFS - _lufs(cv)
    x = _pcm(src, "highpass=f=100,highpass=f=100").astype(np.float64)
    c = _pcm(cv).astype(np.float64)
    n = min(len(x), len(c)); x, c = x[:n], c[:n]
    res = np.copy(x)
    Bk = 24000
    for i in range(0, n, Bk):
        xc, cc = x[i:i + Bk], c[i:i + Bk]
        k = float(xc @ cc) / (float(cc @ cc) + 1e-9)
        res[i:i + Bk] = xc - k * cc
    h = 4800
    m = n // h
    lev = 10 * np.log10((res[:m * h].reshape(m, h) ** 2).mean(1) + 1e-12)
    lev = np.convolve(lev, np.ones(4) / 4, mode="same")
    g = np.minimum(FLOOR_DB - lev, gv - 10)
    g = np.interp(np.arange(n), (np.arange(m) + 0.5) * h, g)
    hv = 480
    mv = n // hv
    dv = 20 * np.log10(np.sqrt((c[:mv * hv].reshape(mv, hv) ** 2).mean(1)) + 1e-9)
    dv = np.convolve(dv, np.ones(5) / 5, mode="same")
    lo, hi = np.percentile(dv, 10), np.percentile(dv, 95)
    on = dv > lo + 0.2 * (hi - lo)
    on = np.convolve(on.astype(float), np.ones(27), mode="full")[6:6 + mv] > 0
    gate = np.where(on, 1.0, 10 ** (-30 / 20))
    gate = np.convolve(gate, np.ones(3) / 3, mode="same")
    gate = np.interp(np.arange(n), (np.arange(mv) + 0.5) * hv, gate)
    y = (c * 10 ** (gv / 20) + res * 10 ** (g / 20)) * gate
    y = np.clip(y, -0.98, 0.98).astype(np.float32)
    import soundfile as sf
    sf.write(out, np.stack([y, y], 1), 48000, subtype="PCM_16")
    print(f"livello {os.path.basename(src)}: voce {gv:+.1f} dB, fondo {np.median(lev):.0f} -> {FLOOR_DB:.0f} dB", flush=True)
    return out


def range_gain(src, a, b, target=-23.0):
    """dB perché la voce in [a, b] arrivi al livello delle altre (chi parla più lontano dal microfono)."""
    x = _pcm(leveled(src))[int(a * 48000):int(b * 48000)]
    h = 2400
    db = 20 * np.log10(np.sqrt((x[:len(x) // h * h].reshape(-1, h) ** 2).mean(1)) + 1e-9)
    v = db[db > max(db.max() - 20, -50)]
    return float(np.clip(target - np.median(v), 0.0, 10.0)) if len(v) else 0.0


class TL(Timeline):
    def _af(self, s):
        if not (s["norm"] and s["src"] in self.audio_map):
            return super()._af(s)
        d = s["d"]
        f = [f"atempo={s['speed']}"] if s["speed"] != 1.0 else []
        f += ["aresample=48000", f"volume={s['gain']}"]
        fd = min(s["fade"], d / 3)
        f.append(f"apad,atrim=end={d:.4f},afade=t=in:d={fd:.3f},afade=t=out:st={d - fd:.4f}:d={fd:.3f}")
        return ",".join(f)


# ---------------- tagli sulla voce vera ----------------
_VOICED = {}


def voiced(src):
    if src not in _VOICED:
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", cleaned(src, VOCE), "-map", "0:a:0", "-ac", "1",
                                          "-ar", "16000", "-af", "highpass=f=100", "-f", "f32le", "-"],
                                         capture_output=True).stdout, np.float32)
        n = len(x) // 160
        db = 20 * np.log10(np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-9)
        db = np.convolve(db, np.ones(8) / 8, mode="same")
        lo, hi = np.percentile(db, 10), np.percentile(db, 95)
        _VOICED[src] = (db > lo + 0.45 * (hi - lo), hi - lo >= 12)
    return _VOICED[src]


def snap(src, a, b, lim_a=0.0, lim_b=1e9):
    v, ok = voiced(src)
    if not ok:
        return a, b
    i, n = int(b * 100), len(v)
    if i < n and v[max(0, i - 3):i + 3].any():
        j = i
        while j < min(n, i + 80) and v[j:j + 12].any():
            j += 1
        b = min(max(b, j / 100 + 0.04), lim_b)
    i = int(a * 100)
    if 0 < i < n and v[max(0, i - 12):i + 3].any():
        j = i
        while j > max(0, i - 50) and v[max(0, j - 10):j].any():
            j -= 1
        a = max(min(a, j / 100 - 0.04), lim_a)
    return a, b


def snap_w(src, a, b):
    st = sorted(t for _, t in words_of(src))
    nxt = [t for t in st if t > b - 0.03]
    prv = [t for t in st if t <= a + 0.08]
    return snap(src, a, b, lim_a=(prv[-1] - 0.06) if prv else 0.0, lim_b=(nxt[0] - 0.02) if nxt else 1e9)


def tight(src, ranges, min_gap=0.32, keep=0.1):
    v, ok = voiced(src)
    if not ok:
        return ranges
    out = []
    for a, b in ranges:
        i = int(a * 100)
        cur = a
        while i < int(b * 100):
            if not v[min(i, len(v) - 1)]:
                j = i
                while j < int(b * 100) and not v[min(j, len(v) - 1)]:
                    j += 1
                if (j - i) / 100 >= min_gap and i / 100 > cur + 0.2 and j < int(b * 100):
                    out.append((cur, i / 100 + keep)); cur = j / 100 - keep
                i = j
            i += 1
        out.append((cur, b))
    return out


def piece(name, parts, gap=0.22, pad=(0.06, 0.1)):
    """Voiceover da uno o più file: parts = [(file, [(a, b), ...]), ...], tratti uniti con respiri di gap s,
    ogni file portato a -18 LUFS (guadagno fisso). -> (wav, durata)."""
    key = abs(hash(json.dumps(parts))) % 10 ** 8
    out = f"{OUT}/{name}_{key}.wav"
    if not os.path.exists(out):
        segs = []
        for j, (src, ranges) in enumerate(parts):
            D = dur_of(src)
            rr = [(max(0, a - pad[0]), min(D, b + pad[1])) for a, b in ranges]
            fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,"
                         f"afade=t=in:d=0.03,afade=t=out:st={(b - a) - 0.05:.3f}:d=0.05,apad=pad_dur={gap}[p{i}];"
                         for i, (a, b) in enumerate(rr))
            tot = sum(b - a + gap for a, b in rr)
            fc += "".join(f"[p{i}]" for i in range(len(rr))) + f"concat=n={len(rr)}:v=0:a=1,atrim=end={tot:.3f}[o]"
            tmp = out.replace(".wav", f"_t{j}.wav")
            run(["ffmpeg", "-v", "error", "-y", "-i", cleaned(src, VOCE), "-filter_complex", fc, "-map", "[o]", "-ac", "1",
                 "-ar", "48000", tmp])
            g = VOICE_LUFS - _lufs(tmp)
            tmp2 = out.replace(".wav", f"_g{j}.wav")
            run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={g:.2f}dB", "-ac", "1", "-ar", "48000", tmp2])
            segs.append(tmp2); os.remove(tmp)
        lst = out.replace(".wav", "_l.txt")
        open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
             "-ac", "1", "-ar", "48000", out])
        x = _pcm(out)                                   # via l'ultimo respiro
        sf_n = len(x) - int(gap * 48000)
        import soundfile as sf
        sf.write(out, x[:sf_n], 48000, subtype="PCM_16")
        for s in segs:
            os.remove(s)
        os.remove(lst)
    return out, dur_of(out)


# ---------------- montaggio ----------------
class Edit:
    def __init__(self, W, H, tag):
        self.tl = TL(W, H, f"{OUT}/{tag}_work")
        self.W, self.H, self.k = W, H, H / 1080
        self.cards = []

    @property
    def t(self):
        return self.tl.t

    def b(self, src, a, d, cx=0.5, speed=1.0, zoom=1.0, zy=0.4, push=True):
        """B-roll muto: sotto solo voce, voiceover o musica (Manuel 16/11: il suono del girato dei B-roll si azzera)."""
        self.tl.broll(src, a, d, gain=0.0, cx=cx, grade=DEF, zoom=zoom,
                      fx=dict(zoom=(1.0, 1.035, None)) if (push and zoom == 1.0) else None, speed=speed, fade=0.12)
        if zoom != 1.0:
            self.tl.shots[-1]["zy"] = zy

    def say(self, src, ranges, cover=None, subs=(), cut_gaps=True, pad=(0.06, 0.12), exact=False, lift=False,
            zooms=None, grade=DEF):
        """Parlato con la voce livellata; cover = {indice: (clip, inizio)} copre quel tratto con un'altra immagine
        mentre la voce continua (B-roll che segue il parlato). subs (inizio, fine, testo) in tempi della sorgente.
        zooms: un ingrandimento per tratto (camera: tagli alternati 1.0 / 1.12, il salto non si vede)."""
        cover = cover or {}
        D = dur_of(src)
        if not exact:
            ranges = [snap_w(src, a, b) for a, b in ranges]
        if cut_gaps and not cover:
            ranges = tight(src, ranges)
        padded = []
        for i, (a, b) in enumerate(ranges):
            nxt = ranges[i + 1][0] if i + 1 < len(ranges) else D
            prv = padded[-1][1] if padded else 0.0
            padded.append((max(prv, a - pad[0], 0.0), min(b + pad[1], nxt, D - 0.05)))
        self.tl.audio_map[src] = leveled(src)
        for i, (a, b) in enumerate(padded):
            t0 = self.t
            g = 10 ** (range_gain(src, a, b) / 20) if lift else 1.0
            if i in cover:
                src2, a2 = cover[i][:2]
                self.tl._add(src2, a2, b - a, gain=0.0, grade=DEF, fade=0.05, fx=dict(zoom=(1.0, 1.035, None)))
                self.tl.vos.append(dict(file=src, a=a, b=b, speed=1.0, t=t0, lev=True, raw=True, af=f"volume={g:.3f}"))
            else:
                z = zooms[i % len(zooms)] if zooms else 1.0
                self.tl.speech(src, [(a, b)], grade=grade, gain=g, zoom=z)
                if z != 1.0:
                    self.tl.shots[-1]["zy"] = 0.25
            for sa, sb, txt in subs:
                lo, hi = max(sa, a), min(sb, b)
                if hi - lo > 0.15:
                    self.tl.subs.append((t0 + (lo - a), t0 + (hi - a), txt))

    def cam(self, ranges):
        """Manuel in camera col fondale: tagli tra le prese con zoom alternato, voce livellata, niente sottotitoli."""
        self.say(CAM, ranges, zooms=[1.0, 1.12], pad=(0.06, 0.12), exact=True, grade="eq=contrast=1.02:saturation=1.0")

    def vo(self, name, parts, items, lead=0.15, tail=0.22):
        """Voiceover sopra immagini mute: items = [(clip, inizio, durata o None[, opzioni di b()])]. -> (t, durata)."""
        f, d = piece(f"vo_{name}", parts)
        t0 = self.t
        self.tl.vos.append(dict(file=f, a=0, b=d, speed=1.0, t=t0 + lead, raw=True))
        total = lead + d + tail
        fixed = sum(x[2] for x in items if x[2])
        rest = max(0.8, total - fixed) / max(1, sum(1 for x in items if not x[2]))
        for it in items:
            self.b(it[0], it[1], it[2] or rest, **(it[3] if len(it) > 3 else {}))
        return t0 + lead, d

    def ass(self):
        k, W, H = self.k, self.W, self.H
        S = lambda v: int(round(v * k))
        sub = self.tl.sub_size
        head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Sub,Poppins Medium,{sub},&H0098D8F2,&H0098D8F2,&H00000000,&H90000000,0,0,0,0,100,100,"
                f"0.5,0,1,{sub / 32:.1f},{sub / 36:.1f},2,{int(W * 0.1)},{int(W * 0.1)},{self.tl.sub_margin},1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        p = f"{self.tl.dir}/scritte.ass"
        with open(p, "w") as f:
            f.write(head)
            for a, b, txt in sorted(self.tl.subs):
                f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{txt}\n")
        return p

    def render(self, out):
        self.tl.fix_freezes()
        for prev, sh in zip(self.tl.shots, self.tl.shots[1:]):      # dissolvenze brevi solo tra B-roll muti
            if not (prev["norm"] or sh["norm"] or "sigla" in sh["src"] or "sigla" in prev["src"]) and sh["d"] > 0.6 \
                    and prev["d"] > 0.3 and sh["src"] != prev["src"] and "chiusura_" not in sh["src"]:
                sh["xin"] = 0.25
        self.tl.ass_override = self.ass()
        for v in self.tl.vos:
            if v.get("lev"):
                v["file"] = self.tl.audio_map[v["file"]]
        self.tl.nat_af = "highpass=f=90"
        print(f"== {os.path.basename(out)}: {len(self.tl.shots)} inquadrature, {self.t:.1f} s", flush=True)
        if PREVIEW:
            return self.tl.render(out, crf=26, preset="veryfast")
        self.tl.drop_shots = True
        self.tl.direct_concat = True
        self.tl.shot_crf = 17
        self.tl.final_opts = ["-maxrate", "38M", "-bufsize", "76M"]
        return self.tl.render(out, crf=20, preset="medium")


def music(tl, name, t0, t1, offset=0.0, level=MUS, fin=1.0, fout=1.2):
    tl.music(t0, t1, f"{AUD}/fk_{name}.flac", offset=offset, level=level, fin=fin, fout=fout, duck=False, norm=False)
    return offset + (t1 - t0)


def closing_visual(W, H, items, dur, card_at, card_dur):
    """Immagini della chiusura senza volti (schermata finale) in una clip sola, con la scritta finale animata."""
    tag = "_".join(f"{os.path.basename(c)[:28]}{a:.1f}" for c, a in items)
    out = f"{OUT}/chiusura_{abs(hash(tag)) % 10**8}_{dur:.2f}_{card_at:.2f}_{W}x{H}.mp4"
    if os.path.exists(out):
        return out
    fr = f"{OUT}/scritta_{W}x{H}_{card_dur:.2f}"
    if not os.path.exists(f"{fr}/0000.png"):
        run(["python3", f"{ROOT}/tools/scritta_finale.py", fr, "--w", str(W), "--h", str(H), "--dur", f"{card_dur:.2f}",
             "--fadeout", "0.6"])
    d = dur / len(items)
    ins, fc = [], ""
    for i, (c, a) in enumerate(items):
        ins += ["-ss", f"{a:.2f}", "-t", f"{d + 0.5:.2f}", "-i", c]
        fc += (f"[{i}:v]scale={W}:{H}:flags=lanczos,{DEF},fps=30,setpts=PTS-STARTPTS,trim=duration={d:.3f},"
               f"setpts=PTS-STARTPTS[v{i}];")
    fc += "".join(f"[v{i}]" for i in range(len(items))) + f"concat=n={len(items)}:v=1:a=0[bg];"
    n = len(items)
    fc += (f"[{n}:v]setpts=PTS-STARTPTS+{card_at:.3f}/TB[ov];[bg][ov]overlay=eof_action=pass:format=auto,"
           f"format=yuv420p[o]")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-framerate", "30", "-i", f"{fr}/%04d.png", "-filter_complex", fc,
         "-map", "[o]", "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "medium", out])
    return out


# ---------------- copione v3 (prese buone misurate sulla trascrizione, 16/11) ----------------
V = {1: [(CORR, [(9.95, 14.95), (15.4, 18.3)])],
     2: [(VOF, [(44.85, 49.65), (54.72, 61.6)])],
     4: [(CORR, [(64.2, 73.9)])],
     5: [(VOF, [(80.4, 81.9)])], 6: [(VOF, [(90.85, 93.15)])], 7: [(VOF, [(94.15, 98.6)])],
     8: [(VOF, [(100.05, 101.95)]), (CORR, [(36.62, 41.95)]), (VOF, [(107.2, 108.95), (110.55, 114.4)])],
     9: [(VOF, [(116.45, 120.6), (121.0, 123.0)])], 10: [(VOF, [(126.4, 135.4)])], 11: [(VOF, [(149.55, 155.9)])],
     12: [(VOF, [(162.35, 164.0)])], 13: [(VOF, [(165.25, 166.3)])], 15: [(VOF, [(169.15, 177.2)])],
     16: [(VOF, [(181.45, 186.75), (197.5, 201.0)])], 18: [(VOF, [(204.75, 211.8)])], 21: [(VOF, [(214.6, 216.85)])],
     23: [(VOF, [(219.9, 230.8)])], 24: [(VOF, [(232.35, 236.8)])]}
CAMR = {3: [(13.2, 15.2), (45.4, 47.95), (53.8, 55.75), (61.3, 62.8), (67.95, 71.3), (115.2, 118.5)],
        14: [(170.6, 172.1), (172.6, 176.8), (177.6, 180.0), (185.0, 187.6)],
        17: [(195.5, 198.9), (220.78, 224.25), (252.93, 258.85)],
        19: [(271.0, 272.75), (279.6, 282.2)],
        20: [(303.9, 306.3), (306.9, 311.2)],
        22: [(325.25, 328.6), (346.18, 348.25), (353.48, 356.62), (382.68, 386.72), (430.08, 433.1), (436.88, 438.77)]}
I = dict(cut_gaps=False, lift=True, exact=True, pad=(0.05, 0.1))     # interviste: tagli esatti sulle risposte

SIGLA_CLIPS = [(C("0029"), 2.0), (C("0025"), 0.5), (ROT, 8.6), (C("0022"), 1.5), (C("0023"), 0.5), (C("0015"), 8.0)]


def long_video(W, H):
    e = Edit(W, H, "long")
    tl = e.tl
    vo = lambda n, items, **kw: e.vo(str(n), V[n], items, **kw)
    E35, E16, E18, E19 = C("0035"), C("0016"), C("0018"), C("0019")

    # 0. APERTURA: l'educatrice di Raksha, la promessa del video (titolo e miniatura); poi la sala, VO1, VO2, sigla
    e.say(E35, [(244.1, 247.95), (248.2, 249.85), (249.85, 252.2), (252.2, 257.65), (257.65, 263.6), (263.6, 268.1)],
          cover={1: (ROT, 7.45), 2: (ROT, 9.15)},
          subs=[(244.1, 247.95, "Quello che cerchiamo di far capire alla comunità è che"),
                (248.2, 252.2, "questi bambini sono come gli altri bambini."),
                (252.2, 257.65, "Le capacità che hanno gli altri bambini, le hanno anche i nostri,"),
                (257.65, 260.25, "solo che lo fanno in un modo diverso."),
                (260.25, 263.6, "In un modo diverso, con uno stile diverso, a una velocità diversa."),
                (263.6, 268.1, "Dobbiamo solo guidarli e dargli la formazione giusta.")], **I)
    t_v1 = e.t
    vo(1, [(C("0034"), 0.0, 2.1), (C("0037"), 6.9, 3.0), (C("0042"), 0.2, None)])
    vo(2, [(C("0029"), 0.0, 3.2), (B("0003"), 4.2, 2.4), (C("0025"), 0.1, 2.9), (C("0006"), 0.4, None)], tail=0.5)
    music(tl, "apertura", t_v1 - 0.3, e.t + 0.2, fin=1.2, fout=0.8)
    t_sigla = sigla_d(tl, OUT, clips=SIGLA_CLIPS, tag="fortkochi")
    t_dopo_sigla = e.t

    # 1. IN CAMERA: dove siamo, i due posti
    e.cam(CAMR[3])

    # 2. ASHWASA
    t_ash = e.t
    vo(4, [(C("0015"), 0.5, 3.4), (C("0002"), 0.3, 3.2), (C("0005"), 3.4, None)])
    e.say(E16, [(30.9, 34.85), (36.0, 38.4), (40.85, 45.3), (47.0, 50.95)],
          subs=[(30.9, 34.85, "Dal 2006 ha cominciato suor Fabiola."), (36.0, 38.4, "È lei che l'ha aperta."),
                (40.85, 45.3, "Sono vent'anni che portiamo avanti questa casa."),
                (47.0, 50.95, "Da qui sono passati più di cento bambini.")], **I)
    vo(5, [(C("0021"), 0.4, None)], tail=0.15)
    e.say(E16, [(85.6, 87.8), (88.5, 92.2)],
          subs=[(85.6, 87.8, "Aveva già una casa qui vicino."),
                (88.5, 92.2, "Fa parte della nostra congregazione, non potevamo andare lontano.")], **I)
    vo(6, [(B("0012"), 0.4, None)], tail=0.15)
    e.say(E16, [(55.55, 60.2)], subs=[(55.55, 60.2, "Negli ultimi anni ero in Italia, lavoravo con gli anziani.")], **I)
    vo(7, [(C("0004"), 0.6, 2.6), (C("0022"), 0.8, None)])
    e.say(E16, [(108.75, 111.3), (117.2, 122.0), (122.0, 125.05), (125.05, 130.0)], cover={2: (C("0025"), 0.0)},
          subs=[(108.75, 111.3, "Arrivano tramite il tribunale."),
                (117.2, 122.0, "Quando i genitori hanno delle difficoltà, portano i bambini davanti al tribunale"),
                (122.0, 125.05, "e spiegano le ragioni."),
                (125.05, 130.0, "Così il tribunale manda i bambini qui, perché ce ne prendiamo cura.")], **I)
    vo(8, [(C("0029"), 10.5, 4.0), (C("0020"), 0.6, 4.0), (C("0026"), 2.0, None)])

    # 3. LA GIORNATA
    t_g = e.t
    tv9, d9 = vo(9, [(C("0006"), 0.3, 2.6), (C("0007"), 0.4, 2.4), (C("0008"), 0.2, None)])
    music(tl, "giornata", t_g - 0.3, e.t + 0.1, fin=1.0, fout=0.6)
    off_g = e.t - t_g + 0.2
    e.say(E18, [(14.1, 17.65), (21.75, 28.3), (29.3, 32.2), (32.8, 35.55), (36.6, 40.6), (41.3, 43.4), (45.9, 49.0),
                (50.2, 55.15)],
          cover={4: (C("0007"), 0.3), 5: (C("0020"), 2.0), 6: (C("0009"), 0.3), 7: (C("0004"), 1.4)},
          subs=[(14.1, 17.65, "I bambini cominciano la scuola alle sette e mezza."),
                (21.75, 25.4, "Si lavano e fanno colazione, ognuno per conto suo:"),
                (25.4, 28.3, "non possiamo tenerli tutti insieme a colazione."),
                (29.3, 32.2, "Poi escono, perché studiano in scuole diverse,"),
                (32.8, 35.55, "e ognuno esce a un'ora diversa."),
                (36.6, 40.6, "Poi alcuni tornano per il pranzo,"),
                (41.3, 43.4, "altri restano a scuola fino a sera."),
                (45.9, 49.0, "Alle sette cenano."),
                (50.2, 55.15, "Poi un po' di studio e di gioco, e poi a dormire.")], **I)
    t10 = e.t
    vo(10, [(C("0015"), 6.0, 3.0), (B("0010"), 0.5, 3.4), (C("0020"), 8.0, None)], tail=0.2)
    music(tl, "giornata", t10 - 0.3, e.t + 0.4, offset=off_g, fin=0.8, fout=0.6)
    e.say(C("0030"), [(8.5, 11.2)], exact=True, pad=(0.0, 0.0))        # Manuel sullo scivolo: "bambino per un giorno"
    e.say(E19, [(7.35, 9.6), (10.45, 11.2), (11.55, 12.6), (32.6, 36.95)],
          subs=[(7.35, 9.6, "Lavoro qui come coordinatrice dei progetti."), (10.45, 11.2, "Quanti anni hai?"),
                (11.55, 12.6, "Ventinove."), (32.6, 36.95, "Faccio l'assistente sociale da cinque anni.")], **I)
    t_like = e.t
    vo(11, [(C("0005"), 1.0, 2.2), (C("0004"), 3.0, 2.4), (C("0029"), 9.0, None)])
    vo(12, [(B("0014"), 0.3, None)], tail=0.15)
    e.say(E16, [(191.2, 196.3), (201.0, 203.2), (204.05, 208.0)],
          subs=[(191.2, 196.3, "Non possiamo mostrare i bambini. Non possiamo fare tante cose."),
                (201.0, 203.2, "Non possiamo prendere decisioni da sole."),
                (204.05, 208.0, "Se abbiamo una proposta, dobbiamo portarla davanti al governo.")], **I)
    vo(13, [(B("0013"), 1.5, None)], tail=0.15)
    e.say(E16, [(246.4, 250.45), (251.5, 254.35), (272.0, 278.1)],
          subs=[(246.4, 250.45, "Vogliamo aiutare i bambini a costruirsi un buon futuro."),
                (251.5, 254.35, "Diciamo, amore e affetto per i bambini."),
                (272.0, 278.1, "Così, naturalmente, vogliamo bene ai bambini, e siamo felici anche noi.")], **I)
    e.say(E18, [(66.3, 67.5), (79.85, 81.9)],
          subs=[(66.3, 67.5, "Cosa ti piace di questo posto?"), (79.85, 81.9, "Sono felice di lavorare qui.")], **I)
    e.cam(CAMR[14])

    # 4. RAKSHA
    t_r = e.t
    vo(15, [(C("0042"), 0.0, 3.0), (C("0034"), 0.0, 2.1), (C("0037"), 0.2, 2.0), (C("0037"), 3.0, None)])
    music(tl, "raksha", t_r - 0.3, e.t + 0.2, fin=1.0, fout=0.6)
    e.say(E35, [(22.7, 27.3), (28.0, 29.3), (29.8, 32.9), (46.2, 49.9), (50.8, 53.8), (54.5, 59.0), (120.1, 125.9)],
          cover={4: (C("0032"), 0.0)},
          subs=[(22.7, 27.3, "Il nome è Raksha Society, per la cura dei bambini con bisogni speciali."),
                (28.0, 29.3, "Raksha cosa vuol dire?"), (29.8, 32.9, "Raksha vuol dire... salvatore."),
                (46.2, 49.9, "È un'organizzazione che lavora con le persone con disabilità."),
                (50.8, 53.8, "Prepariamo ogni singola persona"),
                (54.5, 59.0, "a diventare indipendente, economicamente e nella vita di tutti i giorni."),
                (120.1, 125.9, "Vengono di giorno: dopo le lezioni tornano a casa, e ogni giorno tornano a scuola.")], **I)
    t16 = e.t
    vo(16, [(C("0037"), 11.0, 3.2), (C("0033"), 0.0, 3.2), (C("0037"), 17.0, None)])
    music(tl, "raksha", t16 - 0.3, e.t + 0.2, offset=12.0, fin=0.8, fout=0.8)
    e.cam(CAMR[17])
    t18 = e.t
    vo(18, [(ROT, 9.3, 2.3), (C("0037"), 7.2, 2.7), (C("0038"), 0.2, None)])
    t_fam = e.t
    e.cam(CAMR[19])
    e.say(E35, [(90.6, 94.45), (94.6, 98.6), (99.2, 101.2), (104.4, 108.1)],
          subs=[(90.6, 94.45, "Appena c'è una diagnosi, che abbiano sei mesi o un anno,"),
                (94.6, 98.6, "quando i medici vedono che un bambino è a rischio,"),
                (99.2, 101.2, "li mandano in posti come il nostro."),
                (104.4, 108.1, "Abbiamo bambini fin dai tre mesi di età.")], **I)
    e.say(E35, [(166.1, 170.75), (171.6, 179.3), (179.8, 182.75)], 
          subs=[(166.1, 170.75, "Di solito un figlio che nasce è un sogno per i genitori."),
                (171.6, 175.9, "Quando ai bambini viene diagnosticata una disabilità,"),
                (175.9, 179.3, "i sogni dei genitori vanno in pezzi."),
                (179.8, 182.75, "All'inizio si sentono impotenti.")], **I)
    e.say(E35, [(189.1, 191.95), (195.2, 196.4), (198.0, 203.65), (203.65, 209.6), (210.2, 214.05), (225.7, 231.6)],
          cover={3: (C("0037"), 13.0)},
          subs=[(189.1, 191.95, "Molti all'inizio vengono qui solo per la fisioterapia."), (195.2, 196.4, "Ma poi,"),
                (198.0, 203.65, "con la nostra valutazione, i genitori capiscono che il bambino potrebbe"),
                (203.65, 209.6, "avere difficoltà a scuola e in altro, anche nel parlare e nel linguaggio."),
                (210.2, 214.05, "Allora li seguiamo, li guidiamo come si deve."),
                (225.7, 228.55, "Seguiamo non solo i genitori,"),
                (228.55, 231.6, "anche i fratelli e le sorelle: seguiamo tutta la famiglia.")], **I)
    t_lav = e.t
    e.cam(CAMR[20])
    e.say(E35, [(275.7, 279.95), (280.3, 284.45), (285.1, 287.45), (288.0, 295.1), (295.3, 298.2)],
          subs=[(275.7, 279.95, "Perché oggi, se vuoi trovare un lavoro,"),
                (280.3, 284.45, "prendono la persona più adatta per quel lavoro."),
                (285.1, 287.45, "Ai nostri ragazzi manca qualcosa."),
                (288.0, 295.1, "Anche con la riabilitazione e le terapie, nella vita trovano delle difficoltà."),
                (295.3, 298.2, "A un certo punto hanno bisogno di qualcuno che li guidi.")], **I)
    vo(21, [(C("0041"), 0.0, None)], tail=0.15)
    e.say(E35, [(268.7, 272.75), (272.9, 275.35), (298.6, 302.45), (302.9, 309.6), (310.3, 313.6), (313.7, 314.5)],
          subs=[(268.7, 272.75, "Quando entrano nella società, nella comunità,"),
                (272.9, 275.35, "devono essere accettati come sono."),
                (298.6, 302.45, "Tutti quei limiti devono essere accettati dalla comunità."),
                (302.9, 309.6, "E le barriere, soprattutto quelle fisiche ed emotive, nella società vanno tolte."),
                (310.3, 313.6, "È importante che nella società ci siano persone come te."),
                (313.7, 314.5, "Grazie mille.")], **I)

    # 5. CHIUSURA
    t_fine = e.t
    e.cam(CAMR[22])
    t23 = e.t
    vo(23, [(C("0056"), 1.0, 1.3), (C("0055"), 0.0, 1.2), (C("0048"), 1.0, 1.3), (C("0045"), 1.5, 2.2),
            (C("0026"), 0.0, 2.4), (C("0015"), 9.0, 2.0), (C("0028"), 0.3, None)], lead=0.3, tail=0.5)
    vo(24, [(C("0042"), 0.0, 3.0), (C("0029"), 10.0, None)], lead=0.2, tail=0.4)
    # frase di chiusura dalla registrazione pulita (regola 9/11), immagini senza volti, scritta finale
    f_ch, d_ch = piece("chiusura", [(CHIUSURA, [(0.88, 6.80)])])
    lead, after = 0.3, 2.6
    t_c0 = e.t
    tl.vos.append(dict(file=f_ch, a=0, b=d_ch, speed=1.0, t=t_c0 + lead, raw=True))
    dur = lead + d_ch + after
    items = [(C("0045"), 0.5), (C("0022"), 2.0), (C("0021"), 1.0), (C("0029"), 12.0)]
    tl._add(closing_visual(W, H, items, dur, lead, dur - lead), 0, dur, audio=False, grade="null")
    music(tl, "finale", t23 - 0.4, e.t, fin=1.5, fout=1.0)
    sigla_d(tl, OUT, clips=SIGLA_CLIPS, tag="fortkochi")

    chapters = [(0.0, "Come gli altri bambini", "Like the other children"),
                (t_dopo_sigla, "Due posti a Kochi", "Two places in Kochi"),
                (t_ash, "Ashwasa Bhavan", "Ashwasa Bhavan"),
                (t_g, "La giornata", "The day"),
                (t_r, "Raksha", "Raksha"),
                (t_fam, "Le famiglie", "The families"),
                (t_lav, "Il lavoro, fuori", "Work, outside"),
                (t_fine, "Quello che diamo per scontato", "What we take for granted")]
    out = f"{OUT}/VociVere_fortkochi_long_{W}x{H}.mp4"
    json.dump(dict(chapters=chapters, t_sigla=t_sigla, t_dopo_sigla=t_dopo_sigla, t_like=t_like, t16=t16, t18=t18, t23=t23,
                   total=e.t), open(f"{OUT}/long_{W}x{H}.json", "w"), indent=1)
    e.render(out)
    return out


if __name__ == "__main__":
    what = [a for a in sys.argv[1:] if not a.startswith("--")] or ["long"]
    W, H = (1920, 1080) if PREVIEW else (3840, 2160)
    for w in what:
        if w == "long":
            long_video(W, H)
