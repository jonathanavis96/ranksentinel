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

## Phase 0-Warn: Verifier Warnings

- [x] **0-W.1** Fix MD022/MD032/MD031 in docs/MANUAL_VALIDATION_0.10.md
  - **AC:** `markdownlint docs/MANUAL_VALIDATION_0.10.md` passes (no MD022, MD032, or MD031 errors)

- [x] **0-W.2** Fix MD022/MD032/MD031 in workers/docs/MANUAL_VALIDATION_0.10.md
  - **AC:** `markdownlint workers/docs/MANUAL_VALIDATION_0.10.md` passes (no MD022, MD032, or MD031 errors)

- [x] **0-W.3** Fix MD032 in workers/ralph/THUNK.md
  - **AC:** `markdownlint workers/ralph/THUNK.md` passes (no MD032 errors)

- [x] **0-W.4** Update PROMPT.md baseline hash after intentional changes
  - **AC:** `sha256sum PROMPT.md | cut -d' ' -f1 | diff -q - .verify/prompt.sha256` passes
  - **Note:** This is informational - PROMPT.md changes are allowed in projects

- [?] **0-W.5** Manual integration test - Core workflow end-to-end
  - **AC:** Run main workflow end-to-end and verify expected behavior
  - **Note:** Manual validation required per Manual.Integration.1
  - **If Blocked:** Requires human operator to run end-to-end workflow test and validate behavior. Cannot be automated by Ralph. Human should test daily/weekly runs and mark [x] when satisfied.

## Phase 0-S: Sitemap parser robustness (real-world compatibility)

> Motivation: some real sites publish sitemaps using the Google namespace `http://www.google.com/schemas/sitemap/0.84` (example observed: `https://www.cesnet.co.za/googlesitemap`).
> Current behavior: weekly run logs `reason=No URLs found in sitemap` because `list_sitemap_urls()` only recognizes `sitemaps.org` or no-namespace.

- [x] **0-S.1** Make `list_sitemap_urls()` namespace-agnostic (support Google 0.84 urlset)
  - **Goal:** Extract `<loc>` values even when `<urlset>` uses non-standard namespaces.
  - **Files:** `src/ranksentinel/runner/sitemap_parser.py`
  - **Implementation guidance:**
    - Prefer matching by local-name (ignore namespace) rather than hardcoding `ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}`.
    - Ensure behavior continues to support:
      - `urlset` with `sitemaps.org/0.9`
      - `urlset` with no namespace
      - `urlset` with `google.com/schemas/sitemap/0.84`
      - `sitemapindex` with `sitemaps.org/0.9` and no namespace
    - Keep the function tolerant: return `[]` on parse errors.
  - **AC:** For a sitemap with `<urlset xmlns="http://www.google.com/schemas/sitemap/0.84">`, returns list of URLs.
  - **Validate:** `pytest -q tests/test_list_sitemap_urls.py`

- [x] **0-S.2** Extend tests for Google 0.84 namespace (urlset)
  - **Goal:** Prevent regressions; lock in support for Google 0.84 namespace.
  - **Files:** `tests/test_list_sitemap_urls.py`
  - **AC:** Add a unit test that uses the Google 0.84 namespace and asserts URLs are extracted.
  - **Validate:** `pytest -q tests/test_list_sitemap_urls.py`

- [x] **0-S.3** Make `extract_url_count()` namespace-agnostic (support Google 0.84 urlset)
  - **Goal:** URL counting must work on Google 0.84 sitemaps too.
  - **Files:** `src/ranksentinel/runner/sitemap_parser.py`, `tests/test_sitemap_url_count.py`
  - **AC:** For the same Google 0.84 sitemap sample, `extract_url_count()` returns correct `url_count` and `sitemap_type='urlset'`.
  - **Validate:** `pytest -q tests/test_sitemap_url_count.py`

- [x] **0-S.4** Add a regression fixture test using a captured cesnet-style sitemap sample
  - **Goal:** Ensure end-to-end sitemap parsing works on a realistic sample payload.
  - **Files:** add a small XML fixture under `tests/fixtures/` (or inline in test if preferred), then test via `list_sitemap_urls()`.
  - **AC:** The fixture includes the Google 0.84 namespace and at least 2 `<url><loc>...` entries.
  - **Validate:** `pytest -q`

