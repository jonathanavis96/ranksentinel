import React from 'react';
import Container from '../components/Container';
import Button from '../components/Button';
import Card from '../components/Card';
import { FAQAccordion } from '../components/FAQAccordion';
import { generateMetadata as genMeta } from '../lib/metadata';

export const metadata = genMeta({
  title: 'Pricing',
  description: 'Simple, transparent pricing for RankSentinel. Start free, upgrade when you need more monitoring coverage.',
  path: '/pricing',
});

interface PricingTier {
  name: string;
  price: string;
  bestFor: string;
  features: string[];
  highlighted?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    name: 'Starter',
    price: '$29',
    bestFor: '1 small site',
    features: [
      '1 site',
      'Up to 50 pages monitored',
      'Up to 10 key pages',
      'Up to 3 recipients',
    ],
  },
  {
    name: 'Growth',
    price: '$69',
    bestFor: 'Multiple sites or bigger footprint',
    features: [
      'Up to 3 sites',
      'Up to 200 pages monitored',
      'Up to 25 key pages',
      'Up to 10 recipients',
    ],
    highlighted: true,
  },
  {
    name: 'Agency',
    price: '$199',
    bestFor: 'Agencies + multi-site portfolios',
    features: [
      'Up to 10 sites',
      'Up to 2,000 pages monitored',
      'Up to 100 key pages',
      'Up to 25 recipients',
      'Priority onboarding',
    ],
  },
];

const allPlanFeatures = [
  'Weekly SEO regression digest (Critical / Warning / Info)',
  'Daily critical alerts (only when severity is Critical)',
  'Key-page monitoring (status, redirects, title, canonical, noindex, normalized content)',
  'Sitemap-aware weekly sampling (capped)',
  'Action-first recommendations (top priorities)',
];

