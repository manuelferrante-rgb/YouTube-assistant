#!/usr/bin/env python3
"""Coir, le donne del coir di Anathalavattom (Chirayinkeezhu, Kerala), girato il 6/11.

    python3 projects/coir/build.py long|teaser|madeinindia|indietro|premilla|1975 [--preview]
Girato e voiceover in work/coir/raw (cartella Drive "Coir" 19zCOBK_aJ6a4SFwGffbZvDKUr-IXR8UA, rclone).
Script e testi di Copy in copioni/coir_testi.md ("SCRIPT FINALE v4" e "PER MONTAGGIO" dei verticali), musica della chat
Audio in projects/coir/audio/ (LEGGIMI), girato e scelte in projects/coir/girato.md.
Stesso motore del tè (projects/te/build.py): tagli sulla voce vera, voce pulita con RNNoise, B-roll muti.
Nuovo qui (Manuel 6/11): ogni clip parlata ha la voce portata allo stesso livello e sotto un filo del suo fondo, sempre
allo stesso livello basso (leveled()), così tra una clip e l'altra non cambia né la voce né il fondo.
"""
import glob, json, os, subprocess, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, dur_of, ts, AFFTDN_FIX
from sigla import sigla_d
from voice_clean import cleaned
from reel_kit import Reel
import reel_close as RC

PREVIEW = "--preview" in sys.argv
WORK = f"{ROOT}/work/coir"
R = f"{WORK}/raw"
OUT = f"{WORK}/out"
VOCE = f"{WORK}/voce"
AUD = f"{ROOT}/projects/coir/audio"
VO = f"{R}/voiceoverlungo.m4a"
VOV = f"{R}/voiceoververticali.m4a"
os.makedirs(OUT, exist_ok=True)
DEF = "eq=contrast=1.03:saturation=1.05"
MUS = 0.11                     # musica sotto il VO: ~25 dB sotto la voce (LEGGIMI di Audio)


def C(k):
    """Clip DJI per le ultime 4 cifre (es. "0540" = DJI_20261106082853_0540_D.MP4)."""
    m = glob.glob(f"{R}/DJI_20261106*_{k}_D.MP4")
    assert len(m) == 1, (k, m)
    return m[0]


WORDS = json.load(open(f"{WORK}/words.json")) if os.path.exists(f"{WORK}/words.json") else {}


def words_of(src):
    return WORDS.get(os.path.basename(src), [])


# ---------------- voce allo stesso livello, fondo uguale e basso (Manuel 6/11) ----------------
VOICE_LUFS = -18.0
FLOOR_DB = -56.0               # fondo nelle pause, uguale per tutte le clip


def _pcm(path, af="anull", ch=1):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", str(ch), "-ar", "48000",
                                         "-af", af, "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)