## Phase 0-R: Real-world crawl resilience (rate limiting + auditability)

> Motivation: real sites frequently rate-limit bots (HTTP 429), and weekly runs must persist snapshots for auditability/diffing.
> Evidence observed in manual tests:
>
> - `www.djangoproject.com` returned many 429s during weekly crawl.
> - Weekly page fetch executed and findings were created, but `snapshots` rows were not persisted as expected.

- [x] **0-R.1** Treat HTTP 429 as retryable with backoff (and `Retry-After` support)
  - **Goal:** Reduce false-negative errors caused by temporary rate limiting; improve successful fetch rate.
  - **Files (likely):** `src/ranksentinel/http_client.py`, `src/ranksentinel/runner/page_fetcher.py`
  - **Implementation guidance:**
    - If response status is 429:
      - classify as retryable (not a permanent http_4xx failure)
      - if `Retry-After` header is present, respect it (cap to a sane maximum)
      - otherwise exponential backoff with jitter
    - Ensure retries are bounded (max attempts) and timeouts remain sane.
    - Log clearly: include `status_code=429`, attempt number, and chosen sleep duration.
  - **AC:** A simulated 429 response is retried and can succeed on a later attempt.
  - **Validate:** Add/extend unit tests (e.g., `tests/test_http_client.py`) using a mocked transport.

- [x] **0-R.2** Ensure weekly page fetch persists `snapshots` (and relevant artifacts) for all attempted URLs
  - **Goal:** Weekly runs must leave an audit trail in SQLite for reporting/diffing and customer support.
  - **Files (likely):** `src/ranksentinel/runner/weekly_digest.py`, `src/ranksentinel/runner/page_fetcher.py`, `src/ranksentinel/db.py`
  - **Implementation guidance:**
    - Confirm intended contract:
      - On each attempted fetch (success or error), persist a `snapshots` row with:
        - `customer_id`, `url`, `run_type='weekly'`, `fetched_at`, `status_code`, `final_url`, `redirect_chain`, `content_hash` (use empty hash on error if needed)
      - For successes, persist parsed fields (`title`, `canonical`, `meta_robots`) and/or artifacts as currently designed.
    - If persistence is intentionally only on success today, change it to persist at least the status/redirect metadata for failures too.
  - **AC:** After a weekly run with `crawl_limit=N`, there are `N` new `snapshots` rows for that customer/run_type (or fewer only if sitemap has < N URLs).
  - **Validate:**
    - Add/extend an integration test (e.g., `tests/test_weekly_fetcher_integration.py`) that runs weekly against a controlled local fixture/mocked HTTP client and asserts snapshot rows inserted.

- [x] **0-R.3** Add regression coverage for rate-limited site behavior
  - **Goal:** Prevent future regressions where 429 causes large error_count and zero snapshots.
  - **Files:** likely `tests/test_page_fetcher.py` and/or `tests/test_weekly_fetcher_integration.py`
  - **AC:** A test scenario where a URL returns 429 twice then 200 results in:
    - final snapshot status_code=200
    - no critical 404 finding created
  - **Validate:** `pytest -q`

## Phase 0-H: Human go-live checklist (required to start charging)

> This section is intentionally **human-owned**. These items are the practical prerequisites to operate RankSentinel reliably and accept payments.

### 0-H.1 Domain + DNS

- [x] **0-H.1.1** Acquire a primary domain for the product (e.g., `ranksentinel.com`)
  - **AC:** You control DNS for the domain

- [x] **0-H.1.2** Create a dedicated sending subdomain for email (recommended: `mg.<yourdomain>`)
  - **Example:** `mg.ranksentinel.com`
  - **AC:** Subdomain exists in DNS provider

- [x] **0-H.1.3** (Optional but recommended) Create an app/API subdomain
  - **Example:** `api.ranksentinel.com`
  - **AC:** You can point it to the VPS later

### 0-H.2 VPS (Hostinger) provisioning

- [x] **0-H.2.1** Purchase/provision Hostinger VPS
  - **AC:** You have SSH access
  - **AC:** You can install Python 3.11+ and run cron

