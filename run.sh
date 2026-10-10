#!/bin/bash
# Přihlašovací údaje k NASA Earthdata se čtou ze souboru .env (viz .env.example)
cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "[!] Chybí soubor .env. Zkopíruj .env.example do .env a doplň údaje." >&2
  exit 1
fi

docker run --rm \
  --env-file .env \
  -v "$PWD/output:/output" \
  generate_gps \
  --lat 49.1951 --lon 16.6068 \
  --duration 600 \
  --segment-duration 300 \
  --prefix /output/gps-brno
