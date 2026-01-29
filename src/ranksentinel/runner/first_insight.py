"""First Insight report generation.

This module provides functionality to generate and send an immediate
onboarding report for new customers, helping them see value quickly
without waiting for the weekly schedule.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from sqlite3 import Connection
from typing import Any

from ranksentinel.db import execute, fetch_all, fetch_one, generate_finding_dedupe_key, get_latest_artifact, store_artifact
from ranksentinel.http_client import fetch_text
from ranksentinel.runner.daily_checks import (
    check_canonical_drift,
    check_noindex_regression,
    check_psi_regression,
    check_robots_txt_change,
    check_title_change,
    fetch_psi_metrics,
    fetch_sitemap,
    fetch_url,
    sha256_text,
)
from ranksentinel.runner.logging_utils import generate_run_id, log_stage, log_structured
from ranksentinel.runner.normalization import normalize_url
from ranksentinel.runner.sitemap_parser import extract_url_count
from ranksentinel.reporting.report_composer import compose_weekly_report, CoverageStats


def now_iso() -> str:
    """Return current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def run_first_insight_checks(conn: Connection, customer_id: int, run_id: str, psi_api_key: str | None = None) -> None:
    """Run first insight data collection for a customer.
    
    Collects high-signal checks:
    - Key pages: status/redirect/title/canonical/noindex + content hash
    - Robots.txt + sitemap hash
    - Optional PSI on key pages (if API key provided and enabled)
    
    Writes findings with run_type='first_insight'.
    
    Args:
        conn: Database connection
        customer_id: Customer ID to run checks for
        run_id: Unique run identifier
        psi_api_key: Optional PageSpeed Insights API key
    """
    log_structured(run_id, run_type="first_insight", stage="init", status="start", customer_id=customer_id)
    
    # Get customer settings
    settings_row = fetch_one(
        conn,
        "SELECT sitemap_url, psi_enabled, psi_urls_limit, psi_confirm_runs, "
        "psi_perf_drop_threshold, psi_lcp_increase_threshold_ms "
        "FROM settings WHERE customer_id=?",
        (customer_id,),
    )
    
    # Convert to dict with defaults
    if settings_row:
        customer_settings = dict(settings_row)
    else:
        customer_settings = {
            "sitemap_url": None,
            "psi_enabled": 1,
            "psi_urls_limit": 5,
            "psi_confirm_runs": 2,
            "psi_perf_drop_threshold": 10,
            "psi_lcp_increase_threshold_ms": 500,
        }
    
    # Determine robots.txt base URL
    robots_base_url = None
    if customer_settings.get("sitemap_url"):
        from urllib.parse import urlparse
        parsed = urlparse(str(customer_settings["sitemap_url"]))
        robots_base_url = f"{parsed.scheme}://{parsed.netloc}"
    else:
        # Fall back to first target URL's base
        first_target = fetch_one(
            conn,
            "SELECT url FROM targets WHERE customer_id=? AND is_key=1 LIMIT 1",
            (customer_id,),
        )
        if first_target:
            from urllib.parse import urlparse
            parsed = urlparse(str(first_target["url"]))
            robots_base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Fetch and store robots.txt
    if robots_base_url:
        robots_url = f"{robots_base_url}/robots.txt"
        try:
            with log_stage(run_id, "fetch_robots", customer_id=customer_id, url=robots_url):
                robots_result = fetch_text(robots_url, timeout=10, attempts=2, base_delay=1.0)
            
            if not robots_result.is_error:
                robots_content = robots_result.body or ""
                robots_sha = sha256_text(robots_content)
                fetched_at = now_iso()
                
                # Store as baseline (no comparison on first run)
                store_artifact(
                    conn, customer_id, "robots_txt", robots_base_url,
                    robots_sha, robots_content, fetched_at
                )
                
                log_structured(
                    run_id, customer_id=customer_id, stage="fetch_robots",
                    status="success", url=robots_url, sha=robots_sha[:12]
                )
            else:
                log_structured(
                    run_id, customer_id=customer_id, stage="fetch_robots",
                    status="error", url=robots_url, error=robots_result.error
                )
        except Exception as e:  # noqa: BLE001
            log_structured(
                run_id, customer_id=customer_id, stage="fetch_robots",
                status="error", url=robots_url, error=str(e)
            )
    
    # Fetch and store sitemap
    sitemap_url = customer_settings.get("sitemap_url")
    if sitemap_url:
        try:
            with log_stage(run_id, "fetch_sitemap", customer_id=customer_id, url=sitemap_url):
                sitemap_result = fetch_sitemap(str(sitemap_url))
            
            if not sitemap_result["is_error"]:
                sitemap_content = sitemap_result["body"] or ""
                sitemap_sha = sha256_text(sitemap_content)
                fetched_at = now_iso()
                
                # Extract URL count
                url_count_data = extract_url_count(sitemap_content)
                url_count = url_count_data.get("url_count", 0)
                sitemap_type = url_count_data.get("sitemap_type", "unknown")
                
                # Store as baseline (no comparison on first run)
                store_artifact(
                    conn, customer_id, "sitemap", str(sitemap_url),
                    sitemap_sha, sitemap_content, fetched_at
                )
                
                log_structured(
                    run_id, customer_id=customer_id, stage="fetch_sitemap",
                    status="success", url=sitemap_url, sha=sitemap_sha[:12],
                    url_count=url_count, sitemap_type=sitemap_type
                )
                
                # Create info finding about baseline sitemap
                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                dedupe_key = generate_finding_dedupe_key(
                    customer_id, "first_insight", "indexability", "Sitemap baseline established", None, period
                )
                
                details = f"""Sitemap baseline captured for future monitoring.

- **URL count:** {url_count}
- **Sitemap URL:** `{sitemap_url}`
- **Type:** {sitemap_type}

Future runs will detect changes to this sitemap."""
                
                execute(
                    conn,
                    "INSERT OR IGNORE INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        customer_id,
                        run_id,
                        "first_insight",
                        "info",
                        "indexability",
                        "Sitemap baseline established",
                        details,
                        None,
                        dedupe_key,
                        fetched_at,
                    ),
                )
            else:
                # Sitemap error - create warning finding
                fetched_at = now_iso()
                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                dedupe_key = generate_finding_dedupe_key(
                    customer_id, "first_insight", "indexability", "Sitemap unreachable", None, period
                )
                
                details = f"""Sitemap could not be fetched during initial setup.

- **URL:** `{sitemap_url}`
- **Error:** {sitemap_result['error']}
- **Error Type:** {sitemap_result['error_type']}

Please verify the sitemap URL is correct and accessible."""
                
                execute(
                    conn,
                    "INSERT OR IGNORE INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        customer_id,
                        run_id,
                        "first_insight",
                        "warning",
                        "indexability",
                        "Sitemap unreachable",
                        details,
                        None,
                        dedupe_key,
                        fetched_at,
                    ),
                )
                
                log_structured(
                    run_id, customer_id=customer_id, stage="fetch_sitemap",
                    status="error", url=sitemap_url, error=sitemap_result['error']
                )
        except Exception as e:  # noqa: BLE001
            log_structured(
                run_id, customer_id=customer_id, stage="fetch_sitemap",
                status="error", url=sitemap_url, error=str(e)
            )
    
    # Fetch key pages
    targets = fetch_all(
        conn,
        "SELECT url FROM targets WHERE customer_id=? AND is_key=1",
        (customer_id,),
    )
    
    # Track PSI-checked URLs (limit to psi_urls_limit)
    psi_count = 0
    psi_limit = int(customer_settings.get("psi_urls_limit", 5))
    psi_enabled = bool(customer_settings.get("psi_enabled", 1))
    
    for t in targets:
        raw_url = str(t["url"])
        # Normalize URL for consistency
        url = normalize_url(raw_url, raw_url)
        if not url:
            log_structured(run_id, customer_id=customer_id, stage="validate_url", status="skip", reason="invalid_url")
            continue
        
        try:
            with log_stage(run_id, "fetch_url", customer_id=customer_id, url=url):
                data = fetch_url(url)
        except Exception as e:  # noqa: BLE001
            log_structured(run_id, customer_id=customer_id, stage="fetch_url", status="error", url=url, error=str(e))
            continue
        
        fetched_at = now_iso()
        
        # Store snapshot
        execute(
            conn,
            "INSERT INTO snapshots(customer_id,url,run_type,run_id,fetched_at,status_code,"
            "final_url,redirect_chain,title,canonical,meta_robots,content_hash) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                customer_id,
                url,
                "first_insight",
                run_id,
                fetched_at,
                data["status_code"],
                data["final_url"],
                json.dumps(data["redirect_chain"]),
                data["title"],
                data["canonical"],
                data["meta_robots"],
                data["content_hash"],
            ),
        )
        
        # Store baseline artifacts (no comparison on first run, but establish baseline)
        curr_meta_sha = sha256_text(data["meta_robots"])
        store_artifact(conn, customer_id, "meta_robots", url, curr_meta_sha, data["meta_robots"], fetched_at)
        
        curr_canonical_sha = sha256_text(data["canonical"])
        store_artifact(conn, customer_id, "canonical", url, curr_canonical_sha, data["canonical"], fetched_at)
        
        curr_title_sha = sha256_text(data["title"])
        store_artifact(conn, customer_id, "title", url, curr_title_sha, data["title"], fetched_at)
        
        # Create info finding about baseline capture
        period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
        dedupe_key = generate_finding_dedupe_key(
            customer_id, "first_insight", "content", "Key page baseline captured", url, period
        )
        
        details = f"""Baseline snapshot captured for monitoring.

- **Title:** {data['title'] or '(empty)'}
- **Canonical:** {data['canonical'] or '(none)'}
- **Meta robots:** {data['meta_robots'] or '(none)'}
- **Status:** {data['status_code']}

Future runs will detect changes to this page."""
        
        execute(
            conn,
            "INSERT OR IGNORE INTO findings(customer_id,run_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                customer_id,
                run_id,
                "first_insight",
                "info",
                "content",
                "Key page baseline captured",
                details,
                url,
                dedupe_key,
                fetched_at,
            ),
        )
        
        # PSI checks (optional, limited)
        if psi_enabled and psi_count < psi_limit and psi_api_key:
            with log_stage(run_id, "fetch_psi", customer_id=customer_id, url=url):
                psi_metrics = fetch_psi_metrics(url, psi_api_key)
            
            if psi_metrics:
                # Store as baseline (no regression check on first run)
                execute(
                    conn,
                    "INSERT INTO psi_results(customer_id,url,run_type,fetched_at,perf_score,"
                    "lcp_ms,cls_score,inp_ms,is_regression,is_confirmed,regression_type,raw_json) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        customer_id,
                        url,
                        "first_insight",
                        fetched_at,
                        psi_metrics.get("perf_score"),
                        psi_metrics.get("lcp_ms"),
                        psi_metrics.get("cls_score"),
                        psi_metrics.get("inp_ms"),
                        0,  # is_regression
                        0,  # is_confirmed
                        None,  # regression_type
                        psi_metrics.get("raw_json"),
                    ),
                )
                
                psi_count += 1
                
                log_structured(
                    run_id, customer_id=customer_id, stage="fetch_psi",
                    status="success", url=url, perf_score=psi_metrics.get("perf_score")
                )
    
    log_structured(run_id, run_type="first_insight", stage="complete", status="success", customer_id=customer_id)


