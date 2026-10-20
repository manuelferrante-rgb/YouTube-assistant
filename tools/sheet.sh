#!/bin/bash
# Provino di una clip: 4-6 fotogrammi affiancati (ricerca per tempo, veloce anche su 4K HEVC).
#   tools/sheet.sh <video> <cartella_out>
f=$1; out=${2:-sheets}; mkdir -p "$out"
n=$(basename "$f"); n=${n%.*}
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
k=$(python3 -c "print(6 if $d>12 else 4)")
for i in $(seq 0 $((k-1))); do
  t=$(python3 -c "print(round($d*($i+0.5)/$k,2))")
  ffmpeg -v error -y -ss "$t" -i "$f" -map 0:v:0 -frames:v 1 -vf scale=360:-1 "$out/${n}_$i.png"
done
python3 - "$out" "$n" <<'EOF'
import cv2, numpy as np, glob, sys, os
out, n = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(f"{out}/{n}_*.png"))
im = np.hstack([cv2.imread(x) for x in fs])
cv2.putText(im, n, (6, 30), 0, 0.9, (0, 255, 255), 2)
cv2.imwrite(f"{out}/{n}.jpg", im)
for x in fs: os.remove(x)
EOF
