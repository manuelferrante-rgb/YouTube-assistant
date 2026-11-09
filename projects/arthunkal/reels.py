#!/usr/bin/env python3
"""Arthunkal: i 4 verticali rifatti il 4/11 nel formato reel del 29/10 (regole/formato_reel.md, modello comorin).

    python3 projects/arthunkal/reels.py v1|v2|v3|v4 [--preview]
Manuel 4/11 (dati del mercato): primo fotogramma = la persona o il gesto più forte, già in movimento; mai un montaggio
da trailer, nemmeno nel teaser. Il voiceover registrato di Arthunkal (vo_take1) non è più su Drive: i reel usano
solo il parlato in camera di Manuel e le interviste del girato (work/arthunkal/raw, cartella Drive
1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX). Musica: musica_verticali.wav della chat Audio (Drive montati/arthunkal/audio).
"""
import os, subprocess, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B                                         # clip C(), grafiche storia() e mappa() del lungo
from doc_render import run
from reel_kit import Reel
from voice_clean import cleaned, gated, light
import reel_close as RC

PREVIEW = "--preview" in sys.argv
WORK, OUT, C, NIGHT = B.WORK, f"{B.WORK}/out_reel", B.C, B.NIGHT
os.makedirs(OUT, exist_ok=True)
MUSICA = f"{WORK}/musica_orig/musica_verticali.wav"
MUS_LEVEL, MUS_UP = 0.08, 0.17
CTA = "Ascolta altre voci, su"
PAD = (0.03, 0.06)
GR = "eq=contrast=1.03:saturation=1.05"
VOCE = f"{WORK}/voce"

M = C("072327")       # Manuel all'alba sulla spiaggia
K = C("072415")       # Manuel: "si parte da un santuario... a Kalavoor"
P = C("080217")       # Manuel: prima in strada, poi in spiaggia
BAS = C("091658")     # Manuel davanti alla basilica
PEL = C("085034")     # la pellegrina sulla strada


def ph(a, b, text, times):
    ws = list(zip(text.split(), times))
    assert len(ws) == len(text.split()) == len(times), text
    ws[0] = (ws[0][0], max(ws[0][1], a))
    return a, b, ws


# frasi (trascrizione a pezzi del 4/11, tempi parola; il testo è quello detto)
L1 = ph(0.82, 4.40, "Sono le sette del mattino e queste persone camminano da mezzanotte.",
        [0.82, 1.14, 1.30, 1.62, 1.78, 2.26, 2.42, 2.66, 2.98, 3.46, 3.62])
L2 = ph(5.03, 7.57, "Tredici chilometri lungo la costa del Kerala.", [5.06, 5.54, 6.10, 6.42, 6.50, 6.82, 6.98])
L3 = ph(8.40, 10.16, "Pregando il rosario senza mai fermarsi.", [8.39, 8.79, 8.87, 9.27, 9.51, 9.67])
L4 = ph(10.86, 12.91, "Centinaia di migliaia di persone.", [10.89, 11.61, 11.77, 12.33, 12.49])
L5 = ph(14.46, 18.24, "La prima volta nel 2002 ne erano poche centinaia.",
        [14.49, 14.65, 14.81, 15.13, 15.29, 16.73, 16.89, 17.21, 17.61])
K1 = ph(0.35, 4.54, "Come ci hanno raccontato, si parte da un santuario dedicato a Maria, a Kalavoor.",
        [0.37, 0.61, 0.69, 1.01, 1.49, 1.65, 1.89, 1.97, 2.05, 2.53, 3.01, 3.09, 3.65, 3.81])
P1 = ph(0.50, 2.57, "Prima lo facevano totalmente in strada.", [0.53, 0.85, 1.01, 1.57, 1.97, 2.21])
P2 = ph(3.30, 8.50, "Poi con il traffico si creava troppa confusione e si sono spostati direttamente in spiaggia.",
        [3.33, 3.89, 4.05, 4.21, 4.85, 5.01, 5.57, 5.85, 6.37, 6.45, 6.61, 6.77, 7.41, 7.89, 8.05])
WB = dict(B.W_BASILICA)


