"""Test paywalled vs unlocked digest templates."""

import pytest

from ranksentinel.reporting.report_composer import (
    CoverageStats,
    WeeklyReport,
    compose_weekly_report,
)
from ranksentinel.reporting.severity import CRITICAL, INFO, WARNING


def test_unlocked_digest_shows_real_findings():
    """Test that unlocked (active/trial) customers see real findings."""
    # Create mock finding rows
    findings_rows = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "critical",
            "category": "robots",
            "title": "Homepage blocked by robots.txt",
            "details_md": "Your homepage is now blocked by robots.txt.",
            "url": "https://example.com/",
            "created_at": "2024-01-15 08:30:00",
        }
    ]

    report = compose_weekly_report(
        customer_name="Test Customer",
        findings_rows=findings_rows,
        coverage=None,
        customer_status="active",
    )

    text = report.to_text()
    html = report.to_html()

    # Should show real finding
    assert "Homepage blocked by robots.txt" in text
    assert "https://example.com/" in text
    assert "Your homepage is now blocked by robots.txt" in text

    # Should NOT show locked message
    assert "🔒 LOCKED" not in text
    assert "Upgrade to see" not in text

    # HTML checks
    assert "Homepage blocked by robots.txt" in html
    assert "https://example.com/" in html
    assert "locked" not in html.lower() or "blocked" in html.lower()  # Allow "blocked" from finding


def test_paywalled_digest_shows_locked_examples():
    """Test that paywalled customers see locked examples, not real findings."""
    # Create mock finding rows (these should be hidden)
    findings_rows = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "critical",
            "category": "robots",
            "title": "Homepage blocked by robots.txt",
            "details_md": "Your homepage is now blocked by robots.txt.",
            "url": "https://example.com/",
            "created_at": "2024-01-15 08:30:00",
        }
    ]

    report = compose_weekly_report(
        customer_name="Test Customer",
        findings_rows=findings_rows,
        coverage=None,
        customer_status="paywalled",
    )

    text = report.to_text()
    html = report.to_html()

    # Should NOT show real finding details
    assert "Homepage blocked by robots.txt" not in text
    assert "https://example.com/" not in text
    assert "Your homepage is now blocked by robots.txt" not in text

    # Should show locked message
    assert "🔒 LOCKED" in text
    assert "Upgrade to see your site's critical issues" in text

    # Should show example text
    assert "Example critical issues we detect:" in text
    assert "Important page became non-indexable" in text

    # HTML checks
    assert "🔒 LOCKED" in html
    assert "Upgrade to see your site's critical issues" in html
    assert "Important page became non-indexable" in html
    assert "locked" in html.lower()


def test_previously_interested_shows_locked_examples():
    """Test that previously_interested customers also see locked examples."""
    findings_rows = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "warning",
            "category": "sitemap",
            "title": "Sitemap URL count dropped",
            "details_md": "URL count went from 100 to 80.",
            "url": None,
            "created_at": "2024-01-15 08:30:00",
        }
    ]

    report = compose_weekly_report(
        customer_name="Test Customer",
        findings_rows=findings_rows,
        coverage=None,
        customer_status="previously_interested",
    )

    text = report.to_text()
    html = report.to_html()

    # Should NOT show real finding details (check for the specific details)
    assert "URL count went from 100 to 80" not in text
    assert "2024-01-15 08:30:00" not in text

    # Should show locked message
    assert "🔒 LOCKED" in text
    assert "Upgrade to see your site's warnings" in text
    
    # Should show example text (not the real finding)
    assert "Example warnings we track:" in text


def test_paywalled_digest_all_severity_sections():
    """Test that paywalled digest shows locked examples for all severity levels."""
    # Empty findings to ensure we're testing the locked fallback
    findings_rows = []

    report = compose_weekly_report(
        customer_name="Test Customer",
        findings_rows=findings_rows,
        coverage=None,
        customer_status="paywalled",
    )

    text = report.to_text()
    html = report.to_html()

    # Should show all three locked sections
    assert "CRITICAL" in text
    assert "WARNINGS" in text
    assert "INFO" in text

    # All should be locked
    assert text.count("🔒 LOCKED") == 3

    # Check example content for each severity
    assert "Example critical issues we detect:" in text
    assert "Example warnings we track:" in text
    assert "Example info updates we monitor:" in text

    # HTML should have blur styling
    assert "locked" in html.lower()
    assert "filter: blur" in html


def test_trial_customer_sees_real_findings():
    """Test that trial customers see real findings like active customers."""
    findings_rows = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "info",
            "category": "page_content",
            "title": "Content changed",
            "details_md": "Page content updated significantly.",
            "url": "https://example.com/page",
            "created_at": "2024-01-15 08:30:00",
        }
    ]

    report = compose_weekly_report(
        customer_name="Trial Customer",
        findings_rows=findings_rows,
        coverage=None,
        customer_status="trial",
    )

    text = report.to_text()

    # Trial customers should see real findings
    assert "Content changed" in text
    assert "https://example.com/page" in text
    assert "Page content updated significantly" in text
    assert "🔒 LOCKED" not in text


def test_paywalled_with_mixed_findings():
    """Test paywalled customer with findings in some categories but not others."""
    findings_rows = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "critical",
            "category": "robots",
            "title": "Real critical finding",
            "details_md": "This should be hidden.",
            "url": "https://example.com/",
            "created_at": "2024-01-15 08:30:00",
        }
    ]

    report = compose_weekly_report(
        customer_name="Test Customer",
        findings_rows=findings_rows,
        coverage=None,
        customer_status="paywalled",
    )

    text = report.to_text()

    # Should NOT show real finding
    assert "Real critical finding" not in text
    assert "This should be hidden" not in text

    # Should show locked examples for all sections
    assert "🔒 LOCKED — Upgrade to see your site's critical issues" in text
    assert "🔒 LOCKED — Upgrade to see your site's warnings" in text
    assert "🔒 LOCKED — Upgrade to see informational updates" in text


def test_html_blur_styling():
    """Test that HTML includes blur styling for locked content."""
    report = compose_weekly_report(
        customer_name="Test Customer",
        findings_rows=[],
        coverage=None,
        customer_status="paywalled",
    )

    html = report.to_html()

    # Check for blur CSS
    assert "filter: blur(3px)" in html
    assert "class='locked'" in html
    assert "class='locked-label'" in html

    # Check that locked examples are present
    assert "Important page became non-indexable" in html
    assert "Title or canonical changed on a key page" in html
    assert "Content changed since last snapshot" in html
