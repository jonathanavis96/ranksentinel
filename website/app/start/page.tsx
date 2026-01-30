import React from 'react';
import Container from '../components/Container';
import Header from '../components/Header';
import Footer from '../components/Footer';
import LeadCaptureForm from '../components/LeadCaptureForm';
import { generateMetadata as genMeta } from '../lib/metadata';

export const metadata = genMeta({
  title: 'Start Monitoring',
  description: 'Start monitoring your site for SEO issues. Get weekly digests and critical-only daily alerts.',
  path: '/start',
});

export default function StartPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Header />
      <main id="main-content" className="flex-1">
        <section className="py-16 md:py-24">
          <Container size="md">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold text-[var(--color-headline)] mb-6">
                Start Monitoring Your Site
              </h1>
              <p className="text-lg md:text-xl text-[var(--color-body)] max-w-2xl mx-auto">
                Enter your details below and we&apos;ll start monitoring your site for SEO issues. No credit card required.
              </p>
            </div>

            <div className="max-w-xl mx-auto bg-white border border-[var(--color-border)] rounded-2xl p-8" style={{ boxShadow: '0 4px 12px rgba(16, 24, 40, 0.08)' }}>
              <LeadCaptureForm />
            </div>

            <div className="mt-12 text-center">
              <h2 className="text-2xl font-bold text-[var(--color-headline)] mb-6">What happens next?</h2>
              <div className="grid md:grid-cols-3 gap-8 max-w-3xl mx-auto">
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center text-white font-semibold" style={{ background: 'var(--color-primary)' }}>
                    1
                  </div>
                  <h3 className="font-semibold text-[var(--color-headline)] mb-2">We set up monitoring</h3>
                  <p className="text-sm text-[var(--color-body)]">Your site will be added to our monitoring queue</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center text-white font-semibold" style={{ background: 'var(--color-primary)' }}>
                    2
                  </div>
                  <h3 className="font-semibold text-[var(--color-headline)] mb-2">First scan runs</h3>
                  <p className="text-sm text-[var(--color-body)]">We establish a baseline of your site&apos;s SEO health</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center text-white font-semibold" style={{ background: 'var(--color-primary)' }}>
                    3
                  </div>
                  <h3 className="font-semibold text-[var(--color-headline)] mb-2">You get your first report</h3>
                  <p className="text-sm text-[var(--color-body)]">Weekly digest delivered to your inbox</p>
                </div>
              </div>
            </div>
          </Container>
        </section>
      </main>
      <Footer />
    </div>
  );
}
