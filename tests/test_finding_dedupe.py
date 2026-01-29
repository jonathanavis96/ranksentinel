"""Test finding deduplication functionality."""
import sqlite3
from datetime import datetime, timezone

import pytest

from ranksentinel.db import connect, generate_finding_dedupe_key, init_db, execute


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


def test_generate_dedupe_key_consistency():
    """Test that dedupe key generation is deterministic."""
    key1 = generate_finding_dedupe_key(
        customer_id=1,
        run_type="daily",
        category="indexability",
        title="Key page noindex detected",
        url="https://example.com",
        period="2026-01-29",
    )
    key2 = generate_finding_dedupe_key(
        customer_id=1,
        run_type="daily",
        category="indexability",
        title="Key page noindex detected",
        url="https://example.com",
        period="2026-01-29",
    )
    assert key1 == key2, "Same inputs should produce same dedupe key"


def test_generate_dedupe_key_uniqueness():
    """Test that different inputs produce different keys."""
    base_key = generate_finding_dedupe_key(1, "daily", "indexability", "Title", "https://example.com", "2026-01-29")
    
    # Different customer
    assert base_key != generate_finding_dedupe_key(2, "daily", "indexability", "Title", "https://example.com", "2026-01-29")
    
    # Different run_type
    assert base_key != generate_finding_dedupe_key(1, "weekly", "indexability", "Title", "https://example.com", "2026-01-29")
    
    # Different category
    assert base_key != generate_finding_dedupe_key(1, "daily", "performance", "Title", "https://example.com", "2026-01-29")
    
    # Different title
    assert base_key != generate_finding_dedupe_key(1, "daily", "indexability", "Different Title", "https://example.com", "2026-01-29")
    
    # Different URL
    assert base_key != generate_finding_dedupe_key(1, "daily", "indexability", "Title", "https://other.com", "2026-01-29")
    
    # Different period
    assert base_key != generate_finding_dedupe_key(1, "daily", "indexability", "Title", "https://example.com", "2026-01-30")


def test_finding_dedupe_prevents_duplicates(test_db):
    """Test that duplicate findings are prevented by dedupe_key."""
    # Create a customer first
    execute(test_db, "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)", 
            ("Test Customer", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"))
    
    customer_id = 1
    created_at = "2026-01-29T10:00:00+00:00"
    period = datetime.fromisoformat(created_at).strftime('%Y-%m-%d')
    dedupe_key = generate_finding_dedupe_key(
        customer_id, "daily", "indexability", "Test finding", "https://example.com", period
    )
    
    # Insert first finding
    execute(
        test_db,
        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, "daily", "critical", "indexability", "Test finding", "Details", "https://example.com", dedupe_key, created_at),
    )
    
    # Try to insert duplicate (same dedupe_key)
    execute(
        test_db,
        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, "daily", "critical", "indexability", "Test finding", "Different details", "https://example.com", dedupe_key, created_at),
    )
    
    # Should only have one finding
    count = test_db.execute("SELECT COUNT(*) FROM findings WHERE customer_id=?", (customer_id,)).fetchone()[0]
    assert count == 1, "Duplicate finding should be prevented"


def test_finding_dedupe_allows_different_periods(test_db):
    """Test that same finding in different periods is allowed."""
    # Create a customer first
    execute(test_db, "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)", 
            ("Test Customer", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"))
    
    customer_id = 1
    
    # Day 1
    created_at_1 = "2026-01-29T10:00:00+00:00"
    period_1 = datetime.fromisoformat(created_at_1).strftime('%Y-%m-%d')
    dedupe_key_1 = generate_finding_dedupe_key(
        customer_id, "daily", "indexability", "Test finding", "https://example.com", period_1
    )
    execute(
        test_db,
        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, "daily", "critical", "indexability", "Test finding", "Details", "https://example.com", dedupe_key_1, created_at_1),
    )
    
    # Day 2 (different period, should be allowed)
    created_at_2 = "2026-01-30T10:00:00+00:00"
    period_2 = datetime.fromisoformat(created_at_2).strftime('%Y-%m-%d')
    dedupe_key_2 = generate_finding_dedupe_key(
        customer_id, "daily", "indexability", "Test finding", "https://example.com", period_2
    )
    execute(
        test_db,
        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, "daily", "critical", "indexability", "Test finding", "Details", "https://example.com", dedupe_key_2, created_at_2),
    )
    
    # Should have two findings (one per period)
    count = test_db.execute("SELECT COUNT(*) FROM findings WHERE customer_id=?", (customer_id,)).fetchone()[0]
    assert count == 2, "Same finding in different periods should be allowed"


def test_finding_dedupe_allows_different_urls(test_db):
    """Test that same finding for different URLs in same period is allowed."""
    # Create a customer first
    execute(test_db, "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)", 
            ("Test Customer", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"))
    
    customer_id = 1
    created_at = "2026-01-29T10:00:00+00:00"
    period = datetime.fromisoformat(created_at).strftime('%Y-%m-%d')
    
    # URL 1
    dedupe_key_1 = generate_finding_dedupe_key(
        customer_id, "daily", "indexability", "Test finding", "https://example.com", period
    )
    execute(
        test_db,
        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, "daily", "critical", "indexability", "Test finding", "Details", "https://example.com", dedupe_key_1, created_at),
    )
    
    # URL 2 (different URL, should be allowed)
    dedupe_key_2 = generate_finding_dedupe_key(
        customer_id, "daily", "indexability", "Test finding", "https://other.com", period
    )
    execute(
        test_db,
        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (customer_id, "daily", "critical", "indexability", "Test finding", "Details", "https://other.com", dedupe_key_2, created_at),
    )
    
    # Should have two findings (one per URL)
    count = test_db.execute("SELECT COUNT(*) FROM findings WHERE customer_id=?", (customer_id,)).fetchone()[0]
    assert count == 2, "Same finding for different URLs should be allowed"