def _lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(json.loads(out.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def leveled(src):
    """Voce pulita (RNNoise) a -18 LUFS con guadagno fisso, più il fondo della clip tenuto costante a -56 dB.
    Il fondo è il suono originale meno la voce pulita (sottrazione a blocchi di 0.5 s), portato con un guadagno lento
    (finestre di 0.4 s) sempre allo stesso livello basso: un tuk-tuk che passa non sale, una clip silenziosa non viene
    alzata oltre la voce (guadagno del fondo <= guadagno della voce - 8 dB). Stessi tempi della clip (labiale invariato)."""
    out = f"{VOCE}/liv4_{os.path.splitext(os.path.basename(src))[0]}.wav"
    if os.path.exists(out):
        return out
    cv = cleaned(src, VOCE)
    gv = VOICE_LUFS - _lufs(cv)
    x = _pcm(src, "highpass=f=100,highpass=f=100").astype(np.float64)
    c = _pcm(cv).astype(np.float64)
    n = min(len(x), len(c)); x, c = x[:n], c[:n]
    res = np.copy(x)
    B = 24000
    for i in range(0, n, B):
        xc, cc = x[i:i + B], c[i:i + B]
        k = float(xc @ cc) / (float(cc @ cc) + 1e-9)
        res[i:i + B] = xc - k * cc
    h = 4800                                                     # 0.1 s
    m = n // h
    lev = 10 * np.log10((res[:m * h].reshape(m, h) ** 2).mean(1) + 1e-12)
    lev = np.convolve(lev, np.ones(4) / 4, mode="same")          # 0.4 s
    g = np.minimum(FLOOR_DB - lev, gv - 8)
    g = np.interp(np.arange(n), (np.arange(m) + 0.5) * h, g)
    # nelle pause RNNoise lascia un residuo che cambia da clip a clip: porta (gate dolce, -25 dB) fuori dalle parole,
    # con 60 ms prima e 200 ms dopo ogni tratto di voce, così le parole non perdono attacco né coda
    hv = 480
    mv = n // hv
    dv = 20 * np.log10(np.sqrt((c[:mv * hv].reshape(mv, hv) ** 2).mean(1)) + 1e-9)
    dv = np.convolve(dv, np.ones(5) / 5, mode="same")
    lo, hi = np.percentile(dv, 10), np.percentile(dv, 95)
    on = dv > lo + 0.2 * (hi - lo)          # basso: anche chi parla lontano (interprete, le donne) passa
    on = np.convolve(on.astype(float), np.ones(27), mode="full")[6:6 + mv] > 0      # -60 ms / +200 ms
    gate = np.where(on, 1.0, 10 ** (-25 / 20))
    gate = np.convolve(gate, np.ones(3) / 3, mode="same")
    gate = np.interp(np.arange(n), (np.arange(mv) + 0.5) * hv, gate)
    y = c * gate * 10 ** (gv / 20) + res * 10 ** (g / 20)
    y = np.clip(y, -0.98, 0.98).astype(np.float32)
    import soundfile as sf
    sf.write(out, np.stack([y, y], 1), 48000, subtype="PCM_16")
    print(f"livello {os.path.basename(src)}: voce {gv:+.1f} dB, fondo {np.median(lev):.0f} -> {FLOOR_DB:.0f} dB", flush=True)
    return out


def range_gain(src, a, b, target=-23.0):
    """dB da aggiungere perché la voce in [a, b] (clip livellata) arrivi al livello delle altre: chi risponde lontano
    dal microfono (le donne, l'interprete) si sente come Manuel (Manuel 6/11). Mediana dei 50 ms con voce."""
    x = _pcm(leveled(src))[int(a * 48000):int(b * 48000)]
    h = 2400
    db = 20 * np.log10(np.sqrt((x[:len(x) // h * h].reshape(-1, h) ** 2).mean(1)) + 1e-9)
    v = db[db > max(db.max() - 20, -50)]
    return float(np.clip(target - np.median(v), 0.0, 14.0)) if len(v) else 0.0


class TL(Timeline):
    """Le clip parlate arrivano già livellate (leveled): niente loudnorm dinamico per inquadratura, che alzava il fondo."""

    def _af(self, s):
        if not (s["norm"] and s["src"] in self.audio_map):
            return super()._af(s)
        d = s["d"]
        f = [f"atempo={s['speed']}"] if s["speed"] != 1.0 else []
        f += ["aresample=48000", f"volume={s['gain']}"]
        fd = min(s["fade"], d / 3)
        f.append(f"apad,atrim=end={d:.4f},afade=t=in:d={fd:.3f},afade=t=out:st={d - fd:.4f}:d={fd:.3f}")
        return ",".join(f)


# ---------------- tagli sulla voce vera (da projects/te/build.py) ----------------
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


def piece(name, src, ranges, speed=1.0, gap=0.2, pad=(0.06, 0.1)):
    """Voce da più tratti (misurati sulla voce pulita) uniti con respiri di gap s e accelerata -> (file, durata)."""
    D = dur_of(src)
    ranges = [(max(0, a - pad[0]), min(D, b + pad[1])) for a, b in ranges]
    out = f"{OUT}/{name}_{abs(hash((tuple(ranges), speed, gap))) % 10**8}.wav"
    if not os.path.exists(out):
        fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={speed},aresample=48000,"
                     f"afade=t=in:d=0.03,afade=t=out:st={(b - a) / speed - 0.05:.3f}:d=0.05,apad=pad_dur={gap}[p{i}];"
                     for i, (a, b) in enumerate(ranges))
        tot = sum((b - a) / speed + gap for a, b in ranges) - gap
        fc += "".join(f"[p{i}]" for i in range(len(ranges))) + f"concat=n={len(ranges)}:v=0:a=1,atrim=end={tot:.3f}[o]"
        tmp = out.replace(".wav", "_tmp.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", cleaned(src, VOCE), "-filter_complex", fc, "-map", "[o]", "-ac", "1",
             "-ar", "48000", tmp])
        run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={VOICE_LUFS - _lufs(tmp):.2f}dB", "-ac", "1",
             "-ar", "48000", out])                                  # stesso livello delle clip parlate, guadagno fisso
        os.remove(tmp)
    return out, dur_of(out)


# ---------------- il lungo ----------------
class Edit:
    def __init__(self, W, H, tag):
        self.tl = TL(W, H, f"{OUT}/{tag}_work")
        self.W, self.H, self.k = W, H, H / 1080
        self.labels, self.cards = [], []

    @property
    def t(self):
        return self.tl.t

    def b(self, src, a, d, cx=0.5, speed=1.0, zoom=1.0, zy=0.4, gain=0.0):
        """B-roll muto (gain 0): sotto solo voce, voiceover o musica di Audio. zoom/zy: ingrandimento fisso lieve
        con il taglio spostato in alto (zy=1: si toglie solo la parte alta, es. la mano di Manuel in 0088)."""
        self.tl.broll(src, a, d, gain=gain, cx=cx, grade=DEF, zoom=zoom,
                      fx=None if zoom != 1.0 else dict(zoom=(1.0, 1.04, None)), speed=speed, fade=0.12)
        if zoom != 1.0:
            self.tl.shots[-1]["zy"] = zy

    def say(self, src, ranges, speed=1.0, cover=None, subs=(), cut_gaps=True, pad=(0.06, 0.12), exact=False, lift=False):
        """Parlato con la voce livellata; cover = {indice: (clip, inizio)} copre quel tratto con un'altra immagine
        mentre la voce continua. subs (inizio, fine, testo) in tempi della sorgente."""
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
                self.tl._add(src2, a2, (b - a) / speed, gain=0.0, grade=DEF, fade=0.05, fx=dict(zoom=(1.0, 1.04, None)))
                self.tl.vos.append(dict(file=src, a=a, b=b, speed=speed, t=t0, lev=True, raw=True, af=f"volume={g:.3f}"))
            else:
                self.tl.speech(src, [(a, b)], speed=speed, grade=DEF, gain=g)
            for sa, sb, txt in subs:
                lo, hi = max(sa, a), min(sb, b)
                if hi - lo > 0.15:
                    self.tl.subs.append((t0 + (lo - a) / speed, t0 + (hi - a) / speed, txt))

    def vo(self, name, ranges, items, lead=0.15, tail=0.25, speed=1.0, src=None, db=0.0):
        """Voiceover di Manuel sopra immagini mute: items = [(clip, inizio, durata o None[, opzioni di b()])].
        db: voce un filo più alta nei punti chiave (Manuel 7/11). -> (t voce, durata)."""
        f, d = piece(f"vo_{name}", src or VO, ranges, speed=speed)
        t0 = self.t
        self.tl.vos.append(dict(file=f, a=0, b=d, speed=1.0, t=t0 + lead, raw=True,
                                **({"af": f"volume={db}dB"} if db else {})))
        total = lead + d + tail
        fixed = sum(x[2] for x in items if x[2])
        rest = max(0.8, total - fixed) / max(1, sum(1 for x in items if not x[2]))
        for it in items:
            self.b(it[0], it[1], it[2] or rest, **(it[3] if len(it) > 3 else {}))
        return t0 + lead, d

    def label(self, text, t0, d=2.8):
        self.labels.append((t0, t0 + d, text))

    def card(self, text, t0, t1):
        self.cards.append((t0, t1, text))

    def ass(self):
        k, W, H = self.k, self.W, self.H
        S = lambda v: int(round(v * k))
        sub = self.tl.sub_size
        head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Sub,Poppins Medium,{sub},&H0098D8F2,&H0098D8F2,&H00000000,&H90000000,0,0,0,0,100,100,"
                f"0.5,0,1,{sub / 32:.1f},{sub / 36:.1f},2,{int(W * 0.08)},{int(W * 0.08)},{self.tl.sub_margin},1\n"
                f"Style: Lab,Playfair Display,{S(46)},&H00F2F2F2,&H00FFFFFF,&H00000000,&H80000000,0,-1,0,0,100,100,0.5,0,1,"
                f"{S(1.2)},{S(2.2)},1,{S(70)},{S(70)},{S(64)},1\n"
                f"Style: Fin,Playfair Display,{S(62)},&H00F4F4F4,&H00FFFFFF,&H00000000,&H90000000,0,-1,0,0,100,100,0.5,0,1,"
                f"{S(1.4)},{S(3)},5,{S(120)},{S(120)},0,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        ev = [(0, a, b, "Sub", t) for a, b, t in self.tl.subs]
        ev += [(1, a, b, "Lab", "{\\fad(350,350)}" + t) for a, b, t in self.labels]
        ev += [(2, a, b, "Fin", f"{{\\an5\\pos({W // 2},{H // 2})\\fad(700,600)}}" + t) for a, b, t in self.cards]
        p = f"{self.tl.dir}/scritte.ass"
        with open(p, "w") as f:
            f.write(head)
            for layer, a, b, st, txt in sorted(ev, key=lambda e: e[1]):
                f.write(f"Dialogue: {layer},{ts(a)},{ts(b)},{st},,0,0,0,,{txt}\n")
        return p

    def render(self, out):
        self.tl.fix_freezes()
        for prev, sh in zip(self.tl.shots, self.tl.shots[1:]):      # dissolvenze brevi solo tra B-roll muti
            if not (prev["norm"] or sh["norm"] or "sigla" in sh["src"] or "sigla" in prev["src"]) and sh["d"] > 0.6 \
                    and prev["d"] > 0.3 and sh["src"] != prev["src"] and sh["src"].startswith(R) and prev["src"].startswith(R):
                sh["xin"] = 0.25
        self.tl.ass_override = self.ass()
        # le voci delle clip sotto altre immagini (cover) usano la stessa voce livellata
        for v in self.tl.vos:
            if v.get("lev"):
                v["file"] = self.tl.audio_map[v["file"]]
        self.tl.nat_af = "highpass=f=90"
        print(f"== {os.path.basename(out)}: {len(self.tl.shots)} inquadrature, {self.t:.1f} s", flush=True)
        if PREVIEW:
            return self.tl.render(out, crf=26, preset="veryfast")
        self.tl.drop_shots = True
        self.tl.direct_concat = True                                 # 4K: niente cut.mkv da 11 GB (disco)
        self.tl.shot_crf = 17                                         # inquadrature intermedie più leggere (disco)
        self.tl.final_opts = ["-maxrate", "38M", "-bufsize", "76M"]
        return self.tl.render(out, crf=20, preset="medium")


def music(tl, name, t0, t1, offset=0.0, level=MUS, fin=1.0, fout=1.0):
    tl.music(t0, t1, f"{AUD}/{name}.flac", offset=offset, level=level, fin=fin, fout=fout, duck=False, norm=False)
    return offset + (t1 - t0)


SIGLA_CLIPS = [(C("0544"), 1.6), (C("0540"), 2.0), (C("0021"), 1.0), (C("0069"), 0.3), (C("0089"), 2.0), (C("0087"), 0.5)]
VO2 = f"{R}/vo_v2.m4a"          # VO13-VO18 (Drive: "Ayanikuzhivila-Arathantevila Road.m4a", 7/11)

# voiceover del lungo (voiceoverlungo.m4a e vo_v2.m4a): frasi misurate sulla voce pulita, sempre l'ultima presa ("ripeto")
V = {0: [(4.41, 5.99), (6.41, 8.83)],
     1: [(9.36, 11.22), (11.52, 14.03), (14.41, 15.33), (15.86, 18.44)],
     2: [(19.87, 23.09)], 3: [(23.94, 26.84)],
     4: [(31.07, 34.60), (35.04, 37.66)],
     5: [(40.40, 41.95), (42.33, 45.64), (46.00, 47.41)],
     6: [(51.02, 52.95), (55.12, 58.05)],                    # v2: via "Questa barca ne ha cinquanta" (lo dice 0024)
     7: [(61.32, 62.76), (63.01, 65.11), (65.42, 67.52)],
     8: [(72.72, 74.65)], 9: [(75.57, 79.45)],
     10: [(80.36, 82.59), (82.89, 84.13), (84.57, 86.45)],
     11: [(99.54, 103.69), (103.98, 105.31)], "11b": [(106.45, 107.62)],
     12: [(124.52, 127.01), (127.27, 128.83), (129.15, 130.63), (130.94, 133.43), (133.86, 135.98), (136.26, 138.72)]}
V2 = {13: [(1.69, 5.67), (6.01, 6.83)], 14: [(8.21, 12.82)], 15: [(26.40, 30.85)],
      16: [(31.25, 33.32), (37.18, 39.28)], 17: [(45.81, 47.83), (48.14, 50.99)], 18: [(53.23, 53.84), (54.21, 57.58)]}
I = dict(speed=1.0, cut_gaps=False, lift=True, exact=True)   # interviste: velocità normale, tagli esatti sulle risposte
KEY = dict(speed=0.9, db=2.0)                                 # frasi chiave (Manuel 7/11): 0.9x e voce un filo più alta


def soft_clean(src, a, b):
    """Voce della chiusura 0102 (Manuel 7/11: fondo troppo alto e voce sgranata): passa-alto, riduzione spettrale leggera,
    poi RNNoise mescolato al 85% (meno artefatti del 100%), gate dolce nelle pause e -18 LUFS. Stessi tempi della clip."""
    out = f"{VOCE}/chiusura_{os.path.splitext(os.path.basename(src))[0]}_{a:.2f}_{b:.2f}.wav"
    if os.path.exists(out):
        return out
    from voice_clean import RNN
    cleaned(src, VOCE)                                          # scarica il modello RNNoise se manca
    tmp = out.replace(".wav", "_t.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:a:0", "-ar", "48000", "-af",
         f"aformat=channel_layouts=mono,volume=0.5,highpass=f=110,highpass=f=110,afftdn=nf=-28:nr=14,{AFFTDN_FIX},"
         f"arnndn=m={RNN}:mix=0.85,atrim=start_sample=480,asetpts=PTS-STARTPTS,lowpass=f=11000",
         "-c:a", "pcm_s16le", tmp])
    c = _pcm(tmp).astype(np.float64)
    seg = c[int(a * 48000):int(b * 48000)]
    hv = 480
    m = len(c) // hv
    dv = 20 * np.log10(np.sqrt((c[:m * hv].reshape(m, hv) ** 2).mean(1)) + 1e-9)
    dv = np.convolve(dv, np.ones(5) / 5, mode="same")
    ref = dv[int(a * 100):int(b * 100)]
    lo, hi = np.percentile(ref, 10), np.percentile(ref, 95)
    on = np.convolve((dv > lo + 0.3 * (hi - lo)).astype(float), np.ones(27), mode="full")[6:6 + m] > 0
    gate = np.convolve(np.where(on, 1.0, 10 ** (-30 / 20)), np.ones(3) / 3, mode="same")
    y = c[:m * hv] * np.interp(np.arange(m * hv), (np.arange(m) + 0.5) * hv, gate)
    import soundfile as sf
    sf.write(tmp, np.stack([y, y], 1).astype(np.float32), 48000, subtype="PCM_16")
    seg_l = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(a), "-t", str(b - a), "-i", tmp, "-af",
                            "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    g = VOICE_LUFS - float(json.loads(seg_l.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={g:.2f}dB,alimiter=limit=0.95:level=false",
         "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", out])
    os.remove(tmp)
    return out


