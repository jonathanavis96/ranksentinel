# Step 4 — Page Requirements

## Required reading (agents must open these)

- `brain/skills/domains/websites/architecture/section-composer.md`
- `brain/skills/domains/websites/copywriting/objection-handler.md`

---

## Default direction (RankSentinel)

RankSentinel’s marketing site should use a **modern “soft SaaS” landing style**:

- Big headline
- Quiet background gradients
- Rounded cards
- Minimal nav
- One clear primary CTA
- **Hero “object” visual**: a beautiful **email report preview** (weekly digest + daily critical alert style)

This doc is written to be *implementation-ready* (section layout, anchor IDs, and required content).

---

## Hash / anchor system (required)

Use these anchors for homepage in-page navigation and for reusing sections across pages.

Rules:

- Anchor IDs use **kebab-case**.
- Anchors are stable; don’t change once shipped.
- Nav links should use these hashes (example: `/pricing#plans`).

### Homepage anchors

- `#top`
- `#outcomes`
- `#why-different`
- `#features`
- `#how-it-works`
- `#sample-report`
- `#pricing`
- `#faq`
- `#final-cta`

### Pricing page anchors (for cross-links)

- `/pricing#top`
- `/pricing#plans`
- `/pricing#what-you-get`
- `/pricing#faq`

### FAQ page anchors (optional, if `/faq` is separate)

- `/faq#top`
- `/faq#noise`
- `/faq#js-sites`
- `/faq#setup`

---

## Global layout requirements (all pages)

### Top navigation

Requirements:

- Logo left
- 3–4 links max
- 1 primary nav button (same as primary CTA)

Default nav links (recommended):

- Product (`/product` or `/#features`)
- Pricing (`/pricing` or `/#pricing`)
- Sample report (`/sample-report` or `/#sample-report`)
- FAQ (`/faq` or `/#faq`)
- Primary button: **Start monitoring**

### Primary conversion goal

Site-wide primary CTA should be consistent.

Default primary CTA: **Start monitoring**

Secondary CTA (optional): **See how it works** or **Book a demo**

---

## Homepage — section-by-section blueprint

### 0) Hero + header (`#top`)

**Above-the-fold must be simple and confident.**

Required elements:

- Top nav (see global)
- **Hero badge / pill** (small category statement)
- **Huge headline** (2 lines max)
- Short subhead (1 sentence)
- One primary CTA + optional secondary CTA
- Product preview directly below fold (email report preview object)

Default content (recommended):

- Badge: **Catch SEO regressions before traffic drops**
- Headline: **Low-noise SEO regression monitoring that emails you the actions.**
- Subhead: **Robots, sitemaps, canonicals, noindex, broken links, and PageSpeed regressions—summarized into one weekly digest (with critical-only daily alerts).**
- CTAs:
  - Primary: **Start monitoring**
  - Secondary: **See sample report** (or **See how it works**)

Hero “object” visual (required): **Email report preview card**

- The hero must visually communicate: “you get an actionable weekly email; no dashboard required.”
- The preview should look like a calm Gmail-style card (not a loud mock).

Required fields inside the preview:

- Subject line:
  - `Weekly SEO Regression Digest — example.com`
- Three labeled sections:
  - **Critical**
  - **Warning**
  - **Info**
- Example rows (suggested):
  - Critical: `Key page became noindex`
  - Warning: `Sitemap URL count dropped 18%`
  - Info: `Title changed on /pricing`
- A “Top actions” block:
  - `Top 3 actions this week` with 3 short bullet actions

Optional micro-proof line under CTAs:

- “Designed to avoid false alerts (severity + confirmation + dedupe).”

---

### 1) Social proof strip (`#outcomes`)

Purpose:

- Establish credibility quickly without needing big logos early.

Required structure:

- One-line proof statement + 2–4 proof chips

Default copy options:

- Proof statement: **Built for agencies, founders, and marketing teams.**
- Proof chips (examples):
  - “Low-noise by design”
  - “Critical-only daily emails”
  - “SEO-specific signals (not generic diffs)”
  - “Weekly prioritized actions”

If logos exist later:

- Replace chips with logo row + “Trusted by …” badge.

---

### 2) Why it’s different (3-card trio) (`#why-different`)

This is the Taskk-style “feature trio” that explains the wedge.

Card requirements:

