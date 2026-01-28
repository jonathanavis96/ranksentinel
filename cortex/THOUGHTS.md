# Cortex Thoughts — RankSentinel

Last Updated: 2026-01-28 22:09:32

## Current Mission

Bootstrap and ship an autonomous SEO regression monitor:

- weekly digest email
- daily critical checks (low-noise)
- Python + FastAPI + SQLite + Mailgun + PSI
- VPS cron operation (Hostinger)

## Strategic notes

- The product must differentiate from generic change detection by focusing on SEO-specific regressions and actionable recommendations.
- Alert noise prevention is table-stakes; normalization + severity + confirmation is mandatory.
- Keep MVP UI as email; defer dashboards and Slack/webhooks.

## Next planning focus

- Ensure repo scaffolding includes Cortex runtime scripts (`cortex/one-shot.sh`, `cortex/snapshot.sh`, `cortex/cortex.bash`).
- Ensure Ralph always references `BOOTSTRAP.md` and creates `docs/SKILL_REQUEST_<topic>.md` when blocked.
