#!/usr/bin/env python3
"""Musica originale di Voci Vere (composta in codice, diritti tutti nostri): fondali calmi da documentario.

    python3 audio/musica/compose.py <brano> <out.wav> [--dur S]
    brani: cammino (passo leggero, re maggiore, 72 bpm), storia (piano rado per la linea del tempo),
           arrivo (apertura piena sulla basilica), verticale (il cammino col passo da subito, 60 s)
Strumenti: tappeto di archi sintetici morbidi, piano (parziali leggermente inarmoniche + martelletto),
corde pizzicate (Karplus-Strong), riverbero di sala. Niente scale o strumenti "etnici" da cartolina.
"""
import argparse, subprocess
import numpy as np

SR = 48000
rng = np.random.default_rng(2610)


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def adsr(n, a, r, s=1.0):
    e = np.full(n, s)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    e[:na] = np.linspace(0, s, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def lp_fft(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), len(x))


def pad_note(n, dur, bright=1800):
    """Archi morbidi: 5 seghe leggermente stonate, filtrate, attacco e rilascio lenti."""
    N = int(dur * SR); t = np.arange(N) / SR
    f = hz(n)
    x = np.zeros(N)
    for d in (-7, -3, 0, 4, 8):
        ph = rng.uniform(0, 1)
        fr = f * 2 ** (d / 1200) * (1 + 0.0015 * np.sin(2 * np.pi * rng.uniform(0.1, 0.25) * t))
        p = (np.cumsum(fr) / SR + ph) % 1.0
        x += 2 * p - 1
    x = lp_fft(x, bright, 2) / 5
    return x * adsr(N, min(2.5, dur / 3), min(3.0, dur / 2.5))


def piano_note(n, dur, vel=0.7):
    N = int((dur + 2.5) * SR); t = np.arange(N) / SR
    f = hz(n); B = 0.0004
    x = np.zeros(N)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        tau = 2.8 / (k ** 0.8) * (220 / f) ** 0.35
        x += (vel ** (0.5 + 0.25 * k)) / k ** 1.1 * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6)) * np.exp(-t / tau)
    ham = rng.standard_normal(int(0.01 * SR)) * np.exp(-np.arange(int(0.01 * SR)) / (0.002 * SR)) * 0.08 * vel
    x[:len(ham)] += lp_fft(ham, 3000)
    x *= np.minimum(1, t / 0.003)
    rel = np.ones(N); i = int(dur * SR)
    rel[i:] = np.exp(-(t[i:] - dur) / 0.35)
    return x * rel


def pluck(n, dur, damp=0.996, bright=0.5):
    """Corda pizzicata smorzata (Karplus-Strong)."""
    N = int(dur * SR); p = int(SR / hz(n))
    buf = lp_fft(rng.uniform(-1, 1, p * 4), 1200 + 3000 * bright)[:p]
    y = np.zeros(N); y[:p] = buf
    for i in range(p, N):
        y[i] = damp * 0.5 * (y[i - p] + y[i - p - 1 if i - p - 1 >= 0 else 0])
    return y * adsr(N, 0.002, 0.08)


