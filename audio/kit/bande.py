#!/usr/bin/env python3
"""Controllo dei bassi prima di consegnare: energia per banda e livello sotto 150 Hz.

    python3 audio/kit/bande.py file.wav [file2 ...]
Stampa, per ogni file: LUFS integrati, picco, quota di energia in <60, 60-150, 150-250, 250-1k, 1-4k, >4k Hz e il
livello sotto 150 Hz rispetto al totale (dB). Regola (Manuel 27/10): sotto 150 Hz niente rombo, almeno 35 dB sotto.
"""
import subprocess, sys, re
import numpy as np

SR = 48000
BANDS = [(0, 60), (60, 150), (150, 250), (250, 1000), (1000, 4000), (4000, 24000)]


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<f4").astype(np.float64)


def lufs(p):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); pk = re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", r)
    return (i[-1] if i else "?"), (pk[-1] if pk else "?")


for p in sys.argv[1:]:
    x = load(p)
    n = 1 << 15; P = np.zeros(n // 2 + 1); w = np.hanning(n)
    for i in range(0, max(1, len(x) - n), n // 2):
        seg = x[i:i + n]
        if len(seg) < n:
            break
        P += np.abs(np.fft.rfft(seg * w)) ** 2
    f = np.fft.rfftfreq(n, 1 / SR); tot = P.sum() + 1e-30
    parts = " ".join(f"{a}-{b}:{100 * P[(f >= a) & (f < b)].sum() / tot:5.1f}%" for a, b in BANDS)
    sub = 10 * np.log10(P[f < 150].sum() / tot + 1e-30)
    I, pk = lufs(p)
    print(f"{p.split('/')[-1]}: {I} LUFS, picco {pk} dBTP | {parts} | sotto 150 Hz {sub:.1f} dB "
          f"{'OK' if sub < -35 else 'TROPPO'}")