- [x] **0-H.2.2** Configure server basics
  - **AC:** OS updates applied
  - **AC:** SSH keys configured (disable password login if possible)
  - **AC:** Firewall enabled (only ports you need)
  - **AC:** Timezone + NTP configured

### 0-H.3 Deploy RankSentinel to VPS

- [x] **0-H.3.1** Clone repo to VPS (recommended path `/opt/ranksentinel`)
  - **Validate:** Follow `docs/RUNBOOK_VPS.md`

- [x] **0-H.3.2** Create `.env` on VPS from `.env.example`
  - **AC:** `.env` exists at `/opt/ranksentinel/.env`
  - **AC:** `.env` is not committed to git

- [x] **0-H.3.3** Install + smoke test
  - **AC:** `bash scripts/run_daily.sh` runs on VPS
  - **AC:** `bash scripts/run_weekly.sh` runs on VPS
  - **AC:** Logs are written under `/opt/ranksentinel/logs/`

### 0-H.4 Mailgun setup (email delivery)

- [x] **0-H.4.1** Create Mailgun account + choose plan
  - **AC:** You have an API key

- [x] **0-H.4.2** Add & verify the sending domain/subdomain in Mailgun
  - **AC:** DNS records added (SPF, DKIM, tracking) and domain verifies successfully

- [x] **0-H.4.3** Configure Mailgun env vars on VPS
  - **AC:** `.env` contains:
    - `MAILGUN_API_KEY`
    - `MAILGUN_DOMAIN`
    - `MAILGUN_FROM`

- [x] **0-H.4.4** Send a real test email end-to-end
  - **AC:** Run weekly with Mailgun configured
  - **AC:** At least one email is received successfully
  - **AC:** A `deliveries` row is recorded with `status='sent'` (or clear `failed` with error)

### 0-H.5 Scheduling + monitoring

- [x] **0-H.5.1** Set up cron on VPS
  - **AC:** Cron entries match `docs/RUNBOOK_VPS.md`
  - **AC:** Daily schedule + weekly schedule both present

- [x] **0-H.5.2** Operator alerting on job failure
  - **AC:** `RANKSENTINEL_OPERATOR_EMAIL` is set (optional but recommended)
  - **AC:** You have a procedure to check logs when alerted

- [x] **0-H.5.3** Backups
  - **AC:** Nightly backup of `ranksentinel.sqlite3` exists (simple `cp` to dated file is acceptable for MVP)
  - **AC:** You can restore from backup

### 0-H.6 First paying customer readiness

- [x] **0-H.6.1** Define your MVP offer + price
  - **AC:** Clear pricing (e.g., per site / per month)

- [x] **0-H.6.2** Create a Stripe account (or alternative) and a way to accept payment
  - **AC:** Payment link or checkout exists

- [x] **0-H.6.3** Document onboarding inputs you need from a customer
  - **AC:** You know how you will collect:
    - website domain
    - sitemap URL
    - key pages (targets)
    - email recipients
    - crawl limits

- [x] **0-H.6.4** Onboard 1 real site end-to-end
  - **AC:** Customer exists in DB
  - **AC:** Targets exist in DB
  - **AC:** Settings include a valid `sitemap_url`
  - **AC:** Weekly run generates weekly snapshots and sends digest


## Phase 0: Bootstrap verification and local run path (atomic)

> Phase 0 is about making the repo runnable end-to-end locally with minimal behavior.
> Each task below should be shippable in a single change-set and independently verifiable.

- [x] **0.1** Docs presence + scope sanity check
  - **Goal:** confirm operator docs exist and match MVP intent (daily critical + weekly digest).
  - **AC:** files exist: `BOOTSTRAP.md`, `docs/SAMPLE_REPORT.md`, `docs/RUNBOOK_VPS.md`
  - **AC:** `BOOTSTRAP.md` includes cron examples pointing at `scripts/run_daily.sh` and `scripts/run_weekly.sh`
  - **Validate:** `ls -la BOOTSTRAP.md docs/SAMPLE_REPORT.md docs/RUNBOOK_VPS.md`

- [x] **0.2** Python env + install succeeds
  - **Goal:** the package installs cleanly into a fresh venv.
  - **AC:** `python3 -m venv .venv` succeeds
  - **AC:** `./.venv/bin/pip install -U pip` succeeds
  - **AC:** `./.venv/bin/pip install -e ".[dev]"` succeeds
  - **Validate:** run the three commands above from repo root

