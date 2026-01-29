"""Integration test for weekly fetcher with crawl limit enforcement."""

import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

from ranksentinel.config import Settings
from ranksentinel.db import execute, fetch_all, init_db
from ranksentinel.http_client import FetchResult
from ranksentinel.runner.weekly_digest import run


def test_weekly_fetcher_enforces_crawl_limit(tmp_path):
    """Test that weekly fetcher respects crawl_limit from settings."""
    # Setup test database
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create test customer with sitemap_url and crawl_limit
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, 'active', datetime('now'), datetime('now'))",
        ("Test Customer",)
    )
    
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url, crawl_limit) VALUES(?, ?, ?)",
        (customer_id, "https://example.com/sitemap.xml", 25)
    )
    
    conn.close()
    
    # Mock sitemap with 100 URLs
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    """ + "\n".join([f"<url><loc>https://example.com/page{i}</loc></url>" for i in range(100)]) + """
    </urlset>"""
    
    # Mock fetch_text to return sitemap and page content
    def mock_fetch_text(url, timeout=20, attempts=3):
        if "sitemap.xml" in url:
            return FetchResult(status_code=200, final_url=url, body=sitemap_xml)
        else:
            return FetchResult(status_code=200, final_url=url, body="<html>Page content</html>")
    
    # Create test settings
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    # Patch fetch_text in both weekly_digest and page_fetcher modules
    with patch("ranksentinel.runner.weekly_digest.fetch_text", side_effect=mock_fetch_text), \
         patch("ranksentinel.runner.page_fetcher.fetch_text", side_effect=mock_fetch_text) as mock_page_fetch:
        run(test_settings)
        
        # Count page fetches from page_fetcher (actual page crawls)
        page_fetches = mock_page_fetch.call_args_list
        
        # Should have fetched exactly crawl_limit (25) pages, not all 100
        assert len(page_fetches) == 25, f"Expected 25 page fetches, got {len(page_fetches)}"


def test_weekly_fetcher_records_fetch_status(tmp_path):
    """Test that weekly fetcher logs fetch results and persists snapshots."""
    # Setup test database
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create test customer
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, 'active', datetime('now'), datetime('now'))",
        ("Test Customer",)
    )
    
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url, crawl_limit) VALUES(?, ?, ?)",
        (customer_id, "https://example.com/sitemap.xml", 5)
    )
    
    conn.close()
    
    # Mock sitemap with 10 URLs
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/page1</loc></url>
        <url><loc>https://example.com/page2</loc></url>
        <url><loc>https://example.com/page3</loc></url>
        <url><loc>https://example.com/page4</loc></url>
        <url><loc>https://example.com/page5</loc></url>
        <url><loc>https://example.com/page6</loc></url>
        <url><loc>https://example.com/page7</loc></url>
        <url><loc>https://example.com/page8</loc></url>
        <url><loc>https://example.com/page9</loc></url>
        <url><loc>https://example.com/page10</loc></url>
    </urlset>"""
    
    # Mock fetch_text with mixed success/failure
    fetch_count = [0]
    
    def mock_fetch_text(url, timeout=20, attempts=3):
        if "sitemap.xml" in url:
            return FetchResult(status_code=200, final_url=url, body=sitemap_xml)
        else:
            fetch_count[0] += 1
            if fetch_count[0] == 3:
                # Third page returns 404
                return FetchResult(status_code=404, final_url=url, body="Not Found", error="HTTP 404")
            else:
                return FetchResult(status_code=200, final_url=url, body="<html>Page content</html>")
    
    # Create test settings
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    # Patch fetch_text in both modules
    with patch("ranksentinel.runner.weekly_digest.fetch_text", side_effect=mock_fetch_text), \
         patch("ranksentinel.runner.page_fetcher.fetch_text", side_effect=mock_fetch_text):
        # Should run without errors even with mixed results
        run(test_settings)
        
        # Verify database was updated (findings should be created)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        findings = fetch_all(conn, "SELECT * FROM findings WHERE customer_id=?", (customer_id,))
        
        # Verify snapshots were persisted
        snapshots = fetch_all(
            conn,
            "SELECT * FROM snapshots WHERE customer_id=? AND run_type='weekly'",
            (customer_id,)
        )
        
        # Verify run_coverage was created
        run_coverage = fetch_all(
            conn,
            "SELECT * FROM run_coverage WHERE customer_id=? AND run_type='weekly'",
            (customer_id,)
        )
        
        conn.close()
        
        # Should have at least the bootstrap finding (still in DB, just not in email)
        assert len(findings) >= 1
        
        # Should have exactly 5 snapshots (crawl_limit=5)
        assert len(snapshots) == 5, f"Expected 5 snapshots, got {len(snapshots)}"
        
        # Verify all snapshots have run_id set
        for snapshot in snapshots:
            assert snapshot["run_id"], f"Snapshot missing run_id: {dict(snapshot)}"
            assert snapshot["run_type"] == "weekly"
            assert snapshot["customer_id"] == customer_id
        
        # Should have exactly 1 run_coverage entry
        assert len(run_coverage) == 1, f"Expected 1 run_coverage entry, got {len(run_coverage)}"
        assert run_coverage[0]["run_type"] == "weekly"


def test_weekly_fetcher_skips_customer_without_sitemap(tmp_path):
    """Test that weekly fetcher skips customers without sitemap_url configured."""
    # Setup test database
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create test customer without sitemap_url
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, 'active', datetime('now'), datetime('now'))",
        ("Test Customer",)
    )
    execute(
        conn,
        "INSERT INTO settings(customer_id, crawl_limit) VALUES(?, ?)",
        (customer_id, 100)
    )
    
    conn.close()
    
    # Create test settings
    test_settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
    
    with patch("ranksentinel.runner.weekly_digest.fetch_text") as mock_fetch, \
         patch("ranksentinel.runner.page_fetcher.fetch_text") as mock_page_fetch:
        run(test_settings)
        
        # Should not have made any fetch calls (customer was skipped)
        assert mock_fetch.call_count == 0
        assert mock_page_fetch.call_count == 0
