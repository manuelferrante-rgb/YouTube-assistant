#!/usr/bin/env python3
"""Arthunkal (Kreupasanam Akhanda Japamala, 24/10): lungo 16:9 e 4 verticali.

    python3 projects/arthunkal/build.py long|v1|v2|v3|v4 [--preview]
Girato in work/arthunkal/raw (cartella Drive 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX), voiceover in work/arthunkal/vo.
Decisioni di Manuel in projects/arthunkal/brief.md, blocchi del voiceover in vo_blocchi.md.
"""
import glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, dur_of, ts
from sigla import sigla_d

PREVIEW = "--preview" in sys.argv
W_ = os.path.join
WORK = f"{ROOT}/work/arthunkal"
R = f"{WORK}/raw"
OUT = f"{WORK}/out"
GFX = f"{WORK}/gfx"
AUD = f"{ROOT}/projects/arthunkal/audio"          # suoni e musica forniti dalla chat Audio
VO1, VO2 = f"{WORK}/vo/vo_take1.m4a", f"{WORK}/vo/vo_take2.m4a"
os.makedirs(OUT, exist_ok=True); os.makedirs(GFX, exist_ok=True)

MUSIC = next(iter(glob.glob(f"{WORK}/musica_orig/musica_voiceover.wav")), None)   # musica originale (chat Audio)
MUSIC_V = next(iter(glob.glob(f"{WORK}/musica_orig/musica_verticali.wav")), None)
NIGHT = "eq=brightness=0.03:gamma=1.12:contrast=1.04:saturation=1.08"
DEF = "eq=contrast=1.03:saturation=1.05"


def C(tag):
    """Clip del 24/10 per ora di ripresa HHMMSS."""
    m = glob.glob(f"{R}/DJI_20261024{tag}_*")
    assert len(m) == 1, (tag, m)
    return m[0]


D23 = f"{R}/DJI_20261023140536_0224_D.MP4"          # Manuel sulla spiaggia vuota, 23/10


def M23(tag):
    return f"{R}/dji_mimo_20261023_{tag}.mp4"


# ---------- parlato nelle clip: per non sovrapporre mai due voci ----------
_SEG = {}
for jf in (f"{WORK}/trans24.json", f"{WORK}/raw/trans.json"):
    if os.path.exists(jf):
        for k, v in json.load(open(jf)).items():
            _SEG[os.path.basename(k)] = v


def has_voice(src, a, b):
    """C'è parlato vero in [a, b]? (le parole isolate come "Yeah", "Uh" sono quasi sempre rumore di folla)"""
    return any(s["start"] < b and s["end"] > a and len(s.get("words", [])) >= 2 and s["end"] - s["start"] >= 0.8
               for s in _SEG.get(os.path.basename(src), []))


def piece(name, src, ranges, speed=1.1, gap=0.2):
    """Voce da uno o più tratti di un file, uniti con respiri di `gap` s e accelerata. -> (file, durata)."""
    out = f"{OUT}/{name}.wav"
    if not os.path.exists(out):
        fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={speed},aresample=48000,"
                     f"afade=t=in:d=0.03,afade=t=out:st={(b - a) / speed - 0.05:.3f}:d=0.05,apad=pad_dur={gap}[p{i}];"
                     for i, (a, b) in enumerate(ranges))
        tot = sum((b - a) / speed + gap for a, b in ranges) - gap
        fc += "".join(f"[p{i}]" for i in range(len(ranges))) + f"concat=n={len(ranges)}:v=0:a=1,atrim=end={tot:.3f}[o]"
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[o]", "-ac", "1", "-ar", "48000", out])
    return out, dur_of(out)


def ambient(src, a, d, name=None):
    out = f"{OUT}/amb_{os.path.basename(src)[:30]}_{a:.2f}_{d:.2f}.wav"
    if not os.path.exists(out):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, a):.3f}", "-t", f"{d:.3f}", "-i", src, "-vn", "-ac", "2",
             "-ar", "48000", "-af", f"afade=t=in:d=0.15,afade=t=out:st={max(0, d - 0.25):.3f}:d=0.25", out])
    return out


