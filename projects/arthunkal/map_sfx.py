#!/usr/bin/env python3
"""Effetti sonori della mappa (tools/route_map.py, 8 s): proposta da far approvare a Manuel.

    python3 projects/arthunkal/map_sfx.py out.wav [--t-a 4.1 --t-b 6.0]
Versione 2 (indicazioni di Manuel): un solo whoosh avvicinandosi all'India, tick del contachilometri, ding leggero
all'arrivo. Niente altro.
"""
import argparse, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from sfx import sfx_file

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def pencil(dur, speed, seed=3):
    """Matita su carta: rumore acuto filtrato, a piccoli tratti irregolari, forte quanto la velocità del tratto."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(3800)) ** 2) / (2 * 0.55 ** 2))
    x = np.fft.irfft(X, n)
    grain = np.convolve(np.abs(rng.standard_normal(n // 400 + 2)), np.ones(3) / 3, "same")
    grain = np.interp(np.arange(n), np.arange(len(grain)) * 400, grain)
    x *= grain * speed(np.arange(n) / SR)
    return x / (np.abs(x).max() + 1e-9)


def ding(d=1.6):
    """Campanella leggera e pulita (arrivo)."""
    t = np.arange(int(d * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, a, tau in
            ((1318.5, 1.0, 0.55), (2637.0, 0.35, 0.3), (3951.1, 0.12, 0.18)))
    x *= np.minimum(1, t / 0.004)
    return x / np.abs(x).max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--t-a", type=float, default=4.1); ap.add_argument("--t-b", type=float, default=6.0)
    ap.add_argument("--dur", type=float, default=8.0); ap.add_argument("--km", type=int, default=13)
    a = ap.parse_args()
    out = np.zeros(int(a.dur * SR) + SR)

    def put(x, t, g):
        i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g

    put(load(sfx_file("whoosh")), 0.75, 0.30)             # unico whoosh: ci si avvicina all'India
    tA, tB = a.t_a, a.t_b
    tick = load(sfx_file("tick"))
    ease3 = lambda u: 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    us = np.linspace(0, 1, 2000)
    for km in range(1, a.km + 1):                         # contachilometri: un tick per ogni km
        u = km / a.km
        t = tA + (tB - tA) * us[np.searchsorted([ease3(v) for v in us], u - 0.5 / a.km)]
        put(tick, t, 0.10 + 0.06 * (km == a.km))
    put(ding(), tB, 0.22)                                 # arrivo ad Arthunkal: ding leggero
    out = out[:int(a.dur * SR)]
    out *= 0.89 / max(np.abs(out).max(), 1e-9) if np.abs(out).max() > 0.89 else 1.0
    with wave.open(a.out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
