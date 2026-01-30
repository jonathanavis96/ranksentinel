'use client';

import Link from 'next/link';
import { trackEvent } from '../lib/analytics';

interface AnalyticsLinkProps {
  href: string;
  eventName: string;
  eventProperties?: Record<string, string | number | boolean>;
  children: React.ReactNode;
  className?: string;
}

/**
 * Link component with analytics tracking
 * Use this for CTA links that need click tracking
 */
export function AnalyticsLink({
  href,
  eventName,
  eventProperties = {},
  children,
  className = '',
}: AnalyticsLinkProps) {
  const handleClick = () => {
    trackEvent(eventName, eventProperties);
  };

  return (
    <Link href={href} onClick={handleClick} className={className}>
      {children}
    </Link>
  );
}
