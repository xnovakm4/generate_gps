# GPS Signal Simulator

This tool generates GPS signal simulation data using [gps-sdr-sim](https://github.com/osqzss/gps-sdr-sim). It can be used to create binary files for software-defined radio applications, particularly with HackRF devices.

## Features

- Generate GPS simulation data for any location on Earth, for usage on HackRF
- Split simulations into manageable segments
- Automatically download required ephemeris data from NASA's CDDIS archive
- Available as a Python script or Docker container
- Docker image supports multiple platforms (linux/amd64, linux/arm64)

## Requirements

### For Python Script

- Python 3.6+
- gps-sdr-sim (compiled)
- wget
- gzip
- NASA Earthdata account (for ephemeris downloads)

### For Docker

- Docker
- NASA Earthdata account (for ephemeris downloads)

## Python Script Usage

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/osqzss/gps-sdr-sim.git
   cd gps-sdr-sim
   make
   ```

2. Copy the compiled `gps-sdr-sim` binary next to `generate_gps.py` (or run the script from the directory that contains the binary)

3. Create a `.netrc` file in your home directory with your NASA Earthdata credentials:
   ```bash
   touch ~/.netrc
   ```
   Open the `.netrc` file in a text editor and add the following content (replace `your_username` and `your_password` with your actual Earthdata credentials):
   ```
   machine urs.earthdata.nasa.gov
   login your_username
   password your_password
   ```
   Save the file. For better security, set the file permissions so that only you can read it:
   ```bash
   chmod 600 ~/.netrc
   ```

### Running the Script

```bash
python generate_gps.py [options]
```

### Options

```
--lat FLOAT         Latitude (default: 50.0755, Prague)
--lon FLOAT         Longitude (default: 14.4378, Prague)
--alt INT           Altitude in meters (default: 250)
--duration INT      Total simulation duration in seconds (default: 1800 = 30 minutes)
--segment-duration INT  Duration of each segment in seconds (default: 300 = 5 minutes)
--date YYYYMMDD     Simulation date (default: today)
--time HHMMSS       Simulation start time in UTC (default: current UTC time minus 2 hours)
--prefix STRING     Output file prefix (default: $GPS_PREFIX or "gpssim"; in Docker "/output/gpssim")
```

### Example

```bash
python generate_gps.py --lat 49.1951 --lon 16.6068 --alt 300 --duration 600 --prefix gps-brno
```

This will generate GPS simulation data for Brno, Czech Republic at 300m altitude for 10 minutes (600 seconds), split into segments of 5 minutes each.

## Docker Usage

### Quick Start with `run.sh`

The easiest way to run the generator is the `run.sh` script:

1. Copy `.env.example` to `.env` and fill in your NASA Earthdata credentials:
   ```bash
   cp .env.example .env
   chmod 600 .env
   ```
   `.env` is ignored by git, so your credentials never end up in the repository.

2. Run the script:
   ```bash
   ./run.sh
   ```

On the first run, `run.sh` builds the Docker image `generate_gps` from the local `Dockerfile` (later runs reuse it). Without arguments it generates 10 minutes of data for Brno in two 5-minute segments. Any arguments are passed to `generate_gps.py`:

```bash
./run.sh --lat 50.0755 --lon 14.4378 --duration 900 --prefix /output/gps-prague
```

Output files are written to the local `output` directory. Use `--prefix /output/...` so that the files end up there.

`run.sh` honours these environment variables:

- `IMAGE`: Docker image to use (default: `generate_gps`), e.g. `IMAGE=xnovakm4/generate_gps ./run.sh`
- `REBUILD=1`: force rebuilding the image, e.g. after changing `generate_gps.py` or `Dockerfile`

### Pull from Docker Hub

```bash
docker pull xnovakm4/generate_gps
```

The image is available for both `linux/amd64` and `linux/arm64` platforms.

### Running the Container

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/output" \
  xnovakm4/generate_gps \
  [options]
```

### Environment Variables

- `EARTHDATA_USER`: Your NASA Earthdata username
- `EARTHDATA_PASS`: Your NASA Earthdata password

Keep them in a `.env` file (see `.env.example`) and pass it with `--env-file .env`. You can also pass them with `-e EARTHDATA_USER=... -e EARTHDATA_PASS=...`, but then the password ends up in your shell history.

### Volume Mounts

- Mount a local directory to `/output` to save the generated files. Inside the container the default prefix is `/output/gpssim`, so the files land there even without `--prefix`.

### Example

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/output" \
  xnovakm4/generate_gps \
  --lat 49.1951 --lon 16.6068 \
  --duration 600 \
  --segment-duration 300 \
  --prefix /output/gps-brno
```

This will generate GPS simulation data for Brno, Czech Republic for 10 minutes (600 seconds), split into two 5-minute segments, and save the output files to your local `output` directory with the prefix `gps-brno`.

## Output

The script generates binary files with the specified prefix followed by a segment number:

```
gpssim_01.bin
gpssim_02.bin
...
```

Each file contains I/Q samples that can be used with software-defined radio tools like HackRF.

## File Size Estimation

The script estimates the size of each segment file. With the default sample rate of 2.6 MHz, each second of simulation requires approximately 5.2 MB of storage.

## Building the Docker Image Locally

If you want to build the Docker image yourself:

```bash
git clone https://github.com/xnovakm4/generate_gps.git
cd generate_gps
docker build -t generate_gps .
```

`run.sh` does this automatically when the image does not exist yet.

## Notes

- The script automatically downloads the required ephemeris data from NASA's CDDIS archive
- Authentication with NASA Earthdata is required to download ephemeris files
- The simulation is split into segments to manage file sizes and memory usage
- The default start time is the current UTC time minus 2 hours
- The ephemeris file for the current day may not be available on CDDIS yet. If the download fails, use `--date` with an earlier day

## License

This project is licensed under the terms specified by the gps-sdr-sim project.
