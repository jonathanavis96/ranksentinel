"""Integration test for sitemap index expansion (Shopify-style pattern)."""

import sqlite3
from unittest.mock import patch

from ranksentinel.config import Settings
from ranksentinel.db import execute, fetch_all, init_db
from ranksentinel.http_client import FetchResult
from ranksentinel.runner.weekly_digest import run


def test_sitemapindex_expansion_fetches_page_urls(tmp_path):
    """Test that sitemapindex causes fetching of child sitemaps and extracts page URLs."""
    # Setup test database
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create test customer
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, 'active', datetime('now'), datetime('now'))",
        ("Shopify Store",)
    )
    
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url, crawl_limit) VALUES(?, ?, ?)",
        (customer_id, "https://shopify.example.com/sitemap.xml", 10)
    )
    
    conn.close()
    
    # Mock sitemapindex (root sitemap)
    sitemapindex_xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://shopify.example.com/sitemap_pages.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://shopify.example.com/sitemap_products.xml</loc>
  </sitemap>
</sitemapindex>"""
    
    # Mock child sitemap (pages)
    sitemap_pages_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://shopify.example.com/about</loc></url>
  <url><loc>https://shopify.example.com/contact</loc></url>
  <url><loc>https://shopify.example.com/blog</loc></url>
</urlset>"""
    
    # Mock child sitemap (products)
    sitemap_products_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://shopify.example.com/products/widget</loc></url>
  <url><loc>https://shopify.example.com/products/gadget</loc></url>
</urlset>"""
    
    # Mock fetch_text to return appropriate content
    def mock_fetch_text(url, timeout=20, attempts=3):
        if url == "https://shopify.example.com/sitemap.xml":
            return FetchResult(status_code=200, final_url=url, body=sitemapindex_xml)
        elif url == "https://shopify.example.com/sitemap_pages.xml":
            return FetchResult(status_code=200, final_url=url, body=sitemap_pages_xml)
        elif url == "https://shopify.example.com/sitemap_products.xml":
            return FetchResult(status_code=200, final_url=url, body=sitemap_products_xml)
        else:
            # Page fetches
            return FetchResult(status_code=200, final_url=url, body="<html>Page content</html>")
    
    # Create test settings
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    # Patch fetch_text in both modules
    with patch("ranksentinel.runner.weekly_digest.fetch_text", side_effect=mock_fetch_text), \
         patch("ranksentinel.runner.page_fetcher.fetch_text", side_effect=mock_fetch_text) as mock_page_fetch:
        run(test_settings)
        
        # Count page fetches (should be page URLs, not .xml sitemap URLs)
        page_fetches = mock_page_fetch.call_args_list
        fetched_urls = [call.args[0] if call.args else call.kwargs.get('url') for call in page_fetches]
        
        # Should have fetched page URLs, not sitemap URLs
        assert len(fetched_urls) == 5, f"Expected 5 page fetches, got {len(fetched_urls)}"
        assert "https://shopify.example.com/about" in fetched_urls
        assert "https://shopify.example.com/contact" in fetched_urls
        assert "https://shopify.example.com/blog" in fetched_urls
        assert "https://shopify.example.com/products/widget" in fetched_urls
        assert "https://shopify.example.com/products/gadget" in fetched_urls
        
        # Should NOT fetch sitemap URLs
        assert "https://shopify.example.com/sitemap_pages.xml" not in fetched_urls
        assert "https://shopify.example.com/sitemap_products.xml" not in fetched_urls


def test_sitemapindex_respects_crawl_limit(tmp_path):
    """Test that sitemap index expansion respects crawl_limit."""
    # Setup test database
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create test customer with low crawl_limit
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, 'active', datetime('now'), datetime('now'))",
        ("Shopify Store",)
    )
    
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url, crawl_limit) VALUES(?, ?, ?)",
        (customer_id, "https://shopify.example.com/sitemap.xml", 3)
    )
    
    conn.close()
    
    # Mock sitemapindex
    sitemapindex_xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://shopify.example.com/sitemap_pages.xml</loc>
  </sitemap>
</sitemapindex>"""
    
    # Mock child sitemap with 10 URLs
    sitemap_pages_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join([f"  <url><loc>https://shopify.example.com/page{i}</loc></url>" for i in range(10)]) + """
</urlset>"""
    
    # Mock fetch_text
    def mock_fetch_text(url, timeout=20, attempts=3):
        if url == "https://shopify.example.com/sitemap.xml":
            return FetchResult(status_code=200, final_url=url, body=sitemapindex_xml)
        elif url == "https://shopify.example.com/sitemap_pages.xml":
            return FetchResult(status_code=200, final_url=url, body=sitemap_pages_xml)
        else:
            return FetchResult(status_code=200, final_url=url, body="<html>Page content</html>")
    
    # Create test settings
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    # Patch fetch_text
    with patch("ranksentinel.runner.weekly_digest.fetch_text", side_effect=mock_fetch_text), \
         patch("ranksentinel.runner.page_fetcher.fetch_text", side_effect=mock_fetch_text) as mock_page_fetch:
        run(test_settings)
        
        # Should respect crawl_limit of 3
        page_fetches = mock_page_fetch.call_args_list
        assert len(page_fetches) == 3, f"Expected 3 page fetches (crawl_limit), got {len(page_fetches)}"


def test_sitemapindex_handles_child_fetch_errors(tmp_path):
    """Test that sitemap index expansion continues when child sitemaps fail."""
    # Setup test database
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create test customer
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, 'active', datetime('now'), datetime('now'))",
        ("Shopify Store",)
    )
    
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url, crawl_limit) VALUES(?, ?, ?)",
        (customer_id, "https://shopify.example.com/sitemap.xml", 10)
    )
    
    conn.close()
    
    # Mock sitemapindex with 2 children
    sitemapindex_xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://shopify.example.com/sitemap_broken.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://shopify.example.com/sitemap_working.xml</loc>
  </sitemap>
</sitemapindex>"""
    
    # Mock working child sitemap
    sitemap_working_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://shopify.example.com/page1</loc></url>
  <url><loc>https://shopify.example.com/page2</loc></url>
</urlset>"""
    
    # Mock fetch_text with one failing child
    def mock_fetch_text(url, timeout=20, attempts=3):
        if url == "https://shopify.example.com/sitemap.xml":
            return FetchResult(status_code=200, final_url=url, body=sitemapindex_xml)
        elif url == "https://shopify.example.com/sitemap_broken.xml":
            # First child fails
            return FetchResult(status_code=500, final_url=url, body="", error="HTTP 500")
        elif url == "https://shopify.example.com/sitemap_working.xml":
            # Second child works
            return FetchResult(status_code=200, final_url=url, body=sitemap_working_xml)
        else:
            return FetchResult(status_code=200, final_url=url, body="<html>Page content</html>")
    
    # Create test settings
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    # Patch fetch_text
    with patch("ranksentinel.runner.weekly_digest.fetch_text", side_effect=mock_fetch_text), \
         patch("ranksentinel.runner.page_fetcher.fetch_text", side_effect=mock_fetch_text) as mock_page_fetch:
        run(test_settings)
        
        # Should still fetch pages from working child sitemap
        page_fetches = mock_page_fetch.call_args_list
        fetched_urls = [call.args[0] if call.args else call.kwargs.get('url') for call in page_fetches]
        
        assert len(fetched_urls) == 2
        assert "https://shopify.example.com/page1" in fetched_urls
        assert "https://shopify.example.com/page2" in fetched_urls
