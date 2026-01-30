# RankSentinel — BOOTSTRAP (Operational Spec)

This document is the source of truth for RankSentinel’s MVP scope, job semantics, severity model, normalization rules, storage model, and VPS runbook.

RankSentinel is an autonomous SaaS:

- VPS cron runs jobs
- SQLite stores configuration + run history + findings
- Mailgun delivers emails
- PageSpeed Insights (PSI) provides performance metrics (key URLs only)

## 1) Product definition

RankSentinel sends automated reports:

- **Weekly digest (default):** “what changed / what broke / what regressed / what to do first”
- **Daily critical checks (default):** only high-severity issues (low-noise)

### Differentiation

This is **not** generic page change monitoring. RankSentinel focuses on SEO regressions and indexability risk:

- `robots.txt` changes
- sitemap changes (hash + URL count delta)
- canonical changes
- `noindex` changes
- title changes
- broken internal links + new 404s
- optional PSI regressions on key URLs only (two-run confirmation)

### Non-goals (v1)

- No stealth scraping / anti-bot bypassing by default
- No competitor monitoring
- No visual diffs
- No dashboard UI (email is the MVP UI)
- No Search Console integration (deferred)

## 2) Scheduling defaults

### Daily critical checks

- Frequency: once per day
- Output: send email only when Critical findings exist

### Weekly digest

- Frequency: Monday 09:00 VPS local time
- Output: one structured email per customer

### Weekly crawl parameters

- Crawl budget: N=100 URLs from sitemap per customer
- Always include:
  - all configured key URLs
  - a stable deterministic sample
  - a rotating deterministic slice (changes weekly)

### PSI strategy

- PSI runs on **key URLs only**.
- Starter default: 3–5 key URLs.
- Regression alerts require two-run confirmation:
  - first run beyond threshold => “suspected regression”
  - second consecutive run beyond threshold => “confirmed regression”

## 3) Configuration contract

Secrets must never be committed.

### Environment variables

Core:

- `RANKSENTINEL_DB_PATH` (default `./ranksentinel.sqlite3`)
- `RANKSENTINEL_BASE_URL` (optional; for links in emails)
- `RANKSENTINEL_OPERATOR_EMAIL` (optional; send operator failures)

Mailgun:

- `MAILGUN_API_KEY`
- `MAILGUN_DOMAIN`
- `MAILGUN_FROM`

PSI:

- `PSI_API_KEY`

Stripe (scaffold/spec only in v1):

- `STRIPE_WEBHOOK_SECRET`

Safe defaults:

- If Mailgun isn’t configured, jobs should run and log but skip sending.
- If PSI key is missing, performance checks are skipped and recorded as Info.

## 4) Storage (SQLite) — schema outline

SQLite is the initial persistence layer. Jobs must be idempotent.

### Tables

#### `customers`

- `id` (integer primary key)
- `name` (text)
- `status` (enum: `active`, `past_due`, `canceled`)
- `created_at` (ISO timestamp)
- `updated_at` (ISO timestamp)

Cancellation behavior:

- If `status != active`, cron skips all jobs for that customer.
- Optional retention: keep snapshots/findings for 30 days after cancel, then purge.

#### `targets`

- `id`
- `customer_id`
- `url`
- `is_key` (0/1)
- `created_at`

#### `settings`

- `customer_id` (unique)
- `sitemap_url` (nullable)
- `crawl_limit` (default 100)
- `psi_enabled` (0/1)
- `psi_urls_limit` (default 5)
- `psi_confirm_runs` (default 2)
- thresholds:
  - `psi_perf_drop_threshold` (default 10)
  - `psi_lcp_increase_threshold_ms` (default 500)

#### `snapshots`

Per-URL snapshots for diffing and auditability.

