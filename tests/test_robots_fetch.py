"""Tests for robots.txt fetching and artifact storage."""

from unittest.mock import MagicMock, patch

import pytest

from ranksentinel.config import Settings
from ranksentinel.db import connect, fetch_all, fetch_one, init_db
from ranksentinel.runner.daily_checks import run


@pytest.fixture
def test_db(tmp_path):
    """Create a test database."""
    db_path = tmp_path / "test.db"
    settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    conn = connect(settings)
    init_db(conn)

    # Create test customer
    conn.execute(
        "INSERT INTO customers(id, name, status, created_at, updated_at) "
        "VALUES(1, 'Test Customer', 'active', '2026-01-29T00:00:00Z', '2026-01-29T00:00:00Z')"
    )

    # Create test target
    conn.execute(
        "INSERT INTO targets(customer_id, url, is_key, created_at) "
        "VALUES(1, 'https://example.com/page', 1, '2026-01-29T00:00:00Z')"
    )

    # Create settings with sitemap_url
    conn.execute(
        "INSERT INTO settings(customer_id, sitemap_url) "
        "VALUES(1, 'https://example.com/sitemap.xml')"
    )

    conn.commit()
    yield conn, settings
    conn.close()


def test_robots_fetch_stores_artifact(test_db):
    """Test that robots.txt is fetched and stored as an artifact."""
    conn, settings = test_db

    mock_robots_content = """User-agent: *
Disallow: /admin/
Allow: /
"""

    # Mock fetch_text for sitemap, robots.txt, and HTML fetches
    with patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch:
        # First call: sitemap fetch
        sitemap_response = MagicMock()
        sitemap_response.is_error = False
        sitemap_response.body = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
        sitemap_response.status_code = 200

        # Second call: robots.txt
        robots_response = MagicMock()
        robots_response.is_error = False
        robots_response.body = mock_robots_content
        robots_response.status_code = 200

        # Third call: HTML page fetch
        html_response = MagicMock()
        html_response.is_error = False
        html_response.body = "<html><head><title>Test</title></head><body>Content</body></html>"
        html_response.status_code = 200
        html_response.final_url = "https://example.com/page"
        html_response.redirect_chain = []

        mock_fetch.side_effect = [sitemap_response, robots_response, html_response]

        # Mock PSI (disabled by default in test)
        settings.PSI_API_KEY = ""

        # Run daily checks
        run(settings)

    # Verify robots artifact was stored
    artifacts = fetch_all(
        conn, "SELECT kind, subject, artifact_sha, raw_content FROM artifacts WHERE customer_id=1"
    )

    assert len(artifacts) > 0, "No artifacts stored"

    robots_artifacts = [a for a in artifacts if a["kind"] == "robots_txt"]
    assert (
        len(robots_artifacts) == 1
    ), f"Expected 1 robots_txt artifact, got {len(robots_artifacts)}"

    artifact = robots_artifacts[0]
    assert artifact["subject"] == "https://example.com"
    assert artifact["raw_content"] == mock_robots_content
    assert len(artifact["artifact_sha"]) == 64  # SHA256 hex length


def test_robots_fetch_no_duplicate_on_rerun(test_db):
    """Test that re-running with same robots.txt doesn't create duplicate artifacts."""
    conn, settings = test_db

    mock_robots_content = "User-agent: *\nDisallow: /admin/"

    with patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch:
        # Setup mock responses
        def make_response(body, is_html=False, is_sitemap=False):
            response = MagicMock()
            response.is_error = False
            response.body = body
            response.status_code = 200
            if is_html:
                response.final_url = "https://example.com/page"
                response.redirect_chain = []
            return response

        # First run (sitemap, robots, html)
        mock_fetch.side_effect = [
            make_response(
                '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
                is_sitemap=True,
            ),
            make_response(mock_robots_content),
            make_response(
                "<html><head><title>Test</title></head><body>Content</body></html>", is_html=True
            ),
        ]
        settings.PSI_API_KEY = ""
        run(settings)

        first_count = len(fetch_all(conn, "SELECT * FROM artifacts WHERE kind='robots_txt'"))

        # Second run with same content (sitemap, robots, html)
        mock_fetch.side_effect = [
            make_response(
                '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
                is_sitemap=True,
            ),
            make_response(mock_robots_content),
            make_response(
                "<html><head><title>Test</title></head><body>Content</body></html>", is_html=True
            ),
        ]
        run(settings)

        second_count = len(fetch_all(conn, "SELECT * FROM artifacts WHERE kind='robots_txt'"))

    # Only-on-change: when content hasn't changed, no new artifact is stored
    assert first_count == 1, f"Expected 1 artifact after first run, got {first_count}"
    assert (
        second_count == 1
    ), f"Expected 1 artifact after second run (unchanged), got {second_count}"


