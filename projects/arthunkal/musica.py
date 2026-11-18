#!/usr/bin/env python3
"""Musica originale del lungo arthunkal rifatto (18/11), autore Voci Vere. La fa Montaggio come per fortkochi
(Manuel 16-17/11: poca e bassa, solo dove cala l'attenzione). Modello: projects/fortkochi/musica.py.

    python3 projects/arthunkal/musica.py <brano> <out.wav>
    brani: apertura (~42 s, la notte fino al nome del posto), cammino (~40 s), storia (~40 s, basilica e date),
           finale (~40 s, chiusura)
Carattere: notte e cammino, raccolta e seria, con un passo lento (niente epica, niente pietà). Re minore / Fa maggiore,
72 bpm, archi tenuti, arpeggio di piano rado; stessi strumenti di coir e fortkochi (passa-alto a 160 Hz, nota grave >= fa3).
"""
import os, subprocess, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/audio/musica")
from compose import SR, Track, hp_fft  # noqa: E402
from coir import archi, piano_m, onda  # noqa: E402

CH = {   # Re minore / Fa maggiore, voicing aperti, nota più grave >= fa3 (53)
    "Dm": [57, 62, 65, 69, 74], "Bb": [58, 62, 65, 70, 74], "F": [57, 60, 65, 69, 72], "C": [55, 60, 64, 67, 72],
    "Gm": [55, 58, 62, 67, 70], "Am": [57, 60, 64, 69, 72], "Bbmaj7": [57, 62, 65, 70, 74],
}
BRANI = {
    "apertura": dict(dur=42.0, prog=["Dm", "Bb", "F", "C"], arp=0.5),
    "cammino":  dict(dur=40.0, prog=["Dm", "Bb", "Gm", "C", "Dm", "F", "Bb", "C"], arp=0.75),
    "storia":   dict(dur=40.0, prog=["Bbmaj7", "F", "Gm", "Dm", "Bb", "F", "C", "C"], arp=0.6),
    "finale":   dict(dur=40.0, prog=["Bb", "C", "Am", "Dm", "Bb", "C", "F", "F"], arp=0.7),
}
BPM = 72


def brano(nome):
    b = BRANI[nome]; dur = b["dur"]; beat = 60 / BPM; L = 8 * beat
    T = Track(dur); t = 0.0; k = 0
    while t < dur:
        ch = CH[b["prog"][k % len(b["prog"])]]
        x = t / dur
        g = 0.5 + 0.5 * min(1, x / 0.7)
        if nome == "finale" and x > 0.8:
            g *= 0.85
        for j, n in enumerate(ch[:4]):                      # archi tenuti
            T.add(archi(n, L + 1.4, 2200 + 250 * j, att=1.2, rel=2.0), t - 0.2, 0.055 * g, pan=-0.45 + j * 0.3)
        for j, n in enumerate(ch[2:]):                      # raddoppio alto, si sente anche dal telefono
            T.add(archi(n + 12, L + 1.4, 3300, att=1.5, rel=2.0), t - 0.2, 0.026 * g, pan=0.45 - j * 0.3)
        pat = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 12]
        steps = int(round(L / beat)) * 2                    # crome: muove senza correre
        for s_ in range(steps):
            if x < 0.12 and s_ % 2:                         # l'inizio più rado, poi l'arpeggio si riempie
                continue
            T.add(piano_m(pat[s_ % 6], beat * 0.9, 0.3 + 0.08 * (s_ % 4 == 0)), t + s_ * beat / 2,
                  0.07 * g * b["arp"], pan=-0.22 if s_ % 2 else 0.22)
        if k % 2 == 1:                                      # una nota lunga in alto ogni due accordi, niente motivo
            T.add(piano_m(ch[4] + 12, beat * 4, 0.4), t + 2 * beat, 0.06 * g, pan=0.1)
        T.add(onda(ch[3] + 12, beat * 2, 3200), t + L - beat * 2, 0.035 * g, pan=0.2)   # respiro verso il cambio
        t += L; k += 1
    if nome == "finale":                                    # accordo lungo di fa sotto la chiusura
        tf = dur - 9.0
        for j, n in enumerate(CH["F"]):
            T.add(archi(n, 9.5, 2600, att=1.5, rel=3.5), tf, 0.05, pan=-0.45 + j * 0.22)
    x = T.render(fade_in=1.5, fade_out=4.0, rev=0.36)
    return hp_fft(x)


if __name__ == "__main__":
    nome, out = sys.argv[1], sys.argv[2]
    x = brano(nome)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", out], input=x.astype("<f8").tobytes(), check=True)
