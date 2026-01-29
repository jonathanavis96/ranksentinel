# Step 3 — IA & Sitemap

## Required reading (agents must open these)

- `brain/skills/domains/websites/architecture/sitemap-builder.md`

---

## MVP vs Optional Pages

### MVP Pages (Ship First)

These pages are **required** for the initial launch and align with the section blueprint in `04_page_requirements.md`:

1. **Homepage** (`/` or `/index.html`)
   - Primary landing page with 8 sections (hero → final CTA)
   - Sections: `#top`, `#outcomes`, `#why-different`, `#features`, `#how-it-works`, `#sample-report`, `#pricing`, `#faq`, `#final-cta`
   - **Primary CTA:** "Get a sample report"
   - **Status:** MVP — implementation required

2. **Pricing page** (`/pricing`)
   - Dedicated pricing with plans and packaging
   - Anchor: `#plans` (for cross-links)
   - Copy/structure from `docs/websites/06_pricing_packaging.md`
   - **Primary CTA:** "Start monitoring" or "Get a sample report"
   - **Status:** MVP — implementation required

3. **Sample report page** (`/sample-report`)
   - Showcases email report preview (weekly digest + critical alert)
   - Demonstrates actual value delivered
   - **Primary CTA:** "Get a sample report"
   - **Status:** MVP — implementation required

### Optional Pages (Post-MVP)

These pages can be added after MVP launch or integrated into MVP pages:

4. **Product page** (`/product`) — **OPTIONAL**
   - Detailed feature expansion (Feature Tabs → full sections)
   - "What it monitors" checklist
   - **Alternative:** Can be integrated into homepage `#features` section
   - **Status:** Optional — evaluate after MVP

5. **FAQ page** (`/faq`) — **OPTIONAL**
   - Dedicated FAQ if homepage FAQ (`#faq`) becomes too long
   - **Alternative:** Homepage FAQ section with 3-5 questions (teaser)
   - **Status:** Optional — start with homepage FAQ section, extract if needed

---

## Navigation Structure

Following the 7±2 rule from `sitemap-builder.md`, RankSentinel uses a **minimal nav (4 items max)**.

### Primary Navigation (Header)

```text
[RankSentinel Logo] Product | Pricing | Sample Report [Get a Sample Report CTA Button]
```

**Nav items:**

1. **Product** → `/#features` or `/product` (if optional page is built)
2. **Pricing** → `/pricing` or `/#pricing`
3. **Sample Report** → `/sample-report`
4. **CTA Button:** "Get a sample report" → leads to sample report request flow

**Alternative minimal nav (3 items):**

```text
[RankSentinel Logo] Pricing | Sample Report [Get a Sample Report CTA Button]
```

- Removes "Product" link, relies on homepage sections for feature discovery

### Footer Navigation

```text
| Product | Resources | Legal | Contact |
|---------|-----------|-------|---------|
| Features → /#features | Sample Report → /sample-report | Privacy Policy | Email: support@ranksentinel.com |
| How It Works → /#how-it-works | Pricing → /pricing | Terms of Service | |
| FAQ → /#faq | | | |
```

---

## Page Hierarchy

```text
Home (/)
├── #top (hero)
├── #outcomes (social proof)
├── #why-different (differentiation)
├── #features (feature tabs)
├── #how-it-works (3-step process)
├── #sample-report (report preview)
├── #pricing (pricing teaser)
├── #faq (objections)
└── #final-cta

Pricing (/pricing)
└── #plans

Sample Report (/sample-report)
└── (email preview + CTA)

[Optional - Post-MVP]
Product (/product)
FAQ (/faq)
```

---

## Alignment with `04_page_requirements.md`

### ✅ Resolved Contradictions

1. **MVP scope clarified:**
   - Homepage, Pricing, Sample Report are MVP
   - Product and dedicated FAQ page are optional

2. **Navigation simplified:**
   - 3-4 primary nav items (follows sitemap-builder.md guidance)
   - Homepage sections handle most content needs

3. **Hash/anchor system:**
   - All anchors from `04_page_requirements.md` are preserved
   - Cross-linking between pages is explicit (e.g., `/#pricing` vs `/pricing`)

4. **Primary CTA consistency:**
   - Site-wide: "Get a sample report"
   - Pricing page secondary: "Start monitoring"

### Open Questions

None. MVP scope is clear: **Homepage + Pricing + Sample Report**. If blocked during implementation, default to this three-page structure.
