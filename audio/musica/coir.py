#!/usr/bin/env python3
"""Musica originale del lungo coir (le donne del coir, Anathalavattom, Kerala), autore Voci Vere. Solo musica.

    python3 audio/musica/coir.py <brano> <out.wav> [--dur S]
    brani: intro (VO0 fino alla sigla)  [prove successive: strada, laguna, macchine, finale]

Brief di Copy (copioni/coir_audio_brief.md): piu' profonda e seria degli ultimi video, meno melodia, piu' tappeto,
armonia lenta e scura; dignita', peso, calma; niente pieta', niente epica. Fa minore.
Regola di Manuel (27-28/10): niente tappeto BASSO. La profondita' viene dai medio-bassi (voce piu' grave fa3 = 175 Hz,
archi gravi tra 175 e 400 Hz), passa-alto ripido a 160 Hz su tutto, controllo con audio/kit/bande.py.
Motivo di tre note (MOTIVO): fa - la bemolle - sol, una domanda che resta aperta ("chi li ha fatti?"). Torna
nell'intro, nella laguna e nel finale, dove si chiude sul fa.
"""
import argparse, subprocess, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import SR, Track, piano_note, hp_fft, lp_fft, hz, adsr, rng  # noqa: E402

MOTIVO = [77, 80, 79]          # fa5 - lab5 - sol5 (v2: un'ottava sopra, si sente anche dal telefono)


def archi(n, dur, bright=900, att=2.0, rel=2.5):
    """Archi gravi e scuri: 4 seghe poco stonate, filtro chiuso, vibrato lentissimo, attacco d'arco lento."""
    N = int(dur * SR); t = np.arange(N) / SR; f = hz(n); x = np.zeros(N)
    for d in (-5, -2, 2, 5):
        fr = f * 2 ** (d / 1200) * (1 + 0.0012 * np.sin(2 * np.pi * rng.uniform(0.08, 0.18) * t + rng.uniform(0, 6)))
        p = (np.cumsum(fr) / SR + rng.uniform(0, 1)) % 1.0
        x += 2 * p - 1
    x = lp_fft(x, bright, 2) / 4
    return x * adsr(N, min(att, dur / 3), min(rel, dur / 2.5))


def piano_scuro(n, dur, vel=0.4):
    """Piano col feltro: stessa nota di compose.piano_note, ma piu' morbida (alti tagliati)."""
    x = piano_note(n, dur, vel)
    return lp_fft(x, 3200, 2)


def motivo(T, t0, passo, gain=0.13, chiude=False):
    """Il motivo: tre note lente del piano scuro, raddoppiate piano all'ottava sotto. Se chiude, si posa sul fa."""
    note = MOTIVO + ([77] if chiude else [])
    for i, n in enumerate(note):
        lunga = (i == len(note) - 1)
        T.add(piano_scuro(n, passo * (2.6 if lunga else 1.1), 0.42), t0 + i * passo, gain, pan=0.1)
        T.add(piano_scuro(n - 12, passo * (2.4 if lunga else 1.0), 0.3), t0 + i * passo, gain * 0.35, pan=0.1)


def intro(dur=10.0):
    """VO0 "Su quei tappeti c'e' scritto Made in India. Non c'e' scritto chi li ha fatti." fino alla sigla.
    Un solo accordo che respira (fa minore, poi re bemolle sotto il sol del motivo), archi gravi, il motivo
    a meta' frase, e resta sospeso sul sol: la domanda non ha risposta finche' non arriva il finale."""
    T = Track(dur)
    fm = [53, 60, 65, 68]                          # fa3 do4 fa4 lab4: il fondo serio, senza basso
    dbm7 = [53, 61, 65, 68]                        # fa3 reb4 fa4 lab4: lo stesso fondo che si scurisce
    # v2 (6/11): sul telefono i medio-bassi quasi non si sentono. Archi piu' aperti (filtro 1600-2200 Hz) e la
    # stessa armonia raddoppiata un'ottava sopra, cosi' si sente anche dall'altoparlante; resta scura e lenta.
    for j, n in enumerate(fm):
        T.add(archi(n, 6.5, 2200 + 300 * j, att=2.2), 0.0, 0.09 if n < 60 else 0.07, pan=-0.35 + j * 0.23)
        T.add(archi(n + 12, 6.5, 3200, att=2.6), 0.0, 0.035, pan=0.35 - j * 0.23)
    for j, n in enumerate(dbm7):
        T.add(archi(n, dur - 4.6 + 2.0, 2200 + 300 * j, att=1.8), 4.6, 0.09 if n < 60 else 0.07, pan=-0.35 + j * 0.23)
        T.add(archi(n + 12, dur - 4.6 + 2.0, 3200, att=2.2), 4.6, 0.035, pan=0.35 - j * 0.23)
    T.add(archi(72, dur - 1.0, 2400, att=3.5), 1.0, 0.04, pan=0.4)       # un filo alto (do5)
    motivo(T, 2.4, 1.15, gain=0.17)
    x = T.render(fade_in=1.2, fade_out=2.5, rev=0.42)
    return hp_fft(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brano", choices=["intro"]); ap.add_argument("out")
    ap.add_argument("--dur", type=float, default=0)
    a = ap.parse_args()
    x = {"intro": lambda: intro(a.dur or 10.0)}[a.brano]()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", a.out], input=x.astype("<f8").tobytes(), check=True)


if __name__ == "__main__":
    main()
