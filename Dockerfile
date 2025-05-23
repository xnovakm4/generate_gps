FROM python:3.10-slim

# Instalace nástrojů
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    cmake \
    wget \
    gzip \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Klonování a kompilace gps-sdr-sim
RUN git clone https://github.com/osqzss/gps-sdr-sim.git /opt/gps-sdr-sim && \
    cd /opt/gps-sdr-sim && make && \
    mkdir /app && mv /opt/gps-sdr-sim/gps-sdr-sim /app/ && \
    rm -rf /opt/gps-sdr-sim

# Přidání skriptů
COPY generate_gps.py /app/generate_gps.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

# Spouštěcí skript
ENTRYPOINT ["/entrypoint.sh"]
