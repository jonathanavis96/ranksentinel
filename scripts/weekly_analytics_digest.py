#!/usr/bin/env python3
"""
Weekly Analytics Digest Script

Fetches GA4 data for the RankSentinel marketing website and emails a summary report.

Environment Variables:
    GA4_PROPERTY_ID: GA4 property ID (format: properties/123456789)
    GA4_CREDENTIALS_JSON: Path to service account JSON file
    MAILGUN_API_KEY: Mailgun API key for sending emails
    MAILGUN_DOMAIN: Mailgun domain
    OPERATOR_EMAIL: Email address to send the digest to

Usage:
    python3 scripts/weekly_analytics_digest.py
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """Generate and send weekly analytics digest."""
    
    # Check required environment variables
    required_vars = [
        "GA4_PROPERTY_ID",
        "MAILGUN_API_KEY", 
        "MAILGUN_DOMAIN",
        "OPERATOR_EMAIL"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("\nOptional: GA4_CREDENTIALS_JSON (path to service account JSON)")
        print("If not set, will use Application Default Credentials")
        sys.exit(1)
    
    # Try to import GA4 Data API
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
    except ImportError:
        print("ERROR: google-analytics-data package not installed")
        print("Install with: pip install google-analytics-data")
        sys.exit(1)
    
    from ranksentinel.mailgun import send_email
    
    property_id = os.getenv("GA4_PROPERTY_ID")
    credentials_path = os.getenv("GA4_CREDENTIALS_JSON")
    
    # Initialize GA4 client
    if credentials_path and os.path.exists(credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    try:
        client = BetaAnalyticsDataClient()
    except Exception as e:
        print(f"ERROR: Failed to initialize GA4 client: {e}")
        print("\nMake sure GA4_CREDENTIALS_JSON points to a valid service account JSON file")
        print("or Application Default Credentials are configured.")
        sys.exit(1)
    
    # Calculate date range (last 7 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    print(f"Fetching GA4 data for {start_date} to {end_date}...")
    
    # Build the report request
    request = RunReportRequest(
        property=property_id,
        date_ranges=[DateRange(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )],
        dimensions=[
            Dimension(name="eventName"),
            Dimension(name="pagePath"),
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="activeUsers"),
            Metric(name="sessions"),
        ],
    )
    
    # Fetch the report
    try:
        response = client.run_report(request)
    except Exception as e:
        print(f"ERROR: Failed to fetch GA4 report: {e}")
        sys.exit(1)
    
    # Format the report as text
    report_lines = [
        "RankSentinel Website - Weekly Analytics Digest",
        "=" * 60,
        f"Period: {start_date} to {end_date}",
        "",
        "Summary Metrics:",
        "-" * 60,
    ]
    
    # Extract summary metrics
    total_events = 0
    total_users = 0
    total_sessions = 0
    
    event_breakdown = {}
    page_breakdown = {}
    
    for row in response.rows:
        event_name = row.dimension_values[0].value
        page_path = row.dimension_values[1].value
        event_count = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        sessions = int(row.metric_values[2].value)
        
        total_events += event_count
        total_users = max(total_users, users)  # Users are not additive
        total_sessions = max(total_sessions, sessions)  # Sessions are not additive
        
        # Aggregate by event name
        if event_name not in event_breakdown:
            event_breakdown[event_name] = 0
        event_breakdown[event_name] += event_count
        
        # Aggregate by page path
        if page_path not in page_breakdown:
            page_breakdown[page_path] = 0
        page_breakdown[page_path] += event_count
    
    report_lines.extend([
        f"Total Events: {total_events}",
        f"Active Users: {total_users}",
        f"Sessions: {total_sessions}",
        "",
        "Top Events:",
        "-" * 60,
    ])
    
    # Sort and display top events
    sorted_events = sorted(event_breakdown.items(), key=lambda x: x[1], reverse=True)
    for event_name, count in sorted_events[:10]:
        report_lines.append(f"  {event_name}: {count}")
    
    report_lines.extend([
        "",
        "Top Pages:",
        "-" * 60,
    ])
    
    # Sort and display top pages
    sorted_pages = sorted(page_breakdown.items(), key=lambda x: x[1], reverse=True)
    for page_path, count in sorted_pages[:10]:
        report_lines.append(f"  {page_path}: {count} events")
    
    report_lines.extend([
        "",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ])
    
    report_text = "\n".join(report_lines)
    
    print("\n" + report_text)
    
    # Send via Mailgun
    operator_email = os.getenv("OPERATOR_EMAIL")
    
    subject = f"RankSentinel Website Analytics - Week of {start_date}"
    
    print(f"\nSending report to {operator_email}...")
    
    try:
        send_email(
            to_email=operator_email,
            subject=subject,
            text_body=report_text,
            html_body=f"<pre>{report_text}</pre>",
        )
        print("✓ Report sent successfully")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