def aud(name, fallback=None):
    """Suono della chat Audio se c'è, altrimenti il ripiego (suono vero del girato)."""
    for ext in ("wav", "mp3", "m4a"):
        p = f"{AUD}/{name}.{ext}"
        if os.path.exists(p):
            return p
    return fallback


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

    def b(self, src, a, d, gain=0.35, cx=0.5, grade=DEF, fx=None, speed=1.0, bed=None):
        """B-roll con il suo suono vero. Se nella clip c'è parlato l'audio si azzera e sotto va un letto d'ambiente
        vero preso da una clip senza voci (bed = (clip, inizio)), così non resta mai un buco di silenzio."""
        if gain and has_voice(src, a, a + d * speed):
            gain = 0.0
            b_src, b_a = bed or (C("085422"), 0.0)
            self.tl.sfx(self.t, ambient(b_src, b_a, d + 0.3), 0.32)
        self.tl.broll(src, a, d, gain=gain, cx=cx, grade=grade, fx=fx or dict(zoom=(1.0, 1.04, None)), speed=speed,
                      fade=0.12)

    def say(self, src, ranges, speed=1.1, cx=0.5, cover=None, subs=(), grade=DEF):
        """Parlato in camera tagliato sulle pause; cover = {indice: (clip, a, gain)} copre quel tratto con un'altra
        immagine mentre la voce continua (salti di montaggio nascosti). subs in tempi della sorgente."""
        cover = cover or {}
        for i, (a, b) in enumerate(ranges):
            t0 = self.t
            if i in cover:
                src2, a2 = cover[i][:2]
                g = src2.startswith(GFX)                     # grafiche: senza audio né correzione colore
                self.tl._add(src2, a2, (b - a) / speed, gain=0.0, grade="null" if g else grade, fade=0.05,
                             audio=not g, fx=None if g else dict(zoom=(1.0, 1.04, None)))
                self.tl.vos.append(dict(file=src, a=a, b=b, speed=speed, t=t0))
            else:
                self.tl.speech(src, [(a, b)], speed=speed, cx=cx, grade=grade)
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
        t_end = self.t
        snd = aud("transizione_nero_in", ambient(M23("140234"), 9.2, 0.9))
        self.tl.sfx(max(0, t_end - dur_of(snd)), snd, 0.55)            # il taglio del suono cade sul primo nero
        self.tl._add(self.black, 0, gap, audio=False, grade="null")
        self.strong = strong

    def from_black(self):
        """Inizio scena dal nero: l'ultima inquadratura aggiunta rientra dal nero allargandosi; il suo suono
        parte mezzo secondo prima dell'immagine (J-cut)."""
        sh = self.tl.shots[-1]
        sh["fx"] = dict(black_in=0.35, zoom=(1.08, 1.0, 0.8))
        self.tl.sfx(max(0, sh["t"] - 0.45), ambient(sh["src"], sh["a"] - 0.45, 0.6), 0.35 if sh["gain"] else 0.0)
        snd = aud("transizione_nero_out")
        if snd and getattr(self, "strong", False):                      # solo nei 2-3 cambi forti
            self.tl.sfx(sh["t"], snd, 0.45)
        self.strong = False

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

    def render(self, out):
        self.tl.ass_override = self.ass()
        print(f"== {os.path.basename(out)}: {len(self.tl.shots)} inquadrature, {self.t:.1f} s", flush=True)
        if PREVIEW:
            return self.tl.render(out, crf=26, preset="veryfast")
        return self.tl.render(out, crf=17, preset="medium")


# ---------- grafiche (stile carta nautica, approvate da Manuel) ----------
ROUTE = "Kalavoor|9.55|76.307|santuario di Kreupasanam;Marari|9.62646|76.296;Arthunkal|9.6611|76.3008|basilica di Sant'Andrea"


def mappa(W, H, tA, tB, tkm, dur):
    tag = f"mappa_{tA:.2f}_{tB:.2f}_{tkm:.2f}_{dur:.2f}"
    out = f"{GFX}/{tag}_{W}x{H}.mp4"
    if not os.path.exists(out):
        run(["python3", f"{ROOT}/tools/route_map.py", out, "--route", ROUTE, "--km", "13", "--t-a", f"{tA}",
             "--t-b", f"{tB}", "--t-km", f"{tkm}", "--dur", f"{dur}", "--w", str(W), "--h", str(H)])
    snd = f"{GFX}/{tag}.wav"
    if not os.path.exists(snd):
        run(["python3", f"{ROOT}/projects/arthunkal/map_sfx.py", snd, "--t-a", f"{tA}", "--t-b", f"{tB}",
             "--t-km", f"{tkm}", "--dur", f"{dur}"])
    return out, snd


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
def VO(name, ranges, src=VO1):
    return piece(f"vo_{name}", src, ranges)


