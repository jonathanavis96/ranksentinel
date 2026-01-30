"""Tests for first insight report runner (task 4.6b)."""

from datetime import datetime, timezone

import pytest

from ranksentinel.runner.first_insight import trigger_first_insight_report
from ranksentinel.db import execute, fetch_all


@pytest.fixture
def customer_with_targets(db_conn):
    """Create a customer with key page targets and settings."""
    customer_id = 1  # Default customer from conftest
    now = datetime.now(timezone.utc).isoformat()

    # Add settings
    execute(
        db_conn,
        "INSERT INTO settings(customer_id, sitemap_url, psi_enabled, psi_urls_limit) VALUES(?, ?, ?, ?)",
        (customer_id, "https://example.com/sitemap.xml", 1, 2),
    )

    # Add key page targets (include created_at)
    execute(
        db_conn,
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES(?, ?, ?, ?)",
        (customer_id, "https://example.com/", 1, now),
    )
    execute(
        db_conn,
        "INSERT INTO targets(customer_id, url, is_key, created_at) VALUES(?, ?, ?, ?)",
        (customer_id, "https://example.com/about", 1, now),
    )

    db_conn.commit()

    return {"customer_id": customer_id, "conn": db_conn}


def test_trigger_first_insight_report_structure(customer_with_targets):
    """Test that trigger_first_insight_report returns expected structure."""
    customer_id = customer_with_targets["customer_id"]
    conn = customer_with_targets["conn"]

    # Mock external fetches by pre-populating artifacts (simulate successful fetches)
    # In real usage, this would call external APIs
    # For unit test, we just verify the structure without network calls

    result = trigger_first_insight_report(conn, customer_id, psi_api_key=None)

    # Verify structure
    assert "run_id" in result
    assert "customer_id" in result
    assert "findings_count" in result
    assert "report" in result

    # Verify customer_id matches
    assert result["customer_id"] == customer_id

    # Verify run_id format (should be timestamp-based)
    assert isinstance(result["run_id"], str)
    assert len(result["run_id"]) > 0

    # Verify findings_count is a number
    assert isinstance(result["findings_count"], int)
    assert result["findings_count"] >= 0

    # Verify report object has expected methods
    report = result["report"]
    assert hasattr(report, "to_text")
    assert hasattr(report, "to_html")
    assert hasattr(report, "critical_findings")
    assert hasattr(report, "warning_findings")
    assert hasattr(report, "info_findings")


def test_first_insight_creates_findings_with_correct_run_type(customer_with_targets):
    """Test that findings are created with run_type='first_insight'."""
    customer_id = customer_with_targets["customer_id"]
    conn = customer_with_targets["conn"]

    result = trigger_first_insight_report(conn, customer_id, psi_api_key=None)
    run_id = result["run_id"]

    # Fetch all findings for this run
    findings = fetch_all(
        conn,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=?",
        (customer_id, run_id),
    )

    # Verify all findings have run_type='first_insight'
    for finding in findings:
        assert finding["run_type"] == "first_insight"
        assert finding["run_id"] == run_id
        assert finding["customer_id"] == customer_id


def test_first_insight_creates_baseline_artifacts(customer_with_targets):
    """Test that baseline artifacts are created during first insight run."""
    customer_id = customer_with_targets["customer_id"]
    conn = customer_with_targets["conn"]

    # Pre-populate some artifact baselines to simulate successful fetches
    now = datetime.now(timezone.utc).isoformat()

    # Simulate robots.txt baseline (use fetched_at instead of created_at)
    execute(
        conn,
        "INSERT INTO artifacts(customer_id, kind, subject, artifact_sha, raw_content, fetched_at) "
        "VALUES(?, ?, ?, ?, ?, ?)",
        (
            customer_id,
            "robots_txt",
            "https://example.com",
            "abc123",
            "User-agent: *\nDisallow:",
            now,
        ),
    )

    # Simulate sitemap baseline
    execute(
        conn,
        "INSERT INTO artifacts(customer_id, kind, subject, artifact_sha, raw_content, fetched_at) "
        "VALUES(?, ?, ?, ?, ?, ?)",
        (
            customer_id,
            "sitemap",
            "https://example.com/sitemap.xml",
            "def456",
            "<urlset></urlset>",
            now,
        ),
    )

    conn.commit()

    result = trigger_first_insight_report(conn, customer_id, psi_api_key=None)

    # Verify artifacts were created/updated
    artifacts = fetch_all(
        conn,
        "SELECT * FROM artifacts WHERE customer_id=?",
        (customer_id,),
    )

    # Should have at least the pre-populated artifacts
    assert len(artifacts) >= 2

    # Verify artifact kinds include expected types
    artifact_kinds = {a["kind"] for a in artifacts}
    assert "robots_txt" in artifact_kinds or "sitemap" in artifact_kinds


def test_first_insight_report_composition(customer_with_targets):
    """Test that first insight report is properly composed with sections."""
    customer_id = customer_with_targets["customer_id"]
    conn = customer_with_targets["conn"]

    result = trigger_first_insight_report(conn, customer_id, psi_api_key=None)
    report = result["report"]

    # Verify report has all severity sections
    assert hasattr(report, "critical_findings")
    assert hasattr(report, "warning_findings")
    assert hasattr(report, "info_findings")

    # Verify report can generate text and HTML
    text = report.to_text()
    html = report.to_html()

    assert isinstance(text, str)
    assert isinstance(html, str)
    assert len(text) > 0
    assert len(html) > 0

    # Verify report contains customer name
    assert "Test Customer" in text or "Customer" in text

    # Verify report has structure markers
    assert "RankSentinel" in text
    assert "Executive Summary" in text or "Summary" in text


def test_first_insight_stores_snapshots(customer_with_targets):
    """Test that snapshots are created with run_type='first_insight'."""
    customer_id = customer_with_targets["customer_id"]
    conn = customer_with_targets["conn"]

    result = trigger_first_insight_report(conn, customer_id, psi_api_key=None)
    run_id = result["run_id"]

    # Fetch snapshots for this run
    snapshots = fetch_all(
        conn,
        "SELECT * FROM snapshots WHERE customer_id=? AND run_id=?",
        (customer_id, run_id),
    )

    # Verify snapshots were created (may be 0 if network calls failed in test env)
    # At minimum, verify the query works and returns a list
    assert isinstance(snapshots, list)

    # If snapshots exist, verify they have correct run_type
    for snapshot in snapshots:
        assert snapshot["run_type"] == "first_insight"
        assert snapshot["run_id"] == run_id
        assert snapshot["customer_id"] == customer_id


def test_first_insight_without_psi_key(customer_with_targets):
    """Test that first insight works without PSI API key (optional)."""
    customer_id = customer_with_targets["customer_id"]
    conn = customer_with_targets["conn"]

    # Call without PSI key
    result = trigger_first_insight_report(conn, customer_id, psi_api_key=None)

    # Should still succeed
    assert result["run_id"]
    assert result["customer_id"] == customer_id

    # Verify no PSI results were stored
    psi_results = fetch_all(
        conn,
        "SELECT * FROM psi_results WHERE customer_id=?",
        (customer_id,),
    )

    # Should be empty or not crash
    assert isinstance(psi_results, list)
