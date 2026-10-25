#!/usr/bin/env python3
"""Kit sonoro di Voci Vere costruito dai suoni veri del girato (prima versione: Arthunkal, 25/10).

    python3 audio/kit/build_kit.py [--src work/arthunkal/girato/wav]

Sorgenti (girato di Manuel, cartella Drive 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX, audio estratto a 48 kHz):
- mimo_140234 / mimo_140104: onde e vento sulla spiaggia di Marari, senza voci (23/10)
- 0224 e 0247: click secchi di presa/manipolazione della camera (23-24/10)
Uscite in audio/kit/ (wav 48 kHz 24 bit stereo). Ogni file ha la sua riga in audio/catalogo.md.
"""
import argparse, os, subprocess, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from sfx import _stft_filter, _reverb

SR = 48000
OUT = f"{ROOT}/audio/kit"


def load(src, name, t0, dur, mono=False):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(dur), "-i", f"{src}/{name}.wav",
                          "-ac", "1" if mono else "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x if mono else x.reshape(-1, 2)


def save(name, x, peak_db=-1.5):
    x = np.asarray(x, np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = x / (np.abs(x).max() + 1e-12) * 10 ** (peak_db / 20)
    path = f"{OUT}/{name}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", path], input=x.astype("<f8").tobytes(), check=True)
    print(path, f"{len(x) / SR:.2f} s")


def per_ch(x, fn):
    return np.stack([fn(x[:, c]) for c in range(x.shape[1])], 1)


def sweep(x, f0, f1, q=1.3, floor=0.15):
    """Banda che sale da f0 a f1 lungo il suono (log), con un po' di segnale pieno sotto."""
    d = len(x) / SR

    def g(t, f):
        fc = f0 * (f1 / f0) ** min(1.0, t / d)
        return floor + (1 - floor) * np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) / q) ** 2)
    return per_ch(x, lambda c: _stft_filter(c, g))


def opening(x, f0, f1, t_open):
    """Passa-basso che si apre da f0 a f1 in t_open secondi (come uscire da sott'acqua, ma breve)."""
    def g(t, f):
        fc = f0 * (f1 / f0) ** min(1.0, t / t_open)
        return 1 / np.sqrt(1 + (f / fc) ** 4)
    return per_ch(x, lambda c: _stft_filter(c, g))


def transizione_zoom_nero(src):
    """Zoom nel nero: un'onda vera che monta (0.7 s), taglio netto e 0.2 s di silenzio (il nero).
    Il taglio cade sull'ultimo fotogramma prima del nero."""
    x = load(src, "mimo_140234", 9.10, 0.75)               # onda che sale da -28 a -16 dB
    x = sweep(x, 350, 3200)
    t = np.arange(len(x)) / SR
    env = (t / t[-1]) ** 2.2                              # crescendo
    env[-int(0.012 * SR):] *= np.linspace(1, 0, int(0.012 * SR))   # taglio secco ma senza click
    x = x * env[:, None]
    return np.concatenate([x, np.zeros((int(0.2 * SR), 2))])


def uscita_nero(src):
    """Uscita dal nero: l'onda arriva da lontano (passa-basso che si apre) e poi lascia spazio
    all'audio della scena nuova. 1.8 s."""
    x = load(src, "mimo_140104", 0.0, 1.8)
    x = opening(x, 280, 16000, 0.55)
    t = np.arange(len(x)) / SR
    env = np.minimum(1, t / 0.30) ** 1.5 * np.where(t < 0.7, 1, np.exp(-(t - 0.7) / 0.6))
    return x * env[:, None]


def whoosh_mappa(src):
    """Unico whoosh della mappa (ci si avvicina all'India): vento e onda che salgono e ricadono, 1.3 s."""
    x = load(src, "mimo_140234", 2.70, 1.3)               # onda dei 3.2-3.6 s
    x = sweep(x, 300, 2400, q=1.1, floor=0.1)
    t = np.arange(len(x)) / SR
    env = np.sin(np.pi * np.clip(t / t[-1], 0, 1)) ** 1.6
    return x * env[:, None]


CLICKS = [("0224", 31.294), ("0224", 40.590), ("0247", 8.580)]


def click(src, name, t):
    """Click vero, ripulito: 45 ms dall'attacco, passa-alto, coda che si chiude."""
    x = load(src, name, t - 0.006, 0.05, mono=True)
    i = np.argmax(np.abs(x[:int(0.02 * SR)]))
    x = x[max(0, i - int(0.002 * SR)):][:int(0.045 * SR)]
    x = _stft_filter(x, lambda tt, f: 1 / np.sqrt(1 + (700 / np.maximum(f, 1)) ** 4), n=256, hop=64)
    t = np.arange(len(x)) / SR
    return x * np.exp(-t / 0.012)


def ding_mappa(src):
    """PROVVISORIO (nel girato non ci sono campane né colpi metallici): il click vero di 0224 fa suonare
    un bicchiere d'acciaio da chai ricostruito (modi del bicchiere, battimenti leggeri). Da sostituire
    con una registrazione vera appena Manuel la manda."""
    exc = click(src, "0224", 40.590)
    d = 1.6
    t = np.arange(int(d * SR)) / SR
    modes = ((1320.0, 1.0, 0.70), (1321.6, 0.5, 0.65), (3460.0, 0.30, 0.30), (6530.0, 0.10, 0.14))
    ir = sum(a * np.sin(2 * np.pi * f * t + 0.3 * k) * np.exp(-t / tau) for k, (f, a, tau) in enumerate(modes))
    n = len(exc) + len(ir)
    x = np.fft.irfft(np.fft.rfft(exc, n) * np.fft.rfft(ir, n), n)[:len(ir)]
    x = x / np.abs(x).max() + np.pad(exc / np.abs(exc).max() * 0.15, (0, len(ir) - len(exc)))  # + attacco vero
    return _reverb(x, dur=0.8, mix=0.12, bright=6000)[:len(ir)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=f"{ROOT}/work/arthunkal/girato/wav")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    save("transizione_zoom_nero", transizione_zoom_nero(a.src))
    save("uscita_nero", uscita_nero(a.src))
    save("whoosh_mappa", whoosh_mappa(a.src))
    for k, (n, t) in enumerate(CLICKS, 1):
        save(f"tick_km_{k}", click(a.src, n, t), peak_db=-3)
    save("ding_mappa_provvisorio", ding_mappa(a.src), peak_db=-3)


if __name__ == "__main__":
    main()
