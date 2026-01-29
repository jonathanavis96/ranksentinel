# Step 5 — Copy System

## Required reading (agents must open these)

- `brain/skills/domains/websites/copywriting/value-proposition.md`
- `brain/skills/domains/websites/copywriting/cta-optimizer.md`
- `brain/skills/domains/marketing/content/copywriting.md`

---

## Voice + tone (RankSentinel)

Tone keywords:

- Calm, confident
- Specific, not hype
- Operational clarity (“what changed / what broke / what to do”)
- “Low-noise” is a feature; say it plainly

Avoid:

- Over-claiming (“AI will 10x your traffic”)
- Vague marketing (“next-gen monitoring platform”)
- Dashboard-first language

---

## CTA system (single primary)

Default primary CTA (site-wide): **Get a sample report**

Why:

- Fits early-stage reality (sample report builds trust fastest)
- Matches email-first product UX

Secondary CTAs (optional):

- **See how it works**
- **See pricing**
- **Book a demo** (only if you are actually booking demos)

Rules:

- Always one primary CTA per view.
- Secondary CTA must be visually quieter.

---

## Copy patterns to reuse

### 1) Badge / pill (hero)

Formula:

- “Catch [risk] before [impact]”
- “Designed for [audience]”
- “Low-noise monitoring for [category]”

Default badge (recommended):

- **Catch SEO regressions before traffic drops**

### 2) Headline (H1)

Formula options:

- “Low-noise [category] that [delivers outcome].”
- “[Outcome] monitoring that emails you the actions.”

Default headline (recommended):

- **Low-noise SEO regression monitoring that emails you the actions.**

### 3) Subhead

Rules:

- 1 sentence
- Include concrete signals (robots/sitemaps/canonical/noindex/links/PSI)
- Include delivery mechanism (weekly digest + critical-only daily)

Default subhead (recommended):

- **Robots, sitemaps, canonicals, noindex, broken links, and PageSpeed regressions—summarized into one weekly digest (with critical-only daily alerts).**

### 4) Trust line / micro-proof

Goal: reassure about noise and accuracy.

Examples:

- “Designed to avoid false alerts (severity + confirmation + dedupe).”
- “Daily emails only for Critical findings.”

---

## Section headings + starter copy (homepage)

These should map to the anchors in `docs/websites/04_page_requirements.md`.

### `#why-different` — “Why it’s different”

Heading options:

- “Monitoring that respects your attention.”
- “Built for low-noise teams.”

Recommended:

- **Monitoring that respects your attention.**

Support line (optional):

- “Daily alerts only when something is genuinely risky. Everything else rolls up into a weekly plan.”

### `#features` — “What you get”

Heading options:

- “Everything you need to catch regressions early.”
- “SEO signals that actually matter.”

Recommended:

- **SEO signals that actually matter.**

### `#how-it-works`

Heading options:

- “How it works”
- “Three steps to weekly clarity”

Recommended:

- **Three steps to weekly clarity.**

### `#sample-report`

Heading options:

- “See the weekly digest”
- “A report you can act on in 5 minutes”

Recommended:

- **A report you can act on in 5 minutes.**

### `#pricing`

Heading options:

- “Pricing that scales with your site”
- “Start small. Upgrade when your footprint grows.”

Recommended:

- **Pricing that scales with your site — without noisy alerts.**

### `#faq`

Heading options:

- “FAQ”
- “Questions (and honest answers)”

Recommended:

- **Questions (and honest answers).**

### `#final-cta`

Heading options:

- “Get a sample report”
- “Ready to catch regressions before traffic drops?”

Recommended:

- **Ready to catch regressions before traffic drops?**

Reassurance line:

- “Weekly clarity. Critical-only alerts. No dashboard required.”

---

## FAQ answer principles (copy constraints)

Required FAQ prompts:

1) Will it spam me?

- Must explicitly say: daily emails only for Critical.
- Must include: dedupe + severity + confirmation.

2) Does it work on JS-heavy sites?

- Must be honest: v1 is requests/bs4; Playwright fallback later.

3) What do I need to set up?

- Must list: VPS cron + Mailgun + PSI API key.

---

## “Words we should use” glossary

- “Weekly digest” (not “newsletter”)
- “Critical-only daily alerts” (not “spammy notifications”)
- “Regressions” and “indexability risk”
- “Signals” (robots / sitemap / canonical / noindex / links / PSI)
- “Prioritized actions”
