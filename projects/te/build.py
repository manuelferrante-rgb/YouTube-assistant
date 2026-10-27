#!/usr/bin/env python3
"""Tè di Munnar (26/10): lungo 16:9, teaser e 3 verticali, reel del bucato.

    python3 projects/te/build.py long|bucato [--preview]
Girato in work/te/raw (cartella Drive 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw), voiceover in work/te/vo/Rajmala.m4a.
Girato e parlato in projects/te/girato.md, scaletta in projects/te/brief.md, tagli del VO in vo_tagli.md.
Stesso motore del lungo di arthunkal (projects/arthunkal/build.py): Edit, tagli sulla voce vera, niente fermi.
"""
import glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, dur_of, ts
from sigla import sigla_d
from voice_clean import cleaned

PREVIEW = "--preview" in sys.argv
W_ = os.path.join
WORK = f"{ROOT}/work/te"
R = f"{WORK}/raw"
OUT = f"{WORK}/out"
GFX = f"{WORK}/gfx"
AUD = f"{ROOT}/projects/te/audio"          # suoni e musica forniti dalla chat Audio
VO1 = f"{WORK}/vo/vo_te_pulito.wav"                # VO ripulito da Audio (stessi tempi di Rajmala.m4a)
os.makedirs(OUT, exist_ok=True); os.makedirs(GFX, exist_ok=True)

# 27/10 sera (Manuel): musica_colline tolta (fondo scuro 60-250 Hz, suonava come un motore). Sotto il voiceover va
# solo la musica nuova della chat Audio: MUSIC=<file> quando arriva in projects/te/audio/.
MUSIC = os.environ.get("MUSIC") or None
NIGHT = "eq=brightness=0.03:gamma=1.12:contrast=1.04:saturation=1.08"
DEF = "eq=contrast=1.03:saturation=1.05"


def C(tag):
    """Clip del 26/10 per ora di ripresa HHMMSS."""
    m = glob.glob(f"{R}/DJI_20261026{tag}_*")
    assert len(m) == 1, (tag, m)
    return m[0]


# ---------- parlato nelle clip: per non sovrapporre mai due voci ----------
_SEG = {}
for jf in (f"{WORK}/trans.json",):
    if os.path.exists(jf):
        for k, v in json.load(open(jf)).items():
            _SEG[os.path.basename(k)] = v


def clean_voices(tl):
    """Chi parla si sente con la sua voce pulita (rombo e fondo tolti, tools/voice_clean.py), 27/10 sera."""
    used = {sh["src"] for sh in tl.shots if sh["norm"]} | {v["file"] for v in tl.vos}
    tl.audio_map = {f: cleaned(f, f"{WORK}/voce") for f in used if f.startswith(R)}


def has_voice(src, a, b):
    """C'è parlato vero in [a, b]? (le parole isolate come "Yeah", "Uh" sono quasi sempre rumore di folla)"""
    return any(s["start"] < b and s["end"] > a and len(s.get("words", [])) >= 2 and s["end"] - s["start"] >= 0.8
               for s in _SEG.get(os.path.basename(src), []))

_WVO = ([w for s_ in next(iter(json.load(open(f"{WORK}/vo/rajmala.json")).values())) for w in s_["words"]]
        if os.path.exists(f"{WORK}/vo/rajmala.json") else [])

# ---------- mai parole mangiate: i tagli seguono la voce vera (energia), non solo la trascrizione ----------
_VOICED = {}


def voiced(src):
    """-> (array booleano a 10 ms: c'è voce?, affidabile?). Inaffidabile se la clip è tutta rumore (folla)."""
    if src not in _VOICED:
        import numpy as np
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                                          "-af", "highpass=f=100", "-f", "f32le", "-"], capture_output=True).stdout,
                          np.float32)
        n = len(x) // 160
        db = 20 * np.log10(np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-9)
        db = np.convolve(db, np.ones(8) / 8, mode="same")
        lo, hi = np.percentile(db, 10), np.percentile(db, 95)
        _VOICED[src] = (db > lo + 0.45 * (hi - lo), hi - lo >= 12)
    return _VOICED[src]


def snap(src, a, b, lim_a=0.0, lim_b=1e9):
    """Allarga [a, b] finché la parola in corso non è finita (fine fino a +0.8 s, inizio fino a -0.5 s)."""
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


def tight(src, ranges, min_gap=0.32, keep=0.1):
    """Toglie i vuoti nel parlato: spezza ogni tratto sui silenzi più lunghi di min_gap (lascia keep s per lato)."""
    v, ok = voiced(src)
    if not ok:
        return ranges
    out = []
    for a, b in ranges:
        i, s = int(a * 100), int(a * 100)
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


def gap_at(src, lo, hi):
    """Istante più silenzioso di [lo, hi] (passo 10 ms): il punto dove spezzare una frase tra due parole."""
    import numpy as np
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{lo:.3f}", "-t", f"{hi - lo:.3f}", "-i", src,
                                      "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-af", "highpass=f=100", "-f", "f32le",
                                      "-"], capture_output=True).stdout, np.float32)
    n = len(x) // 160
    e = np.convolve((x[:n * 160].reshape(n, 160) ** 2).mean(1), np.ones(3) / 3, mode="same")
    return round(lo + int(np.argmin(e)) / 100, 2)


def words_of(src):
    """Parole (testo, inizio) della trascrizione di una clip o del voiceover."""
    if src == VO1:
        return _WVO
    return [w for s_ in _SEG.get(os.path.basename(src), []) for w in s_["words"]]


def snap_w(src, a, b):
    """snap limitato dalla trascrizione: la fine non entra nella parola successiva e l'inizio non torna nella
    parola precedente (così un "ne ne" tolto non rientra, Manuel 27/10)."""
    st = sorted(t for _, t in words_of(src))
    nxt = [t for t in st if t > b - 0.03]
    prv = [t for t in st if t <= a + 0.08]
    return snap(src, a, b, lim_a=(prv[-1] - 0.06) if prv else 0.0, lim_b=(nxt[0] - 0.02) if nxt else 1e9)


