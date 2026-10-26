#!/usr/bin/env python3
"""Musica originale tagliata sul montato: un wav unico allineato a 0:00 del lungo, silenzio fuori dai tratti.

    python3 audio/musica/sul_montato.py projects/arthunkal/audio/musica_lungo.json out.wav

Il JSON descrive i tratti (secondi del montato):
  {"durata": 341, "tratti": [{"da": 22.03, "a": 33.07, "dopo": 33.6, "brano": "storia"}, ...]}
- da/a: inizio e fine del tratto (di solito un voiceover o più voiceover uniti da un ponte senza voci);
- dopo: il primo parlato non nostro dopo il tratto (intervista, Manuel in camera): la coda si chiude prima;
- "ponti": [[t0, t1, guadagno]] dentro il tratto, dove la musica scende (es. sotto la voce di Manuel tra la folla);
- brano: storia | cammino | arrivo (da compose.py). Ogni brano è composto una volta per tutto il video e i tratti ne
  prendono il pezzo alla stessa posizione, così la musica resta una sola e non riparte da capo a ogni entrata.
Entrata 0.8 s prima del tratto (la musica arriva un attimo prima della voce), dissolvenze morbide.
"""
import json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose

SR = compose.SR


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
    D = cfg["durata"]; N = int(D * SR)
    beds = {}
    mix = np.zeros((N, 2))
    for tr in cfg["tratti"]:
        b = tr.get("brano", "storia")
        if b not in beds:
            beds[b] = {"storia": compose.storia, "cammino": compose.cammino, "arrivo": compose.arrivo,
                      "colline": compose.colline}[b](D + 8)
        bed = beds[b]
        t0 = max(0.0, tr["da"] - tr.get("pre", 0.8))
        tail = min(tr.get("coda", 1.6), max(0.25, tr.get("dopo", D) - tr["a"] - 0.1))
        t1 = min(D, tr["a"] + tail)
        i0, i1 = int(t0 * SR), int(t1 * SR)
        t = np.arange(i0, i1) / SR
        fin = tr.get("entrata", 0.8)
        g = np.clip((t - t0) / fin, 0, 1) ** 2
        g *= np.clip((t1 - t) / tail, 0, 1) ** 1.5 if tr.get("fine_dolce", True) else 1
        for p0, p1, pg in tr.get("ponti", []):
            ramp = 0.6
            w = np.clip(np.minimum(t - p0, p1 - t) / ramp + 0.5, 0, 1)   # 0 fuori dal ponte, 1 dentro
            g *= 1 - w * (1 - pg)
        off = tr.get("offset", 0.0)                                       # spostamento dentro il brano
        j0 = int((t0 + off) * SR)
        mix[i0:i1] += bed[j0:j0 + (i1 - i0)] * g[:, None]
    pk = np.abs(mix).max()
    mix *= 0.5 / (pk + 1e-9)                                              # picco -6 dBFS, il volume lo dà il mix
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", out], input=mix.astype("<f8").tobytes(), check=True)


if __name__ == "__main__":
    main()