const pricingFAQs = [
  {
    id: 'crawl-frequency',
    question: 'Do you crawl my entire site every day?',
    answer:
      'No. Daily monitoring is focused on your key pages. The weekly digest includes a capped sitemap sample crawl.',
  },
  {
    id: 'alert-spam',
    question: 'Will I get spammed with alerts?',
    answer:
      'No. RankSentinel only sends daily emails when findings are Critical.',
  },
  {
    id: 'add-site',
    question: 'Can I add another site later?',
    answer: 'Yes — upgrade to Growth or Agency.',
  },
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-[var(--color-background)]">
      {/* Hero Section */}
      <section id="top" className="py-16 md:py-24">
        <Container size="lg">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold text-[var(--color-headline)] mb-6">
              Pricing that scales with your site — without noisy alerts.
            </h1>
            <p className="text-lg md:text-xl text-[var(--color-body)] mb-8">
              Start small and upgrade when your monitoring footprint grows.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button as="link" href="/sample-report" size="lg" variant="primary">
                Get a sample report
              </Button>
              <Button
                as="link"
                href="#plans"
                size="lg"
                variant="secondary"
              >
                See pricing
              </Button>
            </div>
          </div>
        </Container>
      </section>

      {/* What You Get Section */}
      <section id="what-you-get" className="py-16 bg-white">
        <Container size="lg">
          <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] text-center mb-12">
            What you get (all plans)
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {allPlanFeatures.map((feature, index) => (
              <Card key={index} padding="md" className="text-center">
                <p className="text-[var(--color-body)]">{feature}</p>
              </Card>
            ))}
          </div>
        </Container>
      </section>

      {/* Pricing Plans Section */}
      <section id="plans" className="py-16 md:py-24">
        <Container size="lg">
          <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] text-center mb-12">
            Plans
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {pricingTiers.map((tier) => (
              <Card
                key={tier.name}
                padding="lg"
                className={`flex flex-col ${
                  tier.highlighted
                    ? 'border-2 border-[var(--color-primary)] shadow-lg'
                    : ''
                }`}
              >
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-[var(--color-headline)] mb-2">
                    {tier.name}
                  </h3>
                  <div className="mb-2">
                    <span className="text-4xl font-bold text-[var(--color-primary)]">
                      {tier.price}
                    </span>
                    <span className="text-[var(--color-body)]">/mo</span>
                  </div>
                  <p className="text-sm text-[var(--color-body)]">
                    Best for: {tier.bestFor}
                  </p>
                </div>
                <ul className="space-y-3 mb-8 flex-grow">
                  {tier.features.map((feature, index) => (
                    <li
                      key={index}
                      className="flex items-start text-[var(--color-body)]"
                    >
                      <svg
                        className="w-5 h-5 text-[var(--color-primary)] mr-2 mt-0.5 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  as="link"
                  href="https://api.ranksentinel.com/signup"
                  size="lg"
                  variant={tier.highlighted ? 'primary' : 'secondary'}
                  className="w-full"
                >
                  Start monitoring
                </Button>
              </Card>
            ))}
          </div>
        </Container>
      </section>

      {/* Upgrade Triggers Section */}
      <section id="upgrade-triggers" className="py-16 bg-white">
        <Container size="lg">
          <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] text-center mb-8">
            Upgrade when:
          </h2>
          <div className="max-w-2xl mx-auto">
            <ul className="space-y-4">
              <li className="flex items-start text-lg text-[var(--color-body)]">
                <svg
                  className="w-6 h-6 text-[var(--color-primary)] mr-3 mt-1 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
                <span>You need more <strong>key pages</strong> (daily monitoring + PSI)</span>
              </li>
              <li className="flex items-start text-lg text-[var(--color-body)]">
                <svg
                  className="w-6 h-6 text-[var(--color-primary)] mr-3 mt-1 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
                <span>You want a larger <strong>weekly sample crawl</strong></span>
              </li>
              <li className="flex items-start text-lg text-[var(--color-body)]">
                <svg
                  className="w-6 h-6 text-[var(--color-primary)] mr-3 mt-1 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
                <span>You&apos;re monitoring <strong>multiple sites</strong></span>
              </li>
            </ul>
          </div>
        </Container>
      </section>

      {/* Pages Monitored Explanation */}
      <section id="pages-monitored" className="py-16">
        <Container size="lg">
          <Card padding="lg" className="max-w-3xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold text-[var(--color-headline)] text-center mb-6">
              What &quot;pages monitored&quot; means
            </h2>
            <p className="text-[var(--color-body)] mb-4">
              RankSentinel&apos;s MVP crawl model is:
            </p>
            <ul className="space-y-2 mb-6">
              <li className="flex items-start text-[var(--color-body)]">
                <span className="font-semibold mr-2">Daily:</span>
                <span>key pages only</span>
              </li>
              <li className="flex items-start text-[var(--color-body)]">
                <span className="font-semibold mr-2">Weekly:</span>
                <span>sitemap sample crawl (capped)</span>
              </li>
            </ul>
            <div className="bg-[var(--color-background)] p-4 rounded-lg">
              <p className="text-[var(--color-body)] text-center">
                <strong>Total pages monitored</strong> = key pages (daily) + weekly sampled pages (weekly cap)
              </p>
            </div>
          </Card>
        </Container>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-16 bg-white">
        <Container size="lg">
          <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] text-center mb-12">
            Pricing FAQ
          </h2>
          <div className="max-w-3xl mx-auto">
            <FAQAccordion items={pricingFAQs} />
          </div>
        </Container>
      </section>

      {/* Final CTA */}
      <section className="py-16 md:py-24">
        <Container size="lg">
          <Card padding="lg" className="text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] mb-4">
              Ready to start monitoring?
            </h2>
            <p className="text-lg text-[var(--color-body)] mb-8 max-w-2xl mx-auto">
              Choose a plan and get your first weekly digest in days.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button as="link" href="https://api.ranksentinel.com/signup" size="lg" variant="primary">
                Start monitoring
              </Button>
              <Button as="link" href="/sample-report" size="lg" variant="secondary">
                See a sample report
              </Button>
            </div>
          </Card>
        </Container>
      </section>
    </main>
  );
}
