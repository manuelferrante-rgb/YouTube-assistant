#!/bin/bash
# te v8 (4/11, Manuel dai dati del mercato): la domanda della miniatura "E oggi, di chi sono queste colline?" resta a
# schermo ~4 s invece di 1.9 (Manuel: 3-5 s nel primo minuto, senza risposta). Parte dal lungo v7 approvato su Drive:
# l'inquadratura delle colline sotto la domanda (114701, prima della sigla) passa da 1.3 a 3.3 s, con il segno
# melodico di Audio (cue_domanda) lungo 3.3 s. Tutto il resto è copiato senza ricodifica (tagli sui fotogrammi chiave
# 15.333 e 16.633 del v7); dopo la sigla i tempi slittano di 2.0 s.
# Il finale non cambia: gli ultimi 14 s (dalle mucche al logo) sono già senza volti in primo piano.
#   bash projects/te/v8_modifiche.sh   (serve work/te/consegnato/VociVere_te_long_4K.mp4 e work/te/raw/*114701*)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
W="$ROOT/work/te"; V="$W/v8"; IN="$W/consegnato/VociVere_te_long_4K.mp4"
mkdir -p "$V"; cd "$V"
SRC=$(ls "$W"/raw/DJI_20261026114701_*)
X264=(-c:v libx264 -preset medium -crf 20 -maxrate 38M -bufsize 76M -profile:v high -level 5.1 -pix_fmt yuv420p
      -g 250 -keyint_min 25 -x264-params open_gop=0 -an)

# la domanda: stesso stile "Big" del lungo; a 0 s (= 0.3 s dopo l'inizio del titolo nel v7) opacità 50% e scala
# 96.95%, poi piena; esce in 0.6 s e a 3.3 s (attacco della sigla) è di nuovo al 50%, come nel v7 a 16.633
cat > q.ass <<'EOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,Playfair Display,300,&H00F4F4F4,&H00FFFFFF,&H00000000,&H90000000,-1,-1,0,0,100,100,1,0,1,3,8,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 2,0:00:00.00,0:00:03.60,Big,,0,0,0,,{\an5\pos(1920,1080)\fade(128,0,255,0,300,3000,3600)\fscx96.95\fscy96.95\t(0,3600,\fscx102\fscy102)}E oggi, di chi sono queste colline?
EOF

# 1. le colline 114701 da 1.0 s, 99 fotogrammi, zoom lento 1.00 -> 1.04 come Edit.b
ffmpeg -v error -y -ss 1.0 -i "$SRC" -filter_complex \
 "[0:v]scale=3840:2160:flags=lanczos:force_original_aspect_ratio=increase,crop=3840:2160,eq=contrast=1.03:saturation=1.05,fps=30,
  trim=end_frame=99,setpts=PTS-STARTPTS,scale=w='trunc(3840*(1+0.04*t/3.3)/2)*2':h='trunc(2160*(1+0.04*t/3.3)/2)*2':eval=frame:flags=bicubic,
  crop=3840:2160,ass=q.ass:fontsdir=$ROOT/models,format=yuv420p[v]" -map "[v]" "${X264[@]}" segQ.mp4

# 2. tratti del v7 copiati: fotogrammi 0-459 e da 499
ffmpeg -v error -y -i "$IN" -map 0:v -c copy -frames:v 460 seg1.mp4
ffmpeg -v error -y -ss 16.633333 -i "$IN" -map 0:v -c copy seg3.mp4
printf "file '%s'\n" seg1.mp4 segQ.mp4 seg3.mp4 > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy video.mp4

# 3. audio: v7 fino a 15.333, segno della domanda lungo 3.3 s (stesso livello del v7, misurato), v7 da 16.633 a 18.333
G=$(python3 - "$IN" "$ROOT/projects/te/audio/cue_domanda.flac" <<'PY'
import subprocess, sys, numpy as np
def rms(f, a, d):
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(d), "-i", f, "-ac", "1", "-ar",
                                      "48000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    return np.sqrt((x ** 2).mean())
print(f"{rms(sys.argv[1], 15.40, 0.9) / rms(sys.argv[2], 0.067, 0.9):.4f}")
PY
)
echo "guadagno cue: $G"
ffmpeg -v error -y -i "$IN" -i "$ROOT/projects/te/audio/cue_domanda.flac" -filter_complex \
 "[0:a]atrim=end_sample=736000,asetpts=PTS-STARTPTS[a1];
  [1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration=3.3,asetpts=PTS-STARTPTS,volume=$G,afade=t=out:st=2.9:d=0.4,adelay=736000S|736000S[c];
  [0:a]atrim=start_sample=798400,asetpts=PTS-STARTPTS,adelay=894400S|894400S[a3];
  [a1][c][a3]amix=inputs=3:normalize=0:duration=longest[o]" -map "[o]" -c:a pcm_s24le audio.wav
ffmpeg -v error -y -i video.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -movflags +faststart \
 VociVere_te_long_4K.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact VociVere_te_long_4K.mp4
