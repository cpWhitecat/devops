#!/usr/bin/env bash
set -euo pipefail

if [ -z "${TARGET+x}" ]; then
  echo "ERROR: TARGET environment variable is required (example: http://host:port/path)" >&2
  exit 2
fi

TARGET_RAW="$TARGET"
# sanitize target for directory name
SANITIZED=$(echo "$TARGET_RAW" | sed -E 's/[^A-Za-z0-9]/_/g')
OUTDIR="/scans/$SANITIZED"
mkdir -p "$OUTDIR"

LOGFILE="$OUTDIR/run.log"

echo "Starting sqlmap scan for: $TARGET_RAW" | tee "$LOGFILE"

# Default level/risk/threads can be overridden via env
LEVEL=${LEVEL:-2}
RISK=${RISK:-1}
THREADS=${THREADS:-5}
CRAWL=${CRAWL:-1}

# Run sqlmap and capture stdout/stderr
sqlmap -u "$TARGET_RAW" --batch --output-dir="/scans" --crawl="$CRAWL" --level="$LEVEL" --risk="$RISK" --threads="$THREADS" 2>&1 | tee -a "$LOGFILE"

# After run, generate simple HTML report
python3 /app/generate_report.py "$OUTDIR" || true

echo "Scan finished. Results in: $OUTDIR"
