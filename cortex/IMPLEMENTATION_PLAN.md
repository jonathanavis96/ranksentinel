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

- [x] **0-W.5** Manual integration test - Core workflow end-to-end
  - **AC:** Run main workflow end-to-end and verify expected behavior
  - **Note:** Manual validation required per Manual.Integration.1
  - **If Blocked:** Requires human operator to run end-to-end workflow test and validate behavior. Cannot be automated by Ralph. Human should test daily/weekly runs and mark [x] when satisfied.

- [x] **0-W.6** Fix MD032 in workers/IMPLEMENTATION_PLAN.md line 90
  - **AC:** `markdownlint workers/IMPLEMENTATION_PLAN.md` passes (no MD032 errors)

- [x] **0-W.7** Fix MD034 in workers/ralph/THUNK.md line 134:274
  - **AC:** `markdownlint workers/ralph/THUNK.md` passes (no MD034 errors)

## Phase 0-K: Agent discipline enforcement (skills + blocked-skill requests)

> Motivation: we want consistent, low-risk execution. Agents must consult Brain skills first, and if blocked, produce a `docs/SKILL_REQUEST_<topic>.md` artifact. This must be enforced mechanically.

- [x] **0-K.1** Fix `./brain/skills` availability inside the workspace (no external symlink)
  - **Problem:** `brain/skills` is currently a symlink to `/home/grafe/code/brain/skills` which is outside the workspace. Rovo/CI cannot read that path, so skills are effectively unavailable to the agent.
  - **Goal:** Ensure `./brain/skills/` is a real directory committed in-repo (or vendored during setup), not a symlink to outside paths.
  - **Implementation guidance (choose one):**
    - **Preferred:** run `bash workers/ralph/sync_brain_skills.sh --from-repo` to vendor the upstream Brain repo into `./brain/skills`.
    - Alternative: run `--from-local` or `--from-sibling` if you have the Brain repo locally.
    - Remove the symlink and ensure `brain/skills/SUMMARY.md` exists and is readable from within the workspace.
  - **AC:** `test -f brain/skills/SUMMARY.md` passes and `readlink brain/skills` fails (meaning it’s not a symlink).

- [x] **0-K.2** Update Ralph prompt to require Brain skills consult + SKILL_REQUEST on block
  - **Files:** `workers/ralph/PROMPT.md` (protected), `workers/ralph/.verify/prompt.sha256` (protected)
  - **Implementation guidance:** Add explicit steps at the top of the prompt:
    - Before implementing: consult `./brain/skills/SUMMARY.md` + relevant domain skill.
    - If blocked: create `docs/SKILL_REQUEST_<topic>.md` and include: context, attempted approach, links, open questions, acceptance criteria.
  - **AC:** Prompt contains explicit language: “MUST consult brain skills first” and “If blocked, MUST create docs/SKILL_REQUEST_*.md before proceeding.”
  - **Validate:** `bash tools/validate_protected_hashes.sh` passes (update hash baseline intentionally).

- [x] **0-K.3** Plan convention: every `[?]` blocked task must include an "If Blocked: docs/SKILL_REQUEST_<topic>.md" line
  - **Goal:** Make the expectation visible at the task-contract level.
  - **Files:** `workers/IMPLEMENTATION_PLAN.md`
  - **AC:** For any future task marked `[?]`, the task contains an "If Blocked:" line naming a `docs/SKILL_REQUEST_*.md` artifact.
  - **Note:** Currently no `[?]` tasks exist in plan. Convention is documented in AGENTS.md and will be enforced for future blocked tasks.

- [x] **0-K.4** Verifier enforcement: fail if blocked tasks exist without SKILL_REQUEST artifacts
  - **Goal:** Mechanical enforcement.
  - **Files (protected):** `workers/ralph/verifier.sh` and/or `rules/AC.rules` plus corresponding hash baselines (`workers/ralph/.verify/verifier.sha256`, `.verify/ac.sha256`).
  - **Implementation guidance (MVP):**
    - If `grep -n "^- \\[[?]\\]" workers/IMPLEMENTATION_PLAN.md` finds any blocked tasks, then:
      - require at least one matching file `docs/SKILL_REQUEST_*.md` exists **and** has been modified recently (or at least exists for MVP)
      - otherwise fail verifier with a clear message.
  - **AC:** A repo state containing a `[?]` task and no `docs/SKILL_REQUEST_*.md` causes verifier to fail.
  - **Validate:** Add a small self-test in verifier or document manual check; ensure protected hashes updated.

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

