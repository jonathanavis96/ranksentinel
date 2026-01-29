import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from ranksentinel.config import Settings
from ranksentinel.db import (
    connect,
    execute,
    fetch_all,
    fetch_one,
    generate_finding_dedupe_key,
    get_latest_artifact,
    init_db,
    store_artifact,
)
from ranksentinel.http_client import fetch_text
from ranksentinel.runner.logging_utils import generate_run_id, log_stage, log_structured, log_summary
from ranksentinel.runner.normalization import (
    extract_canonical,
    extract_meta_robots,
    extract_title,
    normalize_html_to_text,
    normalize_url,
)
from ranksentinel.runner.sitemap_parser import extract_url_count


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def fetch_url(url: str, timeout_s: int = 20) -> dict[str, Any]:
    """Fetch a URL and extract SEO-relevant metadata.

    Uses http_client.fetch_text for consistent retry/timeout behavior.
    """
    result = fetch_text(url, timeout=timeout_s, attempts=3, base_delay=1.0)

    if result.is_error:
        # Log the error and raise to maintain existing behavior
        raise Exception(f"Failed to fetch {url}: {result.error} ({result.error_type})")

    html = result.body or ""
    text = normalize_html_to_text(html) if html else ""
    meta_robots = extract_meta_robots(html) if html else ""
    canonical = extract_canonical(html) if html else ""
    title = extract_title(html) if html else ""

    return {
        "status_code": result.status_code,
        "final_url": result.final_url,
        "redirect_chain": result.redirect_chain,
        "content_hash": sha256_text(text),
        "meta_robots": meta_robots,
        "canonical": canonical,
        "title": title,
    }


def check_noindex_regression(
    conn,
    customer_id: int,
    url: str,
    current_meta_robots: str,
) -> tuple[str, str] | None:
    """Check if noindex was newly introduced.

    Returns (severity, details_md) tuple if regression found, None otherwise.
    """
    prev = fetch_one(
        conn,
        "SELECT meta_robots FROM snapshots WHERE customer_id=? AND url=? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, url),
    )

    if not prev:
        return None

    prev_robots = str(prev["meta_robots"] or "")
    curr_robots = current_meta_robots or ""

    prev_has_noindex = "noindex" in prev_robots.lower()
    curr_has_noindex = "noindex" in curr_robots.lower()

    if not prev_has_noindex and curr_has_noindex:
        details = f"""Key page now has `noindex` directive.

- **Previous:** `{prev_robots or "(empty)"}`
- **Current:** `{curr_robots}`
- **URL:** `{url}`

This prevents search engines from indexing this page."""
        return ("critical", details)

    return None


def check_canonical_drift(
    conn,
    customer_id: int,
    url: str,
    current_canonical: str,
) -> tuple[str, str] | None:
    """Check if canonical changed unexpectedly.

    Returns (severity, details_md) tuple if drift found, None otherwise.
    """
    prev = fetch_one(
        conn,
        "SELECT canonical FROM snapshots WHERE customer_id=? AND url=? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, url),
    )

    if not prev:
        return None

    prev_canonical = str(prev["canonical"] or "")
    curr_canonical = current_canonical or ""

    if prev_canonical != curr_canonical:
        # Determine severity based on the change type
        severity = "warning"

        # Critical cases
        if prev_canonical and not curr_canonical:
            severity = "critical"
            details = f"""Canonical URL disappeared from key page.

- **Previous:** `{prev_canonical}`
- **Current:** `(none)`
- **URL:** `{url}`

This may cause duplicate content issues."""
        elif curr_canonical and not prev_canonical:
            details = f"""Canonical URL was added to key page.

- **Previous:** `(none)`
- **Current:** `{curr_canonical}`
- **URL:** `{url}`"""
        else:
            details = f"""Canonical URL changed on key page.

- **Previous:** `{prev_canonical}`
- **Current:** `{curr_canonical}`
- **URL:** `{url}`"""

        return (severity, details)

    return None


