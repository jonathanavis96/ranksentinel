import React from 'react';

interface EmailReportPreviewProps {
  className?: string;
}

export default function EmailReportPreview({ className = '' }: EmailReportPreviewProps) {
  return (
    <div 
      className={`bg-white rounded-lg border border-zinc-200 shadow-sm overflow-hidden ${className}`}
      role="article"
      aria-label="Sample weekly email report"
    >
      {/* Email Header */}
      <div className="border-b border-zinc-200 bg-zinc-50 px-6 py-4">
        <div className="text-sm text-zinc-600 mb-1">Subject:</div>
        <div className="font-semibold text-zinc-900">
          Weekly SEO Regression Digest — example.com
        </div>
      </div>

      {/* Email Body */}
      <div className="px-6 py-6 space-y-6">
        {/* Executive Summary */}
        <div className="text-sm text-zinc-600">
          <span className="font-semibold text-red-700">2 Critical</span>
          {' • '}
          <span className="font-semibold text-orange-700">3 Warnings</span>
          {' • '}
          <span className="font-semibold text-blue-700">6 Info</span>
        </div>

        {/* Critical Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1 h-5 bg-red-600 rounded-full" aria-hidden="true"></div>
            <h3 className="font-semibold text-zinc-900">Critical</h3>
          </div>
          <div className="space-y-3 pl-4">
            <div className="text-sm">
              <div className="font-medium text-zinc-900">Homepage is now noindex</div>
              <div className="text-zinc-600 mt-1">
                Meta robots changed — your homepage may drop from search results
              </div>
            </div>
            <div className="text-sm">
              <div className="font-medium text-zinc-900">Robots.txt now blocks key section</div>
              <div className="text-zinc-600 mt-1">
                /blog/ disallowed — pages may stop being crawled
              </div>
            </div>
          </div>
        </div>

        {/* Warning Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1 h-5 bg-orange-600 rounded-full" aria-hidden="true"></div>
            <h3 className="font-semibold text-zinc-900">Warning</h3>
          </div>
          <div className="space-y-3 pl-4">
            <div className="text-sm">
              <div className="font-medium text-zinc-900">Sitemap URL count dropped 18%</div>
              <div className="text-zinc-600 mt-1">
                Indicates potential URL removal or canonical changes
              </div>
            </div>
            <div className="text-sm">
              <div className="font-medium text-zinc-900">Spike in 404 responses</div>
              <div className="text-zinc-600 mt-1">
                404 rate increased on previously indexed URLs
              </div>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1 h-5 bg-blue-600 rounded-full" aria-hidden="true"></div>
            <h3 className="font-semibold text-zinc-900">Info</h3>
          </div>
          <div className="space-y-3 pl-4">
            <div className="text-sm">
              <div className="font-medium text-zinc-900">Title changed on /pricing</div>
              <div className="text-zinc-600 mt-1">
                Template update detected — verify intentional
              </div>
            </div>
            <div className="text-sm">
              <div className="font-medium text-zinc-900">New pages added to sitemap</div>
              <div className="text-zinc-600 mt-1">
                12 new URLs published this week
              </div>
            </div>
          </div>
        </div>

        {/* Top Actions */}
        <div className="pt-4 border-t border-zinc-200">
          <h3 className="font-semibold text-zinc-900 mb-3">Top 3 actions this week</h3>
          <ul className="space-y-2 text-sm text-zinc-700 list-decimal list-inside">
            <li>Remove noindex from homepage or scope to staging only</li>
            <li>Review robots.txt and restore /blog/ crawlability</li>
            <li>Investigate sitemap URL count drop and restore missing pages</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
