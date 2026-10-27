#!/usr/bin/env python3
"""Voce pulita dalle clip girate (Manuel 27/10 sera: sotto chi parla solo la sua voce, niente rombo tipo camion).

Passa-alto a 100 Hz (rombo di motori e vento) e riduzione spettrale del rumore stimato clip per clip: per ogni
banda il fondo è il livello più basso (10° percentile) in finestre di 2 s, così segue anche un rumore che cambia
(un mezzo che passa). Nelle pause tra le parole il fondo scende di circa 18 dB, la voce resta com'è.
Scrive un wav 48 kHz stereo con gli stessi tempi della clip (il labiale non cambia: nessun ritardo).
    python3 tools/voice_clean.py clip.mp4 out.wav
    from voice_clean import cleaned; wav = cleaned(clip, workdir)
"""
import os, subprocess, sys
import numpy as np, soundfile as sf

SR, N, HOP = 48000, 2048, 512


def clean(src, out, floor=None, alpha=None):
    """floor/alpha None: forza scelta dal rapporto voce/fondo della clip (misurato 27/10 sul gancio 115233:
    fondo nelle pause -12 dB con 0.06/4, voce -4 dB prima della normalizzazione per inquadratura)."""
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                                      "-af", "highpass=f=100,highpass=f=100", "-f", "f32le", "-"],
                                     capture_output=True, check=True).stdout, np.float32).astype(np.float64)
    L = len(x)
    h = SR // 20
    d = 20 * np.log10(np.sqrt((x[:len(x) // h * h].reshape(-1, h) ** 2).mean(1)) + 1e-9)
    snr = np.percentile(d, 90) - np.percentile(d, 10)
    noisy = snr < 22                                               # strada, vento, motori: riduzione forte
    floor = floor or (0.06 if noisy else 0.13)
    alpha = alpha or (4.0 if noisy else 2.0)
    print(f"voce pulita {os.path.basename(src)}: voce/fondo {snr:.0f} dB -> {'forte' if noisy else 'leggera'}", flush=True)
    xp = np.concatenate([np.zeros(N), x, np.zeros(N + HOP)])
    win = np.hanning(N + 1)[:N]
    nf = (len(xp) - N) // HOP
    idx = np.arange(N)[None, :] + HOP * np.arange(nf)[:, None]
    S = np.fft.rfft(xp[idx] * win, axis=1)
    P = np.abs(S) ** 2
    Ps = np.copy(P)
    Ps[1:-1] = (P[:-2] + P[1:-1] + P[2:]) / 3                      # potenza smussata nel tempo
    # fondo per banda: 10° percentile in blocchi di 2 s, poi il minimo tra blocchi vicini (robusto alla voce)
    B = int(2 * SR / HOP)
    nb = max(1, nf // B)
    blk = np.array([np.percentile(Ps[i * B:(i + 1) * B if i < nb - 1 else nf], 10, axis=0) for i in range(nb)])
    blk = np.minimum(blk, np.minimum(np.roll(blk, 1, 0), np.roll(blk, -1, 0))) if nb > 2 else blk
    centers = (np.arange(nb) + 0.5) * B
    Nz = np.array([np.interp(np.arange(nf), centers, blk[:, k]) for k in range(P.shape[1])]).T
    G = np.clip(1 - alpha * Nz / (Ps + 1e-20), floor, 1.0)
    k = np.ones(5) / 5                                             # niente "rumore musicale": guadagno smussato
    G = np.apply_along_axis(lambda g: np.convolve(g, k, mode="same"), 1, G)
    G = np.apply_along_axis(lambda g: np.convolve(g, np.ones(3) / 3, mode="same"), 0, G)
    y = np.fft.irfft(S * G, n=N, axis=1) * win
    o = np.zeros(len(xp)); wsum = np.zeros(len(xp))
    for i in range(nf):
        o[i * HOP:i * HOP + N] += y[i]; wsum[i * HOP:i * HOP + N] += win ** 2
    o = (o / np.maximum(wsum, 1e-3))[N:N + L]
    o = np.clip(o / np.sqrt(2), -1, 1)                             # stesso livello del mono di ffmpeg
    sf.write(out, np.stack([o, o], 1).astype(np.float32), SR, subtype="PCM_16")
    return out


def cleaned(src, workdir):
    os.makedirs(workdir, exist_ok=True)
    out = f"{workdir}/voce_{os.path.splitext(os.path.basename(src))[0]}.wav"
    if not os.path.exists(out):
        clean(src, out)
    return out


if __name__ == "__main__":
    clean(sys.argv[1], sys.argv[2])
