# Navigation Labels + CTA Placement Rules

**Purpose:** Lock down site-wide navigation structure and CTA consistency to prevent conversion-killing copy drift.

**Status:** MVP specification (approved for implementation)

**References:**
- `docs/websites/04_page_requirements.md` (global layout requirements)
- `docs/websites/05_copy_system.md` (voice + tone)
- `brain/skills/domains/websites/copywriting/cta-optimizer.md` (CTA best practices)

---

## Top Navigation (Header)

### Structure

- **Logo:** Left-aligned, links to `/`
- **Links:** 3–4 max, center or right-aligned
- **Primary button:** 1 button (right-aligned), matches primary CTA

### Nav Links (MVP)

| Label | Destination | Notes |
|-------|-------------|-------|
| **Product** | `/#features` | Scrolls to features section on homepage |
| **Pricing** | `/pricing` | Dedicated pricing page |
| **Sample Report** | `/sample-report` | Dedicated sample report showcase |
| **FAQ** | `/#faq` | Scrolls to FAQ section on homepage |

### Primary Nav Button (MVP)

- **Label:** "Get a sample report"
- **Destination:** `/sample-report` (or form/action endpoint when available)
- **Style:** Primary button (brand color, high contrast)
- **Consistency rule:** This button appears identically on all pages

### Alternative Links (Post-MVP)

If `/product` becomes a separate page:
- **Product** → `/product` (instead of `/#features`)

If `/faq` becomes a separate page:
- **FAQ** → `/faq` (instead of `/#faq`)

---

## Footer Navigation

### Structure

Multi-column layout with links grouped by category.

### Footer Links (MVP)

**Column 1: Product**
- Product → `/#features`
- Pricing → `/pricing`
- Sample Report → `/sample-report`

**Column 2: Resources**
- FAQ → `/#faq`
- Documentation → (placeholder for future `/docs`)

**Column 3: Company**
- About → (placeholder for future `/about`)
- Contact → (placeholder for future `/contact` or `mailto:`)

**Column 4: Legal**
- Privacy Policy → (placeholder for future `/privacy`)
- Terms of Service → (placeholder for future `/terms`)

### Footer Bottom

- Copyright: `© 2026 RankSentinel. All rights reserved.`
- Social links: (optional, TBD)

---

## CTA Placement Rules

### One Primary CTA Per Page View

**Rule:** Each page or viewport section should have ONE dominant call-to-action. Secondary CTAs are allowed but must be visually de-emphasized.

**Primary CTA (site-wide):** "Get a sample report"

**Secondary CTA (optional):** "See how it works" or "Book a demo"

### Homepage CTA Placement

| Section | Primary CTA | Secondary CTA | Notes |
|---------|-------------|---------------|-------|
| `#top` (Hero) | Get a sample report | See how it works (optional) | Above the fold, maximum prominence |
| `#outcomes` | — | — | Social proof only, no CTA |
| `#why-different` | — | — | Educational content, no CTA |
| `#features` | — | — | Feature showcase, no CTA |
| `#how-it-works` | Get a sample report | — | CTA inside section after explanation |
| `#sample-report` | Get a sample report | — | Showcases value, reinforces CTA |
| `#pricing` | See pricing details | — | Links to `/pricing` (button or link) |
| `#faq` | — | — | FAQ section, no CTA |
| `#final-cta` | Get a sample report | — | Final conversion opportunity |

### Pricing Page CTA Placement

- **Primary CTA:** "Start monitoring" (on each plan card)
- **Alternative:** "Get a sample report" (for users not ready to commit)
- **Rule:** Each pricing tier card has ONE prominent button

### Sample Report Page CTA Placement

- **Primary CTA:** "Get a sample report" (after showcasing the report value)
- **Context:** User has seen the value; CTA is the natural next step

---

## CTA Copy Variants (Approved)

### Primary CTA Variants

Use these interchangeably based on context:

1. **"Get a sample report"** (default, most pages)
2. **"Start monitoring"** (pricing page, plan selection)
3. **"See a sample report"** (alternative phrasing for variety)

### Secondary CTA Variants

1. **"See how it works"** (links to `/#how-it-works`)
2. **"Book a demo"** (links to demo scheduling, if available)
3. **"Learn more"** (generic fallback, use sparingly)

---

## Trust + Proof Lines (Under CTAs)

**Purpose:** Reassure users about noise and accuracy without cluttering the CTA.

**Default trust line (optional, use under primary CTAs):**

- "Designed to avoid false alerts (severity + confirmation + dedupe)."

**Alternative trust lines:**

- "Daily emails only for Critical findings."
- "No dashboard required. Just actionable emails."

---

## Anchor Link Consistency

All in-page navigation and cross-page links must use the anchor system defined in `docs/websites/04_page_requirements.md`.

### Homepage Anchors

- `#top`, `#outcomes`, `#why-different`, `#features`, `#how-it-works`, `#sample-report`, `#pricing`, `#faq`, `#final-cta`

### Pricing Page Anchors

- `/pricing#top`, `/pricing#plans`, `/pricing#compare`, `/pricing#what-you-get`, `/pricing#faq`

### Sample Report Page Anchors

- `/sample-report#top` (default)

### Cross-Page Link Examples

- Link from homepage to pricing section: `/pricing#plans`
- Link from nav to features: `/#features`
- Link from footer to FAQ: `/#faq`

---

## Acceptance Criteria (Task 1.2)

- [x] Nav labels and URLs are explicitly listed (header + footer)
- [x] "One primary CTA per page view" is documented with examples
- [x] CTA variants are approved and consistent
- [x] Anchor link system is referenced and aligned with `04_page_requirements.md`
- [x] Trust lines are provided as optional CTA enhancements

---

## Open Questions

None. Implementation is unblocked.

---

## Change Log

- **2026-01-30:** Initial specification created (Task 1.2)
