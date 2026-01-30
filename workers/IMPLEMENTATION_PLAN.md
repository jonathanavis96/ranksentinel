# Implementation Plan — RankSentinel Website

Last Updated: 2026-01-29 23:10:00

## Execution rules (Ralph)

- Execute **top-to-bottom**.
- In each BUILD iteration, implement **only the first unchecked** item (`- [ ]`) in file order.
- Every item must include:
  - **Goal** (why)
  - **AC** (acceptance criteria; how we know it’s done)
  - **If Blocked** (what to do if dependencies are missing)

## Non-negotiable decisions (do not change without user approval)

- **Frontend stack:** Next.js (App Router) with static export.
- **Hosting:**
  - `ranksentinel.com` (marketing site): GitHub Pages + custom domain.
  - `api.ranksentinel.com` (FastAPI): Hostinger VPS.
- **Design direction:** “Soft SaaS landing” + Palette A (Signal Teal + Ink).

## Phase 0-Warn: Verifier Warnings

- [x] **0.1** Fix MD032 errors in docs/websites/NAV_CTA_SPEC.md
  - **AC:** `markdownlint docs/websites/NAV_CTA_SPEC.md` passes (no MD032 errors)
  - **Completed:** 2026-01-30 - Added blank lines around lists

- [x] **0.2** Fix MD009/no-trailing-spaces in workers/ralph/THUNK.md
  - **AC:** `markdownlint workers/ralph/THUNK.md` passes (no MD009 errors)
  - **Completed:** 2026-01-30 - Removed trailing space from line 199

- [x] **0.2** Fix MD032 errors in website/app/components/README.md
  - **AC:** `markdownlint website/app/components/README.md` passes (no MD032 errors)
  - **Completed:** 2026-01-30 - Added blank lines around lists

- [x] **0.3** Fix markdown errors in website/node_modules/@alloc/quick-lru/readme.md
  - **AC:** `markdownlint website/node_modules/@alloc/quick-lru/readme.md` passes (no MD040, MD014, MD010 errors)
  - **Completed:** 2026-01-30 - Added node_modules to .markdownlintignore (third-party code should not be modified)

- [x] **0.4** Fix markdown errors in website/node_modules/@babel/parser/CHANGELOG.md
  - **AC:** `markdownlint website/node_modules/@babel/parser/CHANGELOG.md` passes (no MD032, MD028, MD034, MD049, MD022, MD004, MD007 errors)
  - **Completed:** 2026-01-30 - Added node_modules to .markdownlintignore (third-party code should not be modified)

  - Source of truth: `docs/websites/10_design_ux.md`.
- **CTA system:** Dual (contextual, one primary CTA per page view).
  - Homepage primary CTA: **Get a sample report** → `POST /public/leads`.
  - Pricing primary CTA: **Start monitoring** → `POST /public/start-monitoring`.
  - Source of truth: `docs/websites/05_copy_system.md`.
- **Trials / paywall:** Provision immediately as `trial`, then paywall after trial ends.
  - Trial ends after **7 days OR 1 weekly digest** (whichever comes first).
  - Post-trial cadence:
    - Weekly paywalled email for **4 weeks**.
    - Then `previously_interested` with **monthly** locked reminder.
  - Payment flips status to `active`.
- **Analytics:** GA4 via GTM with required events.
- **GA4 weekly digest:** Send the **full report** via email (no LLM summarization).
- **Payments:** Paystack checkout links.

## Mandatory references

Project docs:

- `docs/WEBSITE_REQUIREMENTS.md`
- `docs/websites/SUMMARY.md`
- `docs/websites/03_ia_sitemap.md`
- `docs/websites/04_page_requirements.md`
- `docs/websites/05_copy_system.md`
- `docs/websites/06_pricing_packaging.md`
- `docs/websites/10_design_ux.md`
- `docs/websites/11_qa_acceptance.md`
- `docs/websites/12_launch.md`
- `docs/SAMPLE_REPORT.md`
- `BOOTSTRAP.md`