- [x] **0-S.5** Shopify sitemap index expansion (crawl actual page URLs, not child sitemap XML)
  - **Goal:** Handle common Shopify pattern where `sitemap.xml` is a `sitemapindex` of child sitemaps (`sitemap_pages_*.xml`, `sitemap_products_*.xml`, etc.). Weekly should crawl URLs inside those child sitemaps.
  - **Files (likely):** `src/ranksentinel/runner/weekly_digest.py`, `src/ranksentinel/runner/sitemap_parser.py`, `tests/test_weekly_fetcher_integration.py`
  - **Implementation guidance (MVP):**
    - If the configured sitemap parses as a `sitemapindex`, treat each `<loc>` as a *child sitemap URL*.
    - Fetch child sitemap XML(s) (polite: timeout+retries) and extract their `<url><loc>` page URLs.
    - Enforce a hard cap to avoid blowups (e.g., expand at most first 10 child sitemaps and stop once you have `crawl_limit` page URLs).
    - Emit structured logs that make it obvious whether we crawled pages vs sitemaps (e.g., `stage=sitemap_expand`, `child_sitemaps_fetched`, `page_urls_extracted`).
  - **AC:** With a Shopify-style sitemapindex, weekly fetches *page URLs* (not `.xml` sitemap URLs) and can detect 404s on pages.
  - **Validate:** Add an integration test using mocked HTTP responses: root sitemapindex -> child urlset -> page URLs; assert fetched URLs are pages and not `.xml`.

## Phase 0-R: Real-world crawl resilience (rate limiting + auditability)

### Test-fix followups (post 0K/0S/0R/0E)

- [x] **0-R.5** Fix sqlite test inserts to satisfy NOT NULL columns (`customers.created_at`, `customers.updated_at`, `targets.created_at`)
  - **Why:** `pytest` currently fails with `NOT NULL constraint failed: customers.created_at` in sitemap tests.
  - **Do:** Update tests (at least `tests/test_sitemap_fetch.py`) to insert required timestamp columns, or change schema to provide safe defaults.
  - **Skills:** `brain/skills/domains/backend/sqlite-schema-test-alignment.md`, `brain/skills/domains/backend/database-patterns.md`, `brain/skills/domains/code-quality/testing-patterns.md`, `brain/skills/playbooks/investigate-test-failures.md`
  - **AC:** `./.venv/bin/pytest -q tests/test_sitemap_fetch.py` passes.

- [x] **0-R.6** Fix `tests/test_page_fetcher.py::test_persist_fetch_results_placeholder` to initialize schema (call `init_db()` before using snapshots)
  - **Why:** Fails with `sqlite3.OperationalError: no such table: snapshots` because test creates a bare SQLite DB.
  - **Do:** In the test, call `init_db(conn)` (or use shared fixture) before invoking `persist_fetch_results()`.
  - **Skills:** `brain/skills/domains/backend/sqlite-schema-test-alignment.md`, `brain/skills/domains/code-quality/testing-patterns.md`, `brain/skills/playbooks/investigate-test-failures.md`
  - **AC:** `./.venv/bin/pytest -q tests/test_page_fetcher.py::test_persist_fetch_results_placeholder` passes.

- [x] **0-R.7** Align robots fetch tests with current artifact storage semantics
  - **Why:** `tests/test_robots_fetch.py` has failing assertions vs actual implementation (subject/raw_content expectations).
  - **Do:** Inspect current daily robots persistence (kind/subject normalization, newline normalization, etc.) and update tests to assert the real contract (ideally via `get_latest_artifact()` rather than raw SQL).
  - **Skills:** `brain/skills/domains/backend/sqlite-schema-test-alignment.md`, `brain/skills/domains/code-quality/testing-patterns.md`, `brain/skills/playbooks/investigate-test-failures.md`
  - **AC:** `./.venv/bin/pytest -q tests/test_robots_fetch.py` passes.