- `customer_id`, `url`, `run_type`, `run_id`, `fetched_at`
- status, final URL, redirect chain
- title, canonical, meta robots
- normalized text hash
- `error_type`, `error` (optional, for fetch failures)
  - On fetch failure: `status_code=0`, `content_hash=''`, `error_type` and `error` populated
  - Enables weekly run auditability and "New vs Resolved" diffing

#### `artifacts` (planned)

Global artifacts like robots.txt and sitemap.

- `artifact_type`: `robots` or `sitemap`
- `sha256`
- textual content (capped)
- metadata json (e.g., sitemap url_count)

#### `psi_results` (planned)

- perf score
- LCP, CLS, INP
- raw json (optional)

#### `findings`

- `run_type`: `daily` or `weekly`
- `severity`: `critical`, `warning`, `info`
- `category`: `indexability`, `crawlability`, `links`, `content`, `performance`
- `title`, `details_md`, optional `url`

#### `deliveries`

- run metadata for sent/skipped/failed emails

## 5) Severity model

### Critical (alert immediately)

- Key page becomes `noindex`
- Canonical disappears or points off-domain unexpectedly
- `robots.txt` introduces new Disallow affecting key paths
- Sitemap disappears or URL count drops drastically
- Spike in 5xx/4xx on key pages
- Confirmed PSI regression beyond threshold on key pages

### Warning (weekly digest)

- Title changed on key pages
- Redirect target changed
- Increase in duplicate titles (crawl sample)
- Broken internal links increased

### Info (context)

- Non-critical content changes on monitored pages
- PSI improved
- Minor sitemap churn

## 6) Noise prevention (normalization rules)

Goal: “more signal, less noise”.

v1 normalization strategy for content hashing:

- Parse HTML
- Remove: `script`, `style`, `noscript`
- Remove: `nav`, `header`, `footer` when present
- Remove likely cookie/consent banners (id/class contains `cookie`, `consent`, `gdpr`)
- Normalize whitespace
- Normalize obvious timestamps into tokens

v1.1 can add per-site ignore selectors.

## 7) Job semantics (idempotency + retry)

### Idempotency

Jobs must be safe to re-run:

- a daily run for (customer, date) must not create duplicate findings
- dedupe findings by (customer_id, run_type, category, title, url, date)

### Retry/backoff

Transient failures:

- retry up to 3 attempts with exponential backoff (1s, 2s, 4s)

### Operator failure visibility

On repeated job failure:

- write clear logs
- optional operator email to `RANKSENTINEL_OPERATOR_EMAIL`

## 8) Cron schedules (Hostinger VPS)

Example crontab:

```bash
# Daily checks (01:15)
15 1 * * * /bin/bash /opt/ranksentinel/scripts/run_daily.sh >> /opt/ranksentinel/cron_daily.log 2>&1

# Weekly digest (Monday 09:00)
0 9 * * 1 /bin/bash /opt/ranksentinel/scripts/run_weekly.sh >> /opt/ranksentinel/cron_weekly.log 2>&1
```

## 9) Onboarding (FastAPI admin endpoint)

v1 onboarding is a tiny admin endpoint that writes to SQLite:

- create customer (status active)
- add targets (key URLs)
- set sitemap URL and crawl limit

Stripe integration plan (scaffold/spec only):

- webhook updates `customers.status` (`active`, `past_due`, `canceled`)

## 10) Agent workflow requirements

Dedicated Cortex + Ralph exist inside this repo.

Ralph must read these first each iteration:

1. `BOOTSTRAP.md`
2. `workers/ralph/THOUGHTS.md`
3. `workers/ralph/VALIDATION_CRITERIA.md`

### Blocked knowledge rule (project-local)

If blocked by missing knowledge:

1. Create a project-local doc: `docs/SKILL_REQUEST_<topic>.md`
   - include: context, what is needed, constraints, examples, acceptance criteria
2. Mark the task blocked with an “If Blocked” note pointing to that doc
3. The intention is to later upstream a generalized skill into the Brain repo

## 11) Runbook

See `docs/RUNBOOK_VPS.md`.
