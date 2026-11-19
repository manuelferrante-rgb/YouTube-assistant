#!/usr/bin/env python3
"""Arthunkal RIFATTO DA ZERO (Manuel 17-18/11): lungo 16:9 4K, trailer (verticale e orizzontale), reel ponte, 4 reel.

    python3 projects/arthunkal/rifacimento.py long|trailer|trailer_h [--preview]
Piano: analisi/arthunkal_rifacimento.md (Insights) e copioni/arthunkal_pacchetto.md, "RIFACIMENTO" + "Aggiornamento 18/11"
(Copy: la statua NON è stata filmata, Milano e il 1647 solo nella voce di Manuel e nella linea del tempo). Modello
analisi/competitor/progetto_happiness_mumbai.md. Girato in work/arthunkal/raw (Drive 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX),
trascrizione in work/arthunkal/tr/tutte.json, scelte in projects/arthunkal/girato.md. Nessun voiceover nuovo: si monta solo
con il parlato del girato (Manuel in camera e interviste), la sigla con la frase della missione e la chiusura fissa.
Motore e regole come projects/fortkochi/build.py (Manuel 17/11: camera 1.05x senza pause, B-roll sulle cose dette, zoom
secchi nelle interviste, solo voce pulita, niente B-roll ripetuti, musica originale di Montaggio poca e bassa).
"""
import glob, json, os, subprocess, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, dur_of, ts, FPS
from sigla import sigla_d
from voice_clean import cleaned

PREVIEW = "--preview" in sys.argv
WORK = f"{ROOT}/work/arthunkal"
R = f"{WORK}/raw"
OUT = f"{WORK}/out2"
GFX = f"{WORK}/gfx2"
VOCE = f"{WORK}/voce"
AUD = f"{ROOT}/projects/arthunkal/audio"
CHIUSURA = f"{ROOT}/assets/voce/chiusura_vocivere.m4a"
for d in (OUT, GFX, VOCE):
    os.makedirs(d, exist_ok=True)
DEF = "eq=contrast=1.03:saturation=1.05"
NIGHT = "eq=brightness=0.03:gamma=1.12:contrast=1.04:saturation=1.08"
MUS = 0.075                          # musica sotto la voce: bassa, costante
SUB_K = 1.5                          # sottotitoli delle interviste 1.5 volte più grandi (Manuel 18/11: si guarda dal telefono)


def M23(k):
    m = glob.glob(f"{R}/dji_mimo_20261023_{k}_*")
    assert len(m) == 1, (k, m)
    return m[0]


def C(k):
    """Clip del girato per numero (le 4 cifre nel nome DJI_..._0236_D.MP4)."""
    m = glob.glob(f"{R}/DJI_*_{k}_D.MP4")
    assert len(m) == 1, (k, m)
    return m[0]


# ---------------- voce allo stesso livello (da projects/fortkochi/build.py) ----------------
VOICE_LUFS = -18.0


def _pcm(path, af="anull", ch=1):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", str(ch), "-ar", "48000",
                                         "-af", af, "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)


def _lufs(path, a=None, b=None):
    pre = ["-ss", str(a), "-t", str(b - a)] if a is not None else []
    out = subprocess.run(["ffmpeg", "-hide_banner", *pre, "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(json.loads(out.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def soft_rnn(src, out):
    """Pulizia più leggera per le clip col vento o la folla forte (RNNoise pieno mangia l'inizio delle parole)."""
    from voice_clean import RNN
    cleaned(src, VOCE)
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:a:0", "-ar", "48000", "-af",
         "aformat=channel_layouts=mono,volume=0.5,highpass=f=150,highpass=f=150,afftdn=nf=-25:nr=12,"
         f"atrim=start_sample=1200,asetpts=PTS-STARTPTS,arnndn=m={RNN}:mix=0.6,atrim=start_sample=480,asetpts=PTS-STARTPTS",
         "-c:a", "pcm_s16le", out])
    return out


SOFT = set()                          # clip da pulire più piano (si riempie dopo l'ascolto)


def leveled(src):
    """Solo la voce pulita (RNNoise) a -18 LUFS con guadagno fisso; nelle pause si chiude a -45 dB. Stessi tempi."""
    name = os.path.splitext(os.path.basename(src))[0]
    out = f"{VOCE}/liv_{name}.wav"
    if os.path.exists(out):
        return out
    code = name.split("_")[2]
    cv = soft_rnn(src, f"{VOCE}/soft_{name}.wav") if code in SOFT else cleaned(src, VOCE)
    gv = VOICE_LUFS - _lufs(cv)
    c = _pcm(cv).astype(np.float64)
    n = len(c); hv = 480; mv = n // hv
    dv = 20 * np.log10(np.sqrt((c[:mv * hv].reshape(mv, hv) ** 2).mean(1)) + 1e-9)
    dv = np.convolve(dv, np.ones(5) / 5, mode="same")
    lo, hi = np.percentile(dv, 10), np.percentile(dv, 95)
    on = dv > lo + 0.2 * (hi - lo)
    on = np.convolve(on.astype(float), np.ones(27), mode="full")[6:6 + mv] > 0
    gate = np.where(on, 1.0, 10 ** (-45 / 20))
    gate = np.convolve(gate, np.ones(5) / 5, mode="same")
    gate = np.interp(np.arange(n), (np.arange(mv) + 0.5) * hv, gate)
    y = np.clip(c * gate * 10 ** (gv / 20), -0.98, 0.98).astype(np.float32)
    import soundfile as sf
    sf.write(out, np.stack([y, y], 1), 48000, subtype="PCM_16")
    print(f"voce {name}: {gv:+.1f} dB", flush=True)
    return out