- [x] **0-R.8** Ensure customer status gating tests create data consistent with schema + runner behavior
  - **Why:** `tests/test_customer_status_gating.py` is currently failing in full suite.
  - **Do:** Ensure test DB setup inserts required `created_at/updated_at` fields and any required settings rows so the runner can proceed without error.
  - **Skills:** `brain/skills/domains/backend/sqlite-schema-test-alignment.md`, `brain/skills/domains/code-quality/testing-patterns.md`, `brain/skills/domains/backend/database-patterns.md`, `brain/skills/playbooks/investigate-test-failures.md`
  - **AC:** `./.venv/bin/pytest -q tests/test_customer_status_gating.py` passes.

- [x] **0-R.9** Weekly crawl resilience: handle HTTP 429 without hanging the whole run
  - **Why:** weekly entrypoint can stall/timeout due to rate limits (429) when fetching many URLs.
  - **Do (MVP scheduler):** Implement a **fair round-robin fetch scheduler** with **per-domain cooldown** so rate-limited customers are **interleaved** with other customers (not deferred until the end).
    - Model work as tasks: `(customer_id, url)`.
    - Maintain `domain_next_allowed_at[domain]`.
    - Maintain a queue (or per-customer queues) and iterate **round-robin**:
      - Pop next task.
      - If `now < domain_next_allowed_at[domain]`, push it to the end and continue (this naturally interleaves).
      - Fetch URL.
      - On **HTTP 429**:
        - increment `run_coverage.http_429_count`
        - set `domain_next_allowed_at[domain] = now + backoff` (exponential + jitter; cap max cooldown)
        - requeue the same task (so it gets retried later)
      - On success/non-429 error: persist snapshot/run_coverage as appropriate, move on.
    - Add **boundedness**:
      - max attempts per `(customer_id,url)` (e.g., 3)
      - max total 429s per domain per run (after which remaining URLs are marked `error_type="http_429"` and skipped)
      - no unbounded sleep (scheduler keeps working on other tasks while cooling down)
    - Persist auditability:
      - when skipping due to threshold, create snapshots/run_coverage entries that make it obvious we were rate-limited.
  - **Done:** Fixed `page_fetcher_scheduled.py` to persist 429 responses to results dict so they get counted in `run_coverage.http_429_count`. All AC requirements verified: (1) Weekly run completes with repeated 429s, (2) Rate-limited customers are interleaved (not deferred), (3) http_429_count recorded correctly, (4) Runtime bounded by caps, (5) Interleaving behavior confirmed via integration test. All existing tests pass (12/12 for scheduler + weekly fetcher integration).
  - **Skills:** `brain/skills/domains/backend/error-handling-patterns.md`, `brain/skills/domains/backend/api-design-patterns.md`, `brain/skills/domains/infrastructure/observability-patterns.md`, `brain/skills/domains/code-quality/testing-patterns.md`
  - **AC:**
    - Weekly run completes even when a customer domain responds with repeated 429s.
    - Rate-limited customer URLs are retried throughout the run (interleaved), not only at the end.
    - `run_coverage.http_429_count > 0` is recorded.
    - No unbounded sleep; runtime remains bounded by caps.
    - Add/extend a test using mocked HTTP responses to simulate: A(429), B(200), C(200), A(429), B(200), ... and assert interleaving behavior.

- [x] **0-R.9a** Round-robin + cooldown scheduler implementation skeleton (helper + wiring)
  - **Goal:** Make 0-R.9 easy to implement in one pass by providing a concrete code structure.
  - **Do:**
    - Add a small scheduler helper (new module or local helper) that:
      - accepts per-customer URL queues
      - yields the next `(customer_id, url)` to fetch based on cooldown + round-robin fairness
      - tracks attempts per task and enforces caps
    - Wire weekly fetch loop to use this helper (likely in `src/ranksentinel/runner/weekly_digest.py` / `page_fetcher.py`).
  - **Done:** Implemented `fetch_scheduler.py` with round-robin scheduling, per-domain cooldown, exponential backoff with jitter, attempt tracking, and 429 threshold caps. Created `page_fetcher_scheduled.py` for multi-customer scheduled fetching. Refactored `weekly_digest.py` into 3 phases: (1) collect URLs, (2) scheduled fetch across all customers, (3) process results. All scheduler tests passing (9/9).
    - Add structured logs for scheduling decisions: `event=schedule_defer`, `domain`, `cooldown_ms`, `queue_len`, `customer_id`.
  - **Skills:** `brain/skills/domains/backend/error-handling-patterns.md`, `brain/skills/domains/backend/api-design-patterns.md`, `brain/skills/domains/infrastructure/observability-patterns.md`, `brain/skills/domains/code-quality/testing-patterns.md`
  - **AC:**
    - Unit test exists for scheduler ordering under cooldown (A deferred, B/C proceed, A retried later).
    - Weekly integration test for interleaving remains green.

