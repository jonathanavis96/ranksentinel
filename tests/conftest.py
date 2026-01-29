"""Shared pytest fixtures for RankSentinel tests.

This module provides reusable fixtures for:
- Database connections (in-memory and file-based)
- Sample robots.txt bodies (various comment/whitespace cases)
- Sample sitemap XML (urlset and sitemap index)
- Sample HTML pages (title, canonical, meta robots)
- Sample PSI JSON responses (minimal representative samples)
"""
import sqlite3
from datetime import datetime, timezone

import pytest

from ranksentinel.config import Settings
from ranksentinel.db import connect, init_db


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def db_conn():
    """Create in-memory database with initialized schema and a test customer.
    
    Yields:
        sqlite3.Connection: In-memory database connection with row_factory set.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Insert default test customer
    conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        ("Test Customer", "active", datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    
    yield conn
    conn.close()


@pytest.fixture
def test_db(tmp_path):
    """Create a file-based test database with Settings object.
    
    This fixture is for integration tests that need a real database file.
    Includes a test customer with ID=1 and a sample target.
    
    Yields:
        tuple: (connection, Settings instance)
    """
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


# ============================================================================
# Robots.txt Fixtures
# ============================================================================

@pytest.fixture
def robots_simple():
    """Simple robots.txt with basic directives."""
    return """User-agent: *
Disallow: /admin/
Allow: /
"""


@pytest.fixture
def robots_with_comments():
    """Robots.txt with various comment styles."""
    return """# Main comment
User-agent: *
Disallow: /admin/  # inline comment
# Another comment
Allow: /public/
"""


@pytest.fixture
def robots_with_whitespace():
    """Robots.txt with extra whitespace and blank lines."""
    return """
User-agent: *

Disallow: /admin/

Allow: /

"""


@pytest.fixture
def robots_restrictive():
    """Highly restrictive robots.txt."""
    return """User-agent: *
Disallow: /
"""


@pytest.fixture
def robots_empty():
    """Empty robots.txt (allows everything)."""
    return ""


# ============================================================================
# Sitemap XML Fixtures
# ============================================================================

@pytest.fixture
def sitemap_urlset():
    """Basic sitemap with urlset (direct URL list)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/page1</loc>
    <lastmod>2024-01-02</lastmod>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
    <lastmod>2024-01-03</lastmod>
  </url>
</urlset>
"""


@pytest.fixture
def sitemap_index():
    """Sitemap index file (points to other sitemaps)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-pages.xml</loc>
    <lastmod>2024-01-01</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-posts.xml</loc>
    <lastmod>2024-01-02</lastmod>
  </sitemap>
</sitemapindex>
"""


@pytest.fixture
def sitemap_large():
    """Large sitemap with many URLs for sampling tests."""
    urls = [
        f'  <url><loc>https://example.com/page{i}</loc></url>'
        for i in range(200)
    ]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>
"""


@pytest.fixture
def sitemap_empty():
    """Empty sitemap (no URLs)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>
"""


# ============================================================================
# HTML Page Fixtures
# ============================================================================

@pytest.fixture
def html_basic():
    """Basic HTML page with title."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>
"""


@pytest.fixture
def html_with_canonical():
    """HTML page with canonical URL."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
    <link rel="canonical" href="https://example.com/canonical-page" />
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>
"""


@pytest.fixture
def html_with_meta_robots():
    """HTML page with meta robots directives."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
    <meta name="robots" content="noindex, nofollow" />
</head>
<body>
    <h1>Welcome</h1>
</body>
</html>
"""


@pytest.fixture
def html_complex():
    """Complex HTML with multiple SEO signals."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Complex Test Page</title>
    <meta name="description" content="This is a test page" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="https://example.com/complex" />
    <meta property="og:title" content="Complex Page" />
</head>
<body>
    <h1>Complex Content</h1>
    <a href="/page1">Link 1</a>
    <a href="/page2">Link 2</a>
</body>
</html>
"""


@pytest.fixture
def html_no_title():
    """HTML page missing title tag."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
</head>
<body>
    <h1>No Title</h1>
</body>
</html>
"""


# ============================================================================
# PSI (PageSpeed Insights) JSON Fixtures
# ============================================================================

@pytest.fixture
def psi_good_score():
    """PSI response with good performance score."""
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {
                    "score": 0.95
                }
            },
            "audits": {
                "first-contentful-paint": {
                    "score": 0.9,
                    "numericValue": 1200
                },
                "speed-index": {
                    "score": 0.95,
                    "numericValue": 1800
                }
            }
        }
    }


@pytest.fixture
def psi_poor_score():
    """PSI response with poor performance score."""
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {
                    "score": 0.45
                }
            },
            "audits": {
                "first-contentful-paint": {
                    "score": 0.3,
                    "numericValue": 4500
                },
                "speed-index": {
                    "score": 0.4,
                    "numericValue": 6200
                }
            }
        }
    }


@pytest.fixture
def psi_minimal():
    """Minimal PSI response for basic testing."""
    return {
        "lighthouseResult": {
            "categories": {
                "performance": {
                    "score": 0.75
                }
            }
        }
    }


@pytest.fixture
def psi_error():
    """PSI error response."""
    return {
        "error": {
            "code": 500,
            "message": "Internal error",
            "status": "INTERNAL"
        }
    }
