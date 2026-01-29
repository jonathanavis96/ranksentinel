"""Integration test for broken link detection in weekly digest."""

import sqlite3
import tempfile
from pathlib import Path

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, init_db
from ranksentinel.runner.weekly_digest import detect_broken_internal_links


def test_detect_broken_links_with_fixtures():
    """Test broken link detection with controlled fixtures."""
    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
        
        conn = connect(settings)
        init_db(conn)
        
        # Create test customer
        customer_id = execute(
            conn,
            "INSERT INTO customers(name,status,created_at,updated_at) VALUES(?,?,?,?)",
            ("Test Customer", "active", "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
        )
        
        # Create a snapshot with a broken link fixture
        # Note: This is a controlled test - in real usage, snapshots are created by daily/weekly runs
        execute(
            conn,
            "INSERT INTO snapshots(customer_id,url,run_type,run_id,fetched_at,status_code,final_url,redirect_chain,title,canonical,meta_robots,content_hash) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                customer_id,
                "https://example.com/test-page",
                "weekly",
                "test-run-id",
                "2024-01-01T00:00:00Z",
                200,
                "https://example.com/test-page",
                "[]",
                "Test Page",
                "",
                "",
                "abc123",
            ),
        )
        
        # Since detect_broken_internal_links fetches actual pages, we can't fully test
        # without mocking or a test server. This test verifies the function runs without crashing.
        try:
            detect_broken_internal_links(
                conn,
                "test-run-id",
                customer_id,
                "weekly",
                max_pages_to_check=1,
                max_links_per_page=5,
            )
            # Function completed without exception
            success = True
        except Exception as e:
            print(f"Error: {e}")
            success = False
        
        conn.close()
        
        assert success, "detect_broken_internal_links should not crash"


def test_broken_links_table_schema():
    """Verify broken_links table exists with correct schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        settings = Settings(RANKSENTINEL_DB_PATH=str(db_path))
        
        conn = connect(settings)
        init_db(conn)
        
        # Check table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='broken_links'"
        )
        result = cursor.fetchone()
        assert result is not None, "broken_links table should exist"
        
        # Check columns
        cursor = conn.execute("PRAGMA table_info(broken_links)")
        columns = {row[1] for row in cursor.fetchall()}
        
        expected_columns = {
            "id",
            "customer_id",
            "source_url",
            "target_url",
            "status_code",
            "error_message",
            "run_type",
            "detected_at",
        }
        
        assert columns == expected_columns, f"Expected columns {expected_columns}, got {columns}"
        
        conn.close()