Brain skills (open those relevant to the current item):

- IA/structure:
  - `brain/skills/domains/websites/architecture/sitemap-builder.md`
  - `brain/skills/domains/websites/architecture/section-composer.md`
- Copy:
  - `brain/skills/domains/websites/copywriting/value-proposition.md`
  - `brain/skills/domains/websites/copywriting/cta-optimizer.md`
  - `brain/skills/domains/websites/copywriting/objection-handler.md`
- Design:
  - `brain/skills/domains/websites/design/color-system.md`
  - `brain/skills/domains/websites/design/typography-system.md`
  - `brain/skills/domains/websites/design/spacing-layout.md`
- Frontend quality:
  - `brain/skills/domains/frontend/accessibility-patterns.md`
  - `brain/skills/domains/frontend/react-patterns.md`
- SEO:
  - `brain/skills/domains/marketing/seo/seo-audit.md`

---

## Website build tasks (atomic)

### Phase 0-Lint: Markdown Lint Errors

- [x] **0.1** Fix MD024 in brain_upstream/cortex/PLAN_DONE.md
  - **AC:** `markdownlint brain_upstream/cortex/PLAN_DONE.md` passes (no MD024 errors for "Archived on 2026-01-26")

- [x] **0.2** Fix MD056 table column count errors in brain_upstream/TEMPLATE_DRIFT_REPORT.md
  - **AC:** `markdownlint brain_upstream/TEMPLATE_DRIFT_REPORT.md` passes (no MD056 errors on lines 61, 77, 87)

- [x] **0.3** Fix MD040 in brain_upstream/TEMPLATE_DRIFT_REPORT.md
  - **AC:** `markdownlint brain_upstream/TEMPLATE_DRIFT_REPORT.md` passes (no MD040 errors on line 254)

- [x] **0.4** Fix MD056 table column count errors in brain_upstream/workers/ralph/THUNK.md
  - **AC:** `markdownlint brain_upstream/workers/ralph/THUNK.md` passes (no MD056 errors on lines 829, 839, 841-848)

### Task 1: Planning sanity + IA confirmation

- [x] **1.1** Confirm MVP page list and section blueprint alignment
  - **Goal:** Ensure IA matches the section blueprint and we’re shipping the right pages first.
  - **References:** `docs/websites/03_ia_sitemap.md`, `docs/websites/04_page_requirements.md`, `brain/skills/domains/websites/architecture/sitemap-builder.md`.
  - **AC:**
    - `docs/websites/03_ia_sitemap.md` clearly marks MVP pages vs optional.
    - Any contradictions with `04_page_requirements.md` are resolved and documented.
  - **If Blocked:** Add a short “Open Questions” list to `03_ia_sitemap.md` and proceed with homepage/pricing/sample-report as MVP.

- [x] **1.2** Lock nav labels + destinations + CTA placement rules
  - **Goal:** Make the site consistent and avoid conversion-killing copy drift.
  - **References:** `docs/websites/05_copy_system.md`, `brain/skills/domains/websites/copywriting/cta-optimizer.md`.
  - **AC:**
    - Nav labels and URLs are explicitly listed (header + footer).
    - "One primary CTA per page view" is documented with examples.
  - **If Blocked:** Default to:
    - Links: Product, Pricing, Sample report, FAQ.
    - Buttons: homepage "Get a sample report"; pricing "Start monitoring".
  - **Completed:** Created `docs/websites/NAV_CTA_SPEC.md` with comprehensive navigation and CTA rules.

### Task 2: Frontend scaffold (Next.js static export)

- [x] **2.1** Create Next.js App Router site under `website/` configured for static export
  - **Goal:** Establish the marketing site codebase with reproducible builds.
  - **References:** `brain/skills/domains/frontend/react-patterns.md`.
  - **AC:**
    - `website/` exists and runs locally (`dev`) and builds (`build` + `export` or equivalent).
    - Static output is compatible with GitHub Pages.
  - **If Blocked:** If static export limitations block routing/metadata, document constraints and switch to a compatible static approach (still Next.js-based) with user approval.

