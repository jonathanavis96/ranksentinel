import React from 'react';
import Container from '../components/Container';
import Header from '../components/Header';
import { generateMetadata as genMeta } from '../lib/metadata';

export const metadata = genMeta({
  title: 'Privacy Policy',
  description: 'RankSentinel Privacy Policy - How we collect, use, and protect your data.',
  path: '/privacy',
});

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header />
      <main id="main-content" className="flex-1">
        <Container>
        <div className="py-16 max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold text-[var(--color-headline)] mb-8">
            Privacy Policy
          </h1>
          
          <div className="prose prose-lg text-[var(--color-body)] space-y-6">
            <p className="text-sm text-[var(--color-body-secondary)]">
              <strong>Effective Date:</strong> January 30, 2025
            </p>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                1. Information We Collect
              </h2>
              <p>
                RankSentinel collects information necessary to provide SEO monitoring services:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Account Information:</strong> Email address, domain name, and optional payment details.</li>
                <li><strong>Website Data:</strong> Public website content, sitemaps, robots.txt files, and page metadata accessed via standard HTTP requests.</li>
                <li><strong>Usage Data:</strong> Service interactions, email opens, and link clicks for service improvement.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                2. How We Use Your Information
              </h2>
              <p>We use collected information to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Monitor your website for SEO regressions and changes</li>
                <li>Deliver weekly digest reports via email</li>
                <li>Communicate service updates and recommendations</li>
                <li>Process payments and maintain account records</li>
                <li>Improve our monitoring algorithms and service quality</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                3. Data Sharing and Disclosure
              </h2>
              <p>
                RankSentinel does not sell your personal information. We may share data only in these cases:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Service Providers:</strong> Third-party vendors (email delivery, payment processing) under strict confidentiality agreements.</li>
                <li><strong>Legal Requirements:</strong> When required by law, regulation, or legal process.</li>
                <li><strong>Business Transfers:</strong> In the event of a merger, acquisition, or sale of assets.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                4. Data Security
              </h2>
              <p>
                We implement industry-standard security measures to protect your data, including encryption in transit and at rest, secure server infrastructure, and regular security audits. However, no system is completely secure, and we cannot guarantee absolute security.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                5. Data Retention
              </h2>
              <p>
                We retain your data for as long as your account is active or as needed to provide services. Historical monitoring data is retained to enable trend analysis and regression detection. You may request data deletion by contacting us.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                6. Your Rights
              </h2>
              <p>You have the right to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Access and review your personal information</li>
                <li>Request correction of inaccurate data</li>
                <li>Request deletion of your data (subject to legal obligations)</li>
                <li>Opt out of marketing communications</li>
                <li>Export your data in a portable format</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                7. Cookies and Tracking
              </h2>
              <p>
                RankSentinel uses minimal cookies for essential functionality (session management, authentication). We do not use third-party advertising cookies or cross-site tracking.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                8. International Data Transfers
              </h2>
              <p>
                Your data may be processed in countries outside your residence. We ensure appropriate safeguards are in place for international transfers in compliance with applicable data protection laws.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                9. Children&apos;s Privacy
              </h2>
              <p>
                RankSentinel is not intended for users under 18. We do not knowingly collect information from children.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                10. Changes to This Policy
              </h2>
              <p>
                We may update this Privacy Policy periodically. Material changes will be communicated via email or prominent notice on our website. Continued use after changes constitutes acceptance.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                Contact Us
              </h2>
              <p>
                For privacy-related questions or to exercise your rights, contact us at:
              </p>
              <p className="mt-2">
                <strong>Email:</strong> privacy@ranksentinel.com
              </p>
            </section>
          </div>
        </div>
        </Container>
      </main>
    </div>
  );
}