def piece(name, src, ranges, speed=1.1, gap=0.2, exact=False):
    """Voce da uno o più tratti di un file, uniti con respiri di `gap` s e accelerata. -> (file, durata).
    exact: tagli già misurati sulla forma d'onda, senza snap (es. una parola ripetuta tolta)."""
    if not exact:
        ranges = [snap_w(src, a, b) for a, b in ranges]
    out = f"{OUT}/{name}_{abs(hash(tuple(ranges))) % 10**8}.wav"
    if not os.path.exists(out):
        fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={speed},aresample=48000,"
                     f"afade=t=in:d=0.03,afade=t=out:st={(b - a) / speed - 0.05:.3f}:d=0.05,apad=pad_dur={gap}[p{i}];"
                     for i, (a, b) in enumerate(ranges))
        tot = sum((b - a) / speed + gap for a, b in ranges) - gap
        fc += "".join(f"[p{i}]" for i in range(len(ranges))) + f"concat=n={len(ranges)}:v=0:a=1,atrim=end={tot:.3f}[o]"
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[o]", "-ac", "1", "-ar", "48000", out])
    return out, dur_of(out)


def ambient(src, a, d, name=None):
    if has_voice(src, a, a + d):                                    # mai voci sotto altre voci o sotto la mappa
        print(f"ATTENZIONE ambiente con parlato: {os.path.basename(src)} {a:.1f}-{a + d:.1f}", flush=True)
    out = f"{OUT}/amb_{os.path.basename(src)[:30]}_{a:.2f}_{d:.2f}.wav"
    if not os.path.exists(out):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, a):.3f}", "-t", f"{d:.3f}", "-i", src, "-vn", "-ac", "2",
             "-ar", "48000", "-af", f"afade=t=in:d=0.15,afade=t=out:st={max(0, d - 0.25):.3f}:d=0.25", out])
    return out


def aud(name, fallback=None):
    """Suono della chat Audio se c'è, altrimenti il ripiego (suono vero del girato)."""
    for ext in ("wav", "flac", "mp3", "m4a"):
        p = f"{AUD}/{name}.{ext}"
        if os.path.exists(p):
            return p
    return fallback


_DUR = {}


def clip_dur(src):
    if src not in _DUR:
        _DUR[src] = dur_of(src)
    return _DUR[src]


