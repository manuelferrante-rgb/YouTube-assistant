#!/usr/bin/env python3
"""Musica originale del lungo coir (le donne del coir, Anathalavattom, Kerala), autore Voci Vere. Solo musica.

    python3 audio/musica/coir.py <brano> <stile> <out.wav>
    brani: intro (~10 s), strada (~30 s), laguna (~30 s), macchine (~12 s), finale (~35 s)
    stili (tre bozze per brano, Manuel 6/11: "dammi di tutti gli audio le tre bozze"):
      A  ostinato d'archi in crome (spiccato) + accordi lunghi che crescono: il piu' cinematografico
      B  arpeggio di piano in semicrome, morbido, sopra archi che respirano: fluido, in movimento
      C  pulsazione moderna: pizzicato alto in semicrome + archi a ondate sul tempo debole + piano in ottave

Brief di Copy (copioni/coir_audio_brief.md): seria, profonda, armonia scura (fa minore); dignita', peso, calma;
niente pieta', niente epica. Manuel 6/11 sulla prima prova: "un po' troppo lento e poco cinematografico" -> ora con
un passo (84-96 bpm), accordi che cambiano ogni battuta o due, crescendo dentro ogni brano.
Regola di Manuel (27-28/10): niente tappeto basso. Voce piu' grave fa3 (175 Hz), passa-alto ripido a 160 Hz su tutto,
controllo con audio/kit/bande.py. Le voci sono raddoppiate in alto perche' si sentano anche dal telefono.
Motivo di tre note (fa - lab - sol, una domanda aperta): nell'intro, nella laguna e nel finale, dove si chiude sul fa.
"""
import argparse, subprocess, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import SR, Track, piano_note, pluck, hp_fft, lp_fft, hz, adsr, rng  # noqa: E402

MOTIVO = [77, 80, 79]          # fa5 - lab5 - sol5

# accordi in fa minore, voce piu' grave >= fa3 (53)
CH = {
    "Fm": [53, 60, 65, 68, 72], "Db": [53, 61, 65, 68, 73], "Ab": [56, 60, 63, 68, 72],
    "Eb": [55, 58, 63, 67, 70], "Cm": [55, 60, 63, 67, 72], "Bbm": [53, 58, 65, 70, 73],
    "Fsus": [53, 60, 65, 67, 72],
}

BRANI = {   # durata, bpm, progressione (un accordo ogni `bar` battute), motivo (secondo), chiude
    "intro":    dict(dur=10.0, prog=["Fm", "Db", "Fm", "Fsus"], bars=1, motivo=2.5, chiude=False),
    "strada":   dict(dur=30.0, prog=["Fm", "Db", "Ab", "Eb"], bars=2, motivo=None, chiude=False),
    "laguna":   dict(dur=30.0, prog=["Db", "Ab", "Fm", "Eb"], bars=2, motivo=15.0, chiude=False),
    "macchine": dict(dur=12.0, prog=["Fm", "Fm", "Db", "Eb"], bars=1, motivo=None, chiude=False),
    "finale":   dict(dur=35.0, prog=["Db", "Eb", "Fm", "Ab", "Db", "Eb", "Fsus", "Fm"], bars=2, motivo=26.0, chiude=True),
}
STILI = {"A": 92, "B": 84, "C": 96}


def archi(n, dur, bright=2400, att=1.0, rel=1.5):
    """Archi tenuti: 4 seghe poco stonate, vibrato lento."""
    N = int(dur * SR); t = np.arange(N) / SR; f = hz(n); x = np.zeros(N)
    for d in (-6, -2, 2, 6):
        fr = f * 2 ** (d / 1200) * (1 + 0.0018 * np.sin(2 * np.pi * rng.uniform(4.5, 5.5) * t + rng.uniform(0, 6)))
        p = (np.cumsum(fr) / SR + rng.uniform(0, 1)) % 1.0
        x += 2 * p - 1
    x = lp_fft(x, bright, 2) / 4
    return x * adsr(N, min(att, dur / 3), min(rel, dur / 2.5))


def spiccato(n, vel=0.7):
    """Arco corto (spiccato): attacco netto, coda breve, sempre una nota, mai un rumore."""
    dur = 0.22; N = int((dur + 0.1) * SR); t = np.arange(N) / SR; f = hz(n); x = np.zeros(N)
    for d in (-5, 0, 5):
        p = (f * 2 ** (d / 1200) * t + rng.uniform(0, 1)) % 1.0
        x += 2 * p - 1
    x = lp_fft(x, 1800 + 2200 * vel, 2) / 3
    return x * np.minimum(1, t / 0.006) * np.exp(-t / 0.09) * vel


def onda(n, dur, bright=2600):
    """Arco che cresce e cade in una battuta (archi a ondate)."""
    x = archi(n, dur, bright, att=0.05, rel=0.05)
    t = np.arange(len(x)) / SR
    return x * (np.clip(t / dur, 0, 1) ** 1.6) * np.exp(-np.maximum(0, t - 0.85 * dur) / 0.06)