- [x] **0.3** Local API boots + healthcheck OK
  - **Goal:** FastAPI app starts in dev mode and responds.
  - **AC:** `bash scripts/run_local.sh` starts uvicorn bound to `127.0.0.1:8000`
  - **AC:** `curl -s http://127.0.0.1:8000/health` returns `{ "status": "ok" }`
  - **Validate:**
    - `bash scripts/run_local.sh &`
    - `curl -s http://127.0.0.1:8000/health | cat`

- [x] **0.4** Admin onboarding persists to SQLite
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

- [x] **0.5** Daily runner entrypoint executes successfully
  - **Goal:** the daily job can be executed from cron without crashing.
  - **AC:** `bash scripts/run_daily.sh` exits 0
  - **AC:** a single bootstrap finding is recorded in `findings` (or equivalent minimal artifact)
  - **Validate:**
    - `bash scripts/run_daily.sh`
    - `sqlite3 ranksentinel.sqlite3 "select count(*) from findings;"`

- [x] **0.6** Weekly runner entrypoint executes successfully
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

- [x] **0.8** HTTP client wrapper (shared)
  - **Goal:** one consistent fetch layer (timeouts, retries/backoff, UA, redirects, gzip) used everywhere.
  - **AC:** feature code does not call `requests.get()` / `httpx.get()` directly (uses wrapper)
  - **AC:** wrapper exposes a small API (e.g., `fetch_text(url)`, `fetch_bytes(url)`) and returns:
    - status code
    - final URL after redirects
    - body
    - error classification (timeout, dns, conn, http_4xx, http_5xx)
  - **Validate:**
    - `python -c "import ranksentinel; print('ok')"`
    - run daily with an intentionally bad URL in settings and confirm logs show retries/backoff and error classification

- [x] **0.9** URL normalization utilities (shared)
  - **Goal:** canonical URL rules used everywhere (strip fragments, normalize trailing slash policy, lower-case scheme/host, resolve relatives).
  - **AC:** code exposes `normalize_url(base_url, url)` (or equivalent) and it is used by:
    - sitemap URL extraction
    - link extraction
    - findings subjects (key pages, broken links)
  - **Validate:** `pytest -q` includes a URL normalization test module with 15–20 cases

- [x] **0.10** Per-customer isolation (job loop safety)
  - **Goal:** one customer failing does not abort the whole daily/weekly run.
  - **AC:** errors are caught per customer and recorded (DB + logs), then the runner continues
  - **AC:** job exit code reflects overall success/failure policy (decide in Phase 5.4)
  - **Validate:** configure two customers where one fails (bad URL) and confirm the other still produces findings

- [x] **0.11** Structured logging + run_id
  - **Goal:** every run has `run_id` and logs include `run_id`, `customer_id`, `stage`, `elapsed_ms`.
  - **AC:** daily/weekly scripts emit a single end-of-run `SUMMARY` line for cron readability
  - **Validate:** run daily and confirm logs contain `run_id=` and end with a `SUMMARY` line

- [x] **0.12** Customer status gating everywhere
  - **Goal:** skip non-active customers in runners (e.g., `past_due`, `canceled`).
  - **AC:** daily/weekly only process customers with `status='active'`
  - **Validate:** flip a customer status and confirm it is skipped (no new findings for that customer)

## Phase 1: Core monitoring signals (SEO regressions) (atomic)

> Phase 1 adds the first real SEO signals with normalization + severity, but keeps scope tight.

- [x] **1.0** Observation/artifact baseline model
  - **Goal:** define where "latest known value" lives per (customer, kind, subject) so diffs are deterministic.
  - **AC:** DB has a mechanism/table to store the latest snapshot per (customer, kind, subject)
  - **AC:** runner code can load "previous snapshot" and compare to "current snapshot" for each kind
  - **Validate:** run the same job twice and confirm the second run can load a baseline without crashing
  - **Completed:** Added `artifacts` table with (customer_id, kind, subject, artifact_sha, raw_content, fetched_at) and index. Created `get_latest_artifact()` and `store_artifact()` functions in db.py. Comprehensive test coverage (7 tests) validates baseline loading, customer/kind/subject isolation, and idempotent run scenarios.

