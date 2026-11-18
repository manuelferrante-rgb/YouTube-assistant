#!/usr/bin/env python3
"""Frase della missione per la sigla dei lunghi (Manuel 18/11, testo di Copy), presa unica "Via Palmanova 3.m4a"
(originale su Drive nella cartella di arthunkal, sottocartella sigla). Pulita (passa-alto, riduzione rumore leggera,
RNNoise all'80%), pause accorciate, 1.05x come i voiceover (Manuel 17/11), -16 LUFS.
    python3 projects/sigla_missione/voce.py <presa.m4a>   -> assets/voce/sigla_missione.m4a (+ tempi in .json)
"""
import json, os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from voice_clean import RNN, clean_rnn

SRC = sys.argv[1]
OUT = f"{ROOT}/assets/voce/sigla_missione.m4a"
SPEED = 1.05
# tratti di voce misurati sull'energia a 10 ms; pause tra i tratti
SEGS = [(1.20, 2.36), (2.62, 8.19), (8.76, 10.99), (11.18, 11.81), (12.08, 12.78)]
GAPS = [0.15, 0.25, 0.20, 0.12]
Q, V = 3, 4                      # indice del tratto "Questo è" e del tratto "Voci Vere"

if not os.path.exists(RNN):
    clean_rnn(SRC, f"{ROOT}/work/rnnoise/prova.wav")  # scarica il modello
fc, t, marks = "", 0.0, {}
for i, (a, b) in enumerate(SEGS):
    g = GAPS[i] if i < len(GAPS) else 0.0
    if i == Q: marks["questo"] = t / SPEED
    if i == V: marks["voci"] = t / SPEED
    fc += (f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.03:.3f}:d=0.03,"
           f"apad=pad_dur={g}[p{i}];")
    t += b - a + g
fc += "".join(f"[p{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=0:a=1,atrim=end={t:.3f},"
fc += (f"aformat=channel_layouts=mono,highpass=f=80,afftdn=nf=-32:nr=8,atrim=start_sample=1200,asetpts=PTS-STARTPTS,"
       f"arnndn=m={RNN}:mix=0.8,atrim=start_sample=480,asetpts=PTS-STARTPTS,atempo={SPEED},"
       "loudnorm=I=-16:TP=-2:LRA=7,aresample=48000[o]")
# il ritardo dei due filtri (1680 campioni) si toglie: si allunga l'ingresso con 0.05 s di silenzio in coda
fc = fc.replace(f"atrim=end={t:.3f},", f"apad=pad_dur=0.06,atrim=end={t + 0.05:.3f},")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[o]", "-ac", "1",
                "-c:a", "aac", "-b:a", "192k", OUT], check=True)
marks["fine"] = t / SPEED
json.dump(marks, open(OUT.replace(".m4a", ".json"), "w"), indent=1)
print(OUT, marks)
