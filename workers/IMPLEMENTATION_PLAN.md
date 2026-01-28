# Implementation Plan — RankSentinel

Last updated: 2026-01-28 23:40:00

## Current state summary

Bootstrap repo generated via Brain `scripts/new-project.sh`.

- Core docs exist: `BOOTSTRAP.md`, `docs/SAMPLE_REPORT.md`, `docs/RUNBOOK_VPS.md`
- Minimal Python skeleton exists under `src/`:
  - FastAPI admin endpoints (customer/targets/settings)
  - SQLite schema init for customers/targets/settings/findings/deliveries
  - Daily/weekly runner stubs

## Goal

Ship an autonomous SEO regression monitor (daily critical checks + weekly digest) with:

- low-noise alerts
- actionable recommendations
- VPS cron deployment
- Mailgun email delivery
- PSI regressions on key URLs (two-run confirmation)

<!-- Cortex adds new Task Contracts below this line -->

## Prioritized tasks

### Phase 0 — Bootstrap verification and local run path (atomic)

> Phase 0 is about making the repo runnable end-to-end locally with minimal behavior.
> Each task below should be shippable in a single change-set and independently verifiable.

- [ ] **0.1** Docs presence + scope sanity check
  - **Goal:** confirm operator docs exist and match MVP intent (daily critical + weekly digest).
  - **AC:** files exist: `BOOTSTRAP.md`, `docs/SAMPLE_REPORT.md`, `docs/RUNBOOK_VPS.md`
  - **AC:** `BOOTSTRAP.md` includes cron examples pointing at `scripts/run_daily.sh` and `scripts/run_weekly.sh`
  - **Validate:** `ls -la BOOTSTRAP.md docs/SAMPLE_REPORT.md docs/RUNBOOK_VPS.md`

- [ ] **0.2** Python env + install succeeds
  - **Goal:** the package installs cleanly into a fresh venv.
  - **AC:** `python3 -m venv .venv` succeeds
  - **AC:** `./.venv/bin/pip install -U pip` succeeds
  - **AC:** `./.venv/bin/pip install -e ".[dev]"` succeeds
  - **Validate:** run the three commands above from repo root

- [ ] **0.3** Local API boots + healthcheck OK
  - **Goal:** FastAPI app starts in dev mode and responds.
  - **AC:** `bash scripts/run_local.sh` starts uvicorn bound to `127.0.0.1:8000`
  - **AC:** `curl -s http://127.0.0.1:8000/health` returns `{ "status": "ok" }`
  - **Validate:**
    - `bash scripts/run_local.sh &`
    - `curl -s http://127.0.0.1:8000/health | cat`

- [ ] **0.4** Admin onboarding persists to SQLite
  - **Goal:** creating a customer and targets writes to the DB.
  - **AC:** using Swagger UI (or curl), you can:
    - create customer (`POST /admin/customers`)
    - add at least 1 target (`POST /admin/customers/{customer_id}/targets`)
  - **AC:** `ranksentinel.sqlite3` exists after onboarding
  - **AC:** DB contains at least 1 row in `customers` and `targets`
  - **Validate:**
    - `test -f ranksentinel.sqlite3`
    - `sqlite3 ranksentinel.sqlite3 "select count(*) from customers;"`
    - `sqlite3 ranksentinel.sqlite3 "select count(*) from targets;"`

- [ ] **0.5** Daily runner entrypoint executes successfully
  - **Goal:** the daily job can be executed from cron without crashing.
  - **AC:** `bash scripts/run_daily.sh` exits 0
  - **AC:** a single bootstrap finding is recorded in `findings` (or equivalent minimal artifact)
  - **Validate:**
    - `bash scripts/run_daily.sh`
    - `sqlite3 ranksentinel.sqlite3 "select count(*) from findings;"`

- [ ] **0.6** Weekly runner entrypoint executes successfully
  - **Goal:** the weekly job can be executed from cron without crashing.
  - **AC:** `bash scripts/run_weekly.sh` exits 0
  - **AC:** a single bootstrap finding is recorded in `findings` (or equivalent minimal artifact)
  - **Validate:**
    - `bash scripts/run_weekly.sh`
    - `sqlite3 ranksentinel.sqlite3 "select count(*) from findings;"`

