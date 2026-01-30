"""Test database migration logic in init_db()."""

import sqlite3
import tempfile
from pathlib import Path

from ranksentinel.db import init_db


def test_init_db_creates_run_coverage_table():
    """Test that init_db() creates run_coverage table on a new database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))

        # Initialize the database
        init_db(conn)

        # Verify run_coverage table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='run_coverage'")
        result = cursor.fetchone()
        assert result is not None, "run_coverage table should exist"
        assert result[0] == "run_coverage"

        conn.close()


def test_init_db_adds_missing_columns_to_snapshots():
    """Test that init_db() adds run_id, error_type, error columns to existing snapshots table."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))

        # Create an "old" snapshots table without run_id, error_type, error columns
        conn.execute("""
            CREATE TABLE snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
                fetched_at TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                final_url TEXT NOT NULL,
                redirect_chain TEXT NOT NULL,
                title TEXT,
                canonical TEXT,
                meta_robots TEXT,
                content_hash TEXT NOT NULL
            )
        """)

        # Insert a test row to ensure no data loss
        conn.execute("""
            INSERT INTO snapshots (customer_id, url, run_type, fetched_at, status_code,
                                   final_url, redirect_chain, content_hash)
            VALUES (1, 'https://example.com', 'daily', '2026-01-29T10:00:00Z', 200,
                    'https://example.com', '[]', 'abc123')
        """)
        conn.commit()

        # Verify columns don't exist yet
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(snapshots)")
        columns_before = {row[1] for row in cursor.fetchall()}
        assert "run_id" not in columns_before
        assert "error_type" not in columns_before
        assert "error" not in columns_before

        # Run init_db() to apply migrations
        init_db(conn)

        # Verify new columns exist
        cursor.execute("PRAGMA table_info(snapshots)")
        columns_after = {row[1] for row in cursor.fetchall()}
        assert "run_id" in columns_after, "run_id column should be added"
        assert "error_type" in columns_after, "error_type column should be added"
        assert "error" in columns_after, "error column should be added"

        # Verify existing data is preserved
        cursor.execute("SELECT customer_id, url, status_code FROM snapshots WHERE id=1")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 1
        assert row[1] == "https://example.com"
        assert row[2] == 200

        conn.close()


def test_init_db_adds_missing_run_id_to_findings():
    """Test that init_db() adds run_id column to existing findings table."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))

        # Create an "old" findings table without run_id column
        conn.execute("""
            CREATE TABLE findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
                severity TEXT NOT NULL CHECK(severity IN ('critical','warning','info')),
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                details_md TEXT NOT NULL,
                url TEXT,
                dedupe_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(dedupe_key)
            )
        """)
        conn.commit()

        # Verify run_id doesn't exist yet
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(findings)")
        columns_before = {row[1] for row in cursor.fetchall()}
        assert "run_id" not in columns_before

        # Run init_db() to apply migrations
        init_db(conn)

        # Verify run_id column exists
        cursor.execute("PRAGMA table_info(findings)")
        columns_after = {row[1] for row in cursor.fetchall()}
        assert "run_id" in columns_after, "run_id column should be added to findings"

        conn.close()


def test_init_db_is_idempotent():
    """Test that running init_db() multiple times is safe."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path))

        # Run init_db() multiple times
        init_db(conn)
        init_db(conn)
        init_db(conn)

        # Verify schema is still correct
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='run_coverage'")
        assert cursor.fetchone() is not None

        cursor.execute("PRAGMA table_info(snapshots)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "run_id" in columns
        assert "error_type" in columns
        assert "error" in columns

        conn.close()