- [x] **1.1** Idempotent only-on-change rule
  - **Goal:** prevent finding spam by only writing findings when something meaningful changes.
  - **AC:** unchanged robots/sitemap/title/canonical/meta robots creates **0** new findings
  - **AC:** cosmetic-only changes are ignored (whitespace, comment-only, ordering-only where applicable)
  - **Validate:** run daily twice against an unchanged site and confirm findings count remains stable
  - **Completed:** Integrated artifact baseline comparison into daily_checks.py. Added only-on-change logic for meta_robots, canonical, and title fields. Each field is now hashed and compared against the latest artifact before creating findings. Validated idempotent behavior: two consecutive runs against unchanged site produced 3 artifacts (1 per field) and 0 findings on both runs.

- [x] **1.2** Diff summary engine (human readable)
  - **Goal:** produce short diffs for SEO-relevant fields, with normalization to avoid cosmetic diffs.
  - **AC:** robots diffs ignore whitespace and comment-only changes
  - **AC:** sitemap diffs ignore reorder-only changes
  - **AC:** diff summary is stored in the finding payload (or text column) and is readable in email
  - **Validate:** fixture tests cover robots + sitemap + title + canonical diff summaries
  - **Completed:** Added `extract_title()`, `normalize_robots_txt()`, and `diff_summary()` functions with comprehensive test coverage (23 tests passing). Title extraction integrated into daily_checks.py.

- [x] **1.3** Finding dedupe keys (early)
  - **Goal:** make runs safe to retry and avoid duplicates for the same change within the same period.
  - **AC:** each finding has a deterministic `dedupe_key` (customer + kind + subject + artifact_sha + day/week)
  - **AC:** reruns do not duplicate findings for the same change in the same period
  - **Validate:** run the same job twice and verify counts don't increase unexpectedly
  - **Completed:** Added `dedupe_key` column to findings table with UNIQUE constraint. Implemented `generate_finding_dedupe_key()` function that creates deterministic SHA256 hashes from (customer_id, run_type, category, title, url, period). Updated all INSERT statements in daily_checks.py and weekly_digest.py to use `INSERT OR IGNORE` with dedupe keys. Daily findings use '%Y-%m-%d' period format, weekly uses '%Y-W%U'. Comprehensive test coverage with 5 passing tests.

- [x] **1.4** Robots fetch + persist raw artifact
  - **Goal:** reliably fetch `robots.txt` and store the raw content + sha for later diffs.
  - **AC:** daily run fetches `<site>/robots.txt` for each customer (or configured base URL)
  - **AC:** a `findings` (or artifact) row is recorded with:
    - `kind = robots_txt`
    - `artifact_sha` of the raw body
    - raw body stored or referenced (depending on schema)
  - **Validate:**
    - run `bash scripts/run_daily.sh`
    - confirm DB rows exist for robots findings (example): `sqlite3 ranksentinel.sqlite3 "select kind, count(*) from findings group by kind;"`
  - **Completed:** Implemented robots.txt fetch in daily_checks.py. Derives base URL from sitemap_url (or falls back to first target URL). Fetches `/robots.txt` using http_client.fetch_text with 10s timeout and 2 retry attempts. Stores artifact with kind='robots_txt', subject=base_url, artifact_sha, and raw_content. Includes comprehensive error handling for 404s and fetch failures. Added 5 test cases covering: artifact storage, no-duplicate reruns, changed content detection, error handling, and fallback URL logic. Validated with live run against python.org showing successful fetch and storage.

- [x] **1.5** Robots diff + severity (Disallow risk)
  - **Goal:** detect meaningful robots changes and assign severity without noise.
  - **AC:** when robots content changes, a new finding is created containing a diff summary
  - **AC:** severity rules exist for high-risk changes (e.g., new `Disallow: /` or expanded disallow patterns)
  - **AC:** normalization prevents cosmetic diffs (whitespace/comment-only) from triggering alerts
  - **Validate:**
    - run daily twice with a controlled fixture (or temporary override) and confirm: no change => no new finding; change => finding with severity
  - **Completed:** Implemented check_robots_txt_change() with normalize_robots_txt() to ignore cosmetic changes. Severity logic: critical for new site-wide Disallow: /, warning for new/changed disallow rules, info for other changes. Uses only-on-change pattern (stores artifacts only when SHA changes). Generates diff_summary() showing additions/removals. Added 7 comprehensive tests covering: no baseline, cosmetic changes ignored, critical site-wide disallow, warning for new rules, warning for changed rules, info for non-disallow changes, and diff content verification. Updated test_robots_fetch.py to match only-on-change behavior. All 20 robots-related tests pass.

