#!/usr/bin/env python3
"""Reel "Comunismo in Kerala" (9:16): voce di Manuel a 1.2x, B-roll suo alternato a grafiche animate,
Manuel in camera ogni tanto, sottotitoli animati parola per parola, titoli animati, pochi effetti sonori.

    python3 projects/comunismo/build.py [--preview]
Girato in work/comunismo/raw (cartella Drive "Comunismo in Kerala"), stock Pixabay in work/comunismo/stock.
"""
import glob, os, subprocess, sys
import numpy as np, cv2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, ts
from sfx import sfx_file

W, H = (540, 960) if "--preview" in sys.argv else (1080, 1920)
K = W / 1080
R = f"{ROOT}/work/comunismo/raw"
STOCK = f"{ROOT}/work/comunismo/stock"
GFX = f"{ROOT}/work/comunismo/gfx"
OUT = f"{ROOT}/work/comunismo/out"
os.makedirs(GFX, exist_ok=True); os.makedirs(OUT, exist_ok=True)
SP = 1.2           # voce di Manuel (richiesta: 1.15-1.2x)
GAP = 0.08         # respiro tra le frasi
AMB = 0.12         # suono d'ambiente del B-roll sotto la voce
CX_M = 0.47        # Manuel nel ritaglio verticale


def clip(tag):
    """Clip dall'orario nel nome (es. 120520): solo il campo dell'orario, non i numeri lunghi dopo."""
    m = glob.glob(f"{R}/dji_mimo_20261022_{tag}_*") or glob.glob(f"{R}/*{tag}*")
    assert len(m) == 1, (tag, m)
    return m[0]


FLAG_REAL = clip("IMG_8420")
SEGNI, HOUSEBOAT, CANALE, STRADA = (clip(t) for t in ("105538", "110018", "111734", "111828"))
OLD_FILM = ("hue=s=0,eq=contrast=1.25:brightness='-0.05+0.04*random(1)':eval=frame,"
            "noise=alls=24:allf=t+u,vignette=PI/4")


# ---------- grafiche ----------


def flag(kind):
    p = f"{GFX}/flag_{kind}_fill_{W}.mp4"
    if not os.path.exists(p):
        run(["python3", f"{ROOT}/tools/flag_anim.py", p, "--kind", kind, "--w", str(W), "--h", str(H), "--dur", "4",
             "--fill"])
    return p


def kerala_map():
    p = f"{GFX}/map_kerala_{W}.mp4"
    if not os.path.exists(p):
        run(["python3", f"{ROOT}/tools/map_anim.py", p, "--lat", "10.2", "--lon", "76.4", "--name", "Kerala",
             "--w", str(W), "--h", str(H), "--zoomscale", "0.6", "--dur", "3.4"])
    return p