def wb(a, b):
    """Parole della basilica: tempi della tabella del lungo, corretti il 4/11 sulla voce pulita ("Questa" a 1.55,
    "Nel" non si sente nella folla: la frase parte da "1647" a 16.71)."""
    fix = {"Questa": 1.55, "chiesa": 1.70, "l'ha": 1.98, "ricostruita": 2.14, "1647": 16.71, "un": 5.10, "Qui": 11.44}
    return [(w, fix.get(w, t)) for w, t in B.W_BASILICA if a - 0.05 <= t < b and w != "Nel"]


def gaps(src, a, b, min_gap=0.25):
    """Pause dentro una frase (voce pulita, energia a 10 ms): [(da, a)] da togliere."""
    wav = cleaned(src, VOCE)
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", wav, "-ac", "1",
                                      "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    n = len(x) // 160
    db = 20 * np.log10(np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-9)
    db = np.convolve(db, np.ones(3) / 3, mode="same")
    on = db > max(db.max() - 32, np.percentile(db, 20) + 8)
    out, i = [], 0
    while i < n:
        if not on[i]:
            j = i
            while j < n and not on[j]:
                j += 1
            if 0 < i and j < n and (j - i) / 100 >= min_gap:
                out.append((a + i / 100 + 0.04, a + j / 100 - 0.03))
            i = j
        i += 1
    return out


def say(r, src, line, visuals):
    """Frase sopra immagini, senza le pause interne (narr allarga i tagli di +0.12/-0.06: si compensa)."""
    a, b, ws = line
    # solo pause vere (>= 0.3 s): sotto, il taglio cadeva sulle consonanti ("persone" diventava "pedone", Manuel 8/11)
    cuts = [(ca - 0.12, cb + 0.06) for ca, cb in gaps(src, a, b, min_gap=0.3)]
    return r.narr(src, a, b, visuals, words=ws, pad=PAD, cuts=cuts)


def logo_card(W, H, d, src, a, grade=GR, cx=0.5):
    """Logo chiaro (70%) che sfuma sull'ultima persona, che continua sotto un velo nero leggero (35%)."""
    out = f"{OUT}/logo_{os.path.basename(src)[:26]}_{a:.2f}_{d:.2f}_{cx}_{W}x{H}.mp4"
    lw = int(W * 0.7) // 2 * 2
    if not os.path.exists(out):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d + 0.5:.3f}", "-i", src, "-loop", "1", "-t",
             f"{d:.3f}", "-i", f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png", "-filter_complex",
             f"[0:v:0]crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{cx}-ih*9/32))':0,scale={W}:{H}:flags=lanczos,fps=30,{grade},"
             "tpad=stop_mode=clone:stop_duration=2[v0];"
             f"color=c=black@0.35:s={W}x{H}:r=30:d={d:.3f},format=rgba,fade=t=in:st=0:d=0.5:alpha=1[k];"
             "[v0][k]overlay=shortest=1[bg];"
             f"[1]scale={lw}:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[l];[bg][l]overlay=(W-w)/2:(H-h)/2:shortest=1,"
             "format=yuv420p", "-an", "-t", f"{d:.3f}", "-r", "30", "-c:v", "libx264", "-crf", "16", out])
    return out


def size():
    return (540, 960) if PREVIEW else (1080, 1920)


def reel(tag):
    W, H = size()
    return Reel(f"{OUT}/{tag}_{W}_work", W, H, speed=1.0, gap=0.0, amb=0.0, cap_box=True)


def close(r, place, person, tail_title=None, variant="A"):
    """Chiusura stabile (Manuel 5/11, tools/reel_close.py): "Ascolta altre voci, su" sull'ultima persona appena spariscono
    i sottotitoli, il logo 0.8 s dopo; variante A o B alternata tra i reel. tail_title (teaser): la domanda prima, sul
    luogo (1.2 s)."""
    t_b = r.t
    r.cap_stop.append(t_b)
    if tail_title:
        r.own(*place)(1.2)
        r.title(t_b, r.t, tail_title, "Tag", 400)
    src, a = person[:2]
    cx = person[2] if len(person) > 2 else 0.5
    gr = person[3] if len(person) > 3 else GR
    _, end = RC.close(r, OUT, src, a, variant=variant, grade=gr, cx=cx)
    r.tl.music(0.0, t_b + 0.3, MUSICA, offset=0.0, level=MUS_LEVEL, fin=0.05, fout=0.3, duck=False, norm=False)
    r.tl.music(t_b, end, MUSICA, offset=t_b, level=MUS_UP, fin=0.1, fout=1.0, duck=False, norm=False)
    return t_b