def closing_visual(W, H, items, dur, card_at, card_dur):
    """Immagini della chiusura (le donne sedute, l'uomo nella laguna, la fabbrica, la laguna) montate in una clip sola,
    con la scritta finale animata (tools/scritta_finale.py, font D, riquadro con la luce a cometa) da card_at s."""
    tag = "_".join(f"{os.path.basename(c)[24:28]}{a:.1f}" for c, a in items)
    out = f"{OUT}/chiusura_{tag}_{dur:.2f}_{card_at:.2f}_{W}x{H}.mp4"
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


def long_video(W, H):
    """Lungo v2 (7/11): tutto a 1x, VO13-VO18, tre momenti di sole immagini e musica, il parlato di Manuel ripreso
    (copioni/coir_testi.md, "LUNGO v2") e le correzioni di Manuel del 7/11."""
    e = Edit(W, H, "long")
    tl = e.tl
    vo = lambda n, items, **kw: e.vo(str(n), V[n], items, **kw)
    vo2 = lambda n, items, **kw: e.vo(f"v2_{n}", V2[n], items, src=VO2, **kw)

    def quiet(items, track, offset, level=0.28, nat=0.0):
        """Momento di sole immagini e musica (niente voce né scritte): items = [(clip, inizio, durata)]."""
        t0 = e.t
        for c, a, d in items:
            e.b(c, a, d, gain=nat)
        music(tl, track, t0 - 0.3, e.t + 0.2, offset=offset, level=level, fin=0.8, fout=1.2)
        return t0

    # 0. INTRO: parte subito parlata. La voce di 0034 va già sopra l'uomo nella laguna; finita la sua clip entra
    # l'immagine di Manuel in barca (Manuel 7/11)
    e.say(C("0034"), [(0.1, 2.5), (2.5, 4.1)], cover={0: (C("0544"), 1.6)}, exact=True, pad=(0.0, 0.1))
    e.say(C("0038"), [(0.0, 3.5)])                                    # "Il cocco da cui viene estratta la fibra viene da qua."
    t_mi = e.t
    vo(0, [(C("0063"), 4.0, 2.6), (C("0069"), 0.0, None)], lead=0.1, tail=0.2)
    music(tl, "coir_intro", t_mi - 0.4, e.t + 0.3, fin=0.4, fout=0.4)    # sfuma sull'attacco della sigla
    sigla_d(tl, OUT, clips=SIGLA_CLIPS, tag="coir")

    # 1. DOVE SIAMO, LE DONNE CHE NON LO FANNO PIÙ
    t_1 = e.t
    e.say(C("0039"), [(0.0, 1.9)])                                  # "Mi trovo nel sud dell'India,"
    e.say(C("0040"), [(0.0, 2.3)])                                    # "ad Anathalavattom, in Kerala."
    t_v1 = e.t
    vo(1, [(C("0525"), 0.3, 4.6), (C("0529"), 0.3, None)], lead=0.15)
    off = music(tl, "coir_strada", t_v1 - 0.2, e.t + 0.2, fin=0.3, fout=0.8)
    e.say(C("0526"), [(5.17, 12.25), (13.25, 15.35)], exact=True)     # prima c'è la domanda in inglese: niente snap
    e.say(C("0527"), [(18.1, 18.8), (19.9, 21.05)], subs=[(18.0, 21.1, "1975.")], **I)
    e.say(C("0532"), [(0.0, 5.75)])                                   # "Più rimango qua, più arrivano altre donne..."
    t_2 = e.t
    vo(2, [(C("0527"), 29.5, 3.6)], lead=0.15, tail=0.1)
    vo(3, [(C("0529"), 5.5, 2.2), (C("0121"), 2.0, None)], lead=0.1, tail=0.3)
    music(tl, "coir_strada", t_2 - 0.3, e.t, offset=off, fin=0.8, fout=1.0)

    # 2. LA SOCIETÀ: subito il posto e le persone che aprono il cocco, Manuel in camera un attimo, di nuovo loro
    t_s = e.t
    e.say(C("0536"), [(0.0, 5.3)], cover={0: (C("0537"), 18.5)})     # "Forse abbiamo trovato... una società" sul posto
    e.say(C("0538"), [(0.35, 2.2), (2.45, 3.9), (4.25, 5.55), (5.7, 8.6), (9.65, 12.15)],
          cover={0: (C("0061"), 0.3), 1: (C("0109"), 1.0), 3: (C("0063"), 13.0), 4: (C("0540"), 6.0)})
    vo(4, [(C("0527"), 4.0, 3.2), (C("0109"), 3.5, None)])          # 8/11 (Insights): persone al lavoro, non la laguna vuota

    # 3. LA LAGUNA E L'UOMO IN BARCA
    t_l = e.t
    e.say(C("0546"), [(9.4, 11.0), (12.6, 16.75), (17.8, 18.8), (20.6, 23.5), (25.1, 25.7), (27.3, 28.0), (28.6, 30.4)],
          cover={1: (C("0544"), 0.0), 3: (C("0540"), 6.0), 4: (C("0008"), 0.5), 6: (C("0009"), 0.5)})
    quiet([(C("0544"), 4.2, 2.6)], "coir_laguna", 0.0, level=0.22)   # l'uomo nella laguna, solo musica (8/11: via il largo)
    e.say(C("0023"), [(12.95, 17.1), (18.6, 19.95)])                  # "Adesso andiamo a prendere il cocco..."
    t_m = e.t
    vo(5, [(C("0021"), 1.0, 2.2), (C("0107"), 2.0, 2.4), (C("0108"), 9.0, None)], lead=0.3)
    e.say(C("0044"), [(0.0, 2.6)])                                    # la barca affondata si vede nella sua clip (7/11)
    e.b(C("0020"), 1.0, 1.4)
    tv6, d6 = vo(6, [(C("0046"), 0.8, 3.0), (C("0047"), 0.0, None)])
    music(tl, "coir_laguna", t_m - 0.6, e.t + 0.3, offset=max(0.0, 15.0 - (tv6 - (t_m - 0.6))), fin=0.8, fout=1.0)
    e.say(C("0024"), [(0.2, 6.2)])                        # "Questa barca è più anziana della società..."
    t13 = e.t
    vo2(13, [(C("0052"), 0.0, 4.0), (C("0056"), 4.0, 2.4), (C("0057"), 0.0, None)])
    music(tl, "coir_laguna", t13 - 0.4, e.t + 0.3, offset=20.0, fin=0.5, fout=1.0)
    e.say(C("0031"), [(0.0, 4.45), (4.95, 9.4)], cover={1: (C("0058"), 0.5)})
    e.say(C("0045"), [(0.0, 4.0), (5.1, 7.4), (8.7, 12.6)])
    vo2(14, [(C("0097"), 0.0, 2.0), (C("0099"), 0.3, 1.8), (C("0104"), 0.3, None)])
    # "Mi sento privilegiato": prima le persone al lavoro, poi Manuel, poi di nuovo loro (7/11)
    e.say(C("0043"), [(0.0, 1.43), (1.43, 2.5), (2.53, 4.8)], cover={0: (C("0111"), 0.5), 2: (C("0068"), 1.0)}, exact=True,
          pad=(0.02, 0.06))
    e.say(C("0064"), [(5.95, 9.35)], exact=True)                      # "mi prendono in giro, posso andare in Italia..."

    # 4. LE DONNE SOTTO LA TETTOIA (il cuore)
    t_d = e.t
    vo(7, [(C("0540"), 0.5, 2.6), (C("0109"), 1.0, 1.6), (C("0110"), 0.5, 1.6), (C("0111"), 0.5, None)], lead=0.3, tail=0.1)
    vo2(15, [(C("0540"), 6.0, None)], lead=0.05)
    e.say(C("0542"), [(4.4, 7.65), (9.35, 10.45)],
          subs=[(4.4, 7.65, "Da quanti anni fai questo lavoro?"), (9.35, 10.45, "Quarant'anni.")], **I)
    e.say(C("0549"), [(0.0, 1.65), (1.85, 2.5), (5.75, 6.7), (7.05, 8.7), (9.5, 11.3), (11.45, 12.55), (13.35, 15.95)],
          subs=[(0.0, 1.65, "Come ti chiami?"), (1.9, 2.45, "Premilla."), (5.75, 6.7, "Quanti anni hai?"),
                (7.05, 8.7, "Sessanta."), (9.5, 11.3, "E da quanti anni fai questo lavoro?"),
                (11.45, 12.55, "Quarant'anni."), (13.35, 15.95, "La società ha aperto quarant'anni fa.")], **I)
    vo(8, [(C("0010"), 0.3, None)], lead=0.1, tail=0.2)
    e.say(C("0001"), [(4.6, 14.4)])                                   # "loro sono le prime, le uniche donne... tutti i giorni"
    e.say(C("0543"), [(5.05, 6.85), (8.85, 12.15)], cover={1: (C("0063"), 13.0)})
    e.say(C("0015"), [(0.0, 3.95)])                                   # "È difficile comunicare... l'interprete"
    t_sal = e.t
    e.say(C("0002"), [(0.0, 1.6), (35.7, 36.85)], cover={0: (C("0106"), 0.5), 1: (C("0109"), 3.0)},
          subs=[(0.0, 1.6, "Quanto è il salario?"), (35.7, 36.85, "Quattrocento rupie al giorno.")], **I)
    e.say(C("0003"), [(0.55, 2.1), (2.3, 5.65)], cover={0: (C("0016"), 0.0), 1: (C("0063"), 0.5)},
          subs=[(0.55, 5.65, "Con un salario così basso, i giovani non vengono.")], **I)
    e.say(C("0006"), [(0.0, 4.9), (6.2, 9.6), (10.2, 13.3), (14.4, 19.0), (19.4, 21.95), (22.4, 24.7), (25.1, 28.5),
                      (29.1, 30.2), (30.8, 35.2)],
          cover={2: (C("0111"), 1.0), 3: (C("0110"), 0.5), 5: (C("0106"), 3.0), 6: (C("0063"), 0.8)})
    quiet([(C("0549"), 0.3, 5.0)], "coir_strada", 12.0)              # dopo il salario: Premilla in primo piano (8/11)

    # 5. LE MACCHINE E LA FABBRICA
    t_f = e.t
    e.say(C("0062"), [(2.4, 8.25)])
    e.say(C("0548"), [(6.2, 9.2), (10.1, 14.65)])                          # "da qui vengono messi a lavorare dentro le macchine..."
    t_9 = e.t
    vo(9, [(C("0017"), 0.0, 2.2), (C("0090"), 0.3, None)], lead=0.4, tail=0.1)
    vo2(16, [(C("0017"), 15.0, 2.4), (C("0105"), 0.2, None)], tail=0.3)
    music(tl, "coir_macchine", t_9 - 0.5, min(e.t, t_9 + 11.5), fin=0.5, fout=1.2)
    # "280 al giorno in 8 ore" fluido: via la parola accennata prima di "in 8 ore" (10.76 s) e le pause (7/11)
    e.say(C("0076"), [(1.3, 9.5), (9.94, 10.52), (10.93, 12.1)], exact=True, pad=(0.03, 0.05))
    vo(10, [(C("0069"), 0.0, 2.2), (C("0072"), 1.0, 2.0), (C("0073"), 0.5, None)], tail=0.1)
    vo2(17, [(C("0066"), 3.0, 1.8), (C("0068"), 1.0, 2.0), (C("0074"), 0.0, None)], lead=0.05, tail=0.1)
    vo2(18, [(C("0085"), 0.0, None)], lead=0.05, tail=0.3)

    # 6. CLIMAX: I NOSTRI TAPPETI
    t_c = e.t
    e.say(C("0091"), [(0.0, 3.95)])
    e.say(C("0092"), [(0.1, 4.85)])
    e.say(C("0547"), [(10.25, 12.8)], cover={0: (C("0099"), 0.5)})
    e.say(C("0547"), [(13.7, 15.0), (19.5, 22.6)], cover={0: (C("0087"), 0.0), 1: (C("0099"), 0.5)},
          subs=[(13.7, 15.0, "Tappeti..."), (19.5, 22.6, "da esportare in Francia, Germania.")], **I)
    vo(11, [(C("0087"), 0.0, 2.6), (C("0063"), 4.0, None)], tail=0.0)
    # "Adesso sapete chi li ha fatti": pausa prima e dopo, 0.9x, voce un filo più alta (7/11)
    e.vo("11b", V["11b"], [(C("0542"), 1.6, None)], lead=0.7, tail=0.7, **KEY)
    quiet([(C("0087"), 0.0, 2.4), (C("0074"), 0.0, 3.0), (C("0068"), 2.0, 2.6)], "coir_laguna", 13.0, nat=0.25)
    e.say(C("0094"), [(0.3, 5.5), (6.0, 8.8)])
    e.b(C("0540"), 3.0, 0.6)                                           # pausa sulle donne prima degli 80 centesimi
    e.say(C("0094"), [(9.6, 12.3)], cover={0: (C("0540"), 3.6)}, exact=True, speed=0.9)
    e.tl.vos[-1]["af"] = "volume=2dB"
    quiet([(C("0542"), 4.0, 2.0), (C("0549"), 8.0, 2.0), (C("0085"), 2.0, 2.0), (C("0529"), 0.0, 2.0),
           (C("0047"), 0.0, 2.0)], "coir_intro", 0.0, level=0.3)       # 10 s sui volti: torna il motivo dell'inizio

    # 7. FINALE: VO12 su volti e laguna, poi la frase di chiusura senza Manuel in video, con la scritta, e la sigla
    t_e = e.t
    e.say(C("0098"), [(0.0, 1.7), (2.4, 3.45)])                       # "Una tradizione centenaria che si sta perdendo."
    e.say(C("0099"), [(0.4, 3.25)], cover={0: (C("0107"), 6.0)})      # "Sono venuto qui in India a documentarla."
    vo(12, [(C("0063"), 4.0, 2.6), (C("0085"), 2.5, 2.4), (C("0549"), 8.0, 2.6), (C("0115"), 0.0, 4.2),
            (C("0089"), 0.0, None)], lead=0.6, tail=0.6)
    # chiusura (7/11): voce di 0102 ripulita, sopra le donne sedute, l'uomo nella laguna, la fabbrica e la laguna;
    # la scritta entra con la voce; dopo la frase ancora poche immagini con la musica
    a2, b2 = 0.0, 5.35
    t_c0 = e.t
    lead, after = 0.3, 2.6
    tl.vos.append(dict(file=soft_clean(C("0102"), a2, b2), a=a2, b=b2, speed=1.0, t=t_c0 + lead, raw=True))
    dur = lead + (b2 - a2) + after
    items = [(C("0063"), 4.2), (C("0544"), 1.5), (C("0069"), 0.0), (C("0074"), 0.0), (C("0107"), 2.0)]
    tl._add(closing_visual(W, H, items, dur, lead, dur - lead), 0, dur, audio=False, grade="null")
    off = max(0.0, 34.6 - (e.t - t_e))
    music(tl, "coir_finale", t_e, t_c0 + lead + (b2 - a2) + 0.4, offset=off, fin=1.0, fout=0.6)
    music(tl, "coir_finale", t_c0 + lead + (b2 - a2), e.t, offset=off + t_c0 + lead + (b2 - a2) - t_e, level=0.3,
          fin=0.5, fout=1.0)
    sigla_d(tl, OUT, clips=SIGLA_CLIPS, tag="coir")

    chapters = [(0.0, "Made in India"), (t_1, "Le donne che non lo fanno più"), (t_l, "La laguna"),
                (t_d, "Sotto la tettoia"), (t_f, "La fabbrica"), (t_c, "I nostri tappeti"), (t_e, "Chiusura")]
    out = f"{OUT}/VociVere_coir_long_{W}x{H}.mp4"
    json.dump(dict(chapters=chapters, t_sal=t_sal, t_s=t_s, banners=dict(iscriviti=t_1 + 0.3, like=t_m + 0.5)),
              open(f"{OUT}/long_{W}x{H}.json", "w"), indent=1)
    e.render(out)
    return out


