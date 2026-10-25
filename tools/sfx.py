#!/usr/bin/env python3
"""Effetti sonori cinematografici sintetizzati (nessun diritto da gestire): colpi, whoosh, riser, flash, logo.

    python3 tools/sfx.py [cartella]        # genera tutti i file .wav (default models/sfx)
Uso dal montaggio: sfx_file("hit") -> percorso del wav (lo genera se manca).
Effetti brevi e asciutti, pensati per i tagli dell'intro e per la sigla: niente musica.
"""
import os, sys, wave
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = f"{ROOT}/models/sfx"
SR = 48000
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _noise(d):
    return rng.standard_normal(int(d * SR))


def _stft_filter(x, gain_fn, n=1024, hop=256):
    """Filtro variabile nel tempo: gain_fn(tempo, frequenze) -> guadagno per ogni bin."""
    w = np.hanning(n)
    pad = np.concatenate([np.zeros(n), x, np.zeros(n)])
    out = np.zeros_like(pad); norm = np.zeros_like(pad)
    f = np.fft.rfftfreq(n, 1 / SR)
    for i in range(0, len(pad) - n, hop):
        X = np.fft.rfft(pad[i:i + n] * w)
        X *= gain_fn(max(0.0, (i - n + n / 2) / SR), f)
        out[i:i + n] += np.fft.irfft(X) * w
        norm[i:i + n] += w ** 2
    out /= np.maximum(norm, 1e-6)
    return out[n:n + len(x)]


def _band(fc, q=1.2):
    """Banda gaussiana in ottave attorno a fc."""
    return lambda f: np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) / q) ** 2)


def _reverb(x, dur=1.2, mix=0.25, bright=4000):
    t = _t(dur)
    ir = _noise(dur) * np.exp(-t / (dur / 5))
    ir = _stft_filter(ir, lambda tt, f: np.exp(-f / bright))
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    n = len(x) + len(ir)
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:n]
    dry = np.concatenate([x, np.zeros(len(ir))])
    return dry + mix * wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(x))


def _stereo(x, pan=None):
    """pan: array -1..1 (sinistra..destra) o None (centro)."""
    if pan is None:
        return np.stack([x, x], 1)
    p = (np.asarray(pan) + 1) / 2
    return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], 1) * np.sqrt(2)


def _norm(x, peak=0.9):
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def _sub(d, f0=62, f1=32, tau=0.45):
    t = _t(d)
    ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / 0.12)) / SR
    return np.sin(ph) * np.exp(-t / tau) * np.minimum(1, t / 0.004)


# ---------------- effetti ----------------
def boom(d=2.2):
    """Colpo basso profondo (impatto d'apertura)."""
    t = _t(d)
    x = _sub(d, 70, 30, 0.6)
    click = _stft_filter(_noise(d), lambda tt, f: np.exp(-f / 2500)) * np.exp(-t / 0.025)
    x = np.tanh(1.6 * (x + 0.5 * click))
    return _stereo(_norm(_reverb(x, 1.8, 0.35, 1800)))


def hit(d=1.4):
    """Colpo cinematografico corto: corpo basso + attacco + un filo di metallo."""
    t = _t(d)
    body = _sub(d, 90, 42, 0.28)
    snap = _stft_filter(_noise(d), lambda tt, f: _band(1800, 1.5)(f)) * np.exp(-t / 0.018)
    metal = sum(np.sin(2 * np.pi * fr * t) * np.exp(-t / tau) for fr, tau in ((173, .35), (412, .22), (761, .15))) * 0.12
    x = np.tanh(1.8 * (body + 0.7 * snap + metal))
    return _stereo(_norm(_reverb(x, 1.2, 0.3, 3000)))


def whoosh(d=0.55, rev=False):
    """Passaggio d'aria rapido tra due inquadrature (rev: cresce fino al taglio)."""
    t = _t(d)
    c = 0.62 * d
    env = np.where(t < c, (t / c) ** 2.2, np.exp(-(t - c) / (0.12 * d)))
    fc = lambda tt: 350 * (9 ** np.clip(tt / c, 0, 1)) if tt < c else 3150 * np.exp(-(tt - c) / (0.25 * d))
    x = _stft_filter(_noise(d), lambda tt, f: _band(max(fc(tt), 250), 0.9)(f)) * env
    x = _norm(x)
    if rev:
        x = x[::-1]
    return _stereo(x, np.linspace(-0.7, 0.7, len(x)))


