"""Test that shared fixtures are working correctly."""
import pytest


def test_db_conn_fixture(db_conn):
    """Verify db_conn fixture creates a working database."""
    cursor = db_conn.execute("SELECT name FROM customers WHERE id=1")
    row = cursor.fetchone()
    assert row is not None
    assert row["name"] == "Test Customer"


def test_robots_fixtures(robots_simple, robots_with_comments, robots_restrictive):
    """Verify robots.txt fixtures contain expected content."""
    assert "User-agent: *" in robots_simple
    assert "Disallow: /admin/" in robots_simple
    
    assert "# Main comment" in robots_with_comments
    assert "inline comment" in robots_with_comments
    
    assert "Disallow: /" in robots_restrictive


def test_sitemap_fixtures(sitemap_urlset, sitemap_index, sitemap_empty):
    """Verify sitemap XML fixtures are valid XML."""
    assert '<?xml version="1.0"' in sitemap_urlset
    assert '<urlset' in sitemap_urlset
    assert '<loc>https://example.com/</loc>' in sitemap_urlset
    
    assert '<sitemapindex' in sitemap_index
    assert 'sitemap-pages.xml' in sitemap_index
    
    assert '<urlset' in sitemap_empty
    assert '<loc>' not in sitemap_empty


def test_html_fixtures(html_basic, html_with_canonical, html_with_meta_robots):
    """Verify HTML fixtures contain expected elements."""
    assert '<title>Test Page</title>' in html_basic
    assert '<h1>Welcome</h1>' in html_basic
    
    assert 'rel="canonical"' in html_with_canonical
    assert 'https://example.com/canonical-page' in html_with_canonical
    
    assert 'name="robots"' in html_with_meta_robots
    assert 'noindex, nofollow' in html_with_meta_robots


def test_psi_fixtures(psi_good_score, psi_poor_score, psi_error):
    """Verify PSI JSON fixtures have expected structure."""
    assert psi_good_score["lighthouseResult"]["categories"]["performance"]["score"] == 0.95
    assert psi_poor_score["lighthouseResult"]["categories"]["performance"]["score"] == 0.45
    assert "error" in psi_error
    assert psi_error["error"]["code"] == 500