def trigger_first_insight_report(
    conn: Connection, 
    customer_id: int, 
    psi_api_key: str | None = None,
    mailgun_client: Any | None = None,
    recipient_email: str | None = None,
) -> dict[str, Any]:
    """Trigger generation and delivery of a First Insight report.
    
    Args:
        conn: Database connection
        customer_id: ID of the customer to generate report for
        psi_api_key: Optional PageSpeed Insights API key
        mailgun_client: Optional MailgunClient instance for sending emails
        recipient_email: Optional recipient email address
        
    Returns:
        Dict with run_id, findings count, and email delivery status
        
    Note:
        Implements idempotency: only one email per customer per day.
        Checks deliveries table for existing first_insight delivery today.
    """
    from ranksentinel.mailgun import send_and_log
    from ranksentinel.reporting.email_templates import render_first_insight
    
    run_id = generate_run_id()
    today = datetime.now(timezone.utc).date().isoformat()
    
    # Check for existing first_insight delivery today (idempotency)
    existing_delivery = fetch_one(
        conn,
        "SELECT id FROM deliveries WHERE customer_id=? AND run_type='first_insight' "
        "AND DATE(sent_at) = DATE(?) LIMIT 1",
        (customer_id, today),
    )
    
    if existing_delivery:
        log_structured(
            run_id, 
            run_type="first_insight", 
            stage="dedupe_check", 
            status="skipped", 
            customer_id=customer_id,
            reason="Already sent first_insight email today"
        )
        return {
            "run_id": run_id,
            "customer_id": customer_id,
            "email_sent": False,
            "dedupe_reason": "Already sent today",
        }
    
    # Run data collection
    run_first_insight_checks(conn, customer_id, run_id, psi_api_key)
    
    # Fetch findings for this run
    findings = fetch_all(
        conn,
        "SELECT * FROM findings WHERE customer_id=? AND run_id=? ORDER BY created_at DESC",
        (customer_id, run_id),
    )
    
    # Get customer name
    customer_row = fetch_one(conn, "SELECT name FROM customers WHERE id=?", (customer_id,))
    customer_name = customer_row["name"] if customer_row else f"Customer {customer_id}"
    
    # Compose report (reuse weekly composer)
    report = compose_weekly_report(customer_name, findings)
    
    result = {
        "run_id": run_id,
        "customer_id": customer_id,
        "findings_count": len(findings),
        "report": report,
        "email_sent": False,
    }
    
    # Send email if client and recipient provided
    if mailgun_client and recipient_email:
        try:
            # Render email using first_insight template
            report_text = report.to_text()
            report_html = report.to_html()
            email_msg = render_first_insight(customer_name, report_text, report_html)
            
            # Send and log delivery
            success = send_and_log(
                conn=conn,
                client=mailgun_client,
                customer_id=customer_id,
                run_type="first_insight",
                recipient=recipient_email,
                subject=email_msg.subject,
                text_body=email_msg.text,
                html_body=email_msg.html,
            )
            
            result["email_sent"] = success
            
            if success:
                log_structured(
                    run_id,
                    run_type="first_insight",
                    stage="send_email",
                    status="success",
                    customer_id=customer_id,
                    recipient=recipient_email,
                )
            else:
                log_structured(
                    run_id,
                    run_type="first_insight",
                    stage="send_email",
                    status="failed",
                    customer_id=customer_id,
                )
        except Exception as e:
            log_structured(
                run_id,
                run_type="first_insight",
                stage="send_email",
                status="error",
                customer_id=customer_id,
                error=str(e),
            )
            result["email_error"] = str(e)
    
    return result
