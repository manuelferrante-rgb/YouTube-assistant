#!/usr/bin/env python3
"""Suoni per il video sul tè di Munnar (26/10): dal girato di Manuel, e costruiti solo dove il girato non c'è.

    python3 audio/kit/te_suoni.py [--src work/te/wav]
Uscite in projects/te/audio/ (flac 48 kHz). Sorgenti: clip DJI_20261026HHMMSS della cartella Drive del video,
audio estratto in work/te/wav/HHMMSS.wav; le clip usate per gli ambienti non hanno parlato (trascrizione).
"""
import argparse, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_kit
from build_kit import load, per_ch, ROOT, SR
from sfx import _stft_filter, _reverb

OUT = f"{ROOT}/projects/te/audio"
rng = np.random.default_rng(1877)


def save(name, x, peak_db=-3.0):
    x = np.asarray(x, float)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x / (np.abs(x).max() + 1e-12) * 10 ** (peak_db / 20)
    path = f"{OUT}/{name}.flac"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "flac", "-sample_fmt", "s16", path], input=x.astype("<f8").tobytes(), check=True)
    print(path, f"{len(x) / SR:.2f} s")


def band(x, lo=None, hi=None, order=4):
    def g(t, f):
        r = np.ones_like(f)
        if lo:
            r /= np.sqrt(1 + (lo / np.maximum(f, 1)) ** order)
        if hi:
            r /= np.sqrt(1 + (f / hi) ** order)
        return r
    return per_ch(x, lambda c: _stft_filter(c, g)) if x.ndim == 2 else _stft_filter(x, g)


def loop(pieces, dur, xf=2.0):
    n = int(dur * SR); x = int(xf * SR)
    out = np.zeros((n + 60 * SR, 2)); pos = 0; k = 0
    while pos < n:
        p = pieces[k % len(pieces)].copy(); k += 1
        g = np.ones(len(p)); g[:x] = np.linspace(0, 1, x); g[-x:] = np.linspace(1, 0, x)
        out[pos:pos + len(p)] += p * g[:, None]
        pos += len(p) - x
    return out[:n]


def fades(x, a=1.5, b=2.5):
    t = np.arange(len(x)) / SR
    return x * (np.minimum(1, t / a) * np.minimum(1, (t[-1] - t) / b))[:, None]


def ambiente_colline(src, dur=60):
    """Aria tra i filari (132930, 132655): il vento sul microfono tolto sotto i 180 Hz, resta il fruscio delle
    colline. Letto per le panoramiche e per tutte le scene IA all'aperto."""
    a = load(src, "132930", 0.2, 7.0); b = load(src, "132655", 0.3, 11.5)
    x = loop([a, b], dur, xf=2.5)
    return fades(band(x, lo=180, hi=9000))


def chai(src):
    """Il chai master che tira il tè (142545, 27 s, nessuno parla): versate, tazze, il chiosco."""
    return fades(band(load(src, "142545", 0.0, 27.2), lo=90), 0.3, 1.5)


def motore(src):
    """Motore del bus sulla strada per Munnar (110437, 10 s, senza parlato): sacchi e camion del blocco 12."""
    return fades(band(load(src, "110437", 0.0, 10.2), lo=40, hi=8000), 0.8, 2.0)


def carta(dur=2.4):
    """Foglio maneggiato (costruito: grani di rumore filtrato, irregolari): contratto 1877, legge 1971. Basso."""
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    env = np.zeros(n)
    for c in np.cumsum(rng.uniform(0.05, 0.25, 30)):
        if c < dur - 0.2:
            i = int(c * SR); L = int(rng.uniform(0.03, 0.12) * SR)
            env[i:i + L] += rng.uniform(0.3, 1.0) * np.hanning(L)[:n - i]
    x = _stft_filter(x * env, lambda tt, f: np.exp(-0.5 * (np.log2(np.maximum(f, 1) / 3200) / 1.3) ** 2))
    return _reverb(x, dur=0.5, mix=0.12, bright=5000)[:n] * np.minimum(1, (dur - t) / 0.3)


def penna(dur=2.0):
    """Pennino su carta (costruito): tratti brevi e granulosi, ritmo di scrittura a mano."""
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    speed = np.zeros(n)
    for c in np.cumsum(rng.uniform(0.12, 0.35, 12)):
        if c < dur - 0.2:
            i = int(c * SR); L = int(rng.uniform(0.08, 0.22) * SR)
            speed[i:i + L] += np.hanning(L)[:n - i]
    grain = np.abs(rng.standard_normal(n // 60 + 2)); grain = np.interp(np.arange(n), np.arange(len(grain)) * 60, grain)
    x = _stft_filter(x * speed * grain, lambda tt, f: np.exp(-0.5 * (np.log2(np.maximum(f, 1) / 4500) / 0.8) ** 2))
    return x * np.minimum(1, (dur - t) / 0.2)


def orologio(src, dur=12.0):
    """Orologio a pendolo lontano nella stanza d'ufficio (blocco 4): i click veri della camera di Arthunkal,
    tic e tac alternati, con stanza."""
    arth = f"{ROOT}/work/arthunkal/girato/wav"
    tic = build_kit.click(arth, "0224", 31.294); tac = build_kit.click(arth, "0247", 8.580)
    tic = band(tic, lo=900, hi=5000); tac = band(tac, lo=700, hi=3500) * 0.8
    n = int(dur * SR); x = np.zeros(n)
    for k in range(int(dur)):
        s = tic if k % 2 == 0 else tac
        i = int((k + 0.15) * SR); x[i:i + len(s)] += s[:n - i]
    return _reverb(x, dur=1.4, mix=0.4, bright=3500)[:n]


def fabbrica(dur=20.0):
    """PROVVISORIO (nessuna fabbrica nel girato), blocco 8: ventole dell'appassimento (aria calda, rumore lento) e un
    ronzio elettrico a 50 Hz, molto bassi. Senza colpi di macchine inventati."""
    n = int(dur * SR); t = np.arange(n) / SR
    air = _stft_filter(rng.standard_normal(n), lambda tt, f: 1 / np.sqrt(1 + (f / 900) ** 2) / np.sqrt(1 + (120 / np.maximum(f, 1)) ** 4))
    air *= 1 + 0.15 * np.sin(2 * np.pi * 0.21 * t)
    blade = 1 + 0.08 * np.sin(2 * np.pi * 23.0 * t)            # pale della ventola
    hum = sum(a * np.sin(2 * np.pi * 50 * k * t) for k, a in ((1, 1.0), (2, 0.5), (3, 0.25), (4, 0.1)))
    x = air / np.abs(air).max() * blade + 0.12 * hum
    return np.stack([x, np.roll(x, 911)], 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=f"{ROOT}/work/te/wav")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    save("ambiente_colline", ambiente_colline(a.src))
    save("chai_tirato", chai(a.src))
    save("motore_camion", motore(a.src))
    save("carta", carta(), peak_db=-9)
    save("penna", penna(), peak_db=-12)
    save("orologio_lontano", orologio(a.src), peak_db=-12)
    save("fabbrica_provvisorio", fades(fabbrica(), 2.0, 3.0), peak_db=-9)


if __name__ == "__main__":
    main()