class Edit:
    """Timeline + scritte (etichette in corsivo, titolo grande) + passaggi nel nero."""

    def __init__(self, W, H, tag):
        self.tl = Timeline(W, H, f"{OUT}/{tag}_work")
        self.tl.voice_check = has_voice
        self.W, self.H, self.k = W, H, (H / 1080 if W > H else W / 1080)
        self.labels, self.titles = [], []
        self.black = f"{OUT}/black_{W}x{H}.mp4"
        if not os.path.exists(self.black):
            run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r=30:d=2",
                 "-c:v", "libx264", "-crf", "18", self.black])

    @property
    def t(self):
        return self.tl.t

    def b(self, src, a, d, cx=0.5, grade=DEF, fx=None, speed=1.0):
        """B-roll muto (Manuel, 27/10 sera): mai rumori del girato, né sotto chi parla né da soli. Nei tratti senza
        parlato vanno solo, se servono, i suoni melodici della chat Audio; altrimenti il B-roll si tiene breve."""
        self.tl.broll(src, a, d, gain=0.0, cx=cx, grade=grade, fx=fx or dict(zoom=(1.0, 1.04, None)), speed=speed,
                      fade=0.12)

    def say(self, src, ranges, speed=1.1, cx=0.5, cover=None, subs=(), grade=DEF, gain=1.0, cut_gaps=False, pad=(0.06, 0.12)):
        """Parlato in camera tagliato sulle pause; cover = {indice: (clip, a, gain)} copre quel tratto con un'altra
        immagine mentre la voce continua (salti di montaggio nascosti). subs in tempi della sorgente."""
        cover = cover or {}
        D = clip_dur(src)
        ranges = [snap_w(src, a, b) for a, b in ranges]              # la parola in corso finisce sempre
        if cut_gaps:                                                # niente vuoti dentro le frasi (Manuel, 26/10)
            assert not cover, "cut_gaps con cover: gli indici cambierebbero"
            ranges = tight(src, ranges)
        merged = []
        for a, b in ranges:                                         # tratti che ora si toccano: uno solo
            if merged and a <= merged[-1][1] + 0.02 and not cover:
                merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
            else:
                merged.append((a, b))
        ranges = merged
        # margini per non mangiare le parole: 0.06 s prima e 0.12 s dopo (senza sovrapporre il tratto successivo);
        # più stretti dove la frase deve suonare unica
        padded = []
        for i, (a, b) in enumerate(ranges):
            nxt = ranges[i + 1][0] if i + 1 < len(ranges) else D
            prv = padded[-1][1] if padded else 0.0
            padded.append((max(prv, a - pad[0], 0.0), min(b + pad[1], nxt, D - 0.05)))
        for i, (a, b) in enumerate(padded):
            t0 = self.t
            if i in cover:
                src2, a2 = cover[i][:2]
                g = src2.startswith(GFX)                     # grafiche: senza audio né correzione colore
                self.tl._add(src2, a2, (b - a) / speed, gain=0.0, grade="null" if g else grade, fade=0.05,
                             audio=not g, fx=None if g else dict(zoom=(1.0, 1.04, None)))
                self.tl.vos.append(dict(file=src, a=a, b=b, speed=speed, t=t0))
            else:
                self.tl.speech(src, [(a, b)], speed=speed, cx=cx, grade=grade, gain=gain)
            for sa, sb, txt in subs:
                lo, hi = max(sa, a), min(sb, b)
                if hi - lo > 0.15:
                    self.tl.subs.append((t0 + (lo - a) / speed, t0 + (hi - a) / speed, txt))

    def vo(self, file, d, shots, lead=0.2, tail=0.3, weights=None, music=None):
        """Voiceover sopra immagini; music = offset nella musica originale (solo sotto il voiceover)."""
        t0 = self.tl.vo(file, 0, d, shots, speed=1.0, lead=lead, tail=tail, nat=0.18, weights=weights)
        if music is not None and MUSIC:
            self.tl.music(t0, self.t, MUSIC, offset=music, level=0.42, fin=0.6, fout=0.9)
        return t0

    def to_black(self, z=1.16, T=0.55, gap=0.22, strong=False):
        """Fine scena: spinta che accelera e va nel nero, breve nero, suono d'ingresso nel nero."""
        last = self.tl.shots[-1]
        fx = dict(last.get("fx") or {}); fx.pop("zoom", None)
        fx.update(push_out=(z, T), black_out=0.3)
        last["fx"] = fx
        self.tl._add(self.black, 0, gap, audio=False, grade="null")
        self.strong = strong

    def from_black(self):
        """Inizio scena dal nero: l'ultima inquadratura aggiunta rientra dal nero allargandosi; il suo suono
        parte mezzo secondo prima dell'immagine (J-cut)."""
        sh = self.tl.shots[-1]
        sh["fx"] = dict(black_in=0.35, zoom=(1.08, 1.0, 0.8))   # niente ambienti di transizione (27/10 sera)

    def bed(self, t0, t1, src, a=0.0, gain=0.16):
        """Letto d'ambiente vero e basso sotto una scena intera: niente buchi di quasi silenzio tra i tagli."""
        d, n = t1 - t0, dur_of(src) - a - 0.3
        t = t0
        while t < t1 - 0.1:
            seg = min(n, t1 - t + 0.3)
            self.tl.sfx(t, ambient(src, a, seg), gain)
            t += seg - 0.3

    def label(self, text, t0, d=2.6):
        self.labels.append((t0, t0 + d, text))

    def title(self, text, t0, d):
        self.titles.append((t0, t0 + d, text))

    def ass(self):
        k, W, H = self.k, self.W, self.H
        S = lambda v: int(round(v * k))
        vert = H > W
        head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Sub,Poppins Medium,{self.tl.sub_size},&H0098D8F2,&H0098D8F2,&H00000000,&H90000000,0,0,0,0,100,100,"
                f"0.5,0,1,{self.tl.sub_size / 32:.1f},{self.tl.sub_size / 36:.1f},2,{int(W * 0.08)},{int(W * 0.08)},"
                f"{self.tl.sub_margin},1\n"
                f"Style: Lab,Playfair Display,{S(46)},&H00F2F2F2,&H00FFFFFF,&H00000000,&H80000000,0,-1,0,0,100,100,0.5,0,1,"
                f"{S(1.2)},{S(2.2)},1,{S(70)},{S(70)},{S(64)},1\n"
                f"Style: Big,Playfair Display,{S(150)},&H00F4F4F4,&H00FFFFFF,&H00000000,&H90000000,-1,-1,0,0,100,100,1,0,1,"
                f"{S(1.5)},{S(4)},5,0,0,0,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        ev = [(0, a, b, "Sub", t) for a, b, t in self.tl.subs]
        for a, b, t in self.labels:
            ev.append((1, a, b, "Lab", "{\\fad(350,350)}" + t))
        for a, b, t in self.titles:
            ev.append((2, a, b, "Big", f"{{\\an5\\pos({W // 2},{H // 2})\\fad(600,600)\\fscx96\\fscy96"
                                         f"\\t(0,{int((b - a) * 1000)},\\fscx102\\fscy102)}}" + t))
        p = f"{self.tl.dir}/scritte.ass"
        with open(p, "w") as f:
            f.write(head)
            for layer, a, b, st, txt in sorted(ev, key=lambda e: e[1]):
                f.write(f"Dialogue: {layer},{ts(a)},{ts(b)},{st},,0,0,0,,{txt}\n")
        return p

    def finalize(self, xin=0.3):
        """Prima del render: niente fermo immagine (inizio anticipato o leggero rallentatore se la clip è corta)
        e dissolvenze brevi tra immagini senza parlato (mai sul parlato in camera, sul nero o sulle grafiche)."""
        GFXLIKE = lambda sh: sh["src"].startswith(GFX) or sh["src"] == self.black or "sigla" in sh["src"]
        self.tl.fix_freezes()
        for prev, sh in zip(self.tl.shots, self.tl.shots[1:]):
            if prev["norm"] or sh["norm"] or GFXLIKE(prev) or GFXLIKE(sh):
                continue
            if "black_out" in (prev.get("fx") or {}) or "black_in" in (sh.get("fx") or {}):
                continue
            if sh["d"] > 2 * xin and prev["d"] > xin:
                sh["xin"] = xin

    def render(self, out):
        self.finalize()
        self.tl.ass_override = self.ass()
        clean_voices(self.tl)
        print(f"== {os.path.basename(out)}: {len(self.tl.shots)} inquadrature, {self.t:.1f} s", flush=True)
        if PREVIEW:
            return self.tl.render(out, crf=26, preset="veryfast")
        self.tl.drop_shots = True                                   # disco stretto: consegna diretta per Drive
        self.tl.final_opts = ["-maxrate", "38M", "-bufsize", "76M"]
        return self.tl.render(out, crf=20, preset="medium")


# ---------- grafiche (stile carta nautica, approvate da Manuel) ----------

def storia(W, H, name, events, dur, prev=""):
    out = f"{GFX}/storia_{name}_{W}x{H}.mp4"
    if not os.path.exists(out):
        cmd = ["python3", f"{ROOT}/tools/timeline_anim.py", out, "--events", events, "--dur", f"{dur}",
               "--w", str(W), "--h", str(H)]
        if prev:
            cmd += ["--prev", prev]
        run(cmd)
    return out


# ---------- voiceover (vo_take1, tempi in vo_blocchi.md) ----------
def VO(name, ranges, src=VO1, **kw):
    return piece(f"vo_{name}", src, ranges, **kw)


LOGO_W = f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png"


def logo_card(src, t, dur, W, H, out, cx=0.5):
    """Fermo immagine sfocato e scurito con il logo che entra (stessa chiusura del mercato)."""
    if os.path.exists(out):
        return out
    crop = f"crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{cx}-ih*9/32))':0," if H > W else ""
    lw = int(W * (0.62 if H > W else 0.42))
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src, "-loop", "1", "-t", f"{dur}", "-i", LOGO_W,
         "-filter_complex",
         f"[0:v]{crop}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},trim=end_frame=1,"
         f"tpad=stop_mode=clone:stop_duration={dur},fps=30,trim=duration={dur},setpts=PTS-STARTPTS,split[a][b];"
         f"[b]gblur=sigma={int(28 * W / 1920)},eq=brightness=-0.24:saturation=0.65[bl];"
         f"[a][bl]xfade=transition=fade:duration=0.6:offset=0.05[v];"
         f"[1:v]scale={lw}:-1,format=rgba,fade=t=in:st=0.35:d=0.6:alpha=1[lg];"
         f"[v][lg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[o]",
         "-map", "[o]", "-t", f"{dur}", "-c:v", "libx264", "-crf", "15", "-preset", "veryfast", out])
    return out