# ================= LUNGO =================
def long_video(W, H):
    """Lungo v2 (25/10, Manuel lo vuole più lungo): tutto il girato utile, ~7-8 minuti, niente riempitivi."""
    e = Edit(W, H, "long")
    tl = e.tl

    # 1. GANCIO: la spiaggia piena all'alba, la sua voce; raffica dei momenti più forti; poi i numeri
    e.say(C("072327"), [(0.75, 4.45)], cx=0.5)                     # "Sono le sette del mattino... da mezzanotte."
    tl.sfx(e.t - 0.2, ambient(C("072504"), 0.0, 6.4), 0.45)         # letto di folla sotto la raffica
    for src, a, d, g, gr in [(C("091255"), 0.35, 1.3, 0.5, DEF), (C("075747"), 1.0, 1.0, 0.0, DEF),
                             (C("023744"), 0.3, 1.1, 0.4, NIGHT), (C("075231"), 2.0, 1.0, 0.4, DEF),
                             (C("090733"), 4.0, 1.4, 0.5, DEF)]:
        e.b(src, a, d, gain=g, grade=gr, fx=dict(zoom=(1.06, 1.0, 0.4)))
    e.say(C("072327"), [(5.0, 7.6), (8.4, 10.1)], cover={1: (C("072504"), 0.2)})   # 13 km... senza mai fermarsi
    # anello aperto col legame italiano (Insights): la statua arrivata da Milano, sciolto nella parte sulla storia
    e.say(C("091658"), [(21.0, 24.25)], subs=[(21.0, 24.25, "arrivò da Milano una statua di San Sebastiano.")],
          cover={0: (C("091255"), 0.9)})
    tl.sfx(max(0, e.t - 0.4), ambient(C("072504"), 0.5, 2.0), 0.45)   # ponte sonoro sull'attacco della sigla
    # 2. SIGLA
    sigla_d(tl, OUT if not PREVIEW else f"{OUT}/sigla_prev")

    # 3. LA MAPPA sul blocco 2 (pausa tolta tra "Arthunkal" e "Tredici")
    f, d = VO("2", [(16.2, 19.25), (19.75, 24.85), (25.75, 29.3)])
    lead = 1.4                                                       # "Si chiama Akhanda Japamala" sul rosario
    t0 = e.t
    tl.vos.append(dict(file=f, a=0, b=d, speed=1.0, t=t0))
    tl.sfx(max(0, t0 - 0.6), ambient(C("072504"), 1.0, lead + 1.0), 0.3)   # ponte sull'uscita della sigla
    e.b(C("075747"), 1.2, lead, gain=0.0)
    e.label("Kreupasanam Akhanda Japamala", t0 + 0.1, 2.4)
    tA, tB, tkm = 5.12 - lead, 6.80 - lead, 7.86 - lead + 0.3
    mdur = round(9.16 - lead + 0.55, 2)
    mp, msnd = mappa(W, H, round(tA, 2), round(tB, 2), round(tkm, 2), mdur)
    tm = e.t
    tl._add(mp, 0, mdur, audio=False, grade="null")
    tl.sfx(tm, msnd, 0.8)
    tl.sfx(tm, ambient(C("072327"), 13.0, mdur), 0.18)
    e.b(C("072504"), 0.0, max(1.6, t0 + d + 0.3 - e.t))              # "...e la preghiera non si ferma mai"

    # 4. IL GIORNO PRIMA: la costa vuota, il santuarietto con le ghirlande, le sue parole sul posto
    t_prima = e.t
    e.say(M23("140912"), [(0.8, 3.45)])                               # "Sono lungo la costa dell'oceano Indiano, in Kerala."
    e.label("Marari, il giorno prima", t_prima + 0.3, 2.6)
    e.b(M23("140234"), 0.5, 2.6, gain=0.6)
    e.say(D23, [(7.8, 11.75), (13.3, 14.85), (17.7, 18.65), (20.25, 22.45), (28.4, 30.85), (31.65, 33.3),
                (35.2, 36.1), (37.1, 38.2)],
          cover={1: (M23("140104"), 0.3), 3: (M23("140912"), 3.5), 4: (M23("140104"), 2.2), 6: (M23("140234"), 11.0)})
    e.b(M23("141012"), 0.0, 3.4, gain=0.6)                           # ghirlande, barche a secco
    e.say(M23("140626"), [(0.8, 2.5), (3.5, 4.5), (5.15, 6.2), (7.25, 8.75), (11.2, 13.2), (14.1, 16.1), (17.75, 19.7)],
          cover={2: (M23("140234"), 14.0), 3: (M23("141012"), 3.4), 5: (D23, 1.5)},
          subs=[(7.25, 8.75, "alla Beata Vergine.")])
    f, d = VO("1c", [(9.6, 12.45)])                                  # "Nessuno avrebbe detto che di notte..."
    e.vo(f, d, [(M23("140234"), 5.5), (D23, 39.0)], lead=0.4, tail=0.6)
    e.to_black(strong=True)

    # 5. 2:30 DI NOTTE: niente voce, solo il suono vero; poi il blocco 3 e il jolly b
    t_n = e.t
    e.b(C("023744"), 0.0, 3.8, gain=0.8, grade=NIGHT)
    e.from_black()
    e.title("2:30 di notte", t_n + 0.5, 3.6)
    e.label("Lungo la costa, 2:30 di notte", t_n + 4.6, 2.6)
    e.b(C("023529"), 0.0, 2.6, gain=0.8, grade=NIGHT)
    e.b(C("023356"), 0.3, 3.0, gain=0.8, grade=NIGHT)            # solo suono vero: mai oltre ~10 s di fila
    f, d = VO("3", [(31.8, 34.5), (34.9, 40.2)])
    e.vo(f, d, [(C("023818"), 0.0, .5, NIGHT), (C("023628"), 0.3, .5, NIGHT), (C("023510"), 0.0, .5, NIGHT),
                (C("023356"), 5.5, .5, NIGHT)],
         lead=0.3, tail=0.4)
    f, d = VO("jb", [(190.75, 193.65)])
    e.vo(f, d, [(C("023744"), 2.0, .5, NIGHT), (C("023529"), 2.0, .5, NIGHT)], lead=0.4, tail=0.6)
    e.b(C("023356"), 8.0, 3.0, gain=0.8, grade=NIGHT)
    e.b(C("023744"), 2.2, 2.4, gain=0.8, grade=NIGHT)
    e.to_black()

    # 6. L'ALBA SULLA SPIAGGIA
    t_a = e.t
    e.b(C("072327"), 13.0, 2.4, gain=0.7)
    e.from_black()
    e.label("Sulla spiaggia, 7 del mattino", t_a + 0.4, 2.6)
    tl.sfx(t_a, ambient(C("072504"), 0.0, 3.4), 0.45)               # la spiaggia all'alba: passi e voci lontane
    e.say(C("072327"), [(10.8, 12.95), (14.4, 15.95), (16.7, 18.3)], cover={1: (C("072504"), 1.0), 2: (C("072504"), 2.6)})
    e.say(C("072415"), [(0.3, 4.6)])                                 # "Come ci hanno raccontato si parte... Kalavoor"
    e.say(C("072430"), [(0.0, 3.6)])                                 # "Per 13-14 km fino ad Arthunkal."
    e.b(C("072504"), 0.0, 3.0, gain=0.6)
    e.b(C("072327"), 18.6, 2.2, gain=0.6)
    e.say(C("075209"), [(0.5, 3.15), (3.8, 5.1)])                    # "Siamo a Marari... da qui passa il cammino"
    e.say(C("080217"), [(0.5, 2.6), (3.4, 8.55)], cover={1: (C("080133"), 0.5)})   # prima in strada, poi in spiaggia
    e.say(C("080133"), [(0.6, 2.35)], cover={0: (C("072504"), 1.4)})              # "e lì si riprende sulla spiaggia"

    # 7. CHI CAMMINA: il blocco 8 sui volti, poi la domanda una volta sola e le risposte
    t_c = e.t
    f, d = VO("8b", [(134.6, 140.55)])
    e.vo(f, d, [(C("085345"), 0.0), (C("074032"), 9.0), (C("090348"), 0.5), (C("085613"), 0.0)], lead=0.3, music=0.0)
    e.say(C("071857"), [(15.85, 17.15)], subs=[(15.85, 17.15, "Che cosa significa per te?")])
    e.say(C("071857"), [(17.55, 20.4), (21.05, 25.7), (55.8, 59.7), (61.9, 64.45)], speed=1.0,
          cover={2: (C("072504"), 0.0)},
          subs=[(17.55, 20.4, "È una marcia che si fa ogni anno."),
                (21.05, 25.7, "Nasce da un'apparizione di Maria, qui ad Alappuzha."),
                (55.8, 59.7, "Ottobre è il mese di Maria: lo dedichiamo a questa marcia."),
                (61.9, 64.45, "Partecipano circa quattrocentomila persone.")])
    e.b(C("074032"), 17.5, 2.6, gain=0.5, bed=(C("085422"), 2.0))
    e.say(C("074350"), [(12.2, 14.95), (18.35, 21.3), (21.8, 23.1), (30.6, 31.6), (32.3, 33.1)], speed=1.0,
          subs=[(12.2, 14.95, "È un atto di devozione alla Madonna."),
                (18.35, 21.3, "Mi ha dato tante benedizioni nella vita."),
                (21.8, 23.1, "Attraverso Gesù Cristo."), (30.6, 31.6, "Ho ventisei anni."),
                (32.3, 33.1, "È la prima volta qui.")])
    e.b(C("085345"), 1.5, 2.5, gain=0.5)
    e.say(C("085034"), [(30.75, 32.2), (33.0, 33.7), (45.5, 51.0), (51.4, 57.3)], speed=1.0,
          subs=[(30.75, 32.2, "È la prima volta per te?"), (33.0, 33.7, "No."),
                (45.5, 48.2, "È fede, è credere."), (48.2, 51.0, "Lì succedono tanti miracoli."),
                (51.4, 55.9, "Chi partecipa ci trova qualcosa."), (55.9, 57.3, "Un po' di felicità.")])
    e.to_black()

    # 8. CHI NON CAMMINA: cibo, acqua, volontari (anche induisti), l'ambulanza
    t_o = e.t
    e.b(C("073357"), 0.3, 2.4, gain=0.7)
    e.from_black()
    f, d = VO("5", [(62.4, 71.75)])
    e.vo(f, d, [(C("074113"), 0.0), (C("075956"), 0.0), (C("080046"), 0.0), (C("023356"), 1.0, .5, NIGHT),
                (C("075826"), 0.2)], lead=0.2, music=25.0)
    e.say(C("075124"), [(3.1, 7.75)])
    e.b(C("073357"), 6.0, 3.0, gain=0.7, bed=(C("085208"), 1.0))
    e.say(C("080133"), [(2.6, 6.05)])                                # "Questa è stata una sosta interna per bere e mangiare"
    e.say(C("075419"), [(1.4, 4.0)])
    e.say(C("075747"), [(1.0, 6.1)])
    e.say(C("075441"), [(1.2, 2.6)], subs=[(1.2, 2.6, "Sta arrivando l'ambulanza.")])
    e.b(C("075441"), 3.0, 3.0, gain=0.6, bed=(C("085208"), 5.0))
    e.say(C("075826"), [(0.6, 2.9)])

    # 9. IN STRADA VERSO ARTHUNKAL
    t_s = e.t
    e.say(C("080017"), [(0.0, 3.3), (5.1, 6.4)])                      # "Proviamo per un pezzettino ad unirci a loro"
    f, d = VO("ja", [(186.9, 189.2)])
    e.vo(f, d, [(C("083552"), 0.2), (C("085153"), 0.3)], lead=0.3, tail=0.3)
    tl.sfx(e.t, ambient(C("085422"), 0.0, 8.0), 0.3)                # letto di strada sotto la sequenza
    tl.sfx(e.t + 8.0, ambient(C("085345"), 0.0, 9.0), 0.3)
    for src, a, dd in [(C("084510"), 0.5, 2.6), (C("085208"), 0.5, 2.4), (C("085422"), 1.0, 3.0),
                       (C("090224"), 0.5, 2.2)]:                    # niente camminate ripetute (Insights)
        e.b(src, a, dd, gain=0.6)
    f, d = VO("jc", [(195.55, 197.55)])
    e.vo(f, d, [(C("085613"), 0.3), (C("090348"), 2.0)], lead=0.3, tail=0.4)
    e.to_black(strong=True)

    # 10. L'ARRIVO: la basilica, il suono vero della folla e degli altoparlanti
    t_r = e.t
    e.b(C("090733"), 0.0, 6.8, gain=0.75)
    e.from_black()
    tl.subs.append((t_r + 0.05, t_r + 1.9, "E dopo chilometri di cammino!"))   # audio coperto dalla folla
    e.label("Basilica di Arthunkal", t_r + 3.8, 2.8)
    for src, a, dd in [(C("090813"), 0.0, 3.0), (C("090903"), 0.5, 4.5), (C("091255"), 0.9, 2.3),
                       (C("090951"), 0.0, 2.0), (C("091540"), 1.0, 4.0), (C("091405"), 0.0, 3.0),
                       (C("091505"), 0.0, 1.5), (C("090903"), 8.5, 4.5), (C("090813"), 0.5, 2.5)]:
        e.b(src, a, dd, gain=0.6)

    # 11. LA STORIA: 52 d.C. (voiceover), poi Manuel davanti alla basilica con la linea del tempo
    f, d = VO("6a", [(81.0, 88.2)])
    sA = storia(W, H, "A", "52 d.C.|San Tommaso|secondo la tradizione|1.45", 3.6)
    t6 = e.t
    tl.vos.append(dict(file=f, a=0, b=d, speed=1.0, t=t6 + 0.2))
    e.b(C("091453"), 0.0, 2.0, gain=0.25)
    e.b(C("090825"), 0.0, 0.9, gain=0.25)
    t_sa = e.t
    tl._add(sA, 0, (t6 + 0.2 + d + 0.35) - e.t, audio=False, grade="null")
    tl.sfx(t_sa, ambient(C("091540"), 4.0, e.t - t_sa + 0.2), 0.15)
    sB = storia(W, H, "B", "1584|padre Giacomo Fenicio|gesuita italiano, ricostruisce la chiesa|0.55", 6.0, prev="52 d.C.")
    sC = storia(W, H, "C", "1647|la statua di San Sebastiano|arriva da Milano|0.4", 4.9, prev="52 d.C.;1584")
    subs = [(0.0, 3.2, "Questa chiesa l'ha ricostruita nel 1584"), (4.6, 9.6, "un gesuita italiano, padre Giacomo Fenicio."),
            (12.5, 15.2, "Qui lo chiamano ancora Veluthachan,"), (15.2, 18.3, "il padre bianco."),
            (19.0, 21.0, "Nel 1647"), (21.0, 24.2, "arrivò da Milano una statua di San Sebastiano.")]
    e.say(C("091658"), [(0.0, 1.6), (1.6, 3.2), (4.6, 9.6), (12.5, 18.3), (19.0, 24.2)],
          cover={1: (sB, 0.0), 2: (sB, 1.45), 4: (sC, 0.0)}, subs=subs)
    f, d = VO("7b", [(109.25, 115.05)])
    e.vo(f, d, [(C("091540"), 3.0), (C("091405"), 0.5), (C("090903"), 8.0)], lead=0.3, tail=0.5, music=60.0)
    e.to_black(strong=True)

    # 12. IL RITORNO (immagini in ordine di ripresa), poi il blocco 10 e il claim di Manuel
    t_f = e.t
    e.b(C("091748"), 0.0, 3.4, gain=0.6)
    e.from_black()
    for src, a, dd in [(C("092013"), 0.0, 1.4), (C("092151"), 0.0, 1.6), (C("092219"), 0.0, 3.0),
                       (C("093848"), 0.5, 3.6)]:
        e.b(src, a, dd, gain=0.6)
    e.say(C("094735"), [(0.55, 1.5), (2.25, 3.2), (4.9, 6.2)])     # "Fa caldissimo. Un sacco umido. Si sente un sacco."
    tl.sfx(e.t, ambient(C("085208"), 9.0, 1.7), 0.3)                # la clip del bus fermo è quasi muta
    e.b(C("094640"), 0.0, 1.4, gain=0.6, bed=(C("085208"), 9.0))
    e.b(C("101618"), 0.0, 5.5, gain=0.7, bed=(C("101821"), 0.0))
    f, d = VO("10", [(162.3, 164.65), (166.4, 173.3), (174.15, 182.45)], src=VO1)
    e.vo(f, d, [(C("092756"), 0.0), (C("094758"), 0.0), (C("095400"), 0.0), (C("095653"), 0.0),
                (C("095730"), 0.0), (C("101821"), 0.0)], lead=0.6, tail=0.8, music=90.0)
    e.say(C("093832"), [(0.45, 2.75), (3.6, 5.95)])
    tl.shots[-1]["fx"] = dict(black_out=0.25)

    chapters = [(0.0, "Prima dell'alba"), (t_prima, "Il giorno prima"), (t_n, "2:30 di notte"),
                (t_a, "L'alba sulla spiaggia"), (t_c, "Chi cammina"), (t_o, "Chi non cammina"),
                (t_s, "In strada"), (t_r, "L'arrivo ad Arthunkal"), (t6, "La storia"), (t_f, "Il ritorno")]
    ml = aud("musica_voiceover_lungo")                              # musica già a misura dalla chat Audio
    if ml:
        tl.musics = [dict(t0=0.0, t1=tl.t, track=ml, offset=0.0, level=0.42, fin=0.05, fout=0.5)]
    out = f"{OUT}/VociVere_arthunkal_long_{W}x{H}.mp4"
    with open(f"{OUT}/voiceover_{W}x{H}.txt", "w") as fh:          # inizio e fine dei soli voiceover (per la musica)
        for v in tl.vos:
            if os.path.basename(v["file"]).startswith("vo_"):
                fh.write(f"{v['t']:.2f}\t{v['t'] + (v['b'] - v['a']) / v['speed']:.2f}\t{os.path.basename(v['file'])}\n")
    e.render(out)
    with open(f"{OUT}/capitoli_{W}x{H}.txt", "w") as fh:
        for t, n in chapters:
            fh.write(f"{int(t // 60)}:{int(t % 60):02d} {n}\n")
    return out