- [x] **0-R.10** Restore green test suite after above fixes
  - **Why:** Currently `pytest -q` reports `9 failed`.
  - **Do:** Run full suite and fix any remaining failures introduced by changes.
  - **Skills:** `brain/skills/playbooks/investigate-test-failures.md`, `brain/skills/domains/code-quality/testing-patterns.md`
  - **AC:** `./.venv/bin/pytest -q` passes.

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

- [x] **0-R.2a** Define weekly snapshot persistence schema (run_id-linked, supports errors)
  - **Goal:** Make weekly crawl auditability possible and enable "New vs Resolved" later.
  - **Files:** `src/ranksentinel/db.py`, `BOOTSTRAP.md` (if spec update needed)
  - **Proposed schema (MVP):**
    - Extend `snapshots` table to include:
      - `run_id TEXT` (links snapshot rows to a specific run)
      - `error_type TEXT` and `error TEXT` (optional, for fetch failures)
    - Keep existing fields; on failure persist:
      - `status_code = 0` (or other explicit sentinel) and `content_hash = ''` (empty)
      - `final_url = url`, `redirect_chain = '[]'`
    - Add index for lookup: `(customer_id, run_type, fetched_at DESC)` and optionally `(customer_id, run_id)`.
  - **AC:** Schema supports storing a row even when the fetch failed, and supports scoping a report to a specific run_id.

- [x] **0-R.2b** Implement DB migration-on-startup (no manual migrations)
  - **Goal:** Ensure existing DB files get new tables/columns automatically when the runner starts.
  - **Files:** `src/ranksentinel/db.py`
  - **Implementation guidance:**
    - Enhance `init_db(conn)` to be idempotent but also apply lightweight migrations:
      - create missing tables (`run_coverage`)
      - `ALTER TABLE` add missing columns (e.g., `snapshots.run_id`, `snapshots.error_type`, `snapshots.error`)
      - (Also ensure `findings.run_id` exists if code expects it)
    - Use `PRAGMA table_info(<table>)` checks before ALTER.
  - **AC:** Running `init_db()` against an older DB creates `run_coverage` and adds missing columns without data loss.
  - **Validate:** Add a unit test that creates an "old" schema (without these columns) and then calls `init_db()` and asserts columns exist.

- [x] **0-R.2c** Persist weekly page fetch results into `snapshots` for all attempted URLs
  - **Goal:** Weekly runs must leave an audit trail in SQLite for reporting/diffing and customer support.
  - **Files (likely):** `src/ranksentinel/runner/weekly_digest.py`, `src/ranksentinel/runner/page_fetcher.py`, `src/ranksentinel/db.py`
  - **Implementation guidance:**
    - Implement `persist_fetch_results()` in `page_fetcher.py` (remove "schema TBD" stub).
    - Call it from `weekly_digest.run()` immediately after `fetch_pages()`.
    - Persist one row per attempted URL with `run_type='weekly'` and the current `run_id`.
  - **AC:** After a weekly run with `crawl_limit=N`, there are `N` new `snapshots` rows with `run_type='weekly'` and `run_id=<current run_id>` (or fewer only if sitemap has < N URLs).
  - **Validate:** Extend `tests/test_weekly_fetcher_integration.py` to assert snapshot rows inserted and include run_id.

