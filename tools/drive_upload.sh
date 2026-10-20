#!/bin/bash
# Carica i video finiti nella cartella Drive, sottocartella "montati/<progetto>".
# Il token OAuth di rclone arriva dalla variabile d'ambiente GDRIVE_RCLONE_TOKEN.
#   tools/drive_upload.sh <progetto> <file...>
set -euo pipefail

: "${GDRIVE_RCLONE_TOKEN:?manca GDRIVE_RCLONE_TOKEN nelle impostazioni ambiente}"
PROJ="${1:?nome progetto}"; shift
[ $# -gt 0 ] || { echo "nessun file da caricare" >&2; exit 1; }

export RCLONE_CONFIG_GDRIVE_TYPE=drive
export RCLONE_CONFIG_GDRIVE_SCOPE=drive
export RCLONE_CONFIG_GDRIVE_TOKEN="$GDRIVE_RCLONE_TOKEN"
export RCLONE_CONFIG_GDRIVE_ROOT_FOLDER_ID="${GDRIVE_FOLDER_ID:-1X3qkOWu91EZUWqKoVu0pZ3Dd1ipXlGeB}"

for f in "$@"; do
  rclone copy -P "$f" "gdrive:montati/$PROJ"
done
rclone lsl "gdrive:montati/$PROJ"