# ================= VERTICALI (formato regole/formato_reel.md, modello projects/comorin/build.py) =================
PAD = (0.03, 0.06)
PAUSE = 0.45                 # pausa d'enfasi dopo le frasi chiave dei verticali (Manuel 6/11)
VMUS, VMUS_UP = 0.11, 0.26


def vphrase(a, b, text, cut=()):
    """Frase del VO dei verticali (tratto misurato sulla voce pulita) con le parole del copione: tempi dalla trascrizione
    quando le parole sono tante quante; altrimenti distribuiti sulle lettere."""
    asr = [t for w, t in words_of(VOV) if a - 0.15 <= t < b]
    ws = text.split()
    if len(asr) == len(ws):
        times = [max(t, a) for t in asr]
    else:
        L = sum(len(w) + 1 for w in ws)
        acc, times = 0, []
        for w in ws:
            times.append(a + (b - a) * acc / L); acc += len(w) + 1
    return (a, b, list(zip(ws, times)), list(cut))


def at(t0, line, w):
    """Tempo nel montato della parola w della frase che parte a t0."""
    tw = next(t for x, t in line[2] if x.lower().startswith(w.lower()))
    return t0 + (tw - (line[0] - PAD[0]))


def vsize():
    return (540, 960) if PREVIEW else (1080, 1920)


