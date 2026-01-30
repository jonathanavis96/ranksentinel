import React from 'react';

interface EmailReportPreviewProps {
  className?: string;
  style?: React.CSSProperties;
  /**
   * teaser: homepage-style preview (header + top priorities only)
   * full: includes example findings + PSI block
   */
  variant?: 'teaser' | 'full';
}

function Chip({
  label,
  color,
}: {
  label: string;
  color: 'critical' | 'warning' | 'info' | 'neutral';
}) {
  const styles: Record<typeof color, string> = {
    critical: 'bg-[#FEE4E2] text-[var(--color-critical)] border-[#FDA29B]',
    warning: 'bg-[#FEF0C7] text-[var(--color-warning)] border-[#FEC84B]',
    info: 'bg-[#EFF8FF] text-[var(--color-info)] border-[#B2DDFF]',
    neutral: 'bg-[var(--color-background)] text-[var(--color-body)] border-[var(--color-border)]',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${styles[color]}`}>
      {label}
    </span>
  );
}

function SectionHeading({
  label,
  dotColor,
}: {
  label: string;
  dotColor: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-2.5 h-2.5 rounded-full" style={{ background: dotColor }} aria-hidden="true" />
      <h3 className="text-sm font-semibold text-[var(--color-headline)]">{label}</h3>
    </div>
  );
}

function Finding({
  title,
  url,
  action,
}: {
  title: string;
  url: string;
  action: string;
}) {
  return (
    <div className="text-sm">
      <div className="font-medium text-[var(--color-headline)]">{title}</div>
      <div className="mt-1 font-mono text-xs text-[var(--color-body)] opacity-80">{url}</div>
      <div className="mt-1 text-[var(--color-body)]">Recommended: {action}</div>
    </div>
  );
}

/**
 * Email-first "product screenshot" mock.
 *
 * Requirements (per user spec):
 * - Calm email client card (not a dashboard)
 * - Top 3 priorities strip
 * - Severity sections (Critical/Warning/Info)
 * - PSI mini-block with 2-run confirmation language
 * - Footer hint: schedule link
 */
export default function EmailReportPreview({
  className = '',
  style,
  variant = 'full',
}: EmailReportPreviewProps) {
  return (
    <div
      className={`bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden ${className}`}
      style={style || { boxShadow: '0 10px 30px rgba(16, 24, 40, 0.08)' }}
      role="article"
      aria-label="Sample weekly email report"
    >
      {/* Email header chrome */}
      <div className="border-b border-[var(--color-border)] bg-[var(--color-background)] px-6 py-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs text-[var(--color-body)]">From:</div>
            <div className="text-sm font-medium text-[var(--color-headline)]">RankSentinel</div>
          </div>
          <div className="text-xs text-[var(--color-body)] opacity-80">Mon 09:12</div>
        </div>
        <div className="mt-3">
          <div className="text-xs text-[var(--color-body)]">Subject:</div>
          <div className="text-sm font-semibold text-[var(--color-headline)]">Weekly SEO Regression Digest — example.com</div>
        </div>
      </div>

      {/* Email body */}
      <div className="px-6 py-6 space-y-6">
        {/* Top priorities strip */}
        <div className="rounded-xl border border-[var(--color-border)] bg-white p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="text-sm font-semibold text-[var(--color-headline)]">This week’s priorities (Top 3)</div>
            <div className="flex flex-wrap gap-2">
              <Chip label="2 Critical" color="critical" />
              <Chip label="3 Warning" color="warning" />
              <Chip label="4 Info" color="info" />
            </div>
          </div>
          {variant === 'full' ? (
            <ol className="mt-3 space-y-2 text-sm text-[var(--color-body)] list-decimal list-inside">
              <li>
                <span className="font-medium text-[var(--color-headline)]">Homepage set to noindex</span>{' '}
                <span className="text-[var(--color-body)]">— remove or scope to staging</span>
              </li>
              <li>
                <span className="font-medium text-[var(--color-headline)]">Robots.txt blocks /blog/</span>{' '}
                <span className="text-[var(--color-body)]">— restore crawlability</span>
              </li>
              <li>
                <span className="font-medium text-[var(--color-headline)]">Performance regression confirmed</span>{' '}
                <span className="text-[var(--color-body)]">— investigate LCP +650ms</span>
              </li>
            </ol>
          ) : (
            <div className="mt-3 text-sm text-[var(--color-body)]">
              Top findings + recommendations inside.
            </div>
          )}
        </div>

        {variant === 'full' && (
          <>
            {/* Critical */}
            <div className="space-y-3">
              <SectionHeading label="Critical" dotColor="var(--color-critical)" />
              <div className="pl-4 space-y-3">
                <Finding
                  title="Key page set to noindex (indexability loss)"
                  url="https://example.com/"
                  action="Remove noindex or restrict to staging"
                />
                <Finding
                  title="Homepage returning 503 (availability risk)"
                  url="https://example.com/"
                  action="Fix origin errors; confirm 200 on repeat run"
                />
              </div>
            </div>

            {/* Warning */}
            <div className="space-y-3">
              <SectionHeading label="Warning" dotColor="var(--color-warning)" />
              <div className="pl-4 space-y-3">
                <Finding
                  title="Canonical changed on /pricing"
                  url="https://example.com/pricing"
                  action="Confirm canonical target and update templates"
                />
                <Finding
                  title="Sitemap URL count dropped 18%"
                  url="https://example.com/sitemap.xml"
                  action="Verify missing URLs and unintended removals"
                />
                <Finding
                  title="Spike in 404 responses"
                  url="https://example.com/blog/some-removed-post"
                  action="Redirect or restore; validate via re-crawl"
                />
              </div>
            </div>

            {/* Info */}
            <div className="space-y-3">
              <SectionHeading label="Info" dotColor="var(--color-info)" />
              <div className="pl-4 space-y-3">
                <Finding
                  title="Title updated on /about"
                  url="https://example.com/about"
                  action="Verify change is intentional"
                />
                <Finding
                  title="Content hash changed on /services"
                  url="https://example.com/services"
                  action="Review copy/template change"
                />
                <Finding
                  title="New pages added to sitemap"
                  url="https://example.com/sitemap.xml"
                  action="Review for quality; ensure canonical is correct"
                />
                <Finding
                  title="Meta description changed on /pricing"
                  url="https://example.com/pricing"
                  action="Confirm intent and avoid truncation"
                />
              </div>
            </div>

            {/* PSI mini-block */}
            <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] p-4">
              <div className="text-sm font-semibold text-[var(--color-headline)]">PageSpeed Insights</div>
              <div className="mt-1 text-sm text-[var(--color-body)]">
                Performance regression confirmed <span className="font-medium text-[var(--color-headline)]">(2 runs)</span>
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                <Chip label="Perf -12" color="neutral" />
                <Chip label="LCP +650ms" color="neutral" />
              </div>
            </div>

            {/* Footer hint */}
            <div className="pt-2 border-t border-[var(--color-border)]">
              <div className="text-sm text-[var(--color-body)]">
                Set my report schedule (optional):{' '}
                <span className="text-[var(--color-primary)] font-medium">ranksentinel.com/schedule</span>
              </div>
            </div>
          </>
        )}

        {variant === 'teaser' && (
          <div className="pt-2 border-t border-[var(--color-border)]">
            <div className="text-sm text-[var(--color-body)]">
              There&apos;s more in the full sample report — see below.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