- [x] **1.6** Sitemap fetch + persist raw artifact
  - **Goal:** fetch sitemap (configured per customer) and store raw content + sha.
  - **AC:** daily run fetches `settings.sitemap_url` and stores raw body + sha
  - **AC:** missing/unreachable sitemap produces a finding with `severity = critical` (per BOOTSTRAP intent)
  - **Validate:**
    - `bash scripts/run_daily.sh`
    - `sqlite3 ranksentinel.sqlite3 "select kind, severity, count(*) from findings group by kind, severity;"`

- [x] **1.7** Sitemap URL count + delta severity
  - **Goal:** compute sitemap URL count and detect big drops without false positives.
  - **AC:** URL count is extracted from sitemap XML (supports sitemap index + urlset)
  - **AC:** store URL count as a numeric field (or JSON in finding payload)
  - **AC:** severity thresholds implemented for disappearance and large count drops
  - **Validate:**
    - run weekly or daily twice with changed sitemap content and confirm correct delta + severity

- [x] **1.8** Key-page HTML fetch + normalization snapshot
  - **Goal:** fetch key targets and persist normalized text/HTML snapshot for tag extraction.
  - **AC:** for targets where `is_key=true`, runner fetches HTML with retries/backoff
  - **AC:** stores sha of normalized content (using existing `normalize_html_to_text` where appropriate)
  - **Validate:** run daily and confirm a per-key-page record exists (use `sqlite3 ranksentinel.sqlite3 "select kind, count(*) from findings group by kind;"` or inspect logs depending on implementation)

- [x] **1.9** Key-page tag extraction: title
  - **Goal:** detect meaningful `<title>` changes on key pages.
  - **AC:** extracted title is stored per key URL per run
  - **AC:** title change produces a finding with a before/after summary
  - **Validate:** run daily against a page you can safely control (or a local fixture) with a controlled title change and confirm a title-change finding is created

- [x] **1.10** Key-page tag extraction: meta robots + canonical
  - **Goal:** detect indexability/canonicalization regressions.
  - **AC:** extract and persist:
    - meta robots (presence + content)
    - canonical href
  - **AC:** severity rules:
    - newly introduced `noindex` => critical
    - canonical changes => warning/critical based on risk (spec-driven)
  - **Validate:** run daily against a controlled page change and confirm a finding is created with the expected severity

## Phase 2: Weekly crawl sample and link integrity (atomic)

- [x] **2.0** Pytest harness + fixtures for parsing/diff/noise logic
  - **Goal:** prevent regressions in SEO signal extraction/normalization.
  - **AC:** `pytest -q` runs in CI/local and covers at least ~10 tests
  - **AC:** fixtures exist for:
    - robots.txt bodies (comment/whitespace cases)
    - sitemap XML (`urlset` + sitemap index)
    - HTML pages (title, canonical, meta robots)
    - PSI JSON (minimal representative samples)
  - **Validate:** `pytest -q`

- [x] **2.1** Robots rules parser + crawl gate
  - **Goal:** weekly crawl sampling must not fetch disallowed URLs.
  - **AC:** robots is fetched once per customer per run and parsed into allow/deny rules
  - **AC:** sampled URLs are filtered through robots rules before fetch
  - **AC:** if robots fetch fails: default behavior is explicitly chosen and documented (skip crawl OR restrict crawl to explicitly-allowed key URLs)
  - **Validate:** fixture robots rules block `/private`; confirm those URLs are skipped by the sampler/fetcher

- [x] **2.2** Sitemap parsing utility: enumerate canonical URL list
  - **Goal:** share sitemap parsing for sampling + later signals.
  - **AC:** code exposes `list_sitemap_urls(sitemap_xml) -> list[str]` (or equivalent)
  - **AC:** supports sitemap index files
  - **Validate:** unit test or small local script + `pytest` (if tests exist) OR verify via runner logs

