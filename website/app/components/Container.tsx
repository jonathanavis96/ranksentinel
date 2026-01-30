import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  className?: string;
}

/**
 * Container component for consistent max-width and horizontal padding.
 * 
 * Sizes:
 * - sm: 640px (narrow content like blog posts)
 * - md: 768px (medium content)
 * - lg: 1024px (standard content)
 * - xl: 1280px (wide content, default)
 * - 2xl: 1536px (full-width sections)
 */
export default function Container({ 
  children, 
  size = 'xl',
  className = '' 
}: ContainerProps) {
  const maxWidthClass = {
    'sm': 'max-w-[640px]',
    'md': 'max-w-[768px]',
    'lg': 'max-w-[1024px]',
    'xl': 'max-w-[1280px]',
    '2xl': 'max-w-[1536px]'
  }[size];

  return (
    <div className={`w-full ${maxWidthClass} mx-auto px-4 md:px-8 ${className}`}>
      {children}
    </div>
  );
}
