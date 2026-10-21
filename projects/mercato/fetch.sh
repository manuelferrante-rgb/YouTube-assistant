#!/bin/bash
# Riscarica da Drive girato e musica del progetto mercato (per ricostruire i video in una nuova sessione).
cd "$(dirname "$0")/../.."
mkdir -p work/raw work/musica work/vo work/out
cp projects/mercato/vo/*.m4a work/vo/
cp projects/mercato/data/seg_speech.json work/out/
while read id n; do
  case "$n" in
    MUSICA:*) f="work/musica/${n#MUSICA:}" ;;
    DJI_*) f="work/raw/$n.MP4" ;;
    *) f="work/raw/dji_$n.mp4" ;;
  esac
  [ -s "$f" ] || tools/drive.sh "$id" "$f" &
done < projects/mercato/data/drive_ids.txt
wait
python3 tools/map_anim.py work/map_marari_4k.mp4 --lat 9.62646 --lon 76.29600 --name Marari
python3 tools/map_anim.py work/map_marari_9x16.mp4 --lat 9.62646 --lon 76.29600 --name Marari --w 1080 --h 1920 --zoomscale 0.4
