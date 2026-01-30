#!/usr/bin/env bash
# cortex/cortex.bash - Compatibility shim (prefer cortex/cortex-ranksentinel.bash)
#
# Supported entrypoint:
#   bash cortex/cortex-ranksentinel.bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/cortex-ranksentinel.bash" "$@"
