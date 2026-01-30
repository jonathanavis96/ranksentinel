"""Tests for robots.txt diff detection and severity assessment."""

import sqlite3
from datetime import datetime, timezone

import pytest

from ranksentinel.db import execute, init_db, store_artifact
from ranksentinel.runner.daily_checks import check_robots_txt_change


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)

    # Insert test customer
    execute(
        conn,
        "INSERT INTO customers(id, name, status, created_at, updated_at) VALUES(1, 'Test', 'active', '2026-01-01', '2026-01-01')",
    )

    yield conn
    conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def test_robots_no_baseline(test_db):
    """No finding when there's no baseline to compare against."""
    result = check_robots_txt_change(
        test_db,
        customer_id=1,
        base_url="https://example.com",
        current_robots_content="User-agent: *\nDisallow: /admin/",
    )
    assert result is None


def test_robots_cosmetic_change_ignored(test_db):
    """Cosmetic changes (whitespace, comments) should not trigger findings."""
    base_url = "https://example.com"

    # Store baseline with comments and extra whitespace
    baseline_content = """
# This is a comment
User-agent: *
Disallow: /admin/

# Another comment
Disallow: /private/
"""
    store_artifact(test_db, 1, "robots_txt", base_url, "baseline_sha", baseline_content, now_iso())

    # New content has different comments/whitespace but same directives
    new_content = """User-agent: *
Disallow: /admin/
Disallow: /private/"""

    result = check_robots_txt_change(test_db, 1, base_url, new_content)
    assert result is None


def test_robots_critical_sitewide_disallow(test_db):
    """Critical severity when site-wide disallow is added."""
    base_url = "https://example.com"

    # Baseline allows everything
    baseline_content = """User-agent: *
Disallow:"""
    store_artifact(test_db, 1, "robots_txt", base_url, "baseline_sha", baseline_content, now_iso())

    # New content blocks entire site
    new_content = """User-agent: *
Disallow: /"""

    result = check_robots_txt_change(test_db, 1, base_url, new_content)
    assert result is not None
    severity, details = result
    assert severity == "critical"
    assert "Disallow: /" in details


def test_robots_warning_new_disallow_rules(test_db):
    """Warning severity when new disallow rules are added."""
    base_url = "https://example.com"

    # Baseline has one disallow
    baseline_content = """User-agent: *
Disallow: /admin/"""
    store_artifact(test_db, 1, "robots_txt", base_url, "baseline_sha", baseline_content, now_iso())

    # New content adds more disallow rules
    new_content = """User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /temp/"""

    result = check_robots_txt_change(test_db, 1, base_url, new_content)
    assert result is not None
    severity, details = result
    assert severity == "warning"
    assert "Disallow: /private/" in details
    assert "Disallow: /temp/" in details


def test_robots_warning_changed_disallow_rules(test_db):
    """Warning severity when disallow rules change."""
    base_url = "https://example.com"

    # Baseline
    baseline_content = """User-agent: *
Disallow: /admin/"""
    store_artifact(test_db, 1, "robots_txt", base_url, "baseline_sha", baseline_content, now_iso())

    # Changed disallow path
    new_content = """User-agent: *
Disallow: /backend/"""

    result = check_robots_txt_change(test_db, 1, base_url, new_content)
    assert result is not None
    severity, details = result
    assert severity == "warning"
    assert "Removed" in details or "Added" in details


def test_robots_info_non_disallow_change(test_db):
    """Info severity for non-disallow changes."""
    base_url = "https://example.com"

    # Baseline
    baseline_content = """User-agent: *
Disallow: /admin/
Sitemap: https://example.com/sitemap.xml"""
    store_artifact(test_db, 1, "robots_txt", base_url, "baseline_sha", baseline_content, now_iso())

    # Change sitemap only
    new_content = """User-agent: *
Disallow: /admin/
Sitemap: https://example.com/sitemap_index.xml"""

    result = check_robots_txt_change(test_db, 1, base_url, new_content)
    assert result is not None
    severity, details = result
    assert severity == "info"


def test_robots_diff_includes_changes(test_db):
    """Diff summary should show what was added and removed."""
    base_url = "https://example.com"

    baseline_content = """User-agent: *
Disallow: /admin/
Allow: /public/"""
    store_artifact(test_db, 1, "robots_txt", base_url, "baseline_sha", baseline_content, now_iso())

    new_content = """User-agent: *
Disallow: /admin/
Disallow: /private/"""

    result = check_robots_txt_change(test_db, 1, base_url, new_content)
    assert result is not None
    severity, details = result

    # Check that diff includes removed and added lines
    assert "Removed" in details or "Added" in details
    assert "Disallow: /private/" in details