def vreel(name):
    W, H = vsize()
    r = Reel(f"{OUT}/reel_{name}_{W}_work", W, H, speed=1.0, gap=0.0, amb=0.0, cap_box=True)
    def say(line, vis, pause=0.0):
        """pause: breve silenzio dopo la frase (Manuel 6/11: solo dove serve a far arrivare un concetto, mai lunga);
        l'immagine resta, la musica continua sotto."""
        r.GAP = pause
        t0 = r.narr(VOV, line[0], line[1], vis, words=line[2], pad=PAD,
                    cuts=[(ca - 0.12, cb + 0.06) for ca, cb in line[3]])
        r.GAP = 0.0
        return t0
    return r, say


def faster(src, out, k=1.1):
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", f"[0:v]setpts=PTS/{k},fps=30[v];[0:a]atempo={k}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out])
    return out


def vfinish(r, name, track, t_b, end, offset=0.0):
    tl = r.tl
    tl.music(0.0, t_b + 0.3, f"{AUD}/{track}.flac", offset=offset, level=VMUS, fin=0.05, fout=0.3, duck=False, norm=False)
    tl.music(t_b, end, f"{AUD}/{track}.flac", offset=offset + t_b, level=VMUS_UP, fin=0.1, fout=1.0, duck=False, norm=False)
    tl.audio_map = {VOV: cleaned(VOV, VOCE)}
    tl.nat_af = "highpass=f=90"
    W, H = r.W, r.H
    out = f"{OUT}/VociVere_coir_{name}_{W}x{H}.mp4"
    # velocità normale (Manuel 6/11: il VO dei verticali di coir è già sciolto, niente 1.1x)
    return r.render(out, crf=16 if W == 1080 else 24, preset="medium" if W == 1080 else "veryfast")