- [x] **2.2** Add basic tooling for the website (lint/format/typecheck)
  - **Goal:** Prevent formatting drift and obvious bugs.
  - **AC:**
    - `website/` has scripts: `lint`, `format` (or `fmt`), `typecheck` (if TS).
    - CI-friendly commands exist.
  - **If Blocked:** Implement minimal ESLint + Prettier (or Biome) and document any exceptions.

### Task 3: Design tokens + base components (Palette A)

- [x] **3.1** Implement Palette A tokens (hex) as CSS variables (and/or Tailwind theme)
  - **Goal:** Make design consistent and easy to evolve.
  - **References:** `docs/websites/10_design_ux.md`, `brain/skills/domains/websites/design/color-system.md`.
  - **AC:**
    - Tokens exist for all specified hexes:
      - Core: `#F7FAFC`, `#FFFFFF`, `#E6EDF5`, `#0B1220`, `#445066`
      - Brand: `#0F766E`, `#0B5F59`, `#E6FFFB`
      - Severity: `#B42318`, `#B54708`, `#175CD3`, `#027A48`
      - Hero gradient per doc.
  - **If Blocked:** Use CSS variables only (no Tailwind), but keep naming consistent.

- [x] **3.2** Implement layout primitives (container widths, spacing scale)
  - **Goal:** Create a predictable “soft SaaS” rhythm and readable measure.
  - **References:** `docs/websites/10_design_ux.md`, `brain/skills/domains/websites/design/spacing-layout.md`.
  - **AC:**
    - Max-width container component exists.
    - Spacing scale is documented or encoded in utility classes.
  - **If Blocked:** Use a minimal container + spacing utilities and document defaults.

- [x] **3.3** Implement core UI components
  - **Goal:** Standardize nav/buttons/cards to match the design direction.
  - **References:** `docs/websites/10_design_ux.md`, `brain/skills/domains/frontend/accessibility-patterns.md`.
  - **Scope:** Header/Nav, Footer, Button (primary/secondary), Card, Badge/Pill.
  - **AC:**
    - Rounded corners + light borders + subtle shadows match the doc.
    - Focus states are visible and keyboard navigation works.
  - **If Blocked:** Prefer accessibility correctness over visual parity; note visual deltas.
  - **Completed:** 2026-01-30 - All core UI components created with accessibility features

- [x] **3.4** Implement the Email Report Preview (hero object)
  - **Goal:** Make the value instantly legible: "email-first monitoring, no dashboard required."
  - **References:** `docs/websites/04_page_requirements.md`, `docs/websites/10_design_ux.md`.
  - **AC:**
    - Includes subject: "Weekly SEO Regression Digest — example.com".
    - Has sections: Critical / Warning / Info.
    - Includes "Top 3 actions this week".
    - Uses severity colors as accents (not loud backgrounds).
  - **If Blocked:** Reduce to a static component (no interactivity) but keep exact content structure.
  - **Completed:** 2026-01-30 - EmailReportPreview component created with severity sections, top actions, and accessible markup

### Task 4: Homepage implementation (sections + copy)

- [x] **4.1** Implement homepage sections exactly per blueprint
  - **Completed:** 2026-01-30 - All homepage sections implemented per blueprint (hero, social proof, why different, features, how it works, sample report, pricing teaser, FAQ teaser, final CTA)
  - **Goal:** Ship the primary conversion page in the intended “soft SaaS” style.
  - **References:** `docs/websites/04_page_requirements.md`, `docs/websites/05_copy_system.md`, `brain/skills/domains/websites/architecture/section-composer.md`.
  - **AC:** Homepage contains:
    - Hero (badge, headline, subhead, CTAs, email preview)
    - Social proof strip
    - 3-card “why different” trio
    - Feature tabs
    - How it works
    - Sample report section
    - Pricing teaser
    - FAQ teaser
    - Final CTA
  - **If Blocked:** Ship hero + why-different + pricing + final CTA first, then fill remaining sections.

