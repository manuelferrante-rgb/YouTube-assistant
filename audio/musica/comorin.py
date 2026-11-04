#!/usr/bin/env python3
"""Musica originale per i 4 reel di Capo Comorin (Kanyakumari), autore Voci Vere. Stessa tavolozza di compose.py
(piano, pizzicato, archi alti a respiri), passa-alto a 160 Hz, nessuna nota sotto i 196 Hz. Solo musica.

    python3 audio/musica/comorin.py <brano> <out.wav>
    brani: cocco (20 s, 120 bpm, a tempo con i colpi del machete: griglia nel LEGGIMI del video),
           canna, canna_gancio, canna_rivelazione, canna_chiusura,
           statua, statua_gancio, statua_rivelazione, statua_chiusura,
           mari_8.8, mari_8.0 (loop perfetto: la fine si attacca all'inizio; 8.8 s diventa 8.0 s a 1.1x)
"""
import argparse, subprocess, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import SR, Track, piano_note, pluck, swell, campana, hp_fft, reverb, lp_fft, hz, adsr  # noqa: E402


def marimba(n, dur=0.6, vel=0.7):
    """Legno intonato (parziali 1, 4, 9.9 a decadimento rapido): l'accento sul colpo, sempre una nota, mai un rumore."""
    N = int((dur + 0.4) * SR); t = np.arange(N) / SR; f = hz(n)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.06)
         + 0.12 * np.sin(2 * np.pi * 9.9 * f * t) * np.exp(-t / 0.02))
    return x * np.minimum(1, t / 0.0015) * vel


# ---------------- Reel 1, cocco: la musica porta tutto (la dorico, 120 bpm, battuta = 2 s) ----------------
def cocco():
    beat = 0.5; bar = 2.0; dur = 20.0
    T = Track(dur)
    am, c, g, em = [69, 72, 76], [67, 72, 76], [67, 71, 74], [64, 67, 71]
    prog = {1: am, 2: am, 3: g, 4: am, 5: c, 6: g, 7: am}
    # gancio, 0.0 s: primo colpo. Accordo di legno + campanella, poi una levata di pizzicato verso il groove
    for n in (69, 76, 81):
        T.add(marimba(n, 1.2, 0.8), 0.0, 0.16)
    T.add(campana(88, 1.0, 0.45), 0.0, 0.05, pan=0.3)
    for s_, n in enumerate([69, 72, 74, 76]):
        T.add(pluck(n, 0.4, 0.993, 0.5), 1.0 + s_ * 0.25, 0.07, pan=0.35 if s_ % 2 else -0.25)
    for b in range(1, 8):
        t0 = b * bar; ch = prog[b]
        arp = [ch[0], ch[1], ch[2], ch[1] + 12]
        steps = 8 if b != 6 else 4                         # battuta 6 (gli scarti): si svuota
        for s_ in range(steps):
            T.add(pluck(arp[s_ % 4], 0.45, 0.992, 0.5), t0 + s_ * (bar / steps), 0.06, pan=0.35 if s_ % 2 else -0.25)
        hits = [0, 1, 2] if b <= 4 else ([0, 2] if b == 5 else [0])   # colpi: prendi-taglia-taglia-porgi
        for h in hits:
            for n in (ch[0], ch[2]):
                T.add(marimba(n + 12 if h else n, 0.5, 0.75 if h == 0 else 0.6), t0 + h * beat, 0.13)
        if b == 5:                                          # passaggio alla polpa: arpeggio che sale, si apre in do
            for s_, n in enumerate([72, 76, 79, 84]):
                T.add(piano_note(n, 0.45, 0.5), t0 + 1.0 + s_ * 0.25, 0.12, pan=0.1)
            for j, n in enumerate(c):
                T.add(swell(n + 12, 2.4), t0, 0.035, pan=-0.4 + j * 0.4)
        if b in (2, 4):                                     # piccola melodia di piano, sopra il groove
            for s_, (n, d) in enumerate([(81, 0.5), (79, 0.25), (76, 0.25), (74, 0.5), (76, 0.5)]):
                T.add(piano_note(n, d * 0.95, 0.45), t0 + sum(x[1] for x in [(81, 0.5), (79, 0.25), (76, 0.25), (74, 0.5), (76, 0.5)][:s_]), 0.1, pan=0.1)
    # chiusura, 16 s: tre note che scendono sulla tonica, campanella che resta fino alla fine del logo
    for s_, n in enumerate([81, 79, 76, 69]):
        T.add(piano_note(n, 0.5 if s_ < 3 else 2.5, 0.5), 16.0 + s_ * 0.5, 0.14, pan=0.1)
    for n in (69, 76):
        T.add(marimba(n, 1.5, 0.6), 17.5, 0.1)
    T.add(campana(88, 2.0, 0.45), 17.5, 0.05, pan=0.3)
    for j, n in enumerate(am):
        T.add(swell(n + 12, 3.5), 16.0, 0.03, pan=-0.4 + j * 0.4)
    return hp_fft(T.render(fade_in=0.01, fade_out=1.5, rev=0.26))


