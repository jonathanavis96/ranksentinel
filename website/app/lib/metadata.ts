import { Metadata } from 'next';

/**
 * Shared SEO metadata configuration for RankSentinel
 * 
 * SEO best practices applied:
 * - brain/skills/domains/marketing/seo/seo-audit.md (meta tags, OG protocol)
 * - brain/skills/domains/marketing/seo/schema-markup.md (Open Graph structure)
 * 
 * Copy guidelines applied:
 * - brain/skills/domains/websites/copywriting/value-proposition.md
 *   (outcome-focused description; clear, specific, believable)
 * - brain/skills/domains/marketing/content/copy-editing.md
 *   (tighten copy; remove fluff; concrete delivery mechanism)
 */

export const siteConfig = {
  name: 'RankSentinel',
  // Value-prop first, concrete delivery mechanism second (email), avoid fluff.
  // Pattern: [End result/transformation] + [specific audience pain] + [delivery method]
  // References:
  // - brain/skills/domains/websites/copywriting/value-proposition.md
  // - brain/skills/domains/marketing/content/copy-editing.md
  description:
    'Low-noise SEO monitoring that catches the changes that hurt rankings—before traffic drops. Weekly digests + daily critical alerts via email.',
  url: process.env.NEXT_PUBLIC_SITE_URL || 'https://ranksentinel.com',
  // Needed for GitHub Pages (/ranksentinel) and future custom domains (empty basePath)
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  // OG image: 1200×630 webp, basePath-safe, text matches value-prop copy
  // Cache-busting timestamp forces social platforms to re-fetch after updates
  ogImage: '/og-image.webp?v=1738248000',
  twitterHandle: '@ranksentinel',
};

/**
 * Generate metadata for a page with proper defaults and overrides
 */
export function generateMetadata({
  title,
  description,
  path = '',
  ogImage,
  noIndex = false,
}: {
  title: string;
  description?: string;
  path?: string;
  ogImage?: string;
  noIndex?: boolean;
}): Metadata {
  const fullTitle = title === siteConfig.name ? title : `${title} | ${siteConfig.name}`;
  const finalDescription = description || siteConfig.description;
  const canonicalUrl = `${siteConfig.url}${siteConfig.basePath}${path}`;
  const finalOgImage = ogImage || `${siteConfig.url}${siteConfig.basePath}${siteConfig.ogImage}`;

  return {
    title: fullTitle,
    description: finalDescription,
    ...(noIndex && { robots: { index: false, follow: false } }),
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      type: 'website',
      locale: 'en_US',
      url: canonicalUrl,
      title: fullTitle,
      description: finalDescription,
      siteName: siteConfig.name,
      images: [
        {
          url: finalOgImage,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
      // Open Graph protocol: brain/skills/domains/marketing/seo/schema-markup.md
    },
    twitter: {
      card: 'summary_large_image',
      title: fullTitle,
      description: finalDescription,
      images: [finalOgImage],
      creator: siteConfig.twitterHandle,
    },
  };
}

/**
 * Default metadata for the site root
 */
export const defaultMetadata: Metadata = generateMetadata({
  title: siteConfig.name,
  description: siteConfig.description,
  path: '',
});
