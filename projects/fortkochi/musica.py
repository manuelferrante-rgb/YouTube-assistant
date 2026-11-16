#!/usr/bin/env python3
"""Musica originale del lungo fortkochi (Ashwasa Bhavan e Raksha, Kochi), autore Voci Vere. La fa Montaggio
(Manuel 16/11: "la chat Audio per ora non la uso, l'audio generalo tu"; poca, solo dove cala l'attenzione).

    python3 projects/fortkochi/musica.py <brano> <out.wav>
    brani: apertura (~34 s, sotto VO1-VO2 fino alla sigla), giornata (~50 s, VO9-VO10: la vita di casa),
           raksha (~28 s, VO15-VO16), finale (~45 s, VO23, VO24 e la chiusura)
Carattere: calda e seria, accompagna senza commuovere (niente pietà, niente epica). Mi bemolle maggiore, 80 bpm,
arpeggio di piano morbido sopra archi che respirano, un accordo ogni due battute, crescendo leggero dentro il brano.
Stessi strumenti e regole della musica di coir (audio/musica/coir.py): niente tappeto basso, voce più grave >= fa3,
passa-alto ripido a 160 Hz, raddoppi in alto per il telefono.
"""
import os, subprocess, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/audio/musica")
from compose import SR, Track, hp_fft  # noqa: E402
from coir import archi, piano_m, onda  # noqa: E402

CH = {   # Mi bemolle maggiore, voicing aperti, nota più grave >= fa3 (53)
    "Eb": [55, 58, 63, 67, 70], "Cm": [55, 60, 63, 67, 72], "Ab": [56, 60, 63, 68, 72],
    "Bb": [58, 62, 65, 70, 74], "Gm": [55, 58, 62, 67, 70], "Absus": [56, 61, 63, 68, 73], "Fm": [53, 60, 65, 68, 72],
}
BRANI = {
    "apertura": dict(dur=34.0, prog=["Eb", "Cm", "Ab", "Bb"], arp=0.55),
    "giornata": dict(dur=50.0, prog=["Ab", "Eb", "Cm", "Bb", "Ab", "Eb", "Fm", "Bb"], arp=0.8),
    "raksha":   dict(dur=28.0, prog=["Cm", "Ab", "Eb", "Bb"], arp=0.6),
    "finale":   dict(dur=45.0, prog=["Ab", "Bb", "Gm", "Cm", "Ab", "Bb", "Eb", "Eb"], arp=0.7),
}
BPM = 80


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
    if nome == "finale":                                    # accordo lungo di mi bemolle sotto la chiusura
        tf = dur - 9.0
        for j, n in enumerate(CH["Eb"]):
            T.add(archi(n, 9.5, 2600, att=1.5, rel=3.5), tf, 0.05, pan=-0.45 + j * 0.22)
    x = T.render(fade_in=1.5, fade_out=4.0, rev=0.36)
    return hp_fft(x)


if __name__ == "__main__":
    nome, out = sys.argv[1], sys.argv[2]
    x = brano(nome)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", out], input=x.astype("<f8").tobytes(), check=True)
