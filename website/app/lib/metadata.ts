import { Metadata } from 'next';

/**
 * Shared SEO metadata configuration for RankSentinel
 * 
 * References:
 * - brain/skills/domains/marketing/seo/seo-audit.md
 * - Task 12.1: SEO metadata defaults and per-page metadata
 */

export const siteConfig = {
  name: 'RankSentinel',
  description: 'Low-noise SEO monitoring that catches the changes that hurt rankings—before traffic drops. Weekly digests + daily critical alerts via email.',
  url: process.env.NEXT_PUBLIC_SITE_URL || 'https://ranksentinel.com',
  ogImage: '/og-image.webp',
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
  const canonicalUrl = `${siteConfig.url}${path}`;
  const finalOgImage = ogImage || `${siteConfig.url}${siteConfig.ogImage}`;

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