if __name__ == "__main__":
    what = [a for a in sys.argv[1:] if not a.startswith("--")] or ["long"]
    W, H = (960, 540) if PREVIEW else (3840, 2160)
    for w in what:
        if w == "long":
            long_video(W, H)


# ================= VERTICALI (9:16, regole in fondo a regole/montaggio_documentario.md) =================
from reel_kit import Reel, brush_in

_W24 = json.load(open(f"{WORK}/trans24.json")) if os.path.exists(f"{WORK}/trans24.json") else {}
_WVO = json.load(open(f"{WORK}/vo/vo_take1.json")) if os.path.exists(f"{WORK}/vo/vo_take1.json") else {}
FIX = {"Carra": "Kerala", "Artunkal": "Arthunkal", "Artunkal.": "Arthunkal.", "Artunkal,": "Arthunkal,",
       "d.C.": "dopo Cristo.", "Calavor": "Kalavoor,", "Akanda": "Akhanda", "Giapamala,": "Japamala,",
       "l'Apostolo": "l'apostolo", "antico.": "è antico."}


def words(src_json, key_part, a, b):
    """Parole (testo corretto, tempo) di una clip o del voiceover nell'intervallo [a, b)."""
    out = []
    for k, segs in src_json.items():
        if key_part in os.path.basename(k):
            for s in segs:
                out += [(FIX.get(w, w), t) for w, t in s["words"] if a - 0.05 <= t < b]
    return out


