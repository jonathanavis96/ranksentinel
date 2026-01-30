import React from 'react';
import Container from '../components/Container';
import { generateMetadata as genMeta } from '../lib/metadata';

export const metadata = genMeta({
  title: 'Terms of Service',
  description: 'RankSentinel Terms of Service - User agreement and service conditions.',
  path: '/terms',
});

export default function TermsPage() {
  return (
    <main id="main-content" className="min-h-screen bg-white">
      <Container>
        <div className="py-16 max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold text-[var(--color-headline)] mb-8">
            Terms of Service
          </h1>
          
          <div className="prose prose-lg text-[var(--color-body)] space-y-6">
            <p className="text-sm text-[var(--color-body-secondary)]">
              <strong>Effective Date:</strong> January 30, 2025
            </p>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                1. Acceptance of Terms
              </h2>
              <p>
                By accessing or using RankSentinel ("the Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, do not use the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                2. Service Description
              </h2>
              <p>
                RankSentinel provides automated SEO monitoring services that:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Monitor your website for technical SEO issues and regressions</li>
                <li>Track changes to sitemaps, robots.txt, and page metadata</li>
                <li>Deliver weekly digest reports via email</li>
                <li>Provide severity-scored findings and recommendations</li>
              </ul>
              <p className="mt-4">
                The Service accesses only publicly available information via standard HTTP requests, respecting robots.txt and standard web protocols.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                3. User Accounts and Responsibilities
              </h2>
              <p>
                <strong>Account Creation:</strong> You must provide accurate, current information and maintain the security of your account credentials.
              </p>
              <p className="mt-4">
                <strong>Acceptable Use:</strong> You agree to use the Service only for lawful purposes and in accordance with these Terms. You must not:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Monitor websites you do not own or have authorization to monitor</li>
                <li>Attempt to circumvent service limitations or access restrictions</li>
                <li>Use the Service to transmit malicious code or spam</li>
                <li>Reverse engineer, decompile, or attempt to extract source code</li>
                <li>Resell or redistribute the Service without permission</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                4. Subscription and Payment
              </h2>
              <p>
                <strong>Billing:</strong> Subscriptions are billed in advance on a recurring basis (weekly, monthly, or annually). You authorize us to charge your payment method for applicable fees.
              </p>
              <p className="mt-4">
                <strong>Refunds:</strong> Refunds are provided at our discretion for unused service periods. No refunds for partial weeks or months.
              </p>
              <p className="mt-4">
                <strong>Cancellation:</strong> You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period.
              </p>
              <p className="mt-4">
                <strong>Price Changes:</strong> We reserve the right to modify pricing with 30 days' advance notice. Continued use after price changes constitutes acceptance.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                5. Service Limitations and Availability
              </h2>
              <p>
                <strong>Best Effort:</strong> We strive for high availability but do not guarantee uninterrupted or error-free service. Scheduled maintenance may occur with advance notice.
              </p>
              <p className="mt-4">
                <strong>Rate Limits:</strong> The Service may enforce rate limits on monitoring frequency and scope based on your subscription tier.
              </p>
              <p className="mt-4">
                <strong>Data Accuracy:</strong> While we aim for accurate monitoring, we do not guarantee completeness or real-time detection of all SEO issues. The Service is a monitoring tool, not a guarantee of SEO performance.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                6. Intellectual Property
              </h2>
              <p>
                <strong>Service IP:</strong> RankSentinel, its algorithms, software, and documentation are proprietary and protected by intellectual property laws. You receive a limited, non-exclusive, non-transferable license to use the Service.
              </p>
              <p className="mt-4">
                <strong>Your Data:</strong> You retain ownership of your website data. By using the Service, you grant us a limited license to access, process, and store your data solely to provide the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                7. Disclaimer of Warranties
              </h2>
              <p>
                THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL MEET YOUR REQUIREMENTS OR THAT IT WILL BE UNINTERRUPTED, TIMELY, SECURE, OR ERROR-FREE.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                8. Limitation of Liability
              </h2>
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, RANKSENTINEL SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, REVENUE, DATA, OR BUSINESS OPPORTUNITIES ARISING FROM YOUR USE OF THE SERVICE. OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID FOR THE SERVICE IN THE 12 MONTHS PRECEDING THE CLAIM.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                9. Indemnification
              </h2>
              <p>
                You agree to indemnify and hold harmless RankSentinel from any claims, damages, losses, or expenses (including legal fees) arising from your use of the Service, violation of these Terms, or infringement of third-party rights.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                10. Termination
              </h2>
              <p>
                We may suspend or terminate your access to the Service at any time for violation of these Terms, fraudulent activity, or any reason with notice. Upon termination, your right to use the Service ceases immediately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                11. Governing Law and Disputes
              </h2>
              <p>
                These Terms are governed by the laws of [Jurisdiction]. Any disputes shall be resolved through binding arbitration in accordance with [Arbitration Rules], except for small claims court matters.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                12. Changes to Terms
              </h2>
              <p>
                We may modify these Terms at any time. Material changes will be communicated via email or prominent notice on our website at least 30 days before taking effect. Continued use after changes constitutes acceptance.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                13. Miscellaneous
              </h2>
              <p>
                <strong>Entire Agreement:</strong> These Terms constitute the entire agreement between you and RankSentinel regarding the Service.
              </p>
              <p className="mt-4">
                <strong>Severability:</strong> If any provision is found unenforceable, the remaining provisions remain in effect.
              </p>
              <p className="mt-4">
                <strong>No Waiver:</strong> Failure to enforce any provision does not constitute a waiver of that provision.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-[var(--color-headline)] mt-8 mb-4">
                Contact Us
              </h2>
              <p>
                For questions about these Terms, contact us at:
              </p>
              <p className="mt-2">
                <strong>Email:</strong> legal@ranksentinel.com
              </p>
            </section>
          </div>
        </div>
      </Container>
    </main>
  );
}
