#!/bin/bash

# Vygeneruj .netrc, pokud jsou dostupné přihlašovací údaje
if [[ -n "$EARTHDATA_USER" && -n "$EARTHDATA_PASS" ]]; then
  echo "machine urs.earthdata.nasa.gov" > /root/.netrc
  echo "login $EARTHDATA_USER" >> /root/.netrc
  echo "password $EARTHDATA_PASS" >> /root/.netrc
  chmod 600 /root/.netrc
fi

# Spusť Python skript
exec python /app/generate_gps.py "$@"