W_BASILICA = [("Questa", 0.0), ("chiesa", 0.51), ("l'ha", 1.01), ("ricostruita", 1.22), ("nel", 2.03), ("1584", 2.33),
              ("un", 4.76), ("gesuita", 5.07), ("italiano,", 5.98), ("padre", 7.2), ("Giacomo", 7.91), ("Fenicio.", 8.72),
              ("Qui", 12.67), ("lo", 13.07), ("chiamano", 13.28), ("ancora", 14.09), ("Veluthachan,", 15.61),
              ("il", 17.23), ("padre", 17.33), ("bianco.", 17.84), ("Nel", 19.15), ("1647", 19.46), ("arrivò", 21.18),
              ("da", 21.69), ("Milano", 21.89), ("una", 22.4), ("statua", 22.6), ("di", 23.11), ("San", 23.21),
              ("Sebastiano.", 23.51)]


def vreel(tag):
    W, H = (540, 960) if PREVIEW else (1080, 1920)
    return Reel(f"{OUT}/{tag}_{W}_work", W, H, cx_cam=0.5), W, H


def vfinish(r, tag, W, H):
    base = r.render(f"{OUT}/{tag}_base_{W}x{H}.mp4", crf=18 if W == 1080 else 24,
                    preset="medium" if W == 1080 else "veryfast")
    out = f"{OUT}/VociVere_arthunkal_{tag}_{W}x{H}.mp4"
    brush_in(base, out, dur=0.27)
    return out


