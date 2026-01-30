# Validation Criteria — RankSentinel

Last verified: 2026-01-28 23:40:00

## Purpose

Quality gates and acceptance criteria for RankSentinel.

This file is used by Ralph (and humans) to confirm that changes satisfy:

- the operational spec in `BOOTSTRAP.md`
- the project goals in `workers/ralph/THOUGHTS.md`
- autonomous operation requirements (cron + idempotency + low-noise alerts)

## 1) Structure validation

- [ ] `BOOTSTRAP.md` exists and matches MVP scope (daily critical + weekly digest)
- [ ] `docs/SAMPLE_REPORT.md` exists and uses Critical/Warning/Info sections
- [ ] `docs/RUNBOOK_VPS.md` exists and includes crontab examples
- [ ] Source code is in project root `src/` (not under `workers/ralph/`)
- [ ] `pyproject.toml` exists and defines runtime deps
- [ ] `.env.example` exists and includes Mailgun + PSI + Stripe webhook secret placeholders
- [ ] `workers/IMPLEMENTATION_PLAN.md` exists and is the prioritized task list
- [ ] `workers/ralph/THOUGHTS.md` describes goals/non-goals and references `BOOTSTRAP.md`

## 2) Functional validation (bootstrap-level)

Bootstrap is valid when the minimal skeleton runs:

- [ ] Admin API starts locally (`uvicorn ranksentinel.api:app`)
- [ ] `/health` returns `{ "status": "ok" }`
- [ ] Admin onboarding endpoints work:
  - [ ] Create customer
  - [ ] Add targets
  - [ ] Patch settings
- [ ] Daily job entrypoint runs without crashing (even if it only records bootstrap findings)
- [ ] Weekly job entrypoint runs without crashing (even if it only records bootstrap findings)

## 3) Operational validation

- [ ] Jobs are safe to re-run (idempotency planned, no runaway duplication)
- [ ] Retry/backoff exists for transient network calls (v1 uses 3 attempts)
- [ ] Failures are visible via logs; operator email is optional and must not leak secrets
- [ ] No risky behaviors are introduced (no stealth scraping by default)

## 4) Documentation validation

- [ ] `README.md` includes local quickstart and points to `BOOTSTRAP.md`
- [ ] `BOOTSTRAP.md` includes:
  - schedule defaults
  - severity model
  - normalization rules
  - schema outline
  - cron examples
  - onboarding semantics
- [ ] `workers/ralph/AGENTS.md` includes:
  - mandatory read order
  - project-local SKILL_REQUEST behavior

## Validation commands

Run from repo root.

```bash
# Show key docs
ls -la BOOTSTRAP.md docs/SAMPLE_REPORT.md docs/RUNBOOK_VPS.md

# Python env + install
python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install -e ".[dev]"

# Start API
bash scripts/run_local.sh &

# Health check
curl -s http://127.0.0.1:8000/health | cat

# Run jobs
bash scripts/run_daily.sh
bash scripts/run_weekly.sh

# Ralph verifier (repo meta)
bash workers/ralph/verifier.sh
```
