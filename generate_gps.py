#!/usr/bin/env python3

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path


def find_gps_sim():
    # Hledat binárku vedle skriptu, případně v aktuální složce
    for candidate in (Path(__file__).resolve().parent / "gps-sdr-sim", Path.cwd() / "gps-sdr-sim"):
        if candidate.exists():
            return str(candidate)
    sys.exit("[!] gps-sdr-sim nebyl nalezen ve složce. Nejprve jej zkompiluj pomocí `make`.")


def estimate_output_size(duration, sample_rate=2600000):
    bytes_per_second = sample_rate * 2  # 8bit I + Q
    total_bytes = duration * bytes_per_second
    gb = total_bytes / (1024 ** 3)
    return gb


def day_of_year(dt: datetime.date) -> str:
    return dt.strftime('%j')


def wget(url):
    cookies = str(Path.home() / ".urs_cookies")
    return subprocess.run([
        "wget", "--quiet",
        "--load-cookies", cookies,
        "--save-cookies", cookies,
        "--keep-session-cookies", "--auth-no-challenge=on",
        url
    ]).returncode == 0


def download_ephemeris(ephemeris_url, eph_file):
    # Nejprve zkusit .gz, pokud selže, zkusit .Z
    for ext in ("gz", "Z"):
        url = f"{ephemeris_url}.{ext}"
        print(f"[+] Stahuji ephemeris: {url}")
        if wget(url):
            print(f"[+] Rozbaluji {eph_file}.{ext}")
            # gzip umí rozbalit .gz i .Z
            subprocess.run(["gzip", "-df", f"{eph_file}.{ext}"], check=True)
            return
        print(f"[!] Soubor .{ext} se nepodařilo stáhnout")
    sys.exit("[!] Chyba při stahování ephemeris (.gz ani .Z verze není dostupná)")


def run_simulation(gps_sim, eph_file, lat, lon, alt, duration, timestamp, output_file):
    cmd = [
        gps_sim,
        "-b", "8",
        "-e", eph_file,
        "-l", f"{lat},{lon},{alt}",
        "-d", str(duration),
        "-t", timestamp,
        "-o", output_file
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Generátor GPS simulace pomocí gps-sdr-sim pro HackRF")
    parser.add_argument("--lat", type=float, default=50.0755, help="Zeměpisná šířka (default: Praha)")
    parser.add_argument("--lon", type=float, default=14.4378, help="Zeměpisná délka (default: Praha)")
    parser.add_argument("--alt", type=int, default=250, help="Nadmořská výška v metrech")
    parser.add_argument("--duration", type=int, default=1800, help="Celková délka simulace v sekundách (např. 1800 = 30 minut)")
    parser.add_argument("--segment-duration", type=int, default=300, help="Délka jednoho segmentu (např. 300 = 5 minut)")
    parser.add_argument("--date", type=str, help="Datum simulace ve formátu YYYYMMDD (default: dnes)")
    parser.add_argument("--time", type=str, help="Čas simulace ve formátu HHMMSS (default: aktuální UTC čas - 2 hodiny)")
    parser.add_argument("--prefix", type=str, default=os.environ.get("GPS_PREFIX", "gpssim"),
                        help="Prefix výstupních souborů (default: $GPS_PREFIX nebo gpssim)")
    args = parser.parse_args()

    gps_sim = find_gps_sim()

    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)
    date_str = args.date if args.date else now.strftime('%Y%m%d')
    time_str = args.time if args.time else now.strftime('%H%M%S')
    start_time = datetime.datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")

    year = date_str[:4]
    doy = day_of_year(start_time.date())
    yy = year[2:]
    eph_file = f"brdc{doy}0.{yy}n"
    eph_url = f"https://cddis.nasa.gov/archive/gnss/data/daily/{year}/{doy}/{yy}n/{eph_file}"

    total_segments = (args.duration + args.segment_duration - 1) // args.segment_duration
    est_size_gb = estimate_output_size(args.segment_duration)

    print(f"[+] Parametry simulace:")
    print(f"    Souřadnice: {args.lat}, {args.lon}, {args.alt}")
    print(f"    Celková délka: {args.duration} sekund")
    print(f"    Segmenty: {total_segments} × {args.segment_duration} sekund")
    print(f"    Odhad velikosti jednoho segmentu: ~{est_size_gb:.2f} GB")
    print(f"    Výstupní soubory: {args.prefix}_NN.bin")

    download_ephemeris(eph_url, eph_file)


    for i in range(total_segments):
        remaining = args.duration - i * args.segment_duration
        current_segment_duration = min(args.segment_duration, remaining)
        segment_start = start_time + datetime.timedelta(seconds=i * args.segment_duration)
        timestamp = segment_start.strftime("%Y/%m/%d,%H:%M:%S")
        output_file = f"{args.prefix}_{i+1:02}.bin"

        print(f"[+] Generuji segment {i+1}/{total_segments} ({timestamp}) → {output_file}, délka {current_segment_duration} s")
        run_simulation(gps_sim, eph_file, args.lat, args.lon, args.alt, current_segment_duration, timestamp, output_file)

    print("[+] Všechny segmenty byly úspěšně vygenerovány.")


if __name__ == "__main__":
    main()
