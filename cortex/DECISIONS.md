# DECISIONS — RankSentinel

Last updated: 2026-01-28 22:09:32

## Active decisions

### DEC-2026-01-28-001: MVP is email-first (no dashboard)

**Decision:** MVP output is a weekly email digest and optional daily critical email alerts.

**Rationale:** Email reduces scope, accelerates time-to-value, and aligns with set-and-forget operations.

### DEC-2026-01-28-002: Use PSI for performance on key URLs only

**Decision:** PageSpeed Insights API runs only for key URLs; regressions require two-run confirmation.

**Rationale:** Keeps costs and noise under control while providing high-value regression signals.