- [x] **4.2** Implement Feature Tabs component
  - **Goal:** Show breadth without clutter.
  - **References:** `docs/websites/04_page_requirements.md`.
  - **AC:** Tabs exist with correct labels and each has 3 bullets + preview snippet:
    - Daily Critical Checks
    - Weekly Digest
    - SEO Signals
    - PSI Monitoring
  - **If Blocked:** Replace tabs with a 4-card grid; keep same content.

- [x] **4.3** Implement FAQ accordion (accessible)
  - **Goal:** Handle core objections with low friction.
  - **References:** `docs/websites/04_page_requirements.md`, `brain/skills/domains/frontend/accessibility-patterns.md`.
  - **AC:**
    - Contains the required questions (noise, JS-heavy, setup).
    - Keyboard navigable with correct ARIA.
  - **If Blocked:** Use a static FAQ list but keep headings/structure and add anchors.

### Task 5: Additional pages (pricing, sample report, legal, 404)

- [x] **5.1** Implement `/pricing` from pricing doc
  - **Goal:** Make upgrade path and limits obvious.
  - **References:** `docs/websites/06_pricing_packaging.md`, `docs/websites/05_copy_system.md`.
  - **AC:**
    - Plan cards exist as specified.
    - PSI limits and crawl limits are visible.
    - Primary CTA on pricing is “Start monitoring”.
  - **If Blocked:** Ship a simplified 3-tier card layout and link to contact for enterprise.

- [x] **5.2** Implement `/sample-report`
  - **Goal:** Provide a tangible proof artifact.
  - **References:** `docs/SAMPLE_REPORT.md`, `docs/websites/04_page_requirements.md`.
  - **AC:**
    - Shows a full (or near-full) sample digest.
    - Has a primary CTA “Get a sample report”.
  - **If Blocked:** Embed a truncated sample and link to the full doc.

- [x] **5.3** Implement `/privacy` and `/terms`
  - **Goal:** Reduce procurement friction and improve trust.
  - **References:** `docs/WEBSITE_REQUIREMENTS.md`.
  - **AC:** Pages exist and are linked in the footer.
  - **If Blocked:** Ship minimal placeholders labeled “Draft” and create follow-up tasks.

- [x] **5.4** Implement `/404`
  - **Goal:** Avoid dead ends.
  - **AC:** Has navigation back to `/` and `/pricing`.
  - **If Blocked:** Use a basic 404 page without custom styling.

### Task 6: API contract + forms integration

- [x] **6.1** Write website↔API contract doc
  - **Goal:** Prevent frontend/backend mismatch.
  - **AC:** A doc under `docs/` includes:
    - endpoints
    - request/response JSON
    - CORS rules
    - error handling
  - **If Blocked:** Document as a section inside `docs/WEBSITE_REQUIREMENTS.md`.

- [x] **6.2** Implement website forms (frictionless)
  - **Goal:** Max conversions with minimal inputs.
  - **AC:**
    - Homepage form uses: email (required), domain (required), key pages optional.
    - Sitemap toggle default ON:
      - ON: allow submit with no key pages.
      - OFF: require ≥1 key page.
    - Honeypot present.
  - **If Blocked:** Remove key pages and keep only email+domain.

- [x] **6.3** Wire website forms to API (`/public/leads`, `/public/start-monitoring`)
  - **Goal:** End-to-end conversions.
  - **AC:**
    - Success state is clean.
    - Error state is clear.
    - Configurable API base URL for local/prod.
  - **If Blocked:** Point to a stub endpoint and log submissions locally (temporary).

### Task 7: Anti-abuse + email canonicalization

- [x] **7.1** Implement email canonicalization and dedupe (Gmail dot/plus)
  - **Goal:** Prevent trial abuse via email variants.
  - **Requirements:**
    - Lowercase and trim.
    - For Gmail/Googlemail: remove dots, strip `+tag`, normalize domain to `gmail.com`.
    - Store: `email_raw`, `email_canonical`.
    - Uniqueness constraints:
      - Account owner/lead: global unique on `email_canonical`.
      - Recipients: unique on `(customer_id, email_canonical)`.
  - **AC:** Re-signup with dot/plus variants maps to the same canonical email and is rejected or safely merged.
  - **If Blocked:** Implement canonicalization only and add follow-up task for DB uniqueness index.