def check_title_change(
    conn,
    customer_id: int,
    url: str,
    current_title: str,
) -> tuple[str, str] | None:
    """Check if page title changed.

    Returns (severity, details_md) tuple if change found, None otherwise.
    """
    prev = fetch_one(
        conn,
        "SELECT title FROM snapshots WHERE customer_id=? AND url=? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, url),
    )

    if not prev:
        return None

    prev_title = str(prev["title"] or "")
    curr_title = current_title or ""

    if prev_title != curr_title:
        # Title changes are informational by default
        severity = "info"

        # Warning cases
        if prev_title and not curr_title:
            severity = "warning"
            details = f"""Page title disappeared from key page.

- **Previous:** `{prev_title}`
- **Current:** `(empty)`
- **URL:** `{url}`"""
        elif curr_title and not prev_title:
            details = f"""Page title was added to key page.

- **Previous:** `(empty)`
- **Current:** `{curr_title}`
- **URL:** `{url}`"""
        else:
            details = f"""Page title changed on key page.

- **Previous:** `{prev_title}`
- **Current:** `{curr_title}`
- **URL:** `{url}`"""

        return (severity, details)

    return None


def fetch_sitemap(sitemap_url: str, timeout_s: int = 20) -> dict[str, Any]:
    """Fetch sitemap content and return raw body.
    
    Uses http_client.fetch_text for consistent retry/timeout behavior.
    Returns dict with status_code, body, and error info.
    """
    result = fetch_text(sitemap_url, timeout=timeout_s, attempts=3, base_delay=1.0)
    
    if result.is_error:
        return {
            "is_error": True,
            "error": result.error,
            "error_type": result.error_type,
            "status_code": result.status_code,
            "body": None,
        }
    
    return {
        "is_error": False,
        "error": None,
        "error_type": None,
        "status_code": result.status_code,
        "body": result.body or "",
    }


def check_robots_txt_change(
    conn,
    customer_id: int,
    base_url: str,
    current_robots_content: str,
) -> tuple[str, str] | None:
    """Check if robots.txt changed with meaningful diff and severity assessment.

    Returns (severity, details_md) tuple if meaningful change found, None otherwise.
    Uses normalization to ignore cosmetic changes (whitespace, comments).
    Assigns severity based on risk of disallow rule changes.
    """
    from ranksentinel.runner.normalization import normalize_robots_txt, diff_summary

    prev = get_latest_artifact(conn, customer_id, "robots_txt", base_url)

    if not prev:
        # No baseline yet
        return None

    prev_content = str(prev["raw_content"] or "")
    curr_content = current_robots_content or ""

    # Normalize both to ignore cosmetic differences
    prev_normalized = normalize_robots_txt(prev_content)
    curr_normalized = normalize_robots_txt(curr_content)

    if prev_normalized == curr_normalized:
        # No meaningful change
        return None

    # Meaningful change detected - generate diff and determine severity
    diff_text = diff_summary(prev_normalized, curr_normalized, "robots.txt")

    # Analyze severity based on disallow rules
    severity = "info"  # Default to informational

    prev_lower = prev_normalized.lower()
    curr_lower = curr_normalized.lower()

    # Critical: New site-wide disallow
    if "disallow: /" in curr_lower and "disallow: /" not in prev_lower:
        severity = "critical"
    # Critical: Previously allowed paths now disallowed
    elif "disallow:" in curr_lower:
        # Check for expanded disallow patterns
        prev_disallows = [line for line in prev_lower.split("\n") if line.startswith("disallow:")]
        curr_disallows = [line for line in curr_lower.split("\n") if line.startswith("disallow:")]
        
        if len(curr_disallows) > len(prev_disallows):
            # More disallow rules added
            severity = "warning"
        elif curr_disallows != prev_disallows:
            # Disallow rules changed
            severity = "warning"

    details = f"""Robots.txt configuration changed.

- **Base URL:** `{base_url}`
- **Severity:** Changes to disallow rules detected

{diff_text}

Review these changes to ensure they align with your SEO strategy."""

    return (severity, details)