VOICE = {BAS: lambda s: gated(s, VOCE, depth_db=-12.0, double=True),       # 8/11: davanti alla basilica la folla tra le parole si sentiva troppo
         PEL: lambda s: light(s, VOCE)}      # 8/11: RNNoise cancellava la voce della pellegrina (si sentiva solo la musica)


def finish(r, name, voices):
    r.tl.audio_map = {v: VOICE.get(v, lambda s: cleaned(s, VOCE))(v) for v in voices}
    r.tl.nat_af = "highpass=f=90"
    W, H = r.W, r.H
    out = f"{OUT}/VociVere_arthunkal_{name}_{W}x{H}.mp4"
    one = r.render(out.replace(".mp4", "_1x.mp4"), crf=16 if W == 1080 else 24, preset="medium" if W == 1080 else "veryfast")
    if os.environ.get("PLAN"):
        return one
    return norm14(faster(one, out, 1.1))


def norm14(f):
    """-14 LUFS: guadagno fisso più limitatore sui picchi (-1.5 dBTP), così anche i reel con le interviste ci arrivano."""
    import json
    def meas(x):
        e = subprocess.run(["ffmpeg", "-hide_banner", "-i", x, "-af", "loudnorm=I=-14:TP=-1:print_format=json", "-f", "null",
                            "-"], capture_output=True, text=True).stderr
        return float(json.loads(e.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])
    g, tmp = -14 - meas(f), f.replace(".mp4", "_n.mp4")
    for _ in range(3):
        if abs(g) < 0.05:
            break
        run(["ffmpeg", "-v", "error", "-y", "-i", f, "-c:v", "copy", "-af",
             f"volume={g:.2f}dB,alimiter=limit=0.84:level=disabled:attack=1:release=60", "-c:a", "aac", "-b:a", "256k",
             "-movflags", "+faststart", tmp])
        i = meas(tmp)
        if abs(i + 14) <= 0.2:
            break
        g += -14 - i
    if os.path.exists(tmp):
        os.replace(tmp, f)
    return f


def faster(src, out, k):
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", f"[0:v]setpts=PTS/{k},fps=30[v];[0:a]atempo={k}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out])
    return out


# ------------------------------------------------------------- v1: teaser (prima del lungo), nessun arrivo
def v1():
    r = reel("v1")
    # GANCIO: la donna che cammina verso la camera nella notte, già in movimento
    say(r, M, L2, [(r.own(C("023818"), 0.4, grade=NIGHT), 1.0), (r.own(C("023744"), 0.3, grade=NIGHT), None)])
    r.title(0.0, r.t, "2:30 di notte, in cammino", "Tag", 400)
    say(r, M, L3, [(r.own(C("023529"), 2.0, grade=NIGHT), None)])
    say(r, M, L1, [(r.own(C("072504"), 0.0), 1.6), (r.own(C("075231"), 1.0), None)])
    say(r, M, L4, [(r.own(C("085345"), 0.0), None)])
    close(r, (C("072504"), 1.8), (C("073335"), 0.0), tail_title="Perché?")
    return finish(r, "v1_teaser", [M])


