#!/usr/bin/env python3
"""Porta un video a -14 LUFS: guadagno fisso + limitatore (-1.5 dBTP), video copiato. python3 tools/norm14.py file..."""
import json, os, subprocess, sys


def meas(x):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", x, "-af", "loudnorm=I=-14:TP=-1:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(json.loads(e.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def norm14(f):
    g, tmp = -14 - meas(f), f.replace(".mp4", "_n.mp4")
    for _ in range(3):
        if abs(g) < 0.05:
            break
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-c:v", "copy", "-af",
                        f"volume={g:.2f}dB,alimiter=limit=0.84:level=disabled:attack=1:release=60", "-c:a", "aac",
                        "-b:a", "256k", "-movflags", "+faststart", tmp], check=True)
        i = meas(tmp)
        if abs(i + 14) <= 0.2:
            break
        g += -14 - i
    if os.path.exists(tmp):
        os.replace(tmp, f)
    return f


if __name__ == "__main__":
    for f in sys.argv[1:]:
        norm14(f); print(f, f"{meas(f):.1f} LUFS")