def test_robots_fetch_changed_content(test_db):
    """Test that changed robots.txt creates a new artifact."""
    conn, settings = test_db

    mock_robots_v1 = "User-agent: *\nDisallow: /admin/"
    mock_robots_v2 = "User-agent: *\nDisallow: /"  # More restrictive

    with patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch:

        def make_response(body, is_html=False, is_sitemap=False):
            response = MagicMock()
            response.is_error = False
            response.body = body
            response.status_code = 200
            if is_html:
                response.final_url = "https://example.com/page"
                response.redirect_chain = []
            return response

        # First run (sitemap, robots, html)
        mock_fetch.side_effect = [
            make_response(
                '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
                is_sitemap=True,
            ),
            make_response(mock_robots_v1),
            make_response(
                "<html><head><title>Test</title></head><body>Content</body></html>", is_html=True
            ),
        ]
        settings.PSI_API_KEY = ""
        run(settings)

        # Second run with changed content (sitemap, robots, html)
        mock_fetch.side_effect = [
            make_response(
                '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
                is_sitemap=True,
            ),
            make_response(mock_robots_v2),
            make_response(
                "<html><head><title>Test</title></head><body>Content</body></html>", is_html=True
            ),
        ]
        run(settings)

    # Verify both artifacts stored
    artifacts = fetch_all(
        conn, "SELECT artifact_sha, raw_content FROM artifacts WHERE kind='robots_txt' ORDER BY id"
    )

    assert len(artifacts) == 2
    assert artifacts[0]["raw_content"] == mock_robots_v1
    assert artifacts[1]["raw_content"] == mock_robots_v2
    assert artifacts[0]["artifact_sha"] != artifacts[1]["artifact_sha"]


def test_robots_fetch_error_handling(test_db):
    """Test that robots.txt fetch errors are handled gracefully."""
    conn, settings = test_db

    with patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch:
        # First call: sitemap succeeds
        sitemap_response = MagicMock()
        sitemap_response.is_error = False
        sitemap_response.body = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
        sitemap_response.status_code = 200

        # Second call: robots.txt fails
        robots_response = MagicMock()
        robots_response.is_error = True
        robots_response.error = "404 Not Found"
        robots_response.error_type = "http_error"

        # Third call: HTML page succeeds
        html_response = MagicMock()
        html_response.is_error = False
        html_response.body = "<html><head><title>Test</title></head><body>Content</body></html>"
        html_response.status_code = 200
        html_response.final_url = "https://example.com/page"
        html_response.redirect_chain = []

        mock_fetch.side_effect = [sitemap_response, robots_response, html_response]
        settings.PSI_API_KEY = ""

        # Should not raise exception
        run(settings)

    # Verify no robots artifact was stored
    robots_artifacts = fetch_all(conn, "SELECT * FROM artifacts WHERE kind='robots_txt'")
    assert len(robots_artifacts) == 0


def test_robots_fetch_fallback_to_target_url(test_db):
    """Test that robots.txt uses first target URL when sitemap_url is not set."""
    conn, settings = test_db

    # Remove sitemap_url from settings
    conn.execute("UPDATE settings SET sitemap_url=NULL WHERE customer_id=1")
    conn.commit()

    mock_robots_content = "User-agent: *\nAllow: /"

    with patch("ranksentinel.runner.daily_checks.fetch_text") as mock_fetch:

        def make_response(body, is_html=False):
            response = MagicMock()
            response.is_error = False
            response.body = body
            response.status_code = 200
            if is_html:
                response.final_url = "https://example.com/page"
                response.redirect_chain = []
            return response

        # No sitemap, so only robots + html
        mock_fetch.side_effect = [
            make_response(mock_robots_content),
            make_response(
                "<html><head><title>Test</title></head><body>Content</body></html>", is_html=True
            ),
        ]
        settings.PSI_API_KEY = ""
        run(settings)

    # Verify robots artifact was stored with base URL from target
    artifact = fetch_one(conn, "SELECT subject FROM artifacts WHERE kind='robots_txt'")

    assert artifact is not None
    assert artifact["subject"] == "https://example.com"
