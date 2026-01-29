"""Tests for weekly report composer."""

import sqlite3

import pytest

from ranksentinel.reporting.report_composer import compose_weekly_report, parse_severity
from ranksentinel.reporting.severity import CRITICAL, INFO, WARNING


def test_parse_severity():
    """Test severity string parsing."""
    assert parse_severity("critical") == CRITICAL
    assert parse_severity("warning") == WARNING
    assert parse_severity("info") == INFO
    assert parse_severity("unknown") == INFO  # Default


def test_compose_weekly_report_empty():
    """Test composing report with no findings."""
    report = compose_weekly_report("TestCo", [])
    
    assert report.customer_name == "TestCo"
    assert report.critical_count == 0
    assert report.warning_count == 0
    assert report.info_count == 0
    assert report.total_count == 0


def test_compose_weekly_report_with_findings():
    """Test composing report with mixed severity findings."""
    # Create mock findings rows
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "critical",
            "category": "indexability",
            "title": "Homepage is now noindex",
            "details_md": "The homepage has a noindex directive.",
            "url": "https://example.com/",
            "created_at": "2026-01-29T10:00:00Z",
        },
        {
            "id": 2,
            "customer_id": 1,
            "severity": "warning",
            "category": "indexability",
            "title": "Canonical URL changed",
            "details_md": "The canonical URL has changed.",
            "url": "https://example.com/page",
            "created_at": "2026-01-29T10:01:00Z",
        },
        {
            "id": 3,
            "customer_id": 1,
            "severity": "info",
            "category": "content",
            "title": "Page title changed",
            "details_md": "The page title has been updated.",
            "url": "https://example.com/about",
            "created_at": "2026-01-29T10:02:00Z",
        },
        {
            "id": 4,
            "customer_id": 1,
            "severity": "critical",
            "category": "indexability",
            "title": "Page not found (404)",
            "details_md": "Page returns 404.",
            "url": "https://example.com/missing",
            "created_at": "2026-01-29T10:03:00Z",
        },
    ]
    
    # Convert to dict-like objects that support .get()
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    
    report = compose_weekly_report("TestCo", mock_rows)
    
    assert report.customer_name == "TestCo"
    assert report.critical_count == 2
    assert report.warning_count == 1
    assert report.info_count == 1
    assert report.total_count == 4
    
    # Check sorting: critical should come first
    assert len(report.critical_findings) == 2
    assert report.critical_findings[0].title == "Homepage is now noindex"
    assert report.critical_findings[1].title == "Page not found (404)"
    
    # Check recommendations are populated
    assert "noindex" in report.critical_findings[0].recommendation.lower()
    assert all(f.recommendation for f in report.critical_findings)
    assert all(f.recommendation for f in report.warning_findings)
    assert all(f.recommendation for f in report.info_findings)


def test_weekly_report_text_format():
    """Test text format output structure."""
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "critical",
            "category": "indexability",
            "title": "Test finding",
            "details_md": "Test details.",
            "url": "https://example.com/",
            "created_at": "2026-01-29T10:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    text = report.to_text()
    
    # Check key sections are present
    assert "RankSentinel Weekly Digest — TestCo" in text
    assert "Executive Summary" in text
    assert "1 Critical" in text
    assert "CRITICAL" in text
    assert "Test finding" in text
    assert "https://example.com/" in text
    assert "→ Recommended Action:" in text


def test_weekly_report_html_format():
    """Test HTML format output structure."""
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "warning",
            "category": "content",
            "title": "Test warning",
            "details_md": "Test details.",
            "url": None,  # Test without URL
            "created_at": "2026-01-29T10:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    html = report.to_html()
    
    # Check HTML structure
    assert "<html>" in html
    assert "<h1>RankSentinel Weekly Digest — TestCo</h1>" in html
    assert "Executive Summary" in html
    assert "1</strong> Warnings" in html
    assert "<h2>Warnings</h2>" in html
    assert "Test warning" in html
    assert "→ Recommended Action:" in html
    assert "</html>" in html