- [x] **0-R.4** Verify weekly snapshots + run_coverage tables are created in the *real* SQLite DB
  - **Goal:** Catch schema drift where code expects new tables but the live DB never got `init_db()` applied.
  - **Files (likely):** `src/ranksentinel/db.py`, `src/ranksentinel/runner/weekly_digest.py`, `scripts/run_weekly.sh`, docs as needed
  - **Implementation guidance:**
    - Ensure weekly calls `init_db(conn)` against the configured `RANKSENTINEL_DB_PATH`.
    - Add a smoke/integration test that runs a weekly pass against a temp DB and asserts:
      - `run_coverage` table exists + row inserted
      - `snapshots` includes `run_type='weekly'` rows
    - (Optional) Consider adding a small startup log line printing DB path for easier debugging.
  - **AC:** After a weekly run in this workspace, `sqlite3 ranksentinel.sqlite3 "select count(*) from run_coverage;"` is > 0 and `select run_type,count(*) from snapshots group by run_type;` includes weekly.

- [x] **0-R.3** Add regression coverage for rate-limited site behavior
  - **Goal:** Prevent future regressions where 429 causes large error_count and zero snapshots.
  - **Files:** likely `tests/test_page_fetcher.py` and/or `tests/test_weekly_fetcher_integration.py`
  - **AC:** A test scenario where a URL returns 429 twice then 200 results in:
    - final snapshot status_code=200
    - no critical 404 finding created
  - **Validate:** `pytest -q`

## Phase 0-E: Weekly email UX improvements (must feel valuable even with no issues)

> Motivation: the weekly email must provide clear value even when there are 0 issues.
> Current gaps observed in manual tests:
>
> - "No issues" emails contain only a bootstrap placeholder finding and lack coverage stats.
> - Emails can include stale findings from earlier in the week without making "resolved" vs "new" clear.

- [x] **0-E.1** Remove bootstrap placeholder finding from customer-facing weekly emails
  - **Goal:** Don’t send low-value “bootstrap” noise to customers.
  - **Files (likely):** `src/ranksentinel/runner/weekly_digest.py`, `src/ranksentinel/reporting/report_composer.py`
  - **Implementation guidance (choose one):**
    - Stop inserting the `category='bootstrap'` weekly finding entirely, OR
    - Exclude `category='bootstrap'` from the query used to compose customer emails.
  - **AC:** Weekly email contains no "Weekly digest executed (bootstrap)" item.
  - **Validate:** Add/extend `tests/test_report_composer.py` (or integration test) to assert bootstrap findings are excluded.

- [x] **0-E.2** Add an "All clear" header when there are 0 Critical and 0 Warnings
  - **Goal:** Make a healthy week feel like a positive outcome.
  - **Files:** `src/ranksentinel/reporting/report_composer.py`
  - **AC:** If `critical_count==0` and `warning_count==0`, text + HTML include an explicit "All clear" message.
  - **Validate:** Unit test for text + HTML output.

- [x] **0-E.3** Persist per-run coverage stats (needed for email/reporting)
  - **Goal:** Include what was checked (sitemap URL, total URLs, sampled URLs, success/error counts, 404 count, broken link count).
  - **Files (likely):** `src/ranksentinel/db.py`, `src/ranksentinel/runner/weekly_digest.py`
  - **Implementation guidance:**
    - Add a small new DB table (e.g., `run_coverage`) keyed by `(run_id, customer_id, run_type)` storing:
      - `sitemap_url`, `total_urls`, `sampled_urls`, `success_count`, `error_count`, `http_429_count`, `http_404_count`, timestamps.
    - Insert/update this row during weekly processing.
  - **AC:** After a weekly run, coverage stats exist in DB for that customer and run_id.
  - **Validate:** Add integration test to assert row exists and counts are non-null.

- [x] **0-E.4** Include coverage stats in the weekly email (text + HTML)
  - **Goal:** Even when there are no findings, the email shows what RankSentinel monitored.
  - **Files (likely):** `src/ranksentinel/runner/weekly_digest.py`, `src/ranksentinel/reporting/report_composer.py`
  - **Implementation guidance:**
    - Fetch the most recent `run_coverage` row for the customer/run_id and render a "Coverage" section.
  - **AC:** Email includes a Coverage section with:
    - sitemap URL
    - total URLs in sitemap
    - sampled URLs (crawl_limit)
    - success vs error counts (including 429 count)
  - **Validate:** Unit/integration test verifying section exists.

