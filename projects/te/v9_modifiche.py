#!/usr/bin/env python3
"""te v9 (8/11, Insights dai dati del mercato a 7 giorni): a metà video niente B-roll larghi senza persone.

Parte dal lungo v8 consegnato (work/te/consegnato/VociVere_te_long_4K.mp4, banner inclusi) e sostituisce solo
l'immagine di 9 tratti di colline o case vuote (audio identico, tempi e capitoli invariati):
- dove si sente Sadish e la sua clip lo mostra, si torna su di lui in sincrono (offset misurati con la
  correlazione dell'audio, a 10 ms);
- dove c'è il voiceover o la sua clip è girata sul paesaggio, mani che raccolgono, Sadish tra i filari.
I sottotitoli (e l'etichetta "Pombilai Orumai") erano impressi: si riscrivono negli stessi tratti con lo stesso
stile del lungo (Edit.ass in build.py). Una sola ricodifica con i parametri x264 del v8, audio copiato.
    python3 projects/te/v9_modifiche.py   (girato in work/te/raw dalla cartella Drive 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw)
"""
import glob, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W_ = f"{ROOT}/work/te"
IN = f"{W_}/consegnato/VociVere_te_long_4K.mp4"
V = f"{W_}/v9"
OUT = f"{W_}/VociVere_te_long_4K_v9.mp4"
DEF = "eq=contrast=1.03:saturation=1.05"
os.makedirs(V, exist_ok=True)


def C(k):
    m = glob.glob(f"{W_}/raw/DJI_20261026{k}_*")
    assert len(m) == 1, k
    return m[0]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)


# sottotitoli del lungo (build.py) per clip: (inizio, fine, testo) in tempi della clip
SUBS = {
    "133721": [(119.5, 123.5, "Oggi raccolgo qui, domani vado su un'altra collina."),
               (124.0, 131.2, "Poi il mese dopo si torna qui. È un giro.")],
    "134520": [(6.2, 11.2, "Normalmente, al giorno, una persona raccoglie"),
               (12.2, 16.5, "da ventisei a ventinove chili al giorno."), (17.0, 17.6, "In media."),
               (26.8, 29.5, "E chi raccoglie di più?"), (29.6, 30.5, "Soldi in più."),
               (58.2, 61.4, "Qui a Munnar ci sono tante fabbriche."),
               (62.0, 70.2, "Qui intorno ce ne sono tre, quattro: a venti, venticinque, trenta chilometri.")],
    "133946": [(0.1, 1.2, "Conosci la storia?"), (32.6, 34.2, "1877."), (42.7, 43.7, "Era un inglese."),
               (54.7, 61.6, "A Munnar, tutto intorno, nord, sud, est, ovest, per quaranta chilometri,"),
               (62.4, 64.8, "ovunque piantagioni di tè."),
               (65.5, 72.8, "Tutte queste montagne si chiamano Kannan Devan Hills.")],
    "134136": [(8.2, 13.0, "Sono trattati bene. Un ottimo rapporto,"), (13.0, 19.4, "aiuto, casa, cure mediche, trasporto."),
               (20.1, 22.4, "L'azienda dà tutto gratis.")],
    "134639": [(12.2, 14.8, "Qui è una cultura molto profonda."), (16.3, 19.0, "La produzione migliore dell'India. Buona qualità.")],
}

# tratti (inizio, fine nel lungo v8) -> chi si sente (clip, [(da t, delta = sorgente - montato)]) e immagini nuove.
# sync=True: si mostra la clip di chi parla nello stesso istante; altrimenti items = [(clip, inizio, durata)].
WIN = [
    dict(a=121.30, b=133.63, voice=("133721", [(0, -2.29)]), sync=True),
    dict(a=160.60, b=177.17, voice=("134520", [(0, -154.64), (173.0, -146.46)]),
         items=[("133721", 69.5, 4.2), ("133703", 1.0, 4.5), ("133721", 98.5, 4.3), ("135922", 0.0, None)]),
    dict(a=184.13, b=196.67, voice=("134520", [(0, -125.99)]), sync=True),
    dict(a=211.43, b=215.97, voice=("133946", [(0, -211.40), (212.5, -180.16), (214.25, -171.90)]),
         items=[("133625", 0.5, None)]),
    dict(a=215.97, b=226.53, voice=("133946", [(0, -161.33)]), sync=True),
    dict(a=226.53, b=234.07, voice=("133946", [(0, -161.10)]), items=[("133703", 5.0, 4.0), ("133721", 75.5, None)]),
    dict(a=249.87, b=258.07, voice=None, items=[("135527", 3.0, 4.2), ("133721", 86.0, None)]),
    dict(a=265.87, b=280.43, voice=("134136", [(0, -257.72)]), sync=True),
    dict(a=311.50, b=319.57, voice=None, items=[("133721", 80.0, 4.0), ("135527", 10.0, None)]),
    dict(a=329.07, b=336.47, voice=("134639", [(0, -316.92)]), sync=True),
]
LABEL = (313.5, 316.5, "Pombilai Orumai: unità delle donne")


