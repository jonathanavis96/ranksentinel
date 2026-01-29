# Cortex Implementation Plan — RankSentinel

Last Updated: 2026-01-28 22:09:32

## Mission

From `BOOTSTRAP.md`: Ship an autonomous SEO regression monitor (daily critical
checks + weekly digest) with low-noise alerts.

## Relationship to Ralph

Ralph executes work from `workers/IMPLEMENTATION_PLAN.md`.

Cortex uses this file for higher-level planning notes and phase intent. The
source of truth task list is `workers/IMPLEMENTATION_PLAN.md`.

## Strategic phases (summary)

- Phase 0: Local run path + bootstrap verification
- Phase 1: Robots + sitemap + key-page tag extraction
- Phase 2: Weekly crawl sampling + broken internal links / 404s
- Phase 3: PSI integration + two-run confirmation
- Phase 4: Mailgun delivery + report formatting
- Phase 5: VPS cron hardening (idempotency, operator alerts)