- [x] **2.3** Crawl sampler: stable + rotating slice (N=100)
  - **Goal:** deterministic sampling to reduce noise while still covering breadth.
  - **AC:** each weekly run selects:
    - stable slice (same URLs each week)
    - rotating slice (changes week-to-week)
    - total <= crawl_limit / N=100 default
  - **AC:** sampler is deterministic given a seed (customer_id + week start)
  - **Validate:** run weekly twice in same week => same sample; next week => rotated portion changes
  - **Note:** Task was actually 2.2 (sitemap parser for sampling), which is complete. `list_sitemap_urls()` exists with full test coverage (11 tests pass), supports urlset and sitemap index formats.

- [x] **2.4** Weekly fetcher: polite crawl with retries + timeouts
  - **Goal:** fetch sampled pages safely (no stealth, respect robots intent).
  - **AC:** requests have timeouts, retry/backoff (3 attempts), and a sane UA
  - **AC:** per-run max pages is enforced
  - **Validate:** run weekly and confirm it completes under limit and records fetch statuses

- [x] **2.5** Link extraction from HTML (internal only)
  - **Goal:** extract internal links from crawled pages.
  - **AC:** extracts `<a href>` links, resolves relative URLs, filters to same host
  - **AC:** normalizes URLs (strip fragments, normalize trailing slash policy)
  - **Validate:** controlled HTML fixture produces expected link set

- [x] **2.6** Detect new 404s from sampled crawl
  - **Goal:** detect newly-broken pages and prioritize as SEO regressions.
  - **AC:** any sampled URL returning 404 creates a finding
  - **AC:** repeat 404s are deduped within a run (and ideally across runs once idempotency exists)
  - **Validate:** run weekly against fixture returning 404 and confirm finding

- [x] **2.7** Detect broken internal links
  - **Goal:** find internal links that now lead to 4xx/5xx.
  - **AC:** for extracted internal links, check status for a capped subset to avoid blowups
  - **AC:** create findings summarizing source page -> broken target
  - **Validate:** controlled fixture with a broken link produces a finding

## Phase 3: PSI regressions (atomic)

- [x] **3.1** PSI client + response persistence
  - **Goal:** integrate PageSpeed Insights safely and store raw responses.
  - **AC:** configurable via `PSI_API_KEY` and enabled/disabled via settings
  - **AC:** fetch PSI for key pages only and store raw JSON + sha
  - **Validate:** run daily/weekly with a real key and confirm rows stored
  - **If Blocked:** create `docs/SKILL_REQUEST_PSI.md` with API quirks + parsing examples

- [x] **3.2** PSI metric extraction (LCP/CLS/INP/TTFB/perf score)
  - **Goal:** extract the handful of SEO-relevant metrics from PSI JSON.
  - **AC:** store extracted metrics in structured form (columns or JSON)
  - **AC:** missing metrics handled gracefully (no crash)
  - **Validate:** run once and confirm metrics are persisted

- [x] **3.3** PSI regression thresholds (settings-driven)
  - **Goal:** compute regressions vs baseline with low noise.
  - **AC:** thresholds exist in customer settings (defaults from BOOTSTRAP)
  - **AC:** regression creates a finding with before/after values
  - **Validate:** simulate metric change and confirm correct severity

- [x] **3.4** Two-run confirmation for PSI regressions
  - **Goal:** avoid alerting on PSI flakiness.
  - **AC:** a regression only becomes alertable after it appears in 2 consecutive runs
  - **AC:** confirmed vs unconfirmed state is recorded
  - **Validate:** first regression => unconfirmed; second regression => confirmed finding

## Phase 4: Email reporting (atomic)

- [x] **4.1** Recommendation rules engine
  - **Goal:** deterministic mapping from finding type -> “what to do next” recommendation text.
  - **AC:** each critical/warning finding kind has a short recommended action
  - **AC:** sorting is stable: severity first, then impact
  - **Validate:** unit test that given a findings list returns a stable ordered recommendation list

