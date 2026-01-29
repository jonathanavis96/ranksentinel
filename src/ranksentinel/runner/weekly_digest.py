import time
from datetime import datetime, timezone

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, fetch_one, generate_finding_dedupe_key, init_db
from ranksentinel.http_client import fetch_text
from ranksentinel.reporting.severity import CRITICAL
from ranksentinel.runner.finding_utils import insert_finding
from ranksentinel.runner.link_checker import find_broken_links
from ranksentinel.runner.logging_utils import generate_run_id, log_stage, log_structured, log_summary
from ranksentinel.runner.normalization import normalize_url
from ranksentinel.runner.page_fetcher import PageFetchResult, fetch_pages
from ranksentinel.runner.sitemap_parser import list_sitemap_urls


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def detect_new_404s(
    conn,
    run_id: str,
    customer_id: int,
    fetch_results: list[PageFetchResult],
    period: str,
) -> None:
    """Detect newly-broken pages (404s) from sampled crawl.
    
    Args:
        conn: Database connection
        run_id: Unique run identifier
        customer_id: Customer ID
        fetch_results: List of page fetch results
        period: Period identifier (e.g., '2026-W05')
    """
    # Track 404s seen in this run for deduplication
    seen_404s = set()
    
    for result in fetch_results:
        if result.is_404:
            # Normalize URL for deduplication (use result.url as both base and url since it's already absolute)
            normalized_url = normalize_url(result.url, result.url)
            
            # Skip if already seen in this run
            if normalized_url in seen_404s:
                log_structured(
                    run_id,
                    run_type="weekly",
                    stage="detect_404s",
                    status="deduped_in_run",
                    customer_id=customer_id,
                    url=normalized_url,
                )
                continue
            
            seen_404s.add(normalized_url)
            
            # Create finding for this 404
            insert_finding(
                conn=conn,
                run_id=run_id,
                customer_id=customer_id,
                run_type="weekly",
                severity=CRITICAL,
                category="indexability",
                title=f"Page not found (404): {normalized_url}",
                details_md=f"The page at `{normalized_url}` returned a 404 status code during the weekly crawl sample.",
                url=normalized_url,
                period=period,
            )
            
            log_structured(
                run_id,
                run_type="weekly",
                stage="detect_404s",
                status="found",
                customer_id=customer_id,
                url=normalized_url,
            )
    
    log_structured(
        run_id,
        run_type="weekly",
        stage="detect_404s",
        status="complete",
        customer_id=customer_id,
        total_404s=len(seen_404s),
    )


def detect_broken_internal_links(
    conn,
    customer_id: int,
    run_type: str,
    max_pages_to_check: int = 20,
    max_links_per_page: int = 50,
) -> None:
    """Detect broken internal links for a customer's targets.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        run_type: 'daily' or 'weekly'
        max_pages_to_check: Maximum number of pages to check for broken links
        max_links_per_page: Maximum links to check per page
    """
    # Get recent snapshots for this customer (limit to avoid blowups)
    snapshots = fetch_all(
        conn,
        "SELECT url, final_url FROM snapshots "
        "WHERE customer_id=? AND run_type=? AND status_code=200 "
        "ORDER BY fetched_at DESC LIMIT ?",
        (customer_id, run_type, max_pages_to_check),
    )
    
    detected_at = now_iso()
    total_broken = 0
    
    for snapshot in snapshots:
        raw_url = str(snapshot["url"])
        # Normalize URL for consistency
        source_url = normalize_url(raw_url, raw_url)
        if not source_url:
            continue
        
        # Fetch the page content
        result = fetch_text(source_url, timeout=20, attempts=2, base_delay=1.0)
        
        if result.is_error or not result.body:
            continue
        
        # Find broken links on this page
        broken_links = find_broken_links(
            source_url,
            result.body,
            max_links_to_check=max_links_per_page,
            timeout_s=10,
        )
        
        # Store broken links in database (URLs already normalized by link_checker)
        for target_url, status_code, error_msg in broken_links:
            execute(
                conn,
                "INSERT INTO broken_links(customer_id,source_url,target_url,status_code,error_message,run_type,detected_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    customer_id,
                    source_url,
                    target_url,
                    status_code,
                    error_msg or None,
                    run_type,
                    detected_at,
                ),
            )
            total_broken += 1
    
    # Generate finding if broken links were detected
    if total_broken > 0:
        # Get breakdown by source page
        breakdown = fetch_all(
            conn,
            "SELECT source_url, COUNT(*) as count FROM broken_links "
            "WHERE customer_id=? AND run_type=? AND detected_at=? "
            "GROUP BY source_url ORDER BY count DESC LIMIT 10",
            (customer_id, run_type, detected_at),
        )
        
        details_parts = [f"Found {total_broken} broken internal link(s).\n"]
        details_parts.append("**Top affected pages:**\n")
        
        for row in breakdown:
            details_parts.append(f"- `{row['source_url']}`: {row['count']} broken link(s)")
        
        if len(breakdown) >= 10:
            details_parts.append("\n*(showing top 10)*")
        
        details_md = "\n".join(details_parts)
        
        # Use ISO week format for weekly deduplication (e.g., '2026-W04')
        period = datetime.fromisoformat(detected_at).strftime('%Y-W%U')
        dedupe_key = generate_finding_dedupe_key(
            customer_id, run_type, "links", "Broken internal links detected", None, period
        )
        execute(
            conn,
            "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                customer_id,
                run_type,
                "warning",
                "links",
                "Broken internal links detected",
                details_md,
                None,
                dedupe_key,
                detected_at,
            ),
        )