def riser(d=1.6):
    """Tensione che sale e si interrompe sul taglio."""
    t = _t(d)
    env = (t / d) ** 2.5
    x = _stft_filter(_noise(d), lambda tt, f: _band(250 * 24 ** (tt / d), 0.7)(f)) * env
    tone = np.sin(2 * np.pi * np.cumsum(110 * 6 ** (t / d)) / SR) * env * 0.25
    return _stereo(_norm(x + tone, 0.85))


def flash(d=0.6):
    """Lampo: scatto secco brillante con una coda d'aria."""
    t = _t(d)
    shk = _stft_filter(_noise(d), lambda tt, f: (f > 3000) * 1.0) * np.exp(-t / 0.012)
    air = _stft_filter(_noise(d), lambda tt, f: _band(6000 * np.exp(-tt / 0.2), 0.8)(f)) * np.exp(-t / 0.09) * 0.5
    thump = _sub(d, 120, 60, 0.06) * 0.6
    return _stereo(_norm(_reverb(shk + air + thump, 0.6, 0.2, 7000), 0.8))


def stamp(d=1.0):
    """Colpo del logo (la V che si stampa): pieno, corto, con eco breve."""
    t = _t(d)
    body = _sub(d, 110, 48, 0.16)
    snap = _stft_filter(_noise(d), lambda tt, f: _band(1200, 1.3)(f)) * np.exp(-t / 0.012)
    x = np.tanh(2.2 * (body + 0.9 * snap))
    return _stereo(_norm(_reverb(x, 0.9, 0.35, 2500)))


def tick(d=0.12):
    """Battitura veloce (lettere che compaiono)."""
    t = _t(d)
    x = _stft_filter(_noise(d), lambda tt, f: _band(3500, 0.6)(f)) * np.exp(-t / 0.006)
    x += np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.01) * 0.3
    return _stereo(_norm(x, 0.7))


def shimmer(d=1.8):
    """Rivelazione elegante (la parola VERE in oro): soffio che sale e scintilla."""
    t = _t(d)
    rise = 0.35
    swell = _stft_filter(_noise(d), lambda tt, f: _band(2500 * 2 ** min(tt / rise, 1.5), 0.6)(f))
    swell *= np.where(t < rise, (t / rise) ** 2, np.exp(-(t - rise) / 0.08)) * 0.6
    bells = sum(np.sin(2 * np.pi * fr * t + k) * np.exp(-np.maximum(t - rise, 0) / 0.7) * (t > rise)
                for k, fr in enumerate((1318.5, 1975.5, 2637.0, 3951.1))) * 0.18
    sub = np.concatenate([np.zeros(int(rise * SR)), _sub(d - rise, 80, 40, 0.5)])[:len(t)] * 0.7
    return _stereo(_norm(_reverb(swell + bells + sub, 1.6, 0.4, 6000), 0.85))


SFX = {"boom": boom, "hit": hit, "whoosh": whoosh, "whoosh_rev": lambda: whoosh(0.7, rev=True),
       "whoosh_short": lambda: whoosh(0.32), "riser": riser, "riser_long": lambda: riser(2.6), "flash": flash,
       "stamp": stamp, "tick": tick, "shimmer": shimmer}


def write(path, x):
    nf = int(min(0.4 * SR, len(x) / 4))  # coda sfumata: mai un taglio netto
    x = x.copy(); x[-nf:] *= np.linspace(1, 0, nf)[:, None] ** 2
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def sfx_file(name):
    os.makedirs(DIR, exist_ok=True)
    p = f"{DIR}/{name}.wav"
    if not os.path.exists(p):
        write(p, SFX[name]())
    return p


if __name__ == "__main__":
    if len(sys.argv) > 1:
        DIR = sys.argv[1]
    for k in SFX:
        print(sfx_file(k))
