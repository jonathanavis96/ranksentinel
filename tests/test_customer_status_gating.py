"""Test customer status gating in runners.

NOTE: These tests require the full environment with dependencies installed.
To run: PYTHONPATH=src python3 -m pytest tests/test_customer_status_gating.py -v
"""

import sqlite3
from datetime import datetime, timezone

import pytest


def _setup_test_db(db_path, monkeypatch):
    """Helper to set up test database with customers of different statuses."""
    pytest.importorskip("ranksentinel.config")
    pytest.importorskip("ranksentinel.db")
    
    from ranksentinel.config import Settings
    from ranksentinel.db import init_db
    
    monkeypatch.setenv("RANKSENTINEL_DB_PATH", str(db_path))
    monkeypatch.setenv("MAILGUN_API_KEY", "test-key")
    monkeypatch.setenv("MAILGUN_DOMAIN", "test.example.com")
    
    settings = Settings()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Create customers with different statuses
    cursor = conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Active Customer", "active", now, now)
    )
    active_id = cursor.lastrowid
    
    cursor = conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Past Due Customer", "past_due", now, now)
    )
    past_due_id = cursor.lastrowid
    
    cursor = conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("Canceled Customer", "canceled", now, now)
    )
    canceled_id = cursor.lastrowid
    
    return settings, conn, (active_id, past_due_id, canceled_id)


def test_daily_skips_non_active_customers(tmp_path, monkeypatch):
    """Test that daily runner only processes active customers."""
    pytest.importorskip("ranksentinel.runner.daily_checks")
    
    from ranksentinel.runner.daily_checks import run as run_daily
    
    db_path = tmp_path / "test.db"
    settings, conn, (active_id, past_due_id, canceled_id) = _setup_test_db(db_path, monkeypatch)
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Add targets for all customers
    for cid in [active_id, past_due_id, canceled_id]:
        conn.execute(
            "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES (?, ?, ?, ?)",
            (cid, "https://example.com", 1, now)
        )
        conn.execute(
            "INSERT INTO settings(customer_id) VALUES (?)",
            (cid,)
        )
    
    conn.commit()
    conn.close()
    
    # Run daily checks
    run_daily(settings)
    
    # Verify only active customer has snapshots
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    active_snapshots = conn.execute(
        "SELECT COUNT(*) as cnt FROM snapshots WHERE customer_id=?", (active_id,)
    ).fetchone()["cnt"]
    
    past_due_snapshots = conn.execute(
        "SELECT COUNT(*) as cnt FROM snapshots WHERE customer_id=?", (past_due_id,)
    ).fetchone()["cnt"]
    
    canceled_snapshots = conn.execute(
        "SELECT COUNT(*) as cnt FROM snapshots WHERE customer_id=?", (canceled_id,)
    ).fetchone()["cnt"]
    
    conn.close()
    
    assert active_snapshots > 0, "Active customer should have snapshots"
    assert past_due_snapshots == 0, "Past due customer should have no snapshots"
    assert canceled_snapshots == 0, "Canceled customer should have no snapshots"


def test_weekly_skips_non_active_customers(tmp_path, monkeypatch):
    """Test that weekly runner only processes active customers."""
    pytest.importorskip("ranksentinel.runner.weekly_digest")
    
    from unittest.mock import Mock, patch
    from ranksentinel.runner.weekly_digest import run as run_weekly
    
    db_path = tmp_path / "test.db"
    settings, conn, (active_id, past_due_id, canceled_id) = _setup_test_db(db_path, monkeypatch)
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Add targets and settings for all customers
    for cid in [active_id, past_due_id, canceled_id]:
        conn.execute(
            "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES (?, ?, ?, ?)",
            (cid, "https://example.com", 1, now)
        )
        conn.execute(
            "INSERT INTO settings(customer_id, sitemap_url) VALUES (?, ?)",
            (cid, "https://example.com/sitemap.xml")
        )
    
    conn.commit()
    conn.close()
    
    # Mock HTTP responses for sitemap and pages
    def mock_fetch_text(url, timeout=20, attempts=3, base_delay=1.0):
        mock_result = Mock()
        if "sitemap.xml" in url:
            # Return a simple sitemap with one URL
            mock_result.is_error = False
            mock_result.body = '<?xml version="1.0"?><urlset><url><loc>https://example.com/page1</loc></url></urlset>'
            mock_result.status_code = 200
        else:
            # Return successful page response
            mock_result.is_error = False
            mock_result.body = "<html><body>Test</body></html>"
            mock_result.status_code = 200
            mock_result.final_url = url
            mock_result.error = None
            mock_result.error_type = None
        return mock_result
    
    # Run weekly digest with mocked HTTP
    with patch("ranksentinel.runner.weekly_digest.fetch_text", side_effect=mock_fetch_text), \
         patch("ranksentinel.runner.page_fetcher.fetch_text", side_effect=mock_fetch_text):
        run_weekly(settings)
    
    # Verify only active customer has snapshots
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    active_snapshots = conn.execute(
        "SELECT COUNT(*) as cnt FROM snapshots WHERE customer_id=?", (active_id,)
    ).fetchone()["cnt"]
    
    past_due_snapshots = conn.execute(
        "SELECT COUNT(*) as cnt FROM snapshots WHERE customer_id=?", (past_due_id,)
    ).fetchone()["cnt"]
    
    canceled_snapshots = conn.execute(
        "SELECT COUNT(*) as cnt FROM snapshots WHERE customer_id=?", (canceled_id,)
    ).fetchone()["cnt"]
    
    conn.close()
    
    assert active_snapshots > 0, "Active customer should have snapshots"
    assert past_due_snapshots == 0, "Past due customer should have no snapshots"
    assert canceled_snapshots == 0, "Canceled customer should have no snapshots"
