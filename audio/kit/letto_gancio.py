#!/usr/bin/env python3
"""Letto sonoro naturale per un gancio calmo (Arthunkal, 26/10): onde vere e rosario lontano, dal girato.

    python3 audio/kit/letto_gancio.py [--src work/arthunkal/girato/wav] [--dur 40]
Uscite in projects/arthunkal/audio/: letto_onde.wav, rosario_lontano.wav (separati, per abbassare il rosario sotto le
voci) e letto_gancio.wav (già insieme: rosario 14 dB sotto le onde).
Sorgenti: mimo_140234 (onde, spiaggia di Marari 23/10), 0264 (rosario cantato sul cammino, 24/10, senza il "yeah"
a 3.3-4.7 s), 0234 (mormorio della folla di notte, 24/10).
"""
import argparse, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_kit import load, save, per_ch, ROOT, SR
from sfx import _stft_filter, _reverb


def loop(pieces, dur, xf=2.0):
    """Incolla i pezzi in giro con dissolvenze incrociate finché arriva a dur secondi."""
    n = int(dur * SR); x = int(xf * SR)
    out = np.zeros((n + 40 * SR, 2)); pos = 0; k = 0
    while pos < n:
        p = pieces[k % len(pieces)].copy(); k += 1
        g = np.ones(len(p)); g[:x] = np.linspace(0, 1, x); g[-x:] = np.linspace(1, 0, x)
        out[pos:pos + len(p)] += p * g[:, None]
        pos += len(p) - x
    return out[:n]


def lontano(x, fc=1500):
    x = per_ch(x, lambda c: _stft_filter(c, lambda t, f: 1 / np.sqrt(1 + (f / fc) ** 4)))
    return np.stack([_reverb(x[:, c], dur=2.0, mix=0.45, bright=2500)[:len(x)] for c in range(2)], 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=f"{ROOT}/work/arthunkal/girato/wav"); ap.add_argument("--dur", type=float, default=40)
    a = ap.parse_args()
    import build_kit
    build_kit.OUT = f"{ROOT}/projects/arthunkal/audio"
    onde = loop([load(a.src, "mimo_140234", 0.3, 18.6), load(a.src, "mimo_140104", 0.2, 4.0)], a.dur, xf=2.5)
    canto = loop([load(a.src, "0264", 0.0, 3.3), load(a.src, "0264", 4.7, 7.1), load(a.src, "0234", 0.2, 3.8)], a.dur, xf=1.2)
    canto = lontano(canto)
    t = np.arange(len(onde)) / SR
    fade = (np.minimum(1, t / 1.5) * np.minimum(1, (a.dur - t) / 2.5))[:, None]
    onde *= fade; canto *= fade
    save("letto_onde", onde, peak_db=-3)
    save("rosario_lontano", canto, peak_db=-3)
    on = onde / np.abs(onde).max(); ca = canto / np.abs(canto).max()
    save("letto_gancio", on + ca * 10 ** (-14 / 20), peak_db=-3)


if __name__ == "__main__":
    main()
