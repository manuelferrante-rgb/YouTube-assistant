#!/bin/bash
# Prepara l'ambiente cloud: dipendenze Python, modello di trascrizione, font.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
M="$ROOT/models"
mkdir -p "$M"

# rclone per caricare i video finiti su Drive (da GitHub)
if ! command -v rclone >/dev/null 2>&1; then
  V=v1.68.2
  T=$(mktemp -d)
  curl -fsSL --retry 3 -o "$T/rc.zip" "https://github.com/rclone/rclone/releases/download/$V/rclone-$V-linux-amd64.zip"
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$T/rc.zip" "$T"
  install -m 755 "$T/rclone-$V-linux-amd64/rclone" /usr/local/bin/rclone
  rm -rf "$T"
fi

pip install -q --break-system-packages -r "$ROOT/requirements.txt" 2>&1 | grep -v "WARNING: Running pip" || true

dl() {  # dl URL DEST
  if [ ! -s "$2" ]; then curl -fsSL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"; fi
}
dl https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf "$M/Anton-Regular.ttf"
# font dei sottotitoli e delle etichette della mappa
dl https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Medium.ttf "$M/Poppins-Medium.ttf"
# dati cartografici reali per la mappa animata (Natural Earth)
mkdir -p "$M/geo"
dl https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson "$M/geo/admin0_50m.geojson"
dl https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_1_states_provinces.geojson "$M/geo/admin1_10m.geojson"
# trascrizione multilingua con tempi parola (parakeet-tdt-0.6b-v3)
P="$M/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
if [ ! -s "$P/tokens.txt" ]; then
  curl -fsSL --retry 3 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2 | tar xj -C "$M"
fi
