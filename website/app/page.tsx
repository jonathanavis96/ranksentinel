import React from 'react';
import Image from 'next/image';
import { Button, Container, EmailReportPreview, FAQAccordion, FeatureTabs, Footer, Header } from './components';

export default function Home() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Header />

      <main id="main-content" className="flex-1">
        {/* 0) Hero (#top) — center-stacked, massive headline */}
        <section id="top" className="pt-24 pb-12 md:pt-32 md:pb-16" style={{ background: 'radial-gradient(ellipse 100% 80% at 50% 0%, #E6FFFB 0%, rgba(230, 255, 251, 0.4) 40%, #F7FAFC 70%)' }}>
          <Container size="xl">
            <div className="text-center space-y-8">
              {/* Category badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[var(--color-border)] bg-white/80" style={{ boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)' }}>
                <span className="inline-flex items-center justify-center w-2 h-2 rounded-full bg-[var(--color-primary)]" aria-hidden="true"></span>
                <span className="text-sm font-medium text-[var(--color-headline)]">Low-noise SEO monitoring</span>
              </div>

              {/* Massive headline with inline logo icon */}
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-[var(--color-headline)] max-w-5xl mx-auto leading-tight flex flex-wrap items-center justify-center gap-3">
                <span>Catch SEO Issues</span>
                <Image
                  src="/ranksentinel-logo-icon.webp"
                  alt=""
                  width={32}
                  height={32}
                  className="inline-block h-[1em] w-auto"
                  style={{ filter: 'drop-shadow(0 8px 24px rgba(15, 118, 110, 0.4))' }}
                  aria-hidden="true"
                />
                <span>Before Traffic Drops</span>
              </h1>

              {/* Subhead */}
              <p className="text-lg md:text-xl text-[var(--color-body)] max-w-3xl mx-auto">
                Get weekly email reports that catch broken links, sitemap changes, and page speed drops before they hurt your rankings. Daily alerts only when it&apos;s critical.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
                <Button
                  as="link"
                  href="/start"
                  variant="primary"
                  size="lg"
                  className="rounded-full"
                  analyticsEventName="cta_start_monitoring_click"
                  analyticsEventProperties={{ location: 'home_hero' }}
                >
                  Start monitoring
                </Button>
                <Button as="link" href="/sample-report" variant="secondary" size="lg">
                  See sample report
                </Button>
              </div>

              {/* Trust line */}
              <p className="text-sm text-[var(--color-body)]">
                No credit card required. Start your first scan in minutes.
              </p>
            </div>
          </Container>
        </section>

        {/* 1) Why RankSentinel is different (#why-different) — Taskk-style cards moved up */}
        <section id="why-different" className="pt-6 pb-12 md:pt-8 md:pb-16">
          <Container size="xl">
            <div className="grid md:grid-cols-3 gap-6">
              {/* Card 1 */}
              <div 
                className="rounded-3xl border border-[var(--color-border)] p-8 relative overflow-hidden text-center"
                style={{ 
                  background: 'linear-gradient(135deg, rgba(230, 255, 251, 0.6) 0%, rgba(230, 255, 251, 0.2) 100%)',
                  boxShadow: '0 4px 12px rgba(15, 118, 110, 0.08)'
                }}
              >
                <div className="relative z-10 space-y-4">
                  {/* Image tile */}
                  <div className="px-2">
                    <div className="relative w-full aspect-[16/9] rounded-2xl overflow-hidden">
                      <Image
                        src="/critical-alerts-only.png"
                        alt=""
                        fill
                        sizes="(min-width: 768px) 33vw, 100vw"
                        className="object-contain"
                        aria-hidden="true"
                      />
                    </div>
                  </div>

                  {/* Number badge */}
                  <div className="inline-flex items-center justify-center w-10 h-10 rounded-full text-base font-semibold" style={{ background: 'rgba(15, 118, 110, 0.15)', color: 'var(--color-primary)' }}>
                    1
                  </div>

                  <h3 className="text-xl font-semibold text-[var(--color-headline)]">Critical-Only Alerts</h3>
                  <p className="text-[var(--color-body)] leading-relaxed">
                    Daily emails only when severity is Critical. Everything else waits for the weekly digest. No inbox spam.
                  </p>
                </div>
              </div>

              {/* Card 2 */}
              <div 
                className="rounded-3xl border border-[var(--color-border)] p-8 relative overflow-hidden text-center"
                style={{ 
                  background: 'linear-gradient(135deg, rgba(230, 246, 255, 0.6) 0%, rgba(230, 246, 255, 0.2) 100%)',
                  boxShadow: '0 4px 12px rgba(23, 92, 211, 0.08)'
                }}
              >
                <div className="relative z-10 space-y-4">
                  {/* Image tile */}
                  <div className="px-2">
                    <div className="relative w-full aspect-[16/9] rounded-2xl overflow-hidden">
                      <Image
                        src="/seo-specific-checks.png"
                        alt=""
                        fill
                        sizes="(min-width: 768px) 33vw, 100vw"
                        className="object-contain"
                        aria-hidden="true"
                      />
                    </div>
                  </div>

                  {/* Number badge */}
                  <div className="inline-flex items-center justify-center w-10 h-10 rounded-full text-base font-semibold" style={{ background: 'rgba(23, 92, 211, 0.15)', color: 'var(--color-info)' }}>
                    2
                  </div>

                  <h3 className="text-xl font-semibold text-[var(--color-headline)]">SEO-Specific Checks</h3>
                  <p className="text-[var(--color-body)] leading-relaxed">
                    Robots.txt, sitemaps, canonicals, noindex, broken links, and PageSpeed—tailored for rankings, not generic monitoring.
                  </p>
                </div>
              </div>

              {/* Card 3 */}
              <div 
                className="rounded-3xl border border-[var(--color-border)] p-8 relative overflow-hidden text-center"
                style={{ 
                  background: 'linear-gradient(135deg, rgba(254, 243, 199, 0.6) 0%, rgba(254, 243, 199, 0.2) 100%)',
                  boxShadow: '0 4px 12px rgba(181, 71, 8, 0.08)'
                }}
              >
                <div className="relative z-10 space-y-4">
                  {/* Image tile */}
                  <div className="px-2">
                    <div className="relative w-full aspect-[16/9] rounded-2xl overflow-hidden">
                      <Image
                        src="/prioritized-action-list.png"
                        alt=""
                        fill
                        sizes="(min-width: 768px) 33vw, 100vw"
                        className="object-contain"
                        aria-hidden="true"
                      />
                    </div>
                  </div>

                  {/* Number badge */}
                  <div className="inline-flex items-center justify-center w-10 h-10 rounded-full text-base font-semibold" style={{ background: 'rgba(181, 71, 8, 0.15)', color: 'var(--color-warning)' }}>
                    3
                  </div>

                  <h3 className="text-xl font-semibold text-[var(--color-headline)]">Prioritized Action List</h3>
                  <p className="text-[var(--color-body)] leading-relaxed">
                    Weekly digest groups findings by severity and shows you the Top 3 actions first. Scan in seconds.
                  </p>
                </div>
              </div>
            </div>
          </Container>
        </section>

        {/* 2) Sample report teaser (#sample-report) */}
        <section id="sample-report" className="py-16 md:py-20">
          <Container size="lg">
            <div className="text-center space-y-6">
              <h2 className="text-2xl md:text-3xl font-bold text-[var(--color-headline)]">See what you&apos;ll get every week</h2>
              <p className="text-[var(--color-body)] max-w-2xl mx-auto">
                A real weekly digest example showing how issues are surfaced and prioritized.
              </p>

              <div className="pt-8">
                <EmailReportPreview
                  variant="teaser"
                  className="max-w-3xl mx-auto"
                  style={{ boxShadow: '0 20px 60px rgba(15, 118, 110, 0.15)' }}
                />
              </div>

              <p className="text-[var(--color-body)] max-w-2xl mx-auto">
                See the full example digest, including the Top 3 priorities and confirmation language.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-2">
                <Button
                  as="link"
                  href="/sample-report"
                  variant="primary"
                  size="lg"
                  analyticsEventName="cta_see_sample_report_click"
                  analyticsEventProperties={{ location: 'home_sample_report_teaser' }}
                >
                  See sample report
                </Button>
                <Button as="link" href="/pricing" variant="secondary" size="lg">
                  See pricing
                </Button>
              </div>
            </div>
          </Container>
        </section>

        {/* 3) Social proof / credibility strip (#outcomes) */}
        <section id="outcomes" className="py-10 border-y border-[var(--color-border)] bg-white">
          <Container size="lg">
            <div className="grid md:grid-cols-3 gap-6 text-sm">
              <div className="flex items-start gap-3">
                <span className="mt-1 w-2.5 h-2.5 rounded-full" style={{ background: 'var(--color-primary)' }} aria-hidden="true" />
                <div>
                  <div className="font-medium text-[var(--color-headline)]">Built for founders, SEO leads, and agencies.</div>
                  <div className="text-[var(--color-body)]">Clear signal over noisy diffs.</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="mt-1 w-2.5 h-2.5 rounded-full" style={{ background: 'var(--color-primary)' }} aria-hidden="true" />
                <div>
                  <div className="font-medium text-[var(--color-headline)]">Email-first: no dashboard required.</div>
                  <div className="text-[var(--color-body)]">Forward it to your team in one click.</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="mt-1 w-2.5 h-2.5 rounded-full" style={{ background: 'var(--color-primary)' }} aria-hidden="true" />
                <div>
                  <div className="font-medium text-[var(--color-headline)]">Noise reduction built-in.</div>
                  <div className="text-[var(--color-body)]">Severity + confirmation + dedupe.</div>
                </div>
              </div>
            </div>
          </Container>
        </section>

        {/* 3) Product detail (#features) */}
        <section id="features" className="py-20 md:py-28 bg-white border-y border-[var(--color-border)]">
          <Container size="lg">
            <div className="text-center space-y-4 mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">Weekly clarity + critical-only alerts</h2>
              <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
                RankSentinel monitors the few changes that actually move rankings—then emails the actions to take. No dashboard. No spam.
              </p>
            </div>

            <FeatureTabs />

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-10">
              <Button
                as="link"
                href="/start"
                variant="primary"
                size="lg"
                analyticsEventName="cta_start_monitoring_click"
                analyticsEventProperties={{ location: 'home_product_section' }}
              >
                Start monitoring
              </Button>
              <Button
                as="link"
                href="/sample-report"
                variant="secondary"
                size="lg"
                analyticsEventName="cta_see_sample_report_click"
                analyticsEventProperties={{ location: 'home_product_section' }}
              >
                See sample report
              </Button>
            </div>
          </Container>
        </section>

        {/* 4) How it works (#how-it-works) */}
        <section id="how-it-works" className="pt-16 pb-10 md:pt-20 md:pb-14">
          <Container size="lg">
            <div className="text-center space-y-4 mb-10">
              <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">How it works</h2>
              <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
                Set it up once. Forget it. Update schedule anytime.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-10">
              <div className="text-center space-y-3">
                <div className="w-12 h-12 rounded-full mx-auto flex items-center justify-center text-white font-semibold" style={{ background: 'var(--color-primary)' }}>
                  1
                </div>
                <h3 className="text-lg font-semibold text-[var(--color-headline)]">Add your site</h3>
                <p className="text-[var(--color-body)]">Email + domain + optional key pages.</p>
              </div>
              <div className="text-center space-y-3">
                <div className="w-12 h-12 rounded-full mx-auto flex items-center justify-center text-white font-semibold" style={{ background: 'var(--color-primary)' }}>
                  2
                </div>
                <h3 className="text-lg font-semibold text-[var(--color-headline)]">We monitor 24/7</h3>
                <p className="text-[var(--color-body)]">Automated checks run daily + weekly. You just get the emails.</p>
              </div>
              <div className="text-center space-y-3">
                <div className="w-12 h-12 rounded-full mx-auto flex items-center justify-center text-white font-semibold" style={{ background: 'var(--color-primary)' }}>
                  3
                </div>
                <h3 className="text-lg font-semibold text-[var(--color-headline)]">You get the weekly action email</h3>
                <p className="text-[var(--color-body)]">Prioritized, low-noise, easy to forward.</p>
              </div>
            </div>
          </Container>
        </section>

        {/* 6) Pricing teaser (#pricing) */}
        <section id="pricing" className="pt-12 pb-20 md:pt-16 md:pb-28">
          <Container size="lg">
            <div className="text-center space-y-4 mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">Pricing</h2>
              <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">Simple tiers to match your monitoring scope.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white border border-[var(--color-border)] rounded-2xl p-8" style={{ boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)' }}>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-semibold text-[var(--color-headline)]">Starter</h3>
                    <p className="text-[var(--color-body)] mt-2">For small sites and side projects</p>
                  </div>
                  <div className="text-4xl font-bold text-[var(--color-headline)]">
                    $29<span className="text-xl font-normal text-[var(--color-body)]">/mo</span>
                  </div>
                  <ul className="space-y-3 text-[var(--color-body)] text-sm">
                    <li>10 key pages</li>
                    <li>PSI for 3 pages</li>
                    <li>Weekly digest + daily critical</li>
                  </ul>
                  <Button as="link" href="/pricing#plans" variant="secondary" size="lg" className="w-full">
                    View details
                  </Button>
                </div>
              </div>

              <div className="bg-white border-2 border-[var(--color-primary)] rounded-2xl p-8" style={{ boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)' }}>
                <div className="space-y-6">
                  <div>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border" style={{ background: 'var(--color-accent-tint)', color: 'var(--color-primary)', borderColor: 'var(--color-border)' }}>
                      Most popular
                    </span>
                    <h3 className="text-xl font-semibold text-[var(--color-headline)] mt-3">Pro</h3>
                    <p className="text-[var(--color-body)] mt-2">For growing businesses</p>
                  </div>
                  <div className="text-4xl font-bold text-[var(--color-headline)]">
                    $69<span className="text-xl font-normal text-[var(--color-body)]">/mo</span>
                  </div>
                  <ul className="space-y-3 text-[var(--color-body)] text-sm">
                    <li>50 key pages</li>
                    <li>PSI for 10 pages</li>
                    <li>100 URL crawl</li>
                  </ul>
                  <Button as="link" href="/pricing#plans" variant="primary" size="lg" className="w-full">
                    View details
                  </Button>
                </div>
              </div>

              <div className="bg-white border border-[var(--color-border)] rounded-2xl p-8" style={{ boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)' }}>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-semibold text-[var(--color-headline)]">Agency</h3>
                    <p className="text-[var(--color-body)] mt-2">For teams monitoring multiple sites</p>
                  </div>
                  <div className="text-4xl font-bold text-[var(--color-headline)]">
                    $199<span className="text-xl font-normal text-[var(--color-body)]">/mo</span>
                  </div>
                  <ul className="space-y-3 text-[var(--color-body)] text-sm">
                    <li>5 domains</li>
                    <li>Larger crawl limits</li>
                    <li>Webhook later (roadmap)</li>
                  </ul>
                  <Button as="link" href="/pricing#plans" variant="secondary" size="lg" className="w-full">
                    View details
                  </Button>
                </div>
              </div>
            </div>
          </Container>
        </section>

        {/* 7) FAQ (#faq) */}
        <section id="faq" className="py-20 md:py-28 bg-white border-y border-[var(--color-border)]">
          <Container size="lg">
            <div className="max-w-3xl mx-auto">
              <div className="text-center mb-10">
                <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] mb-4">FAQ</h2>
                <p className="text-lg text-[var(--color-body)]">Answers to the most common objections.</p>
              </div>

              <FAQAccordion
                items={[
                  {
                    id: 'noise',
                    question: 'Will it spam me?',
                    answer:
                      'No. Daily emails are sent only for Critical findings. Everything else is summarized in the weekly digest. Noise reduction is built in via severity scoring, confirmation logic, and deduplication.',
                  },
                  {
                    id: 'js',
                    question: 'Does it work on JS-heavy sites?',
                    answer:
                      'Version 1 focuses on server-rendered HTML via requests/BeautifulSoup. A Playwright-based fallback is planned for pages flagged as likely client-rendered.',
                  },
                  {
                    id: 'setup',
                    question: 'What do I need to set up?',
                    answer:
                      'A VPS with cron, a Mailgun account for email delivery, and a Google PageSpeed Insights API key. After that, RankSentinel runs automatically and stores history in SQLite.',
                  },
                  {
                    id: 'schedule',
                    question: 'Can I change my schedule?',
                    answer:
                      'Yes. You can update your schedule anytime from the schedule page linked in every email.',
                  },
                  {
                    id: 'dashboard',
                    question: 'Do I need a dashboard?',
                    answer: 'No. Email is the dashboard: weekly priorities + critical-only alerts.',
                  },
                ]}
              />
            </div>
          </Container>
        </section>

        {/* 8) Final CTA (#final-cta) */}
        <section id="final-cta" className="py-20 md:py-28">
          <Container size="lg">
            <div
              className="rounded-3xl border border-[var(--color-border)] bg-white px-8 py-12 text-center"
              style={{ boxShadow: '0 10px 30px rgba(16, 24, 40, 0.08)' }}
            >
              <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] max-w-3xl mx-auto">
                Want to see what your weekly digest looks like?
              </h2>
              <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto mt-4">No dashboard. No noise. Just weekly actions.</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
                <Button
                  as="link"
                  href="/start"
                  variant="primary"
                  size="lg"
                  analyticsEventName="cta_start_monitoring_click"
                  analyticsEventProperties={{ location: 'home_final_cta' }}
                >
                  Start monitoring
                </Button>
                <Button as="link" href="/sample-report" variant="secondary" size="lg">
                  See sample report
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
