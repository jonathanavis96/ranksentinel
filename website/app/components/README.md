# Components

## Layout Primitives

### Container

Provides consistent max-width and horizontal padding for content areas.

**Usage:**

```tsx
import Container from '@/app/components/Container';

// Default (xl - 1280px)
<Container>
  <h1>Content here</h1>
</Container>

// Narrow content
<Container size="md">
  <article>Blog post content</article>
</Container>

// Wide content
<Container size="2xl">
  <div>Full-width section</div>
</Container>
```

**Sizes:**

- `sm`: 640px (narrow content like blog posts)
- `md`: 768px (medium content)
- `lg`: 1024px (standard content)
- `xl`: 1280px (wide content, **default**)
- `2xl`: 1536px (full-width sections)

**Responsive behavior:**

- Mobile: 16px horizontal padding
- Desktop (≥768px): 32px horizontal padding

## Spacing Scale

All spacing values use an 8px base unit for predictable rhythm.

Available via CSS variables in `globals.css`:

```css
--space-0: 0
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 20px
--space-6: 24px
--space-8: 32px
--space-10: 40px
--space-12: 48px
--space-16: 64px
--space-20: 80px
--space-24: 96px
--space-32: 128px
```

**Tailwind equivalents:**

- Use Tailwind's default spacing scale (already 8px-based)
- Or use CSS custom properties: `style={{ paddingTop: 'var(--space-20)' }}`

## Section Spacing Pattern

Recommended vertical spacing for landing page sections:

- **Hero sections:** 96px top/bottom (var(--space-24))
- **Standard sections:** 80px top/bottom (var(--space-20))
- **Mobile:** 48px top/bottom (var(--space-12))

**Example:**

```tsx
<section className="py-20 md:py-24">
  <Container>
    {/* Section content */}
  </Container>
</section>
```

## Container Widths

Available via CSS variables:

```css
--container-sm: 640px
--container-md: 768px
--container-lg: 1024px
--container-xl: 1280px (default)
--container-2xl: 1536px
```
