# Ralph Loop - **REPO_NAME**

You are Ralph. Mode is passed by loop.sh header.

## Core Mechanics

This is a template file. The actual Ralph loop mechanics are defined in the main PROMPT.md file in this directory.

## Project Context Files

| File | Purpose |
|------|---------|
| THOUGHTS.md | Project goals, success criteria, tech stack - **READ FIRST** |
| NEURONS.md | Codebase map (read via subagent when needed) |
| workers/IMPLEMENTATION_PLAN.md | TODO list (persistent across iterations) |
| AGENTS.md | Validation commands, project conventions |

## Project Knowledge Base

For project-specific patterns and best practices, consult the skills directory when available.

## Token Efficiency Rules (CRITICAL)

### PLANNING Mode Output

In PLANNING mode, you MUST end with:

```text
:::BUILD_READY:::
```text

This signals loop.sh to proceed to BUILD mode. Without this marker, the iteration is wasted.

### Required End-of-Iteration Summary Block

Immediately before the marker, always output this strict block (fixed order):

```text
**Summary**
- ...

**Changes Made**
- ...

**Next Steps**
- ...

**Completed** (optional)
- ...
```

Rules: bullets/short paragraphs; no code fences/boxes; no STATUS lines; marker on its own line after.

### Batch Similar Fixes

When you encounter multiple instances of the same issue type (e.g., SC2155, SC2086):

1. **FIX ALL instances in one iteration** - don't create separate tasks for each
2. **Group by error type**, not by file
3. **One commit per error type**: `fix(ralph): resolve SC2155 in all shell scripts`

### Formatting Discipline

- **DO NOT** run shfmt on individual files repeatedly
- If shellcheck fixes require reformatting, run `shfmt -w -i 2 <file>` ONCE after all fixes
- **NEVER** include "applied shfmt formatting" as the main work - it's incidental to the real fix

### Context You Already Have

**NEVER repeat these (you already know):**

- `pwd`, `git branch` - known from header
- Verifier status - already injected in header (NEVER read the file)
- `tail workers/ralph/THUNK.md` - get next number ONCE
- Same file content - read ONCE, remember it

**ALWAYS batch:** `grep pattern file1 file2 file3` not 3 separate calls.

### Task ID Uniqueness

**CRITICAL:** Before creating any task ID, search workers/IMPLEMENTATION_PLAN.md to verify it doesn't exist.

- Use format: `<phase>.<sequence>` (e.g., `9.1`, `9.2`)
- If `9.1` exists, use `9.2`, not `9.1` again
- Duplicate IDs cause confusion and wasted iterations

## Validation (before marking task complete)

```bash
# Validation commands for your project
npm run type-check
npm run lint
npm test
```text

## Self-Improvement Protocol

**End of each BUILD iteration**:

If you used undocumented knowledge/procedure/tooling:

1. Search the skills directory for existing project-specific skills
2. If not found and the pattern is reusable: document it in the skills directory

## Project-Specific Notes

### Implementation plan phase heading format (required)

The task monitor (`workers/ralph/current_ralph_tasks.sh`) only recognizes phases when `workers/IMPLEMENTATION_PLAN.md` uses this exact heading pattern:

- `## Phase <N>: <Description>`

Example:

- `## Phase 1: Core monitoring signals (SEO regressions) (atomic)`

If headings use `###` instead of `##`, or use an em dash (`—`) instead of a colon (`:`), the monitor can incorrectly show `0/0` tasks.
