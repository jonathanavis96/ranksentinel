# RankSentinel — Website Requirements (Master)

This document defines the **RankSentinel marketing website requirements**.

It is designed for humans and agents:

- Use this file for the **full, end-to-end requirements**.
- Use `docs/websites/SUMMARY.md` for the **low-token navigation map**.
- For each step, the agent **MUST open and read the linked skill documents** in `brain/skills/…` before writing copy, designing, or implementing.

## Scope

- Marketing website only (no app/dashboard UI required).
- Primary UX is: **explain product → build trust → convert** (waitlist/demo/purchase).

## Source of truth references

- Product contract: `docs/ranksentinel_spec/10_bootstrap_contract.md` (if present)
- Sample embedded report: `docs/SAMPLE_REPORT.md`
- Competitor anchors: `docs/COMPETITOR_PRICING_SNAPSHOT.md`

---

## Step 1 — Goals & non-goals

**Project-specific goals**

- Communicate the wedge: **low-noise SEO regression monitoring** (not generic website change detection).
- Make the weekly digest tangible (show an embedded sample report).
- Convert to one primary action (choose one): “Request access” / “Book a demo” / “Start monitoring”.

**Non-goals**

- No dashboard dependency.
- No generic “monitor anything” positioning.

**Read (required)**

- `brain/skills/domains/websites/discovery/requirements-distiller.md`
- `brain/skills/domains/websites/discovery/scope-control.md`

---

## Step 2 — Audience & positioning

**Primary audiences**

- SEO lead / growth lead
- Engineer/PM responsible for templates/routing/infra

**Positioning constraints (RankSentinel-specific)**

- Weekly digest is the default value.
- Daily email only for Critical findings.
- Emphasize: severity + dedupe + confirmation (noise control).

**Read (required)**

- `brain/skills/domains/websites/discovery/audience-mapping.md`
- `brain/skills/domains/marketing/strategy/launch-strategy.md`

---

## Step 3 — Information architecture (IA) & sitemap

**Required pages**

- Home (`/`)
- Product (`/product`)
- Pricing (`/pricing`)
- FAQ (`/faq`) (can be a section on Home initially)
- About (`/about`) (or “Why RankSentinel”)
- Trust/Security (`/security` or `/trust`)
- Sample report (`/sample-report`)

**Read (required)**

- `brain/skills/domains/websites/architecture/sitemap-builder.md`

---

## Step 4 — Page requirements (section-by-section)

**Homepage required sections**

1. Hero (clear promise + CTA)
2. Proof/credibility
3. Outcomes
4. What it monitors (robots/sitemaps/noindex/canonical/links/PSI)
5. How it works
6. Sample report preview
7. Pricing teaser
8. FAQ / objections
9. Final CTA

**Read (required)**

- `brain/skills/domains/websites/architecture/section-composer.md`
- `brain/skills/domains/websites/copywriting/objection-handler.md`

---

## Step 5 — Copy system (headlines, proof, CTAs)

**Read (required)**

- `brain/skills/domains/websites/copywriting/value-proposition.md`
- `brain/skills/domains/websites/copywriting/cta-optimizer.md`
- `brain/skills/domains/marketing/content/copywriting.md`

---

## Step 6 — Pricing & packaging

Pricing must match the MVP crawl reality (small sites + key pages + weekly sample crawl).

**Read (required)**

- `brain/skills/domains/marketing/strategy/pricing-strategy.md`

### Competitor anchors (must reference)

- `docs/COMPETITOR_PRICING_SNAPSHOT.md`

### Pricing page copy

The full pricing page copy (ready to embed) lives here:

- `docs/websites/06_pricing_packaging.md`

### Recommended tiers (current)

- Starter — **$29/mo**
- Growth — **$69/mo**
- Agency — **$199/mo**

### What “pages monitored” means

RankSentinel is **not** a full-site crawler in the MVP:

- **Daily:** key pages only
- **Weekly:** sitemap sample crawl (capped)

If the pricing page shows a single “pages monitored” number, define it explicitly:

> Total pages monitored = key pages + weekly sampled pages (capped)

---

## Step 7 — CRO

**Read (required)**

- `brain/skills/domains/marketing/cro/page-cro.md`
- `brain/skills/domains/marketing/cro/form-cro.md`

---

## Step 8 — SEO (marketing site)

**Read (required)**

- `brain/skills/domains/marketing/seo/schema-markup.md`
- `brain/skills/domains/marketing/seo/seo-audit.md`

---

## Step 9 — Analytics

**Read (required)**

- `brain/skills/domains/marketing/growth/analytics-tracking.md`

---

## Step 10 — Design & UX

**Read (required)**

- `brain/skills/domains/websites/design/design-direction.md`
- `brain/skills/domains/websites/design/typography-system.md`
- `brain/skills/domains/websites/design/color-system.md`
- `brain/skills/domains/websites/design/spacing-layout.md`

---

## Step 11 — QA & acceptance criteria

**Read (required)**

- `brain/skills/domains/websites/qa/acceptance-criteria.md`
- `brain/skills/domains/websites/qa/accessibility.md`
- `brain/skills/domains/websites/qa/visual-qa.md`

---

## Step 12 — Launch checklist

**Read (required)**

- `brain/skills/domains/websites/launch/deployment.md`
- `brain/skills/domains/websites/launch/finishing-pass.md`
