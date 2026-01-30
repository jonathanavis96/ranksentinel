import React from 'react';
import { Container, Button, Badge, EmailReportPreview, Footer, Header } from '../components';
import { generateMetadata as genMeta } from '../lib/metadata';

export const metadata = genMeta({
  title: 'Sample Report',
  description: 'See what a RankSentinel weekly SEO monitoring report looks like. Real insights delivered to your inbox.',
  path: '/sample-report',
});

export default function SampleReportPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Header />

      <main id="main-content" className="flex-1">
        <section id="top" className="pt-20 pb-12 md:pt-28 md:pb-16">
          <Container size="lg">
            <div className="text-center space-y-6">
              <Badge>Sample weekly digest</Badge>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-[var(--color-headline)]">
                A real RankSentinel report, delivered by email
              </h1>
              <p className="text-lg md:text-xl text-[var(--color-body)] max-w-3xl mx-auto">
                This is what you receive every week: critical issues first, then warnings and informational changes, plus a short prioritized action list.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-2">
                <Button
                  as="link"
                  href="/start"
                  variant="primary"
                  size="lg"
                  analyticsEventName="cta_start_monitoring_click"
                  analyticsEventProperties={{ location: 'sample_report_hero' }}
                >
                  Start monitoring
                </Button>
                <Button as="link" href="/pricing" variant="secondary" size="lg">
                  See pricing
                </Button>
              </div>
            </div>
          </Container>
        </section>

        {/* Signature preview object (calm email-style card) */}
        <section className="pb-16">
          <Container size="lg">
            <EmailReportPreview className="max-w-3xl mx-auto" />
          </Container>
        </section>

        {/* CTA after preview */}
        <section className="py-16 bg-white border-y border-[var(--color-border)]">
          <Container size="lg">
            <div className="text-center">
              <p className="text-[var(--color-body)] mb-4">Want this report for your site?</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button
                  as="link"
                  href="/start"
                  variant="primary"
                  size="lg"
                  analyticsEventName="cta_start_monitoring_click"
                  analyticsEventProperties={{ location: 'sample_report_bottom_cta' }}
                >
                  Start monitoring
                </Button>
                <Button as="link" href="/pricing" variant="secondary" size="lg">
                  See pricing
                </Button>
              </div>
            </div>
          </Container>
        </section>
      </main>

      <Footer />
    </div>
  );
}