# ================= LUNGO =================
# sigla a tema (Manuel, 26/10): 6 pezzi del pellegrinaggio al posto di quelli del mercato

ROUTE = "Marari|9.62646|76.296|la costa;Munnar|10.0889|77.0595|le colline del tè"


def mappa(W, H, tA, tB, dur):
    tag = f"mappa_{tA:.2f}_{tB:.2f}_{dur:.2f}"
    out = f"{GFX}/{tag}_{W}x{H}.mp4"
    if not os.path.exists(out):
        run(["python3", f"{ROOT}/tools/route_map.py", out, "--route", ROUTE, "--km", "0", "--t-a", f"{tA}",
             "--t-b", f"{tB}", "--dur", f"{dur}", "--w", str(W), "--h", str(H)])
    snd = f"{GFX}/{tag}.wav"
    if not os.path.exists(snd):
        run(["python3", f"{ROOT}/projects/arthunkal/map_sfx.py", snd, "--t-a", f"{tA}", "--t-b", f"{tB}",
             "--t-km", f"{tB}", "--dur", f"{dur}"])
    return out, snd


SIGLA_CLIPS = [(C("115803"), 0.5), (C("133721"), 70.0), (C("115958"), 1.0), (C("142447"), 18.0), (C("135033"), 1.0),
               (C("114701"), 4.0)]                                  # sigla a tema: filari, raccolta, cesto, chai
QUIET = (C("114701"), 0.0)                                          # panorama tra i filari: ambiente vero, senza voci
PX = lambda i: f"{WORK}/stock/px_{i}.mp4"                           # Pixabay: solo immagini generiche, senza persone


def vo_over(e, name, ranges, items, lead=0.15, tail=0.25, music=None, **kw):
    """Voiceover sopra immagini e grafiche: items = [(clip, inizio, durata) | (grafica, None, durata)];
    durata None = si divide il resto. -> (t0 della voce, durata della voce)."""
    f, d = VO(name, ranges, **kw)
    t0 = e.t
    e.tl.vos.append(dict(file=f, a=0, b=d, speed=1.0, t=t0 + lead))
    total = lead + d + tail
    fixed = sum(x[2] for x in items if x[2])
    rest = max(0.8, total - fixed) / max(1, sum(1 for x in items if not x[2]))
    e.starts = []                                                 # inizio di ogni immagine (per i suoni di Audio)
    for src, a, dd in items:
        dd = dd or rest
        e.starts.append(e.t)
        if a is None:
            e.tl._add(src, 0, dd, audio=False, grade="null")
        else:                                                     # muta: sotto il voiceover solo la voce
            e.b(src, a, dd)
    if music is not None and MUSIC:
        e.tl.music(t0, e.t, MUSIC, offset=music, level=0.42, fin=0.6, fout=0.9)
    return t0 + lead, d


