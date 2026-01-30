# Skill Request: GA4 Data API Weekly Reporting

## Context

Implementing task 11.3 from `workers/IMPLEMENTATION_PLAN.md`: Weekly analytics digest email that fetches GA4 data and emails it via Mailgun.

RankSentinel is an SEO monitoring tool with a marketing website built in Next.js. We have GTM/GA4 tracking implemented (tasks 11.1 and 11.2 completed), and now need to pull weekly reports programmatically to monitor website performance (conversions, traffic, events).

## Attempted Approach

- Consulted `brain/skills/domains/marketing/growth/analytics-tracking.md` but it focuses on event implementation, not API reporting
- Checked existing codebase - no GA4 Data API integration exists
- Need to build a Python script that can run via cron

## What We Need

A clear pattern for:

1. **Authentication & Setup**
   - How to set up GA4 Data API credentials (service account vs OAuth)
   - What Python library to use (`google-analytics-data` official client?)
   - How to securely store credentials (service account JSON vs environment variables)
   - What scopes/permissions are needed

2. **Data Extraction**
   - How to query GA4 for weekly metrics (page views, events, conversions)
   - What dimensions/metrics are most useful for a marketing website
   - How to structure queries for the Data API v1
   - Date range handling for "last 7 days"

3. **Report Format**
   - Should we export as CSV, JSON, or formatted text?
   - What's the best way to make raw data actionable for manual review?
   - How to handle empty/no data scenarios

4. **Email Delivery**
   - Best practice for attaching reports to Mailgun emails
   - File vs inline text considerations

## Constraints

- **No secrets in code**: All credentials via environment variables
- **Simple & maintainable**: Prefer official Google libraries over custom HTTP
- **Cron-friendly**: Script must be idempotent and handle failures gracefully
- **Minimal dependencies**: Prefer lightweight solutions
- **Low alert noise**: Should only notify on success, not spam on transient failures

## Links & Examples

- GA4 Data API docs: https://developers.google.com/analytics/devguides/reporting/data/v1
- Existing Mailgun integration: `src/ranksentinel/mailgun.py`
- Existing email templates: `src/ranksentinel/reporting/email_templates.py`
- Cron scripts: `scripts/run_weekly.sh`

## Open Questions

1. Do we need a GA4 property ID separate from GTM container ID?
2. Should we use a service account (recommended for server-to-server) or OAuth?
3. What happens if GA4 API quota is exceeded?
4. Should the script fail silently or send an error notification?
5. Should we cache/store historical data or just email and discard?

## Acceptance Criteria

A good skill document would enable us to:

- Set up GA4 Data API credentials correctly and securely
- Write a Python script that queries weekly metrics
- Format the data for operator review (CSV/JSON attachment)
- Send via Mailgun with minimal error-prone configuration
- Add to weekly cron schedule with confidence

## Related Files

- `scripts/run_weekly.sh` - where this script would be called
- `src/ranksentinel/mailgun.py` - existing email infrastructure
- `.env.example` - where new env vars should be documented
- `pyproject.toml` - where dependencies should be added

## Priority

**Medium** - This is monitoring for the marketing website, not core product functionality. Can be deferred if complex, but would provide valuable insight into lead generation performance.

## Fallback

If GA4 Data API is too complex, acceptable fallback per task AC:
> **If Blocked:** Output to a local file and email a link/path.

Could implement a simpler solution that just emails a link to GA4 dashboard or saves report locally.