def hook(r, txt, d=2.2):
    r.title(0.0, d, txt, "Mid", 820)
    hit = aud("transizione_nero_out")                               # colpo basso fatto con un'onda vera (chat Audio)
    if hit:
        r.tl.sfx(0.0, hit, 0.35)


def v1():
    """TEASER (prima del lungo): la notte, il cammino, nessun arrivo. Chiude su "Perché?"."""
    r, W, H = vreel("v1_teaser")
    tl = r.tl
    r.own(C("023744"), 0.0, gain=0.8, grade=NIGHT)(2.2)
    hook(r, "2:30 di notte.\\NTutti in cammino.")
    t = r.t
    r.own(C("023356"), 0.5, gain=0.8, grade=NIGHT)(1.8)
    r.own(C("023628"), 0.6, gain=0.8, grade=NIGHT)(1.5)
    r.title(t + 0.2, t + 3.2, "Costa del Kerala, India", "Small", 400)
    t = r.narr(VO1, 31.7, 39.9, [(r.own(C("023818"), 0.0, gain=0.0, grade=NIGHT), None),
                                 (r.own(C("023529"), 0.2, gain=0.0, grade=NIGHT), None),
                                 (r.own(C("023510"), 0.0, gain=0.0, grade=NIGHT), None)],
               words=words(_WVO, "", 31.7, 39.9), cuts=[(34.3, 34.7), (38.4, 39.25)])
    r.title(t + 0.3, t + 2.8, "Pregano camminando", "Small", 400)
    if MUSIC_V:
        tl.music(0, r.t, MUSIC_V, offset=0.0, level=0.5, fin=0.3, fout=0.8)
    # la sua voce all'alba sopra la folla sulla spiaggia (nella clip la camera guarda il cielo)
    r.narr(C("072327"), 0.75, 4.45, [(r.own(C("072504"), 0.0, gain=0.0), None)],
           words=words(_W24, "072327", 0.75, 4.45))
    r.narr(C("072327"), 5.0, 10.1, [(r.own(C("075231"), 1.0, gain=0.0), None), (r.own(C("072504"), 1.6, gain=0.0), None)],
           words=words(_W24, "072327", 5.0, 10.1), cuts=[(7.6, 8.35)])
    t = r.t
    r.own(C("085345"), 0.0, gain=0.6)(1.8)
    r.own(C("075231"), 6.0, gain=0.6)(1.4)
    r.title(t + 1.0, r.t, "Perché?", "Mid", 820)
    if MUSIC_V:
        tl.music(t - 0.2, r.t, MUSIC_V, offset=30.0, level=0.45, fin=0.4, fout=0.5)
    return vfinish(r, "v1_teaser", W, H)


