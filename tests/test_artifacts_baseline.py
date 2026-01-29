"""Test artifact baseline model for observation/diff functionality."""

import sqlite3
from datetime import datetime, timezone

import pytest

from ranksentinel.db import get_latest_artifact, init_db, store_artifact


@pytest.fixture
def db_conn():
    """Create in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    # Insert test customer
    conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        (
            "Test Customer",
            "active",
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    yield conn
    conn.close()


def test_store_and_retrieve_artifact(db_conn):
    """Test storing and retrieving an artifact."""
    customer_id = 1
    kind = "robots_txt"
    subject = "https://example.com/robots.txt"
    artifact_sha = "abc123def456"
    raw_content = "User-agent: *\nDisallow: /admin/"
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Store artifact
    artifact_id = store_artifact(
        db_conn, customer_id, kind, subject, artifact_sha, raw_content, fetched_at
    )
    assert artifact_id > 0

    # Retrieve latest artifact
    result = get_latest_artifact(db_conn, customer_id, kind, subject)
    assert result is not None
    assert result["artifact_sha"] == artifact_sha
    assert result["raw_content"] == raw_content
    assert result["fetched_at"] == fetched_at


def test_get_latest_artifact_returns_most_recent(db_conn):
    """Test that get_latest_artifact returns the most recent artifact."""
    customer_id = 1
    kind = "robots_txt"
    subject = "https://example.com/robots.txt"

    # Store three artifacts at different times
    store_artifact(db_conn, customer_id, kind, subject, "sha1", "content1", "2024-01-01T00:00:00Z")
    store_artifact(db_conn, customer_id, kind, subject, "sha2", "content2", "2024-01-02T00:00:00Z")
    store_artifact(db_conn, customer_id, kind, subject, "sha3", "content3", "2024-01-03T00:00:00Z")

    # Should get the most recent (sha3)
    result = get_latest_artifact(db_conn, customer_id, kind, subject)
    assert result is not None
    assert result["artifact_sha"] == "sha3"
    assert result["raw_content"] == "content3"


def test_get_latest_artifact_customer_isolation(db_conn):
    """Test that artifacts are isolated by customer_id."""
    # Add second customer
    db_conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?, ?, ?, ?)",
        (
            "Customer 2",
            "active",
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    db_conn.commit()

    kind = "robots_txt"
    subject = "https://example.com/robots.txt"

    # Store artifact for customer 1
    store_artifact(db_conn, 1, kind, subject, "sha1", "content1", "2024-01-01T00:00:00Z")
    # Store artifact for customer 2
    store_artifact(db_conn, 2, kind, subject, "sha2", "content2", "2024-01-02T00:00:00Z")

    # Each customer should get their own artifact
    result1 = get_latest_artifact(db_conn, 1, kind, subject)
    result2 = get_latest_artifact(db_conn, 2, kind, subject)

    assert result1["artifact_sha"] == "sha1"
    assert result2["artifact_sha"] == "sha2"


def test_get_latest_artifact_kind_isolation(db_conn):
    """Test that artifacts are isolated by kind."""
    customer_id = 1
    subject = "https://example.com"

    # Store different kinds
    store_artifact(
        db_conn,
        customer_id,
        "robots_txt",
        subject,
        "sha1",
        "robots content",
        "2024-01-01T00:00:00Z",
    )
    store_artifact(
        db_conn, customer_id, "sitemap", subject, "sha2", "sitemap content", "2024-01-01T00:00:00Z"
    )

    # Each kind should be retrieved independently
    robots_result = get_latest_artifact(db_conn, customer_id, "robots_txt", subject)
    sitemap_result = get_latest_artifact(db_conn, customer_id, "sitemap", subject)

    assert robots_result["raw_content"] == "robots content"
    assert sitemap_result["raw_content"] == "sitemap content"


def test_get_latest_artifact_subject_isolation(db_conn):
    """Test that artifacts are isolated by subject."""
    customer_id = 1
    kind = "robots_txt"

    # Store different subjects
    store_artifact(
        db_conn,
        customer_id,
        kind,
        "https://example.com/robots.txt",
        "sha1",
        "content1",
        "2024-01-01T00:00:00Z",
    )
    store_artifact(
        db_conn,
        customer_id,
        kind,
        "https://other.com/robots.txt",
        "sha2",
        "content2",
        "2024-01-01T00:00:00Z",
    )

    # Each subject should be retrieved independently
    result1 = get_latest_artifact(db_conn, customer_id, kind, "https://example.com/robots.txt")
    result2 = get_latest_artifact(db_conn, customer_id, kind, "https://other.com/robots.txt")

    assert result1["raw_content"] == "content1"
    assert result2["raw_content"] == "content2"


def test_get_latest_artifact_no_baseline(db_conn):
    """Test that get_latest_artifact returns None when no baseline exists."""
    result = get_latest_artifact(db_conn, 1, "robots_txt", "https://example.com/robots.txt")
    assert result is None


def test_idempotent_run_scenario(db_conn):
    """Test that running the same job twice can load baseline without crashing.

    This simulates:
    1. First run: no baseline exists, store new artifact
    2. Second run: baseline exists, load and compare
    """
    customer_id = 1
    kind = "robots_txt"
    subject = "https://example.com/robots.txt"
    content = "User-agent: *\nDisallow: /admin/"
    sha = "abc123"

    # First run - no baseline
    baseline_run1 = get_latest_artifact(db_conn, customer_id, kind, subject)
    assert baseline_run1 is None  # No baseline on first run

    # Store artifact after first run
    store_artifact(db_conn, customer_id, kind, subject, sha, content, "2024-01-01T00:00:00Z")

    # Second run - baseline exists
    baseline_run2 = get_latest_artifact(db_conn, customer_id, kind, subject)
    assert baseline_run2 is not None  # Baseline exists
    assert baseline_run2["artifact_sha"] == sha
    assert baseline_run2["raw_content"] == content

    # Simulate storing the same content again (unchanged)
    store_artifact(db_conn, customer_id, kind, subject, sha, content, "2024-01-02T00:00:00Z")

    # Third run - should still load baseline without issues
    baseline_run3 = get_latest_artifact(db_conn, customer_id, kind, subject)
    assert baseline_run3 is not None
    assert baseline_run3["artifact_sha"] == sha  # Most recent sha (same content)
