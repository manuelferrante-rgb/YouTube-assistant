#!/usr/bin/env python3
"""Mette i banner (tools/subscribe_banner.py) su un lungo già finito, senza rifare il 4K (Manuel 5/11).

    python3 tools/apply_banners.py in.mp4 out.mp4 --iscriviti 23.3 --like 220.0
Banner in basso al centro (4.5% dal fondo), larghi il 27% / 21% dello schermo; i click entrano nel mix (volume 0.45).
Si ricodificano solo i tratti tra i fotogrammi chiave attorno a ogni banner (stessi parametri x264 dei lunghi:
crf 20, maxrate 38M, high 5.1, GOP chiuso); il resto si copia. Audio: mix completo ricodificato in AAC 320k.
Scegliere i tempi dove non ci sono sottotitoli né scritte in basso al centro.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "38M", "-bufsize", "76M", "-profile:v", "high",
        "-level", "5.1", "-pix_fmt", "yuv420p", "-g", "250", "-keyint_min", "25", "-x264-params", "open_gop=0", "-an"]
DUR = {"iscriviti": 4.9, "like": 3.9}
VOL = 0.45


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)[:1500]); print(r.stderr[-2000:]); sys.exit(1)
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--iscriviti", type=float); ap.add_argument("--like", type=float)
    a = ap.parse_args()
    info = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,nb_frames",
                           "-of", "json", a.inp]))["streams"][0]
    W, N = info["width"], int(info["nb_frames"])
    bdir = f"{ROOT}/work/banner"
    keys = [int(round(float(l.split(",")[0]) * 30)) for l in run(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "packet=pts_time,flags", "-of", "csv=p=0", a.inp]
    ).split() if ",K" in l]
    jobs = sorted([(t, k) for k, t in (("iscriviti", a.iscriviti), ("like", a.like)) if t is not None])
    for t, k in jobs:
        mov = f"{bdir}/banner_{k}_{W}.mov"
        if not os.path.exists(mov):
            run(["python3", f"{ROOT}/tools/subscribe_banner.py", bdir, k, "--w", str(W)])
    work = os.path.splitext(a.out)[0] + "_banner_work"
    os.makedirs(work, exist_ok=True)
    segs, cur = [], 0
    for i, (t, k) in enumerate(jobs):
        f0, f1 = int(round(t * 30)), int(round((t + DUR[k]) * 30))
        k0 = max(x for x in keys if x <= f0)
        k1 = min([x for x in keys if x >= f1 + 1] + [N])
        if k0 > cur:
            p = f"{work}/c{i}.mp4"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cur / 30:.6f}", "-i", a.inp, "-map", "0:v", "-c", "copy",
                 "-frames:v", str(k0 - cur), p])
            segs.append(p)
        p = f"{work}/b{i}.mp4"
        off = (f0 - k0) / 30
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{k0 / 30:.6f}", "-i", a.inp, "-i", f"{bdir}/banner_{k}_{W}.mov",
             "-filter_complex", f"[1:v]setpts=PTS-STARTPTS+{off:.4f}/TB[o];[0:v][o]overlay=(W-w)/2:H-h-H*0.045:eof_action=pass,"
             f"format=yuv420p[v]", "-map", "[v]", "-frames:v", str(k1 - k0)] + X264 + [p])
        segs.append(p)
        cur = k1
    if cur < N:
        p = f"{work}/c_end.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cur / 30:.6f}", "-i", a.inp, "-map", "0:v", "-c", "copy", p])
        segs.append(p)
    with open(f"{work}/list.txt", "w") as f:
        f.writelines(f"file '{os.path.abspath(s)}'\n" for s in segs)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/list.txt", "-c", "copy", f"{work}/video.mp4"])
    # audio: il mix del lungo più i click
    ins, fc, labels = ["-i", a.inp], "", ["[0:a]"]
    for i, (t, k) in enumerate(jobs):
        ins += ["-i", f"{bdir}/banner_{k}_click.wav"]
        d = int(round(t * 48000))
        fc += f"[{i + 1}:a]volume={VOL},adelay={d}S|{d}S[c{i}];"
        labels.append(f"[c{i}]")
    fc += "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first[o]"
    run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[o]", "-c:a", "pcm_s24le", f"{work}/audio.wav"])
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/video.mp4", "-i", f"{work}/audio.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", a.out])
    n2 = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=nb_frames", "-of", "json",
                         a.out]))["streams"][0]["nb_frames"]
    print(a.out, "fotogrammi", n2, "su", N)


if __name__ == "__main__":
    main()
