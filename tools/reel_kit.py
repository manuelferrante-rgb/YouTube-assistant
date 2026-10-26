#!/usr/bin/env python3
"""Strumenti comuni per i reel Voci Vere (9:16), nati dal reel "Comunismo in Kerala".

Regole di Manuel per i reel: voce a 1.2x, solo tempi morti tagliati (testo intero), B-roll suo alternato a
grafiche animate, Manuel in camera ogni tanto, sottotitoli su tutto il parlato centrali nella safe zone,
animati parola per parola (parola corrente in oro), non troppo grandi; titoli animati; pochi effetti sonori.

    from reel_kit import Reel
    r = Reel(workdir, W=1080, H=1920)
    t0 = r.cam(src, a, b, words=[("Ciao", 0.4), ...])            # Manuel in camera, labiale in sincrono
    r.narr(src, a, b, [(r.own(broll, 2.0), 1.5), (r.gen(gfx), None)], words=[...])   # voce sopra immagini
    r.title(t_in, t_out, "1957", "Big")
    r.render(out)
"""
import os
from doc_render import Timeline, ts, dur_of

GOLD, WHITE = "&H004B8AB6&", "&H00FFFFFF&"


class Reel:
    def __init__(self, workdir, W=1080, H=1920, speed=1.2, gap=0.08, amb=0.12, cx_cam=0.5):
        self.tl = Timeline(W, H, workdir)
        self.W, self.H, self.K = W, H, W / 1080
        self.SP, self.GAP, self.AMB, self.CX = speed, gap, amb, cx_cam
        self.words_ = []       # (parola, tempo nel montato)
        self.blocks = []       # sottotitoli a blocco (interviste tradotte): (inizio, fine, testo)
        self.titles = []       # (inizio, fine, testo, stile, y)
        self.raw_ass = []      # eventi ASS già pronti (contatori ecc.)
        self.dir = workdir

    @property
    def t(self):
        return self.tl.t

    # ---------- tempi ----------
    def out_t(self, t0, a, t_src, speed=None):
        return t0 + (t_src + 0.06 - a) / (speed or self.SP)

    def words(self, t0, a, ws, speed=None):
        for w, t in ws:
            self.words_.append((w, self.out_t(t0, a, t, speed)))

    # ---------- immagini ----------
    def own(self, src, a, cx=0.5, speed=1.0, grade=None, fx=None, gain=None):
        """B-roll girato da Manuel (con un filo del suo suono d'ambiente)."""
        def f(d):
            kw = dict(grade=grade) if grade else {}
            self.tl._add(src, a, d * speed, speed=speed, gain=self.AMB if gain is None else gain, cx=cx, fade=0.05,
                         fx=fx, **kw)
        return f

    def gen(self, src, a=0.0, speed=1.0, grade="null", fx=None):
        """Grafica generata (senza audio)."""
        def f(d):
            self.tl._add(src, a, d * speed, speed=speed, grade=grade, audio=False, fx=fx)
        return f

    # ---------- parlato ----------
    def narr(self, src, a, b, visuals, words=(), speed=None, cuts=()):
        """Voce di una clip sopra immagini: visuals = [(funzione, durata o None)]; None si divide il resto.
        cuts: pause interne da togliere [(da, a)] in tempi della sorgente (la voce diventa più tratti attaccati)."""
        sp = speed or self.SP
        t0 = self.tl.t
        # margini per non mangiare le parole: 0.06 s prima, 0.12 s dopo (anche ai bordi delle pause tolte)
        a, b = max(0.0, a - 0.06), min(b + 0.12, dur_of(src) - 0.05)
        cuts = [(ca + 0.12, cb - 0.06) for ca, cb in cuts if cb - ca > 0.3]
        ranges, cur = [], a
        for ca, cb in sorted(cuts):
            ranges.append((cur, ca)); cur = cb
        ranges.append((cur, b))
        t = t0
        for ra, rb in ranges:
            self.tl.vos.append(dict(file=src, a=ra, b=rb, speed=sp, t=t))
            self.words(t, ra, [(w, wt) for w, wt in words if ra - 0.1 <= wt < rb], sp)
            t += (rb - ra) / sp
        total = t - t0 + self.GAP
        fixed = sum(d for _, d in visuals if d)
        rest = max(0.2, total - fixed) / max(1, sum(1 for _, d in visuals if not d))
        for fn, d in visuals:
            fn(d or rest)
        return t0

    def src_to_out(self, t0, a, t_src, cuts=(), speed=None):
        """Tempo nel montato di un istante della sorgente, tenendo conto delle pause tolte."""
        removed = sum(min(cb, t_src) - ca for ca, cb in cuts if t_src > ca)
        return t0 + (t_src - a - removed) / (speed or self.SP)

    def cam(self, src, a, b, words=(), speed=None, cx=None, fx=None, block=None):
        """Parlato in camera, labiale in sincrono.
        block: [(a, b, italiano, originale)] per le battute in altra lingua: italiano al centro, originale in basso."""
        sp = speed or self.SP
        t0 = self.tl.t
        a, b = max(0.0, a - 0.06), min(b + 0.12, dur_of(src) - 0.05)   # margini sulle parole
        self.tl.speech(src, [(a, b)], speed=sp, cx=self.CX if cx is None else cx,
                       fx=fx or dict(zoom=(1.06, 1.0, 0.3)))
        self.words(t0, a, words, sp)
        for sa, sb, it, orig in block or ():
            self.blocks.append((t0 + (sa - a) / sp, t0 + (sb - a) / sp, it, orig))
        return t0

    def title(self, a, b, txt, style="Mid", y=430):
        self.titles.append((a, b, txt, style, y))

    # ---------- sottotitoli animati e titoli ----------
    @staticmethod
    def _chunks(ws):
        out, cur = [], []
        for w, t in ws:
            cur.append((w, t))
            if len(cur) >= 3 or len(" ".join(x for x, _ in cur)) >= 16 or w[-1] in ".,?!":
                out.append(cur); cur = []
        if cur:
            out.append(cur)
        return out

    def ass(self, end):
        S = lambda v: int(round(v * self.K))
        W = self.W
        head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {self.H}\nWrapStyle: 2\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
                "MarginL, MarginR, MarginV, Encoding\n"
                f"Style: Cap,Poppins,{S(58)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{S(4)},{S(2)},5,0,0,0,1\n"
                f"Style: Big,Anton,{S(190)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,2,0,1,{S(3)},{S(5)},5,0,0,0,1\n"
                f"Style: Mid,Anton,{S(96)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,1,0,1,{S(3)},{S(4)},5,0,0,0,1\n"
                f"Style: Orig,Poppins,{S(44)},&H00E6E6E6,&H00FFFFFF,&H00000000,&H80000000,0,-1,0,0,100,100,0,0,1,{S(3)},{S(2)},5,0,0,0,1\n"
                f"Style: Small,Poppins,{S(46)},&H004B8AB6,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,{S(3)},{S(2)},5,0,0,0,1\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        ev, y_cap, y_orig = [], S(1180), S(1440)
        cs = self._chunks(sorted(self.words_, key=lambda x: x[1]))
        starts = sorted([c[0][1] for c in cs] + [bl[0] for bl in self.blocks])
        for ci, c in enumerate(cs):
            nxt = [s for s in starts if s > c[0][1] + 1e-3]
            c_end = min(nxt[0] if nxt else end, c[-1][1] + 1.0)   # mai due sottotitoli insieme
            for i, (w, t) in enumerate(c):
                e = c[i + 1][1] if i + 1 < len(c) else c_end
                parts = [(f"{{\\c{GOLD}}}" if j == i else f"{{\\c{WHITE}}}") + x for j, (x, _) in enumerate(c)]
                pop = "\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)" if i == 0 else ""
                ev.append((1, t, e, "Cap", f"{{\\an5\\pos({W // 2},{y_cap}){pop}}}" + " ".join(parts)))
        for a, b, it, orig in self.blocks:
            ev.append((1, a, b, "Cap", f"{{\\an5\\pos({W // 2},{y_cap})\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}}{it}"))
            if orig:
                ev.append((1, a, b, "Orig", f"{{\\an5\\pos({W // 2},{y_orig})}}{orig}"))
        for a, b, txt, st, y in self.titles:
            tag = (f"{{\\an5\\pos({W // 2},{S(y)})\\fscx125\\fscy125\\alpha&HFF&"
                   f"\\t(0,140,\\fscx100\\fscy100\\alpha&H00&)\\fad(0,120)}}")
            ev.append((2, a, b, st, tag + txt))
        ev += self.raw_ass
        p = f"{self.dir}/reel.ass"
        with open(p, "w") as f:
            f.write(head)
            for layer, a, b, st, txt in sorted(ev, key=lambda e: e[1]):
                f.write(f"Dialogue: {layer},{ts(a)},{ts(b)},{st},,0,0,0,,{txt}\n")
        return p

    def render(self, out, crf=18, preset="medium"):
        self.tl.fix_freezes()
        self.tl.ass_override = self.ass(self.tl.t)
        print(f"== reel: {len(self.tl.shots)} inquadrature, {self.tl.t:.1f} s")
        self.tl.render(out, crf=crf, preset=preset)
        return out


