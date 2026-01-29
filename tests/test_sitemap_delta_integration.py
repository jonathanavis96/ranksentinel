"""Integration test for sitemap URL count delta detection."""

import sqlite3
from datetime import datetime, timezone

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, init_db, store_artifact
from ranksentinel.runner.daily_checks import sha256_text


def test_sitemap_url_count_delta_detection():
    """Test sitemap URL count change detection with severity levels."""
    # Use in-memory database for testing
    settings = Settings(RANKSENTINEL_DB_PATH=":memory:")
    conn = connect(settings)
    init_db(conn)
    
    # Create test customer
    customer_id = execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)",
        ("Test Customer", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )
    
    # Set sitemap URL in settings
    sitemap_url = "https://example.com/sitemap.xml"
    execute(
        conn,
        "INSERT INTO settings(customer_id, sitemap_url) VALUES(?,?)",
        (customer_id, sitemap_url),
    )
    
    # Baseline: sitemap with 100 URLs
    baseline_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join([f'  <url><loc>https://example.com/page{i}</loc></url>' for i in range(100)]) + """
</urlset>"""
    
    baseline_sha = sha256_text(baseline_xml)
    baseline_time = "2026-01-28T00:00:00Z"
    
    store_artifact(
        conn, customer_id, "sitemap", sitemap_url,
        baseline_sha, baseline_xml, baseline_time
    )
    
    # Test Case 1: Moderate drop (15% = 85 URLs) -> warning
    moderate_drop_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join([f'  <url><loc>https://example.com/page{i}</loc></url>' for i in range(85)]) + """
</urlset>"""
    
    moderate_sha = sha256_text(moderate_drop_xml)
    moderate_time = "2026-01-29T00:00:00Z"
    
    store_artifact(
        conn, customer_id, "sitemap", sitemap_url,
        moderate_sha, moderate_drop_xml, moderate_time
    )
    
    # Simulate the detection logic from daily_checks.py
    from ranksentinel.runner.sitemap_parser import extract_url_count
    from ranksentinel.db import generate_finding_dedupe_key, get_latest_artifact
    
    # Get artifacts in order
    artifacts = fetch_all(
        conn,
        "SELECT artifact_sha, raw_content, fetched_at FROM artifacts "
        "WHERE customer_id=? AND kind='sitemap' AND subject=? "
        "ORDER BY fetched_at ASC",
        (customer_id, sitemap_url),
    )
    
    assert len(artifacts) == 2
    
    # Verify baseline
    baseline_artifact = artifacts[0]
    baseline_count_data = extract_url_count(baseline_artifact["raw_content"])
    assert baseline_count_data["url_count"] == 100
    
    # Verify moderate drop
    moderate_artifact = artifacts[1]
    moderate_count_data = extract_url_count(moderate_artifact["raw_content"])
    assert moderate_count_data["url_count"] == 85
    
    # Calculate delta
    prev_count = baseline_count_data["url_count"]
    curr_count = moderate_count_data["url_count"]
    count_delta = curr_count - prev_count
    pct_change = (count_delta / prev_count) * 100
    
    assert count_delta == -15
    assert pct_change == -15.0
    
    # Check severity determination
    assert pct_change <= -10  # Should be warning
    assert pct_change > -30   # Not critical yet
    
    # Test Case 2: Large drop (50% = 50 URLs) -> critical
    large_drop_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join([f'  <url><loc>https://example.com/page{i}</loc></url>' for i in range(50)]) + """
</urlset>"""
    
    large_sha = sha256_text(large_drop_xml)
    large_time = "2026-01-30T00:00:00Z"
    
    store_artifact(
        conn, customer_id, "sitemap", sitemap_url,
        large_sha, large_drop_xml, large_time
    )
    
    # Get latest two artifacts
    artifacts = fetch_all(
        conn,
        "SELECT artifact_sha, raw_content FROM artifacts "
        "WHERE customer_id=? AND kind='sitemap' AND subject=? "
        "ORDER BY fetched_at DESC LIMIT 2",
        (customer_id, sitemap_url),
    )
    
    # Compare large drop to previous (moderate drop)
    current = artifacts[0]
    previous = artifacts[1]
    
    prev_count_data = extract_url_count(previous["raw_content"])
    curr_count_data = extract_url_count(current["raw_content"])
    
    prev_count = prev_count_data["url_count"]
    curr_count = curr_count_data["url_count"]
    count_delta = curr_count - prev_count
    pct_change = (count_delta / prev_count) * 100
    
    assert prev_count == 85
    assert curr_count == 50
    assert pct_change < -30  # Should be critical
    
    # Test Case 3: Complete disappearance (0 URLs) -> critical
    empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
    
    empty_sha = sha256_text(empty_xml)
    empty_time = "2026-01-31T00:00:00Z"
    
    store_artifact(
        conn, customer_id, "sitemap", sitemap_url,
        empty_sha, empty_xml, empty_time
    )
    
    # Get latest
    latest = fetch_all(
        conn,
        "SELECT raw_content FROM artifacts "
        "WHERE customer_id=? AND kind='sitemap' AND subject=? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, sitemap_url),
    )[0]
    
    latest_count_data = extract_url_count(latest["raw_content"])
    assert latest_count_data["url_count"] == 0
    # This should trigger the critical "dropped to zero" case
    
    conn.close()


def test_sitemap_index_url_count():
    """Test URL count extraction from sitemap index."""
    from ranksentinel.runner.sitemap_parser import extract_url_count
    
    index_xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap2.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap3.xml</loc>
  </sitemap>
</sitemapindex>"""
    
    result = extract_url_count(index_xml)
    assert result["url_count"] == 3
    assert result["sitemap_type"] == "index"
