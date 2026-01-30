import React from 'react';
import { Container, Button, Badge } from '../components';
import { generateMetadata as genMeta } from '../lib/metadata';

export const metadata = genMeta({
  title: 'Sample Report',
  description: 'See what a RankSentinel weekly SEO monitoring report looks like. Real insights delivered to your inbox.',
  path: '/sample-report',
});

export default function SampleReportPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <Container className="py-12 md:py-20">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
            Sample RankSentinel Weekly Digest
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto mb-8">
            See exactly what you'll receive every week. This example shows how RankSentinel detects critical SEO issues and site health problems.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button as="link" href="/#sample-report" variant="primary" size="lg">
              Get a sample report
            </Button>
            <Button as="link" href="/pricing" variant="secondary" size="lg">
              View pricing
            </Button>
          </div>
        </div>

        {/* Email Preview Container */}
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden">
          {/* Email Header */}
          <div className="bg-slate-50 border-b border-slate-200 p-6">
            <div className="text-sm text-slate-600 mb-2">
              <strong>Subject:</strong> RankSentinel Weekly Digest — ExampleCo
            </div>
            <div className="text-sm text-slate-600">
              <strong>To:</strong> seo@exampleco.com
            </div>
          </div>

          {/* Email Body */}
          <div className="p-8 md:p-12">
            {/* Executive Summary */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-slate-900 mb-4">
                Executive Summary
              </h2>
              <div className="flex flex-wrap gap-3 mb-4">
                <Badge variant="critical">2 Critical</Badge>
                <Badge variant="warning">3 Warnings</Badge>
                <Badge variant="info">6 Info</Badge>
              </div>
              <p className="text-slate-700 leading-relaxed">
                This report focuses on SEO regressions and high-signal site health issues. It avoids alert noise by normalizing page content and only escalating high-severity issues.
              </p>
            </section>

            <hr className="my-8 border-slate-200" />

            {/* Critical Issues */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-red-600 mb-6">Critical</h2>
              
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  1) Homepage is now <code className="bg-slate-100 px-2 py-1 rounded text-sm">noindex</code>
                </h3>
                <ul className="space-y-2 text-slate-700 mb-4">
                  <li><strong>URL:</strong> <code className="text-sm bg-slate-100 px-2 py-1 rounded">https://example.com/</code></li>
                  <li><strong>Detected:</strong> Meta robots changed from <code className="text-sm bg-slate-100 px-2 py-1 rounded">index,follow</code> → <code className="text-sm bg-slate-100 px-2 py-1 rounded">noindex,follow</code></li>
                  <li><strong>Why it matters:</strong> Your homepage may drop from search results.</li>
                </ul>
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                  <p className="text-sm font-semibold text-red-800 mb-2">Action Required</p>
                  <p className="text-sm text-red-700">Remove the noindex directive immediately to prevent deindexing.</p>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  2) Robots.txt now blocks critical crawl paths
                </h3>
                <ul className="space-y-2 text-slate-700 mb-4">
                  <li><strong>Detected:</strong> New rule added: <code className="text-sm bg-slate-100 px-2 py-1 rounded">Disallow: /blog/</code></li>
                  <li><strong>Why it matters:</strong> Google cannot crawl your blog content (200+ pages).</li>
                </ul>
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                  <p className="text-sm font-semibold text-red-800 mb-2">Action Required</p>
                  <p className="text-sm text-red-700">Audit your robots.txt deployment and remove the /blog/ disallow rule.</p>
                </div>
              </div>
            </section>

            <hr className="my-8 border-slate-200" />

            {/* Warnings */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-amber-600 mb-6">Warnings</h2>
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  1) Sitemap URL count dropped by 45%
                </h3>
                <ul className="space-y-2 text-slate-700 text-sm">
                  <li><strong>Previous count:</strong> 850 URLs</li>
                  <li><strong>Current count:</strong> 468 URLs</li>
                  <li><strong>Why it matters:</strong> Missing pages may not be crawled efficiently.</li>
                </ul>
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  2) New 404s detected on high-traffic pages
                </h3>
                <ul className="space-y-2 text-slate-700 text-sm">
                  <li><strong>URLs:</strong> 3 pages now returning 404</li>
                  <li><strong>Examples:</strong> <code className="text-xs bg-slate-100 px-2 py-1 rounded">/pricing-old</code>, <code className="text-xs bg-slate-100 px-2 py-1 rounded">/contact-us</code></li>
                  <li><strong>Why it matters:</strong> Broken links hurt UX and may lose backlink equity.</li>
                </ul>
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  3) Canonical tag changes on product pages
                </h3>
                <ul className="space-y-2 text-slate-700 text-sm">
                  <li><strong>Affected:</strong> 12 product pages</li>
                  <li><strong>Why it matters:</strong> Unintended canonical changes can dilute ranking signals.</li>
                </ul>
              </div>
            </section>

            <hr className="my-8 border-slate-200" />

            {/* Info */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-blue-600 mb-6">Info</h2>
              
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  1) Minor content changes detected
                </h3>
                <p className="text-slate-700 text-sm">
                  <strong>Detected:</strong> Non-structural content edits on several pages.<br />
                  <strong>Action:</strong> No action needed unless edits were unplanned.
                </p>
              </div>
            </section>

            <hr className="my-8 border-slate-200" />

            {/* Recommendations */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">
                Recommendations (Next 7 Days)
              </h2>
              <ol className="list-decimal list-inside space-y-3 text-slate-700">
                <li><strong>Fix homepage noindex</strong> and redeploy.</li>
                <li><strong>Audit robots.txt</strong> changes and confirm crawl rules.</li>
                <li><strong>Investigate sitemap URL drop</strong> (compare current vs last-known-good export).</li>
                <li><strong>Add redirects</strong> for new 404s affecting organic traffic.</li>
              </ol>
            </section>

            <hr className="my-8 border-slate-200" />

            {/* Report Metadata */}
            <section className="text-sm text-slate-500">
              <p><strong>Generated:</strong> 2026-01-29 18:15:00</p>
              <p><strong>Report type:</strong> Weekly digest</p>
            </section>
          </div>

          {/* Footer CTA */}
          <div className="bg-slate-50 border-t border-slate-200 p-8 text-center">
            <h3 className="text-xl font-semibold text-slate-900 mb-3">
              Ready to protect your SEO rankings?
            </h3>
            <p className="text-slate-600 mb-6 max-w-2xl mx-auto">
              Get weekly digests like this delivered to your inbox. Start monitoring your site today.
            </p>
            <Button as="link" href="/#sample-report" variant="primary" size="lg">
              Get a sample report
            </Button>
          </div>
        </div>

        {/* Bottom CTA Section */}
        <div className="text-center mt-12">
          <p className="text-slate-600 mb-4">
            Want to see how this works for your site?
          </p>
          <Button as="link" href="/pricing" variant="secondary" size="lg">
            View pricing plans
          </Button>
        </div>
      </Container>
    </div>
  );
}
