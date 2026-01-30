'use client';

import { useState } from 'react';

interface Tab {
  id: string;
  label: string;
  bullets: string[];
  microProof: string;
  example: string;
}

const tabs: Tab[] = [
  {
    id: 'what-you-get',
    label: 'What you get',
    bullets: [
      'Weekly digest with Top 3 priorities (so you know what to do first)',
      'Daily email only when something is genuinely Critical',
      'Emails are forwardable (share with dev/PM without rewriting the issue)',
    ],
    microProof: 'Daily alerts are gated by severity and sent only after confirmation logic (so you don\'t get paged for blips).',
    example: '“This week’s priorities: Fix homepage noindex • Restore robots crawlability • Investigate LCP regression”',
  },
  {
    id: 'noise-prevention',
    label: 'Noise prevention',
    bullets: [
      'Normalization + dedupe reduce template-change spam',
      'Confirmation runs filter one-off fetch/infra errors',
      'Focused scope (key pages) keeps signal high',
    ],
    microProof: 'If something changes once, it’s tracked; if it repeats and impacts SEO, it becomes a prioritized item (or a critical alert).',
    example: '“Confirmed regression (2 runs): LCP +650ms on /pricing”',
  },
  {
    id: 'what-we-monitor',
    label: 'What we monitor',
    bullets: [
      'Indexability: meta robots (noindex/nofollow) and canonical changes',
      'Crawl control: robots.txt + sitemap changes (adds/removals/count shifts)',
      'Site integrity: internal link issues + spikes in 404s',
      'Performance: key-page PSI regressions (tracked as regressions, not vanity scores)',
    ],
    microProof: 'Coverage is opinionated: it prioritizes signals that commonly precede traffic drops—then groups them by severity.',
    example: '“Critical: Homepage set to noindex • Warning: Sitemap URL count dropped 18%”',
  },
  {
    id: 'setup-scope',
    label: 'Setup & scope',
    bullets: [
      'Add your domain + email (minutes)',
      'Choose your key pages (homepage, pricing, top landing pages)',
      'Set weekly schedule (optional) and let it run',
    ],
    microProof: 'Monitoring starts with a baseline snapshot so future diffs are meaningful (not noisy).',
    example: '“Baseline established → Next digest includes only confirmed changes since last week”',
  },
];

export function FeatureTabs() {
  const [activeTab, setActiveTab] = useState(tabs[0].id);

  return (
    <div className="w-full">
      {/* Tab List */}
      <div
        role="tablist"
        aria-label="Product coverage"
        className="flex flex-wrap gap-2 mb-8 border-b border-[var(--color-border)]"
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(e) => {
              const currentIndex = tabs.findIndex((t) => t.id === activeTab);
              let newIndex = currentIndex;

              if (e.key === 'ArrowRight') {
                newIndex = (currentIndex + 1) % tabs.length;
                e.preventDefault();
              } else if (e.key === 'ArrowLeft') {
                newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
                e.preventDefault();
              } else if (e.key === 'Home') {
                newIndex = 0;
                e.preventDefault();
              } else if (e.key === 'End') {
                newIndex = tabs.length - 1;
                e.preventDefault();
              }

              if (newIndex !== currentIndex) {
                setActiveTab(tabs[newIndex].id);
                document.getElementById(`tab-${tabs[newIndex].id}`)?.focus();
              }
            }}
            className={`
              px-6 py-3 text-base font-medium transition-colors
              border-b-2 -mb-px
              focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2
              ${
                activeTab === tab.id
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-body)] hover:text-[var(--color-headline)] hover:border-[var(--color-border-strong)]'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      {tabs.map((tab) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
          tabIndex={0}
          className="focus:outline-none"
        >
          {activeTab === tab.id && (
            <div className="space-y-6">
              {/* Bullets */}
              <ul className="space-y-3">
                {tab.bullets.map((bullet, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="text-[var(--color-primary)] mt-1 text-lg">✓</span>
                    <span className="text-[var(--color-body)] text-base">{bullet}</span>
                  </li>
                ))}
              </ul>

              {/* Micro-proof + example */}
              <div className="bg-[var(--color-bg-subtle)] border border-[var(--color-border)] rounded-lg p-6 space-y-4">
                <div>
                  <div className="text-sm font-semibold text-[var(--color-headline)]">Micro-proof</div>
                  <p className="text-[var(--color-body)] text-base">{tab.microProof}</p>
                </div>
                <div>
                  <div className="text-sm font-semibold text-[var(--color-headline)]">Example</div>
                  <p className="text-[var(--color-body)] text-base italic">{tab.example}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