- Icon + title + 2–3 bullets per card
- Keep copy operational and specific; avoid “AI magic” language

Default 3 cards (recommended):

1. **Critical-only daily alerts (no spam)**
   - Daily email only when severity is Critical
   - Confirmation + dedupe to avoid false positives

2. **SEO-specific regression checks**
   - robots.txt, sitemaps, canonical, noindex
   - status/redirect drift, broken internal links, new 404s

3. **Weekly prioritized action report**
   - One digest that summarizes what changed
   - “What to do first” recommendations

---

### 3) Feature tabs (Kawa-style breadth without clutter) (`#features`)

Tabs (required):

- **Daily Critical Checks**
- **Weekly Digest**
- **SEO Signals**
- **PSI Monitoring**

Each tab must include:

- 3 bullets describing outcomes
- A small preview snippet (either an email section excerpt or mini card)

Suggested bullets per tab:

**Daily Critical Checks**

- Alerts only when severity is Critical
- Focused on key pages (high leverage)
- Designed for low false positives (dedupe + confirmation)

**Weekly Digest**

- Critical / Warning / Info grouped summaries
- “Top actions this week” prioritized list
- Stable diffs (normalized content) to reduce noise

**SEO Signals**

- robots.txt change detection
- sitemap deltas (hash + URL count)
- canonical/noindex/title changes
- internal broken links + new 404s

**PSI Monitoring**

- PageSpeed Insights on key URLs
- Confirmation logic for regressions (avoid one-off blips)
- Clear “what changed” + action suggestions

---

### 4) How it works (3-step) (`#how-it-works`)

Structure:

- 3 numbered steps with short headings
- Optional small “operational note” (cron / email delivery)

Default steps:

1. **Add your domain + key pages**
2. **RankSentinel runs daily + weekly via cron**
3. **You get a prioritized report by email**

Operational note (optional, but accurate):

- “Runs on a VPS with cron + Mailgun + PSI API key.”

---

### 5) Sample report preview section (`#sample-report`)

Purpose:

- Make the weekly digest tangible.

Requirements:

- Embed or link to `docs/SAMPLE_REPORT.md` content (or a formatted excerpt)
- Show at least:
  - A “Critical” example
  - A “Warning” example
  - A “Top actions” example

CTA inside section:

- Primary: **Start monitoring**
- Secondary: **See pricing**

---

### 6) Pricing teaser (homepage) (`#pricing`)

Purpose:

- Give clarity without forcing a full table.

Requirements:

- 3 plan cards (Starter / Growth / Agency)
- Show 2–3 constraints users understand (pages monitored, key pages, recipients)
- Link to full pricing page `/pricing#plans`

Homepage CTA:

- Primary: **See pricing**
- Secondary: **See sample report**

---

### 7) FAQ / objections (`#faq`)

Must include at least these questions (wording can vary):

1. **Will it spam me?**
   - Answer must emphasize: severity + confirmation + dedupe; daily only for Critical

2. **Does it work on JS-heavy sites?**
   - Answer must be honest: v1 is requests/bs4; Playwright fallback later (roadmap)

3. **What do I need to set up?**
   - Answer: one-time VPS cron + Mailgun + PSI key

FAQ format:

- Accordion is fine (ensure accessibility)
- Keep answers concise and reassuring

---

### 8) Final CTA block (`#final-cta`)

Requirements:

- Repeat primary CTA: **Start monitoring**
- Short reassurance line:
  - “Weekly clarity. Critical-only alerts. No dashboard required.”

---

## Other required pages (high-level requirements)

### Product page (`/product`)

- Reuse the same hero system (badge → headline → subhead → CTA)
- Expand the Feature Tabs into full-width sections
- Include a “What it monitors” checklist aligned to:
  - robots.txt
  - sitemap deltas
  - canonical
  - noindex
  - titles
  - internal links + 404s
  - PSI (key pages)

### Sample report page (`/sample-report`)

- Lead with the email preview object
- Show a complete example digest (or a close approximation)
- CTA: Start monitoring

### Pricing page (`/pricing`)

- Use the copy and plan structure from `docs/websites/06_pricing_packaging.md`
- Ensure `/pricing#plans` exists

### FAQ page (`/faq`) (optional)

- Can be a dedicated page if homepage FAQ becomes too long
- If separate, keep homepage FAQ as a teaser (3 questions) and link to full FAQ page
