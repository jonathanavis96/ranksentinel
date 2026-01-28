# THOUGHTS.md — RankSentinel

Catch SEO regressions before traffic drops.

## What this project does

RankSentinel sends automated reports that highlight SEO regressions and high-signal site health issues.

It is designed to be set-and-forget:

- VPS cron runs daily and weekly jobs
- SQLite stores config and findings
- Mailgun sends emails
- PageSpeed Insights (PSI) provides performance metrics for key URLs only

### Primary goal

Provide a weekly email report that answers:

1. What changed?
2. What broke?
3. What regressed?
4. What should we do first?

### Key features (MVP)

- Daily critical checks (low-noise):
  - key page `noindex`
  - canonical drift
  - robots.txt breaking changes
  - sitemap disappearance or large URL-count drop
  - key-page 4xx/5xx spikes
  - confirmed PSI regressions (two-run confirmation)
- Weekly digest:
  - robots.txt + sitemap diffs
  - crawl sample (N=100)
  - new 404 discovery + broken internal links
  - title changes/duplicates (sample)
  - prioritized recommendations

### Target users

- Small SaaS teams without dedicated SEO engineering
- Agencies managing multiple websites
- Content sites where link rot and template changes impact traffic

## Non-goals (v1)

- Generic page diffing as a product category
- Competitor monitoring/scraping
- Stealth anti-bot bypassing
- Full dashboard UI (email first)
- Search Console integration

## Success metrics

- Low noise: users do not ignore alerts
- High signal: reports catch real regressions before business impact
- Autonomous: cron jobs run without operator involvement on success

## Source of truth docs

Ralph must treat these as authoritative:

1. `BOOTSTRAP.md` — operational spec (scope, schedule, schema outline, severity, normalization)
2. `docs/SAMPLE_REPORT.md` — example report format
3. `docs/RUNBOOK_VPS.md` — VPS deployment and cron

## Knowledge gap rule (project-local)

If implementation is blocked by missing knowledge:

1. Create a project-local document: `docs/SKILL_REQUEST_<topic>.md`
   - context
   - what is needed
   - constraints
   - examples
   - acceptance criteria
2. Mark the task as blocked with an "If Blocked" note pointing to the doc

The intention is to later upstream this as a reusable Brain skill.