def v2():
    """LA STATUA DI MILANO: 52 d.C., il gesuita italiano, il padre bianco, la statua del 1647."""
    r, W, H = vreel("v2_statua")
    r.own(C("091255"), 0.9, gain=0.5)(2.2)
    hook(r, "Scolpita a Milano.\\NNel 1647.")
    t = r.narr(VO1, 81.0, 88.2, [(r.own(C("090825"), 0.0, gain=0.25, cx=0.5), 2.0), (r.own(C("091540"), 1.0, gain=0.25), None)],
               words=words(_WVO, "", 81.0, 88.2), cuts=[(83.0, 83.45)])
    r.title(t + 0.2, t + 2.6, "Arthunkal, Kerala, India", "Small", 400)
    sB = storia(W, H, "Bv", "1584|padre Giacomo Fenicio|gesuita italiano|0.2", 4.5, prev="52 d.C.")
    sC = storia(W, H, "Cv", "1647|la statua di San Sebastiano|arriva da Milano|0.3", 5.0, prev="1584")
    sp = r.SP
    src = C("091658")
    r.narr(src, 0.0, 24.2, [(r.own(src, 0.0, speed=sp, gain=0.0), 3.2 / sp), (r.gen(sB), 5.0 / sp),
                            (r.own(src, 12.5, speed=sp, gain=0.0), 5.8 / sp), (r.gen(sC), None)],
           words=W_BASILICA, cuts=[(3.2, 4.6), (9.6, 12.5), (18.3, 19.0)])
    r.narr(VO1, 109.25, 115.05, [(r.own(C("091540"), 3.0, gain=0.2), None), (r.own(C("091405"), 0.5, gain=0.2), None),
                                 (r.own(C("090903"), 8.0, gain=0.2), None)],
           words=words(_WVO, "", 109.25, 115.05))
    r.own(C("090825"), 0.0, gain=0.4)(1.5)
    if MUSIC_V:
        r.tl.music(0, r.t, MUSIC_V, offset=0.0, level=0.35, fin=0.3, fout=0.8)
    return vfinish(r, "v2_statua", W, H)


