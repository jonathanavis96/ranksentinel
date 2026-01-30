'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import Container from './Container';
import Button from './Button';
import { withBasePath } from '../lib/asset';

interface NavLink {
  href: string;
  label: string;
}

interface HeaderProps {
  className?: string;
}

/**
 * Header/Navigation component
 *
 * Source of truth:
 * - docs/websites/NAV_CTA_SPEC.md
 * - user-provided detailed landing page spec (Palette A, dual CTA funnel)
 */
export default function Header({ className = '' }: HeaderProps) {
  const [isScrolled, setIsScrolled] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navLinks: NavLink[] = [
    { href: '/#features', label: 'Product' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/sample-report', label: 'Sample Report' },
    { href: '/#faq', label: 'FAQ' },
  ];

  const headerChrome = isScrolled
    ? 'bg-white/80 backdrop-blur-sm border-b border-[var(--color-border)]'
    : 'bg-transparent border-b border-transparent';

  return (
    <>
      {/* Skip link for keyboard navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-[var(--color-headline)] focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)]"
      >
        Skip to main content
      </a>

      <header className={`w-full sticky top-0 z-40 transition-colors ${headerChrome} ${className}`} role="banner">
        <Container>
          <nav className="flex items-center justify-between h-16" aria-label="Main navigation">
            {/* Logo */}
            <Link
              href="/"
              className="flex items-center focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 rounded"
            >
              <Image
                src={withBasePath('/ranksentinel-logo.webp')}
                alt="RankSentinel"
                width={160}
                height={40}
                className="h-10 w-auto"
                priority
              />
            </Link>

            {/* Center nav links in white rounded box (Taskk style) */}
            <div className="hidden md:flex absolute left-1/2 -translate-x-1/2 items-center bg-white rounded-full border border-[var(--color-border)] px-6 py-2" style={{ boxShadow: '0 2px 8px rgba(16, 24, 40, 0.08)' }}>
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-sm text-[var(--color-body)] hover:text-[var(--color-headline)] transition-colors px-4 py-1 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 rounded"
                >
                  {link.label}
                </Link>
              ))}
            </div>

            {/* Primary CTA (black pill with deep shadow) */}
            <Button
              as="link"
              href="/start"
              variant="primary"
              size="md"
              className="px-5 py-2.5 text-sm rounded-full"
              analyticsEventName="cta_start_monitoring_click"
              analyticsEventProperties={{ location: 'header' }}
            >
              Start monitoring
            </Button>
          </nav>
        </Container>
      </header>
    </>
  );
}
