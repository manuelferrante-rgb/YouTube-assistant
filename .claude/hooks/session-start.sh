#!/bin/bash
# Prepara l'ambiente cloud: dipendenze Python, modello di trascrizione, font.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
M="$ROOT/models"
mkdir -p "$M"

pip install -q --break-system-packages -r "$ROOT/requirements.txt" 2>&1 | grep -v "WARNING: Running pip" || true

dl() {  # dl URL DEST
  if [ ! -s "$2" ]; then curl -fsSL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"; fi
}
dl https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf "$M/Anton-Regular.ttf"
# trascrizione multilingua con tempi parola (parakeet-tdt-0.6b-v3)
P="$M/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
if [ ! -s "$P/tokens.txt" ]; then
  curl -fsSL --retry 3 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2 | tar xj -C "$M"
fi
