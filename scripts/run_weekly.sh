#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

# Activate venv if it exists
if [ -d .venv ]; then
  source .venv/bin/activate
fi

python3 -m ranksentinel.runner.weekly_digest