### Task 8: Scheduling settings follow-up (email link → schedule page)

- [x] **8.1** Implement schedule settings page (`/schedule`) with timezone auto-detect
  - **Goal:** Let motivated users customize cadence without hurting initial conversion.
  - **Timezone UX (confirmed):**
    - Default timezone from `Intl.DateTimeFormat().resolvedOptions().timeZone`.
    - Dropdown override.
    - Fallback to UTC if detection fails.
  - **Post-save UX (confirmed):**
    - Stay on page.
    - Show success panel:
      - “Saved”
      - “You’ll receive reports every <weekday> at <time> (<timezone> / <UTC offset>).”
      - “First report: …”
    - Preview:
      - Before save: best-effort client preview.
      - After save: API response is authoritative.
  - **AC:** Matches UX rules above.
  - **If Blocked:** Skip preview and show only the API-computed next run after save.

- [x] **8.2** Implement schedule token link in emails (30-day expiry, scoped, rotated)
  - **Goal:** Passwordless schedule settings.
  - **Requirements (confirmed):**
    - Expiry: 30 days.
    - Scope: schedule update only.
    - Rotate/single-use token after successful update.
    - Include "Set schedule" link in:
      - confirmation emails
      - unlocked weekly digest emails
      - paywalled weekly emails
  - **AC:** Token works, cannot be guessed, and old token no longer works after update.
  - **If Blocked:** Use a short-lived token and include a "request new link" endpoint.

- [x] **8.3** Implement `POST /public/schedule` (API source of truth)
  - **Goal:** Persist schedule + return authoritative next run.
  - **Request:** token, digest_weekday, digest_time_local, digest_timezone.
  - **Response (required):**
    - `timezone`
    - `utc_offset_minutes` (at next run)
    - `next_run_at_utc` (ISO)
    - `next_run_at_local` (ISO) (recommended)
  - **AC:** Uses backend timezone rules (DST-safe) and returns authoritative next run.
  - **If Blocked:** Return only `next_run_at_utc` and `timezone` initially; add follow-up.

### Task 9: Funnel endpoints + trial provisioning

- [x] **9.1** Implement `POST /public/leads`
  - **Goal:** Capture demand and deliver sample report.
  - **AC:**
    - Stores lead.
    - Sends sample report email.
    - Includes optional "Start monitoring" next-step link.
  - **If Blocked:** Store lead only and log a TODO for email send.
  - **Completed:** 2026-01-30 - Added `render_sample_report()` email template, updated endpoint to send sample report with CTA to start monitoring, tests verify email sending and graceful failure handling.

- [x] **9.2** Implement `POST /public/start-monitoring` with immediate trial provisioning
  - **Goal:** Deliver instant value while controlling abuse.
  - **Status model:** `trial` → `paywalled` → `previously_interested` → `active`.
  - **Trial limits (confirmed):**
    - Key pages max: 3–5
    - Sitemap crawl: 25–50 URLs
    - PSI: 0–1 pages (or off)
    - Daily checks: critical-only
    - Weekly digest: on (limited by caps)
  - **AC:** Customer is provisioned as `trial`, jobs scheduled under trial limits, confirmation email sent.
  - **If Blocked:** Provision customer record only and queue jobs later.
  - **Completed:** 2026-01-30 - Updated database schema to support trial/paywalled/previously_interested statuses, implemented trial provisioning endpoint with 5 key page limit, 50 URL crawl limit, 1 PSI page limit, added `render_trial_confirmation()` email template, tests verify trial status creation, limit enforcement, and confirmation email sending.

### Task 10: Trial expiry + paywall campaign emails

