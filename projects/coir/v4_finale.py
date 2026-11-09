#!/usr/bin/env python3
"""coir v4 (9/11, Insights + Manuel): negli ultimi 15 s nessun volto in primo piano (schermata finale di YouTube).

Parte dal lungo v3 consegnato (work/coir/out/VociVere_coir_long_4K.mp4, 6:45, banner inclusi). Cambia solo l'immagine:
- sotto la frase di chiusura (390.47-398.73): prima i volti chiesti da Manuel il 7/11 (le donne sedute, l'uomo nella
  laguna), poi la fabbrica senza volti (la macchina, le matasse) e la laguna; la scritta finale resta uguale;
- la sigla finale (398.73-404.73) con 6 pezzi senza volti al posto di quelli dell'inizio.
Audio, tempi e capitoli invariati. Una sola ricodifica con i parametri del lungo, audio copiato.
    python3 projects/coir/v4_finale.py   (clip in work/coir/raw dalla cartella Drive "Coir")
"""
import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = sys.argv[:1]
import build as B
from doc_render import Timeline, run

IN = f"{B.OUT}/VociVere_coir_long_4K.mp4"
OUT = f"{B.OUT}/VociVere_coir_long_4K_v4.mp4"
W, H = 3840, 2160
T_CLOSE, T_SIGLA, LEAD, DUR = 390.4667, 398.7333, 0.3, 8.2667

items = [(B.C("0063"), 4.2), (B.C("0544"), 1.5), (B.C("0017"), 0.5), (B.C("0087"), 0.5), (B.C("0107"), 2.0)]
close = B.closing_visual(W, H, items, DUR, LEAD, DUR - LEAD)
tl = Timeline(W, H, f"{B.OUT}/sigla_fine_work")
B.sigla_d(tl, B.OUT, clips=[(B.C("0021"), 1.0), (B.C("0089"), 2.0), (B.C("0087"), 0.5), (B.C("0017"), 1.0),
                            (B.C("0098"), 0.5), (B.C("0107"), 3.0)], tag="coir_fine")
sig = tl.shots[-1]["src"]
fc = (f"[0:v][1:v]overlay=eof_action=pass:enable='between(t,{T_CLOSE - 0.001:.4f},{T_SIGLA - 0.017:.4f})'[a];"
      f"[a][2:v]overlay=eof_action=pass:enable='gte(t,{T_SIGLA - 0.001:.4f})',format=yuv420p[v]")
run(["ffmpeg", "-v", "error", "-y", "-i", IN, "-itsoffset", f"{T_CLOSE:.4f}", "-i", close, "-itsoffset", f"{T_SIGLA:.4f}",
     "-i", sig, "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
     "-maxrate", "38M", "-bufsize", "76M", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "copy",
     "-movflags", "+faststart", OUT])
print(OUT)
