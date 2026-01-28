# Project Guidance for AI Agents

## Knowledge Base (Optional Integration)

> **Brain Integration:** If `./brain/` exists, use it for KB lookups. Otherwise, proceed without external brain KB - this project works standalone.

### Progressive Disclosure: Always Read in This Order

**If brain repository is available, ALWAYS start here:**

1. `./brain/skills/SUMMARY.md` - Knowledge base overview and usage guide
2. `./brain/skills/domains/frontend/react-patterns.md` - Top 10 most applicable performance rules (covers 80% of scenarios)

**Only if HOTLIST doesn't cover your scenario:**
3. `./brain/skills/index.md` - Full categorized rule index (find specific categories)

**Only when you need deep knowledge on a specific topic:**
4. `./brain/skills/domains/frontend/react-patterns.md` (see sections within) - Individual rule files (read ONLY specific rules you need)

❌ **NEVER scan all 45 rules by default** - Token-inefficient and slow  
✅ **Use the hierarchy above** - Fast and targeted  
✅ **Only open specific rule files when needed for the task** - don't read everything "just in case"

### Why This Order Matters

- **Token efficiency**: HOTLIST covers most common scenarios with minimal tokens
- **Faster results**: Start broad, drill down only when needed
- **Avoid overwhelm**: Don't read all rules unless explicitly instructed

### Standalone Mode

If the brain repository is not present (e.g., project cloned standalone), skip the KB lookups above and rely on:

- Project-local documentation in `docs/`
- Standard best practices for your tech stack
- Any project-specific conventions documented in this file

## Knowledge Growth Rule (Mandatory)

When you discover a new convention, architectural decision, or project-specific pattern:

1. **Create a KB file** in the brain repo:
   - Project-specific: `./brain/skills/projects/<project-slug>.md`
   - Domain/cross-project: `./brain/skills/domains/<domain>.md`

2. **Update the index**: Add a link in `./brain/skills/SUMMARY.md`

3. **Structure new KB files** with:

   ```markdown
   # [Title]
   
   ## Why This Exists
   [Explain the problem this solves or decision rationale]
   
   ## When to Use It
   [Specific scenarios or conditions for applying this knowledge]
   
   ## Details
   [The actual knowledge, patterns, conventions, etc.]
   ```

## Skills + Self-Improvement Protocol

> **Note:** This protocol requires the brain repository at `./brain/`. If running standalone (brain not present), skip this section.

**Start of iteration:**

1. Study `./brain/skills/SUMMARY.md` for overview
2. Check `./brain/skills/index.md` for available skills
3. Review `./brain/skills/self-improvement/GAP_CAPTURE_RULES.md` for capture protocol

**End of iteration:**

1. If you used undocumented knowledge/procedure/tooling:
   - Search `./brain/skills/` for existing matching skill
   - Search `cortex/GAP_CAPTURE.md` for existing local gap entry
   - If not found: append new entry to `cortex/GAP_CAPTURE.md` (or use the helper below)
   - Create marker: `touch cortex/.gap_pending`

**Helper (recommended):**

```bash
bash workers/ralph/capture_gap.sh "Suggested Skill Name" \
  --type "Pattern" \
  --priority "P1" \
  --why "1-2 lines" \
  --trigger "what you were doing" \
  --evidence "paths/notes"
```text
2. Brain's Cortex will sync gaps on next session (see Rule 6: Marker Protocol)

## Parallelism Rule

**Reading/searching/spec review**: Use up to **100 parallel subagents** for maximum efficiency

- File reading, searching, spec analysis, documentation review
- Gathering context from multiple sources simultaneously

**Build/tests/benchmarks**: Use exactly **1 agent**

- Running build commands, executing tests, benchmarks
- Making file modifications and commits

## Core Principles

### Before Making Changes

1. **Search the codebase** - Don't assume anything is missing; search first
2. **Read targeted knowledge** - Follow the hierarchy: SUMMARY → HOTLIST → specific rules
3. **Check existing patterns** - Look for established conventions in the codebase before inventing new ones