- [x] **0.7** Cron-ready scripts: executable + non-recursive + single source of truth
  - **Goal:** avoid drift/duplication and ensure scripts are safe for cron.
  - **AC:** `scripts/run_daily.sh` and `scripts/run_weekly.sh` are executable (`test -x ...`)
  - **AC:** neither script calls itself (no recursion)
  - **AC:** any wrapper scripts under `bin/` and `workers/bin/` (if kept) delegate to `scripts/` only
  - **Validate:**
    - `test -x scripts/run_daily.sh scripts/run_weekly.sh scripts/run_local.sh`
    - `! grep -n 'bash scripts/run_daily\.sh' scripts/run_daily.sh`
    - `! grep -n 'bash scripts/run_weekly\.sh' scripts/run_weekly.sh`

### Phase 1 — Core monitoring signals (SEO regressions) (atomic)

> Phase 1 adds the first real SEO signals with normalization + severity, but keeps scope tight.

- [ ] **1.1** Robots fetch + persist raw artifact
  - **Goal:** reliably fetch `robots.txt` and store the raw content + sha for later diffs.
  - **AC:** daily run fetches `<site>/robots.txt` for each customer (or configured base URL)
  - **AC:** a `findings` (or artifact) row is recorded with:
    - `kind = robots_txt`
    - `artifact_sha` of the raw body
    - raw body stored or referenced (depending on schema)
  - **Validate:**
    - run `bash scripts/run_daily.sh`
    - confirm DB rows exist for robots findings (example): `sqlite3 ranksentinel.sqlite3 "select kind, count(*) from findings group by kind;"`

- [ ] **1.2** Robots diff + severity (Disallow risk)
  - **Goal:** detect meaningful robots changes and assign severity without noise.
  - **AC:** when robots content changes, a new finding is created containing a diff summary
  - **AC:** severity rules exist for high-risk changes (e.g., new `Disallow: /` or expanded disallow patterns)
  - **AC:** normalization prevents cosmetic diffs (whitespace/comment-only) from triggering alerts
  - **Validate:**
    - run daily twice with a controlled fixture (or temporary override) and confirm: no change => no new finding; change => finding with severity

- [ ] **1.3** Sitemap fetch + persist raw artifact
  - **Goal:** fetch sitemap (configured per customer) and store raw content + sha.
  - **AC:** daily run fetches `settings.sitemap_url` and stores raw body + sha
  - **AC:** missing/unreachable sitemap produces a finding with `severity = critical` (per BOOTSTRAP intent)
  - **Validate:**
    - `bash scripts/run_daily.sh`
    - `sqlite3 ranksentinel.sqlite3 "select kind, severity, count(*) from findings group by kind, severity;"`

- [ ] **1.4** Sitemap URL count + delta severity
  - **Goal:** compute sitemap URL count and detect big drops without false positives.
  - **AC:** URL count is extracted from sitemap XML (supports sitemap index + urlset)
  - **AC:** store URL count as a numeric field (or JSON in finding payload)
  - **AC:** severity thresholds implemented for disappearance and large count drops
  - **Validate:**
    - run weekly or daily twice with changed sitemap content and confirm correct delta + severity

- [ ] **1.5** Key-page HTML fetch + normalization snapshot
  - **Goal:** fetch key targets and persist normalized text/HTML snapshot for tag extraction.
  - **AC:** for targets where `is_key=true`, runner fetches HTML with retries/backoff
  - **AC:** stores sha of normalized content (using existing `normalize_html_to_text` where appropriate)
  - **Validate:** run daily and confirm a per-key-page record exists (use `sqlite3 ranksentinel.sqlite3 "select kind, count(*) from findings group by kind;"` or inspect logs depending on implementation)

- [ ] **1.6** Key-page tag extraction: title
  - **Goal:** detect meaningful `<title>` changes on key pages.
  - **AC:** extracted title is stored per key URL per run
  - **AC:** title change produces a finding with a before/after summary
  - **Validate:** run daily against a page you can safely control (or a local fixture) with a controlled title change and confirm a title-change finding is created