def frames(t):
    return round(t * 30)


def segment(i, w):
    """Immagine nuova del tratto, 4K 30p, esattamente quanti fotogrammi il tratto."""
    out = f"{V}/seg{i:02d}.mp4"
    n = frames(w["b"]) - frames(w["a"])
    if os.path.exists(out):
        return out, n
    if w.get("sync"):
        k, d = w["voice"][0], w["voice"][1][0][1]
        parts = [(k, w["a"] + d, n / 30, False)]
    else:
        fixed = sum(x[2] for x in w["items"] if x[2])
        parts = [(k, a, d or (n / 30 - fixed), True) for k, a, d in w["items"]]
    ins, fc = [], ""
    for j, (k, a, d, zoom) in enumerate(parts):
        ins += ["-ss", f"{a:.3f}", "-t", f"{d + 0.5:.3f}", "-i", C(k)]
        z = (f",scale=w='trunc(3840*(1+0.04*t/{d:.3f})/2)*2':h='trunc(2160*(1+0.04*t/{d:.3f})/2)*2':eval=frame:"
             "flags=bicubic,crop=3840:2160") if zoom else ""
        fc += (f"[{j}:v]scale=3840:2160:flags=lanczos,{DEF},fps=30,trim=duration={d:.4f},setpts=PTS-STARTPTS{z}[v{j}];")
    fc += "".join(f"[v{j}]" for j in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0,trim=end_frame={n},format=yuv420p[o]"
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[o]", "-frames:v", str(n), "-c:v", "libx264",
         "-crf", "12", "-preset", "veryfast", out])
    return out, n


def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass():
    W, H, k = 3840, 2160, 2.0
    S = lambda v: int(round(v * k))
    sub = int(52 * k)
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
            "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"
            f"Style: Sub,Poppins Medium,{sub},&H0098D8F2,&H0098D8F2,&H00000000,&H90000000,0,0,0,0,100,100,"
            f"0.5,0,1,{sub / 32:.1f},{sub / 36:.1f},2,{int(W * 0.08)},{int(W * 0.08)},{int(110 * k)},1\n"
            f"Style: Lab,Playfair Display,{S(46)},&H00F2F2F2,&H00FFFFFF,&H00000000,&H80000000,0,-1,0,0,100,100,0.5,0,1,"
            f"{S(1.2)},{S(2.2)},1,{S(70)},{S(70)},{S(64)},1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for w in WIN:
        if not w["voice"]:
            continue
        k_, deltas = w["voice"]
        for j, (t0, d) in enumerate(deltas):
            lo = max(w["a"], t0)
            hi = min(w["b"], deltas[j + 1][0] if j + 1 < len(deltas) else 1e9)
            for sa, sb, txt in SUBS[k_]:
                a, b = max(sa - d, lo), min(sb - d, hi)
                if b - a > 0.15:
                    ev.append((a, b, "Sub", txt))
    ev.append((LABEL[0], LABEL[1], "Lab", "{\\fad(350,350)}" + LABEL[2]))
    p = f"{V}/v9.ass"
    with open(p, "w") as f:
        f.write(head)
        for a, b, st, txt in sorted(ev):
            f.write(f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{txt}\n")
    return p, ev


def main():
    segs = [segment(i, w) for i, w in enumerate(WIN)]
    p, ev = ass()
    for e in ev:
        print(f"  {e[0]:7.2f}-{e[1]:7.2f} {e[3]}")
    ins, fc, last = ["-i", IN], "", "0:v"
    for i, ((f, n), w) in enumerate(zip(segs, WIN)):
        ins += ["-itsoffset", f"{frames(w['a']) / 30:.4f}", "-i", f]
        fc += (f"[{last}][{i + 1}:v]overlay=eof_action=pass:enable='between(t,{frames(w['a']) / 30 - 0.001:.4f},{(frames(w['a']) + n - 0.5) / 30:.4f})'"
               f"[o{i}];")
        last = f"o{i}"
    fc += f"[{last}]ass={p}:fontsdir={ROOT}/models,format=yuv420p[v]"
    if os.environ.get("TEST"):                                   # anteprima veloce di alcuni secondi
        a = float(os.environ["TEST"])
        run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc.replace("format=yuv420p[v]", "scale=1280:720,format=yuv420p[v]"),
             "-map", "[v]", "-map", "0:a", "-ss", f"{a}", "-t", "6", "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-c:a", "aac",
             f"{V}/test_{a}.mp4"])
        return
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264",
         "-preset", "medium", "-crf", "20", "-maxrate", "38M", "-bufsize", "76M", "-profile:v", "high", "-level", "5.1",
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", OUT])
    print(OUT)


if __name__ == "__main__":
    main()