def teaser():
    """L'uomo della laguna (Kerala, India solo qui)."""
    r, say = vreel("teaser")
    T1 = vphrase(11.66, 14.12, "Quello che lui tira su ogni giorno può finire all'ingresso di casa tua.")
    T2 = vphrase(14.49, 15.0, "Gusci di cocco.")
    T3 = vphrase(15.28, 16.07, "Kerala, India.")
    T4 = vphrase(16.31, 18.89, "Ha settantasei anni. Scende in questa laguna e li tira su a mano.")
    T5 = vphrase(19.20, 21.59, "Restano sott'acqua per mesi, finché la fibra non si stacca.")
    T6 = vphrase(21.97, 24.75, "La sua barca ne ha cinquanta. E lui la spinge ancora con una pertica.")
    say(T1, [(r.own(C("0544"), 1.0, cx=0.5), None)], pause=PAUSE)
    r.title(0.0, r.t, "Fino a casa tua", "Tag", 400)
    t2 = say(T2, [(r.own(C("0021"), 1.0, cx=0.45), None)])
    r.title(t2, r.t, "Gusci di cocco", "Tag", 400)
    t3 = say(T3, [(r.own(C("0107"), 2.0, cx=0.55), None)])
    r.title(t3, r.t + 0.4, "Kerala, India", "Tag", 400)
    say(T4, [(r.own(C("0052"), 2.0, cx=0.45), 1.5), (r.own(C("0046"), 0.8, cx=0.5), None)])
    say(T5, [(r.own(C("0108"), 9.0, cx=0.45), 1.3), (r.own(C("0061"), 0.5, cx=0.8), None)])
    say(T6, [(r.own(C("0022"), 1.0, cx=0.5), 1.4), (r.own(C("0020"), 1.0, cx=0.5), None)])
    t_b = r.t
    r.cap_stop.append(t_b)
    _, end = RC.close(r, OUT, C("0052"), 4.0, variant="A", cx=0.45)   # lui che sorride in camera
    return vfinish(r, "teaser", "coir_laguna", t_b, end)


