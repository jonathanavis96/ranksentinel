import React from 'react';

type BadgeVariant = 'default' | 'critical' | 'warning' | 'info' | 'success';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

/**
 * Badge/Pill component
 * 
 * Design specifications:
 * - Default (hero badge): Background #E6FFFB, text dark/teal, border #E6EDF5
 * - Severity variants use appropriate colors as accents (not loud backgrounds)
 * - Fully rounded (9999px)
 * - Small font size (12-14px)
 * 
 * Usage:
 * - Hero category labels
 * - Severity indicators in email preview
 * - Status labels
 */
export default function Badge({
  children,
  variant = 'default',
  className = '',
}: BadgeProps) {
  const variantStyles = {
    default: 'bg-[var(--color-accent-tint)] text-[var(--color-primary)] border-[var(--color-border)]',
    critical: 'bg-red-50 text-[var(--color-critical)] border-red-100',
    warning: 'bg-orange-50 text-[var(--color-warning)] border-orange-100',
    info: 'bg-blue-50 text-[var(--color-info)] border-blue-100',
    success: 'bg-green-50 text-[var(--color-success)] border-green-100',
  };

  return (
    <span
      className={`
        inline-flex 
        items-center 
        px-3 
        py-1 
        text-xs 
        font-medium 
        rounded-full 
        border
        ${variantStyles[variant]}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {children}
    </span>
  );
}
