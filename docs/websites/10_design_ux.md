# Step 10 — Design & UX

## Required reading (agents must open these)

- `brain/skills/domains/websites/design/design-direction.md`
- `brain/skills/domains/websites/design/typography-system.md`
- `brain/skills/domains/websites/design/color-system.md`
- `brain/skills/domains/websites/design/spacing-layout.md`

---

## Default design direction: Soft SaaS + “Signal Teal + Ink”

Goal: **trustworthy, calm, premium, low-noise monitoring**.

Visual system keywords:

- White space
- Rounded corners
- Subtle gradients (quiet, not loud)
- Light borders + very light shadows
- Calm palette so the “email report preview” stands out

---

## Palette A (Recommended): Signal Teal + Ink

Vibe: trustworthy, calm, premium, “low-noise monitoring”

Best for: agencies + founders + “peace of mind” positioning

### Core

- Background: `#F7FAFC`
- Surface cards: `#FFFFFF`
- Border: `#E6EDF5`
- Headline text (ink): `#0B1220`
- Body text: `#445066`

### Brand accent

- Primary (teal): `#0F766E`
- Primary hover: `#0B5F59`
- Soft accent tint: `#E6FFFB`

### Severity (email + UI)

- Critical: `#B42318` (muted red, not neon)
- Warning: `#B54708` (amber/burnt orange)
- Info: `#175CD3` (quiet blue)
- Success/OK: `#027A48`

### Gradient

Hero wash:

```css
radial-gradient(60% 60% at 50% 0%, #E6FFFB 0%, #F7FAFC 65%)
```

Why it fits RankSentinel: it feels like “monitoring + clarity”, and the teal reads as “signal” without screaming.

---

## Typography (high-level)

Constraints:

- Use a clean modern sans for most UI and body.
- Optional: a slightly editorial display font for H1/H2 *only if* it doesn’t reduce clarity.

Hero headline requirements:

- Large, 2 lines max
- Keyword-forward (SEO regression monitoring / weekly digest / low-noise)

---

## Spacing + layout rules

Use the spacing guidance from `brain/skills/domains/websites/design/spacing-layout.md`.

Recommended landing page rhythm:

- Major section vertical spacing: 80–120px
- Within section spacing: 20–40px
- Card grid gaps: 16–24px

Max width guidance:

- Text blocks: 60–75ch (readability)
- Hero: allow wider headline but keep subhead readable

---

## Components (implementation-ready specs)

### 1) Header / top nav

- Height: ~64–72px
- Transparent or subtle background over hero wash
- One primary button (teal)
- Links: low-contrast but readable; on hover, increase contrast (not underline-only)

### 2) Hero badge / pill

Purpose: category statement above headline.

- Background: `#E6FFFB`
- Text: `#0B1220` or teal darkened
- Border: `#E6EDF5`
- Radius: fully rounded (999px)
- Font size: small (12–14px)

### 3) Buttons

Primary:

- Background: `#0F766E`
- Hover: `#0B5F59`
- Text: white
- Radius: 10–14px
- Shadow: subtle only on hover

Secondary:

- Background: transparent
- Border: `#E6EDF5`
- Text: `#0B1220`

### 4) Cards (default)

- Background: `#FFFFFF`
- Border: 1px `#E6EDF5`
- Radius: 16–20px
- Shadow: *very light* (avoid heavy drop shadows)

Suggested shadow token:

```css
box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
```

### 5) Email report preview (hero object)

This is the signature visual. It must look like a calm “email client card”.

Structure (required):

- Container card (rounded)
- Header row:
  - “From: RankSentinel” (small)
  - Subject line (prominent): “Weekly SEO Regression Digest — example.com”
- Section blocks:
  - Critical (red accent)
  - Warning (amber accent)
  - Info (blue accent)
- “Top 3 actions this week” block

Styling rules:

- Use borders more than shadows
- Use severity colors as **accents** (e.g., left border or pill), not full backgrounds
- Body copy should be readable at a glance; keep lines short

Severity label chips:

- Critical chip:
  - bg: very light tint of critical (or neutral + colored dot)
  - text: `#B42318`
- Warning chip text: `#B54708`
- Info chip text: `#175CD3`

### 6) Feature tabs

- Tabs should look like pills or segmented control
- Active tab uses soft accent tint + teal border
- Tab content: 3 bullets + small preview snippet card

### 7) FAQ accordion (accessibility)

Requirements:

- Keyboard navigable
- Proper `aria-expanded` and `aria-controls`
- Visible focus outlines

---

## Imagery and illustration guidance

- Avoid busy illustrations.
- Prefer:
  - the email preview object
  - small icon set (consistent stroke width)
  - occasional subtle abstract gradient blobs behind sections

---

## Don’ts (to keep the “soft SaaS” feel)

- Don’t use neon severity colors.
- Don’t use heavy shadows.
- Don’t clutter the hero with multiple competing CTAs.
- Don’t introduce a dashboard UI unless it’s real; the product’s UX is email-first.
