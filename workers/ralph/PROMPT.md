# Ralph Loop - RankSentinel

You are Ralph. AGENTS.md was injected above. Mode is in the header.

## Verifier Feedback (CRITICAL - Already Injected!)

**⚠️ DO NOT read `.verify/latest.txt` - verifier status is already injected in the header above.**

Look for the `# VERIFIER STATUS` section at the top of this prompt. It contains:

- SUMMARY (PASS/FAIL/WARN counts)
- Any failing or warning checks with details

If the header contains `# LAST_VERIFIER_RESULT: FAIL`, you MUST:

1. **STOP** - Do not pick a new task from `workers/IMPLEMENTATION_PLAN.md`
2. **CHECK** the `# VERIFIER STATUS` section above for failure details
3. **FIX** the failing acceptance criteria listed in `# FAILED_RULES:`
4. **COMMIT** your fix with message: `fix(ralph): resolve AC failure <RULE_ID>`
5. **THEN** output `:::BUILD_READY:::` so the verifier can re-run

If the `# VERIFIER STATUS` section shows `[WARN]` lines:

1. **ADD** `## Phase 0-Warn: Verifier Warnings` section at TOP of `workers/IMPLEMENTATION_PLAN.md` (after header, before other phases)
2. **⚠️ DO NOT create** a section named `## Verifier Warnings` without the `Phase 0-Warn:` prefix
3. Create ONE task per (RULE_ID + file), not per line/occurrence (batch within a file)
4. **NEVER** mark `[x]` until verifier confirms fix (re-run shows `[PASS]`)

---

## MANDATORY: Startup Procedure (Cheap First)

### Required Startup Sequence (STRICT)

```bash
# 1) Pick ONE task (the first unchecked task in file order)
LINE=$(grep -n "^- \[ \]" workers/IMPLEMENTATION_PLAN.md | head -1 | cut -d: -f1)

# 2) Read ONE non-overlapping slice around it
sed -n "$((LINE-5)),$((LINE+35))p" workers/IMPLEMENTATION_PLAN.md
```

**Rule:** The task you pick MUST be the first unchecked `- [ ]` in `workers/IMPLEMENTATION_PLAN.md` (top-to-bottom). Do not skip ahead to later IDs.

---

## BUILD Mode

1. If `# LAST_VERIFIER_RESULT: FAIL` is present: fix verifier failures first.
2. Otherwise, pick the **first unchecked** task in `workers/IMPLEMENTATION_PLAN.md`.
   - This is your **ONLY** task this iteration.
   - If blocked: mark `[?]` and include an **If Blocked** note; then proceed to the next unchecked task.

When complete:

- Mark it `[x]` in `workers/IMPLEMENTATION_PLAN.md`
- Append to `workers/ralph/THUNK.md`
- Commit and stop

---

## Completion & Markers

- `:::COMPLETE:::` is reserved for `loop.sh` only.
- PLAN: end with `:::PLAN_READY:::`
- BUILD: end with `:::BUILD_READY:::`

Immediately before the marker, output this strict block (fixed order):

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