- [x] **1.7** Key-page tag extraction: meta robots + canonical
  - **Goal:** detect indexability/canonicalization regressions.
  - **AC:** extract and persist:
    - meta robots (presence + content)
    - canonical href
  - **AC:** severity rules:
    - newly introduced `noindex` => critical
    - canonical changes => warning/critical based on risk (spec-driven)
  - **Validate:** run daily against a controlled page change and confirm a finding is created with the expected severity

### Phase 2 — Weekly crawl sample and link integrity (atomic)

- [ ] **2.1** Sitemap parsing utility: enumerate canonical URL list
  - **Goal:** share sitemap parsing for sampling + later signals.
  - **AC:** code exposes `list_sitemap_urls(sitemap_xml) -> list[str]` (or equivalent)
  - **AC:** supports sitemap index files
  - **Validate:** unit test or small local script + `pytest` (if tests exist) OR verify via runner logs

- [ ] **2.2** Crawl sampler: stable + rotating slice (N=100)
  - **Goal:** deterministic sampling to reduce noise while still covering breadth.
  - **AC:** each weekly run selects:
    - stable slice (same URLs each week)
    - rotating slice (changes week-to-week)
    - total <= crawl_limit / N=100 default
  - **AC:** sampler is deterministic given a seed (customer_id + week start)
  - **Validate:** run weekly twice in same week => same sample; next week => rotated portion changes

- [ ] **2.3** Weekly fetcher: polite crawl with retries + timeouts
  - **Goal:** fetch sampled pages safely (no stealth, respect robots intent).
  - **AC:** requests have timeouts, retry/backoff (3 attempts), and a sane UA
  - **AC:** per-run max pages is enforced
  - **Validate:** run weekly and confirm it completes under limit and records fetch statuses

- [ ] **2.4** Link extraction from HTML (internal only)
  - **Goal:** extract internal links from crawled pages.
  - **AC:** extracts `<a href>` links, resolves relative URLs, filters to same host
  - **AC:** normalizes URLs (strip fragments, normalize trailing slash policy)
  - **Validate:** controlled HTML fixture produces expected link set

- [ ] **2.5** Detect new 404s from sampled crawl
  - **Goal:** detect newly-broken pages and prioritize as SEO regressions.
  - **AC:** any sampled URL returning 404 creates a finding
  - **AC:** repeat 404s are deduped within a run (and ideally across runs once idempotency exists)
  - **Validate:** run weekly against fixture returning 404 and confirm finding

- [ ] **2.6** Detect broken internal links
  - **Goal:** find internal links that now lead to 4xx/5xx.
  - **AC:** for extracted internal links, check status for a capped subset to avoid blowups
  - **AC:** create findings summarizing source page -> broken target
  - **Validate:** controlled fixture with a broken link produces a finding

### Phase 3 — PSI regressions (atomic)

- [ ] **3.1** PSI client + response persistence
  - **Goal:** integrate PageSpeed Insights safely and store raw responses.
  - **AC:** configurable via `PSI_API_KEY` and enabled/disabled via settings
  - **AC:** fetch PSI for key pages only and store raw JSON + sha
  - **Validate:** run daily/weekly with a real key and confirm rows stored
  - **If Blocked:** create `docs/SKILL_REQUEST_PSI.md` with API quirks + parsing examples

- [ ] **3.2** PSI metric extraction (LCP/CLS/INP/TTFB/perf score)
  - **Goal:** extract the handful of SEO-relevant metrics from PSI JSON.
  - **AC:** store extracted metrics in structured form (columns or JSON)
  - **AC:** missing metrics handled gracefully (no crash)
  - **Validate:** run once and confirm metrics are persisted

- [ ] **3.3** PSI regression thresholds (settings-driven)
  - **Goal:** compute regressions vs baseline with low noise.
  - **AC:** thresholds exist in customer settings (defaults from BOOTSTRAP)
  - **AC:** regression creates a finding with before/after values
  - **Validate:** simulate metric change and confirm correct severity

- [ ] **3.4** Two-run confirmation for PSI regressions
  - **Goal:** avoid alerting on PSI flakiness.
  - **AC:** a regression only becomes alertable after it appears in 2 consecutive runs
  - **AC:** confirmed vs unconfirmed state is recorded
  - **Validate:** first regression => unconfirmed; second regression => confirmed finding

### Phase 4 — Email reporting (atomic)

