"""Utilities for creating and persisting findings."""

import sqlite3
from datetime import datetime, timezone

from ranksentinel.db import execute, generate_finding_dedupe_key
from ranksentinel.reporting.severity import CRITICAL, INFO, WARNING, Severity
from ranksentinel.runner.logging_utils import log_structured


def insert_finding(
    conn: sqlite3.Connection,
    run_id: str,
    customer_id: int,
    run_type: str,
    severity: Severity,
    category: str,
    title: str,
    details_md: str,
    url: str | None,
    period: str,
) -> int | None:
    """Insert a finding with deduplication.
    
    Args:
        conn: Database connection
        run_id: Unique run identifier for logging
        customer_id: Customer ID
        run_type: 'daily' or 'weekly'
        severity: Severity object (CRITICAL, WARNING, INFO)
        category: Finding category (e.g., 'indexability', 'performance')
        title: Finding title
        details_md: Markdown details
        url: URL associated with the finding (optional)
        period: Period identifier (e.g., '2026-01-29' for daily, '2026-W05' for weekly)
    
    Returns:
        ID of inserted finding or None if dedupe prevented insertion
    """
    dedupe_key = generate_finding_dedupe_key(
        customer_id, run_type, category, title, url, period
    )
    
    created_at = datetime.now(timezone.utc).isoformat()
    
    try:
        finding_id = execute(
            conn,
            "INSERT INTO findings(customer_id, run_type, severity, category, title, details_md, url, dedupe_key, created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (customer_id, run_type, severity.key, category, title, details_md, url, dedupe_key, created_at),
        )
        
        log_structured(
            run_id,
            run_type=run_type,
            stage="finding",
            status="created",
            customer_id=customer_id,
            severity=severity.key,
            category=category,
            title=title,
            url=url,
            finding_id=finding_id,
        )
        
        return finding_id
        
    except sqlite3.IntegrityError:
        # Dedupe key collision - finding already exists
        log_structured(
            run_id,
            run_type=run_type,
            stage="finding",
            status="deduped",
            customer_id=customer_id,
            severity=severity.key,
            category=category,
            title=title,
            url=url,
        )
        return None
