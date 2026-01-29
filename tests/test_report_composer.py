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