# ---------------- Reel 2, canna: leggera e calda (re maggiore, 76 bpm) ----------------
def canna(dur=30.0):
    beat = 60 / 76; bar = 4 * beat
    prog = [[62, 66, 69], [59, 62, 66], [67, 71, 74], [57, 64, 69]]     # D  Bm  G  A (voci medie, calde)
    mel = [[(74, 1), (73, 0.5), (71, 0.5), (69, 2)], [(71, 1), (69, 1), (66, 2)],
           [(67, 1), (71, 0.5), (74, 0.5), (76, 2)], [(73, 1.5), (71, 0.5), (69, 2)]]
    T = Track(dur); t = 0.0; k = 0
    while t < dur:
        ch = prog[k % 4]
        for s_ in range(8):
            arp = [ch[0], ch[1], ch[2], ch[1] + 12]
            T.add(pluck(arp[s_ % 4], beat, 0.994, 0.4), t + s_ * beat / 2, 0.05, pan=0.35 if s_ % 2 else -0.25)
        for j, n in enumerate(ch):                          # archi caldi ma sopra i 196 Hz, a respiro
            T.add(swell(n if n >= 60 else n + 12, bar * 1.4, 2400), t, 0.03, pan=-0.4 + j * 0.4)
        if k >= 1 and k % 6 != 5:
            ts = t
            for n, b in mel[k % 4]:
                T.add(piano_note(n, beat * b * 0.95, 0.45), ts, 0.12, pan=0.1); ts += beat * b
        t += bar; k += 1
    return hp_fft(T.render(fade_in=0.4, fade_out=3.0, rev=0.3))


# ---------------- Reel 3, statua: mare aperto, più ampia (mi maggiore, 66 bpm) ----------------
def statua(dur=36.0):
    beat = 60 / 66; bar = 4 * beat
    prog = [[64, 71, 76], [61, 68, 73], [69, 76, 81], [66, 71, 78]]     # E  C#m  A  B/F# (quinte aperte)
    mel = [[(80, 2), (78, 1), (76, 1)], [(76, 2), (73, 2)], [(76, 1), (78, 1), (80, 2)], [(83, 2), (78, 2)]]
    T = Track(dur); t = 0.0; k = 0
    while t < dur:
        ch = prog[k % 4]
        for j, n in enumerate(ch):
            T.add(swell(n + 12 if n < 70 else n, bar * 1.7, 3600), t, 0.04, pan=-0.6 + j * 0.6)
        for s_ in range(4):                                 # pizzicato rado, a semiminime: si respira
            T.add(pluck([ch[0], ch[2], ch[1] + 12, ch[2]][s_], beat * 1.5, 0.995, 0.35), t + s_ * beat, 0.045,
                  pan=0.5 if s_ % 2 else -0.5)
        if k >= 1 and k % 5 != 4:
            ts = t
            for n, b in mel[k % 4]:
                T.add(piano_note(n, beat * b * 0.95, 0.42), ts, 0.12, pan=0.1); ts += beat * b
        if k % 4 == 2:
            T.add(campana(88, beat * 2, 0.4), t, 0.035, pan=0.4)
        t += bar; k += 1
    return hp_fft(T.render(fade_in=0.4, fade_out=3.5, rev=0.4))


