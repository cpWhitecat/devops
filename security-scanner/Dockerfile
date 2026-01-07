FROM python:3.11-slim

# Install basic tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates git build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy scanner scripts
COPY run_scan.sh /app/run_scan.sh
COPY generate_report.py /app/generate_report.py
RUN chmod +x /app/run_scan.sh

# Install sqlmap
RUN pip install --no-cache-dir sqlmap

VOLUME ["/scans"]

ENTRYPOINT ["/app/run_scan.sh"]
