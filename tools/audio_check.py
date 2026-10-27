#!/usr/bin/env python3
"""Controllo del fondo nel mix prima di consegnare (Manuel, 27/10: niente rumori continui sotto la voce).

Per ogni finestra di 5 s misura il fondo (10° percentile del livello a 50 ms, cioè le pause tra le parole) e i
bassi sotto 70 Hz (rombo tipo camion/vento). Segnala le finestre sopra soglia.
    python3 tools/audio_check.py video_o_wav [--floor -42] [--low -40]
"""
import argparse, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("--floor", type=float, default=-42); ap.add_argument("--low", type=float, default=-40)
a = ap.parse_args()
SR = 16000


def pcm(af):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                                         "-af", af, "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)


def db50(x):
    h = SR // 20
    n = len(x) // h
    return 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)


full, low = db50(pcm("anull")), db50(pcm("lowpass=f=70,lowpass=f=70"))
bad = 0
for i in range(0, len(full), 100):
    f, l = np.percentile(full[i:i + 100], 10), np.percentile(low[i:i + 100], 50)
    flag = (" FONDO" if f > a.floor else "") + (" BASSI" if l > a.low else "")
    bad += bool(flag)
    print(f"{int(i / 20 // 60)}:{i / 20 % 60:04.1f}  fondo {f:6.1f} dB  bassi {l:6.1f} dB{flag}")
print(f"finestre segnalate: {bad} su {(len(full) + 99) // 100}")