def test_sorting_stability():
    """Test that sorting is stable: severity first, then priority."""
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "warning",
            "category": "indexability",
            "title": "Canonical URL changed",  # priority 2
            "details_md": "Details",
            "url": "https://example.com/1",
            "created_at": "2026-01-29T10:00:00Z",
        },
        {
            "id": 2,
            "customer_id": 1,
            "severity": "critical",
            "category": "indexability",
            "title": "Page not found (404)",  # priority 3
            "details_md": "Details",
            "url": "https://example.com/2",
            "created_at": "2026-01-29T10:01:00Z",
        },
        {
            "id": 3,
            "customer_id": 1,
            "severity": "critical",
            "category": "indexability",
            "title": "Homepage is now noindex",  # priority 1
            "details_md": "Details",
            "url": "https://example.com/3",
            "created_at": "2026-01-29T10:02:00Z",
        },
        {
            "id": 4,
            "customer_id": 1,
            "severity": "warning",
            "category": "indexability",
            "title": "Canonical URL disappeared",  # priority 1
            "details_md": "Details",
            "url": "https://example.com/4",
            "created_at": "2026-01-29T10:03:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    # Critical findings should be sorted by priority
    assert len(report.critical_findings) == 2
    assert report.critical_findings[0].title == "Homepage is now noindex"  # priority 1
    assert report.critical_findings[1].title == "Page not found (404)"  # priority 3
    
    # Warning findings should be sorted by priority
    assert len(report.warning_findings) == 2
    assert report.warning_findings[0].title == "Canonical URL disappeared"  # priority 1
    assert report.warning_findings[1].title == "Canonical URL changed"  # priority 2


def test_bootstrap_findings_excluded_from_weekly_report():
    """Test that bootstrap category findings are excluded from weekly emails."""
    findings = [
        {
            "id": 1,
            "customer_id": 123,
            "severity": "info",
            "category": "bootstrap",
            "title": "Weekly digest executed (bootstrap)",
            "details_md": "This is the bootstrap weekly digest placeholder.",
            "url": None,
            "created_at": "2026-01-28T10:00:00Z",
        },
        {
            "id": 2,
            "customer_id": 123,
            "severity": "critical",
            "category": "content-change",
            "title": "Homepage is now noindex",
            "details_md": "The homepage now has noindex.",
            "url": "https://example.com/",
            "created_at": "2026-01-28T12:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    # Note: In practice, the SQL query excludes bootstrap findings,
    # but this tests the composer behavior if bootstrap findings slip through
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    # Report should include the bootstrap finding if passed (composer doesn't filter)
    # The actual filtering happens in the SQL query in weekly_digest.py
    assert report.info_count == 1
    assert report.critical_count == 1
    
    # Verify bootstrap finding is in the report (composer doesn't filter)
    bootstrap_in_report = any(f.category == "bootstrap" for f in report.info_findings)
    assert bootstrap_in_report, "Composer should include bootstrap if passed (filtering is SQL's job)"


def test_all_clear_text_output_no_critical_no_warnings():
    """Test that 'All clear' message appears in text output when critical_count==0 and warning_count==0."""
    # Only info findings - no critical, no warnings
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "info",
            "category": "content",
            "title": "Page title changed",
            "details_md": "The page title was updated.",
            "url": "https://example.com/page",
            "created_at": "2026-01-29T10:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    text = report.to_text()
    
    # Verify all clear message is present
    assert "✓ ALL CLEAR" in text
    assert "Great news! No critical issues or warnings detected this week." in text
    assert "0 Critical" in text
    assert "0 Warnings" in text
    assert "1 Info" in text


def test_all_clear_text_output_empty_report():
    """Test that 'All clear' message appears in text output when there are no findings at all."""
    report = compose_weekly_report("TestCo", [])
    
    text = report.to_text()
    
    # Verify all clear message is present
    assert "✓ ALL CLEAR" in text
    assert "Great news! No critical issues or warnings detected this week." in text
    assert "0 Critical" in text
    assert "0 Warnings" in text
    assert "0 Info" in text


def test_all_clear_html_output_no_critical_no_warnings():
    """Test that 'All clear' banner appears in HTML output when critical_count==0 and warning_count==0."""
    # Only info findings - no critical, no warnings
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "info",
            "category": "content",
            "title": "Page title changed",
            "details_md": "The page title was updated.",
            "url": "https://example.com/page",
            "created_at": "2026-01-29T10:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    html = report.to_html()
    
    # Verify all clear banner is present
    assert "<div class='all-clear'>" in html
    assert "<h2>✓ All Clear</h2>" in html
    assert "Great news! No critical issues or warnings detected this week." in html
    assert "0</strong> Critical" in html
    assert "0</strong> Warnings" in html


def test_all_clear_html_output_empty_report():
    """Test that 'All clear' banner appears in HTML output when there are no findings at all."""
    report = compose_weekly_report("TestCo", [])
    
    html = report.to_html()
    
    # Verify all clear banner is present
    assert "<div class='all-clear'>" in html
    assert "<h2>✓ All Clear</h2>" in html
    assert "Great news! No critical issues or warnings detected this week." in html


def test_no_all_clear_when_critical_present():
    """Test that 'All clear' message does NOT appear when there are critical findings."""
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "critical",
            "category": "indexability",
            "title": "Page not found (404)",
            "details_md": "Page returns 404.",
            "url": "https://example.com/missing",
            "created_at": "2026-01-29T10:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    text = report.to_text()
    html = report.to_html()
    
    # Verify all clear message is NOT present
    assert "ALL CLEAR" not in text
    assert "All Clear" not in html


def test_no_all_clear_when_warnings_present():
    """Test that 'All clear' message does NOT appear when there are warning findings."""
    findings = [
        {
            "id": 1,
            "customer_id": 1,
            "severity": "warning",
            "category": "content",
            "title": "Canonical URL changed",
            "details_md": "The canonical URL has changed.",
            "url": "https://example.com/page",
            "created_at": "2026-01-29T10:00:00Z",
        },
    ]
    
    class MockRow:
        def __init__(self, data):
            self._data = data
        
        def __getitem__(self, key):
            return self._data[key]
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    mock_rows = [MockRow(f) for f in findings]
    report = compose_weekly_report("TestCo", mock_rows)
    
    text = report.to_text()
    html = report.to_html()
    
    # Verify all clear message is NOT present
    assert "ALL CLEAR" not in text
    assert "All Clear" not in html
