'use client';

import { useState } from 'react';

interface Tab {
  id: string;
  label: string;
  bullets: string[];
  preview: string;
}

const tabs: Tab[] = [
  {
    id: 'daily-critical',
    label: 'Daily Critical Checks',
    bullets: [
      'Alerts only when severity is Critical',
      'Focused on key pages (high leverage)',
      'Designed for low false positives (dedupe + confirmation)',
    ],
    preview: 'Daily email sent only when critical SEO regressions are detected on your most important pages.',
  },
  {
    id: 'weekly-digest',
    label: 'Weekly Digest',
    bullets: [
      'Critical / Warning / Info grouped summaries',
      '"Top actions this week" prioritized list',
      'Stable diffs (normalized content) to reduce noise',
    ],
    preview: 'Comprehensive weekly summary with actionable recommendations ranked by priority.',
  },
  {
    id: 'seo-signals',
    label: 'SEO Signals',
    bullets: [
      'robots.txt change detection',
      'sitemap deltas (hash + URL count)',
      'canonical/noindex/title changes',
      'internal broken links + new 404s',
    ],
    preview: 'Monitor the signals that matter: robots rules, sitemaps, meta tags, and link integrity.',
  },
  {
    id: 'psi-monitoring',
    label: 'PSI Monitoring',
    bullets: [
      'PageSpeed Insights on key URLs',
      'Confirmation logic for regressions (avoid one-off blips)',
      'Track performance trends over time',
    ],
    preview: 'PageSpeed monitoring with smart confirmation to filter out temporary fluctuations.',
  },
];

export function FeatureTabs() {
  const [activeTab, setActiveTab] = useState(tabs[0].id);

  const activeTabData = tabs.find((tab) => tab.id === activeTab) || tabs[0];

  return (
    <div className="w-full">
      {/* Tab List */}
      <div
        role="tablist"
        aria-label="Feature categories"
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

              {/* Preview Snippet */}
              <div className="bg-[var(--color-bg-subtle)] border border-[var(--color-border)] rounded-lg p-6">
                <p className="text-[var(--color-body)] text-base italic">{tab.preview}</p>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
