#!/usr/bin/env python3
"""Aggiunge la chiusura stabile (tools/reel_close.py) a un reel già finito che non ce l'ha (Manuel 5/11).

    python3 tools/append_closing.py in.mp4 out.mp4 --src clip.mp4 --a 1.5 [--cx 0.5] [--variant A|B]
        [--music brano --music-at 12.3 --cut 1.5]
Coda di 2.8 s: la clip --src da --a per 0.8 s con "Ascolta altre voci, su", poi 2 s di logo sulla stessa clip sotto il
velo. Audio della coda: il brano --music da --music-at (dove si trova nel brano la fine del reel dopo il taglio), allo
stesso livello del reel (misurato sugli ultimi 2 s prima del taglio), con uscita di 1 s; senza --music, il brano
--music-quiet a -24 dB. --cut toglie gli ultimi secondi del reel (es. la dissolvenza della musica) prima della coda.
--overlay T: non aggiunge niente, mette solo la scritta da T alla fine (reel che chiudono già con il logo della sigla).
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, f"{ROOT}/tools")
from reel_kit import Reel
import reel_close as RC
from doc_render import run

GR = "eq=contrast=1.03:saturation=1.05"


def dur(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def rms_db(f, a, d):
    out = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{a}", "-t", f"{d}", "-i", f, "-vn", "-af",
                          "astats=measure_perchannel=none", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in out.splitlines() if "RMS level dB" in l][-1].split(":")[-1])


def cta_ass(work, W, H, t0, t1, variant):
    r = Reel(f"{work}/ass", W, H)
    r.title(t0, t1, RC.CTA, RC.VARIANTS[variant]["style"], 400)
    return r.ass(t1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--src"); ap.add_argument("--a", type=float, default=0.0); ap.add_argument("--cx", type=float, default=0.5)
    ap.add_argument("--grade", default=GR); ap.add_argument("--variant", default="A")
    ap.add_argument("--music"); ap.add_argument("--music-at", type=float, default=0.0); ap.add_argument("--cut", type=float, default=0.0)
    ap.add_argument("--music-quiet"); ap.add_argument("--quiet-at", type=float, default=8.0); ap.add_argument("--overlay", type=float)
    a = ap.parse_args()
    work = os.path.splitext(a.out)[0] + "_work"
    os.makedirs(work, exist_ok=True)
    W, H = 1080, 1920
    D = dur(a.inp)
    if a.overlay is not None:
        ass = cta_ass(work, W, H, a.overlay, D + 1, a.variant)
        run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-vf", f"ass={ass}:fontsdir={ROOT}/models", "-c:v", "libx264",
             "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", a.out])
        print(a.out); return
    T = D - a.cut
    TAIL = RC.LOGO_DELAY + RC.LOGO_DUR
    logo = RC.logo_card(work, W, H, RC.LOGO_DUR, a.src, a.a + RC.LOGO_DELAY, grade=a.grade, cx=a.cx, variant=a.variant)
    ass = cta_ass(work, W, H, 0.0, TAIL, a.variant)
    tail_v = f"{work}/tail.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a.a:.3f}", "-i", a.src, "-i", logo, "-filter_complex",
         f"[0:v:0]crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{a.cx}-ih*9/32))':0,scale={W}:{H}:flags=lanczos,fps=30,{a.grade},"
         f"trim=end_frame={int(round(RC.LOGO_DELAY * 30))},setpts=PTS-STARTPTS,format=yuv420p[p];"
         f"[1:v]fps=30,setpts=PTS-STARTPTS,format=yuv420p[l];[p][l]concat=n=2:v=1:a=0,ass={ass}:fontsdir={ROOT}/models[v]",
         "-map", "[v]", "-c:v", "libx264", "-crf", "14", "-preset", "medium", tail_v])
    # audio della coda
    tail_a = f"{work}/tail.wav"
    if a.music:
        ref = rms_db(a.inp, max(0, T - 2.0), 2.0)
        mus = rms_db(a.music, a.music_at - 2.0, 2.0)
        g = ref - mus
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a.music_at:.3f}", "-t", f"{TAIL:.3f}", "-i", a.music, "-af",
             f"aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,afade=t=out:st={TAIL - 1.0:.3f}:d=1.0",
             tail_a])
    else:
        src = a.music_quiet
        m = rms_db(src, a.quiet_at, TAIL)                          # da un punto del brano già pieno: niente buco
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a.quiet_at:.3f}", "-t", f"{TAIL:.3f}", "-i", src, "-af",
             f"aresample=48000,aformat=channel_layouts=stereo,volume={-24 - m:.2f}dB,afade=t=in:d=0.12,"
             f"afade=t=out:st={TAIL - 1.0:.3f}:d=1.0", tail_a])
    n_main = int(round(T * 30))
    run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-i", tail_v, "-i", tail_a, "-filter_complex",
         f"[0:v]trim=end_frame={n_main},setpts=PTS-STARTPTS,fps=30,format=yuv420p[v0];[1:v]setpts=PTS-STARTPTS[v1];"
         f"[v0][v1]concat=n=2:v=1:a=0[v];"
         f"[0:a]atrim=end={T:.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a0];"
         f"[2:a]asetpts=PTS-STARTPTS[a1];[a0][a1]concat=n=2:v=0:a=1[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.out])
    print(a.out, f"{dur(a.out):.2f}s")


if __name__ == "__main__":
    main()
