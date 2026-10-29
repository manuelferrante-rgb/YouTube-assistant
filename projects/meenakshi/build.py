#!/usr/bin/env python3
"""Tempio di Meenakshi, Madurai (29/10): un solo verticale 9:16, tutto in voiceover.

    python3 projects/meenakshi/build.py [--preview]
Girato e VO (Mudakathan.m4a) in work/meenakshi/raw (cartella Drive 1Gov2PE4EU32BZPdJW3miH3oYPc68Iv8v, rclone).
Sequenza e testi di Manuel/Copy in copioni/meenakshi_testi.md ("PER MONTAGGIO"), musica e segni di Audio in
projects/meenakshi/audio/, girato in projects/meenakshi/girato.md.
"""
import glob, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import run
from reel_kit import Reel
from voice_clean import cleaned

PREVIEW = "--preview" in sys.argv
WORK = f"{ROOT}/work/meenakshi"
R = f"{WORK}/raw"
OUT = f"{WORK}/out"
AUD = f"{ROOT}/projects/meenakshi/audio"
VO = f"{R}/Mudakathan.m4a"
os.makedirs(OUT, exist_ok=True)

MUSICA = f"{AUD}/musica_meenakshi.flac"
MUS_LEVEL = 0.08                     # bassissima e costante sotto il VO (circa 23 dB sotto la voce, Manuel 27/10)
MUS_UP = 0.17                        # sulla signora, senza voce: +7 dB (Copy/Audio 29/10)
NIGHT = "eq=brightness=0.03:gamma=1.12:contrast=1.04:saturation=1.08"
CTA = ""                             # frase finale a schermo (la scrive Copy, Manuel 29/10); "\\N" per andare a capo
SP = 1.0                             # voce calma (copione di Copy): niente accelerazione


def C(tag):
    """Clip del 29/10 per ora di ripresa HHMMSS."""
    m = glob.glob(f"{R}/dji_mimo_20261029_{tag}_*")
    assert len(m) == 1, (tag, m)
    return m[0]


def cue(tl, t, name, d, gain, fout=0.5):
    """Segno melodico della chat Audio, lungo d secondi con coda sfumata."""
    out = f"{OUT}/cue_{name}_{d:.2f}.wav"
    if not os.path.exists(out):
        run(["ffmpeg", "-v", "error", "-y", "-i", f"{AUD}/{name}.flac", "-t", f"{d:.3f}", "-af",
             f"afade=t=out:st={d - fout:.3f}:d={fout}", "-ac", "2", "-ar", "48000", out])
    tl.sfx(t, out, gain)


# frasi del VO: tratti di voce misurati a 10 ms sulla voce pulita (RNNoise), parole dalla trascrizione corrette
# a orecchio sul copione ("tempo e" = "tempio", "Irena Yak" = "i re Nayak", 500/600 detti per esteso)
L1 = (3.04, 6.22, [("Nel", 3.04), ("1310", 3.12), ("si", 4.16), ("racconta", 4.32), ("questo", 4.8), ("tempio", 5.04),
                   ("fu", 5.36), ("saccheggiato.", 5.52)])
L2 = (7.07, 8.01, [("Guardatelo", 7.07), ("oggi.", 7.72)])
L3 = (8.99, 11.86, [("Tempio", 8.99), ("di", 9.24), ("Meenakshi,", 9.32), ("Madurai,", 9.96), ("nel", 10.68),
                    ("Tamil", 10.84), ("Nadu,", 11.24), ("in", 11.48), ("India.", 11.64)])
L4 = (12.57, 16.52, [("Lo", 12.57), ("ricostruiscono", 12.65), ("e", 13.37), ("lo", 13.45), ("ampliano", 13.69),
                     ("i", 14.09), ("re", 14.25), ("Nayak,", 14.45), ("tra", 14.89), ("il", 15.05),
                     ("Cinquecento", 15.13), ("e", 15.69), ("il", 15.85), ("Seicento.", 15.93)])
L5 = (17.12, 19.78, [("E", 17.12), ("i", 17.17), ("colori", 17.21), ("delle", 17.53), ("torri", 17.77), ("li", 18.09),
                     ("rifanno", 18.25), ("ogni", 18.73), ("consacrazione.", 18.97)])
L6 = (20.62, 22.81, [("Secoli", 20.62), ("dopo,", 21.03), ("qui", 21.43), ("si", 21.59), ("viene", 21.75),
                     ("ancora", 22.07), ("a", 22.31), ("pregare.", 22.39)])


