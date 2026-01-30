"""Test sitemap fetch and artifact storage."""

from unittest.mock import Mock, patch

import pytest

from ranksentinel.config import Settings
from ranksentinel.db import connect, get_latest_artifact, init_db
from ranksentinel.runner.daily_checks import run


@pytest.fixture
def test_db(tmp_path):
    """Create a test database."""
    db_path = tmp_path / "test.db"
    settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    conn = connect(settings)
    init_db(conn)
    yield conn, settings
    conn.close()


def test_sitemap_fetch_and_store(test_db):
    """Test that sitemap is fetched and stored as artifact on change."""
    conn, settings = test_db

    # Create test customer with sitemap_url
    cursor = conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Test Co", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO settings(customer_id, sitemap_url) VALUES (?, ?)",
        (customer_id, "https://example.com/sitemap.xml"),
    )
    conn.execute(
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES (?, ?, ?, ?)",
        (customer_id, "https://example.com/page1", 1, "2026-01-29T00:00:00Z"),
    )
    conn.commit()

    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
    <lastmod>2024-01-01</lastmod>
  </url>
</urlset>"""

    # Mock fetch_text to return sitemap
    with (
        patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch,
        patch("ranksentinel.runner.daily_checks.Settings") as mock_settings,
    ):
        # Setup mock responses
        mock_fetch_result = Mock()
        mock_fetch_result.is_error = False
        mock_fetch_result.body = sitemap_content
        mock_fetch_result.status_code = 200
        mock_fetch_result.final_url = "https://example.com/sitemap.xml"
        mock_fetch_result.redirect_chain = []

        def fetch_side_effect(url, **kwargs):
            if "sitemap.xml" in url:
                return mock_fetch_result
            # For other URLs (like page fetches), return minimal HTML
            html_result = Mock()
            html_result.is_error = False
            html_result.body = "<html><head><title>Test</title></head><body>Content</body></html>"
            html_result.status_code = 200
            html_result.final_url = url
            html_result.redirect_chain = []
            return html_result

        mock_fetch.side_effect = fetch_side_effect

        # Run daily checks
        run(settings)

    # Check that sitemap artifact was stored
    artifact = get_latest_artifact(conn, customer_id, "sitemap", "https://example.com/sitemap.xml")
    assert artifact is not None
    assert sitemap_content in artifact["raw_content"]


def test_sitemap_missing_creates_finding(test_db):
    """Test that missing/unreachable sitemap produces critical finding."""
    conn, settings = test_db

    # Create test customer with sitemap_url
    cursor = conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Test Co", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO settings(customer_id, sitemap_url) VALUES (?, ?)",
        (customer_id, "https://example.com/sitemap.xml"),
    )
    conn.execute(
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES (?, ?, ?, ?)",
        (customer_id, "https://example.com/page1", 1, "2026-01-29T00:00:00Z"),
    )
    conn.commit()

    # Mock fetch_text to return error for sitemap
    with (
        patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch,
        patch("ranksentinel.runner.daily_checks.Settings") as mock_settings,
    ):
        # Setup mock responses
        mock_fetch_result = Mock()
        mock_fetch_result.is_error = True
        mock_fetch_result.error = "404 Not Found"
        mock_fetch_result.error_type = "http_error"
        mock_fetch_result.status_code = 404
        mock_fetch_result.body = None

        def fetch_side_effect(url, **kwargs):
            if "sitemap.xml" in url:
                return mock_fetch_result
            # For other URLs, return minimal HTML
            html_result = Mock()
            html_result.is_error = False
            html_result.body = "<html><head><title>Test</title></head><body>Content</body></html>"
            html_result.status_code = 200
            html_result.final_url = url
            html_result.redirect_chain = []
            return html_result

        mock_fetch.side_effect = fetch_side_effect

        # Run daily checks
        run(settings)

    # Check that critical finding was created
    findings = conn.execute(
        "SELECT severity, category, title FROM findings WHERE customer_id=? AND title=?",
        (customer_id, "Sitemap unreachable"),
    ).fetchall()

    assert len(findings) == 1
    finding = findings[0]
    assert finding["severity"] == "critical"
    assert finding["category"] == "indexability"


def test_sitemap_no_change_no_store(test_db):
    """Test that unchanged sitemap is not re-stored."""
    conn, settings = test_db

    # Create test customer with sitemap_url
    cursor = conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Test Co", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )
    customer_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO settings(customer_id, sitemap_url) VALUES (?, ?)",
        (customer_id, "https://example.com/sitemap.xml"),
    )
    conn.execute(
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES (?, ?, ?, ?)",
        (customer_id, "https://example.com/page1", 1, "2026-01-29T00:00:00Z"),
    )
    conn.commit()

    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
  </url>
</urlset>"""

    # Pre-store the sitemap artifact
    import hashlib
    from datetime import datetime, timezone

    sha = hashlib.sha256(sitemap_content.encode("utf-8")).hexdigest()
    fetched_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO artifacts(customer_id, kind, subject, artifact_sha, raw_content, fetched_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            customer_id,
            "sitemap",
            "https://example.com/sitemap.xml",
            sha,
            sitemap_content,
            fetched_at,
        ),
    )
    conn.commit()

    # Mock fetch_text to return same sitemap
    with (
        patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch,
        patch("ranksentinel.runner.daily_checks.Settings") as mock_settings,
    ):
        mock_fetch_result = Mock()
        mock_fetch_result.is_error = False
        mock_fetch_result.body = sitemap_content
        mock_fetch_result.status_code = 200
        mock_fetch_result.final_url = "https://example.com/sitemap.xml"
        mock_fetch_result.redirect_chain = []

        def fetch_side_effect(url, **kwargs):
            if "sitemap.xml" in url:
                return mock_fetch_result
            # For other URLs, return minimal HTML
            html_result = Mock()
            html_result.is_error = False
            html_result.body = "<html><head><title>Test</title></head><body>Content</body></html>"
            html_result.status_code = 200
            html_result.final_url = url
            html_result.redirect_chain = []
            return html_result

        mock_fetch.side_effect = fetch_side_effect

        # Run daily checks
        run(settings)

    # Check that only one artifact exists (not duplicated)
    artifact_count = conn.execute(
        "SELECT COUNT(*) as count FROM artifacts WHERE customer_id=? AND kind=?",
        (customer_id, "sitemap"),
    ).fetchone()["count"]

    assert artifact_count == 1