def brush_in(src, out, dur=0.27, seed=3):
    """Apertura con pennellata: l'immagine si rivela da sinistra con un bordo a setole (dur secondi), resto invariato."""
    import subprocess, numpy as np, cv2
    from doc_render import run
    W, H = (int(v) for v in run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                 "stream=width,height", "-of", "csv=p=0", src]).strip().split(","))
    n = max(2, round(dur * 30))
    rng = np.random.default_rng(seed)
    yy = np.arange(H, dtype=np.float32)
    # bordo della pennellata: ondulazione morbida + setole fitte, leggermente inclinato
    soft = np.convolve(rng.standard_normal(H + 200), np.ones(120) / 120, "same")[100:100 + H] * 9
    bristle = np.convolve(rng.standard_normal(H + 10), np.ones(3) / 3, "same")[5:5 + H]
    jitter = (soft * 0.06 + bristle * 0.025) * W
    tilt = (yy - H / 2) * 0.18
    mdir = f"{os.path.dirname(out)}/brush_masks"
    os.makedirs(mdir, exist_ok=True)
    X = np.arange(W, dtype=np.float32)[None, :]
    for f in range(n):
        p = 1 - (1 - (f + 1) / n) ** 2                      # ease-out
        edge = (p * 1.35 - 0.15) * W + jitter - tilt
        m = np.clip((edge[:, None] - X) / (0.012 * W) + 0.5, 0, 1)
        cv2.imwrite(f"{mdir}/m{f:03d}.png", cv2.GaussianBlur((m * 255).astype(np.uint8), (0, 0), 1.2))
    d = n / 30
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-framerate", "30", "-i", f"{mdir}/m%03d.png", "-filter_complex",
         f"[0:v]split[a][b];[a]trim=end_frame={n},setpts=PTS-STARTPTS[h];[b]trim=start_frame={n},setpts=PTS-STARTPTS[t];"
         f"[1:v]format=gray,scale={W}:{H}[m];color=black:s={W}x{H}:r=30:d={d:.4f}[k];"
         f"[h][m]alphamerge[ha];[k][ha]overlay=shortest=1,format=yuv420p[hb];[hb][t]concat=n=2:v=1:a=0,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "copy",
         "-movflags", "+faststart", out])
    return out
