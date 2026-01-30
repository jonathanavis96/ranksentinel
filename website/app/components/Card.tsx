import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

/**
 * Card component
 * 
 * Design specifications:
 * - Background: White (#FFFFFF)
 * - Border: 1px solid #E6EDF5
 * - Radius: 16-20px
 * - Shadow: Very light (0 1px 2px rgba(16, 24, 40, 0.06))
 * - Optional hover state with slightly enhanced shadow
 * 
 * Accessibility:
 * - Semantic structure preserved (div by default)
 * - Custom content determines heading hierarchy
 */
export default function Card({
  children,
  className = '',
  padding = 'md',
  hover = false,
}: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const hoverStyles = hover
    ? 'hover:shadow-md transition-shadow duration-200'
    : '';

  return (
    <div
      className={`
        bg-white 
        border border-[var(--color-border)] 
        rounded-2xl 
        shadow-[0_1px_2px_rgba(16,24,40,0.06)]
        ${paddingStyles[padding]}
        ${hoverStyles}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {children}
    </div>
  );
}
