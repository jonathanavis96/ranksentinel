#!/usr/bin/env bash
# verify-brain.sh - Brain consistency checker
# Run daily to detect maintenance issues and auto-update MAINTENANCE.md
#
# Usage: bash verify-brain.sh [--quiet]
#   --quiet: Only output if issues found

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RALPH_DIR="$(dirname "$SCRIPT_DIR")"
BRAIN_ROOT="$(cd "$RALPH_DIR/../.." && pwd)"
cd "$RALPH_DIR"

MAINTENANCE_FILE=".maintenance/MAINTENANCE.md"
QUIET="${1:-}"
TODAY=$(date +%Y-%m-%d)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

issues_found=0
new_maintenance_items=()

log_info() {
  [[ "$QUIET" != "--quiet" ]] && echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}⚠${NC} $1"
  ((issues_found++)) || true
}

log_error() {
  echo -e "${RED}✗${NC} $1"
  ((issues_found++)) || true
}

add_maintenance_item() {
  local item="- [ ] $TODAY: $1"
  # Check if similar item already exists in MAINTENANCE.md (ignore date prefix)
  local item_text="$1"
  if [[ -f "$MAINTENANCE_FILE" ]] && grep -qF "$item_text" "$MAINTENANCE_FILE" 2>/dev/null; then
    # Item already exists, skip
    return
  fi
  new_maintenance_items+=("$item")
}