### Code Quality

- Prefer standard patterns from the knowledge base over custom solutions
- Keep components small and focused
- Write clear, self-documenting code with minimal comments

### Project Structure

**⚠️ CRITICAL: Source code goes in PROJECT ROOT, not in workers/ralph/!**

```text
project-root/           ← Working directory for application files
├── src/                ← Source code HERE
├── package.json        ← Config files HERE
├── tsconfig.json       
├── README.md           ← Project readme
└── workers/ralph/      ← Ralph files (loop + project context)
    ├── AGENTS.md       ← This file (agent guidance)
    ├── THOUGHTS.md     ← Project vision
    ├── NEURONS.md      ← Codebase map
    ├── PROMPT.md       ← Loop prompt
    ├── workers/IMPLEMENTATION_PLAN.md  ← Task tracking
    ├── VALIDATION_CRITERIA.md  ← Quality gates
    ├── RALPH.md        ← Loop contract
    ├── loop.sh         ← Loop runner
    ├── kb/             ← Project knowledge base
    └── logs/           ← Iteration logs
```

- **Source code**: Always in `src/` at project root (NOT `workers/ralph/src/`)
- **Config files**: Always at project root (`package.json`, `tsconfig.json`, etc.)
- **workers/ralph/ directory**: Contains loop infrastructure AND project context (AGENTS, THOUGHTS, NEURONS, kb/, logs/)
- Keep project goals and vision in `workers/ralph/THOUGHTS.md`
- Maintain `workers/IMPLEMENTATION_PLAN.md` as a prioritized task list

## Environment Prerequisites

- **Environment:** WSL (Windows Subsystem for Linux) on Windows 11 with Ubuntu
- **Shell:** bash (comes with WSL Ubuntu)
- **Atlassian CLI:** `acli` - <https://developer.atlassian.com/cloud/cli/>
- **RovoDev:** `acli rovodev auth && acli rovodev usage site`

### WSL/Windows 11 Specifics

- Working directory: `/mnt/c/...` or `/home/...` depending on where repository is cloned
- Git line endings: Use `core.autocrlf=input` to avoid CRLF issues
- File permissions: WSL handles Unix permissions on Windows filesystem
- Path separators: Use Unix-style `/` paths (WSL translates automatically)

## Ralph Integration

This project uses the Ralph Wiggum iterative loop for systematic development:

- **Single unified prompt**: See `workers/ralph/PROMPT.md` (determines mode from iteration number)
- **Progress tracking**: All work logged in `workers/ralph/progress.txt`
- **Completion**: Look for `:::COMPLETE:::` sentinel

## RovoDev + CLI Guardrails

When working with RovoDev and Atlassian CLI:

- **Always run repo scripts with PowerShell 7** (`pwsh`), not Windows PowerShell 5.1 (`powershell.exe`)
- **If Ralph/RovoDev appears to "hang" or "wait"**, first run:
  - `acli rovodev auth status`
  - `acli rovodev usage site` (select a valid site if prompted)
  - then retry
- **Don't assume the correct site is the one open in the browser** - rely on CLI-selected site
- **If a command needs interactivity**, the agent must clearly tell the user what input/action is required
- **Avoid long-running background watchers/polling** unless the user explicitly wants it - prefer short, bounded runs

### Secrets and Tokens

- **Never paste API tokens, secrets, or credentials** into logs, markdown, or console output
- Use placeholders like `PASTE_TOKEN_HERE` and instruct the user to provide them locally

### UTF-8 Logging

- **Any PowerShell file writes must explicitly use UTF-8**:
  - `Out-File -Encoding utf8`
  - `Add-Content -Encoding utf8` (or equivalent)
- Avoid UTF-16 defaults that cause NUL spam in VS Code

## Project-Specific Notes

[Add project-specific conventions, architecture decisions, and patterns here]