def long_video(W, H):
    """Lungo (26/10): gancio sulle colline affittate nel 1877, Munnar, Sadish tra i filari, la storia con il
    voiceover e la linea del tempo, il tè in città, chiusura con il logo. Scaletta in projects/te/brief.md."""
    e = Edit(W, H, "long")
    tl = e.tl
    G = lambda name, ev, dur, prev="": storia(W, H, name, ev, dur, prev)

    # 0. GANCIO (Manuel 27/10): si parte da Manuel tra i filari; mentre dice dell'affitto del 1877 si vede Sadish
    e.say(C("115233"), [(36.5, 39.6), (41.4, 44.55), (44.55, 47.8)], cover={1: (C("133703"), 1.0), 2: (C("133703"), 4.5)})
    e.title("1877 · 3.000 rupie l'anno", e.t - 3.6, 3.4)               # la cifra del titolo, con "l'anno" (Insights)
    vo_over(e, "1", [(2.0, 5.42)], [(C("115728"), 0.5, None), (C("113517"), 0.5, None)], lead=0.2, tail=0.3)
    # una frase sola, senza nessun vuoto (Manuel 27/10): pause tolte anche tra "E la storia." e "nella raccolta"
    e.say(C("120307"), [(0.82, 2.95), (3.6, 5.95)], cover={0: (C("133721"), 69.6)}, pad=(0.03, 0.04))
    e.say(C("120356"), tight(C("120356"), [(1.97, 6.6)], min_gap=0.15, keep=0.05), pad=(0.03, 0.04))
    t_q = e.t
    e.b(C("114701"), 1.0, 1.8)                                        # breve: sotto non c'è suono (27/10 sera)
    e.title("E oggi, di chi sono queste colline?", t_q - 0.5, 2.3)      # domanda aperta, la risposta è al blocco 10
    sigla_d(tl, OUT, clips=SIGLA_CLIPS, tag="te")

    # 1. MUNNAR: dove siamo, la mappa, le colline e l'affitto del 1877
    t_m = e.t
    e.say(C("115233"), [(12.0, 15.3)])                               # "Sono a Munnar, in Kerala, a oltre 1500 metri."
    e.label("Munnar, Kerala", t_m + 0.3, 2.6)
    e.b(C("132930"), 0.5, 1.5)                             # solo un attimo di colline, niente mappa (27/10)
    vo_over(e, "2", [(6.6, 17.95)], [(G("1877", "1877|John Daniel Munro|affitta le colline dal raja di Poonjar|0.55", 3.8),
                                     None, 3.8), (PX(41146), 2.0, 2.6), (C("132655"), 1.0, None), (C("133703"), 6.0, None)],
             tail=0.15, music=0.0)
    vo_over(e, "3", [(18.75, 24.69)], [(G("1880", "1880|il primo tè|su una cinquantina di acri|0.65", 3.0, "1877"), None, 3.0),
                                       (C("132727"), 0.5, None)], lead=0.15, tail=0.2, music=11.0)

    # 2. CON SADISH TRA I FILARI
    t_s = e.t
    e.say(C("133625"), [(1.0, 6.7)])                                 # "Sadish è di qui... non il panorama, ma il lavoro."
    I = dict(speed=1.0, gain=1.3)
    e.say(C("133721"), [(8.2, 9.7), (10.0, 16.4), (17.2, 18.8), (19.6, 24.9), (30.3, 38.6), (39.5, 47.2)],
          cover={1: (C("134442"), 0.5), 3: (C("132655"), 1.0), 5: (C("133703"), 3.0)},
          subs=[(8.2, 9.7, "Questa è la piantagione di tè."),
                (10.0, 13.6, "Tutte le montagne che vedi, ovunque, sono tè."), (13.6, 16.4, "Verde. Coperte verdi."),
                (17.2, 18.8, "Coprono tutte le montagne."),
                (19.6, 24.9, "A Munnar quasi tutti lavorano nel tè."),
                (30.3, 34.4, "Già prima che nascessi io, mio padre e mia madre"),
                (34.4, 38.6, "lavoravano nel tè: per il governo, per le compagnie, nelle piantagioni."),
                (39.5, 44.0, "Una pianta di tè vive più di cent'anni."), (44.5, 47.2, "Questa pianta ha più di cent'anni.")],
          **I)
    e.say(C("133721"), [(55.4, 56.6)], subs=[(55.4, 56.6, "Solo acqua piovana.")], cover={0: (PX(92994), 3.0)}, **I)
    e.say(C("134852"), tight(C("134852"), [(0.3, 10.5)]))            # Manuel riporta Sadish: tutto organico
    e.say(C("133721"), [(57.4, 63.9), (69.5, 74.6), (76.0, 80.3), (81.1, 83.9), (85.0, 89.9)],
          cover={0: (C("135012"), 4.0)},
          subs=[(57.4, 63.9, "Queste foglie si raccolgono ogni dieci, quindici giorni."),
                (69.5, 74.6, "Questo è il metodo di raccolta: due, tre foglie."),
                (76.0, 80.3, "Due, tre foglie: sono quelle di buona qualità."),
                (81.1, 83.9, "Queste, le buone, vanno in fabbrica."),
                (85.0, 89.9, "Queste scure, nere, sono foglie cattive. Non si usano.")], **I)
    e.say(C("133721"), [(107.5, 111.7), (119.5, 131.2)],
          cover={1: (C("135033"), 0.5)},
          subs=[(107.5, 108.4, "Chi raccoglie?"), (108.4, 111.7, "Tutti: donne e uomini."),
                (119.5, 123.5, "Oggi raccolgo qui, domani vado su un'altra collina."),
                (124.0, 131.2, "Poi il mese dopo si torna qui. È un giro.")], **I)
    # Manuel: le foglie in mano, l'orario di lavoro
    rg = tight(C("135758"), [(0.0, 18.2)]) + [(18.3, 20.5)]            # "in generale c'è un processo": Sadish cammina
    e.say(C("135758"), rg, cover={len(rg) - 1: (C("135922"), 0.3)})
    e.say(C("134231"), tight(C("134231"), [(0.0, 12.8)]), cover={1: (C("133703"), 6.0)})
    # quanto si raccoglie, dove vanno le foglie
    e.say(C("134520"), [(6.2, 17.6), (26.8, 30.5), (50.8, 57.6), (58.2, 70.2)],
          cover={3: (C("114701"), 5.0)},
          subs=[(6.2, 11.2, "Normalmente, al giorno, una persona raccoglie"),
                (12.2, 16.5, "da ventisei a ventinove chili al giorno."), (17.0, 17.6, "In media."),
                (26.8, 29.5, "E chi raccoglie di più?"), (29.6, 30.5, "Soldi in più."),
                (50.8, 52.4, "Dove vanno le foglie?"), (53.9, 57.6, "Alla fabbrica del tè."),
                (58.2, 61.4, "Qui a Munnar ci sono tante fabbriche."),
                (62.0, 70.2, "Qui intorno ce ne sono tre, quattro: a venti, venticinque, trenta chilometri.")], **I)
    vo_over(e, "7", [(53.44, 58.38)], [(C("133703"), 1.0, None), (C("133721"), 70.0, None)], music=20.0)
    vo_over(e, "8", [(64.9, 70.6), (83.4, 86.1)], [(C("135758"), 3.5, None), (C("142433"), 1.0, None),
                                                   (C("142447"), 3.0, None)], tail=0.25, music=27.0)
    e.to_black()

    # 3. LA STORIA E DI CHI SONO OGGI LE COLLINE
    t_h = e.t
    e.b(C("134442"), 0.0, 1.2)
    e.from_black()
    e.say(C("133946"), [(0.1, 1.2), (32.6, 34.2), (42.7, 43.7), (54.7, 64.8), (65.5, 72.8)],
          cover={3: (C("135012"), 2.0)},
          subs=[(0.1, 1.2, "Conosci la storia?"), (32.6, 34.2, "1877."), (42.7, 43.7, "Era un inglese."),
                (54.7, 61.6, "A Munnar, tutto intorno, nord, sud, est, ovest, per quaranta chilometri,"),
                (62.4, 64.8, "ovunque piantagioni di tè."),
                (65.5, 72.8, "Tutte queste montagne si chiamano Kannan Devan Hills.")], **I)
    vo_over(e, "4", [(25.35, 29.91), (30.33, 36.19)],
            [(G("1895", "1895|Finlay Muir|compagnia scozzese di Glasgow|0.5", 3.4, "1877;1880"), None, 3.4),
             (C("113517"), 1.5, 3.0),
             (G("1897", "1897|Kannan Devan Hills Produce Company|0.6", 3.6, "1880;1895"), None, 3.6),
             (C("132930"), 3.0, None)], music=35.0)
    vo_over(e, "5", [(37.16, 43.93)],
            [(G("1901", "1901|la foresta tagliata|su larga scala|0.6;1911|il tè copre|circa 6.500 ettari|3.35", 5.0,
                "1895;1897"), None, 5.0), (C("132930"), 0.5, None)], music=47.0)
    vo_over(e, "6", [(44.82, 51.63)], [(C("132655"), 4.0, None), (C("115553"), 0.0, None)], tail=0.2, music=54.0)
    e.say(C("134136"), [(0.1, 7.6), (8.2, 22.4)], cover={1: (C("132655"), 2.0)},
          subs=[(0.1, 7.6, "Com'è il rapporto tra questa grande azienda e chi vive qui?"),
                (8.2, 13.0, "Sono trattati bene. Un ottimo rapporto,"),
                (13.0, 19.4, "aiuto, casa, cure mediche, trasporto."),
                (20.1, 22.4, "L'azienda dà tutto gratis.")], **I)
    vo_over(e, "9", [(88.16, 92.16)],                               # anno breve, poi subito le carte (27/10)
            [(G("1971b", "1971|legge del Kerala|sulle terre di queste colline|0.35", 1.9, "1901;1911"), None, 1.9),
             (PX(349087), 2.0, None)], tail=0.1, music=62.0)
    vo_over(e, "10", [(92.92, 101.25)],
            [(G("2005", "2005|l'azienda ai dipendenti|circa tredicimila|0.6", 3.6, "1911;1971"), None, 3.6),
             (C("132727"), 1.0, None), (C("135922"), 0.5, None)], music=66.0)
    e.say(C("135136"), tight(C("135136"), [(0.5, 25.3)]))
    vo_over(e, "11", [(101.98, 111.3), (111.74, 114.92)],
            [(G("2015", "2015|migliaia di raccoglitrici|bloccano Munnar per nove giorni|0.55", 4.0, "1971;2005"), None, 4.0),
             (C("135033"), 2.0, None), (C("115553"), 0.5, None)], music=76.0)
    e.label("Pombilai Orumai: unità delle donne", tl.vos[-1]["t"] + 5.9, 3.0)
    e.say(C("134639"), [(0.1, 9.3), (12.2, 19.0)], cover={1: (C("135012"), 6.0)},
          subs=[(0.1, 7.0, "Sai che l'India è il secondo produttore di tè al mondo, dopo la Cina?"),
                (8.1, 9.3, "Sì, l'India è seconda."),
                (12.2, 14.8, "Qui è una cultura molto profonda."),
                (16.3, 19.0, "La produzione migliore dell'India. Buona qualità.")], **I)
    # "colline ne ne produceva": il primo "ne" (131.64-131.73) si toglie sulla forma d'onda, senza respiro (27/10)
    vo_over(e, "12", [(130.30, 131.63), (131.735, 138.3)],
            [(PX(70333), 2.0, None), (C("132655"), 3.0, None), (C("132930"), 1.0, None)],
            tail=0.2, music=90.0, gap=0.0, exact=True)
    e.to_black(strong=True)

    # 4. IL TÈ IN CITTÀ (Manuel 27/10 sera): prima parte veloce, poche scene, subito al master che non vuole parlare.
    # Il B-roll del chai copre il parlato mentre se ne parla; ogni ritorno in camera ha voce e immagine dello stesso tratto.
    t_c = e.t
    e.b(C("141843"), 0.0, 1.2)
    e.from_black()
    e.label("Munnar", t_c + 0.3, 2.4)
    e.say(C("141707"), R_141707, cover={1: (C("142447"), 2.0)})      # il chai si vede su "questo tè tradizionale"
    e.say(C("142726"), [(43.4, 46.0), (46.3, 49.2)], speed=1.0, gain=1.3, cover={0: (C("142545"), 2.0)},
          subs=[(43.4, 46.0, "Lui è il chai master."), (46.3, 49.2, "Io servo.")])
    e.say(C("143138"), [(0.4, 2.6)])                                 # "In conclusione assaggiamo questo tè."
    e.say(C("143318"), R_143318, cover={1: (C("142545"), 2.0)})      # il master mentre Manuel dice "al master"

    # 5. CHIUSURA: VO 14 sulla sera e la nebbia, logo Voci Vere
    t_f = e.t
    vo_over(e, "14", [(155.36, 160.21)], [(C("160612"), 0.5, None), (C("152338"), 0.5, None)],   # niente bus (27/10)
            lead=0.4, tail=0.6, music=100.0)
    tl._add(logo_card(C("115803"), 2.5, 3.5, W, H, f"{OUT}/fine_logo_{W}x{H}.mp4"), 0, 3.5, audio=False,
            grade="null", fade=0.05)
    tl.shots[-1]["fx"] = dict(black_out=0.4)
    if MUSIC:
        tl.music(t_f, e.t, MUSIC, offset=100.0, level=0.42, fin=0.6, fout=1.6)

    # 27/10 sera (Manuel): niente letti continui sotto la voce (ambiente_colline sotto tutto suonava come un camion),
    # niente fruscii sulle grafiche; voce pulita, i suoni di Audio solo dove servono. Bassi tolti dal suono delle clip.
    tl.nat_af = "highpass=f=90"
    chapters = [(0.0, "Le colline del tè"), (t_m, "Munnar"), (t_s, "Con Sadish tra i filari"),
                (t_h, "La storia e chi ci lavora"), (t_c, "Il tè del chai master")]   # chiusura < 10 s: nel capitolo del chai
    out = f"{OUT}/VociVere_te_long_{W}x{H}.mp4"
    with open(f"{OUT}/voiceover_{W}x{H}.txt", "w") as fh:
        for v in tl.vos:
            if os.path.basename(v["file"]).startswith("vo_"):
                fh.write(f"{v['t']:.2f}\t{v['t'] + (v['b'] - v['a']) / v['speed']:.2f}\t{os.path.basename(v['file'])}\n")
    e.render(out)
    with open(f"{OUT}/capitoli_{W}x{H}.txt", "w") as fh:
        for t, n in chapters:
            fh.write(f"{int(t // 60)}:{int(t % 60):02d} {n}\n")
    return out