# =============================================================================
# CHECK 1: Skills Index Completeness
# =============================================================================
check_skills_index() {
  log_info "Checking skills index completeness..."

  local index_file="$BRAIN_ROOT/skills/index.md"
  if [[ ! -f "$index_file" ]]; then
    log_error "skills/index.md not found"
    add_maintenance_item "Create skills/index.md"
    return
  fi

  # Find all skill files in domains/ and projects/
  local missing_from_index=()
  while IFS= read -r skill_file; do
    local basename
    basename=$(basename "$skill_file")
    # Skip README files and index files
    [[ "$basename" == "README.md" || "$basename" == "index.md" ]] && continue

    # Check if file is referenced in index.md
    if ! grep -q "$basename" "$index_file" 2>/dev/null; then
      missing_from_index+=("$skill_file")
    fi
  done < <(find "$BRAIN_ROOT/skills/domains" "$BRAIN_ROOT/skills/projects" -name "*.md" -type f 2>/dev/null)

  if [[ ${#missing_from_index[@]} -gt 0 ]]; then
    log_warn "Skills missing from index.md:"
    for f in "${missing_from_index[@]}"; do
      echo "       - $f"
    done
    add_maintenance_item "Add missing skills to index.md: ${missing_from_index[*]}"
  else
    log_info "All skills listed in index.md"
  fi
}

# =============================================================================
# CHECK 2: SUMMARY.md Completeness
# =============================================================================
check_summary_completeness() {
  log_info "Checking SUMMARY.md completeness..."

  local summary_file="$BRAIN_ROOT/skills/SUMMARY.md"
  if [[ ! -f "$summary_file" ]]; then
    log_error "skills/SUMMARY.md not found"
    add_maintenance_item "Create skills/SUMMARY.md"
    return
  fi

  local missing_from_summary=()
  while IFS= read -r skill_file; do
    local basename
    basename=$(basename "$skill_file")
    [[ "$basename" == "README.md" || "$basename" == "SUMMARY.md" || "$basename" == "index.md" ]] && continue

    if ! grep -q "$basename" "$summary_file" 2>/dev/null; then
      missing_from_summary+=("$skill_file")
    fi
  done < <(find "$BRAIN_ROOT/skills/domains" "$BRAIN_ROOT/skills/projects" -name "*.md" -type f 2>/dev/null)

  if [[ ${#missing_from_summary[@]} -gt 0 ]]; then
    log_warn "Skills missing from SUMMARY.md:"
    for f in "${missing_from_summary[@]}"; do
      echo "       - $f"
    done
    add_maintenance_item "Add missing skills to SUMMARY.md: ${missing_from_summary[*]}"
  else
    log_info "All skills listed in SUMMARY.md"
  fi
}

# =============================================================================
# CHECK 3: Template Sync Check
# =============================================================================
check_template_sync() {
  log_info "Checking template synchronization..."

  # Define source -> template mappings
  # Format: "source_file:template_file:check_type"
  # check_type: "hash" = full file match, "structure" = key sections only
  local mappings=(
    "$BRAIN_ROOT/skills/self-improvement/SKILL_TEMPLATE.md:$BRAIN_ROOT/templates/ralph/SKILL_TEMPLATE.md:hash"
    "PROMPT.md:$BRAIN_ROOT/templates/ralph/PROMPT.md:structure"
    "IMPLEMENTATION_PLAN.md:$BRAIN_ROOT/templates/ralph/IMPLEMENTATION_PLAN.project.md:structure"
  )

  # Required structural sections for templates
  local required_sections=(
    "## Maintenance Check"
    "## MAINTENANCE"
  )

  for mapping in "${mappings[@]}"; do
    local source="${mapping%%:*}"
    local rest="${mapping#*:}"
    local template="${rest%%:*}"
    local check_type="${rest##*:}"

    # Skip if source doesn't exist
    [[ ! -f "$source" ]] && continue

    # Skip if template doesn't exist (might be intentional)
    if [[ ! -f "$template" ]]; then
      # Only warn if template directory exists
      local template_dir
      template_dir=$(dirname "$template")
      if [[ -d "$template_dir" ]]; then
        log_warn "Template missing: $template (source: $source)"
        add_maintenance_item "Create or sync template: $template from $source"
      fi
      continue
    fi

    if [[ "$check_type" == "hash" ]]; then
      # Full file comparison
      local source_hash
      source_hash=$(sha256sum "$source" 2>/dev/null | cut -d' ' -f1)
      local template_hash
      template_hash=$(sha256sum "$template" 2>/dev/null | cut -d' ' -f1)

      if [[ "$source_hash" != "$template_hash" ]]; then
        log_warn "Template out of sync: $template differs from $source"
        add_maintenance_item "Sync template $template with source $source"
      fi
    elif [[ "$check_type" == "structure" ]]; then
      # Check only that required sections exist in template
      local missing_sections=()
      for section in "${required_sections[@]}"; do
        if ! grep -qF "$section" "$template" 2>/dev/null; then
          missing_sections+=("$section")
        fi
      done

      if [[ ${#missing_sections[@]} -gt 0 ]]; then
        log_warn "Template $template missing required sections: ${missing_sections[*]}"
        add_maintenance_item "Add missing sections to $template: ${missing_sections[*]}"
      fi
    fi
  done

  log_info "Template sync check complete"
}

# =============================================================================
# CHECK 4: Recently Modified Files (last 7 days)
# =============================================================================
check_recently_modified() {
  log_info "Checking recently modified files..."

  local modified_files=()
  while IFS= read -r file; do
    modified_files+=("$file")
  done < <(find . -name "*.md" -type f -mtime -7 ! -path "./.git/*" ! -name "MAINTENANCE.md" 2>/dev/null | head -20)

  if [[ ${#modified_files[@]} -gt 0 ]]; then
    log_info "Recently modified files (last 7 days):"
    for f in "${modified_files[@]}"; do
      echo "       - $f"
    done
  fi
}

# =============================================================================
# CHECK 5: Broken Links in Skills
# =============================================================================
check_broken_links() {
  log_info "Checking for broken links in skills..."

  local broken_links=()
  while IFS= read -r skill_file; do
    # Extract markdown links: [text](path)
    while IFS= read -r link; do
      # Skip external links and anchors
      [[ "$link" =~ ^https?:// || "$link" =~ ^# || -z "$link" ]] && continue

      # Resolve relative path from skill file location
      local skill_dir
      skill_dir=$(dirname "$skill_file")
      local target="$skill_dir/$link"

      # Normalize path
      target=$(realpath -m "$target" 2>/dev/null || echo "$target")

      # Check if target exists (strip any #anchor)
      local target_file="${target%%#*}"
      if [[ ! -e "$target_file" && ! -e "$SCRIPT_DIR/$link" ]]; then
        broken_links+=("$skill_file -> $link")
      fi
    done < <(grep -oP '\[.*?\]\(\K[^)]+' "$skill_file" 2>/dev/null || true)
  done < <(find "$BRAIN_ROOT/skills" -name "*.md" -type f 2>/dev/null)

  if [[ ${#broken_links[@]} -gt 0 ]]; then
    log_warn "Broken links detected:"
    for link in "${broken_links[@]}"; do
      echo "       - $link"
    done
    add_maintenance_item "Fix broken links in skills files"
  else
    log_info "No broken links detected"
  fi
}

# =============================================================================
# CHECK 6: Skills Missing Quick Reference Tables (new convention)
# =============================================================================
check_quick_reference_tables() {
  log_info "Checking skills for Quick Reference tables..."

  local missing_tables=()
  while IFS= read -r skill_file; do
    local basename
    basename=$(basename "$skill_file")
    # Skip meta files
    [[ "$basename" == "README.md" || "$basename" == "SUMMARY.md" || "$basename" == "index.md" || "$basename" == "conventions.md" ]] && continue

    # Check for Quick Reference section
    if ! grep -qi "## Quick Reference\|## At a Glance\|### Common Mistakes" "$skill_file" 2>/dev/null; then
      missing_tables+=("$skill_file")
    fi
  done < <(find "$BRAIN_ROOT/skills/domains" -name "*.md" -type f 2>/dev/null)

  if [[ ${#missing_tables[@]} -gt 0 ]]; then
    log_warn "Skills missing Quick Reference tables:"
    for f in "${missing_tables[@]}"; do
      echo "       - $f"
    done
    add_maintenance_item "Add Quick Reference tables to: ${missing_tables[*]}"
  else
    log_info "All skills have Quick Reference tables"
  fi
}

# =============================================================================
# UPDATE MAINTENANCE.md
# =============================================================================
update_maintenance_file() {
  if [[ ${#new_maintenance_items[@]} -eq 0 ]]; then
    log_info "No new maintenance items to add"
    return
  fi

  echo ""
  echo -e "${YELLOW}Adding ${#new_maintenance_items[@]} items to MAINTENANCE.md${NC}"

  # Create MAINTENANCE.md if it doesn't exist
  if [[ ! -f "$MAINTENANCE_FILE" ]]; then
    cat >"$MAINTENANCE_FILE" <<'EOF'
# Brain Maintenance

This file tracks maintenance tasks for the brain repository.
Run `bash verify-brain.sh` daily to update this file.

## Triggered Items
<!-- Auto-populated by verify-brain.sh -->

## Periodic Checks (Daily)
<!-- Run verify-brain.sh daily to check these -->
- [ ] Verify all skills listed in index.md
- [ ] Check templates match sources
- [ ] Review recently modified files for consistency
- [ ] Check for broken links
- [ ] Verify skills have Quick Reference tables
EOF
  fi

  # Append new items to Triggered Items section
  # Find the line number of "## Triggered Items" and insert after the comment
  local temp_file
  temp_file=$(mktemp)
  local inserted=false

  while IFS= read -r line; do
    echo "$line" >>"$temp_file"
    if [[ "$line" == "<!-- Auto-populated by verify-brain.sh -->" && "$inserted" == false ]]; then
      for item in "${new_maintenance_items[@]}"; do
        echo "$item" >>"$temp_file"
      done
      inserted=true
    fi
  done <"$MAINTENANCE_FILE"

  mv "$temp_file" "$MAINTENANCE_FILE"

  echo ""
  echo "New maintenance items added:"
  for item in "${new_maintenance_items[@]}"; do
    echo "  $item"
  done
}

# =============================================================================
# MAIN
# =============================================================================
main() {
  echo "=================================="
  echo "Brain Consistency Check - $TODAY"
  echo "=================================="
  echo ""

  check_skills_index
  check_summary_completeness
  check_template_sync
  check_broken_links
  check_quick_reference_tables
  check_recently_modified

  echo ""
  echo "=================================="

  if [[ $issues_found -eq 0 ]]; then
    echo -e "${GREEN}All checks passed!${NC}"
  else
    echo -e "${YELLOW}Found $issues_found issue(s)${NC}"
    update_maintenance_file
  fi

  echo "=================================="

  # Exit with appropriate code
  [[ $issues_found -gt 0 ]] && exit 1 || exit 0
}

main
