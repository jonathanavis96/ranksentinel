'use client';

import React from 'react';
import Link from 'next/link';
import { trackEvent } from '../lib/analytics';

type ButtonVariant = 'primary' | 'secondary';
type ButtonSize = 'sm' | 'md' | 'lg';

interface AnalyticsProps {
  /** If provided, a click will emit a dataLayer event via trackEvent() */
  analyticsEventName?: string;
  analyticsEventProperties?: Record<string, string | number | boolean>;
}

interface BaseButtonProps extends AnalyticsProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
  disabled?: boolean;
}

interface ButtonAsButtonProps extends BaseButtonProps {
  as?: 'button';
  type?: 'button' | 'submit' | 'reset';
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  href?: never;
}

interface ButtonAsLinkProps extends BaseButtonProps {
  as: 'link';
  href: string;
  type?: never;
  /**
   * Optional additional click handler (runs after analytics tracking).
   * Note: keep this client-side only.
   */
  onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void;
}

type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps;

/**
 * Button component with primary and secondary variants
 * 
 * Design specifications:
 * - Primary: Teal background (#0F766E), white text, hover darken
 * - Secondary: Transparent bg, border, dark text
 * - Rounded corners: 10-14px
 * - Subtle shadow on hover (primary only)
 * 
 * Accessibility features:
 * - Focus-visible ring
 * - Disabled state with reduced opacity and cursor-not-allowed
 * - Proper semantic elements (button vs link)
 * - Keyboard navigation support
 */
export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  as = 'button',
  analyticsEventName,
  analyticsEventProperties,
  ...props
}: ButtonProps) {
  // Base styles shared by all variants
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  // Variant styles (primary uses black bg to match reference examples, hovers to teal)
  const variantStyles = {
    primary: 'bg-[var(--color-headline)] hover:bg-[var(--color-primary)] text-white hover:shadow-md',
    secondary: 'bg-transparent border border-[var(--color-border)] text-[var(--color-headline)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]',
  };

  // Size styles
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-4 py-2 text-sm rounded-lg',
    lg: 'px-6 py-3 text-base rounded-xl',
  };

  const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

  const emitAnalytics = () => {
    if (analyticsEventName) {
      trackEvent(analyticsEventName, analyticsEventProperties || {});
    }
  };

  if (as === 'link') {
    const linkProps = props as ButtonAsLinkProps;

    const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
      emitAnalytics();
      linkProps.onClick?.(e);
    };

    return (
      <Link
        href={linkProps.href}
        className={combinedClassName}
        aria-disabled={disabled}
        onClick={handleLinkClick}
      >
        {children}
      </Link>
    );
  }

  const buttonProps = props as ButtonAsButtonProps;
  
  const handleButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    emitAnalytics();
    buttonProps.onClick?.(e);
  };

  return (
    <button
      type={buttonProps.type || 'button'}
      onClick={handleButtonClick}
      disabled={disabled}
      className={combinedClassName}
    >
      {children}
    </button>
  );
}
