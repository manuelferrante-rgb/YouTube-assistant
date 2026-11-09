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


RNN_URL = "https://raw.githubusercontent.com/GregorR/rnnoise-models/master/conjoined-burgers-2018-08-28/cb.rnnn"
RNN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "rnnoise", "cb.rnnn")


def clean_rnn(src, out):
    """RNNoise (rete neurale addestrata sul parlato, filtro arnndn di ffmpeg): toglie vento, motori e strada molto più
    della riduzione spettrale (gancio 115233, 27/10 sera: pause da -27 a -59 dB, voce intatta). Il filtro ritarda di
    480 campioni a 48 kHz (10 ms, misurato): si tolgono, così il labiale non cambia.
    volume=0.5 (4/11, comorin): il mono di ffmpeg somma i canali (+3 dB) e su una registrazione a 0 dBFS arnndn
    saturava (crepitio su "Thiruvalluvar"); il livello lo rimette a posto la normalizzazione del montaggio."""
    if not os.path.exists(RNN):
        os.makedirs(os.path.dirname(RNN), exist_ok=True)
        subprocess.run(["curl", "-sSfL", "-o", RNN, RNN_URL], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:a:0", "-ar", str(SR), "-af",
                    f"aformat=channel_layouts=mono,volume=0.5,highpass=f=100,highpass=f=100,arnndn=m={RNN},"
                    "atrim=start_sample=480,asetpts=PTS-STARTPTS,pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_s16le", out],
                   check=True)
    print(f"voce pulita (RNNoise) {os.path.basename(src)}", flush=True)
    return out


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
    out = f"{workdir}/voce_rnn_{os.path.splitext(os.path.basename(src))[0]}.wav"
    if not os.path.exists(out):
        clean_rnn(src, out)
    return out


if __name__ == "__main__":
    clean_rnn(sys.argv[1], sys.argv[2])


def _gate(y, depth_db=-25.0, rel=0.2, pre=0.06, thr=0.3):
    """Gate dolce: fuori dalle parole (con pre s prima e rel s dopo ogni tratto di voce) il suono scende di depth_db."""
    hv = 480
    m = len(y) // hv
    dv = 20 * np.log10(np.sqrt((y[:m * hv].reshape(m, hv) ** 2).mean(1)) + 1e-9)
    dv = np.convolve(dv, np.ones(5) / 5, mode="same")
    lo, hi = np.percentile(dv, 10), np.percentile(dv, 95)
    on = np.convolve((dv > lo + thr * (hi - lo)).astype(float), np.ones(int((pre + rel) * 100) + 1),
                     mode="full")[int(pre * 100):int(pre * 100) + m] > 0
    g = np.convolve(np.where(on, 1.0, 10 ** (depth_db / 20)), np.ones(3) / 3, mode="same")
    return y[:m * hv] * np.interp(np.arange(m * hv), (np.arange(m) + 0.5) * hv, g)


def gated(src, workdir, depth_db=-25.0, double=False):
    """RNNoise + gate dolce nelle pause (8/11, arthunkal: folla e altoparlanti davanti alla basilica). double: un secondo
    passaggio di RNNoise sulla voce già pulita (fondo nelle micro-pause da -34 a -40 dB, voce invariata). Stessi tempi."""
    out = f"{workdir}/voce_gate{'2' if double else ''}_{os.path.splitext(os.path.basename(src))[0]}.wav"
    if not os.path.exists(out):
        af = f"arnndn=m={RNN},atrim=start_sample=480,asetpts=PTS-STARTPTS" if double else "anull"
        c = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", cleaned(src, workdir), "-ac", "1", "-ar", str(SR),
                                          "-af", af, "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
        y = _gate(c.astype(np.float64), depth_db, pre=0.15, thr=0.2)   # attacchi morbidi ("Qui") salvi
        sf.write(out, np.stack([y, y], 1).astype(np.float32), SR, subtype="PCM_16")
    return out


def light(src, workdir, nr=12):
    """Pulizia leggera (passa-alto + riduzione spettrale, niente RNNoise) per chi parla piano e lontano dal microfono:
    RNNoise la scambia per rumore e la cancella (8/11, la pellegrina di arthunkal: da -28 a -50 dB). Ritardo di afftdn
    tolto, stessi tempi della clip."""
    out = f"{workdir}/voce_light_{os.path.splitext(os.path.basename(src))[0]}.wav"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:a:0", "-ar", str(SR), "-af",
                        f"aformat=channel_layouts=mono,highpass=f=120,highpass=f=120,afftdn=nf=-30:nr={nr},"
                        "atrim=start_sample=1200,asetpts=PTS-STARTPTS,pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_s16le", out],
                       check=True)
    return out
