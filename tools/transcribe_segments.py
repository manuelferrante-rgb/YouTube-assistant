#!/usr/bin/env python3
"""Trascrizione a frasi con tempi affidabili: divide l'audio in tratti di voce (energia) e trascrive ognuno.

A differenza di analyze_clips.py (un'unica trascrizione con tempi rimappati linearmente, imprecisi sulle
clip lunghe con pause), qui ogni tratto ha inizio/fine reali e le parole hanno tempi assoluti.
    python3 tools/transcribe_segments.py out.json clip1 clip2 ...
"""
import json, os, subprocess, sys
import numpy as np, sherpa_onnx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyze_clips import words_from_tokens

M = os.path.join(HERE, "..", "models", "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
SR = 16000


def audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def regions(x, gap=0.5, min_len=0.3):
    hop = SR // 100
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
    db = np.convolve(db, np.ones(7) / 7, mode="same")
    thr = max(np.percentile(db, 15) + 10, np.percentile(db, 97) - 30)
    v = db > thr
    regs, s = [], None
    for i, on in enumerate(v):
        if on and s is None:
            s = i
        if not on and s is not None:
            regs.append([s / 100, i / 100]); s = None
    if s is not None:
        regs.append([s / 100, n / 100])
    out = []
    for r in regs:
        if out and r[0] - out[-1][1] < gap:
            out[-1][1] = r[1]
        else:
            out.append(r)
    # tratti troppo lunghi (rumore continuo) spezzati a 12 s per non perdere precisione
    res = []
    for a, b in out:
        while b - a > 14:
            res.append([a, a + 12]); a += 12
        if b - a >= min_len:
            res.append([a, b])
    return res


def main(out, clips):
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx", joiner=f"{M}/joiner.int8.onnx",
        tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=4)
    res = {}
    for c in clips:
        x = audio(c)
        segs = []
        for a, b in regions(x):
            pa, pb = max(0, a - 0.15), min(len(x) / SR, b + 0.15)
            st = rec.create_stream()
            st.accept_waveform(SR, x[int(pa * SR):int(pb * SR)])
            rec.decode_stream(st)
            ws = words_from_tokens(list(st.result.tokens), list(st.result.timestamps))
            if not ws:
                continue
            segs.append({"start": round(a, 2), "end": round(b, 2), "text": st.result.text.strip(),
                         "words": [[w, round(pa + t, 2)] for w, t in ws]})
        res[os.path.basename(c)] = segs
        print(f"== {os.path.basename(c)}")
        for s in segs:
            print(f"  {s['start']:7.2f}-{s['end']:7.2f}  {s['text']}")
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
