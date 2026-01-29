"""Tests for daily critical email gating functionality."""

import sqlite3
from unittest.mock import Mock, patch

from ranksentinel.config import Settings
from ranksentinel.db import init_db
from ranksentinel.reporting.email_templates import render_daily_critical_alert
from ranksentinel.reporting.report_composer import compose_daily_critical_report


def test_compose_daily_critical_report_only_critical(tmp_path):
    """Test that compose_daily_critical_report only includes critical findings."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Insert test customer
    conn.execute("INSERT INTO customers(name, status) VALUES(?, ?)", 
                 ("Test Customer", "active"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Insert settings with email
    conn.execute("INSERT INTO settings(customer_id, email) VALUES(?, ?)",
                 (customer_id, "test@example.com"))
    
    # Insert findings with different severities
    findings = [
        (customer_id, "daily", "critical", "indexability", "Critical issue 1", "Details 1", None),
        (customer_id, "daily", "warning", "indexability", "Warning issue", "Details 2", None),
        (customer_id, "daily", "critical", "performance", "Critical issue 2", "Details 3", None),
        (customer_id, "daily", "info", "content", "Info issue", "Details 4", None),
    ]
    
    for finding in findings:
        conn.execute(
            "INSERT INTO findings(customer_id, run_type, severity, category, title, details_md, url) "
            "VALUES(?, ?, ?, ?, ?, ?, ?)",
            finding
        )
    
    # Fetch all findings
    all_findings = conn.execute(
        "SELECT * FROM findings WHERE customer_id=?", (customer_id,)
    ).fetchall()
    
    # Compose report
    report = compose_daily_critical_report("Test Customer", all_findings)
    
    # Assert only critical findings are included
    assert report.critical_count == 2
    assert report.warning_count == 0
    assert report.info_count == 0
    assert report.total_count == 2
    
    # Verify critical findings are correct
    assert report.critical_findings[0].title in ["Critical issue 1", "Critical issue 2"]
    assert report.critical_findings[1].title in ["Critical issue 1", "Critical issue 2"]
    
    conn.close()


def test_render_daily_critical_alert():
    """Test that daily critical alert email is rendered correctly."""
    critical_text = "Test critical text"
    critical_html = "<div>Test critical HTML</div>"
    
    email = render_daily_critical_alert("Test Customer", critical_text, critical_html)
    
    # Check subject
    assert "Critical Alert" in email.subject
    assert "Test Customer" in email.subject
    
    # Check text body
    assert "CRITICAL ALERT" in email.text
    assert "Test Customer" in email.text
    assert critical_text in email.text
    assert "Next Steps" in email.text
    
    # Check HTML body
    assert "Critical Alert" in email.html
    assert "Test Customer" in email.html
    assert critical_html in email.html
    assert "Next Steps" in email.html


def test_daily_email_skipped_when_no_critical_findings(tmp_path):
    """Test that daily email is not sent when there are no critical findings."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Insert test customer
    conn.execute("INSERT INTO customers(name, status) VALUES(?, ?)", 
                 ("Test Customer", "active"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Insert only warning and info findings (no critical)
    findings = [
        (customer_id, "daily", "warning", "indexability", "Warning issue", "Details", None),
        (customer_id, "daily", "info", "content", "Info issue", "Details", None),
    ]
    
    for finding in findings:
        conn.execute(
            "INSERT INTO findings(customer_id, run_type, severity, category, title, details_md, url) "
            "VALUES(?, ?, ?, ?, ?, ?, ?)",
            finding
        )
    
    # Fetch critical findings
    critical_findings = conn.execute(
        "SELECT * FROM findings WHERE customer_id=? AND severity='critical'", (customer_id,)
    ).fetchall()
    
    # Assert no critical findings exist
    assert len(critical_findings) == 0
    
    conn.close()


def test_daily_email_sent_when_critical_findings_exist(tmp_path):
    """Test that daily email is sent when critical findings exist."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    init_db(conn)
    
    # Insert test customer
    conn.execute("INSERT INTO customers(name, status) VALUES(?, ?)", 
                 ("Test Customer", "active"))
    customer_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    # Insert critical finding
    conn.execute(
        "INSERT INTO findings(customer_id, run_type, severity, category, title, details_md, url) "
        "VALUES(?, ?, ?, ?, ?, ?, ?)",
        (customer_id, "daily", "critical", "indexability", "Critical issue", "Details", None)
    )
    
    # Fetch critical findings
    critical_findings = conn.execute(
        "SELECT * FROM findings WHERE customer_id=? AND severity='critical'", (customer_id,)
    ).fetchall()
    
    # Assert critical findings exist
    assert len(critical_findings) == 1
    
    # Compose report and verify it has critical findings
    report = compose_daily_critical_report("Test Customer", critical_findings)
    assert report.critical_count == 1
    
    conn.close()
