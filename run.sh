docker run --rm \
  -e EARTHDATA_USER=xnovakm4 \
  -e EARTHDATA_PASS="your_password" \
  -v "$PWD/output:/output" \
  gps-sim-generator \
  --lat 49.1951 --lon 16.6068 \
  --duration 600 \
  --segment-duration 300 \
  --prefix /output/gps-brno