def range_gain(src, a, b, target=-23.0):
    x = _pcm(leveled(src))[int(a * 48000):int(b * 48000)]
    h = 2400
    db = 20 * np.log10(np.sqrt((x[:len(x) // h * h].reshape(-1, h) ** 2).mean(1)) + 1e-9)
    v = db[db > max(db.max() - 20, -50)]
    return float(np.clip(target - np.median(v), 0.0, 10.0)) if len(v) else 0.0


class TL(Timeline):
    def _vf(self, s):
        """Verticali: anche qui lo zoom secco (ritaglio 9:16 più stretto), che il motore fa solo nel 16:9."""
        f = super()._vf(s)
        if self.vertical and s["zoom"] != 1.0:
            z, cx, zy = s["zoom"], s["cx"], s.get("zy", 0.3)
            f = f.replace(f"crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{cx}-ih*9/32))':0",
                          f"crop=ih*9/16/{z}:ih/{z}:'max(0,min(iw-ih*9/16/{z},iw*{cx}-ih*9/32/{z}))':'(ih-ih/{z})*{zy}'", 1)
        return f

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


def tight(src, ranges, min_gap=0.32, keep=0.1):
    v, ok = voiced(src)
    if not ok:
        return ranges
    out = []
    for a, b in ranges:
        i = int(a * 100); cur = a
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


VO_SPEED = 1.05                # Manuel 17/11: camera e voiceover a 1.05x, senza pause né respiri


def piece(name, parts, gap=0.04, speed=VO_SPEED):
    """Voce da un file (chiusura fissa): parts = [(file, [(a, b)])] -> (wav, durata), -18 LUFS, 1.05x."""
    key = abs(hash(json.dumps([parts, gap, speed]))) % 10 ** 8
    out = f"{OUT}/{name}_{key}.wav"
    if not os.path.exists(out):
        (src, rr), = parts
        fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.015,"
                     f"afade=t=out:st={(b - a) - 0.025:.3f}:d=0.025,apad=pad_dur={gap}[p{i}];" for i, (a, b) in enumerate(rr))
        fc += "".join(f"[p{i}]" for i in range(len(rr))) + f"concat=n={len(rr)}:v=0:a=1[o]"
        tmp = out.replace(".wav", "_t.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[o]", "-ac", "1", "-ar", "48000", tmp])
        g = VOICE_LUFS - _lufs(tmp)
        run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={g:.2f}dB,atempo={speed}", "-ac", "1", "-ar", "48000", out])
        os.remove(tmp)
    return out, dur_of(out)


# ---------------- parole di Manuel (sottotitoli parola per parola nei verticali) ----------------
_TR = json.load(open(f"{WORK}/tr/tutte.json"))
FIX = {"Calabur.": "Kalavoor.", "Artun": "Arthunkal.", "Cal.": None, "Carra": "Kerala", "troppusione": "confusione",
       "Gesuita": "gesuita", "Feniscio.": "Fenicio.", "Belluta": "Veluthachan.", "Chan.": None, "S.": None,
       "antico.": "è antico.", "dice": "si dice", "siamo": "si sono", "13-14": "tredici, quattordici", "km": "chilometri",
       "volontar": "Volontari", "Feniscio": "Fenicio", "ricostruita,": "ricostruita"}
OVERRIDE = {   # parole riscritte a mano dove il riconoscimento sbaglia (tempi della voce nella clip)
    "0267": [("Volontari", 1.04), ("induisti", 1.52), ("che", 3.19), ("danno", 3.35), ("la", 3.59), ("loro", 3.75),
             ("mano,", 3.91), ("ma", 4.15), ("tanto", 4.31), ("è", 4.45), ("una", 4.55), ("festa", 4.9), ("cattolica.", 5.48)],
    "0296": [("E", 0.15), ("dopo", 0.35), ("chilometri", 0.65), ("di", 1.15), ("cammino!", 1.35)],
    "0262": [("Chi", 3.16), ("prega,", 3.32), ("chi", 4.18), ("guarda", 4.42), ("dalle", 4.82), ("case,", 5.06), ("chi", 5.38),
             ("offre", 5.54), ("acqua", 5.94), ("e", 6.34), ("chi", 6.58), ("è", 6.82), ("solo", 6.98), ("curioso.", 7.22)],
}


def words_of(src):
    code = os.path.basename(src).split("_")[2]
    if code in OVERRIDE:
        return OVERRIDE[code]
    out = []
    for s in _TR.get(src, []) or _TR.get(os.path.relpath(src, ROOT), []) or \
            next((v for k, v in _TR.items() if k.endswith(os.path.basename(src))), []):
        for w, t in s["words"]:
            w = FIX.get(w, w)
            if w:
                out.append((w, t))
    return out


# ---------------- montaggio ----------------
USED = {}                              # B-roll già usati: niente ripetizioni (Manuel 17/11)


def mark(src, a, d):
    k = os.path.basename(src)
    for a0, d0 in USED.get(k, []):
        if a < a0 + d0 - 0.2 and a0 < a + d - 0.2:
            print(f"ATTENZIONE B-roll ripetuto: {k[:30]} {a:.1f}-{a + d:.1f} (già {a0:.1f}-{a0 + d0:.1f})", flush=True)
    USED.setdefault(k, []).append((a, d))


class Edit:
    def __init__(self, W, H, tag):
        self.tl = TL(W, H, f"{OUT}/{tag}_work")
        self.W, self.H, self.k = W, H, (H / 1080 if W > H else W / 1080)
        self.vertical = H > W
        if not self.vertical:
            self.tl.sub_size = int(52 * self.k * SUB_K)
        self.titles = []               # (t0, t1, stile, testo)
        self.words_ = []               # verticali: parole di Manuel nel montato
        self.cam_speed = VO_SPEED
        self.tags = []                 # verticali: (t0, t1, testo, stile, y) per reel_kit

    @property
    def t(self):
        return self.tl.t

    def b(self, src, a, d, cx=0.5, speed=1.0, zoom=1.0, nat=0.0, grade=DEF, push=True):
        """B-roll: muto sotto la voce; nat > 0 solo nell'apertura e all'arrivo (suono vero, nessuna voce)."""
        mark(src, a, d * speed)
        self.tl.broll(src, a, d, gain=nat, cx=cx, grade=grade, zoom=zoom,
                      fx=dict(zoom=(1.0, 1.035, None)) if push else None, speed=speed, fade=0.12)

    def say(self, src, segs, subs=(), lift=False, zooms=None, grade=DEF, speed=1.0, cut=None, pad=(0.05, 0.1), cx=0.5,
            boost=0.0, words=False):
        """Parlato con la voce pulita della clip. segs = [(a, b) o (a, b, (clip, inizio))]: il terzo elemento copre quel
        tratto con un B-roll (o una grafica) mentre la voce continua. subs (inizio, fine, testo) in tempi della sorgente."""
        D = dur_of(src)
        pieces = []
        for (a, b, *cv) in segs:
            cv = cv[0] if cv else None
            sub = tight(src, [(a, b)], min_gap=cut[0], keep=cut[1]) if cut else [(a, b)]
            off = 0.0
            for m, (p, q) in enumerate(sub):
                p2 = max(0.0, p - (pad[0] if m == 0 else 0.0))
                q2 = min(D - 0.05, q + (pad[1] if m == len(sub) - 1 else 0.0))
                if pieces and pieces[-1][1] > p2 and pieces[-1][0] < p2:
                    p2 = pieces[-1][1]
                pieces.append((p2, q2, cv, off))
                off += (q2 - p2) / speed
        self.tl.audio_map[src] = leveled(src)
        zi = 0
        for a, b, cv, off in pieces:
            t0 = self.t
            g = 10 ** ((range_gain(src, a, b) if lift else 0.0) / 20 + boost / 20)
            if cv:
                if not cv[0].startswith(GFX):
                    mark(cv[0], cv[1] + off, (b - a) / speed)
                fx = None if cv[0].startswith(GFX) else dict(zoom=(1.0, 1.035, None))
                self.tl._add(cv[0], cv[1] + off, (b - a) / speed, gain=0.0, grade="null" if cv[0].startswith(GFX) else DEF,
                             fade=0.05, fx=fx, cx=cx, audio=not cv[0].startswith(GFX))
                self.tl.vos.append(dict(file=src, a=a, b=b, speed=speed, t=t0, lev=True, raw=True, af=f"volume={g:.3f}"))
            else:
                z = zooms[zi % len(zooms)] if zooms else 1.0
                zi += 1
                self.tl.speech(src, [(a, b)], speed=speed, grade=grade, gain=g, zoom=z, cx=cx)
                if z != 1.0:
                    self.tl.shots[-1]["zy"] = 0.3
            for sa, sb, txt in subs:
                lo, hi = max(sa, a), min(sb, b)
                if hi - lo > 0.15:
                    self.tl.subs.append((t0 + (lo - a) / speed, t0 + (hi - a) / speed, txt))
            if self.vertical and words:
                for w, wt in words_of(src):
                    if a - 0.08 <= wt < b - 0.05:
                        self.words_.append((w, t0 + (max(wt, a) + 0.06 - a) / speed))

    def cam(self, src, segs, **kw):
        """Manuel in camera: 1.05x, via pause e respiri, B-roll sulle cose che dice, zoom alternato tra i tagli."""
        kw.setdefault("zooms", [1.0, 1.12])
        self.say(src, segs, speed=self.cam_speed, cut=(0.15, 0.05), pad=(0.05, 0.08), words=True, **kw)

    def gfx(self, path, d=None, audio=False):
        self.tl._add(path, 0, d or dur_of(path), gain=1.0, grade="null", audio=audio)

    def close(self, src, a, cx=0.5, variant="A", grade=DEF):
        """Chiusura dei reel (regola stabile 5/11, tools/reel_close.py): l'ultima persona con "Ascolta altre voci, su",
        il logo 0.8 s dopo sotto il velo, 2 s, fine."""
        from reel_close import logo_card, LOGO_DELAY, LOGO_DUR, CTA, VARIANTS
        t_c = self.t
        self.tl._add(src, a, LOGO_DELAY, gain=0.0, cx=cx, grade=grade, fade=0.05)
        self.gfx(logo_card(OUT, self.W, self.H, LOGO_DUR, src, a + LOGO_DELAY, grade=grade, cx=cx, variant=variant),
                 LOGO_DUR)
        self.tags.append((t_c, self.t, CTA, VARIANTS[variant]["style"], 400))
        return t_c

    def title(self, t0, t1, txt, style="Promessa"):
        self.titles.append((t0, t1, style, txt))

    def ass_v(self):
        """Verticali: sottotitoli del formato dei reel (tools/reel_kit.py): parole di Manuel una per una in oro su fascia
        scura, interviste tradotte a pezzi su una riga, il fatto in alto all'inizio (Tag), la chiusura."""
        from reel_kit import Reel
        r = Reel(self.tl.dir, W=self.W, H=self.H, cap_box=True)
        r.words_ = list(self.words_)
        r.blocks = [(a, b, txt, "") for a, b, txt in self.tl.subs]
        r.titles = list(self.tags)
        stops = [t1 for t0, t1, txt, st, y in self.tags if st in ("TagIn", "TagInB")]
        r.cap_stop = [t0 for t0, t1, txt, st, y in self.tags if st in ("TagIn", "TagInB")]
        return r.ass(self.t)

    def ass(self):
        if self.vertical and (self.words_ or self.tags):
            return self.ass_v()
        k, W, H = self.k, self.W, self.H
        S = lambda v: int(round(v * k))
        sub = self.tl.sub_size
        v = self.vertical
        head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Sub,Poppins Medium,{sub},&H0098D8F2,&H0098D8F2,&H00000000,&H90000000,0,0,0,0,100,100,"
                f"0.5,0,1,{sub / 32:.1f},{sub / 36:.1f},2,{int(W * 0.08)},{int(W * 0.08)},{self.tl.sub_margin},1\n"
                f"Style: Promessa,Anton,{S(135 if v else 120)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,"
                f"2,0,1,{S(2)},{S(5)},{8 if v else 2},{S(60)},{S(60)},{S(330 if v else 150)},1\n"
                f"Style: Luogo,Anton,{S(190 if v else 200)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,"
                f"4,0,1,{S(3)},{S(6)},5,0,0,0,1\n"
                f"Style: Fatto,Anton,{S(100)},&H004B8AB6,&H004B8AB6,&H00FFFFFF,&H00000000,0,0,0,0,100,100,"
                f"2,0,3,{S(18)},0,8,{S(60)},{S(60)},{S(300)},1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        p = f"{self.tl.dir}/scritte.ass"
        with open(p, "w") as f:
            f.write(head)
            for a, b, txt in sorted(self.tl.subs):
                f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{txt}\n")
            for a, b, st, txt in self.titles:
                fx = r"{\fad(350,450)}" if st != "Fatto" else r"{\fad(0,300)}"
                f.write(f"Dialogue: 1,{ts(a)},{ts(b)},{st},,0,0,0,,{fx}{txt}\n")
        return p

    def render(self, out, xin=False):
        self.tl.fix_freezes()
        if xin:
            # dissolvenze solo dentro l'apertura (Manuel 18/11 su fortkochi: tagli netti al posto delle dissolvenze)
            for prev, sh in zip(self.tl.shots, self.tl.shots[1:]):
                if sh.get("open") and prev.get("open") and sh["d"] > 0.6 and prev["d"] > 0.3:
                    sh["xin"] = 0.3
        self.tl.ass_override = self.ass()
        for v in self.tl.vos:
            if v.get("lev"):
                v["file"] = self.tl.audio_map[v["file"]]
        self.tl.nat_af = "highpass=f=90"
        print(f"== {os.path.basename(out)}: {len(self.tl.shots)} inquadrature, {self.t:.1f} s", flush=True)
        if PREVIEW:
            return self.tl.render(out, crf=26, preset="veryfast")
        if not self.vertical:
            self.tl.drop_shots = True
            self.tl.direct_concat = True
            self.tl.shot_crf = 17
            self.tl.final_opts = ["-maxrate", "38M", "-bufsize", "76M"]
        return self.tl.render(out, crf=20 if not self.vertical else 18, preset="medium")


def music(tl, name, t0, t1, offset=0.0, level=MUS, fin=1.0, fout=1.2):
    tl.music(t0, t1, f"{AUD}/ar_{name}.flac", offset=offset, level=level, fin=fin, fout=fout, duck=False, norm=False)
    return offset + (t1 - t0)


def storia(W, H, name, events, dur, prev=""):
    """Linea del tempo stile carta nautica (tools/timeline_anim.py)."""
    out = f"{GFX}/storia_{name}_{dur:.2f}_{W}x{H}.mp4"
    if not os.path.exists(out):
        cmd = ["python3", f"{ROOT}/tools/timeline_anim.py", out, "--events", events, "--dur", f"{dur}",
               "--w", str(W), "--h", str(H)]
        if prev:
            cmd += ["--prev", prev]
        run(cmd)
    return out


def closing_visual(W, H, items, dur, card_at, card_dur):
    """Immagini della chiusura senza volti (schermata finale) in una clip sola, con la scritta finale animata."""
    tag = "_".join(f"{os.path.basename(c)[:28]}{a:.1f}" for c, a in items)
    out = f"{OUT}/chiusura_{abs(hash(tag)) % 10**8}_{dur:.2f}_{card_at:.2f}_{W}x{H}.mp4"
    if os.path.exists(out):
        return out
    # Manuel 19/11: la luce sulla riga "Seguimi per scoprire le prossime storie" parte quando lui dice "Seguimi"
    # (4.69 s nel file della chiusura, che parte da 0.88 a 1.05x: 3.63 s dopo l'inizio della voce = inizio della scritta)
    comet = (4.69 - 0.88) / 1.05
    fr = f"{OUT}/scritta_{W}x{H}_{card_dur:.2f}_c{comet:.2f}"
    if not os.path.exists(f"{fr}/0000.png"):
        run(["python3", f"{ROOT}/tools/scritta_finale.py", fr, "--w", str(W), "--h", str(H), "--dur", f"{card_dur:.2f}",
             "--fadeout", "0.6", "--comet", f"{comet:.2f}"])
    d = dur / len(items)
    ins, fc = [], ""
    for i, (c, a) in enumerate(items):
        mark(c, a, d)
        ins += ["-ss", f"{a:.2f}", "-t", f"{d + 0.5:.2f}", "-i", c]
        fc += (f"[{i}:v]scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=increase,crop={W}:{H},{DEF},fps=30,"
               f"setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=2,trim=duration={d:.3f},setpts=PTS-STARTPTS[v{i}];")
    fc += "".join(f"[v{i}]" for i in range(len(items))) + f"concat=n={len(items)}:v=1:a=0[bg];"
    n = len(items)
    fc += (f"[{n}:v]setpts=PTS-STARTPTS+{card_at:.3f}/TB[ov];[bg][ov]overlay=eof_action=pass:format=auto,"
           f"format=yuv420p[o]")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-framerate", "30", "-i", f"{fr}/%04d.png", "-filter_complex", fc,
         "-map", "[o]", "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "medium", out])
    return out


# ---------------- interviste (tempi in projects/arthunkal/interviste.md, ricontrollati sulla trascrizione 18/11) ----------------
I = dict(lift=True, pad=(0.05, 0.1), zooms=[1.0, 1.15], cut=(0.35, 0.1))   # zoom secco a ogni taglio, via le pause lunghe

# sigla: 8 pezzi del video che non tornano altrove (lampi da 1.2 s sotto la frase della missione)
SIGLA_CLIPS = [(C("0313"), 0.2), (C("0312"), 0.2), (C("0326"), 0.1), (C("0329"), 0.3), (C("0286"), 0.2),
               (C("0310"), 0.4), (C("0322"), 0.3), (C("0289"), 0.4)]


def apertura(e, vertical=False):
    """30-40 s di sole immagini forti con il suono vero e la musica: la notte col rosario, poi l'alba sulla spiaggia, la
    promessa a schermo nei primi secondi, il nome del posto grande. È anche il TRAILER (Manuel 18/11)."""
    tl = e.tl
    t0 = e.t
    cx = {} if not vertical else {"0236": 0.55, "0234": 0.5, "0237": 0.45, "0233": 0.5, "0235": 0.6, "0231": 0.35,
                                    "0246": 0.5, "0264": 0.5, "0283": 0.5, "0263": 0.5, "0243": 0.45}
    shots = [("0236", 0.0, 3.0, NIGHT), ("0234", 0.2, 2.9, NIGHT), ("0237", 0.0, 2.4, NIGHT), ("0233", 0.0, 2.4, NIGHT),
             ("0235", 1.6, 2.4, NIGHT), ("0231", 0.2, 3.0, NIGHT),
             ("0246", 0.0, 3.2, DEF), ("0264", 0.0, 3.0, DEF), ("0283", 1.0, 3.0, DEF), ("0243", 18.3, 2.4, DEF),
             ("0263", 0.0, 4.6, DEF)]
    for k, a, d, gr in shots:
        e.b(C(k), a, d, nat=0.0 if k == "0263" else 0.55, grade=gr, cx=cx.get(k, 0.5))   # 0263: c'è la voce di Manuel
        tl.shots[-1]["open"] = True
    # la promessa nei primi secondi, poi il nome del posto (Copy 18/11)
    e.title(t0 + 0.9, t0 + 5.6, r"MIGLIAIA DI PERSONE,\N13 KM A PIEDI" if vertical else "MIGLIAIA DI PERSONE, 13 KM A PIEDI")
    e.title(t0 + 6.0, t0 + 10.6, "DA MEZZANOTTE ALL'ALBA")
    t_luogo = e.t - 4.6
    e.title(t_luogo + 0.4, e.t - 0.1, r"ARTHUNKAL\N{\fs%d}KERALA, INDIA" % int(90 * e.k), "Luogo")
    music(tl, "apertura", t0, e.t + 0.3, level=0.30, fin=0.8, fout=0.6)
    return t0


def long_video(W, H):
    e = Edit(W, H, "long")
    tl = e.tl
    # 0. APERTURA + SIGLA
    apertura(e)
    t_sigla = sigla_d(tl, OUT, clips=SIGLA_CLIPS, tag="arthunkal", missione=True)
    t_dopo_sigla = e.t

    # 1. LA PROMESSA IN CAMERA: Manuel sulla spiaggia alle sette del mattino (la sua camera guarda la folla)
    E27 = C("0243")
    e.cam(E27, [(0.72, 4.45), (5.0, 7.62), (8.35, 10.1, (C("0264"), 3.4)), (10.8, 12.95, (C("0283"), 7.5)),
                (14.4, 18.3)], zooms=[1.0])
    t_iscr = t_dopo_sigla + 6.0
    E15, E30 = C("0244"), C("0245")
    e.cam(E15, [(1.5, 4.6)])                               # "si parte da un santuario dedicato a Maria a Kalavoor"
    e.cam(E30, [(0.0, 3.6)])                                # "per 13-14 km fino ad Arthunkal"

    # 2. PERCHÉ CAMMINANO: l'organizzatore, Manuel sul cristianesimo antico, i ragazzi (cristiani e musulmani insieme)
    t_perche = e.t
    e.say(C("0240"), [(17.55, 20.4), (21.05, 25.65, (C("0239"), 0.0)), (61.75, 64.45)],
          subs=[(17.55, 20.4, "È una marcia che si fa ogni anno."),
                (21.05, 24.3, "Nasce da un'apparizione di Maria,"), (24.3, 25.65, "qui ad Alappuzha."),
                (61.75, 64.45, "Partecipano circa quattrocentomila persone.")], **I)
    e.cam(C("0254"), [(0.75, 2.8), (5.3, 9.05), (9.75, 11.0)])     # "In Kerala il cristianesimo è antico... 52 d.C."
    e.say(C("0247"), [(10.0, 13.25)], subs=[(10.0, 13.25, "È come una preghiera a Gesù, il mio amore.")], **I)
    e.say(C("0249"), [(0.05, 2.2), (6.75, 10.4), (11.0, 12.25)],
          subs=[(0.05, 2.2, "Perché tornate ogni anno?"), (6.75, 10.4, "Per la Madre, Maria."),
                (11.0, 12.25, "Veniamo sempre.")], **I)
    e.say(C("0250"), [(0.0, 1.8), (2.3, 3.4), (4.0, 7.2)],
          subs=[(0.0, 1.8, "Ci sono cristiani..."), (2.3, 3.4, "Sì."), (4.0, 5.0, "Musulmani."),
                (5.0, 7.2, "Sì. Tutti insieme.")], **I)

    # 3. CHI NON CAMMINA: cibo e acqua gratis, volontari anche induisti (verso il minuto 2)
    t_cibo = e.t
    e.b(C("0269"), 0.0, 2.2)
    m_cibo = e.t - 2.2
    e.cam(C("0255"), [(4.1, 5.6), (6.9, 9.6)], zooms=[1.0])        # "una comunità intera che... da bere e da mangiare"
    e.cam(C("0262"), [(3.05, 3.8), (4.2, 5.4), (5.4, 6.4, (C("0271"), 0.0)), (6.4, 7.8)], zooms=[1.0])
    e.cam(C("0265"), [(1.35, 4.05)], zooms=[1.0])                   # "volontari e volontarie devoti alla causa"
    e.cam(C("0267"), [(0.95, 2.15), (3.1, 6.1)], zooms=[1.0])        # "volontari induisti che danno la loro mano..."
    e.b(C("0260"), 0.0, 1.5)
    e.cam(C("0268"), [(0.55, 2.95)], zooms=[1.0])                   # "davvero una comunità riunita"
    e.cam(C("0274"), [(2.6, 6.05)], zooms=[1.0])                    # "una sosta per bere e mangiare qualcosino"
    music(tl, "cammino", m_cibo - 0.3, e.t + 0.2, fin=0.8, fout=0.8)

    # 4. IN CAMMINO CON LORO: Manuel si unisce, la strada, Elizabeth, la pellegrina ("lì succedono tanti miracoli")
    t_cammino = e.t
    e.cam(C("0270"), [(0.0, 3.3), (5.15, 6.35)])                   # "Proviamo per un pezzettino ad unirci a loro..."
    t_m2 = e.t
    e.b(C("0282"), 0.3, 2.0)
    e.b(C("0277"), 0.2, 2.2)
    e.cam(C("0276"), [(0.45, 2.65), (3.3, 6.2, (C("0285"), 0.8)), (6.2, 8.6)])   # prima in strada, col traffico, ora in spiaggia
    e.b(C("0284"), 0.0, 2.4)
    off = music(tl, "cammino", t_m2 - 0.3, e.t + 0.2, offset=14.0, fin=0.6, fout=0.8)
    e.say(C("0261"), [(11.75, 15.05), (18.3, 21.4, (C("0258"), 17.0))],
          subs=[(11.75, 15.05, "È un atto di devozione alla Madonna."),
                (18.3, 21.4, "Mi ha dato tante benedizioni nella vita.")], **I)
    e.say(C("0261"), [(30.65, 31.5), (32.3, 33.15)], subs=[(30.65, 31.5, "Ho ventisei anni."),
                                                          (32.3, 33.15, "È la prima volta qui.")], **I)
    e.b(C("0279"), 0.3, 2.0)
    music(tl, "cammino", e.t - 2.3, e.t + 0.1, offset=off + 3.0, fin=0.5, fout=0.6)
    t_like = e.t
    e.say(C("0281"), [(30.75, 32.2), (33.0, 33.7), (38.0, 39.5), (40.1, 41.75), (43.35, 44.75)],
          subs=[(30.75, 32.2, "È la prima volta per te?"), (33.0, 33.7, "No."),
                (38.0, 39.5, "Abbiamo camminato sulla spiaggia."), (40.1, 41.75, "E ora siamo in strada."),
                (43.35, 44.75, "Che cosa significa per te?")], **I)
    e.say(C("0281"), [(45.6, 49.2), (51.2, 55.4, (C("0283"), 10.5)), (55.85, 57.1)], boost=7.0,       # lei è lontana dal microfono
          subs=[(45.6, 47.0, "È fede, è credere."),
                (47.2, 49.2, "Lì succedono tanti miracoli."), (51.2, 55.4, "Chi partecipa ci trova qualcosa."),
                (55.85, 57.1, "Un po' di felicità.")], **I)

    # 5. L'ARRIVO E LA BASILICA (verso i due terzi): la storia, 1584 e 1647 (Milano in scritta nella linea del tempo)
    t_arrivo = e.t
    e.cam(C("0296"), [(0.0, 1.95)], zooms=[1.0])                     # "E dopo chilometri di cammino!"
    e.b(C("0296"), 2.4, 3.6, nat=0.35)
    e.b(C("0297"), 0.2, 2.6, nat=0.35)
    e.b(C("0302"), 0.0, 3.2, nat=0.35)
    e.b(C("0299"), 0.5, 3.0, nat=0.35)
    t_ig = e.t - 2.8
    e.b(C("0308"), 0.8, 3.0, nat=0.35)
    music(tl, "storia", t_arrivo + 1.8, e.t + 0.2, level=0.16, fin=1.0, fout=0.6)
    t_storia = e.t
    s1 = storia(W, H, "1584", "1584|padre Giacomo Fenicio|gesuita italiano, ricostruisce la chiesa|0.5", 7.0)
    s2 = storia(W, H, "1647", "1647|San Sebastiano|una statua arrivata da Milano|0.6", 6.0, prev="1584")
    e.cam(C("0316"), [(1.55, 2.75), (2.75, 5.95, (s1, 0.0)), (8.95, 10.6, (s1, 3.1)), (14.6, 16.55, (C("0306"), 0.9))])
    e.cam(C("0320"), [(0.4, 2.25), (2.65, 6.6, (s2, 0.0)), (7.0, 8.4, (C("0307"), 0.0))])
    e.b(C("0305"), 0.0, 3.0)
    e.b(C("0309"), 15.0, 3.0)
    music(tl, "storia", t_storia - 0.2, e.t + 0.2, offset=t_storia - t_arrivo - 2.0, level=MUS, fin=0.4, fout=1.0)

    # 6. CHIUSURA: immagini senza volti per gli ultimi 15 s (schermata finale), la frase fissa di Manuel
    # TODO voiceover di chiusura da chiedere a Manuel (riflessione finale): per ora solo la chiusura fissa
    e.cam(C("0325"), [(0.55, 1.6), (2.25, 3.3)])                    # "Fa caldissimo. Un sacco umido."
    t_tuk = e.t
    e.b(C("0330"), 0.3, 3.6)                                      # il ritorno in tuk-tuk con le signore
    t_fine = e.t
    e.b(C("0314"), 0.0, 3.0)                                      # la folla di spalle che va via
    e.b(C("0331"), 0.0, 3.0)
    f_ch, d_ch = piece("chiusura", [(CHIUSURA, [(0.88, 6.80)])])
    lead, after = 0.4, 6.0
    t_c0 = e.t
    tl.vos.append(dict(file=f_ch, a=0, b=d_ch, speed=1.0, t=t_c0 + lead, raw=True))
    dur = lead + d_ch + after
    items = [(M23("140234"), 1.0), (C("0224"), 20.0), (M23("140104"), 0.0)]   # la spiaggia vuota il giorno prima
    tl._add(closing_visual(W, H, items, dur, lead, dur - lead), 0, dur, audio=False, grade="null")
    music(tl, "finale", t_tuk - 0.2, e.t, level=0.12, fin=0.6, fout=1.5)

    chapters = [(0.0, "Da mezzanotte all'alba", "From midnight to dawn"),
                (t_dopo_sigla, "13 km a piedi", "13 km on foot"),
                (t_perche, "Perché camminano", "Why they walk"),
                (t_cibo, "Chi non cammina", "Those who don't walk"),
                (t_cammino, "In cammino con loro", "Walking with them"),
                (t_arrivo, "La basilica", "The basilica"),
                (t_fine, "Chiusura", "Closing")]
    out = f"{OUT}/VociVere_arthunkal_long_{W}x{H}.mp4"
    json.dump(dict(chapters=chapters, t_sigla=t_sigla, t_dopo_sigla=t_dopo_sigla, t_iscr=t_iscr, t_like=t_like, t_ig=t_ig,
                   total=e.t), open(f"{OUT}/long_{W}x{H}.json", "w"), indent=1)
    e.render(out)
    return out


def trailer(W, H):
    """Il TRAILER = l'apertura del lungo + la sigla (Manuel 18/11): verticale (Short/Reel) e orizzontale (WhatsApp, storie)."""
    vertical = H > W
    e = Edit(W, H, f"trailer_{W}x{H}")
    apertura(e, vertical=vertical)
    sigla_d(e.tl, OUT, clips=SIGLA_CLIPS, tag="arthunkal", missione=True)
    out = f"{OUT}/VociVere_arthunkal_trailer_{W}x{H}.mp4"
    e.render(out)
    return out


# ================= VERTICALI (Manuel 18/11: Manuel in camera, movimento, una sola scritta in alto all'inizio, veloci) =================
RS = 1.12                              # Manuel in camera nei reel: più svelto del lungo
RB = 1.25                              # B-roll nei reel: velocizzati


def reel_edit(tag):
    e = Edit(1080, 1920, tag)
    e.cam_speed = RS
    return e


def fact(e, txt, d=3.2):
    """Il fatto in alto dal primo fotogramma (Insights 17/11), oro su bianco."""
    e.tags.append((0.0, d, txt, "Tag", 430))


def reel_music(e, name, t0, t1, level=0.10, offset=0.0):
    music(e.tl, name, t0, t1, offset=offset, level=level, fin=0.4, fout=0.8)


def reel_13km():
    e = reel_edit("r13km")
    fact(e, "13 KM A PIEDI")
    e.b(C("0236"), 3.0, 1.6, nat=0.5, grade=NIGHT, speed=1.0)       # la folla di notte col rosario, dal primo fotogramma
    e.b(C("0234"), 3.1, 0.9, nat=0.5, grade=NIGHT)
    e.b(C("0237"), 2.4, 0.9, nat=0.5, grade=NIGHT, cx=0.45)
    t_m = e.t
    E27 = C("0243")
    e.cam(E27, [(0.72, 2.6), (2.6, 4.45, (C("0231"), 4.0)), (5.0, 7.62), (8.35, 10.1, (C("0264"), 6.0)),
                (10.8, 12.95, (C("0258"), 2.0))], cx=0.45)
    e.tl.shots[-4]["grade"] = NIGHT
    e.cam(C("0244"), [(1.5, 4.6)], cx=0.4)
    e.cam(C("0245"), [(0.0, 3.6)], cx=0.4)
    e.cam(C("0270"), [(0.0, 3.3)], cx=0.45)
    e.b(C("0282"), 1.0, 1.0, speed=RB)
    e.b(C("0279"), 2.3, 1.1, speed=RB)
    e.b(C("0283"), 4.5, 1.2, speed=RB)
    reel_music(e, "cammino", t_m - 0.2, e.t + 2.8)
    e.close(C("0284"), 0.5, variant="A")
    return e


def reel_cibo():
    e = reel_edit("rcibo")
    fact(e, "CIBO GRATIS")
    e.b(C("0235"), 0.0, 1.5, nat=0.5, grade=NIGHT, cx=0.6)           # le mani sulla pentola, di notte
    e.b(C("0231"), 7.0, 1.6, nat=0.5, grade=NIGHT, cx=0.4)
    t_m = e.t
    e.cam(C("0255"), [(4.1, 5.6), (6.9, 9.6)])
    e.cam(C("0262"), [(3.05, 3.8), (4.2, 7.8)])
    e.cam(C("0265"), [(1.35, 4.05)], cx=0.55)
    e.cam(C("0267"), [(0.95, 2.15), (3.1, 6.1)], cx=0.5)
    e.cam(C("0268"), [(0.55, 2.95)])
    e.cam(C("0274"), [(2.6, 6.05)])
    reel_music(e, "cammino", t_m - 0.2, e.t + 2.8, offset=20.0)
    e.close(C("0274"), 6.1, variant="B")
    return e


def reel_pellegrina():
    e = reel_edit("rpell")
    fact(e, "«TANTI MIRACOLI»")
    E = C("0281")
    e.b(E, 6.3, 1.4, cx=0.6, nat=0.5)                              # lei che cammina tra la folla
    e.cam(C("0243"), [(5.0, 7.62)], cx=0.45)                       # "Tredici chilometri lungo la costa del Kerala"
    t_m = e.t
    e.say(E, [(30.75, 32.2), (33.0, 33.7), (38.0, 39.5), (40.1, 41.75), (43.35, 44.75)], speed=1.05, lift=True,
          pad=(0.05, 0.1), cut=(0.3, 0.08), cx=0.55, zooms=[1.0, 1.25],
          subs=[(30.75, 32.2, "È la prima volta per te?"), (33.0, 33.7, "No."),
                (38.0, 39.5, "Abbiamo camminato sulla spiaggia."), (40.1, 41.75, "E ora siamo in strada."),
                (43.35, 44.75, "Che cosa significa per te?")])
    e.say(E, [(45.6, 49.2), (51.2, 55.4), (55.85, 57.1)], speed=1.05, lift=True, boost=7.0, pad=(0.05, 0.1),
          cut=(0.3, 0.08), cx=0.55, zooms=[1.25, 1.0],
          subs=[(45.6, 47.0, "È fede, è credere."), (47.2, 49.2, "Lì succedono tanti miracoli."),
                (51.2, 55.4, "Chi partecipa ci trova qualcosa."), (55.85, 57.1, "Un po' di felicità.")])
    reel_music(e, "storia", t_m - 0.2, e.t + 2.8, level=0.07)
    e.close(E, 57.2, cx=0.55, variant="A")
    return e


def reel_insieme():
    e = reel_edit("rinsieme")
    fact(e, "TUTTI INSIEME")
    e.say(C("0250"), [(0.0, 1.8), (2.3, 3.4), (4.0, 7.2)], speed=1.05, lift=True, pad=(0.05, 0.1), cx=0.6, zooms=[1.0, 1.25],
          subs=[(0.0, 1.8, "Ci sono cristiani..."), (2.3, 3.4, "Sì."), (4.0, 5.0, "Musulmani."),
                (5.0, 7.2, "Sì. Tutti insieme.")])
    t_m = e.t
    e.cam(C("0254"), [(0.75, 2.8), (5.3, 9.05), (9.75, 11.0)])
    e.say(C("0240"), [(21.05, 25.65), (61.75, 64.45)], speed=1.05, lift=True, pad=(0.05, 0.1), cx=0.55, zooms=[1.0, 1.25],
          subs=[(21.05, 24.3, "Nasce da un'apparizione di Maria,"), (24.3, 25.65, "qui ad Alappuzha."),
                (61.75, 64.45, "Partecipano circa quattrocentomila persone.")])
    e.say(C("0247"), [(10.0, 13.25)], speed=1.05, lift=True, cx=0.6,
          subs=[(10.0, 13.25, "È come una preghiera a Gesù, il mio amore.")])
    e.say(C("0249"), [(0.05, 2.2), (6.75, 10.4), (11.0, 12.25)], speed=1.05, lift=True, cx=0.6, zooms=[1.25, 1.0],
          subs=[(0.05, 2.2, "Perché tornate ogni anno?"), (6.75, 10.4, "Per la Madre, Maria."),
                (11.0, 12.25, "Veniamo sempre.")])
    reel_music(e, "cammino", t_m - 0.2, e.t + 2.8, level=0.07, offset=8.0)
    e.close(C("0249"), 12.3, cx=0.6, variant="B")
    return e


def space_clip():
    """Discesa dallo spazio su Arthunkal (tools/space_zoom.py, 9.6611 N 76.3008 E), con il suono del movimento."""
    out = f"{GFX}/spazio_arthunkal.mp4"
    if os.path.exists(out):
        return out
    import soundfile as sf
    n_fr = len(glob.glob(f"{WORK}/sz/*.png"))
    T = n_fr / 30
    SR = 48000
    rng = np.random.default_rng(3)
    n = int(T * SR); t = np.arange(n) / SR; tp = T - 0.27
    w = rng.standard_normal((n, 2))
    X = np.fft.rfft(w, axis=0); f = np.fft.rfftfreq(n, 1 / SR)[:, None]
    P = X / np.sqrt(np.maximum(f, 20))                                 # rumore rosa, poi due bande
    lo = np.fft.irfft(P * (1 / (1 + (f / 900) ** 4)), n, axis=0)
    hi = np.fft.irfft(P * ((f / 900) ** 2 / (1 + (f / 900) ** 2)) / (1 + (f / 6000) ** 4), n, axis=0)
    u = np.clip(t / tp, 0, 1) ** 1.8
    env = np.where(t < tp, 0.3 + 0.7 * u, np.exp(-(t - tp) / 0.16))[:, None]
    y = (lo / np.abs(lo).max() * (1 - 0.6 * u[:, None]) + hi / np.abs(hi).max() * u[:, None]) * env
    sub = np.sin(2 * np.pi * (38 + 30 * u) * t) * np.where(t < tp, 0.2 + 0.8 * u ** 2, np.exp(-(t - tp) / 0.14))
    y += 0.35 * sub[:, None]
    y = y / np.abs(y).max() * 0.7
    wav = f"{GFX}/spazio_arthunkal.wav"
    sf.write(wav, y.astype(np.float32), SR)
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{WORK}/sz/%04d.png", "-i", wav, "-c:v", "libx264",
         "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-shortest", out])
    return out