def v3():
    """UNA PERSONA: una pellegrina risponde a "che cosa significa per te?"."""
    r, W, H = vreel("v3_persona")
    src = C("085034")
    r.own(C("085345"), 0.0, gain=0.6)(2.1)
    hook(r, "13 km a piedi,\\Ndi notte.")
    r.narr(C("072327"), 0.75, 7.6, [(r.own(C("072504"), 0.0, gain=0.0), None), (r.own(C("075231"), 1.0, gain=0.0), None)],
           words=words(_W24, "072327", 0.75, 7.6), cuts=[(4.45, 5.0)])
    t = r.cam(src, 30.75, 33.7, speed=1.05, cx=0.68,
              block=[(30.8, 32.1, "È la prima volta per te?", "For you is the first time?"), (33.1, 33.7, "No.", "No.")])
    r.title(t, t + 2.6, "Arthunkal, Kerala", "Small", 300)
    r.cam(src, 43.4, 44.85, speed=1.05, cx=0.68, block=[(43.45, 44.85, "Che cosa significa per te?", "What does it mean for you?")])
    r.cam(src, 45.7, 57.0, speed=1.05, cx=0.68,
          block=[(45.75, 47.0, "È fede, è credere.", "This is a faith and belief."),
                 (47.35, 49.3, "Lì succedono tanti miracoli.", "There are so many miracles happening there."),
                 (51.3, 55.5, "Chi partecipa ci trova qualcosa.", "Those who are taking part in this, they have something in that."),
                 (56.0, 57.0, "Un po' di felicità.", "Some happiness.")])
    return vfinish(r, "v3_persona", W, H)


def v4():
    """COME FUNZIONA: il nome, la mappa, la spiaggia al posto della strada, la notte, chi aiuta, il 2002."""
    r, W, H = vreel("v4_come_funziona")
    sp = r.SP
    r.own(C("072504"), 0.0, gain=0.6)(2.2)
    hook(r, "13 km pregando.\\NSenza mai smettere.")
    lead = 1.4
    seg = [(16.2, 19.25), (19.75, 24.85), (25.75, 29.3)]

    def out_t(x):
        t, acc = 0.0, 0.0
        for a, b in seg:
            if x < b:
                return acc + (x - a) / sp
            acc += (b - a) / sp
        return acc
    tA, tB, tkm = out_t(22.12) - lead, out_t(23.96) - lead, out_t(25.8) - lead + 0.3
    mdur = round(out_t(27.24) - lead + 0.6, 2)
    mp, msnd = mappa(W, H, round(tA, 2), round(tB, 2), round(tkm, 2), mdur)
    t0 = r.narr(VO1, 16.2, 29.3, [(r.own(C("075747"), 1.2, gain=0.0), lead), (r.gen(mp), None)],
                words=words(_WVO, "", 16.2, 29.3), cuts=[(19.25, 19.75), (24.85, 25.75)])
    r.tl.sfx(t0 + lead, msnd, 0.8)
    r.cam(C("080217"), 0.5, 2.6, words=words(_W24, "080217", 0.5, 2.6))
    r.cam(C("080217"), 3.4, 8.55, words=words(_W24, "080217", 3.4, 8.55))
    t = r.t
    r.own(C("023744"), 0.0, gain=0.8, grade=NIGHT)(2.0)
    r.own(C("023356"), 0.5, gain=0.8, grade=NIGHT)(1.6)
    r.title(t + 0.2, r.t, "Si parte di notte", "Small", 400)
    r.narr(VO1, 62.4, 71.75, [(r.own(C("073357"), 0.3, gain=0.0), None), (r.own(C("075956"), 0.0, gain=0.0), None),
                              (r.own(C("080046"), 0.0, gain=0.0), None)],
           words=words(_WVO, "", 62.4, 71.75))
    r.narr(C("075747"), 1.0, 6.1, [(r.own(C("075747"), 1.0, speed=sp, gain=0.0), None)],
           words=words(_W24, "075747", 1.0, 6.1))
    r.narr(C("072327"), 10.8, 18.3, [(r.own(C("072504"), 2.6, gain=0.0), None), (r.own(C("085345"), 0.0, gain=0.0), None)],
           words=words(_W24, "072327", 10.8, 18.3), cuts=[(12.95, 14.4)])
    r.own(C("075231"), 2.0, gain=0.6)(2.0)
    if MUSIC_V:
        r.tl.music(0, r.t, MUSIC_V, offset=10.0, level=0.3, fin=0.3, fout=0.8)
    return vfinish(r, "v4_come_funziona", W, H)


if __name__ == "__main__":
    for w in [a for a in sys.argv[1:] if not a.startswith("--")]:
        if w in ("v1", "v2", "v3", "v4"):
            globals()[w]()
