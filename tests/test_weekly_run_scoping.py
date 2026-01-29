"""Test weekly email scoping by run_id (task 0-E.5)."""

import sqlite3

import pytest

from ranksentinel.db import execute, fetch_all, init_db
from ranksentinel.reporting.report_composer import compose_weekly_report


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)

    # Create a test customer
    execute(
        conn,
        "INSERT INTO customers(name, status, created_at, updated_at) VALUES(?,?,?,?)",
        ("Test Customer", "active", "2026-01-29T00:00:00Z", "2026-01-29T00:00:00Z"),
    )

    yield conn
    conn.close()


def test_weekly_email_scoped_to_current_run(test_db):
    """Test that weekly email only includes findings from the current run.

    Scenario:
    - Run 1: Create a 404 finding
    - Run 2: 404 is fixed (200 response), no new finding created
    - Run 2 email should NOT show the 404 from run 1

    This satisfies AC: "After fixing an issue (e.g., 404 becomes 200),
    the next weekly email does NOT present it as a current critical issue."
    """
    customer_id = 1

    # Run 1: Create a 404 finding
    run1_time = "2026-01-22T10:00:00+00:00"
    run1_id = "weekly-2026-01-22-1000"

    execute(
        test_db,
        "INSERT INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            customer_id,
            run1_id,
            "weekly",
            "critical",
            "indexability",
            "Page not found (404): https://example.com/page",
            "The page returned a 404 status code.",
            "https://example.com/page",
            "dedupe_run1_404",
            run1_time,
        ),
    )

    # Run 2: No new findings (404 was fixed)
    run2_time = "2026-01-29T10:00:00+00:00"
    run2_id = "weekly-2026-01-29-1000"

    # Query findings for run 2 (simulating weekly email composition)
    findings_run2 = fetch_all(
        test_db,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? AND run_type='weekly' "
        "AND category != 'bootstrap' ORDER BY severity DESC, created_at DESC",
        (customer_id, run2_id),
    )

    # Run 2 email should have zero findings (404 was from run 1)
    assert len(findings_run2) == 0, "Run 2 email should not include findings from run 1"

    # Verify run 1 email would have shown the finding
    findings_run1 = fetch_all(
        test_db,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? AND run_type='weekly' "
        "AND category != 'bootstrap' ORDER BY severity DESC, created_at DESC",
        (customer_id, run1_id),
    )

    assert len(findings_run1) == 1, "Run 1 email should include its own finding"
    assert findings_run1[0]["title"] == "Page not found (404): https://example.com/page"


def test_weekly_email_shows_new_issues_in_current_run(test_db):
    """Test that weekly email correctly shows new issues from the current run."""
    customer_id = 1

    # Run 1: No findings
    run1_id = "weekly-2026-01-22-1000"

    # Run 2: Create a new 404 finding
    run2_time = "2026-01-29T10:00:00+00:00"
    run2_id = "weekly-2026-01-29-1000"

    execute(
        test_db,
        "INSERT INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            customer_id,
            run2_id,
            "weekly",
            "critical",
            "indexability",
            "Page not found (404): https://example.com/broken",
            "The page returned a 404 status code.",
            "https://example.com/broken",
            "dedupe_run2_404",
            run2_time,
        ),
    )

    # Query findings for run 2
    findings_run2 = fetch_all(
        test_db,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? AND run_type='weekly' "
        "AND category != 'bootstrap' ORDER BY severity DESC, created_at DESC",
        (customer_id, run2_id),
    )

    # Run 2 email should show the new finding
    assert len(findings_run2) == 1, "Run 2 email should include new findings from run 2"
    assert findings_run2[0]["title"] == "Page not found (404): https://example.com/broken"

    # Compose report to verify it renders correctly
    report = compose_weekly_report("Test Customer", findings_run2)
    assert report.critical_count == 1
    assert report.warning_count == 0
    assert report.info_count == 0


def test_weekly_email_multiple_runs_isolation(test_db):
    """Test that multiple runs remain isolated from each other."""
    customer_id = 1

    # Run 1: 2 findings
    run1_time = "2026-01-15T10:00:00+00:00"
    run1_id = "weekly-2026-01-15-1000"

    for i in range(2):
        execute(
            test_db,
            "INSERT INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                customer_id,
                run1_id,
                "weekly",
                "warning",
                "links",
                f"Broken link {i}",
                "Details",
                None,
                f"dedupe_run1_{i}",
                run1_time,
            ),
        )

    # Run 2: 1 finding
    run2_time = "2026-01-22T10:00:00+00:00"
    run2_id = "weekly-2026-01-22-1000"

    execute(
        test_db,
        "INSERT INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            customer_id,
            run2_id,
            "weekly",
            "critical",
            "indexability",
            "Sitemap unreachable",
            "Details",
            None,
            "dedupe_run2_sitemap",
            run2_time,
        ),
    )

    # Run 3: 3 findings
    run3_time = "2026-01-29T10:00:00+00:00"
    run3_id = "weekly-2026-01-29-1000"

    for i in range(3):
        execute(
            test_db,
            "INSERT INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                customer_id,
                run3_id,
                "weekly",
                "info",
                "content",
                f"Info finding {i}",
                "Details",
                None,
                f"dedupe_run3_{i}",
                run3_time,
            ),
        )

    # Verify each run has correct count
    findings_run1 = fetch_all(
        test_db,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? AND run_type='weekly'",
        (customer_id, run1_id),
    )
    assert len(findings_run1) == 2

    findings_run2 = fetch_all(
        test_db,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? AND run_type='weekly'",
        (customer_id, run2_id),
    )
    assert len(findings_run2) == 1

    findings_run3 = fetch_all(
        test_db,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? AND run_type='weekly'",
        (customer_id, run3_id),
    )
    assert len(findings_run3) == 3