def madeinindia():
    r, say = vreel("madeinindia")
    M1 = vphrase(28.60, 31.43, "Per ogni tappeto, a loro vanno ottanta centesimi. Ce lo dicono qui.")
    M2 = vphrase(31.77, 34.75, "Hai uno zerbino di cocco? Sopra c'è scritto Made in India. Ecco chi l'ha fatto.")
    M4 = vphrase(35.07, 37.51, "Aprono i gusci a mano, sedute per terra, fino alle due.")
    M5 = vphrase(37.86, 40.62, "La fibra diventa corda, la corda diventa tappeto. E parte per l'Europa.")
    M6 = vphrase(41.03, 43.53, "Il tappeto va lontano. Gli ottanta centesimi restano qui.")
    say(M1, [(r.own(C("0540"), 1.0, cx=0.42), None)], pause=PAUSE)
    r.title(0.0, r.t, "80 centesimi", "Tag", 400)
    t2 = say(M2, [(r.own(C("0540"), 4.5, cx=0.42), 1.2), (r.own(C("0542"), 2.0, cx=0.45), None)])
    r.title(at(t2, M2, "Made"), r.t, "Made in India", "Tag", 400)
    say(M4, [(r.own(C("0109"), 1.0, cx=0.45), 1.3), (r.own(C("0110"), 0.5, cx=0.6), None)])
    say(M5, [(r.own(C("0069"), 0.0, cx=0.4), 1.3), (r.own(C("0087"), 0.0, cx=0.45), None)])
    say(M6, [(r.own(C("0540"), 20.0, cx=0.42), None)])
    t_b = r.t
    r.cap_stop.append(t_b)
    _, end = RC.close(r, OUT, C("0542"), 4.0, variant="B", cx=0.45)
    return vfinish(r, "made_in_india", "coir_finale", t_b, end, offset=4.0)