# ================= REEL DEL BUCATO (a parte dai 4 verticali, Manuel 26/10) =================
from reel_kit import Reel


def bucato():
    """~7 s in loop: lava al rubinetto, strizza, si gira verso la camera. Gancio in sovrimpressione dall'inizio,
    solo suono vero dell'acqua, niente etichetta di luogo (testi di Copy in copioni/te_testi.md)."""
    W, H = (540, 960) if PREVIEW else (1080, 1920)
    r = Reel(f"{OUT}/bucato_{W}_work", W, H, cx_cam=0.4)
    # i colpi dei panni (0.9, 1.5, 2.2 s in 105047; 2.1 s in 105115) mostrati più volte: è lei la "lavatrice"
    Z = dict(zoom=(1.3, 1.3, None))
    r.own(C("105047"), 0.2, cx=0.36, gain=1.0)(1.5)
    r.own(C("105115"), 1.6, cx=0.42, gain=1.0)(1.0)
    r.own(C("105047"), 1.8, cx=0.36, gain=1.0, fx=Z)(0.8)
    r.own(C("105115"), 0.6, cx=0.42, gain=1.0)(0.8)
    r.own(C("105047"), 0.3, cx=0.36, gain=1.0, fx=Z)(0.8)
    r.own(C("105047"), 4.2, cx=0.45, gain=1.0)(2.0)
    r.title(0.0, r.t, "POV: non hai la lavatrice\\N(e non ti serve)", "Mid", 1320)   # emoji solo nel testo del post
    out = r.render(f"{OUT}/VociVere_te_bucato_{W}x{H}.mp4", crf=18 if W == 1080 else 24,
                   preset="medium" if W == 1080 else "veryfast")
    return out