- [ ] **4.1** Weekly report composer (no send)
  - **Goal:** generate the weekly digest text/HTML from findings.
  - **AC:** output matches `docs/SAMPLE_REPORT.md` sectioning (Critical/Warning/Info)
  - **AC:** includes prioritized recommendations derived from finding kinds
  - **Validate:** run weekly and print report to stdout or save to a local file (no email yet)

- [ ] **4.2** Mailgun client + deliveries logging
  - **Goal:** send an email and record the delivery attempt.
  - **AC:** `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `MAILGUN_FROM`, `MAILGUN_TO` used from env/settings
  - **AC:** deliveries table records status + provider message id + timestamps
  - **Validate:** run weekly with Mailgun configured and confirm deliveries row inserted
  - **If Blocked:** create `docs/SKILL_REQUEST_Mailgun.md` (auth, rate limits, error handling)

- [ ] **4.3** Weekly digest sends via Mailgun
  - **Goal:** connect report composer to Mailgun send.
  - **AC:** weekly run sends exactly one email per active customer
  - **AC:** failures do not crash the whole run (per-customer isolation)
  - **Validate:** run weekly and confirm one delivery per customer

- [ ] **4.4** Daily critical email gating
  - **Goal:** keep daily alerts low-noise.
  - **AC:** daily run sends email only if critical findings exist for that run
  - **AC:** email includes only critical section + next actions
  - **Validate:** run daily with no critical findings => no delivery; introduce critical => delivery

### Phase 5 — VPS readiness (atomic)

- [ ] **5.1** Finding idempotency key + dedupe logic
  - **Goal:** make jobs safe to re-run (cron retries, manual reruns).
  - **AC:** each finding has a deterministic `dedupe_key` (customer + kind + subject + artifact_sha + day/week)
  - **AC:** inserts are idempotent (no duplicate rows on rerun)
  - **Validate:** run the same job twice and verify counts don’t increase unexpectedly

- [ ] **5.2** Concurrency guard (lock)
  - **Goal:** prevent overlapping cron runs.
  - **AC:** daily and weekly scripts acquire a lock (file lock) and exit non-zero or no-op if locked
  - **Validate:** start one run, start second => second exits quickly with clear log

- [ ] **5.3** Operator failure alerting (optional)
  - **Goal:** make failures visible without spamming customers.
  - **AC:** optional `OPERATOR_EMAIL` receives failure notifications (no secrets in content)
  - **AC:** failures are logged with actionable context
  - **Validate:** force an error and confirm operator path triggers

- [ ] **5.4** Cron runbook validation against real commands
  - **Goal:** ensure docs match reality.
  - **AC:** `docs/RUNBOOK_VPS.md` commands match the scripts that actually exist
  - **AC:** runbook includes log locations and DB location per BOOTSTRAP
  - **Validate:** follow runbook on a clean machine (or local simulation) without guesswork

### Phase 6 — Markdown Lint Fixes

> Fix markdown linting errors that could not be auto-fixed.

- [ ] **6.1** Fix MD013 line-length errors in BOOTSTRAP.md
  - **AC:** `markdownlint BOOTSTRAP.md` passes (no MD013 errors)
  - **Files:** BOOTSTRAP.md (4 lines: 3, 16, 21, 239, 242)

- [ ] **6.2** Fix MD013 line-length errors in brain/skills/conventions.md
  - **AC:** `markdownlint brain/skills/conventions.md` passes (no MD013 errors)
  - **Files:** brain/skills/conventions.md (3 lines: 5, 70, 184)

- [ ] **6.3** Fix MD013 line-length errors in documentation-anti-patterns.md
  - **AC:** `markdownlint brain/skills/domains/anti-patterns/documentation-anti-patterns.md` passes (no MD013 errors)
  - **Files:** brain/skills/domains/anti-patterns/documentation-anti-patterns.md (10 lines: 5, 7, 21, 42, 75, 147, 167, 217, 286, 324)

- [ ] **6.4** Fix MD024 duplicate heading errors in documentation-anti-patterns.md
  - **AC:** `markdownlint brain/skills/domains/anti-patterns/documentation-anti-patterns.md` passes (no MD024 errors)
  - **Files:** brain/skills/domains/anti-patterns/documentation-anti-patterns.md (20 duplicate heading instances)
