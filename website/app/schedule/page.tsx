'use client';

import React, { useState, useEffect } from 'react';
import { Container, Button } from '../components';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { trackEvent } from '../lib/analytics';

interface ScheduleFormData {
  digest_weekday: string;
  digest_time_local: string;
  digest_timezone: string;
}

interface ScheduleResponse {
  timezone: string;
  utc_offset: string;
  next_run_utc: string;
  next_run_local: string;
}

export default function SchedulePage() {
  const [token, setToken] = useState<string | null>(null);
  const [formData, setFormData] = useState<ScheduleFormData>({
    digest_weekday: 'monday',
    digest_time_local: '09:00',
    digest_timezone: 'UTC'
  });
  const [detectedTimezone, setDetectedTimezone] = useState<string>('UTC');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [saveResult, setSaveResult] = useState<ScheduleResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Detect timezone on mount
  useEffect(() => {
    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (tz) {
        setDetectedTimezone(tz);
        setFormData(prev => ({ ...prev, digest_timezone: tz }));
      }
    } catch (e) {
      console.warn('Timezone detection failed, falling back to UTC', e);
      setDetectedTimezone('UTC');
    }
  }, []);

  // Parse token from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      setToken(urlToken);
    } else {
      setError('No schedule token provided. Please use the link from your email.');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setError('No valid token available');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSaveResult(null);

    try {
      const response = await fetch('/api/public/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          ...formData
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Failed to save schedule' }));
        throw new Error(errorData.error || 'Failed to save schedule');
      }

      const result: ScheduleResponse = await response.json();
      
      // Track successful schedule submission
      trackEvent('start_monitoring_submit', {
        source: 'schedule_page',
        weekday: formData.digest_weekday,
        timezone: formData.digest_timezone,
      });
      
      setSaveResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const weekdays = [
    { value: 'monday', label: 'Monday' },
    { value: 'tuesday', label: 'Tuesday' },
    { value: 'wednesday', label: 'Wednesday' },
    { value: 'thursday', label: 'Thursday' },
    { value: 'friday', label: 'Friday' },
    { value: 'saturday', label: 'Saturday' },
    { value: 'sunday', label: 'Sunday' },
  ];

  // Common timezones for the dropdown
  const commonTimezones = [
    'UTC',
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'America/Toronto',
    'America/Vancouver',
    'Europe/London',
    'Europe/Paris',
    'Europe/Berlin',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Singapore',
    'Australia/Sydney',
    'Pacific/Auckland',
  ];

  // Include detected timezone if not in common list
  const timezoneOptions = commonTimezones.includes(detectedTimezone)
    ? commonTimezones
    : [detectedTimezone, ...commonTimezones];

  const formatNextRun = (localTime: string) => {
    try {
      const date = new Date(localTime);
      return date.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        timeZoneName: 'short'
      });
    } catch {
      return localTime;
    }
  };

  return (
    <>
      <Header />
      <main id="main-content" className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-16">
        <Container className="max-w-2xl">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Schedule Settings
            </h1>
            <p className="text-gray-600 mb-8">
              Customize when you receive your weekly SEO digest reports
            </p>

            {error && !token && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {saveResult && (
              <div className="mb-6 p-6 bg-green-50 border border-green-200 rounded-lg">
                <h2 className="text-lg font-semibold text-green-900 mb-2">
                  ✓ Saved
                </h2>
                <p className="text-green-800 mb-3">
                  You'll receive reports every{' '}
                  <strong className="capitalize">{formData.digest_weekday}</strong> at{' '}
                  <strong>{formData.digest_time_local}</strong>{' '}
                  <span className="text-green-700">
                    ({saveResult.timezone} / {saveResult.utc_offset})
                  </span>
                </p>
                <p className="text-green-800">
                  <strong>First report:</strong>{' '}
                  {formatNextRun(saveResult.next_run_local)}
                </p>
              </div>
            )}

            {error && token && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="weekday" className="block text-sm font-medium text-gray-700 mb-2">
                  Day of Week
                </label>
                <select
                  id="weekday"
                  value={formData.digest_weekday}
                  onChange={(e) => setFormData(prev => ({ ...prev, digest_weekday: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isSubmitting || !token}
                >
                  {weekdays.map(day => (
                    <option key={day.value} value={day.value}>
                      {day.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
                  Time
                </label>
                <input
                  type="time"
                  id="time"
                  value={formData.digest_time_local}
                  onChange={(e) => setFormData(prev => ({ ...prev, digest_time_local: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isSubmitting || !token}
                />
              </div>

              <div>
                <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-2">
                  Timezone
                  {detectedTimezone !== 'UTC' && (
                    <span className="ml-2 text-xs text-gray-500">
                      (detected: {detectedTimezone})
                    </span>
                  )}
                </label>
                <select
                  id="timezone"
                  value={formData.digest_timezone}
                  onChange={(e) => setFormData(prev => ({ ...prev, digest_timezone: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isSubmitting || !token}
                >
                  {timezoneOptions.map(tz => (
                    <option key={tz} value={tz}>
                      {tz}
                    </option>
                  ))}
                </select>
              </div>

              <Button
                type="submit"
                disabled={isSubmitting || !token}
                className="w-full"
              >
                {isSubmitting ? 'Saving...' : 'Save Schedule'}
              </Button>
            </form>

            {!token && (
              <p className="mt-4 text-sm text-gray-500 text-center">
                Need a new link? Check your email for the latest schedule settings link.
              </p>
            )}
          </div>
        </Container>
      </main>
      <Footer />
    </>
  );
}
