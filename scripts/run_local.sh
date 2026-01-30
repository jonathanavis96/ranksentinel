#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

./.venv/bin/uvicorn ranksentinel.api:app --reload --host 127.0.0.1 --port 8000