# ================= VERTICALI (teaser + 3 dopo il lungo; regole in regole/montaggio_documentario.md) =================
def vwords(tag, a, b, src_json=None):
    """Parole (testo, tempo) di una clip nell'intervallo [a, b) dalla trascrizione."""
    segs = _SEG.get(os.path.basename(C(tag)), []) if src_json is None else src_json
    return [(w, t) for s_ in segs for w, t in s_["words"] if a - 0.05 <= t < b]


FIXW = {"Moonar": "Munnar", "Monar": "Munnar", "te": "tè", "te.": "tè.", "Sadice": "Sadish"}


# parole riascoltate a pezzi (la trascrizione automatica di queste clip era sbagliata)
W_143318 = [("Ho", 0.56), ("provato", 0.88), ("a", 1.28), ("fare", 1.36), ("qualche", 1.6), ("domanda", 2.0), ("al", 2.96),
            ("master,", 3.28), ("lo", 3.84), ("chiamano", 4.0), ("così,", 4.32), ("del", 4.56), ("tè,", 4.8), ("e", 5.2),
            ("lui", 5.36), ("si", 5.52), ("è", 5.6), ("rifiutato.", 5.76), ("Forse", 9.04), ("proprio", 9.64), ("qua", 9.98),
            ("è", 10.38), ("l'essenza", 10.62), ("dell'India.", 11.46), ("Fare", 12.8), ("le", 13.2), ("cose", 13.36),
            ("senza", 13.68), ("apprezzamento", 14.0), ("altrui,", 14.66), ("farle", 15.28), ("semplicemente", 15.6),
            ("perché", 16.0), ("ti", 16.24), ("piace", 16.4), ("farle.", 16.88)]
W_143138 = [("In", 0.48), ("conclusione", 0.72), ("assaggiamo", 1.28), ("questo", 1.92), ("tè.", 2.24)]
W_141707 = [("E", 0.24), ("ora", 0.48), ("è", 0.72), ("il", 0.8), ("momento", 0.88), ("di", 1.2), ("provare", 1.36),
            ("questo", 1.92), ("tè", 2.4), ("tradizionale,", 2.8), ("direttamente.", 4.08)]
CUT_141707 = gap_at(C("141707"), 1.70, 2.20)                         # tra "provare" e "questo"
# clip rumorose (strada): tight() non vede le pause, tagli misurati sull'energia e sulle parole riascoltate (27/10 sera)
R_141707 = [(0.1, CUT_141707), (CUT_141707, 3.62), (4.2, 4.9)]       # via la pausa prima di "direttamente"
R_143318 = [(0.4, 2.55), (2.9, 6.4), (8.9, 12.2), (12.75, 17.4)]     # via le pause dopo "domanda" e "dell'India."


def fixw(ws):
    return [(FIXW.get(w, w), t) for w, t in ws]


def vreel(tag):
    W, H = (540, 960) if PREVIEW else (1080, 1920)
    return Reel(f"{OUT}/{tag}_{W}_work", W, H, cx_cam=0.5, amb=0.0), W, H     # B-roll muti (27/10 sera)


def vfinish(r, tag, W, H):
    r.tl.nat_af = "highpass=f=90"                                   # voce pulita: niente letti sotto, niente rombo
    clean_voices(r.tl)
    out = f"{OUT}/VociVere_te_{tag}_{W}x{H}.mp4"
    return r.render(out, crf=18 if W == 1080 else 24, preset="medium" if W == 1080 else "veryfast")


def vhook(r, txt, d=2.2):
    r.title(0.0, d, txt, "Mid", 820)


def mini_sigla(r, W, H):
    """Chiusura del teaser: coda della sigla a tema tè (l'onda che diventa il logo, "Questo è Voci Vere")."""
    sig = Timeline(W, H, f"{OUT}/sigla_v_work")
    sigla_d(sig, OUT, clips=SIGLA_CLIPS, tag="te")
    r.tl._add(sig.shots[-1]["src"], 2.5, 3.5, audio=True, grade="null", fade=0.05)


def v1():
    """TEASER: le colline affittate per 3.000 rupie l'anno; la domanda resta aperta (di chi sono oggi?).
    Solo il girato di chi parla e il voiceover, niente suoni sotto (Manuel 27/10 sera)."""
    r, W, H = vreel("v1_teaser")
    vhook(r, "Affittate per 3.000 rupie\\Nl'anno. Nel 1877.")
    r.cam(C("115233"), 36.5, 39.6, words=fixw(vwords("115233", 36.5, 39.6)), cx=0.5)
    r.narr(C("115233"), 41.4, 47.8, [(r.own(C("133703"), 1.0, cx=0.8), None), (r.own(C("133703"), 4.5, cx=0.62), None)],
           words=fixw(vwords("115233", 41.4, 47.8)))
    r.narr(VO1, 2.0, 5.42, [(r.own(C("115728"), 0.5), None)], words=vwords("", 2.0, 5.42, [dict(words=_WVO)]))
    r.cam(C("120307"), 0.8, 2.95, words=fixw(vwords("120307", 0.8, 2.95)))
    t = r.cam(C("133721"), 10.0, 16.4, speed=1.05, cx=0.55,
              block=[(10.0, 13.6, "Tutte le montagne che vedi sono tè.", "Mountain you see everywhere also tea."),
                     (13.6, 16.4, "Coperte verdi.", "Green blankets.")])
    r.title(r.t - 1.2, r.t + 1.2, "E oggi, di chi sono?", "Mid", 820)   # la domanda entra sulle ultime parole
    r.own(C("114701"), 1.0)(1.2)
    if MUSIC:
        r.tl.music(0, r.t, MUSIC, offset=0.0, level=0.3, fin=0.3, fout=0.5)
    mini_sigla(r, W, H)
    return vfinish(r, "v1_teaser", W, H)


