# Brain Reorganization Proposal

**Created:** 2026-01-20  
**Status:** Draft for discussion

---

## Current State

The `brain/ralph/` root has 26 files + 8 directories. It's cluttered:

### Root Level Files (26 total)

| Category | Files | Count |
|----------|-------|-------|
| **Core Runtime** | `loop.sh`, `verifier.sh`, `PROMPT.md` | 3 |
| **Task Monitors** | `current_ralph_tasks.sh`, `thunk_ralph_tasks.sh`, `render_ac_status.sh` | 3 |
| **Project Setup** | `new-project.sh`, `pr-batch.sh` | 2 |
| **Rules** | `AC.rules`, `AC-hygiene-additions.rules`, `MANUAL_APPROVALS.rules` | 3 |
| **Planning Docs** | `workers/IMPLEMENTATION_PLAN.md`, `THOUGHTS.md`, `workers/ralph/THUNK.md`, `VALIDATION_CRITERIA.md` | 4 |
| **Reference Docs** | `AGENTS.md`, `NEURONS.md`, `README.md` | 3 |
| **Historical** | `HISTORY.md`, `CHANGES.md`, `CODERABBIT_REVIEW_ANALYSIS.md` | 3 |
| **Edge Cases** | `EDGE_CASES.md`, `TEST_SCENARIOS.md` | 2 |
| **Config** | `rovodev-config.yml` | 1 |
| **Backup Files** | `*.bak` files | 2 |

### Directories (8 total)

| Directory | Purpose | Files |
|-----------|---------|-------|
| `.verify/` | Security - waivers, hashes | Good ✓ |
| `.maintenance/` | Consistency checks | Good ✓ (new) |
| `docs/` | Documentation | Only 2 files |
| `generators/` | NEURONS/THOUGHTS generators | Good ✓ |
| `logs/` | Session logs | Good ✓ |
| `old_sh/` | Deprecated scripts | Archive |
| `skills/` | Knowledge base | Good ✓ |
| `templates/` | Project templates | Needs cleanup |

---

## Proposed Structure

```text
brain/ralph/
├── .gitignore
├── .maintenance/           # Consistency checks (keep)
├── .verify/                # Security system (keep)
│
├── AGENTS.md               # KEEP at root - entry point for agents
├── README.md               # KEEP at root - human entry point
├── PROMPT.md               # KEEP at root - core runtime
│
├── bin/                    # NEW - executable scripts
│   ├── loop.sh             # Core loop
│   ├── verifier.sh         # AC verifier
│   ├── new-project.sh      # Project generator
│   ├── pr-batch.sh         # PR batching
│   └── monitors/           # NEW - task monitor scripts
│       ├── current_ralph_tasks.sh
│       ├── thunk_ralph_tasks.sh
│       └── render_ac_status.sh
│
├── rules/                  # NEW - acceptance criteria
│   ├── AC.rules
│   ├── AC-hygiene-additions.rules
│   └── MANUAL_APPROVALS.rules
│
├── docs/                   # EXPAND - all documentation
│   ├── BOOTSTRAPPING.md
│   ├── REFERENCE_SUMMARY.md
│   ├── HISTORY.md          # Move from root
│   ├── CHANGES.md          # Move from root
│   ├── EDGE_CASES.md       # Move from root
│   └── TEST_SCENARIOS.md   # Move from root
│
├── planning/               # NEW - active planning files
│   ├── workers/IMPLEMENTATION_PLAN.md
│   ├── THOUGHTS.md
│   ├── workers/ralph/THUNK.md
│   ├── NEURONS.md
│   └── VALIDATION_CRITERIA.md
│
├── analysis/               # NEW - review/analysis files
│   └── CODERABBIT_REVIEW_ANALYSIS.md
│
├── generators/             # KEEP
├── logs/                   # KEEP
├── old_sh/                 # KEEP (or delete?)
├── skills/                 # KEEP
└── templates/              # KEEP (needs internal cleanup)
```text

---

## Benefits

| Before | After |
|--------|-------|
| 26 files at root | 3 files at root |
| Hard to find scripts | Scripts in `bin/` |
| Docs scattered | Docs in `docs/` |
| Planning files mixed with reference | Clear separation |
| Rules mixed with scripts | Rules in `rules/` |

---

## Migration Impact

### Files That Reference Paths

These files would need path updates:

| File | References To Update |
|------|---------------------|
| `loop.sh` | `verifier.sh`, `PROMPT.md`, `workers/ralph/THUNK.md`, etc. |
| `PROMPT.md` | Various doc references |
| `AGENTS.md` | File locations |
| `templates/ralph/*` | All path references |
| `generators/*.sh` | Output paths |

### Estimate

- **Low risk:** Moving docs (HISTORY, CHANGES, etc.) - rarely referenced
- **Medium risk:** Moving planning files - referenced by loop.sh
- **Higher risk:** Moving scripts - many cross-references

---

## Phased Approach

### Phase A: Low Risk (docs only)
1. Move HISTORY.md, CHANGES.md, EDGE_CASES.md, TEST_SCENARIOS.md → `docs/`
2. Update any references (grep first)
3. Delete .bak files

### Phase B: Medium Risk (rules + analysis)
1. Create `rules/` and move AC*.rules, MANUAL_APPROVALS.rules
2. Create `analysis/` and move CODERABBIT_REVIEW_ANALYSIS.md
3. Update verifier.sh to find rules in new location

### Phase C: Higher Risk (scripts + planning)
1. Create `bin/` and `bin/monitors/`
2. Move scripts, update all cross-references
3. Create `planning/` and move planning docs
4. Update loop.sh, PROMPT.md, generators

---

## Questions for Discussion

1. **Do you want all phases, or just Phase A (low risk)?**
2. **Should `old_sh/` be deleted entirely?**
3. **Should templates also be reorganized internally?**
4. **Is `bin/` the right name, or prefer `scripts/`?**

---

## Alternative: Minimal Cleanup

If full reorg is too much, just do:

1. Delete `.bak` files
2. Move historical docs to `docs/`
3. Create `rules/` for AC files
4. Done - reduces root from 26 to ~18 files

---

_Discuss tomorrow and decide on scope._
