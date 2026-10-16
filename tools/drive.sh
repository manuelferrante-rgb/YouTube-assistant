#!/bin/bash
# Scarica un file da Google Drive condiviso "chiunque abbia il link".
# Gli ID dei file si prendono dal connettore Google Drive (elenco della cartella).
#   tools/drive.sh <file_id> <destinazione>
set -euo pipefail

ID="${1:?file_id}"
DEST="${2:?destinazione}"
mkdir -p "$(dirname "$DEST")"
curl -fL --retry 3 -o "$DEST" \
  "https://drive.usercontent.google.com/download?id=$ID&export=download&confirm=t"
# se Drive risponde con una pagina HTML il file non è condiviso col link
if head -c 200 "$DEST" | grep -qi "<html"; then
  rm -f "$DEST"
  echo "file $ID non scaricabile: controlla che la cartella sia condivisa con 'chiunque abbia il link'" >&2
  exit 1
fi