def v2():
    """COME SI RACCOGLIE: Sadish spiega quali foglie si prendono e ogni quanto si torna sulla stessa collina."""
    r, W, H = vreel("v2_raccolta")
    vhook(r, "Si prendono solo\\Ndue, tre foglie.")
    blk = lambda a, b, it, en: r.cam(C("133721"), a, b, speed=1.05, cx=0.55, block=[(a, b, it, en)])
    blk(69.5, 74.6, "Questo è il metodo di raccolta: due, tre foglie.", "This is the plucking method for the two, three leaves.")
    blk(76.0, 80.3, "Due, tre foglie: sono quelle di buona qualità.", "Two three leaves the good quality.")
    blk(81.1, 83.9, "Queste, le buone, vanno in fabbrica.", "Then this leaves good to the factory.")
    blk(85.0, 89.9, "Queste scure, nere, sono cattive. Non si usano.", "This type dark, the black, bad leaves. Not use.")
    blk(57.4, 63.9, "Queste foglie si raccolgono ogni dieci, quindici giorni.", "This leaves maybe ten, fifteen days the plucking.")
    r.cam(C("133721"), 119.5, 131.2, speed=1.05, cx=0.55,
          block=[(119.5, 123.5, "Oggi raccolgo qui, domani vado su un'altra collina.", "Today I will pluck here, tomorrow another mountain."),
                 (124.0, 131.2, "Il mese dopo si torna qui. È un giro.", "Next month come to here. The circle.")])
    r.own(C("135033"), 1.0)(0.5)
    return vfinish(r, "v2_raccolta", W, H)


def v3():
    """UNA GIORNATA DI LAVORO: quanto si raccoglie, l'orario, chi raccoglie (parole di Sadish, riportate)."""
    r, W, H = vreel("v3_giornata")
    vhook(r, "Quanto tè raccoglie\\Nuna persona al giorno?")
    r.cam(C("134520"), 6.2, 11.25, speed=1.05, cx=0.55,
          block=[(6.2, 11.2, "Normalmente, al giorno, una persona raccoglie", "Normally per day people")])
    r.cam(C("134520"), 12.15, 17.6, speed=1.05, cx=0.55,
          block=[(12.2, 16.5, "da ventisei a ventinove chili al giorno.", "Twenty six to twenty-nine kilograms per day."),
                 (17.0, 17.6, "In media.", "Average.")])
    r.cam(C("134520"), 26.8, 30.5, speed=1.05, cx=0.55,
          block=[(26.8, 29.5, "E chi raccoglie di più?", "More than a kilogram people are also plucking?"),
                 (29.6, 30.5, "Soldi in più.", "Extra money.")])
    # Manuel riporta l'orario: in camera a ogni tratto (voce e immagine dello stesso istante), il secondo sui filari
    for i, (a, b) in enumerate(tight(C("134231"), [(0.0, 12.8)])):
        ws = vwords("134231", a, b)
        if i == 1:
            r.narr(C("134231"), a, b, [(r.own(C("133703"), 6.0), None)], words=ws)
        else:
            r.cam(C("134231"), a, b, words=ws)
    r.cam(C("133721"), 107.5, 111.7, speed=1.05, cx=0.55,
          block=[(107.5, 108.4, "Chi raccoglie?", "Who picks?"), (108.4, 111.7, "Tutti: donne e uomini.", "All people, ladies and men.")])
    r.own(C("135922"), 0.3)(0.5)
    return vfinish(r, "v3_giornata", W, H)


def v4():
    """IL CHAI MASTER: il tè tirato a Munnar, il maestro che non vuole parlare (Manuel 27/10 sera: si arriva subito
    lì, poche scene). Il chai si vede mentre se ne parla; Manuel in camera solo con la sua voce dello stesso istante."""
    r, W, H = vreel("v4_chai")
    vhook(r, "Il chai di Munnar\\Nsi fa così.")
    # gancio: il gesto del chai sulla voce di Manuel (141707 è la salita delle scale, lui fuori campo)
    r.narr(C("141707"), R_141707[0][0], R_141707[-1][1], [(r.own(C("142447"), 2.0), None), (r.own(C("142433"), 0.5), None)],
           words=W_141707, cuts=[(R_141707[1][1], R_141707[2][0])])
    r.cam(C("142726"), 43.4, 49.2, speed=1.05,
          block=[(43.4, 46.0, "Lui è il chai master.", ""), (46.3, 49.2, "Io servo.", "")])
    rg = R_143318
    first = [x for x in rg if x[1] <= 6.6]                        # "Ho provato a fare domanda al master... rifiutato."
    r.narr(C("143318"), first[0][0], first[-1][1], [(r.own(C("142545"), 2.0), None), (r.own(C("142447"), 8.0), None)],
           words=W_143318, cuts=[(first[i][1], first[i + 1][0]) for i in range(len(first) - 1)])
    for a, b in rg[len(first):]:                                  # "Forse proprio qua è l'essenza dell'India..."
        r.cam(C("143318"), a, b, words=[w for w in W_143318 if a - 0.1 <= w[1] < b])
    return vfinish(r, "v4_chai", W, H)


if __name__ == "__main__":
    what = [a for a in sys.argv[1:] if not a.startswith("--")] or ["long"]
    W, H = (960, 540) if PREVIEW else (3840, 2160)
    for w in what:
        if w == "long":
            long_video(W, H)
        elif w == "bucato":
            bucato()
        elif w in ("v1", "v2", "v3", "v4"):
            globals()[w]()
