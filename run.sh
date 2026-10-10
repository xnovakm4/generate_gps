#!/bin/bash
# Spuštění generátoru v Dockeru.
# Přihlašovací údaje k NASA Earthdata se čtou ze souboru .env (viz .env.example).
# Bez argumentů vygeneruje 10 minut pro Brno, jinak se argumenty předají skriptu generate_gps.py.
set -e
cd "$(dirname "$0")"

IMAGE="${IMAGE:-generate_gps}"

if [[ ! -f .env ]]; then
  echo "[!] Chybí soubor .env. Zkopíruj .env.example do .env a doplň údaje." >&2
  exit 1
fi

# Sestavit image, pokud ještě neexistuje (REBUILD=1 vynutí nové sestavení)
if [[ -n "$REBUILD" ]] || ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "[+] Sestavuji Docker image $IMAGE"
  docker build -t "$IMAGE" .
fi

if [[ $# -eq 0 ]]; then
  set -- \
    --lat 49.1951 --lon 16.6068 \
    --duration 600 \
    --segment-duration 300 \
    --prefix /output/gps-brno
fi

mkdir -p output
docker run --rm \
  --env-file .env \
  -v "$PWD/output:/output" \
  "$IMAGE" \
  "$@"
