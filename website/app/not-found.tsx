import Link from 'next/link';
import { Container, Button } from './components';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-teal-50 flex items-center justify-center px-4">
      <Container>
        <div className="text-center max-w-2xl mx-auto py-16">
          {/* 404 Heading */}
          <h1 className="text-8xl font-bold text-teal-600 mb-4">404</h1>
          
          {/* Message */}
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            Page Not Found
          </h2>
          <p className="text-lg text-slate-600 mb-8">
            Sorry, we couldn't find the page you're looking for. It might have been moved or doesn't exist.
          </p>

          {/* Navigation CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/">
              <Button variant="primary" size="lg">
                Go to Homepage
              </Button>
            </Link>
            <Link href="/pricing">
              <Button variant="secondary" size="lg">
                View Pricing
              </Button>
            </Link>
          </div>

          {/* Helpful Links */}
          <div className="mt-12 pt-8 border-t border-slate-200">
            <p className="text-sm text-slate-500 mb-4">
              Need help? Here are some popular pages:
            </p>
            <div className="flex flex-wrap gap-4 justify-center text-sm">
              <Link href="/sample-report" className="text-teal-600 hover:text-teal-700 underline">
                Sample Report
              </Link>
              <Link href="/#features" className="text-teal-600 hover:text-teal-700 underline">
                Features
              </Link>
              <Link href="/#faq" className="text-teal-600 hover:text-teal-700 underline">
                FAQ
              </Link>
            </div>
          </div>
        </div>
      </Container>
    </div>
  );
}
