# Project Guidance for AI Agents (RankSentinel)

## Start Here (mandatory)

Before any work, read in this order:

1. `BOOTSTRAP.md` — MVP scope, schedules, severity model, normalization rules, cron semantics
2. `workers/ralph/THOUGHTS.md` — product vision, goals/non-goals, success metrics
3. `workers/ralph/VALIDATION_CRITERIA.md` — quality gates and verification commands
4. `workers/IMPLEMENTATION_PLAN.md` — the prioritized task list (WEBSITE)
5. `workers/PLAN_MAIN.md` — the backend/app implementation plan (reference)

## Task ordering rule (CRITICAL)

- Always work **top-to-bottom** in `workers/IMPLEMENTATION_PLAN.md`.
- In each BUILD iteration, implement **only the first unchecked** task (`- [ ]`) in file order.
- Do **not** skip to later task IDs unless the current first task is explicitly blocked.
  - If blocked, mark it `[?]` and add an **If Blocked** note, then continue to the next unchecked task.

## Brain Knowledge Base (optional integration)

> If `./brain/` exists, use it. Otherwise, proceed using project-local docs.

Progressive disclosure:

1. `./skills/SUMMARY.md` — knowledge base overview
2. `./skills/index.md` — find relevant skills
3. Open only the specific skill file you need

Suggested skills likely relevant to RankSentinel:

- `./skills/domains/marketing/seo/seo-audit.md`
- `./skills/domains/infrastructure/observability-patterns.md`
- `./skills/domains/backend/api-design-patterns.md`

## Blocked knowledge rule (project-local)

If you are blocked by missing knowledge (API quirks, PSI parsing, Mailgun edge cases, cron/VPS specifics):

1. Create a project-local doc: `docs/SKILL_REQUEST_<topic>.md`
   - Context
   - What is needed
   - Constraints (no stealth scraping, respect robots, no secrets in logs)
   - Examples
   - Acceptance criteria
2. Mark the current task as blocked (`[?]`) with a clear **If Blocked** note pointing to the doc.
3. Continue with the next safe task if possible.

## Core operating rules

- Default to safe behavior: respect robots rules, no anti-bot bypassing.
- Avoid alert spam: prefer severity scoring and normalization.
- Jobs must be idempotent and safe to rerun.
- Never commit secrets (`MAILGUN_API_KEY`, `PSI_API_KEY`, etc.).

## Project structure

- Application code lives at project root (e.g., `src/`, `pyproject.toml`).
- Ralph loop infra lives in `workers/ralph/`.
- The primary task list lives in `workers/IMPLEMENTATION_PLAN.md` (website).
- The backend/app plan is archived at `workers/PLAN_MAIN.md`.