def fetch_psi_metrics(url: str, api_key: str, strategy: str = "mobile") -> dict[str, Any] | None:
    """Fetch PageSpeed Insights metrics for a URL.

    Uses http_client for consistent retry/timeout behavior.
    Returns dict with perf_score, lcp_ms, cls_score, inp_ms, and raw_json.
    Returns None if API call fails or API key is missing.
    """
    if not api_key:
        return None

    # Build PSI URL with query parameters
    psi_url = (
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={url}&key={api_key}&strategy={strategy}&category=performance"
    )

    result = fetch_text(psi_url, timeout=60, attempts=3, base_delay=2.0)

    if result.is_error:
        print(f"PSI fetch failed for {url}: {result.error} ({result.error_type})")
        return None

    try:
        data = json.loads(result.body or "{}")

        # Extract metrics
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        perf = categories.get("performance", {})
        perf_score = int(perf.get("score", 0) * 100) if perf.get("score") is not None else None

        audits = lighthouse.get("audits", {})
        lcp_audit = audits.get("largest-contentful-paint", {})
        cls_audit = audits.get("cumulative-layout-shift", {})
        inp_audit = audits.get("interaction-to-next-paint", {})

        lcp_ms = int(lcp_audit.get("numericValue", 0)) if lcp_audit.get("numericValue") else None
        cls_score = (
            float(cls_audit.get("numericValue", 0))
            if cls_audit.get("numericValue") is not None
            else None
        )
        inp_ms = int(inp_audit.get("numericValue", 0)) if inp_audit.get("numericValue") else None

        return {
            "perf_score": perf_score,
            "lcp_ms": lcp_ms,
            "cls_score": cls_score,
            "inp_ms": inp_ms,
            "raw_json": json.dumps(data),
        }
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"PSI response parsing failed for {url}: {e}")
        return None


def check_psi_regression(
    conn,
    customer_id: int,
    url: str,
    current_metrics: dict[str, Any],
    settings_row: dict[str, Any],
) -> tuple[str, str, str] | None:
    """Check for PSI performance regression with two-run confirmation.

    Returns (severity, title, details_md) tuple if confirmed regression found.
    Returns None if no regression or not yet confirmed.

    Logic:
    - First regression: mark as unconfirmed, no alert
    - Second consecutive regression: mark as confirmed, create critical finding
    """
    perf_threshold = int(settings_row.get("psi_perf_drop_threshold", 10))
    lcp_threshold_ms = int(settings_row.get("psi_lcp_increase_threshold_ms", 500))
    confirm_runs = int(settings_row.get("psi_confirm_runs", 2))

    # Get baseline (most recent non-regression result)
    baseline = fetch_one(
        conn,
        "SELECT perf_score, lcp_ms FROM psi_results "
        "WHERE customer_id=? AND url=? AND is_regression=0 "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, url),
    )

    if not baseline:
        # No baseline yet, this becomes the baseline
        return None

    baseline_perf = baseline["perf_score"]
    baseline_lcp = baseline["lcp_ms"]

    curr_perf = current_metrics.get("perf_score")
    curr_lcp = current_metrics.get("lcp_ms")

    # Detect regression
    is_regression = False
    regression_type = None

    if baseline_perf and curr_perf and (baseline_perf - curr_perf) >= perf_threshold:
        is_regression = True
        regression_type = "perf_score"
    elif baseline_lcp and curr_lcp and (curr_lcp - baseline_lcp) >= lcp_threshold_ms:
        is_regression = True
        regression_type = "lcp"

    if not is_regression:
        return None

    # Check for previous unconfirmed regression
    prev = fetch_one(
        conn,
        "SELECT is_regression, is_confirmed, regression_type FROM psi_results "
        "WHERE customer_id=? AND url=? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, url),
    )

    if prev and prev["is_regression"] == 1 and prev["is_confirmed"] == 0:
        # Previous run was unconfirmed regression, now confirm it
        if confirm_runs <= 2:
            # Generate confirmed finding
            if regression_type == "perf_score":
                details = f"""Performance score dropped on key page (confirmed).

- **Baseline:** {baseline_perf}
- **Current:** {curr_perf}
- **Drop:** {baseline_perf - curr_perf} points
- **URL:** `{url}`

This regression was confirmed across {confirm_runs} consecutive runs."""
                return ("critical", "PSI performance regression (confirmed)", details)
            else:  # lcp
                details = f"""Largest Contentful Paint (LCP) increased on key page (confirmed).

- **Baseline:** {baseline_lcp}ms
- **Current:** {curr_lcp}ms
- **Increase:** +{curr_lcp - baseline_lcp}ms
- **URL:** `{url}`

This regression was confirmed across {confirm_runs} consecutive runs."""
                return ("critical", "PSI LCP regression (confirmed)", details)

    # First regression or not yet confirmed
    return None


