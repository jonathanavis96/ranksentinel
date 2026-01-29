'use client';

import React from 'react';
import Link from 'next/link';
import Container from './Container';

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
 * Accessibility features:
 * - Semantic nav element
 * - Skip link for keyboard users
 * - Focus-visible styles
 * - ARIA labels where appropriate
 */
export default function Header({ className = '' }: HeaderProps) {
  const navLinks: NavLink[] = [
    { href: '/features', label: 'Features' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/docs', label: 'Docs' },
  ];

  return (
    <>
      {/* Skip link for keyboard navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-gray-900 focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)]"
      >
        Skip to main content
      </a>

      <header 
        className={`w-full border-b border-[var(--color-border)] bg-white/80 backdrop-blur-sm sticky top-0 z-40 ${className}`}
        role="banner"
      >
        <Container>
          <nav 
            className="flex items-center justify-between h-16"
            aria-label="Main navigation"
          >
            {/* Logo */}
            <Link 
              href="/"
              className="text-xl font-semibold text-[var(--color-headline)] hover:text-[var(--color-primary)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 rounded"
            >
              RankSentinel
            </Link>

            {/* Nav Links */}
            <div className="flex items-center gap-8">
              <ul className="hidden md:flex items-center gap-6">
                {navLinks.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-[var(--color-body)] hover:text-[var(--color-headline)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 rounded px-2 py-1"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <Link
                href="/signup"
                className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
              >
                Get Started
              </Link>
            </div>
          </nav>
        </Container>
      </header>
    </>
  );
}