- [x] **10.1** Enforce trial expiry and transition `trial → paywalled`
  - **Goal:** Automatically end trials deterministically.
  - **Rules:** Trial ends after 7 days OR 1 weekly digest.
  - **Counters (confirmed):**
    - `post_trial_unlocked_critical_remaining = 1`
    - `post_trial_locked_critical_remaining = 2`
  - **AC:** Trial transitions are idempotent and test-covered.
  - **If Blocked:** End trials by date only and add follow-up for digest-count path.
  - **Completed:** 2026-01-30 - Added trial tracking columns to customers table (trial_started_at, paywalled_since, weekly_digest_sent_count, post_trial_unlocked/locked_critical_remaining), implemented check_and_expire_trials() function with idempotent trial→paywalled transitions based on 7-day OR 1-digest rule, updated start_monitoring endpoint to set trial_started_at, added comprehensive test coverage (9 tests) verifying expiry logic, idempotency, and edge cases.

- [x] **10.2** Weekly paywall emails for 4 weeks, then `previously_interested` monthly reminder
  - **Goal:** Convert trials while keeping cadence familiar.
  - **Paywall cadence:**
    - Weeks 1–4 after trial end: 1 paywalled email/week.
    - After week 4: status → `previously_interested`.
    - `previously_interested`: 1 locked reminder/month on the same weekday/time.
  - **Monthly scheduling rule:** First occurrence of digest weekday on/after the 1st of the month at the saved local time.
  - **Post-trial daily critical behavior (only if real critical occurs; never fabricate):**
    - If paywalled and a real Critical finding occurs:
      - Send 1 unlocked critical (if remaining).
      - Then send 2 locked/blurred critical (if remaining).
      - Then stop daily critical.
  - **AC:**
    - Exactly 4 weekly paywall emails max.
    - Monthly sends at most 1 per month.
    - Critical counters persist and behave exactly.
  - **If Blocked:** Implement weekly paywall only and stop after 4 sends; add follow-up for monthly.
  - **Completed:** 2026-01-30 - Fixed email_logs→deliveries table reference bug in paywall_cadence.py and tests. All paywall cadence logic was already implemented: should_send_paywall_digest() checks weekly (7-day spacing, max 4) for paywalled customers and monthly (first occurrence of digest weekday on/after 1st of month) for previously_interested; increment_digest_count_and_check_transition() auto-transitions paywalled→previously_interested after 4th digest. Weekly digest runner already integrates both functions. Verified with 13 passing tests.

- [x] **10.3** Implement unlocked vs paywalled digest templates (blurred locked examples)
  - **Goal:** Make paywall obvious without revealing real findings.
  - **Paywalled copy (exact; blur the example text so it’s not legible):**
    - 🔴 Critical
      - “🔒 Locked — example issue: ‘Important page became non-indexable’”
      - “🔒 Locked — example fix: ‘Review robots/noindex/canonical settings’”
    - 🟠 Warning
      - “🔒 Locked — example change: ‘Title or canonical changed on a key page’”
    - 🔵 Info
      - “🔒 Locked — example note: ‘Content changed since last snapshot’”
  - **Unlocked digest:** real findings from their site (Critical/Warning/Info).
  - **AC:**
    - Paywalled emails preserve Critical/Warning/Info labels and blur locked text.
    - Unlocked emails contain real findings.
  - **If Blocked:** Use locked content without blur (still no real findings) and file follow-up to add blur.

- [x] **10.4** Paystack checkout links in emails
  - **Goal:** One-click upgrade.
  - **AC:** Env vars exist and button points to correct Paystack URLs:
    - `PAYSTACK_STARTER_CHECKOUT_URL`
    - `PAYSTACK_PRO_CHECKOUT_URL`
    - `PAYSTACK_AGENCY_CHECKOUT_URL`
  - **If Blocked:** Use a single `PAYSTACK_CHECKOUT_URL` and upgrade manually.

### Task 11: Analytics (GA4/GTM) + events + weekly operator digest