# ------------------------------------------------------------- v2: la statua di Milano
def v2():
    r = reel("v2")
    W, H = r.W, r.H
    sB = B.storia(W, H, "Bv5", "1584|padre Giacomo Fenicio|gesuita italiano|0.2", 5.0, prev="52 d.C.")
    sC = B.storia(W, H, "Cv5", "1647|la statua di San Sebastiano|arriva da Milano|0.3", 4.0, prev="1584")
    # GANCIO (Insights + Manuel 9/11): prima un pellegrino, l'anziano col telo bianco della miniatura, poi Manuel
    # davanti alla basilica. L'anziano esce dall'inquadratura dopo ~1 s: rallentato a 0.7x sotto la prima frase
    r.narr(BAS, 1.50, 2.95, [(r.own(C("090951"), 0.0, cx=0.58, speed=0.7), None)], words=wb(1.0, 2.95),
           pad=(PAD[0], 0.0))                                                             # "Questa chiesa l'ha ricostruita"
    r.cam(BAS, 2.95, 4.58, words=wb(2.95, 4.45), pad=(0.0, 0.04))                        # Manuel: "nel 1584"
    tB = r.t
    r.narr(BAS, 5.08, 8.50, [(r.gen(sB, 1.6), None)], words=wb(4.85, 8.95), pad=PAD)      # "un gesuita italiano, padre..."
    r.title(0.0, tB, "Scolpita a Milano nel 1647", "Tag", 400)
    r.cam(BAS, 11.40, 15.28, words=wb(11.1, 15.9), pad=PAD)                             # "Qui lo chiamano ancora Veluthachan..."
    r.narr(BAS, 16.62, 17.9, [(r.gen(sC), None)], words=wb(16.15, 17.9), pad=PAD)         # "1647"
    r.narr(BAS, 17.9, 20.32, [(r.own(C("091405"), 0.5), None)], words=wb(17.9, 20.6), pad=(0.0, 0.06))  # la statua
    close(r, (C("090903"), 0.5), (C("091255"), 0.9), variant="B")
    return finish(r, "v2_statua", [BAS])


# ------------------------------------------------------------- v3: una persona
def v3():
    r = reel("v3")
    cx = 0.68
    # GANCIO: lei che risponde, primo piano
    r.cam(PEL, 45.7, 47.0, cx=cx, pad=PAD, block=[(45.75, 47.0, "È fede, è credere.", "")])
    r.title(0.0, r.t + 0.6, "13 km a piedi, di notte", "Tag", 400)
    say(r, M, L1, [(r.own(C("072504"), 0.0), 1.6), (r.own(C("075231"), 1.0), None)])
    t2 = say(r, M, L2, [(r.own(C("085345"), 0.0), None)])
    r.title(t2 + 0.9, r.t, "Arthunkal, Kerala", "Tag", 400)
    r.cam(PEL, 47.3, 49.3, cx=cx, pad=PAD, block=[(47.35, 49.3, "Lì succedono tanti miracoli.", "")])
    r.cam(PEL, 51.25, 57.0, cx=cx, pad=PAD, block=[(51.3, 55.5, "Chi partecipa ci trova qualcosa.", ""),
                                                   (56.0, 57.0, "Un po' di felicità.", "")])
    close(r, (C("085422"), 1.0), (PEL, 57.05, cx))
    return finish(r, "v3_persona", [M, PEL])


# ------------------------------------------------------------- v4: come funziona
def v4():
    r = reel("v4")
    W, H = r.W, r.H
    # GANCIO: il rosario in mano, che scorre mentre si cammina
    say(r, M, L3, [(r.own(C("075747"), 1.2), None)])
    r.title(0.0, r.t, "13 km pregando", "Tag", 400)
    # la mappa sotto "si parte da un santuario... a Kalavoor" e "Tredici chilometri..." (13 sulla parola "Tredici")
    t_map = r.t
    dK = (K1[1] + PAD[1]) - (K1[0] - PAD[0]) - sum(b - a - 0.18 for a, b in gaps(K, K1[0], K1[1]))
    tA, tB = dK - 1.4, dK - 0.6
    tkm = dK + 0.06
    mdur = round(dK + (L2[1] - L2[0]) + 0.1, 2)
    mp, _ = B.mappa(W, H, round(tA, 2), round(tB, 2), round(tkm, 2), mdur)
    say(r, K, K1, [(r.gen(mp), None)])
    say(r, M, L2, [(r.gen(mp, r.t - t_map), None)])
    r.cam(P, P1[0], P1[1], words=P1[2], pad=PAD)                                       # Manuel in camera
    say(r, P, P2, [(r.own(C("072504"), 0.0), 2.2), (r.own(C("075231"), 2.0), None)])
    say(r, M, L4, [(r.own(C("085345"), 0.0), None)])
    t5 = say(r, M, L5, [(r.own(C("085208"), 1.0), None)])
    r.title(t5 + 0.6, r.t, "Dal 2002", "Tag", 400)
    close(r, (C("075209"), 1.0), (C("073335"), 6.5), variant="B")
    return finish(r, "v4_come_funziona", [M, K, P])


if __name__ == "__main__":
    for w in [a for a in sys.argv[1:] if not a.startswith("--")]:
        print(globals()[w]())
