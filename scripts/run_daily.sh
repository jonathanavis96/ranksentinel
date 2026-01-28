#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

# Activate venv if it exists
if [ -d .venv ]; then
  source .venv/bin/activate
fi

python3 src/ranksentinel/runner/__main__daily.py
