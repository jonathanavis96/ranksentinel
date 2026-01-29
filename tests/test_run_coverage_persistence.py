"""Test run coverage persistence (AC 0-E.3)."""

import sqlite3
from datetime import datetime, timezone

from ranksentinel.db import connect, get_latest_run_coverage, init_db, insert_run_coverage


def test_run_coverage_persisted_after_insert(tmp_path):
    """Test that coverage stats are persisted correctly."""
    # Setup
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create a test customer
    conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)",
        ("Test Customer", "active", "2026-01-29T10:00:00Z", "2026-01-29T10:00:00Z")
    )
    conn.commit()
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Insert run coverage
    run_id = "weekly-20260129-100000"
    created_at = datetime.now(timezone.utc).isoformat()
    
    insert_run_coverage(
        conn=conn,
        customer_id=customer_id,
        run_id=run_id,
        run_type="weekly",
        sitemap_url="https://example.com/sitemap.xml",
        total_urls=500,
        sampled_urls=100,
        success_count=95,
        error_count=5,
        http_429_count=2,
        http_404_count=3,
        broken_link_count=1,
        created_at=created_at,
    )
    
    # Verify coverage exists
    coverage = get_latest_run_coverage(conn, customer_id, "weekly")
    
    assert coverage is not None
    assert coverage["customer_id"] == customer_id
    assert coverage["run_id"] == run_id
    assert coverage["run_type"] == "weekly"
    assert coverage["sitemap_url"] == "https://example.com/sitemap.xml"
    assert coverage["total_urls"] == 500
    assert coverage["sampled_urls"] == 100
    assert coverage["success_count"] == 95
    assert coverage["error_count"] == 5
    assert coverage["http_429_count"] == 2
    assert coverage["http_404_count"] == 3
    assert coverage["broken_link_count"] == 1
    assert coverage["created_at"] == created_at
    
    conn.close()


def test_run_coverage_upsert_on_conflict(tmp_path):
    """Test that coverage stats are updated on conflict (same customer_id, run_id, run_type)."""
    # Setup
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create a test customer
    conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)",
        ("Test Customer", "active", "2026-01-29T10:00:00Z", "2026-01-29T10:00:00Z")
    )
    conn.commit()
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Insert initial coverage
    run_id = "weekly-20260129-100000"
    created_at = datetime.now(timezone.utc).isoformat()
    
    insert_run_coverage(
        conn=conn,
        customer_id=customer_id,
        run_id=run_id,
        run_type="weekly",
        sitemap_url="https://example.com/sitemap.xml",
        total_urls=500,
        sampled_urls=100,
        success_count=95,
        error_count=5,
        http_429_count=2,
        http_404_count=3,
        broken_link_count=0,
        created_at=created_at,
    )
    
    # Update with new broken_link_count
    updated_at = datetime.now(timezone.utc).isoformat()
    insert_run_coverage(
        conn=conn,
        customer_id=customer_id,
        run_id=run_id,
        run_type="weekly",
        sitemap_url="https://example.com/sitemap.xml",
        total_urls=500,
        sampled_urls=100,
        success_count=95,
        error_count=5,
        http_429_count=2,
        http_404_count=3,
        broken_link_count=7,  # Updated
        created_at=updated_at,
    )
    
    # Verify only one row exists and broken_link_count was updated
    coverage = get_latest_run_coverage(conn, customer_id, "weekly")
    
    assert coverage is not None
    assert coverage["broken_link_count"] == 7
    assert coverage["created_at"] == updated_at
    
    # Verify only one row in the table
    count = conn.execute(
        "SELECT COUNT(*) as cnt FROM run_coverage WHERE customer_id=? AND run_id=? AND run_type=?",
        (customer_id, run_id, "weekly")
    ).fetchone()["cnt"]
    assert count == 1
    
    conn.close()


def test_run_coverage_returns_none_when_no_data(tmp_path):
    """Test that get_latest_run_coverage returns None when no coverage exists."""
    # Setup
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Create a test customer
    conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)",
        ("Test Customer", "active", "2026-01-29T10:00:00Z", "2026-01-29T10:00:00Z")
    )
    conn.commit()
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Verify no coverage exists
    coverage = get_latest_run_coverage(conn, customer_id, "weekly")
    assert coverage is None
    
    conn.close()