- [x] **11.1** Add GTM/GA4 integration
  - **Goal:** Track conversions.
  - **AC:** GTM container ID comes from env config and loads correctly.
  - **If Blocked:** Use `gtag.js` directly with GA4 measurement ID.

- [x] **11.2** Implement required analytics events
  - **Goal:** Measure funnel.
  - **AC:** Events fire with useful properties:
    - `cta_get_sample_report_click`
    - `cta_start_monitoring_click`
    - `lead_submit`
    - `start_monitoring_submit`
  - **If Blocked:** Log events to console in dev; ship minimal events.

- [x] **11.3** Weekly analytics digest email (full report; no LLM)
  - **Goal:** Get a raw weekly report delivered for local summarization.
  - **AC:** Script exists (cron runnable) and emails:
    - full GA report payload as text or CSV attachment
    - via Mailgun
  - **If Blocked:** Output to a local file and email a link/path.

### Task 12: SEO + accessibility + performance

- [x] **12.1** Implement SEO metadata defaults and per-page metadata
  - **Goal:** Avoid shipping an SEO tool with weak SEO.
  - **References:** `brain/skills/domains/marketing/seo/seo-audit.md`.
  - **AC:** Titles/descriptions, OG/Twitter, canonical correct.
  - **If Blocked:** Implement site-wide defaults and add follow-up for per-page overrides.

- [x] **12.2** Add `robots.txt` and `sitemap.xml`
  - **Goal:** Enable indexing.
  - **AC:** robots allows indexing; sitemap lists all public routes.
  - **If Blocked:** Ship robots.txt only.

- [x] **12.3** Accessibility pass
  - **Goal:** Keyboard + semantics work.
  - **References:** `brain/skills/domains/frontend/accessibility-patterns.md`.
  - **AC:** No obvious keyboard traps; headings/landmarks are correct.
  - **If Blocked:** Fix the most severe issues and file follow-ups.

- [x] **12.4** Performance pass
  - **Goal:** Fast, calm marketing site.
  - **AC:** Images optimized; minimal JS.
  - **If Blocked:** Defer non-critical animations.

### Task 13: Deployment (GitHub Pages + custom domain)

- [ ] **13.1** GitHub Actions deploy workflow for GitHub Pages
  - **Goal:** Reproducible deployment.
  - **AC:** Workflow builds and deploys `website/` output.
  - **If Blocked:** Document manual deploy steps.

- [ ] **13.2** Custom domain (CNAME) + launch docs
  - **Goal:** Make launch repeatable.
  - **AC:** CNAME is configured and `docs/websites/12_launch.md` includes steps.
  - **If Blocked:** Deploy to default GitHub Pages domain first.

- [ ] **13.3** Environment configuration strategy
  - **Goal:** Safe config for prod.
  - **AC:** API base URL and GTM IDs are configurable; safe local defaults exist.
  - **If Blocked:** Hardcode local dev URLs only; keep prod config pending.

### Task 14: QA + release

- [ ] **14.1** QA checklist run
  - **Goal:** Prevent obvious regressions.
  - **References:** `docs/websites/11_qa_acceptance.md`.
  - **AC:** Checklist is completed with pass/fail notes.
  - **If Blocked:** Run a minimal smoke checklist and file follow-ups.

- [ ] **14.2** End-to-end verification: lead + trial provisioning + first email
  - **Goal:** Ensure the core funnel works.
  - **AC:**
    - lead submission works
    - trial provisioning works
    - at least one expected email is sent
  - **If Blocked:** Validate via logs and local email sink.

- [ ] **14.3** Final content consistency sweep
  - **Goal:** Remove placeholders and enforce CTA consistency.
  - **AC:**
    - No placeholder copy.
    - CTA labels match the copy system.
  - **If Blocked:** Create a punch list and stop.

---

## If blocked (general)

If any item is blocked by unknown values (GTM container ID, Paystack URLs, DNS settings, etc.), create a skill request doc:

- `docs/SKILL_REQUEST_website_<topic>.md`

Include:

- what’s missing
- why it blocks the current task
- proposed defaults
- acceptance criteria
