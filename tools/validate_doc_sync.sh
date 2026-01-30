#!/usr/bin/env bash
#
# validate_doc_sync.sh - Validate documentation stays in sync with config files
#
# Checks that documented configuration (e.g., in README files) matches actual
# config files to prevent CR-6.4-type issues (shfmt flags mismatch).
#
# Exit codes:
#   0 - All documentation in sync
#   1 - Documentation out of sync with configs
#   2 - Script error

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error_count=0

log_error() {
  echo -e "${RED}ERROR:${NC} $*" >&2
  ((error_count++)) || true
}

log_success() {
  echo -e "${GREEN}✓${NC} $*"
}

log_info() {
  echo -e "${YELLOW}INFO:${NC} $*"
}

# =============================================================================
# Check: shfmt flags in shell/README.md vs .pre-commit-config.yaml
# =============================================================================
check_shfmt_flags() {
  log_info "Checking shfmt flags documentation..."

  local readme="skills/domains/languages/shell/README.md"
  local precommit=".pre-commit-config.yaml"

  if [[ ! -f "$readme" ]]; then
    log_error "Shell README not found: $readme"
    return 1
  fi

  if [[ ! -f "$precommit" ]]; then
    log_error "Pre-commit config not found: $precommit"
    return 1
  fi

  # Extract shfmt args from .pre-commit-config.yaml
  # Expected line: args: ["-d", "-i", "2", "-ci"]
  local actual_flags
  actual_flags=$(grep -A 5 'id: shfmt' "$precommit" | grep 'args:' | sed 's/.*args: \[//' | sed 's/\].*//' | tr -d '"' | tr ',' ' ')

  if [[ -z "$actual_flags" ]]; then
    log_error "Could not extract shfmt args from $precommit"
    return 1
  fi

  # Check if README documents the actual flags
  # Look for line containing: args: ["-d", "-i", "2", "-ci"]
  if grep -q "\-d.*\-i.*2.*\-ci" "$readme"; then
    log_success "shfmt flags documented correctly in $readme"
  else
    log_error "shfmt flags in $readme don't match $precommit (expected: $actual_flags)"
    return 1
  fi

  # Check that README explains the difference between pre-commit and manual use
  if grep -q "Pre-commit uses.*check only" "$readme" && grep -q "Manual fixes use.*write changes" "$readme"; then
    log_success "shfmt usage distinction documented in $readme"
  else
    log_error "$readme should explain pre-commit vs manual shfmt usage"
    return 1
  fi
}

# =============================================================================
# Check: markdownlint config in markdown-patterns.md vs .markdownlint.yaml
# =============================================================================
check_markdownlint_config() {
  log_info "Checking markdownlint config documentation..."

  local markdown_patterns="skills/domains/code-quality/markdown-patterns.md"
  local markdownlint_yaml=".markdownlint.yaml"

  if [[ ! -f "$markdown_patterns" ]]; then
    log_info "Markdown patterns file not found (optional check): $markdown_patterns"
    return 0
  fi

  if [[ ! -f "$markdownlint_yaml" ]]; then
    log_error "Markdownlint config not found: $markdownlint_yaml"
    return 1
  fi

  # Check if markdown-patterns.md references the config file
  if grep -q "\.markdownlint\.yaml" "$markdown_patterns"; then
    log_success "markdownlint config referenced in $markdown_patterns"
  else
    log_info "Consider adding reference to $markdownlint_yaml in $markdown_patterns"
  fi
}

# =============================================================================
# Check: shellcheck args in shell/README.md vs .pre-commit-config.yaml
# =============================================================================
check_shellcheck_args() {
  log_info "Checking shellcheck args documentation..."

  local readme="skills/domains/languages/shell/README.md"
  local precommit=".pre-commit-config.yaml"

  if [[ ! -f "$readme" ]] || [[ ! -f "$precommit" ]]; then
    return 0 # Already checked in check_shfmt_flags
  fi

  # Extract shellcheck args from .pre-commit-config.yaml
  # Expected: args: ["-e", "SC1091"]
  local actual_args
  actual_args=$(grep -A 3 'id: shellcheck' "$precommit" | grep 'args:' | sed 's/.*args: \[\(.*\)\].*/\1/' | tr -d '"')

  if [[ -z "$actual_args" ]]; then
    log_info "No shellcheck args found in $precommit (using defaults)"
    return 0
  fi

  # Check if README mentions SC1091 exclusion
  if grep -q "SC1091" "$readme"; then
    log_success "shellcheck exclusions documented in $readme"
  else
    log_info "Consider documenting SC1091 exclusion in $readme"
  fi
}

# =============================================================================
# Main execution
# =============================================================================
main() {
  echo "=========================================="
  echo "Documentation-Config Sync Validation"
  echo "=========================================="
  echo ""

  check_shfmt_flags || true
  check_markdownlint_config || true
  check_shellcheck_args || true

  echo ""
  echo "=========================================="
  if [[ $error_count -eq 0 ]]; then
    echo -e "${GREEN}✓ All documentation in sync${NC}"
    exit 0
  else
    echo -e "${RED}✗ Found $error_count documentation sync issue(s)${NC}"
    exit 1
  fi
}

main "$@"