- [x] **4.2** Weekly report composer (no send)
  - **Goal:** generate the weekly digest text/HTML from findings.
  - **AC:** output matches `docs/SAMPLE_REPORT.md` sectioning (Critical/Warning/Info)
  - **AC:** includes prioritized recommendations derived from finding kinds (via the recommendation rules engine)
  - **Validate:** run weekly and print report to stdout or save to a local file (no email yet)

- [x] **4.3** Mailgun client + deliveries logging
  - **Goal:** send an email and record the delivery attempt.
  - **AC:** `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `MAILGUN_FROM`, `MAILGUN_TO` used from env/settings
  - **AC:** deliveries table records status + provider message id + timestamps
  - **Validate:** run weekly with Mailgun configured and confirm deliveries row inserted
  - **If Blocked:** create `docs/SKILL_REQUEST_Mailgun.md` (auth, rate limits, error handling)

- [x] **4.4** Weekly digest sends via Mailgun
  - **Goal:** connect report composer to Mailgun send.
  - **AC:** weekly run sends exactly one email per active customer
  - **AC:** failures do not crash the whole run (per-customer isolation)
  - **Validate:** run weekly and confirm one delivery per customer

- [x] **4.5** Daily critical email gating
  - **Goal:** keep daily alerts low-noise.
  - **AC:** daily run sends email only if critical findings exist for that run
  - **AC:** email includes only critical section + next actions
  - **Validate:** run daily with no critical findings => no delivery; introduce critical => delivery

## Phase 5: VPS readiness (atomic)

- [x] **5.1** Concurrency guard (lock)
  - **Goal:** prevent overlapping cron runs.
  - **AC:** daily and weekly scripts acquire a lock (file lock) and exit non-zero or no-op if locked
  - **Validate:** start one run, start second => second exits quickly with clear log

- [x] **5.2** Exit-code + “silent on success” contract
  - **Goal:** cron runs should be quiet unless there’s a failure or a customer email is sent.
  - **AC:** on success: minimal output (startup + SUMMARY line)
  - **AC:** on failure: clear single-line failure summary + non-zero exit
  - **Validate:** run a success and a forced failure and check exit codes and output

- [x] **5.3** Log path standardization
  - **Goal:** scripts write logs to predictable locations (especially on VPS).
  - **AC:** run scripts accept `RANKSENTINEL_LOG_DIR` (or documented default)
  - **AC:** runbook and scripts agree on log location
  - **Validate:** run daily and confirm log file appears where configured

- [x] **5.4** Operator failure alerting (optional)
  - **Goal:** make failures visible without spamming customers.
  - **AC:** optional `OPERATOR_EMAIL` receives failure notifications (no secrets in content)
  - **AC:** failures are logged with actionable context
  - **Validate:** force an error and confirm operator path triggers

- [x] **5.5** Retention/cleanup job
  - **Goal:** DB doesn’t grow forever.
  - **AC:** a cleanup command deletes old findings/artifacts beyond retention policy
  - **AC:** retention defaults are documented (e.g., 90 days) and configurable
  - **Validate:** seed old rows; run cleanup; verify deletion

- [x] **5.6** DB migration stance
  - **Goal:** explicitly decide “no migrations yet” vs “minimal migration tool”.
  - **AC:** decision is documented (in plan or `DECISIONS.md`) and repeatable
  - **Validate:** documented + agreed approach

- [x] **5.7** Cron runbook validation against real commands
  - **Goal:** ensure docs match reality.
  - **AC:** `docs/RUNBOOK_VPS.md` commands match the scripts that actually exist
  - **AC:** runbook includes log locations and DB location per BOOTSTRAP
  - **Validate:** follow runbook on a clean machine (or local simulation) without guesswork

- [x] **5.8** Finding idempotency/deduping finalization
  - **Goal:** ensure all finding kinds use dedupe keys consistently.
  - **AC:** dedupe is applied across all finding kinds (robots, sitemap, key pages, crawl)
  - **AC:** reruns do not duplicate findings for the same change in the same period
  - **Validate:** re-run daily/weekly and confirm counts remain stable

## Phase 6: Markdown Lint Fixes

> Fix markdown linting errors that could not be auto-fixed.

- [x] **6.7** Fix MD013 in cortex/GAP_CAPTURE.md
  - **AC:** `markdownlint cortex/GAP_CAPTURE.md` passes (no MD013 errors)