def piano_m(n, dur, vel=0.45):
    return lp_fft(piano_note(n, dur, vel), 3600, 2)


def motivo(T, t0, passo, gain=0.17, chiude=False):
    note = MOTIVO + ([77] if chiude else [])
    for i, n in enumerate(note):
        lunga = i == len(note) - 1
        T.add(piano_m(n, passo * (3.0 if lunga else 1.1), 0.5), t0 + i * passo, gain, pan=0.1)
        T.add(piano_m(n - 12, passo * (2.8 if lunga else 1.0), 0.35), t0 + i * passo, gain * 0.45, pan=0.1)


def brano(nome, stile):
    b = BRANI[nome]; dur = b["dur"]; bpm = STILI[stile]
    beat = 60 / bpm; L = 4 * beat * b["bars"]
    T = Track(dur); t = 0.0; k = 0
    nacc = int(np.ceil(dur / L))
    while t < dur:
        ch = CH[b["prog"][k % len(b["prog"])]]
        # crescendo dentro il brano (il finale sale fino a 3/4 e poi si posa)
        x = t / dur
        g = 0.55 + 0.45 * (min(1, x / 0.75) if nome == "finale" else x)
        if nome == "finale" and x > 0.8:
            g *= 0.8
        # archi tenuti (in tutti gli stili): voci gravi + raddoppio un'ottava sopra
        for j, n in enumerate(ch[:4]):
            T.add(archi(n, L + 1.2, 2200 + 300 * j, att=0.6), t - 0.15, 0.06 * g, pan=-0.45 + j * 0.3)
        for j, n in enumerate(ch[2:]):
            T.add(archi(n + 12, L + 1.2, 3400, att=0.9), t - 0.15, 0.03 * g, pan=0.45 - j * 0.3)
        steps = int(round(L / beat))
        if stile == "A":                                   # ostinato d'archi in crome
            pat = [ch[1], ch[3], ch[2], ch[3]]
            for s_ in range(steps * 2):
                acc = 1.0 if s_ % 4 == 0 else 0.75
                T.add(spiccato(pat[s_ % 4], 0.6 * acc), t + s_ * beat / 2, 0.11 * g, pan=-0.2 if s_ % 2 else 0.2)
                T.add(spiccato(pat[s_ % 4] + 12, 0.45 * acc), t + s_ * beat / 2, 0.05 * g, pan=0.3)
        elif stile == "B":                                 # arpeggio di piano in semicrome
            pat = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 12]
            for s_ in range(steps * 4):
                T.add(piano_m(pat[s_ % 6], beat * 0.6, 0.32 + 0.1 * (s_ % 4 == 0)), t + s_ * beat / 4,
                      0.07 * g, pan=-0.25 if s_ % 2 else 0.25)
        else:                                              # C: pizzicato alto + archi a ondate + piano in ottave
            pat = [ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12]
            for s_ in range(steps * 4):
                T.add(pluck(pat[s_ % 4], beat * 0.5, 0.99, 0.55), t + s_ * beat / 4,
                      0.06 * g * (1.25 if s_ % 4 == 0 else 1.0), pan=0.35 if s_ % 2 else -0.3)
            for s_ in range(0, steps, 2):
                for j, n in enumerate(ch[1:4]):
                    T.add(onda(n + 12, beat * 2, 3000), t + s_ * beat, 0.05 * g, pan=-0.3 + j * 0.3)
            if b["motivo"] is None and k % 2 == 1:
                T.add(piano_m(ch[4] + 12, beat * 3, 0.45), t, 0.09 * g, pan=0.1)
                T.add(piano_m(ch[4], beat * 3, 0.35), t, 0.05 * g, pan=0.1)
        t += L; k += 1
    if b["motivo"] is not None:
        motivo(T, b["motivo"], 60 / bpm * 1.5, chiude=b["chiude"])
    if nome == "finale":                                   # accordo finale lungo di fa minore sotto la chiusura
        tf = b["motivo"] + 4 * 60 / bpm * 1.5
        for j, n in enumerate(CH["Fm"]):
            T.add(archi(n, dur - tf + 1, 2600, att=0.8, rel=3.0), tf, 0.06, pan=-0.45 + j * 0.22)
            T.add(archi(n + 12, dur - tf + 1, 3400, att=1.2, rel=3.0), tf, 0.025, pan=0.45 - j * 0.22)
    fo = {"intro": 2.0, "macchine": 1.5}.get(nome, 4.0)
    x = T.render(fade_in=0.4, fade_out=fo, rev=0.34)
    return hp_fft(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brano", choices=list(BRANI)); ap.add_argument("stile", choices=list(STILI)); ap.add_argument("out")
    a = ap.parse_args()
    x = brano(a.brano, a.stile)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", a.out], input=x.astype("<f8").tobytes(), check=True)


if __name__ == "__main__":
    main()
