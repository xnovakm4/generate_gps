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

2. Copy the `generate_gps.py` script to the gps-sdr-sim directory

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
--time HHMMSS       Simulation time in UTC-2 (default: current time)
--prefix STRING     Output file prefix (default: "gpssim")
```

### Example

```bash
python generate_gps.py --lat 49.1951 --lon 16.6068 --alt 300 --duration 600 --prefix gps-brno
```

This will generate GPS simulation data for Brno, Czech Republic at 300m altitude for 10 minutes (600 seconds), split into segments of 5 minutes each.

## Docker Usage

### Pull from Docker Hub

```bash
docker pull xnovakm4/generate_gps
```

The image is available for both `linux/amd64` and `linux/arm64` platforms.

### Running the Container

```bash
docker run --rm \
  -e EARTHDATA_USER=your_username \
  -e EARTHDATA_PASS=your_password \
  -v "$(pwd)/output:/output" \
  xnovakm4/generate_gps \
  [options]
```

### Environment Variables

- `EARTHDATA_USER`: Your NASA Earthdata username
- `EARTHDATA_PASS`: Your NASA Earthdata password

### Volume Mounts

- Mount a local directory to `/output` to save the generated files

### Example

```bash
docker run --rm \
  -e EARTHDATA_USER=your_username \
  -e EARTHDATA_PASS=your_password \
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
git clone https://github.com/your-username/generate_gps.git
cd generate_gps
docker build -t generate_gps .
```

## Notes

- The script automatically downloads the required ephemeris data from NASA's CDDIS archive
- Authentication with NASA Earthdata is required to download ephemeris files
- The simulation is split into segments to manage file sizes and memory usage
- The default time is set to UTC-2

## License

This project is licensed under the terms specified by the gps-sdr-sim project.