def reverb(st, dur=3.2, mix=0.32, seed=5):
    r = np.random.default_rng(seed)
    n = int(dur * SR); t = np.arange(n) / SR
    out = st.copy()
    for c in range(2):
        ir = r.standard_normal(n) * np.exp(-t / (dur / 6.5))
        ir = lp_fft(ir, 5000); ir[:int(0.012 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        L = len(st) + n
        wet = np.fft.irfft(np.fft.rfft(st[:, c], L) * np.fft.rfft(ir, L), L)[:len(st)]
        out[:, c] = (1 - mix) * st[:, c] + mix * wet * 1.6
    return out


class Track:
    def __init__(self, dur):
        self.x = np.zeros((int((dur + 6) * SR), 2)); self.dur = dur

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(max(0.0, t) * SR)
        if i >= len(self.x):
            return
        sig = sig[:len(self.x) - i] * gain
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.x[i:i + len(sig), 0] += sig * l * 1.414
        self.x[i:i + len(sig), 1] += sig * r * 1.414

    def render(self, fade_in=2.0, fade_out=4.0, rev=0.32):
        x = reverb(self.x, mix=rev)[:int(self.dur * SR)]
        t = np.arange(len(x)) / SR
        g = np.minimum(1, t / fade_in) * np.minimum(1, (self.dur - t) / fade_out)
        x *= g[:, None]
        return x / (np.abs(x).max() + 1e-9) * 0.7


# Re maggiore: I - vi - IV - Vsus (voicing larghi, note MIDI)
CHORDS = {
    "D": [50, 57, 62, 66, 69, 76], "Bm": [47, 54, 62, 66, 69, 74], "G": [43, 50, 59, 62, 66, 71],
    "Asus": [45, 52, 59, 62, 64, 69], "Em": [40, 52, 59, 62, 67, 71], "Gadd9": [43, 55, 62, 66, 69, 74],
    "Em9": [40, 52, 55, 59, 62, 66], "Cmaj7": [36, 48, 55, 59, 64, 67], "D/F#": [42, 50, 57, 62, 66, 69],
}


def colline(dur):
    """Tè di Munnar (26/10): colline e nebbia, mi minore, 64 bpm. Più raccolta di "cammino": tappeto, un piano che
    pensa (poche note, molto spazio) e un passo di corde lontano che entra a metà."""
    beat = 60 / 64; bar = 4 * beat
    prog = ["Em9", "Cmaj7", "G", "D/F#"]
    T = Track(dur); t = 0.0; k = 0
    phrases = [[71, 69, 67], [67, 66, 64, 62], [74, 71], [69, 67, 66]]
    while t < dur:
        ch = CHORDS[prog[k % 4]]; L = 2 * bar
        for j, n in enumerate(ch[1:5]):
            T.add(pad_note(n, L + 3.0, 1100 + 200 * (k % 2)), t - 0.8, 0.095, pan=-0.45 + j * 0.3)
        T.add(pad_note(ch[0], L + 3.0, 380), t - 0.8, 0.12)
        ph = phrases[k % 4]
        if k % 2 == 1 or k >= 8:
            for s_, n in enumerate(ph):
                T.add(piano_note(n, beat * 1.8, 0.42), t + 0.5 + s_ * beat * 2, 0.11, pan=0.12)
        if k >= 4:                          # passo lontano dalla seconda metà del primo minuto
            arp = [ch[2], ch[3], ch[4], ch[3]]
            for s_ in range(8):
                T.add(pluck(arp[s_ % 4], beat * 1.6, 0.993, 0.2), t + s_ * beat, 0.045, pan=-0.3 if s_ % 2 else 0.3)
        t += L; k += 1
    return T.render(fade_in=3.0, fade_out=5.0, rev=0.4)


def cammino(dur, pulse_from=2):
    bpm = 72; beat = 60 / bpm; bar = 4 * beat
    prog = ["D", "Bm", "G", "Asus"]
    T = Track(dur); t = 0.0; k = 0
    motif = [74, 73, 69, 71]           # piccolo disegno di piano, ogni 4 accordi
    while t < dur:
        ch = CHORDS[prog[k % 4]]; L = 2 * bar
        for j, n in enumerate(ch[1:5]):
            T.add(pad_note(n, L + 3.0, 1400 + 300 * (k % 3)), t - 0.8, 0.10, pan=-0.5 + j * 0.33)
        T.add(pad_note(ch[0] - 12 if ch[0] > 45 else ch[0], L + 3.0, 500), t - 0.8, 0.11)      # basso
        if k >= pulse_from:             # il passo entra dopo il primo giro (subito nei verticali)
            arp = [ch[2], ch[3], ch[4], ch[3]]
            for s in range(16):
                vel = 0.5 + 0.15 * (s % 4 == 0)
                T.add(pluck(arp[s % 4] + 12 * (s % 8 >= 6), beat * 1.2, 0.994, 0.3), t + s * beat / 2,
                      0.07 * vel, pan=0.35 if s % 2 else -0.15)
        if k % 4 == 3 and k >= 3:
            for s, n in enumerate(motif):
                T.add(piano_note(n, beat * 1.5, 0.5), t + s * beat * 1.5, 0.11, pan=0.1)
        t += L; k += 1
    return T.render()


def storia(dur):
    beat = 60 / 60
    prog = ["Bm", "G", "D", "Asus"]
    T = Track(dur); t = 0.0; k = 0
    while t < dur:
        ch = CHORDS[prog[k % 4]]; L = 8 * beat
        for j, n in enumerate(ch[1:4]):
            T.add(pad_note(n, L + 2, 1000), t, 0.09, pan=-0.3 + j * 0.3)
        T.add(pad_note(ch[0] - 12, L + 2, 400), t, 0.11)
        for s, n in enumerate([ch[3] + 12, ch[4] + 12, ch[2] + 12]):    # tre note di piano, rade
            T.add(piano_note(n, 2.2, 0.45), t + s * 2.5 + 0.5, 0.12, pan=0.15)
        t += L; k += 1
    return T.render(rev=0.38)


def arrivo(dur):
    beat = 60 / 72; bar = 4 * beat
    prog = ["G", "D", "Em", "Asus", "Gadd9", "D"]
    T = Track(dur); t = 0.0; k = 0
    while t < dur:
        ch = CHORDS[prog[k % len(prog)]]; L = 2 * bar
        grow = min(1.0, 0.45 + k * 0.12)
        for j, n in enumerate(ch[1:]):
            T.add(pad_note(n, L + 2, 1600 + 1400 * grow), t, 0.085 * grow, pan=-0.6 + j * 0.3)
            T.add(pad_note(n + 12, L + 2, 2500), t, 0.03 * grow, pan=0.6 - j * 0.3)
        T.add(pad_note(ch[0] - 12, L + 2, 450), t, 0.14)
        for s in range(4):
            T.add(piano_note(ch[2 + s % 3] + 12, beat * 2, 0.55), t + s * beat * 2, 0.09, pan=0.2)
        t += L; k += 1
    return T.render(fade_in=3.0, fade_out=6.0, rev=0.36)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brano", choices=["cammino", "storia", "arrivo", "verticale", "colline"]); ap.add_argument("out")
    ap.add_argument("--dur", type=float, default=0)
    a = ap.parse_args()
    dur = a.dur or {"cammino": 120, "storia": 64, "arrivo": 64, "verticale": 60, "colline": 240}[a.brano]
    x = {"cammino": cammino, "storia": storia, "arrivo": arrivo,
         "verticale": lambda d: cammino(d, pulse_from=0), "colline": colline}[a.brano](dur)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", a.out], input=x.astype("<f8").tobytes(), check=True)


if __name__ == "__main__":
    main()
