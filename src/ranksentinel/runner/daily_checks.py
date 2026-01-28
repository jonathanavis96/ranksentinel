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


def run(settings: Settings) -> None:
    """Daily critical checks with noindex and canonical regression detection."""
    conn = connect(settings)
    try:
        init_db(conn)
        customers = fetch_all(conn, "SELECT id FROM customers WHERE status='active'")

        for c in customers:
            customer_id = int(c["id"])
            targets = fetch_all(
                conn,
                "SELECT url FROM targets WHERE customer_id=? AND is_key=1",
                (customer_id,),
            )
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
    finally:
        conn.close()
