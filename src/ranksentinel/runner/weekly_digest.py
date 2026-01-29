from datetime import datetime, timezone

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, fetch_one, init_db
from ranksentinel.http_client import fetch_text
from ranksentinel.runner.link_checker import find_broken_links
from ranksentinel.runner.normalization import normalize_url


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        
        execute(
            conn,
            "INSERT INTO findings(customer_id,run_type,severity,category,title,details_md,url,created_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (
                customer_id,
                run_type,
                "warning",
                "links",
                "Broken internal links detected",
                details_md,
                None,
                detected_at,
            ),
        )


def run(settings: Settings) -> None:
    """Weekly digest with broken link detection.
    
    Full weekly digest logic is implemented in later phases.
    """
    conn = connect(settings)
    try:
        init_db(conn)
        customers = fetch_all(conn, "SELECT id FROM customers WHERE status='active'")

        for c in customers:
            customer_id = int(c["id"])
            
            # Detect broken internal links
            detect_broken_internal_links(
                conn,
                customer_id,
                "weekly",
                max_pages_to_check=20,
                max_links_per_page=50,
            )
            
            # Bootstrap placeholder finding
            execute(
                conn,
                "INSERT INTO findings(customer_id,run_type,severity,category,title,details_md,url,created_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (
                    customer_id,
                    "weekly",
                    "info",
                    "bootstrap",
                    "Weekly digest executed (bootstrap)",
                    "This is the bootstrap weekly digest placeholder.\
",
                    None,
                    now_iso(),
                ),
            )
    finally:
        conn.close()