def indietro():
    r, say = vreel("indietro")
    N1 = vphrase(48.33, 50.57, "Duecentottanta pezzi di corda in otto ore.")
    N1b = vphrase(51.02, 52.0, "Camminando all'indietro.")
    N2 = vphrase(52.08, 53.54, "È così che nasce la corda di cocco.")
    N4 = vphrase(54.82, 56.95, "Due fili di fibra, intrecciati passo dopo passo.")
    N5 = vphrase(59.41, 61.24, "Un pezzo, poi un altro. Tutto il giorno.")
    N6 = vphrase(61.51, 64.24, "Lei è Mary. La corda che ha in mano diventerà un tappeto.")
    say(N1, [(r.own(C("0069"), 0.0, cx=0.4), None)])
    r.title(0.0, r.t, "280 pezzi in 8 ore", "Tag", 400)       # sparisce quando entra "All'indietro" (Manuel 9/11)
    t1b = say(N1b, [(r.own(C("0074"), 0.0, cx=0.45), None)], pause=PAUSE)
    r.title(t1b, r.t, "All'indietro", "Tag", 400)
    say(N2, [(r.own(C("0074"), 1.2, cx=0.45), None)])
    say(N4, [(r.own(C("0068"), 1.0, cx=0.62), 1.2), (r.own(C("0073"), 1.5, cx=0.45), None)])
    say(N5, [(r.own(C("0072"), 1.0, cx=0.4), 1.1), (r.own(C("0087"), 0.0, cx=0.45), None)])
    t6 = say(N6, [(r.own(C("0085"), 0.0, cx=0.55), None)])
    r.title(at(t6, N6, "Mary"), at(t6, N6, "Mary") + 1.6, "Mary", "Tag", 400)
    t_b = r.t
    r.cap_stop.append(t_b)
    _, end = RC.close(r, OUT, C("0085"), 4.4, variant="A", cx=0.6)
    return vfinish(r, "indietro", "coir_macchine", t_b, end)


def premilla():
    r, say = vreel("premilla")
    # Manuel 9/11: le scritte in alto coprivano il viso. Dove succede l'immagine si ingrandisce di 1.3 tenendo fermo
    # il bordo alto: il viso scende sotto la scritta (testi, voce e tempi invariati)
    Z = DEF + f",scale={int(r.W * 1.3) // 2 * 2}:{int(r.H * 1.3) // 2 * 2},crop={r.W}:{r.H}:(iw-ow)/2:0"
    Z2 = DEF + f",scale={int(r.W * 1.45) // 2 * 2}:{int(r.H * 1.45) // 2 * 2},crop={r.W}:{r.H}:(iw-ow)/2:0"   # 0016: viso più in alto
    P1 = vphrase(69.03, 71.30, "Quarant'anni ad aprire gusci di cocco. A mano.")
    P2 = vphrase(71.69, 73.07, "Lei è Premilla. Ha sessant'anni.")
    P4 = vphrase(73.30, 75.15, "Quando questa società ha aperto, lei era già qui.")
    P5 = vphrase(81.60, 85.54, "Si lavora sedute per terra, sotto il sole, fino alle due. E ogni mattina, è ancora qui.")
    say(P1, [(r.own(C("0549"), 0.3, cx=0.45, grade=Z), None)], pause=PAUSE)
    r.title(0.0, r.t, "40 anni, a mano", "Tag", 400)
    t2 = say(P2, [(r.own(C("0016"), 0.0, cx=0.68, grade=Z2), None)])
    r.title(at(t2, P2, "Premilla"), r.t + 0.3, "Premilla, 60 anni", "Tag", 400)
    say(P4, [(r.own(C("0001"), 0.3, cx=0.62), None)])
    say(P5, [(r.own(C("0001"), 12.0, cx=0.62), 1.6), (r.own(C("0547"), 48.5, cx=0.5), 1.3), (r.own(C("0549"), 8.0, cx=0.45), None)])
    t_b = r.t
    r.cap_stop.append(t_b)
    _, end = RC.close(r, OUT, C("0016"), 0.4, variant="B", cx=0.68, speed=0.6, grade=Z2,
                      own=(lambda d: r.tl._add(C("0016"), 0.4, d * 0.6, speed=0.6, gain=0.0, cx=0.68, grade=Z2, audio=False)))
    return vfinish(r, "premilla", "coir_finale", t_b, end, offset=12.0)


def r1975():
    """Ordine di Manuel (registrazione finale, "questo è quello finale"): prima il salario, poi il resto."""
    r, say = vreel("1975")
    F1 = vphrase(177.87, 180.64, "Quattro euro al giorno. Il salario è quattrocento rupie.")
    F2 = vphrase(181.18, 182.56, "Per questo i giovani non vengono più.")
    F3 = vphrase(183.04, 184.92, "Se non arriva più nessuno, questo lavoro finisce.")
    F4 = vphrase(185.13, 188.21, "Queste donne lo fanno dal 1975. Oggi nessuna.")
    F5 = vphrase(188.75, 191.52, "Ci indicano un unico posto, qui intorno, dove ancora si fa.")
    say(F1, [(r.own(C("0529"), 0.3, cx=0.4), None)], pause=PAUSE)
    r.title(0.0, r.t, "4 euro al giorno", "Tag", 400)
    say(F2, [(r.own(C("0525"), 0.5, cx=0.35), None)])
    say(F3, [(r.own(C("0527"), 4.0, cx=0.55), None)])
    t4 = say(F4, [(r.own(C("0527"), 30.0, cx=0.5), 1.6), (r.own(C("0525"), 6.0, cx=0.55), None)], pause=PAUSE)
    r.title(at(t4, F4, "1975"), r.t, "Dal 1975", "Tag", 400)
    say(F5, [(r.own(C("0529"), 6.0, cx=0.55), 1.4), (r.own(C("0106"), 4.0, cx=0.5), None)])
    t_b = r.t
    r.cap_stop.append(t_b)
    _, end = RC.close(r, OUT, C("0525"), 1.0, variant="A", cx=0.35)
    return vfinish(r, "1975", "coir_strada", t_b, end)


if __name__ == "__main__":
    what = [a for a in sys.argv[1:] if not a.startswith("--")] or ["long"]
    for w in what:
        if w == "long":
            print(long_video(*((960, 540) if PREVIEW else (3840, 2160))))
        else:
            print({"teaser": teaser, "madeinindia": madeinindia, "indietro": indietro, "premilla": premilla,
                   "1975": r1975}[w]())
