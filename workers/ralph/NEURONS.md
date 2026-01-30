# NEURONS.md - [PROJECT_NAME] Repository Map

**Read via subagent** - This is the codebase map for Ralph. Not loaded in first context.

## Purpose

This is the **project map** that Ralph and all agents read on-demand when needed. It maps the entire repository structure, tells you where everything lives, and provides quick lookup for common tasks.

## Navigation Rules (Read This First)

**Deterministic Context Loading Order:**

1. `AGENTS.md` (injected first by loop.sh - operational guide)
2. `PROMPT.md` (injected second - contains conditional logic for plan/build modes)
3. `NEURONS.md` (this file - read via subagent when needed, NOT injected)
4. `workers/IMPLEMENTATION_PLAN.md` (TODO list - read in BUILD mode via subagent)
5. `THOUGHTS.md` (project goals - read as needed via subagent)
6. Project-specific files as needed

**Progressive Disclosure:** Start broad, drill down only when needed. Don't read everything at once.

---

## Repository Layout

[REPLACE: Map your project's directory structure. Use tree format with brief descriptions.]

```text
/path/to/[PROJECT_NAME]/
├── AGENTS.md                    # Ralph operational guide (how to run)
├── NEURONS.md                   # This file (project map - what exists where)
├── THOUGHTS.md                  # Project vision, goals, and success criteria
│
├── ralph/                       # Ralph loop infrastructure (ONLY loop files here)
│   ├── loop.sh                  # Ralph loop runner (bash)
│   ├── verifier.sh              # AC verifier script
│   ├── PROMPT.md                # Unified prompt (plan + build modes)
│   ├── workers/IMPLEMENTATION_PLAN.md   # Persistent TODO list
│   ├── VALIDATION_CRITERIA.md   # Quality gates and acceptance criteria
│   ├── rovodev-config.yml       # RovoDev configuration
│   ├── rules/                   # Acceptance criteria rules
│   │   ├── AC.rules             # Automated checks
│   │   └── MANUAL_APPROVALS.rules # Manual approval records
│   └── .verify/                 # Verifier state/hashes
│
├── [src/]                       # [REPLACE: Main source code directory - NOT ralph/src/!]
│   ├── [components/]            # [REPLACE: Describe what goes here]
│   ├── [modules/]               # [REPLACE: Describe what goes here]
│   └── [utils/]                 # [REPLACE: Describe what goes here]
│
├── [bin/]                       # [REPLACE: Executable scripts - NOT ralph/bin/!]
├── [drivers/]                   # [REPLACE: External binaries like chromedriver]
├── [tests/]                     # [REPLACE: Test files location]
├── [docs/]                      # [REPLACE: Documentation location]
├── [config/]                    # [REPLACE: Configuration files]
└── [scripts/]                   # [REPLACE: Build/deployment scripts]
```text

---

## Quick Reference Lookup

### "I need to..."

[REPLACE: Create lookup table mapping common tasks to locations in your project]

| Task | Check Here |
|------|------------|
| **Understand project structure** | `NEURONS.md` (this file) |
| **Run Ralph loop** | `AGENTS.md` → `bash ralph/loop.sh` |
| **Find TODO list** | `workers/IMPLEMENTATION_PLAN.md` |
| **Check project goals** | `THOUGHTS.md` |
| **[Common task 1]** | `[location/file.ext]` |
| **[Common task 2]** | `[location/file.ext]` |
| **[Common task 3]** | `[location/file.ext]` |
| **Reference Brain Skills** | `./skills/SUMMARY.md` (if brain exists) |
| **Check React patterns** | `./skills/domains/frontend/react-patterns.md` (if brain exists) |

### "Where do I put..."

[REPLACE: Define where different types of content belong in your project]

| Content Type | Location | Modifiable? |
|--------------|----------|-------------|
| **[Content type 1]** | `[directory/]` | ✅ Yes |
| **[Content type 2]** | `[directory/]` | ✅ Yes |
| **[Content type 3]** | `[directory/]` | ✅ Yes |
| **Configuration** | `[config/]` | ✅ Yes |
| **Documentation** | `[docs/]` | ✅ Yes |
| **Tests** | `[tests/]` | ✅ Yes |
| **Build artifacts** | `[build/]` | ❌ Generated |
| **Dependencies** | `[node_modules/]` | ❌ External |

---

## [Main Directory] Structure

### [src/] or [lib/] (X total files)

[REPLACE: Describe your main source code directory]

**Purpose:** [What lives in this directory and why]

**Key Files:**

- `[file1.ext]` - [Description]
- `[file2.ext]` - [Description]
- `[file3.ext]` - [Description]

**Subdirectories:**

- `[subdir1/]` - [Purpose]
- `[subdir2/]` - [Purpose]
- `[subdir3/]` - [Purpose]

**Common Patterns:**

```text
[REPLACE: Show common code patterns or naming conventions]
```text

---

## [Supporting Directory] Structure

### [tests/] or [docs/] (X total files)

[REPLACE: Describe other important directories in your project]

**Purpose:** [What this directory contains]

**Key Files:**

- `[file1.ext]` - [Description]
- `[file2.ext]` - [Description]

---

## Ralph Loop Infrastructure

### Core Files (at ralph/ root)

**Execution:**

- `loop.sh` - Bash script that runs Ralph iterations
- `rovodev-config.yml` - RovoDev configuration

**Prompts:**

- `PROMPT.md` - Unified prompt with conditional logic (plan mode: gap analysis, NO code changes, updates TODO list; build mode: implement top task, validate, commit)
- `workers/IMPLEMENTATION_PLAN.md` - Persistent TODO list (updated by planning mode, read by building mode)
- `VALIDATION_CRITERIA.md` - Quality gates and acceptance criteria

**Stop Sentinel:**

```text
:::COMPLETE:::
```text

Only output when ALL tasks in workers/IMPLEMENTATION_PLAN.md are 100% complete.

---

## Brain Repository Integration (Optional)

> **Note:** Brain integration is optional. If `./brain/` exists, use it for KB lookups. Otherwise, this project works standalone - skip brain references and rely on project-local docs and standard best practices.

### Knowledge Base References

[REPLACE: Document how this project uses brain repository knowledge]

**If brain repository is available:**

**Performance Patterns (if React/Next.js):**

- Path: `./skills/domains/frontend/`
- Entry: `HOTLIST.md` → `INDEX.md` → `rules/*.md`
- Usage: Consult before implementing React components

**Domain Conventions:**

- Path: `./skills/domains/`
- Relevant domains: `[domain1.md]`, `[domain2.md]`
- Usage: Follow established patterns for [specific functionality]

**Project-Specific Knowledge:**

- Path: `./skills/projects/[project-slug].md`
- Usage: Document learnings that might benefit other projects

### Path Conventions

- Brain references use: `./skills/` (relative from project root, if brain exists)
- Internal references use: `./relative/path` (within project)
- Absolute paths: Avoid - use relative paths for portability

### Standalone Mode

If brain repository is not present:

- Skip all `./brain/` references
- Rely on `docs/` for project documentation
- Use standard best practices for your tech stack

---

## File Counts and Validation

### Quick Checks

[REPLACE: Define validation commands for your project structure]

```bash
# Source file count
find [src/] -name "*.[ext]" | wc -l
# Should be: [X]

# Test file count
find [tests/] -name "*.[ext]" | wc -l
# Should be: [Y]

# Component count (if applicable)
find [src/components/] -name "*.[ext]" | wc -l
# Should be: [Z]
```text

### Validation Commands (Backpressure)

```bash
# Verify directory structure
ls -la [src/] [tests/] [config/]

# Check [specific integrity check for your project]
[validation command 1]

# Verify [another important check]
[validation command 2]

# Test script syntax (if bash/shell scripts)
bash -n [script.sh]

# Check critical files exist
ls -lh AGENTS.md NEURONS.md THOUGHTS.md ralph/PROMPT.md workers/IMPLEMENTATION_PLAN.md
```text

---

## Read-Only vs Modifiable Sections

### ❌ DO NOT MODIFY (Read-Only)

[REPLACE: List directories/files that should not be modified]

- **[directory/]** - [Reason - e.g., "Generated files", "External dependencies"]
- **[directory/]** - [Reason]
- **Brain references** - `./skills/` (upstream knowledge)

### ✅ MODIFIABLE (Active Development)

[REPLACE: List directories/files that are actively developed]

- **AGENTS.md** - Ralph operational guide
- **NEURONS.md** - This project map
- **THOUGHTS.md** - Project vision and goals
- **ralph/** - Ralph loop infrastructure
- **[src/]** - Main source code
- **[tests/]** - Test files
- **[config/]** - Configuration files

---

## Common Workflows

### [Workflow 1 - e.g., "Adding New Feature"]

[REPLACE: Document common workflows in your project]

1. Check if it exists: `grep -r "feature_name" [src/]`
2. Create: `[src/new-feature.ext]`
3. Add tests: `[tests/new-feature.test.ext]`
4. Update: `[relevant documentation]`
5. Validate: `[validation command]`

### [Workflow 2 - e.g., "Running Tests"]

1. Run all tests: `[test command]`
2. Run specific test: `[test command with args]`
3. Check coverage: `[coverage command]`
4. Validate results: `[validation check]`

### [Workflow 3 - e.g., "Building for Production"]

1. Clean build directory: `[clean command]`
2. Run build: `[build command]`
3. Validate output: `[validation command]`
4. Test production build: `[test command]`

### Running Ralph Loop

```bash
cd [/path/to/project/ralph/]
bash loop.sh                           # Single iteration
bash loop.sh --iterations 10           # Multiple iterations
bash loop.sh --prompt PROMPT.md        # Use unified prompt
```text

### Validating Project Integrity

```bash
# File counts
[validation command 1]

# Critical checks
[validation command 2]

# Structure verification
tree -L 2 -I '[exclude-dirs]'
```text

---

## Technology-Specific Patterns

[REPLACE: Add sections specific to your tech stack]

### [For React/Next.js Projects]

**Component Structure:**

```text
components/
├── ComponentName/
│   ├── index.tsx          # Component implementation
│   ├── ComponentName.module.css
│   └── ComponentName.test.tsx
```text

**Performance Checklist:**

- ✅ Memoization where needed (see brain: `./skills/domains/frontend/react-patterns.md`)
- ✅ Dynamic imports for heavy components
- ✅ Image optimization
- ✅ Bundle size monitoring

### [For Python Projects]

**Module Structure:**

```text
[src/]
├── module_name/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
```text

### [For Other Tech Stacks]

[Add relevant patterns for your technology]

---

## Summary

This [PROJECT_NAME] repository contains:

- **[X] source files** ([description])
- **[Y] test files** ([description])
- **[Z] configuration files** ([description])
- **Ralph loop infrastructure** (bash-based, WSL2)

**Remember:**

1. Read NEURONS.md (this file) via subagent when needed
2. Use progressive disclosure (broad → specific)
3. Search before creating (don't assume missing)
4. Follow Brain Skills patterns (if brain exists): `./skills/SUMMARY.md`
5. Consult React patterns (if applicable and brain exists): `./skills/domains/frontend/react-patterns.md`

**For questions about:**

- **How to run Ralph** → See AGENTS.md
- **What exists where** → You're reading it (NEURONS.md)
- **Project goals** → See THOUGHTS.md
- **Brain Skills patterns** → See `./skills/SUMMARY.md` (if brain exists)
- **React optimization** → See `./skills/domains/frontend/react-patterns.md` (if brain exists)

> **Note:** All brain references are optional. If `./brain/` doesn't exist, skip those references - this project works standalone.