def card(img, name, dur=2.0):
    """Foto in una scheda al centro, sfondo sfocato, leggero avvicinamento."""
    p = f"{GFX}/card_{name}_{W}.mp4"
    if os.path.exists(p):
        return p
    im = cv2.imread(img).astype(np.float32) / 255
    bg = cv2.resize(im, (int(H * im.shape[1] / im.shape[0]), H))
    x0 = (bg.shape[1] - W) // 2
    bg = cv2.GaussianBlur(bg[:, x0:x0 + W], (0, 0), 30 * K) * 0.4
    cw = int(W * 0.9); ch = int(cw * im.shape[0] / im.shape[1])
    cy = H // 2
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", p],
                            stdin=subprocess.PIPE)
    n = int(dur * 30)
    for f in range(n):
        z = 1.0 + 0.06 * f / n
        sw, sh = int(cw * z), int(ch * z)
        big = cv2.resize(im, (sw, sh), interpolation=cv2.INTER_AREA)
        crop = big[(sh - ch) // 2:(sh - ch) // 2 + ch, (sw - cw) // 2:(sw - cw) // 2 + cw]
        fr = bg.copy()
        y0, x0c = cy - ch // 2, (W - cw) // 2
        sh_off = int(14 * K)
        fr[y0 + sh_off:y0 + ch + sh_off, x0c + sh_off:x0c + cw + sh_off] *= 0.35   # ombra
        fr[y0:y0 + ch, x0c:x0c + cw] = crop
        proc.stdin.write((np.clip(fr, 0, 1) * 255).astype(np.uint8).tobytes())
    proc.stdin.close(); proc.wait()
    return p


# ---------- montaggio ----------
tl = Timeline(W, H, f"{OUT}/reel_{W}_work")
WORDS = []      # (parola, tempo nel montato)
TITLES = []     # (inizio, fine, testo, stile, y)


def out_t(t0, a, t_src):
    return t0 + (t_src + 0.06 - a) / SP


def words(t0, a, ws):
    for w, t in ws:
        WORDS.append((w, out_t(t0, a, t)))


def own(src, a, cx=0.5, speed=1.0, grade=None, fx=None, gain=AMB):
    def f(d):
        kw = dict(grade=grade) if grade else {}
        tl._add(src, a, d * speed, speed=speed, gain=gain, cx=cx, fade=0.05, fx=fx, **kw)
    return f


def gen(src, a=0.0, speed=1.0, grade="null", fx=None):
    def f(d):
        tl._add(src, a, d * speed, speed=speed, grade=grade, audio=False, fx=fx)
    return f


def narr(src, a, b, visuals):
    """Voce di Manuel (da una sua clip) sopra immagini: visuals = [(funzione, durata o None)]."""
    t0 = tl.t
    total = (b - a) / SP + GAP
    tl.vos.append(dict(file=src, a=a, b=b, speed=SP, t=t0))
    fixed = sum(d for _, d in visuals if d)
    rest = max(0.2, total - fixed) / max(1, sum(1 for _, d in visuals if not d))
    for fn, d in visuals:
        fn(d or rest)
    return t0


def cam(src, a, b, fx=None):
    """Manuel in camera, labiale in sincrono."""
    t0 = tl.t
    tl.speech(src, [(a, b)], speed=SP, cx=CX_M, fx=fx or dict(zoom=(1.06, 1.0, 0.3)))
    return t0


# 1. gancio: bandiere rosse vere, poi la bandiera animata
a, b = 2.10, 5.55
t0 = narr(clip("120352"), a, b, [(own(FLAG_REAL, 0.0, speed=0.78, fx=dict(zoom=(1.12, 1.0, 0.35))), 1.6),
                                  (gen(flag("ldf"), 0.3, fx=dict(zoom=(1.0, 1.06, None))), None)])
tl.sfx(0.0, sfx_file("boom"), 0.3)
words(t0, a, [("Sapevi", 2.07), ("che", 2.63), ("l'India", 2.79), ("ha", 3.27), ("perso", 3.43), ("il", 3.75),
              ("suo", 3.91), ("ultimo", 4.07), ("governo", 4.39), ("comunista?", 4.79)])

# 2. Manuel in camera
a, b = 0.65, 2.95
t0 = cam(clip("120436"), a, b)
words(t0, a, [("Sono", 0.61), ("in", 0.93), ("Kerala", 1.01), ("ed", 1.57), ("è", 1.81), ("successo", 1.89),
              ("proprio", 2.37), ("qui.", 2.53)])

# 3. 1957: il passato in pellicola, poi la bandiera che prende colore su "governo comunista"
a, b = 0.50, 5.10
tl.sfx(max(0, tl.t - 0.5), sfx_file("whoosh_rev"), 0.18)
t_gov = (3.42 - a) / SP
t0 = narr(clip("120508"), a, b, [(own(HOUSEBOAT, 0.5, grade=OLD_FILM, fx=dict(zoom=(1.0, 1.05, None)), gain=0.06), t_gov),
                                  (gen(flag("ldf"), 1.0, grade="hue=s='clip((t-0.15)/0.45,0,1)'"), None)])
words(t0, a, [("Nel", 0.46), ("1957", 0.78), ("il", 1.98), ("Kerala", 2.14), ("elesse", 2.78), ("un", 3.34),
              ("governo", 3.42), ("comunista", 3.82), ("con", 4.30), ("il", 4.54), ("voto.", 4.62)])
TITLES.append((out_t(t0, a, 0.78), t0 + t_gov, "1957", "Big", 560))

# 4. primo in India, secondo al mondo: mappa animata (due tratti di voce, una sola mappa)
src = clip("120520")
t0 = tl.t
(a1, b1), (a2, b2) = (0.60, 1.95), (2.35, 4.50)
d1, d2 = (b1 - a1) / SP, (b2 - a2) / SP
tl.vos.append(dict(file=src, a=a1, b=b1, speed=SP, t=t0))
tl.vos.append(dict(file=src, a=a2, b=b2, speed=SP, t=t0 + d1 + 0.04))
tl._add(kerala_map(), 0.0, d1 + 0.04 + d2 + GAP, grade="null", audio=False)
words(t0, a1, [("Il", 0.66), ("primo", 0.90), ("in", 1.30), ("India.", 1.46)])
words(t0 + d1 + 0.04, a2, [("E", 2.29), ("il", 2.53), ("secondo", 2.61), ("al", 3.01), ("mondo", 3.17), ("dopo", 3.41),
                           ("San", 3.73), ("Marino.", 3.97)])
TITLES.append((t0 + 0.05, t0 + d1 + 0.04, "1° IN INDIA", "Mid", 430))
TITLES.append((t0 + d1 + 0.1, tl.t, "2° AL MONDO", "Mid", 430))
TITLES.append((out_t(t0 + d1 + 0.04, a2, 3.41), tl.t, "dopo San Marino", "Small", 530))

# 5. sinistra e Congresso: le due bandiere, poi il canale (girato di Manuel) su "si sono alternati al potere"
a, b = 0.48, 4.50
src = clip("120532")
t_sin, t_con, t_alt = ((t - a) / SP for t in (1.23, 1.95, 2.99))
t0 = narr(src, a, b, [(gen(flag("ldf"), 0.6), t_con), (gen(flag("udf"), 0.4), t_alt - t_con),
                      (own(CANALE, 0.2, cx=0.55, fx=dict(zoom=(1.0, 1.05, None))), None)])
words(t0, a, [("Da", 0.43), ("allora", 0.75), ("sinistra", 1.23), ("e", 1.79), ("Congresso", 1.95), ("si", 2.59),
              ("sono", 2.75), ("alternati", 2.99), ("al", 3.63), ("potere.", 3.79)])
TITLES.append((t0 + t_sin, t0 + t_con, "SINISTRA", "Mid", 430))
TITLES.append((t0 + t_con, t0 + t_alt, "CONGRESSO", "Mid", 430))

# 6. riforma agraria, scuole e sanità: schede animate da foto Pixabay senza persone
a, b = 0.48, 3.40
t_sc, t_sa = ((t + 0.06 - a) / SP for t in (1.81, 2.53))
t0 = narr(clip("120544"), a, b, [(gen(card(f"{STOCK}/px_4967164.jpg", "risaia")), t_sc),
                                  (gen(card(f"{STOCK}/px_916678.jpg", "scuole")), t_sa - t_sc),
                                  (gen(card(f"{STOCK}/px_840125.jpg", "sanita")), None)])
words(t0, a, [("Tra", 0.45), ("riforma", 0.77), ("agraria,", 1.17), ("scuole", 1.81), ("e", 2.37), ("sanità.", 2.53)])

# 7. 1991: Manuel in camera, poi i cartelli scritti di Alleppey
src = clip("120556")
a, cut, b = 0.55, 2.28, 6.62
t0 = cam(src, a, cut)
TITLES.append((out_t(t0, a, 0.82), t0 + (cut - a) / SP, "1991", "Big", 560))
t1 = narr(src, cut, b, [(own(SEGNI, 0.6, cx=0.5, fx=dict(zoom=(1.0, 1.05, None))), None)])
words(t0, a, [("Nel", 0.50), ("1991", 0.82)])
words(t1, cut, [("è", 2.34), ("diventato", 2.50), ("il", 3.06), ("primo", 3.22), ("stato", 3.70),
                ("totalmente", 4.26), ("alfabetizzato", 4.90), ("dell'India.", 6.02)])

# 8. la sinistra perde: le bandiere vere perdono colore, colpo basso su "perso"
a, b = 0.65, 4.10
t_sx = (2.52 - a) / SP
t0 = narr(clip("120618"), a, b, [(own(FLAG_REAL, 0.25, speed=0.6, grade="hue=s='clip(1-(t-0.85)/0.3,0,1)'"), 1.67),
                                  (gen(flag("ldf"), 0.5, grade="hue=s=0,eq=brightness=-0.12:contrast=1.1",
                                       fx=dict(zoom=(1.1, 1.0, 0.6))), None)])
tl.sfx(out_t(t0, a, 3.48), sfx_file("hit"), 0.28)
words(t0, a, [("Ma", 0.60), ("a", 0.84), ("maggio", 1.00), ("del", 1.40), ("2026", 1.56), ("la", 2.52),
              ("sinistra", 2.68), ("ha", 3.32), ("perso.", 3.48)])
TITLES.append((out_t(t0, a, 1.56), t0 + t_sx, "2026", "Big", 560))

# 9. il Congresso vince: bandiera e contatore dei seggi
a, b = 0.42, 4.88
t0 = narr(clip("120712"), a, b, [(own(HOUSEBOAT, 3.0, cx=0.55), (1.41 - a) / SP),
                                  (own(STRADA, 2.0, cx=0.5), (2.37 - 1.41) / SP),
                                  (gen(flag("udf"), 0.2, fx=dict(zoom=(1.0, 1.05, None))), None)])
words(t0, a, [("La", 0.37), ("coalizione", 0.69), ("del", 1.41), ("Congresso", 1.57), ("ha", 2.21), ("vinto", 2.37),
              ("100", 2.85), ("seggi", 3.33), ("su", 3.81), ("140.", 3.97)])
COUNTER = (out_t(t0, a, 2.37), out_t(t0, a, 2.85) + 0.15, tl.t)
TITLES.append((out_t(t0, a, 2.37), out_t(t0, a, 2.85), "UDF · CONGRESSO", "Mid", 430))
TITLES.append((out_t(t0, a, 3.33), tl.t, "SEGGI SU 140", "Small", 660))

# 10-11. chiusura in camera: domanda e invito a commentare
a, b = 0.12, 2.70
t0 = cam(clip("120830"), a, b)
words(t0, a, [("Fine", 0.15), ("di", 0.39), ("un'era,", 0.55), ("o", 0.87), ("le", 1.03), ("radici", 1.11),
              ("sono", 1.59), ("troppo", 1.75), ("profonde?", 2.07)])
TITLES.append((t0 + 0.1, t0 + (b - a) / SP, "COSA SUCCEDERÀ ORA?", "Mid", 430))
a, b = 0.42, 3.00
t0 = cam(clip("120842"), a, b, fx=dict(zoom=(1.0, 1.04, None)))
words(t0, a, [("E", 0.39), ("tu,", 0.63), ("lo", 0.87), ("sapevi?", 1.03), ("Dimmi", 1.51), ("la", 1.75), ("tua", 1.91),
              ("nei", 2.15), ("commenti.", 2.31)])
END = tl.t


# ---------- sottotitoli animati e titoli (ASS) ----------
GOLD, WHITE = "&H004B8AB6&", "&H00FFFFFF&"


def chunks(ws):
    out, cur = [], []
    for w, t in ws:
        cur.append((w, t))
        txt = " ".join(x for x, _ in cur)
        if len(cur) >= 3 or len(txt) >= 16 or w[-1] in ".,?!":
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def ass_file():
    S = lambda v: int(round(v * K))
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding\n"
            f"Style: Cap,Poppins,{S(58)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{S(4)},{S(2)},5,0,0,0,1\n"
            f"Style: Big,Anton,{S(190)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,2,0,1,{S(3)},{S(5)},5,0,0,0,1\n"
            f"Style: Mid,Anton,{S(96)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,1,0,1,{S(3)},{S(4)},5,0,0,0,1\n"
            f"Style: Small,Poppins,{S(46)},{GOLD.replace('&H00', '&H00').rstrip('&')},&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,{S(3)},{S(2)},5,0,0,0,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    ws = sorted(WORDS, key=lambda x: x[1])
    cs = chunks(ws)
    y_cap = S(1180)
    for ci, c in enumerate(cs):
        c_end = cs[ci + 1][0][1] if ci + 1 < len(cs) else END
        c_end = min(c_end, c[-1][1] + 1.2)
        for i, (w, t) in enumerate(c):
            e = c[i + 1][1] if i + 1 < len(c) else c_end
            parts = [(f"{{\\c{GOLD}}}" if j == i else f"{{\\c{WHITE}}}") + x for j, (x, _) in enumerate(c)]
            pop = "\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)" if i == 0 else ""
            ev.append((1, t, e, "Cap", f"{{\\an5\\pos({W // 2},{y_cap}){pop}}}" + " ".join(parts)))
    for a, b, txt, st, y in TITLES:
        tag = f"{{\\an5\\pos({W // 2},{S(y)})\\fscx125\\fscy125\\alpha&HFF&\\t(0,140,\\fscx100\\fscy100\\alpha&H00&)\\fad(0,120)}}"
        ev.append((2, a, b, st, tag + txt))
    # contatore dei seggi: 0 -> 100
    c0, c1, c2 = COUNTER
    n = int((c1 - c0) * 30)
    for f in range(n):
        u = (f + 1) / n
        val = int(round(100 * (1 - (1 - u) ** 3)))
        ev.append((2, c0 + f / 30, c0 + (f + 1) / 30, "Big", f"{{\\an5\\pos({W // 2},{S(560)})}}{val}"))
    ev.append((2, c1, c2, "Big", f"{{\\an5\\pos({W // 2},{S(560)})\\c{GOLD}\\t(0,150,\\fscx110\\fscy110)\\t(150,300,\\fscx100\\fscy100)}}100"))
    p = f"{OUT}/reel_{W}.ass"
    with open(p, "w") as f:
        f.write(head)
        for layer, a, b, st, txt in sorted(ev, key=lambda e: e[1]):
            f.write(f"Dialogue: {layer},{ts(a)},{ts(b)},{st},,0,0,0,,{txt}\n")
    return p


tl.ass_override = ass_file()
name = f"VociVere_comunismo_reel_{W}x{H}.mp4"
print(f"== reel: {len(tl.shots)} inquadrature, {tl.t:.1f} s")
tl.render(f"{OUT}/{name}", crf=18 if W == 1080 else 23, preset="medium" if W == 1080 else "veryfast")