PAD = (0.03, 0.06)                   # Manuel 29/10: niente respiri tra le frasi, solo il margine per non mangiare parole


def say(r, line, visuals):
    a, b, ws = line
    return r.narr(VO, a, b, visuals, words=ws, pad=PAD)


def at(t0, line, t_src):
    """Tempo nel montato di un istante della frase (per far comparire i titoli sulla parola)."""
    return t0 + (t_src - (line[0] - PAD[0])) / SP


def reel():
    W, H = (540, 960) if PREVIEW else (1080, 1920)
    r = Reel(f"{OUT}/reel_{W}_work", W, H, speed=SP, gap=0.0, amb=0.0)      # B-roll muti (27/10 sera)
    tl = r.tl

    # 1. GANCIO (Manuel 29/10): il signore già zoomato, un secondo; poi la torre con la folla (v3: scambiata con
    # l'elefante), e la rotazione (solo il giro, accelerato) sotto la fine della frase: "Guardatelo oggi" senza pause
    say(r, L1, [(r.own(C("182956"), 2.3, grade=NIGHT, fx=dict(zoom=(1.06, 1.14, None))), 1.1),
                (r.own(C("180356"), 3.0), None),
                (r.own(C("180606"), 0.85, speed=1.6), 0.25)])
    r.title(0.0, 2.0, "Saccheggiato nel 1310", "Tag", 400)
    r.cap_y.append((0.0, r.t, 560))                               # all'inizio sottotitoli più in alto (piace a Manuel)
    cue(tl, 0.0, "cue_gancio", 3.3, 0.24)                         # circa -12 dB sotto la voce
    # 2. "Guardatelo oggi" su Manuel con la torre dietro, poi un secondo dall'alto di notte (la camera che si muove)
    t_riv = say(r, L2, [(r.own(C("180606"), 1.25), None)])
    cue(tl, t_riv, "cue_rivelazione", 3.4, 0.24, fout=0.8)
    # 3. l'elefante di pietra fino a "in India", poi l'interno; titoli sulle parole: nome del tempio, poi Madurai e Tamil Nadu
    t3 = say(r, L3, [(r.own(C("181902"), 0.4, speed=1.5), 1.3), (r.own(C("180328"), 0.3), None)])   # v4: +0.3 / -0.3
    r.title(at(t3, L3, 8.99), at(t3, L3, 9.96), "Tempio di Meenakshi", "Tag", 400)
    r.title(at(t3, L3, 9.96), at(t3, L3, 11.86) + 0.3, "Madurai, Tamil Nadu", "Tag", 400)
    say(r, L4, [(r.own(C("174632"), 1.0), 2.0), (r.own(C("180344"), 1.4), None)])
    say(r, L5, [(r.own(C("175530"), 0.1), 1.4), (r.own(C("180356"), 8.6), None)])
    # 4. una persona che prega, poi l'inizio della carrellata attorno alla torre
    say(r, L6, [(r.own(C("180524"), 5.6), None)])
    t_b = r.t
    r.cap_stop.append(t_b)
    r.own(C("180344"), 0.0)(0.9)
    # 5. chiusura sulla signora anziana, 2 secondi (Manuel: non di più), senza voce
    t_sig = r.t
    r.own(C("193642"), 0.4, grade=NIGHT, fx=dict(black_out=0.4))(2.0)
    cue(tl, t_sig - 0.4, "cue_chiusura", 2.4, 0.45, fout=0.9)
    if CTA:   # frase finale a schermo di Copy, stesso formato dei titoli, sopra la testa della signora
        r.title(t_b + 0.1, r.t, CTA, "Tag", 400)

    end = r.t
    tl.music(0.0, t_b + 0.3, MUSICA, offset=0.0, level=MUS_LEVEL, fin=0.05, fout=0.3, duck=False, norm=False)
    tl.music(t_b, end, MUSICA, offset=t_b, level=MUS_UP, fin=0.3, fout=1.0, duck=False, norm=False)

    tl.nat_af = "highpass=f=90"
    tl.audio_map = {VO: cleaned(VO, f"{WORK}/voce")}              # voce pulita con RNNoise
    out = f"{OUT}/VociVere_meenakshi_reel_{W}x{H}.mp4"
    return r.render(out, crf=18 if W == 1080 else 24, preset="medium" if W == 1080 else "veryfast")


if __name__ == "__main__":
    print(reel())
