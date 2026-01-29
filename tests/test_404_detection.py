"""Tests for 404 detection in weekly crawl."""

import sqlite3

import pytest

from ranksentinel.db import fetch_all, init_db
from ranksentinel.runner.page_fetcher import PageFetchResult
from ranksentinel.runner.weekly_digest import detect_new_404s


@pytest.fixture
def test_conn():
    """Create an in-memory test database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


def test_detect_404_creates_finding(test_conn):
    """Test that a 404 result creates a critical finding."""
    # Create a customer
    cursor = test_conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
        ("Test Customer", "active"),
    )
    customer_id = cursor.lastrowid

    # Create a 404 fetch result
    fetch_results = [
        PageFetchResult(
            url="https://example.com/missing-page",
            status_code=404,
            final_url="https://example.com/missing-page",
            body=None,
            error=None,
            error_type=None,
        )
    ]

    # Run 404 detection
    detect_new_404s(
        conn=test_conn,
        run_id="test-run-001",
        customer_id=customer_id,
        fetch_results=fetch_results,
        period="2026-W05",
    )

    # Verify finding was created
    findings = fetch_all(
        test_conn,
        "SELECT * FROM findings WHERE customer_id=? AND category=?",
        (customer_id, "indexability"),
    )

    assert len(findings) == 1
    finding = findings[0]
    assert finding["severity"] == "critical"
    assert finding["run_type"] == "weekly"
    assert "404" in finding["title"]
    assert "example.com/missing-page" in finding["title"]
    assert finding["url"] == "https://example.com/missing-page"


def test_detect_404_deduplicates_within_run(test_conn):
    """Test that duplicate 404s in the same run are deduped."""
    # Create a customer
    cursor = test_conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
        ("Test Customer", "active"),
    )
    customer_id = cursor.lastrowid

    # Create multiple 404 results for the same URL
    fetch_results = [
        PageFetchResult(
            url="https://example.com/missing",
            status_code=404,
            final_url="https://example.com/missing",
            body=None,
            error=None,
            error_type=None,
        ),
        PageFetchResult(
            url="https://example.com/missing",
            status_code=404,
            final_url="https://example.com/missing",
            body=None,
            error=None,
            error_type=None,
        ),
    ]

    # Run 404 detection
    detect_new_404s(
        conn=test_conn,
        run_id="test-run-002",
        customer_id=customer_id,
        fetch_results=fetch_results,
        period="2026-W05",
    )

    # Verify only one finding was created
    findings = fetch_all(
        test_conn,
        "SELECT * FROM findings WHERE customer_id=? AND category=?",
        (customer_id, "indexability"),
    )

    assert len(findings) == 1


def test_detect_404_ignores_success_responses(test_conn):
    """Test that successful fetches don't create findings."""
    # Create a customer
    cursor = test_conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
        ("Test Customer", "active"),
    )
    customer_id = cursor.lastrowid

    # Create successful fetch results
    fetch_results = [
        PageFetchResult(
            url="https://example.com/page",
            status_code=200,
            final_url="https://example.com/page",
            body="<html>Test</html>",
            error=None,
            error_type=None,
        ),
        PageFetchResult(
            url="https://example.com/another",
            status_code=301,
            final_url="https://example.com/redirect",
            body=None,
            error=None,
            error_type=None,
        ),
    ]

    # Run 404 detection
    detect_new_404s(
        conn=test_conn,
        run_id="test-run-003",
        customer_id=customer_id,
        fetch_results=fetch_results,
        period="2026-W05",
    )

    # Verify no findings were created
    findings = fetch_all(
        test_conn,
        "SELECT * FROM findings WHERE customer_id=?",
        (customer_id,),
    )

    assert len(findings) == 0


def test_detect_404_multiple_different_urls(test_conn):
    """Test that multiple different 404s all create findings."""
    # Create a customer
    cursor = test_conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
        ("Test Customer", "active"),
    )
    customer_id = cursor.lastrowid

    # Create multiple different 404 results
    fetch_results = [
        PageFetchResult(
            url="https://example.com/missing1",
            status_code=404,
            final_url="https://example.com/missing1",
            body=None,
            error=None,
            error_type=None,
        ),
        PageFetchResult(
            url="https://example.com/missing2",
            status_code=404,
            final_url="https://example.com/missing2",
            body=None,
            error=None,
            error_type=None,
        ),
        PageFetchResult(
            url="https://example.com/missing3",
            status_code=404,
            final_url="https://example.com/missing3",
            body=None,
            error=None,
            error_type=None,
        ),
    ]

    # Run 404 detection
    detect_new_404s(
        conn=test_conn,
        run_id="test-run-004",
        customer_id=customer_id,
        fetch_results=fetch_results,
        period="2026-W05",
    )

    # Verify all three findings were created
    findings = fetch_all(
        test_conn,
        "SELECT * FROM findings WHERE customer_id=? AND category=? ORDER BY url",
        (customer_id, "indexability"),
    )

    assert len(findings) == 3
    assert "missing1" in findings[0]["url"]
    assert "missing2" in findings[1]["url"]
    assert "missing3" in findings[2]["url"]


def test_detect_404_deduplicates_across_runs(test_conn):
    """Test that repeat 404s are deduped across runs (same period)."""
    # Create a customer
    cursor = test_conn.execute(
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))",
        ("Test Customer", "active"),
    )
    customer_id = cursor.lastrowid

    # Create a 404 result
    fetch_results = [
        PageFetchResult(
            url="https://example.com/broken",
            status_code=404,
            final_url="https://example.com/broken",
            body=None,
            error=None,
            error_type=None,
        )
    ]

    # Run 404 detection twice with same period
    detect_new_404s(
        conn=test_conn,
        run_id="test-run-005a",
        customer_id=customer_id,
        fetch_results=fetch_results,
        period="2026-W05",
    )

    detect_new_404s(
        conn=test_conn,
        run_id="test-run-005b",
        customer_id=customer_id,
        fetch_results=fetch_results,
        period="2026-W05",
    )

    # Verify only one finding exists (deduped by dedupe_key)
    findings = fetch_all(
        test_conn,
        "SELECT * FROM findings WHERE customer_id=? AND category=?",
        (customer_id, "indexability"),
    )

    assert len(findings) == 1
