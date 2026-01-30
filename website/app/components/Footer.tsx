import React from 'react';
import Link from 'next/link';
import Container from './Container';

interface FooterLink {
  href: string;
  label: string;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

/**
 * Footer component
 *
 * Source of truth:
 * - docs/websites/03_ia_sitemap.md (footer navigation)
 * - docs/websites/NAV_CTA_SPEC.md
 */
export default function Footer() {
  const sections: FooterSection[] = [
    {
      title: 'Product',
      links: [
        { href: '/#features', label: 'Features' },
        { href: '/#how-it-works', label: 'How It Works' },
        { href: '/#faq', label: 'FAQ' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { href: '/sample-report', label: 'Sample Report' },
        { href: '/pricing', label: 'Pricing' },
      ],
    },
    {
      title: 'Legal',
      links: [
        { href: '/privacy', label: 'Privacy Policy' },
        { href: '/terms', label: 'Terms of Service' },
      ],
    },
    {
      title: 'Contact',
      links: [{ href: 'mailto:support@ranksentinel.com', label: 'support@ranksentinel.com' }],
    },
  ];

  return (
    <footer className="w-full border-t border-[var(--color-border)] bg-white mt-auto" role="contentinfo">
      <Container>
        <div className="py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-2 md:col-span-1">
              <Link
                href="/"
                className="text-xl font-semibold text-[var(--color-headline)] hover:text-[var(--color-primary)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 rounded inline-block"
              >
                RankSentinel
              </Link>
              <p className="mt-4 text-sm text-[var(--color-body)]">
                Low-noise SEO regression monitoring delivered weekly via email.
              </p>
            </div>

            {sections.map((section) => (
              <div key={section.title}>
                <h3 className="text-sm font-semibold text-[var(--color-headline)] mb-4">{section.title}</h3>
                <nav aria-label={`${section.title} links`}>
                  <ul className="space-y-3">
                    {section.links.map((link) => (
                      <li key={`${section.title}-${link.href}`}> 
                        {/* next/link supports mailto: but use <a> semantics via Link */}
                        <Link
                          href={link.href}
                          className="text-sm text-[var(--color-body)] hover:text-[var(--color-headline)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 rounded inline-block"
                        >
                          {link.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </nav>
              </div>
            ))}
          </div>

          <div className="pt-8 border-t border-[var(--color-border)]">
            <p className="text-sm text-[var(--color-body)] text-center">
              © {new Date().getFullYear()} RankSentinel. All rights reserved.
            </p>
          </div>
        </div>
      </Container>
    </footer>
  );
}