def cues(video, kind):
    """Segni di gancio, rivelazione, chiusura nella tonalità del reel (canna: re; statua: mi)."""
    if video == "canna":
        beat = 60 / 76; root, tri, up, down = 62, [62, 66, 69], [69, 71, 74, 78], [78, 74, 71, 74]
    else:
        beat = 60 / 66; root, tri, up, down = 64, [64, 71, 76], [71, 76, 78, 83], [83, 80, 76, 76]
    if kind == "gancio":                    # calmo: arpeggio pizzicato che sale e resta aperto
        T = Track(3.5)
        for s_, n in enumerate([tri[0], tri[1], tri[2], tri[1] + 12]):
            T.add(pluck(n, beat * 1.4, 0.994, 0.5), 0.02 + s_ * beat / 2, 0.08, pan=0.35 if s_ % 2 else -0.25)
        T.add(campana(root + 24, beat * 2, 0.4), 0.02, 0.04, pan=0.3)
        return hp_fft(T.render(fade_in=0.01, fade_out=1.0, rev=0.4))
    if kind == "rivelazione":               # accordo sospeso che si apre, piano che sale
        T = Track(4.5)
        for j, n in enumerate([tri[0] + 12, tri[1] + 12 - 2, tri[2] + 12]):
            T.add(swell(n, 3.8), 0.0, 0.035, pan=-0.4 + j * 0.4)
        for s_, n in enumerate(up):
            T.add(piano_note(n, beat * (2.5 if s_ == 3 else 0.7), 0.5), 0.05 + s_ * beat * 0.55, 0.15, pan=0.1)
        return hp_fft(T.render(fade_in=0.02, fade_out=1.3, rev=0.42))
    if kind == "chiusura":                  # tre note che scendono sulla tonica, campanella che resta
        T = Track(5.0)
        for j, n in enumerate(tri):
            T.add(swell(n + 12, 4.0), 0.0, 0.03, pan=-0.4 + j * 0.4)
        for s_, n in enumerate(down):
            T.add(piano_note(n, beat * (2.2 if s_ == 3 else 0.8), 0.45), 0.05 + s_ * beat * 0.8, 0.15, pan=0.1)
        T.add(campana(root + 24, beat * 3, 0.45), 0.05 + 3 * beat * 0.8, 0.05, pan=0.3)
        return hp_fft(T.render(fade_in=0.02, fade_out=1.6, rev=0.42))
    raise ValueError(kind)


# ---------------- Reel 4, tre mari: 8 s in loop perfetto (3/4, 4 battute, onde che salgono e scendono) ----------
def mari(L):
    bar = L / 4; beat = bar / 3
    prog = [[64, 71, 76], [62, 69, 74], [61, 68, 73], [62, 69, 74]]     # E  D  C#m  D: gira su se stesso
    ext = L + 6.0
    T = Track(ext); T.x = np.zeros((int(ext * SR) + int(6 * SR), 2)); T.dur = ext
    for k in range(4):
        t = k * bar; ch = prog[k]
        for j, n in enumerate(ch):                          # l'onda: arco che sale e scende in una battuta e mezza
            T.add(swell(n + 12, bar * 1.5, 3800), t, 0.045, pan=-0.6 + j * 0.6)
        for s_ in range(6):                                 # risacca: pizzicato in crome che sale e torna
            n = [ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1]][s_]
            T.add(pluck(n + 12, beat, 0.995, 0.35), t + s_ * beat / 2, 0.04, pan=-0.5 + s_ * 0.2)
        T.add(piano_note([83, 81, 80, 81][k], beat * 2.5, 0.4), t, 0.1, pan=0.1)
    x = reverb(T.x[:int(ext * SR)], mix=0.42)
    n = int(round(L * SR))
    y = x[:n].copy()
    tail = x[n:]
    for i in range(0, len(tail), n):                        # code e riverbero oltre la fine ripiegati sull'inizio
        seg = tail[i:i + n]; y[:len(seg)] += seg
    y = hp_fft(y)                                           # FFT circolare: il filtro rispetta il loop
    return y / (np.abs(y).max() + 1e-9) * 0.7


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("brano"); ap.add_argument("out"); a = ap.parse_args()
    b = a.brano
    if b == "cocco":
        x = cocco()
    elif b in ("canna", "statua"):
        x = {"canna": canna, "statua": statua}[b]()
    elif b.startswith(("canna_", "statua_")):
        x = cues(*b.split("_"))
    elif b.startswith("mari_"):
        x = mari(float(b.split("_")[1]))
    else:
        raise SystemExit(f"brano sconosciuto: {b}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", a.out], input=x.astype("<f8").tobytes(), check=True)


if __name__ == "__main__":
    main()
