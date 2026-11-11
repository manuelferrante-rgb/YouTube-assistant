#!/usr/bin/env python3
"""coir v6 (11/11, Manuel + Insights): intro nuova. Le tre promesse delle miniature del test (uomo nella laguna,
"Made in India", "80 centesimi a tappeto") si vedono nei primi ~20 s.

Cambia solo VO0: al posto del vecchio (4.4 s, su 0063 donna in rosa + 0069 fabbrica) va il voiceover nuovo di Manuel
(Drive "Coir", file "Intro"): "Su quei tappeti c'è scritto Made in India. Non c'è scritto chi li ha fatti. Né che a loro
per ogni tappeto vanno ottanta centesimi. Quattro euro al giorno. Da oggi, ogni volta che ne vedi uno, saprai da dove
viene." Sotto, SOLO le persone delle miniature (Manuel 11/11), coerenti con il parlato:
  - "Made in India... chi li ha fatti": la signora della miniatura 2 (0063 7.8-10.6, maglia grigia, guarda in camera)
  - "Né che a loro... ottanta centesimi. Quattro euro al giorno": la signora della miniatura 3 (0063 13.78-17.9,
    camicetta a fiori davanti al mucchio di gusci, poi le mani nella fibra)
  - "Da oggi... saprai da dove viene": l'uomo della miniatura 1 nella laguna accanto alla barca (0052 2.0-5.03)
Brano coir_intro di Audio ora per intero (sfuma da solo a ~10 s, prima della sigla).

Niente nuovo render del 4K: dal v5 (Drive montati/coir) si copiano senza ricodifica 0-7.6 s (fino alla fine di 0038)
e dalla sigla (12.4333 s, fotogramma chiave) alla fine; si codifica solo il tratto nuovo. Tutto ciò che viene dopo
slitta di DELTA s (banner compresi). Audio: v5 + tratto nuovo, una sola codifica AAC.
    python3 projects/coir/v6_intro.py        (girato in work/coir/raw, v5 in work/coir/long_v5.mp4)
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from voice_clean import cleaned

WK = f"{ROOT}/work/coir/v6"
RAW = f"{ROOT}/work/coir/raw"
V5 = f"{ROOT}/work/coir/long_v5.mp4"
VO = f"{ROOT}/work/coir/intro/Intro.m4a"
MUSIC = f"{ROOT}/projects/coir/audio/coir_intro.flac"
OUT = f"{ROOT}/work/coir/out/VociVere_coir_long_4K.mp4"
SR, FPS, W, H = 48000, 30, 3840, 2160
DEF = "eq=contrast=1.03:saturation=1.05"          # stesso grade di build.py

T_A = 7.6                    # fine di 0038 nel v5 (fotogramma chiave): da qui il tratto nuovo
T_SIG_OLD = 12.4333333       # attacco della sigla nel v5 (fotogramma chiave)
VO_A, VO_B = 2.28, 12.02     # la frase nel file "Intro" (parlato 2.40-11.91)
T_VO = 7.63                  # dove entra il file della voce (parlato da ~7.75)
# (clip, inizio nella clip, fotogrammi)
SHOTS = [("0063", 7.80, 84),     # 7.6 -> 10.4   miniatura 2
         ("0063", 13.78, 123),   # 10.4 -> 14.5  miniatura 3 (da "Né che a loro")
         ("0052", 2.00, 91)]     # 14.5 -> 17.533 miniatura 1
N_NEW = sum(s[2] for s in SHOTS)
T_SIG_NEW = T_A + N_NEW / FPS
DELTA = T_SIG_NEW - T_SIG_OLD
MUS = 0.11                   # livello della musica sotto il VO in build.py
VOICE_LUFS = -18.0


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)[:500]); print(r.stderr[-2000:]); sys.exit(1)
    return r


def clip(n):
    return next(f"{RAW}/{f}" for f in sorted(os.listdir(RAW)) if f"_{n}_D" in f)


def lufs(path, ss=None, t=None):
    cmd = ["ffmpeg", "-hide_banner"] + (["-ss", str(ss), "-t", str(t)] if ss is not None else []) + \
          ["-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    e = run(cmd).stderr
    return float(json.loads(e.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def video():
    parts = []
    for i, (n, a, nf) in enumerate(SHOTS):
        d = nf / FPS
        z = f"(1.0+0.04*t/{d:.3f})"                 # zoom lento 1.0 -> 1.04 come i B-roll del lungo
        vf = (f"scale={W}:{H}:flags=lanczos,{DEF},fps={FPS},trim=end_frame={nf},setpts=PTS-STARTPTS,"
              f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame:flags=bicubic,crop={W}:{H},"
              f"format=yuv420p")
        p = f"{WK}/shot{i}.mkv"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d + 1:.3f}", "-i", clip(n), "-an", "-vf", vf,
             "-frames:v", str(nf), "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", p])
        parts.append(p)
    lst = f"{WK}/shots.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    mid = f"{WK}/mid.mp4"
    # stessi parametri del lungo (doc_render: crf 20, medium, high, maxrate 38M); ogni GOP chiuso, primo fotogramma IDR
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-crf", "20",
         "-preset", "medium", "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", "-maxrate", "38M",
         "-bufsize", "76M", "-r", str(FPS), "-video_track_timescale", "15360", mid])
    head, tail = f"{WK}/head.h264", f"{WK}/tail.h264"
    run(["ffmpeg", "-v", "error", "-y", "-i", V5, "-map", "0:v", "-c", "copy", "-frames:v", str(round(T_A * FPS)),
         "-bsf:v", "h264_mp4toannexb", "-f", "h264", head])
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{T_SIG_OLD + 0.005:.4f}", "-i", V5, "-map", "0:v", "-c", "copy",
         "-bsf:v", "h264_mp4toannexb", "-f", "h264", tail])
    run(["ffmpeg", "-v", "error", "-y", "-i", mid, "-c", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "h264",
         f"{WK}/mid.h264"])
    allv = f"{WK}/all.h264"            # flussi grezzi in fila (SPS/PPS in ogni IDR): tempi rigenerati a 30 fps
    with open(allv, "wb") as o:
        for p in (head, f"{WK}/mid.h264", tail):
            o.write(open(p, "rb").read())
    return allv


def audio(total):
    # 1. voce nuova: RNNoise come gli altri VO, la frase, -18 LUFS con guadagno fisso
    vt = f"{WK}/vo_tmp.wav"
    L = VO_B - VO_A
    run(["ffmpeg", "-v", "error", "-y", "-i", cleaned(VO, f"{ROOT}/work/coir/voce"), "-af",
         f"atrim={VO_A}:{VO_B},asetpts=PTS-STARTPTS,aresample={SR},afade=t=in:d=0.04,afade=t=out:st={L - 0.08:.3f}:d=0.08",
         "-ac", "1", "-ar", str(SR), vt])
    vo = f"{WK}/vo.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", vt, "-af", f"volume={VOICE_LUFS - lufs(vt):.2f}dB", "-ac", "1",
         "-ar", str(SR), vo])
    # 2. guadagno del master del v5: il vecchio VO0 (a -18 LUFS nel premix) come suona nel file consegnato
    G = 10 ** ((lufs(V5, 7.75, 4.3) - VOICE_LUFS) / 20)
    # 3. tratto nuovo: voce + coir_intro per intero dalla posizione 0.4 (il v5 ne ha già 0-0.4 sotto la fine di 0038)
    n_mid = int(round((T_SIG_NEW - T_A) * SR))
    mid = np.zeros((n_mid, 2))
    v, _ = sf.read(vo, dtype="float64")
    o = int(round((T_VO - T_A) * SR))
    mid[o:o + len(v)] += v[:n_mid - o, None]
    m, msr = sf.read(MUSIC, dtype="float64")
    assert msr == SR
    m = m[int(0.4 * SR):][:n_mid]
    mid[:len(m)] += MUS * m
    mid *= G
    # stesso limitatore del master di doc_render (la voce nuova ha picchi più alti: senza, +1.7 dBFS)
    pm, pl = f"{WK}/mid_pre.wav", f"{WK}/mid_lim.wav"
    sf.write(pm, mid.astype(np.float32), SR, subtype="FLOAT")
    run(["ffmpeg", "-v", "error", "-y", "-i", pm, "-af", "alimiter=limit=0.85:attack=2:release=60:level=false:latency=1",
         "-c:a", "pcm_f32le", pl])
    mid, _ = sf.read(pl, dtype="float64")
    mid = mid[:n_mid]
    # 4. v5 prima e dopo, raccordi di 20 ms
    fin = f"{WK}/v5.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", V5, "-map", "0:a:0", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_f32le", fin])
    a5, _ = sf.read(fin, dtype="float64")
    ia, ib = int(round(T_A * SR)), int(round(T_SIG_OLD * SR))
    x = int(0.02 * SR)
    r = np.linspace(0, 1, x)[:, None]
    head = a5[:ia + x].copy()
    head[ia:] = head[ia:] * (1 - r) + mid[:x] * r
    out = np.concatenate([head, mid[x:], a5[ib:]])
    pk = 20 * np.log10(np.abs(mid).max())
    print(f"guadagno master {20 * np.log10(G):.2f} dB, picco del tratto nuovo {pk:.1f} dBFS, "
          f"LUFS v5 VO0 {lufs(V5, 7.75, 4.3):.1f}")
    out = out[:int(round(total * SR))]
    p = f"{WK}/mix_v6.wav"
    sf.write(p, np.clip(out, -0.98, 0.98).astype(np.float32), SR, subtype="PCM_16")
    return p


def main():
    os.makedirs(WK, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    print(f"sigla da {T_SIG_OLD:.3f} a {T_SIG_NEW:.3f} s: tutto dopo slitta di {DELTA:+.3f} s")
    allv = f"{WK}/all.h264" if os.path.exists(f"{WK}/all.h264") and "--audio" in sys.argv else video()
    dur5 = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V5]).stdout)
    total = dur5 + DELTA
    mix = audio(total)
    run(["ffmpeg", "-v", "error", "-y", "-fflags", "+genpts", "-r", str(FPS), "-f", "h264", "-i", allv, "-i", mix, "-map", "0:v",
         "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart",
         "-t", f"{total:.3f}", OUT])
    print(OUT, f"durata attesa {total:.3f}")


if __name__ == "__main__":
    main()