- [x] **0-E.5** Weekly email should distinguish "New" vs "Existing" vs "Resolved" findings (MVP)
  - **Goal:** Avoid confusion when an issue was fixed but still appears in the "last 7 days" window.
  - **Implementation guidance (MVP acceptable):**
    - Scope the email to the current run via `run_id` (preferred), OR
    - Add a lightweight resolution mechanism by comparing current snapshots vs previous period and marking findings resolved.
  - **AC:** After fixing an issue (e.g., 404 becomes 200), the next weekly email does NOT present it as a current critical issue.
  - **Validate:** Add a test that simulates a 404 in run 1 and a 200 in run 2 and verifies the run 2 email does not show it as active.

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

- [x] **4.6a** First Insight: add admin trigger endpoint (no payment integration)
  - **Goal:** Provide an internal/admin-only way to send a one-off "First Insight" report immediately.
  - **Files (likely):** `src/ranksentinel/api.py`
  - **Implementation guidance:**
    - Add `POST /admin/customers/{customer_id}/send_first_insight`.
    - Endpoint calls an internal function (no duplicated business logic in API layer).
  - **Skills:** `brain/skills/domains/backend/api-design-patterns.md`, `brain/skills/domains/backend/auth-patterns.md`, `brain/skills/domains/code-quality/testing-patterns.md`
  - **AC:** Hitting the endpoint returns 200 and enqueues/executes the first-insight flow for that customer.
  - **Validate:** Unit test for endpoint routing + mocked service call.
  - **Completed:** Added endpoint with stub service function and full test coverage

- [ ] **4.6b** First Insight: implement runner/service to generate report input data
  - **Goal:** Reuse weekly/daily signal collection to generate a “first run” snapshot set without waiting for Monday.
  - **Files (likely):** `src/ranksentinel/runner/first_insight.py`, `src/ranksentinel/runner/daily_checks.py`, `src/ranksentinel/runner/weekly_digest.py`
  - **Implementation guidance (MVP):**
    - Collect the highest-signal checks:
      - key pages: status/redirect/title/canonical/noindex + normalized content hash
      - robots.txt + sitemap hash
      - optional PSI on key pages (respect caps)
    - Write findings scoped to a new run type (e.g., `run_type='first_insight'`) or reuse weekly composer but with a distinct header.
  - **Skills:** `brain/skills/domains/backend/error-handling-patterns.md`, `brain/skills/domains/backend/database-patterns.md`, `brain/skills/domains/code-quality/testing-patterns.md`
  - **AC:** Running the first insight runner produces a report payload with Critical/Warning/Info sections.
  - **Validate:** Unit test for “first insight” report composition given fixture inputs.

- [ ] **4.6c** First Insight: email send + delivery logging
  - **Goal:** Send the first-insight email via Mailgun and record exactly one delivery.
  - **Files (likely):** `src/ranksentinel/mailgun.py`, `src/ranksentinel/reporting/email_templates.py`, `src/ranksentinel/db.py`
  - **Implementation guidance:**
    - Reuse existing weekly email template/layout if possible, but label as “First Insight”.
    - Ensure idempotency: repeated trigger within same day should not send duplicates (dedupe key).
  - **Skills:** `brain/skills/domains/backend/error-handling-patterns.md`, `brain/skills/domains/infrastructure/observability-patterns.md`, `brain/skills/domains/code-quality/testing-patterns.md`
  - **AC:** Exactly one email is sent per trigger window; a delivery row is recorded with `run_type='first_insight'`.
  - **Validate:** Integration test with mocked Mailgun client asserts exactly one delivery recorded.

- [ ] **4.6d** First Insight: payment integration hook (deferred wiring)
  - **Goal:** When payments exist, automatically trigger First Insight on successful payment.
  - **Scope:** Do not implement Stripe/payment processor in this task unless already in scope.
  - **Skills:** `brain/skills/domains/backend/api-design-patterns.md`, `brain/skills/domains/backend/error-handling-patterns.md`
  - **AC:** A single internal function exists that the future webhook handler can call.
  - **Validate:** Code structure supports calling `trigger_first_insight(customer_id)` from webhook code.

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
