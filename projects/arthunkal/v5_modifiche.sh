#!/bin/bash
# Arthunkal v5 (4/11, Manuel dai dati del mercato): parte dal lungo v4 approvato su Drive e cambia solo due tratti.
#  1. "Il giorno prima" (34.53-69.30 del v4, Manuel che parla sulla costa e le ghirlande) -> 6.5 s di costa vuota
#     (140104 fermo + panoramica 140234 che continua senza stacco nel tratto del v4 da 69.30, "Nessuno avrebbe detto...").
#     Etichetta "Marari, il giorno prima". Sotto le onde vere di Marari della chat Audio (letto_onde.flac).
#  2. Finale: sotto "Il viaggio di Voci Vere... continua" (voce invariata) niente Manuel in camera: strada con i
#     pellegrini di spalle (083552, 085208), poi il logo sul fermo sfocato della strada. Ultimi 15 s senza volti in
#     primo piano, per la schermata finale di Studio.
# I tagli cadono su fotogrammi chiave del v4 (34.533, 69.300, 400.567): il resto è copiato senza ricodifica.
#   bash projects/arthunkal/v5_modifiche.sh   (serve work/arthunkal/consegnato/VociVere_arthunkal_long_4K.mp4 e raw/)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
W="$ROOT/work/arthunkal"; V="$W/v5"; R="$W/raw"; IN="$W/consegnato/VociVere_arthunkal_long_4K.mp4"
mkdir -p "$V"; cd "$V"
GR="eq=contrast=1.03:saturation=1.05"
SC="scale=3840:2160:flags=lanczos:force_original_aspect_ratio=increase,crop=3840:2160"
X264=(-c:v libx264 -preset medium -crf 20 -maxrate 38M -bufsize 76M -profile:v high -level 5.1 -pix_fmt yuv420p
      -g 250 -keyint_min 25 -x264-params open_gop=0 -an)
M104=$(ls "$R"/dji_mimo_20261023_140104_*); M234=$(ls "$R"/dji_mimo_20261023_140234_*)
C3552=$(ls "$R"/DJI_20261024083552_*); C5208=$(ls "$R"/DJI_20261024085208_*)

# etichetta in corsivo (stesso stile "Lab" del lungo, scala 4K)
cat > lab.ass <<'EOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lab,Playfair Display,92,&H00F2F2F2,&H00FFFFFF,&H00000000,&H80000000,0,-1,0,0,100,100,0.5,0,1,2.4,4.4,1,140,140,128,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.30,0:00:02.90,Lab,,0,0,0,,{\fad(350,350)}Marari, il giorno prima
EOF

# 1. costa vuota: 87 + 117 fotogrammi, dissolvenza di 9 (0.3 s) = 195 fotogrammi (6.5 s)
ffmpeg -v error -y -ss 0.3 -i "$M104" -ss 1.6 -i "$M234" -filter_complex \
 "[0:v]$SC,$GR,fps=30,trim=end_frame=87,setpts=PTS-STARTPTS[a];[1:v]$SC,$GR,fps=30,trim=end_frame=117,setpts=PTS-STARTPTS[b];
  [a][b]xfade=transition=fade:duration=0.3:offset=2.6,subtitles=lab.ass:fontsdir=$ROOT/models,format=yuv420p,trim=end_frame=195[v]" \
 -map "[v]" "${X264[@]}" segA.mp4

# 2. finale: 60 + 109 fotogrammi, dissolvenza di 9 = 160 (fino a 405.900 del v4), poi logo 105 (3.5 s) = 265
ffmpeg -v error -y -i "$C3552" -ss 7.8 -i "$C5208" -filter_complex \
 "[0:v]$SC,$GR,fps=30,trim=end_frame=60,setpts=PTS-STARTPTS[a];[1:v]$SC,$GR,fps=30,trim=end_frame=109,setpts=PTS-STARTPTS[b];
  [a][b]xfade=transition=fade:duration=0.3:offset=1.7,format=yuv420p[v]" -map "[v]" -c:v ffv1 -an brollB.mkv
ffmpeg -v error -y -sseof -0.04 -i brollB.mkv -frames:v 1 lastB.png
ffmpeg -v error -y -loop 1 -t 3.5 -i lastB.png -loop 1 -t 3.5 -i "$ROOT/assets/brand/logo_vocivere_trasparente_chiaro.png" \
 -filter_complex "[0:v]fps=30,trim=duration=3.5,setpts=PTS-STARTPTS,split[a][b];[b]gblur=sigma=56,eq=brightness=-0.24:saturation=0.65[bl];
  [a][bl]xfade=transition=fade:duration=0.6:offset=0.05[v];[1:v]scale=1612:-1,format=rgba,fade=t=in:st=0.35:d=0.6:alpha=1[lg];
  [v][lg]overlay=(W-w)/2:(H-h)/2:shortest=1,fade=t=out:st=3.1:d=0.4,format=yuv420p,trim=end_frame=105[o]" \
 -map "[o]" -c:v ffv1 logoB.mkv
ffmpeg -v error -y -i brollB.mkv -i logoB.mkv -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" "${X264[@]}" segB.mp4

# 3. tratti del v4 copiati (fotogrammi 0-1035 e 2079-12016)
ffmpeg -v error -y -i "$IN" -map 0:v -c copy -frames:v 1036 seg1.mp4
ffmpeg -v error -y -ss 69.3 -i "$IN" -map 0:v -c copy -frames:v 9938 seg3.mp4
printf "file '%s'\n" seg1.mp4 segA.mp4 seg3.mp4 segB.mp4 > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy video.mp4

# 4. audio: v4 fino a 34.533 (via in 0.1 s, prima che Manuel parli), onde di Marari, v4 da 69.300 (a 41.033)
ffmpeg -v error -y -i "$IN" -i "$ROOT/projects/arthunkal/audio/letto_onde.flac" -filter_complex \
 "[0:a]atrim=end_sample=1657600,afade=t=out:st=34.433:d=0.1[a1];
  [1:a]aresample=48000,atrim=start=3.0:duration=7.1,asetpts=PTS-STARTPTS,volume=0.75,afade=t=in:d=0.3,afade=t=out:st=6.3:d=0.8,adelay=1643200S|1643200S[w];
  [0:a]atrim=start_sample=3326400,asetpts=PTS-STARTPTS,adelay=1969600S|1969600S[a3];
  [a1][w][a3]amix=inputs=3:normalize=0:duration=longest,atrim=end_sample=18294400[o]" \
 -map "[o]" -c:a pcm_s24le audio.wav
ffmpeg -v error -y -i video.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -af "volume=2.2dB,alimiter=limit=0.8:level=disabled:attack=1:release=80" -c:a aac -b:a 320k -movflags +faststart \
 VociVere_arthunkal_long_4K.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact VociVere_arthunkal_long_4K.mp4
