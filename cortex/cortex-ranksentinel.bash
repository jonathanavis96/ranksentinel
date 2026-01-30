#!/usr/bin/env bash
# cortex/cortex-ranksentinel.bash - Interactive chat with Cortex for RankSentinel

set -euo pipefail

# Resolve script directory (follow symlink if needed)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Colors
readonly CYAN='\033[0;36m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🧠 Cortex Interactive Chat${NC}"
echo -e "${CYAN}   RankSentinel${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

usage() {
  echo "Usage: bash cortex/cortex-ranksentinel.bash [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --help, -h           Show this help"
  echo "  --model MODEL        Override model (gpt52, codex, opus, sonnet, auto)"
  echo ""
  echo "Examples:"
  echo "  bash cortex/cortex-ranksentinel.bash"
  echo "  bash cortex/cortex-ranksentinel.bash --model opus"
  echo ""
  echo "For automated planning: bash cortex/one-shot.sh"
  echo "To run Ralph (execution): bash loop.sh"
}

MODEL_ARG="gpt52"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h | --help)
      usage
      exit 0
      ;;
    --model)
      MODEL_ARG="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown: $1" >&2
      usage
      exit 2
      ;;
  esac
done

RESOLVED_MODEL=""
case "$MODEL_ARG" in
  opus) RESOLVED_MODEL="anthropic.claude-opus-4-5-20251101-v1:0" ;;
  gpt52 | gpt-5.2 | gpt5.2) RESOLVED_MODEL="gpt-5.2" ;;
  codex | gpt-5.2-codex) RESOLVED_MODEL="gpt-5.2-codex" ;;
  sonnet) RESOLVED_MODEL="anthropic.claude-sonnet-4-5-20250929-v1:0" ;;
  auto) RESOLVED_MODEL="" ;;
  *) RESOLVED_MODEL="$MODEL_ARG" ;;
esac

echo ""
echo -e "${YELLOW}Generating context snapshot...${NC}"
echo ""

SNAPSHOT_OUTPUT=$(bash "${SCRIPT_DIR}/snapshot.sh")

NEURONS_CONTENT=""
if [[ -f "${PROJECT_ROOT}/NEURONS.md" ]]; then
  NEURONS_CONTENT=$(cat "${PROJECT_ROOT}/NEURONS.md")
elif [[ -f "${PROJECT_ROOT}/cortex/NEURONS.md" ]]; then
  NEURONS_CONTENT=$(cat "${PROJECT_ROOT}/cortex/NEURONS.md")
elif [[ -f "${PROJECT_ROOT}/workers/ralph/NEURONS.md" ]]; then
  NEURONS_CONTENT=$(cat "${PROJECT_ROOT}/workers/ralph/NEURONS.md")
else
  NEURONS_CONTENT="# NEURONS.md not found\n\nCreate it (or generate it) to give Cortex a repo map."
fi

CORTEX_SYSTEM_PROMPT=$(
  cat <<EOF
$(cat "${SCRIPT_DIR}/AGENTS.md")

---

${NEURONS_CONTENT}

---

$(cat "${SCRIPT_DIR}/CORTEX_SYSTEM_PROMPT.md")

---

$(cat "${SCRIPT_DIR}/THOUGHTS.md")

---

# Current Repository State

${SNAPSHOT_OUTPUT}

---

# Chat Mode Instructions

You are now in **chat mode**. The user wants to have a direct conversation with you.

**Do NOT:**
- Automatically start a planning session
- Update files unless explicitly asked
- Execute the full planning workflow

**DO:**
- Answer questions about the RankSentinel project
- Provide guidance and recommendations when asked
- Help the user understand current state and next steps
- Be conversational and helpful
- Wait for user input and respond naturally

**To run Ralph (execution):** User runs \`bash loop.sh\` from project root
EOF
)

CONFIG_FILE="/tmp/cortex_config_$$_$(date +%s).yml"

cat >"$CONFIG_FILE" <<EOF
version: 1
agent:
  additionalSystemPrompt: |
$(while IFS= read -r line; do
  echo "    $line"
done <<<"$CORTEX_SYSTEM_PROMPT")
  streaming: true
  temperature: 0.3
EOF

if [[ -n "$RESOLVED_MODEL" ]]; then
  echo "  modelId: ${RESOLVED_MODEL}" >>"$CONFIG_FILE"
else
  echo "  modelId: auto" >>"$CONFIG_FILE"
fi

# RankSentinel note: its pyproject.toml in this temp scaffold may contain literal '\\n' sequences
# which are invalid TOML. Logfire (used by rovodev runtime) may try to parse it and crash.
# This disables logfire config loading.
LOGFIRE_DISABLE=1 acli rovodev run --config-file "$CONFIG_FILE" --yolo
EXIT_CODE=$?

rm -f "$CONFIG_FILE"
exit $EXIT_CODE
