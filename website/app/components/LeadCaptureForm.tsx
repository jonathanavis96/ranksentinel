'use client';

import React, { useState, FormEvent } from 'react';
import Button from './Button';

interface LeadCaptureFormProps {
  className?: string;
}

interface FormData {
  email: string;
  domain: string;
  keyPages: string;
  useSitemap: boolean;
  honeypot: string; // Anti-spam field
}

interface FormErrors {
  email?: string;
  domain?: string;
  keyPages?: string;
  submit?: string;
}

/**
 * LeadCaptureForm - Frictionless lead capture for RankSentinel
 * 
 * Design principles (from brain/skills/domains/marketing/cro/form-cro.md):
 * - Minimize required fields (email + domain only)
 * - Optional key pages field for power users
 * - Sitemap toggle default ON for ease of use
 * - Honeypot for spam prevention
 * - Inline validation for immediate feedback
 * - Clear error states
 * - No form clearing on error
 * 
 * AC Requirements (Task 6.2):
 * - Email (required), Domain (required), Key pages (optional)
 * - Sitemap toggle default ON:
 *   - ON: allow submit with no key pages
 *   - OFF: require ≥1 key page
 * - Honeypot present
 */
export default function LeadCaptureForm({ className = '' }: LeadCaptureFormProps) {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    domain: '',
    keyPages: '',
    useSitemap: true,
    honeypot: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Email validation
  const validateEmail = (email: string): string | undefined => {
    if (!email.trim()) {
      return 'Email is required';
    }
    // Basic email pattern
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      return 'Please enter a valid email address';
    }
    return undefined;
  };

  // Domain validation
  const validateDomain = (domain: string): string | undefined => {
    if (!domain.trim()) {
      return 'Domain is required';
    }
    // Basic domain pattern (supports http/https and with/without protocol)
    const domainPattern = /^(https?:\/\/)?([\w-]+\.)+[\w-]+(\/.*)?$/;
    if (!domainPattern.test(domain.trim())) {
      return 'Please enter a valid domain (e.g., example.com)';
    }
    return undefined;
  };

  // Key pages validation (conditional on sitemap toggle)
  const validateKeyPages = (keyPages: string, useSitemap: boolean): string | undefined => {
    if (!useSitemap && !keyPages.trim()) {
      return 'Please enter at least one key page URL, or enable sitemap detection';
    }
    return undefined;
  };

  // Handle field blur for inline validation
  const handleBlur = (field: string) => {
    setTouched({ ...touched, [field]: true });
    
    let error: string | undefined;
    if (field === 'email') {
      error = validateEmail(formData.email);
    } else if (field === 'domain') {
      error = validateDomain(formData.domain);
    } else if (field === 'keyPages') {
      error = validateKeyPages(formData.keyPages, formData.useSitemap);
    }
    
    if (error) {
      setErrors({ ...errors, [field]: error });
    } else {
      const newErrors = { ...errors };
      delete newErrors[field as keyof FormErrors];
      setErrors(newErrors);
    }
  };

  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });

    // Clear error on change if field was touched
    if (touched[name] && errors[name as keyof FormErrors]) {
      const newErrors = { ...errors };
      delete newErrors[name as keyof FormErrors];
      setErrors(newErrors);
    }
  };

  // Form submission
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Honeypot check - if filled, it's a bot
    if (formData.honeypot) {
      console.log('Honeypot triggered, ignoring submission');
      return;
    }

    // Validate all fields
    const emailError = validateEmail(formData.email);
    const domainError = validateDomain(formData.domain);
    const keyPagesError = validateKeyPages(formData.keyPages, formData.useSitemap);

    const validationErrors: FormErrors = {};
    if (emailError) validationErrors.email = emailError;
    if (domainError) validationErrors.domain = domainError;
    if (keyPagesError) validationErrors.keyPages = keyPagesError;

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      // Mark all fields as touched
      setTouched({ email: true, domain: true, keyPages: true });
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // Get API base URL from environment or default to localhost
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      
      // Call the public API endpoint
      const response = await fetch(`${apiBaseUrl}/public/start-monitoring`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email.trim(),
          domain: formData.domain.trim(),
          key_pages: formData.keyPages.trim() || null,
          use_sitemap: formData.useSitemap,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle API error
        throw new Error(data.detail || 'Failed to start monitoring');
      }

      // Success state
      if (data.success) {
        alert(data.message || 'Thank you! We\'ll start monitoring your site shortly.');
        
        // Reset form on success
        setFormData({
          email: '',
          domain: '',
          keyPages: '',
          useSitemap: true,
          honeypot: '',
        });
        setTouched({});
      } else {
        throw new Error(data.message || 'Something went wrong');
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({
        submit: error instanceof Error ? error.message : 'Something went wrong. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-4 ${className}`}>
      {/* Email field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-[var(--color-text)] mb-1">
          Email Address <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={() => handleBlur('email')}
          disabled={isSubmitting}
          className={`w-full px-4 py-2.5 rounded-lg border ${
            errors.email && touched.email
              ? 'border-red-500 focus:ring-red-500'
              : 'border-[var(--color-border)] focus:ring-[var(--color-primary)]'
          } focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed bg-white text-[var(--color-text)]`}
          placeholder="you@company.com"
          aria-invalid={errors.email && touched.email ? 'true' : 'false'}
          aria-describedby={errors.email && touched.email ? 'email-error' : undefined}
        />
        {errors.email && touched.email && (
          <p id="email-error" className="mt-1 text-sm text-red-500" role="alert">
            {errors.email}
          </p>
        )}
      </div>

      {/* Domain field */}
      <div>
        <label htmlFor="domain" className="block text-sm font-medium text-[var(--color-text)] mb-1">
          Website Domain <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="domain"
          name="domain"
          value={formData.domain}
          onChange={handleChange}
          onBlur={() => handleBlur('domain')}
          disabled={isSubmitting}
          className={`w-full px-4 py-2.5 rounded-lg border ${
            errors.domain && touched.domain
              ? 'border-red-500 focus:ring-red-500'
              : 'border-[var(--color-border)] focus:ring-[var(--color-primary)]'
          } focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed bg-white text-[var(--color-text)]`}
          placeholder="example.com"
          aria-invalid={errors.domain && touched.domain ? 'true' : 'false'}
          aria-describedby={errors.domain && touched.domain ? 'domain-error' : undefined}
        />
        {errors.domain && touched.domain && (
          <p id="domain-error" className="mt-1 text-sm text-red-500" role="alert">
            {errors.domain}
          </p>
        )}
      </div>

      {/* Sitemap toggle */}
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="useSitemap"
          name="useSitemap"
          checked={formData.useSitemap}
          onChange={handleChange}
          disabled={isSubmitting}
          className="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)] focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <label htmlFor="useSitemap" className="text-sm text-[var(--color-text)]">
          Auto-detect pages from sitemap (recommended)
        </label>
      </div>

      {/* Key pages field (optional) */}
      <div>
        <label htmlFor="keyPages" className="block text-sm font-medium text-[var(--color-text)] mb-1">
          Key Pages {!formData.useSitemap && <span className="text-red-500">*</span>}
          {formData.useSitemap && <span className="text-[var(--color-text-muted)] text-xs ml-1">(optional)</span>}
        </label>
        <textarea
          id="keyPages"
          name="keyPages"
          value={formData.keyPages}
          onChange={handleChange}
          onBlur={() => handleBlur('keyPages')}
          disabled={isSubmitting}
          rows={3}
          className={`w-full px-4 py-2.5 rounded-lg border ${
            errors.keyPages && touched.keyPages
              ? 'border-red-500 focus:ring-red-500'
              : 'border-[var(--color-border)] focus:ring-[var(--color-primary)]'
          } focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed bg-white text-[var(--color-text)] resize-y`}
          placeholder="https://example.com/important-page&#10;https://example.com/another-page"
          aria-invalid={errors.keyPages && touched.keyPages ? 'true' : 'false'}
          aria-describedby={errors.keyPages && touched.keyPages ? 'keyPages-error' : undefined}
        />
        {errors.keyPages && touched.keyPages && (
          <p id="keyPages-error" className="mt-1 text-sm text-red-500" role="alert">
            {errors.keyPages}
          </p>
        )}
        <p className="mt-1 text-xs text-[var(--color-text-muted)]">
          {formData.useSitemap 
            ? 'Optional: Add specific pages to monitor in addition to sitemap pages'
            : 'Enter one URL per line'
          }
        </p>
      </div>

      {/* Honeypot field (hidden from users) */}
      <div className="hidden" aria-hidden="true">
        <label htmlFor="honeypot">Leave this field empty</label>
        <input
          type="text"
          id="honeypot"
          name="honeypot"
          value={formData.honeypot}
          onChange={handleChange}
          tabIndex={-1}
          autoComplete="off"
        />
      </div>

      {/* Submit error */}
      {errors.submit && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg" role="alert">
          <p className="text-sm text-red-700">{errors.submit}</p>
        </div>
      )}

      {/* Submit button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        disabled={isSubmitting}
        className="w-full"
      >
        {isSubmitting ? 'Starting monitoring...' : 'Start Free Monitoring'}
      </Button>

      {/* Privacy note */}
      <p className="text-xs text-center text-[var(--color-text-muted)]">
        No credit card required. We respect your privacy.
      </p>
    </form>
  );
}
