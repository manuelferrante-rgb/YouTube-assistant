#!/usr/bin/env python3
"""Traccia effetti della mappa (tools/route_map.py) con i suoni veri del kit: whoosh, tick dei km, ding.

    python3 audio/kit/mix_mappa.py out.wav [--t-a 4.1 --t-b 6.0 --dur 8 --km 13]
Stessi tempi di projects/arthunkal/map_sfx.py (un tick per km con la stessa curva del contatore, ding all'arrivo),
ma i tick si alternano tra tre click veri con piccole variazioni, così non suonano da macchinetta.
"""
import argparse, os, subprocess
import numpy as np

KIT = os.path.dirname(os.path.abspath(__file__))
SR = 48000


def load(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{KIT}/{name}.wav", "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64).reshape(-1, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--t-a", type=float, default=4.1); ap.add_argument("--t-b", type=float, default=6.0)
    ap.add_argument("--dur", type=float, default=8.0); ap.add_argument("--km", type=int, default=13)
    ap.add_argument("--ding", default="ding_mappa_provvisorio")
    a = ap.parse_args()
    out = np.zeros((int(a.dur * SR) + SR, 2))
    rng = np.random.default_rng(13)

    def put(x, t, g):
        i = int(t * SR); out[i:i + len(x)] += x[:len(out) - i] * g

    put(load("whoosh_mappa"), 0.55, 0.35)                 # unico whoosh: ci si avvicina all'India
    ticks = [load(f"tick_km_{k}") for k in (1, 2, 3)]
    ease3 = lambda u: 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    us = np.linspace(0, 1, 2000); eu = [ease3(v) for v in us]
    for km in range(1, a.km + 1):                         # contachilometri: un tick per ogni km
        t = a.t_a + (a.t_b - a.t_a) * us[np.searchsorted(eu, km / a.km - 0.5 / a.km)]
        g = (0.16 + 0.08 * (km == a.km)) * 10 ** (rng.uniform(-1.5, 1.5) / 20)
        put(ticks[(km - 1) % 3], t, g)
    put(load(a.ding), a.t_b, 0.30)                        # arrivo ad Arthunkal
    out = out[:int(a.dur * SR)]
    pk = np.abs(out).max()
    if pk > 0.89:
        out *= 0.89 / pk
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", a.out], input=out.astype("<f8").tobytes(), check=True)


if __name__ == "__main__":
    main()