def reel_ponte():
    """Reel PONTE (una curiosità che porta al lungo). Manuel 18/11: la discesa dallo spazio resta di Munnar, qui qualcosa
    di simile ma non quello: AVVICINAMENTO A SCATTI alla basilica da terra (da lontano, più vicino, la facciata con le mani
    alzate), un colpo d'aria a ogni stacco, poi Manuel con la storia del gesuita italiano."""
    from sfx import sfx_file
    e = reel_edit("rponte")
    fact(e, "UN ITALIANO, 1584", d=3.6)
    steps = [("0298", 0.0, 0.75, 0.5), ("0297", 1.2, 0.75, 0.52), ("0308", 0.6, 0.8, 0.5), ("0302", 0.4, 1.9, 0.5)]
    for i, (k, a, d, cx) in enumerate(steps):
        t = e.t
        mark(C(k), a, d)
        e.tl._add(C(k), a, d, gain=0.45, cx=cx, grade=DEF, fade=0.03,
                  fx=dict(zoom=(1.0, 1.22 if i < 3 else 1.06, None), **({"flash": 0.1} if i else {})))
        if i:
            e.tl.sfx(max(0.0, t - 0.25), sfx_file("whoosh_short"), 0.35)
    e.tl.sfx(e.t - 1.9, sfx_file("hit"), 0.22)
    s1 = storia(1080, 1920, "1584v", "1584|padre Giacomo Fenicio|gesuita italiano, ricostruisce la chiesa|0.4", 6.0)
    s2 = storia(1080, 1920, "1647v", "1647|San Sebastiano|una statua arrivata da Milano|0.5", 5.0, prev="1584")
    t_m = e.t
    e.cam(C("0316"), [(1.55, 2.75, (C("0305"), 0.3)), (2.75, 5.95), (8.95, 10.6, (s1, 1.0)), (14.6, 16.55, (C("0306"), 0.2))],
          cx=0.45)
    e.cam(C("0320"), [(0.4, 2.25), (2.65, 6.6, (s2, 0.0)), (7.0, 8.4, (C("0308"), 4.5))], cx=0.45)
    reel_music(e, "storia", t_m - 0.2, e.t + 2.8, level=0.08, offset=10.0)
    e.close(C("0299"), 9.0, variant="A")
    return e


REELS = {"r13km": reel_13km, "rcibo": reel_cibo, "rpell": reel_pellegrina, "rinsieme": reel_insieme, "rponte": reel_ponte}


if __name__ == "__main__":
    what = [a for a in sys.argv[1:] if not a.startswith("--")] or ["long"]
    W, H = (1920, 1080) if PREVIEW else (3840, 2160)
    for w in what:
        if w == "long":
            long_video(W, H)
        elif w == "trailer_h":
            trailer(1920, 1080)
        elif w == "trailer":
            trailer(1080, 1920)
        elif w in REELS:
            e = REELS[w]()
            e.render(f"{OUT}/VociVere_arthunkal_{w}_1080x1920.mp4")