def run(settings: Settings) -> None:
    """Weekly digest with broken link detection.
    
    Full weekly digest logic is implemented in later phases.
    """
    run_id = generate_run_id()
    start_time = time.time()
    
    log_structured(run_id, run_type="weekly", stage="init", status="start")
    
    conn = connect(settings)
    try:
        init_db(conn)
        customers = fetch_all(conn, "SELECT id FROM customers WHERE status='active'")
        
        log_structured(run_id, stage="init", status="complete", customer_count=len(customers))

        errors_by_customer = {}
        
        for c in customers:
            customer_id = int(c["id"])
            
            try:
                with log_stage(run_id, "process_customer", customer_id=customer_id):
                    # Fetch customer settings (sitemap_url, crawl_limit)
                    settings_row = fetch_one(
                        conn,
                        "SELECT sitemap_url, crawl_limit FROM settings WHERE customer_id=?",
                        (customer_id,)
                    )
                    
                    if not settings_row or not settings_row["sitemap_url"]:
                        log_structured(
                            run_id,
                            run_type="weekly",
                            stage="skip_customer",
                            status="info",
                            customer_id=customer_id,
                            reason="No sitemap_url configured"
                        )
                        continue
                    
                    sitemap_url = settings_row["sitemap_url"]
                    crawl_limit = settings_row["crawl_limit"] or 100
                    
                    # Fetch sitemap and extract URLs
                    with log_stage(run_id, "fetch_sitemap", customer_id=customer_id):
                        sitemap_result = fetch_text(sitemap_url, timeout=20, attempts=3)
                        
                        if not sitemap_result.ok:
                            log_structured(
                                run_id,
                                run_type="weekly",
                                stage="fetch_sitemap",
                                status="error",
                                customer_id=customer_id,
                                error=sitemap_result.error,
                            )
                            continue
                        
                        urls = list_sitemap_urls(sitemap_result.body)
                        
                        if not urls:
                            log_structured(
                                run_id,
                                run_type="weekly",
                                stage="fetch_sitemap",
                                status="warning",
                                customer_id=customer_id,
                                reason="No URLs found in sitemap"
                            )
                            continue
                    
                    # Fetch sampled pages (up to crawl_limit)
                    fetch_results = fetch_pages(
                        run_id=run_id,
                        customer_id=customer_id,
                        urls=urls,
                        crawl_limit=crawl_limit,
                    )
                    
                    log_structured(
                        run_id,
                        run_type="weekly",
                        stage="fetch_complete",
                        status="info",
                        customer_id=customer_id,
                        total_urls=len(urls),
                        fetched_count=len(fetch_results),
                        success_count=sum(1 for r in fetch_results if r.ok),
                    )
                    
                    # Detect new 404s from sampled crawl
                    with log_stage(run_id, "detect_404s", customer_id=customer_id):
                        detect_new_404s(
                            conn,
                            run_id,
                            customer_id,
                            fetch_results,
                            period=datetime.fromisoformat(now_iso()).strftime('%Y-W%U'),
                        )
                    
                    # Detect broken internal links
                    with log_stage(run_id, "detect_broken_links", customer_id=customer_id):
                        detect_broken_internal_links(
                            conn,
                            customer_id,
                            "weekly",
                            max_pages_to_check=20,
                            max_links_per_page=50,
                        )
                
                    # Bootstrap placeholder finding
                    bootstrap_time = now_iso()
                    period = datetime.fromisoformat(bootstrap_time).strftime('%Y-W%U')
                    dedupe_key = generate_finding_dedupe_key(
                        customer_id, "weekly", "bootstrap", "Weekly digest executed (bootstrap)", None, period
                    )
                    execute(
                        conn,
                        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                        "VALUES(?,?,?,?,?,?,?,?,?)",
                        (
                            customer_id,
                            "weekly",
                            "info",
                            "bootstrap",
                            "Weekly digest executed (bootstrap)",
                            "This is the bootstrap weekly digest placeholder.\
",
                            None,
                            dedupe_key,
                            bootstrap_time,
                        ),
                    )
            except Exception as e:  # noqa: BLE001
                # Catch per-customer errors and record them, then continue to next customer
                error_msg = f"Customer {customer_id} processing failed: {type(e).__name__}: {e}"
                log_structured(run_id, customer_id=customer_id, stage="process_customer", status="error", error=error_msg)
                errors_by_customer[customer_id] = error_msg
                # Log error to database for debugging
                try:
                    error_time = now_iso()
                    period = datetime.fromisoformat(error_time).strftime('%Y-W%U')
                    dedupe_key = generate_finding_dedupe_key(
                        customer_id, "weekly", "system", "Weekly run processing error", None, period
                    )
                    execute(
                        conn,
                        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                        "VALUES(?,?,?,?,?,?,?,?,?)",
                        (
                            customer_id,
                            "weekly",
                            "critical",
                            "system",
                            "Weekly run processing error",
                            f"An error occurred during weekly processing:\\n\\n```\\n{error_msg}\\n```",
                            None,
                            dedupe_key,
                            error_time,
                        ),
                    )
                except Exception as db_error:  # noqa: BLE001
                    log_structured(run_id, customer_id=customer_id, stage="log_error_to_db", status="error", error=str(db_error))
        
        # Calculate elapsed time and print summary
        total_elapsed_ms = int((time.time() - start_time) * 1000)
        total_customers = len(customers)
        failed_customers = len(errors_by_customer)
        successful_customers = total_customers - failed_customers
        
        log_summary(run_id, "weekly", total_customers, successful_customers, failed_customers, total_elapsed_ms)
        
        if errors_by_customer:
            log_structured(run_id, stage="summary", failed_customer_ids=",".join(str(cid) for cid in errors_by_customer.keys()))
    finally:
        conn.close()
