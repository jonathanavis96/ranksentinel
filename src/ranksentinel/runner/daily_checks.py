import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

import requests

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, fetch_one, init_db
from ranksentinel.runner.normalization import (
    extract_canonical,
    extract_meta_robots,
    normalize_html_to_text,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def retry(fn, attempts: int = 3, base_delay_s: float = 1.0):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(base_delay_s * (2**i))
    raise last  # type: ignore[misc]


def fetch_url(url: str, timeout_s: int = 20) -> dict[str, Any]:
    resp = requests.get(
        url,
        timeout=timeout_s,
        allow_redirects=True,
        headers={"User-Agent": "RankSentinel/0.1"},
    )
    chain = [r.url for r in resp.history] + [resp.url]
    ct = resp.headers.get("content-type", "").lower()
    html = resp.text if ct.startswith("text/html") else ""
    text = normalize_html_to_text(html) if html else ""
    meta_robots = extract_meta_robots(html) if html else ""
    canonical = extract_canonical(html) if html else ""
    return {
        "status_code": int(resp.status_code),
        "final_url": resp.url,
        "redirect_chain": chain,
        "content_hash": sha256_text(text),
        "meta_robots": meta_robots,
        "canonical": canonical,
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


def fetch_psi_metrics(url: str, api_key: str, strategy: str = "mobile") -> dict[str, Any] | None:
    """Fetch PageSpeed Insights metrics for a URL.
    
    Returns dict with perf_score, lcp_ms, cls_score, inp_ms, and raw_json.
    Returns None if API call fails or API key is missing.
    """
    if not api_key:
        return None
    
    try:
        psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": api_key,
            "strategy": strategy,
            "category": "performance",
        }
        
        resp = requests.get(psi_url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
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
        cls_score = float(cls_audit.get("numericValue", 0)) if cls_audit.get("numericValue") is not None else None
        inp_ms = int(inp_audit.get("numericValue", 0)) if inp_audit.get("numericValue") else None
        
        return {
            "perf_score": perf_score,
            "lcp_ms": lcp_ms,
            "cls_score": cls_score,
            "inp_ms": inp_ms,
            "raw_json": json.dumps(data),
        }
    except Exception as e:  # noqa: BLE001
        print(f"PSI fetch failed for {url}: {e}")
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
    """Daily critical checks with noindex, canonical, and PSI regression detection."""
    conn = connect(settings)
    try:
        init_db(conn)
        customers = fetch_all(conn, "SELECT id FROM customers WHERE status='active'")

        for c in customers:
            customer_id = int(c["id"])
            
            # Get customer settings
            customer_settings = fetch_one(
                conn,
                "SELECT psi_enabled, psi_urls_limit, psi_confirm_runs, "
                "psi_perf_drop_threshold, psi_lcp_increase_threshold_ms "
                "FROM settings WHERE customer_id=?",
                (customer_id,),
            )
            
            # Use defaults if settings not found
            if not customer_settings:
                customer_settings = {
                    "psi_enabled": 1,
                    "psi_urls_limit": 5,
                    "psi_confirm_runs": 2,
                    "psi_perf_drop_threshold": 10,
                    "psi_lcp_increase_threshold_ms": 500,
                }
            
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
                url = str(t["url"])
                data = retry(lambda: fetch_url(url))
                fetched_at = now_iso()
                
                # Store snapshot
                execute(
                    conn,
                    "INSERT INTO snapshots(customer_id,url,run_type,fetched_at,status_code,"
                    "final_url,redirect_chain,canonical,meta_robots,content_hash) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        customer_id,
                        url,
                        "daily",
                        fetched_at,
                        data["status_code"],
                        data["final_url"],
                        json.dumps(data["redirect_chain"]),
                        data["canonical"],
                        data["meta_robots"],
                        data["content_hash"],
                    ),
                )
                
                # Check for noindex regression
                noindex_result = check_noindex_regression(
                    conn, customer_id, url, data["meta_robots"]
                )
                if noindex_result:
                    severity, details = noindex_result
                    execute(
                        conn,
                        "INSERT INTO findings(customer_id,run_type,severity,category,title,details_md,url,created_at) "
                        "VALUES(?,?,?,?,?,?,?,?)",
                        (
                            customer_id,
                            "daily",
                            severity,
                            "indexability",
                            "Key page noindex detected",
                            details,
                            url,
                            fetched_at,
                        ),
                    )
                
                # Check for canonical drift
                canonical_result = check_canonical_drift(
                    conn, customer_id, url, data["canonical"]
                )
                if canonical_result:
                    severity, details = canonical_result
                    execute(
                        conn,
                        "INSERT INTO findings(customer_id,run_type,severity,category,title,details_md,url,created_at) "
                        "VALUES(?,?,?,?,?,?,?,?)",
                        (
                            customer_id,
                            "daily",
                            severity,
                            "indexability",
                            "Canonical URL changed",
                            details,
                            url,
                            fetched_at,
                        ),
                    )
                
                # PSI checks (only for first N key URLs if enabled)
                if psi_enabled and psi_count < psi_limit and settings.PSI_API_KEY:
                    psi_metrics = retry(lambda: fetch_psi_metrics(url, settings.PSI_API_KEY))
                    
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
                            regression_type = "perf_score" if "Performance score" in title else "lcp"
                            
                            # Create finding
                            execute(
                                conn,
                                "INSERT INTO findings(customer_id,run_type,severity,category,title,details_md,url,created_at) "
                                "VALUES(?,?,?,?,?,?,?,?)",
                                (
                                    customer_id,
                                    "daily",
                                    severity,
                                    "performance",
                                    title,
                                    details,
                                    url,
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
                                perf_threshold = int(customer_settings.get("psi_perf_drop_threshold", 10))
                                lcp_threshold_ms = int(customer_settings.get("psi_lcp_increase_threshold_ms", 500))
                                
                                if baseline_perf and curr_perf and (baseline_perf - curr_perf) >= perf_threshold:
                                    is_regression = 1
                                    regression_type = "perf_score"
                                elif baseline_lcp and curr_lcp and (curr_lcp - baseline_lcp) >= lcp_threshold_ms:
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
    finally:
        conn.close()
