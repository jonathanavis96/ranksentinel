#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

# Set log directory (default: ./logs)
export RANKSENTINEL_LOG_DIR="${RANKSENTINEL_LOG_DIR:-$(pwd)/logs}"

# Ensure log directory exists
mkdir -p "$RANKSENTINEL_LOG_DIR"

# Activate venv if it exists
if [ -d .venv ]; then
  source .venv/bin/activate
fi

python3 src/ranksentinel/runner/__main__weekly.py >> "$RANKSENTINEL_LOG_DIR/weekly_$(date +%Y%m%d).log" 2>&1

# Run weekly analytics digest (optional - requires GA4_PROPERTY_ID)
if [ -n "${GA4_PROPERTY_ID:-}" ]; then
  python3 scripts/weekly_analytics_digest.py >> "$RANKSENTINEL_LOG_DIR/analytics_digest_$(date +%Y%m%d).log" 2>&1
fi