def run(settings: Settings) -> None:
    """Daily critical checks with noindex, canonical, robots.txt, and PSI regression detection."""
    run_id = generate_run_id()
    start_time = time.time()
    
    log_structured(run_id, run_type="daily", stage="init", status="start")
    
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
                    # Get customer settings (including sitemap_url for robots base URL)
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

                    # Fetch and store robots.txt artifact
                    robots_base_url = None
                    if customer_settings.get("sitemap_url"):
                        # Derive base URL from sitemap_url (e.g., https://example.com/sitemap.xml -> https://example.com)
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

                    # Fetch and store sitemap artifact
                    sitemap_url = customer_settings.get("sitemap_url")
                    if sitemap_url:
                        try:
                            with log_stage(run_id, "fetch_sitemap", customer_id=customer_id, url=sitemap_url):
                                sitemap_result = fetch_sitemap(str(sitemap_url))
                            
                            if not sitemap_result["is_error"]:
                                sitemap_content = sitemap_result["body"] or ""
                                sitemap_sha = sha256_text(sitemap_content)
                                fetched_at = now_iso()
                                
                                # Extract URL count from sitemap
                                url_count_data = extract_url_count(sitemap_content)
                                url_count = url_count_data.get("url_count", 0)
                                sitemap_type = url_count_data.get("sitemap_type", "unknown")
                                
                                # Check if sitemap changed before storing
                                prev_sitemap_artifact = get_latest_artifact(conn, customer_id, "sitemap", str(sitemap_url))
                                
                                # Only store if changed
                                if not prev_sitemap_artifact or prev_sitemap_artifact["artifact_sha"] != sitemap_sha:
                                    store_artifact(
                                        conn, customer_id, "sitemap", str(sitemap_url),
                                        sitemap_sha, sitemap_content, fetched_at
                                    )
                                    
                                    log_structured(
                                        run_id, customer_id=customer_id, stage="fetch_sitemap",
                                        status="success", url=sitemap_url, sha=sitemap_sha[:12],
                                        url_count=url_count, sitemap_type=sitemap_type
                                    )
                                    
                                    # Check for URL count changes (if we have a baseline)
                                    if prev_sitemap_artifact:
                                        prev_content = str(prev_sitemap_artifact["raw_content"] or "")
                                        prev_count_data = extract_url_count(prev_content)
                                        prev_url_count = prev_count_data.get("url_count", 0)
                                        
                                        # Detect significant changes
                                        if prev_url_count > 0:
                                            count_delta = url_count - prev_url_count
                                            pct_change = (count_delta / prev_url_count) * 100 if prev_url_count > 0 else 0
                                            
                                            severity = None
                                            title = None
                                            details = None
                                            
                                            # URL count disappeared (complete loss)
                                            if url_count == 0:
                                                severity = "critical"
                                                title = "Sitemap URL count dropped to zero"
                                                details = f"""All URLs disappeared from sitemap.

- **Previous count:** {prev_url_count}
- **Current count:** 0
- **Sitemap URL:** `{sitemap_url}`
- **Type:** {sitemap_type}

This may prevent search engines from discovering your pages."""
                                            # Large drop (>30% loss)
                                            elif pct_change <= -30:
                                                severity = "critical"
                                                title = "Sitemap URL count dropped significantly"
                                                details = f"""Sitemap URL count decreased by {abs(pct_change):.1f}%.

- **Previous count:** {prev_url_count}
- **Current count:** {url_count}
- **Change:** {count_delta} URLs ({pct_change:+.1f}%)
- **Sitemap URL:** `{sitemap_url}`
- **Type:** {sitemap_type}

Review your sitemap generation to ensure pages are not being accidentally excluded."""
                                            # Moderate drop (10-30% loss)
                                            elif pct_change <= -10:
                                                severity = "warning"
                                                title = "Sitemap URL count decreased"
                                                details = f"""Sitemap URL count decreased by {abs(pct_change):.1f}%.

- **Previous count:** {prev_url_count}
- **Current count:** {url_count}
- **Change:** {count_delta} URLs ({pct_change:+.1f}%)
- **Sitemap URL:** `{sitemap_url}`
- **Type:** {sitemap_type}"""
                                            
                                            # Create finding if severity determined
                                            if severity and title and details:
                                                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                                dedupe_key = generate_finding_dedupe_key(
                                                    customer_id, "daily", "indexability", title, None, period
                                                )
                                                execute(
                                                    conn,
                                                    "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                                    "VALUES(?,?,?,?,?,?,?,?,?)",
                                                    (
                                                        customer_id,
                                                        "daily",
                                                        severity,
                                                        "indexability",
                                                        title,
                                                        details,
                                                        None,
                                                        dedupe_key,
                                                        fetched_at,
                                                    ),
                                                )
                            else:
                                # Missing or unreachable sitemap - create critical finding
                                fetched_at = now_iso()
                                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                dedupe_key = generate_finding_dedupe_key(
                                    customer_id, "daily", "indexability", "Sitemap unreachable", None, period
                                )
                                
                                details = f"""Sitemap could not be fetched.

- **URL:** `{sitemap_url}`
- **Error:** {sitemap_result['error']}
- **Error Type:** {sitemap_result['error_type']}

This may prevent search engines from discovering your pages."""
                                
                                execute(
                                    conn,
                                    "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                    "VALUES(?,?,?,?,?,?,?,?,?)",
                                    (
                                        customer_id,
                                        "daily",
                                        "critical",
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

                    if robots_base_url:
                        robots_url = f"{robots_base_url}/robots.txt"
                        try:
                            with log_stage(run_id, "fetch_robots", customer_id=customer_id, url=robots_url):
                                robots_result = fetch_text(robots_url, timeout=10, attempts=2, base_delay=1.0)
                            
                            if not robots_result.is_error:
                                robots_content = robots_result.body or ""
                                robots_sha = sha256_text(robots_content)
                                fetched_at = now_iso()
                                
                                # Check for meaningful changes before storing
                                prev_robots_artifact = get_latest_artifact(conn, customer_id, "robots_txt", robots_base_url)
                                
                                # Only store and check if changed
                                if not prev_robots_artifact or prev_robots_artifact["artifact_sha"] != robots_sha:
                                    # Store artifact (kind=robots_txt, subject=base_url)
                                    store_artifact(
                                        conn, customer_id, "robots_txt", robots_base_url, 
                                        robots_sha, robots_content, fetched_at
                                    )
                                    
                                    log_structured(
                                        run_id, customer_id=customer_id, stage="fetch_robots", 
                                        status="success", url=robots_url, sha=robots_sha[:12]
                                    )
                                    
                                    # Check for meaningful robots.txt changes
                                    robots_result = check_robots_txt_change(
                                        conn, customer_id, robots_base_url, robots_content
                                    )
                                    if robots_result:
                                        severity, details = robots_result
                                        period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                        dedupe_key = generate_finding_dedupe_key(
                                            customer_id, "daily", "indexability", "Robots.txt changed", None, period
                                        )
                                        execute(
                                            conn,
                                            "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                            "VALUES(?,?,?,?,?,?,?,?,?)",
                                            (
                                                customer_id,
                                                "daily",
                                                severity,
                                                "indexability",
                                                "Robots.txt changed",
                                                details,
                                                None,
                                                dedupe_key,
                                                fetched_at,
                                            ),
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
                            "INSERT INTO snapshots(customer_id,url,run_type,fetched_at,status_code,"
                            "final_url,redirect_chain,title,canonical,meta_robots,content_hash) "
                            "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                            (
                                customer_id,
                                url,
                                "daily",
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

                        # Check for noindex regression (only-on-change)
                        meta_robots_changed = False
                        prev_meta_artifact = get_latest_artifact(conn, customer_id, "meta_robots", url)
                        curr_meta_sha = sha256_text(data["meta_robots"])
                        
                        if not prev_meta_artifact or prev_meta_artifact["artifact_sha"] != curr_meta_sha:
                            meta_robots_changed = True
                            store_artifact(conn, customer_id, "meta_robots", url, curr_meta_sha, data["meta_robots"], fetched_at)
                            
                            noindex_result = check_noindex_regression(
                                conn, customer_id, url, data["meta_robots"]
                            )
                            if noindex_result:
                                severity, details = noindex_result
                                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                dedupe_key = generate_finding_dedupe_key(
                                    customer_id, "daily", "indexability", "Key page noindex detected", url, period
                                )
                                execute(
                                    conn,
                                    "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                    "VALUES(?,?,?,?,?,?,?,?,?)",
                                    (
                                        customer_id,
                                        "daily",
                                        severity,
                                        "indexability",
                                        "Key page noindex detected",
                                        details,
                                        url,
                                        dedupe_key,
                                        fetched_at,
                                    ),
                                )

                        # Check for canonical drift (only-on-change)
                        prev_canonical_artifact = get_latest_artifact(conn, customer_id, "canonical", url)
                        curr_canonical_sha = sha256_text(data["canonical"])
                        
                        if not prev_canonical_artifact or prev_canonical_artifact["artifact_sha"] != curr_canonical_sha:
                            store_artifact(conn, customer_id, "canonical", url, curr_canonical_sha, data["canonical"], fetched_at)
                            
                            canonical_result = check_canonical_drift(conn, customer_id, url, data["canonical"])
                            if canonical_result:
                                severity, details = canonical_result
                                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                dedupe_key = generate_finding_dedupe_key(
                                    customer_id, "daily", "indexability", "Canonical URL changed", url, period
                                )
                                execute(
                                    conn,
                                    "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                    "VALUES(?,?,?,?,?,?,?,?,?)",
                                    (
                                        customer_id,
                                        "daily",
                                        severity,
                                        "indexability",
                                        "Canonical URL changed",
                                        details,
                                        url,
                                        dedupe_key,
                                        fetched_at,
                                    ),
                                )

                        # Check for title change (only-on-change)
                        prev_title_artifact = get_latest_artifact(conn, customer_id, "title", url)
                        curr_title_sha = sha256_text(data["title"])
                        
                        if not prev_title_artifact or prev_title_artifact["artifact_sha"] != curr_title_sha:
                            store_artifact(conn, customer_id, "title", url, curr_title_sha, data["title"], fetched_at)
                            
                            title_result = check_title_change(conn, customer_id, url, data["title"])
                            if title_result:
                                severity, details = title_result
                                period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                dedupe_key = generate_finding_dedupe_key(
                                    customer_id, "daily", "content", "Page title changed", url, period
                                )
                                execute(
                                    conn,
                                    "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                    "VALUES(?,?,?,?,?,?,?,?,?)",
                                    (
                                        customer_id,
                                        "daily",
                                        severity,
                                        "content",
                                        "Page title changed",
                                        details,
                                        url,
                                        dedupe_key,
                                        fetched_at,
                                    ),
                                )

                        # PSI checks (only for first N key URLs if enabled)
                        if psi_enabled and psi_count < psi_limit and settings.PSI_API_KEY:
                            with log_stage(run_id, "fetch_psi", customer_id=customer_id, url=url):
                                psi_metrics = fetch_psi_metrics(url, settings.PSI_API_KEY)

                            if psi_metrics:
                                # Determine regression state
                                regression_result = check_psi_regression(
                                    conn, customer_id, url, psi_metrics, customer_settings
                                )

                                is_regression = 0
                                is_confirmed = 0
                                regression_type = None

                                if regression_result:
                                    # Confirmed regression
                                    is_regression = 1
                                    is_confirmed = 1
                                    severity, title, details = regression_result
                                    regression_type = (
                                        "perf_score" if "Performance score" in title else "lcp"
                                    )

                                    # Create finding
                                    period = datetime.fromisoformat(fetched_at).strftime('%Y-%m-%d')
                                    dedupe_key = generate_finding_dedupe_key(
                                        customer_id, "daily", "performance", title, url, period
                                    )
                                    execute(
                                        conn,
                                        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                                        "VALUES(?,?,?,?,?,?,?,?,?)",
                                        (
                                            customer_id,
                                            "daily",
                                            severity,
                                            "performance",
                                            title,
                                            details,
                                            url,
                                            dedupe_key,
                                            fetched_at,
                                        ),
                                    )
                                else:
                                    # Check if this is first regression (unconfirmed)
                                    baseline = fetch_one(
                                        conn,
                                        "SELECT perf_score, lcp_ms FROM psi_results "
                                        "WHERE customer_id=? AND url=? AND is_regression=0 "
                                        "ORDER BY fetched_at DESC LIMIT 1",
                                        (customer_id, url),
                                    )

                                    if baseline:
                                        baseline_perf = baseline["perf_score"]
                                        baseline_lcp = baseline["lcp_ms"]
                                        curr_perf = psi_metrics.get("perf_score")
                                        curr_lcp = psi_metrics.get("lcp_ms")
                                        perf_threshold = int(
                                            customer_settings.get("psi_perf_drop_threshold", 10)
                                        )
                                        lcp_threshold_ms = int(
                                            customer_settings.get("psi_lcp_increase_threshold_ms", 500)
                                        )

                                        if (
                                            baseline_perf
                                            and curr_perf
                                            and (baseline_perf - curr_perf) >= perf_threshold
                                        ):
                                            is_regression = 1
                                            regression_type = "perf_score"
                                        elif (
                                            baseline_lcp
                                            and curr_lcp
                                            and (curr_lcp - baseline_lcp) >= lcp_threshold_ms
                                        ):
                                            is_regression = 1
                                            regression_type = "lcp"

                                # Store PSI result
                                execute(
                                    conn,
                                    "INSERT INTO psi_results(customer_id,url,run_type,fetched_at,perf_score,"
                                    "lcp_ms,cls_score,inp_ms,is_regression,is_confirmed,regression_type,raw_json) "
                                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                                    (
                                        customer_id,
                                        url,
                                        "daily",
                                        fetched_at,
                                        psi_metrics.get("perf_score"),
                                        psi_metrics.get("lcp_ms"),
                                        psi_metrics.get("cls_score"),
                                        psi_metrics.get("inp_ms"),
                                        is_regression,
                                        is_confirmed,
                                        regression_type,
                                        psi_metrics.get("raw_json"),
                                    ),
                                )

                                psi_count += 1
                            
            except Exception as e:  # noqa: BLE001
                # Catch per-customer errors and record them, then continue to next customer
                error_msg = f"Customer {customer_id} processing failed: {type(e).__name__}: {e}"
                log_structured(run_id, customer_id=customer_id, stage="process_customer", status="error", error=error_msg)
                errors_by_customer[customer_id] = error_msg
                # Log error to database for debugging
                try:
                    error_time = now_iso()
                    period = datetime.fromisoformat(error_time).strftime('%Y-%m-%d')
                    dedupe_key = generate_finding_dedupe_key(
                        customer_id, "daily", "system", "Daily run processing error", None, period
                    )
                    execute(
                        conn,
                        "INSERT OR IGNORE INTO findings(customer_id,run_type,severity,category,title,details_md,url,dedupe_key,created_at) "
                        "VALUES(?,?,?,?,?,?,?,?,?)",
                        (
                            customer_id,
                            "daily",
                            "critical",
                            "system",
                            "Daily run processing error",
                            f"An error occurred during daily processing:\n\n```\n{error_msg}\n```",
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
        
        log_summary(run_id, "daily", total_customers, successful_customers, failed_customers, total_elapsed_ms)
        
        if errors_by_customer:
            log_structured(run_id, stage="summary", failed_customer_ids=",".join(str(cid) for cid in errors_by_customer.keys()))
        
        # Send daily critical alerts (only if critical findings exist)
        _send_daily_critical_alerts(conn, settings, run_id)
    finally:
        conn.close()


def _send_daily_critical_alerts(conn, settings: Settings, run_id: str) -> None:
    """Send daily critical alert emails to customers with critical findings.
    
    Only sends email if critical findings exist for this run.
    Uses per-customer isolation - one customer's email failure doesn't affect others.
    """
    from ranksentinel.db import fetch_all, fetch_one
    from ranksentinel.mailgun import MailgunClient, send_and_log
    from ranksentinel.reporting.email_templates import render_daily_critical_alert
    from ranksentinel.reporting.report_composer import compose_daily_critical_report
    from ranksentinel.runner.logging_utils import log_stage, log_structured
    
    # Initialize Mailgun client (skip if not configured)
    try:
        mailgun_client = MailgunClient(settings)
    except (ValueError, Exception) as e:
        log_structured(run_id, stage="email_init", status="skip", reason=f"Mailgun not configured: {e}")
        return
    
    # Get all active customers
    customers = fetch_all(conn, "SELECT id, name, email FROM customers WHERE status='active'")
    
    for customer_row in customers:
        customer_id = int(customer_row["id"])
        customer_name = str(customer_row["name"])
        customer_email = str(customer_row["email"])
        
        try:
            with log_stage(run_id, "daily_email", customer_id=customer_id):
                # Check if there are any critical findings for this customer from today's run
                # Use a time window of last 24 hours to catch findings from this run
                critical_findings = fetch_all(
                    conn,
                    "SELECT * FROM findings "
                    "WHERE customer_id=? AND run_type='daily' AND severity='critical' "
                    "AND datetime(created_at) >= datetime('now', '-24 hours') "
                    "ORDER BY created_at DESC",
                    (customer_id,)
                )
                
                if not critical_findings:
                    # No critical findings - skip email (low-noise principle)
                    log_structured(
                        run_id, customer_id=customer_id, stage="daily_email",
                        status="skip", reason="no_critical_findings"
                    )
                    continue
                
                # Compose critical-only report
                report = compose_daily_critical_report(customer_name, critical_findings)
                
                # Extract critical section text and HTML from the report
                critical_text = _extract_critical_section_text(report)
                critical_html = _extract_critical_section_html(report)
                
                # Render email
                email = render_daily_critical_alert(customer_name, critical_text, critical_html)
                
                # Send and log delivery
                success = send_and_log(
                    conn=conn,
                    client=mailgun_client,
                    customer_id=customer_id,
                    run_type="daily",
                    recipient=customer_email,
                    subject=email.subject,
                    text_body=email.text,
                    html_body=email.html,
                )
                
                if success:
                    log_structured(
                        run_id, customer_id=customer_id, stage="daily_email",
                        status="sent", recipient=customer_email, critical_count=len(critical_findings)
                    )
                else:
                    log_structured(
                        run_id, customer_id=customer_id, stage="daily_email",
                        status="failed", recipient=customer_email
                    )
        
        except Exception as e:  # noqa: BLE001
            # Per-customer isolation: log error and continue to next customer
            log_structured(
                run_id, customer_id=customer_id, stage="daily_email",
                status="error", error=str(e)
            )


def _extract_critical_section_text(report) -> str:
    """Extract plain text critical findings section from a report."""
    lines = []
    lines.append(f"CRITICAL ISSUES ({report.critical_count})")
    lines.append("-" * 60)
    lines.append("")
    
    for idx, finding in enumerate(report.critical_findings, 1):
        lines.append(f"{idx}) {finding.title}")
        lines.append("")
        if finding.url:
            lines.append(f"   URL: {finding.url}")
        lines.append(f"   Detected: {finding.created_at}")
        lines.append("")
        lines.append(f"   {finding.details_md}")
        lines.append("")
        lines.append(f"   → Recommended Action: {finding.recommendation}")
        lines.append("")
    
    return "\n".join(lines)


def _extract_critical_section_html(report) -> str:
    """Extract HTML critical findings section from a report."""
    lines = []
    lines.append("<h2>Critical Issues</h2>")
    
    for idx, finding in enumerate(report.critical_findings, 1):
        lines.append("<div style='background: #fff; border-left: 4px solid #d32f2f; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>")
        lines.append(f"<h3 style='margin-top: 0; color: #1a1a1a;'>{idx}) {finding.title}</h3>")
        lines.append("<div style='color: #666; font-size: 0.9em; margin: 10px 0;'>")
        if finding.url:
            lines.append(f"<div><strong>URL:</strong> <code>{finding.url}</code></div>")
        lines.append(f"<div><strong>Detected:</strong> {finding.created_at}</div>")
        lines.append("</div>")
        lines.append(f"<div style='margin: 15px 0; line-height: 1.6;'>{finding.details_md}</div>")
        lines.append(f"<div style='background: #e8f5e9; border-radius: 4px; padding: 12px; margin-top: 15px;'><strong style='color: #2e7d32;'>→ Recommended Action:</strong> {finding.recommendation}</div>")
        lines.append("</div>")
    
    return "\n".join(lines)
