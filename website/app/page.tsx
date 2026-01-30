import { Badge, Button, Card, Container, EmailReportPreview, FAQAccordion, FeatureTabs, LeadCaptureForm } from './components';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-zinc-50">
      {/* Hero Section */}
      <section id="main-content" className="pt-24 pb-16 md:pt-32 md:pb-24">
        <Container size="lg">
          <div className="text-center space-y-8">
            {/* Hero Badge */}
            <Badge>Catch SEO regressions before traffic drops</Badge>

            {/* Hero Headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-[var(--color-headline)] max-w-4xl mx-auto">
              Low-noise SEO regression monitoring that emails you the actions.
            </h1>

            {/* Hero Subhead */}
            <p className="text-lg md:text-xl text-[var(--color-body)] max-w-3xl mx-auto">
              Robots, sitemaps, canonicals, noindex, broken links, and PageSpeed regressions—summarized into one weekly digest (with critical-only daily alerts).
            </p>

            {/* Lead Capture Form */}
            <div className="pt-4 max-w-xl mx-auto">
              <LeadCaptureForm />
            </div>

            {/* Micro-proof line */}
            <p className="text-sm text-[var(--color-body-light)] max-w-2xl mx-auto pt-4">
              Designed to avoid false alerts (severity + confirmation + dedupe).
            </p>

            {/* Secondary CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-6">
              <Button as="link" href="#sample-report" variant="secondary" size="md">
                Get a sample report
              </Button>
              <Button as="link" href="#how-it-works" variant="secondary" size="md">
                See how it works
              </Button>
            </div>

            {/* Email Preview */}
            <div className="pt-12">
              <EmailReportPreview className="max-w-3xl mx-auto" />
            </div>
          </div>
        </Container>
      </section>

      {/* Social Proof Strip */}
      <section id="outcomes" className="py-12 border-y border-[var(--color-border)] bg-white">
        <Container size="lg">
          <div className="text-center space-y-6">
            <p className="text-base font-medium text-[var(--color-headline)]">
              Built for agencies, founders, and marketing teams.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <Badge variant="info">Low-noise by design</Badge>
              <Badge variant="info">Critical-only daily emails</Badge>
              <Badge variant="info">SEO-specific signals (not generic diffs)</Badge>
              <Badge variant="info">Weekly prioritized actions</Badge>
            </div>
          </div>
        </Container>
      </section>

      {/* Why Different - 3 Card Trio */}
      <section id="why-different" className="py-20 md:py-32">
        <Container size="lg">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              Why it's different
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              Built specifically for SEO regression monitoring—not generic website monitoring with SEO bolted on.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <Card padding="lg">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-[var(--color-accent-tint)] rounded-xl flex items-center justify-center">
                  <span className="text-2xl">🎯</span>
                </div>
                <h3 className="text-xl font-semibold text-[var(--color-headline)]">
                  Critical-only daily alerts (no spam)
                </h3>
                <ul className="space-y-2 text-[var(--color-body)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>Daily email only when severity is Critical</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>Confirmation + dedupe to avoid false positives</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>Only alerts on changes that matter</span>
                  </li>
                </ul>
              </div>
            </Card>

            {/* Card 2 */}
            <Card padding="lg">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-[var(--color-accent-tint)] rounded-xl flex items-center justify-center">
                  <span className="text-2xl">🔍</span>
                </div>
                <h3 className="text-xl font-semibold text-[var(--color-headline)]">
                  SEO-specific regression checks
                </h3>
                <ul className="space-y-2 text-[var(--color-body)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>robots.txt, sitemaps, canonical, noindex</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>Status/redirect drift, broken internal links, new 404s</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>PageSpeed Insights tracking on key pages</span>
                  </li>
                </ul>
              </div>
            </Card>

            {/* Card 3 */}
            <Card padding="lg">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-[var(--color-accent-tint)] rounded-xl flex items-center justify-center">
                  <span className="text-2xl">📋</span>
                </div>
                <h3 className="text-xl font-semibold text-[var(--color-headline)]">
                  Weekly prioritized action report
                </h3>
                <ul className="space-y-2 text-[var(--color-body)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>One digest that summarizes what changed</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>&ldquo;What to do first&rdquo; recommendations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)] mt-1">•</span>
                    <span>Grouped by severity for quick scanning</span>
                  </li>
                </ul>
              </div>
            </Card>
          </div>
        </Container>
      </section>

      {/* Feature Tabs Placeholder */}
      <section id="features" className="py-20 md:py-32 bg-white">
        <Container size="lg">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              Complete SEO monitoring coverage
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              Everything you need to catch regressions before they impact rankings.
            </p>
          </div>

          {/* Note: Full tabs component will be implemented in task 4.2 */}
          <div className="grid md:grid-cols-2 gap-8">
            <Card padding="lg">
              <h3 className="text-xl font-semibold text-[var(--color-headline)] mb-4">Daily Critical Checks</h3>
              <ul className="space-y-2 text-[var(--color-body)]">
                <li>• Alerts only when severity is Critical</li>
                <li>• Focused on key pages (high leverage)</li>
                <li>• Designed for low false positives (dedupe + confirmation)</li>
              </ul>
            </Card>

            <Card padding="lg">
              <h3 className="text-xl font-semibold text-[var(--color-headline)] mb-4">Weekly Digest</h3>
              <ul className="space-y-2 text-[var(--color-body)]">
                <li>• Critical / Warning / Info grouped summaries</li>
                <li>• &ldquo;Top actions this week&rdquo; prioritized list</li>
                <li>• Stable diffs (normalized content) to reduce noise</li>
              </ul>
            </Card>

            <Card padding="lg">
              <h3 className="text-xl font-semibold text-[var(--color-headline)] mb-4">SEO Signals</h3>
              <ul className="space-y-2 text-[var(--color-body)]">
                <li>• robots.txt change detection</li>
                <li>• Sitemap deltas (hash + URL count)</li>
                <li>• Canonical/noindex/title changes</li>
              </ul>
            </Card>

            <Card padding="lg">
              <h3 className="text-xl font-semibold text-[var(--color-headline)] mb-4">PSI Monitoring</h3>
              <ul className="space-y-2 text-[var(--color-body)]">
                <li>• PageSpeed Insights on key URLs</li>
                <li>• Confirmation logic for regressions (avoid one-off blips)</li>
                <li>• Clear &ldquo;what changed&rdquo; + action suggestions</li>
              </ul>
            </Card>
          </div>
        </Container>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 md:py-32">
        <Container size="lg">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              How it works
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              Simple setup, automated monitoring, actionable reports.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {/* Step 1 */}
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-[var(--color-primary)] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
                1
              </div>
              <h3 className="text-xl font-semibold text-[var(--color-headline)]">
                Add your domain + key pages
              </h3>
              <p className="text-[var(--color-body)]">
                Configure which pages matter most for your SEO strategy.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-[var(--color-primary)] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
                2
              </div>
              <h3 className="text-xl font-semibold text-[var(--color-headline)]">
                RankSentinel runs daily + weekly via cron
              </h3>
              <p className="text-[var(--color-body)]">
                Automated checks run on your VPS. No dashboard required.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-[var(--color-primary)] text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
                3
              </div>
              <h3 className="text-xl font-semibold text-[var(--color-headline)]">
                You get a prioritized report by email
              </h3>
              <p className="text-[var(--color-body)]">
                Weekly digests + critical-only daily alerts, delivered to your inbox.
              </p>
            </div>
          </div>

          <p className="text-sm text-[var(--color-body-light)] text-center mt-12">
            Runs on a VPS with cron + Mailgun + PSI API key.
          </p>
        </Container>
      </section>

      {/* Feature Tabs */}
      <section id="features" className="py-20 md:py-32">
        <Container size="lg">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              What RankSentinel monitors
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              Comprehensive SEO regression detection across multiple signals.
            </p>
          </div>

          <FeatureTabs />
        </Container>
      </section>

      {/* Sample Report Preview */}
      <section id="sample-report" className="py-20 md:py-32 bg-white">
        <Container size="lg">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              See what you&rsquo;ll get
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              A real weekly digest example showing how regressions are surfaced and prioritized.
            </p>
          </div>

          <EmailReportPreview className="max-w-3xl mx-auto" />

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-12">
            <Button as="link" href="#pricing" variant="primary" size="lg">
              See pricing
            </Button>
            <Button as="link" href="/sample-report" variant="secondary" size="lg">
              View full sample report
            </Button>
          </div>
        </Container>
      </section>

      {/* Pricing Teaser */}
      <section id="pricing" className="py-20 md:py-32">
        <Container size="lg">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              Choose the plan that fits your monitoring needs.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Starter Plan */}
            <Card padding="lg">
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-[var(--color-headline)]">Starter</h3>
                  <p className="text-[var(--color-body)] mt-2">For small sites and side projects</p>
                </div>
                <div>
                  <div className="text-4xl font-bold text-[var(--color-headline)]">$29<span className="text-xl font-normal text-[var(--color-body)]">/mo</span></div>
                </div>
                <ul className="space-y-3 text-[var(--color-body)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>Up to 50 pages monitored</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>5 key pages for PSI</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>1 email recipient</span>
                  </li>
                </ul>
                <Button as="link" href="/pricing" variant="secondary" size="lg" className="w-full">
                  Learn more
                </Button>
              </div>
            </Card>

            {/* Growth Plan */}
            <Card padding="lg" className="border-2 border-[var(--color-primary)]">
              <div className="space-y-6">
                <div>
                  <Badge variant="info" className="mb-2">Most Popular</Badge>
                  <h3 className="text-xl font-semibold text-[var(--color-headline)]">Growth</h3>
                  <p className="text-[var(--color-body)] mt-2">For growing businesses</p>
                </div>
                <div>
                  <div className="text-4xl font-bold text-[var(--color-headline)]">$79<span className="text-xl font-normal text-[var(--color-body)]">/mo</span></div>
                </div>
                <ul className="space-y-3 text-[var(--color-body)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>Up to 200 pages monitored</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>15 key pages for PSI</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>3 email recipients</span>
                  </li>
                </ul>
                <Button as="link" href="/pricing" variant="primary" size="lg" className="w-full">
                  Learn more
                </Button>
              </div>
            </Card>

            {/* Agency Plan */}
            <Card padding="lg">
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-[var(--color-headline)]">Agency</h3>
                  <p className="text-[var(--color-body)] mt-2">For agencies and enterprises</p>
                </div>
                <div>
                  <div className="text-4xl font-bold text-[var(--color-headline)]">$199<span className="text-xl font-normal text-[var(--color-body)]">/mo</span></div>
                </div>
                <ul className="space-y-3 text-[var(--color-body)]">
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>Up to 1000 pages monitored</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>50 key pages for PSI</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[var(--color-primary)]">✓</span>
                    <span>10 email recipients</span>
                  </li>
                </ul>
                <Button as="link" href="/pricing" variant="secondary" size="lg" className="w-full">
                  Learn more
                </Button>
              </div>
            </Card>
          </div>

          <div className="text-center mt-12">
            <Button as="link" href="/pricing" variant="primary" size="lg">
              See full pricing details
            </Button>
          </div>
        </Container>
      </section>

      {/* FAQ Teaser */}
      <section id="faq" className="py-20 md:py-32 bg-white">
        <Container size="lg">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)]">
              Frequently asked questions
            </h2>
          </div>

          {/* Note: Full accordion component will be implemented in task 4.3 */}
          <div className="max-w-3xl mx-auto space-y-6">
            <Card padding="lg">
              <h3 className="text-lg font-semibold text-[var(--color-headline)] mb-3">
                Will it spam me?
              </h3>
              <p className="text-[var(--color-body)]">
                No. Daily emails are sent only when severity is Critical. Everything else is batched into the weekly digest.
                We use confirmation + dedupe logic to avoid false positives.
              </p>
            </Card>

            <Card padding="lg">
              <h3 className="text-lg font-semibold text-[var(--color-headline)] mb-3">
                Does it work on JS-heavy sites?
              </h3>
              <p className="text-[var(--color-body)]">
                Version 1 uses requests + BeautifulSoup for fast, low-cost monitoring.
                For JS-rendered content, a Playwright fallback is on the roadmap.
              </p>
            </Card>

            <Card padding="lg">
              <h3 className="text-lg font-semibold text-[var(--color-headline)] mb-3">
                What do I need to set up?
              </h3>
              <p className="text-[var(--color-body)]">
                One-time setup on a VPS with cron scheduling, Mailgun for email delivery, and a PageSpeed Insights API key.
              </p>
            </Card>
          </div>

          <div className="text-center mt-12">
            <Button as="link" href="/faq" variant="secondary" size="lg">
              See all FAQs
            </Button>
          </div>
        </Container>
      </section>

      {/* Final CTA */}
      <section id="final-cta" className="py-20 md:py-32 bg-gradient-to-b from-[var(--color-accent-tint)] to-white">
        <Container size="lg">
          <div className="text-center space-y-8">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-headline)] max-w-3xl mx-auto">
              Start monitoring your SEO health
            </h2>
            <p className="text-lg text-[var(--color-body)] max-w-2xl mx-auto">
              Weekly clarity. Critical-only alerts. No dashboard required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <Button as="link" href="#sample-report" variant="primary" size="lg">
                Get a sample report
              </Button>
              <Button as="link" href="/pricing" variant="secondary" size="lg">
                See pricing
              </Button>
            </div>
          </div>
        </Container>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Frequently Asked Questions
              </h2>
              <p className="text-lg text-gray-600">
                Common questions about RankSentinel's approach to SEO monitoring.
              </p>
            </div>
            <FAQAccordion
              items={[
                {
                  id: 'noise',
                  question: 'Will it spam me with alerts?',
                  answer:
                    'No. RankSentinel is designed to avoid false alerts through severity scoring, confirmation logic, and deduplication. Daily emails are sent only when severity is Critical. All other findings are batched into the weekly digest, grouped by severity (Critical / Warning / Info).',
                },
                {
                  id: 'js-sites',
                  question: 'Does it work on JavaScript-heavy sites?',
                  answer:
                    'Version 1 uses requests/BeautifulSoup for HTML parsing, which works well for server-rendered and hybrid sites. For client-side rendered apps that require JavaScript execution, a Playwright-based fallback is on the roadmap. If your site uses server-side rendering or pre-rendering, RankSentinel will work out of the box.',
                },
                {
                  id: 'setup',
                  question: 'What do I need to set up?',
                  answer:
                    'You need a VPS with cron access, a Mailgun account for email delivery, and a Google PageSpeed Insights API key. Setup is one-time: configure your domain, add key pages to monitor, set recipient emails, and schedule the daily and weekly cron jobs. No ongoing maintenance required.',
                },
              ]}
            />
          </div>
        </Container>
      </section>

      {/* Final CTA */}
      <section id="final-cta" className="py-24 bg-gradient-to-br from-blue-50 to-indigo-50">
        <Container>
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to catch regressions before traffic drops?
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Weekly clarity. Critical-only alerts. No dashboard required.
            </p>
            <Button as="link" href="#sample-report" variant="primary" size="lg">
              Get a sample report
            </Button>
          </div>
        </Container>
      </section>
    </div>
  );
}
