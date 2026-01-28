import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

import requests

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, init_db
from ranksentinel.runner.normalization import normalize_html_to_text


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
    return {
        "status_code": int(resp.status_code),
        "final_url": resp.url,
        "redirect_chain": chain,
        "content_hash": sha256_text(text),
    }


def run(settings: Settings) -> None:
    """Bootstrap-level daily run.

    Full daily logic (robots/sitemap/canonical/noindex/severity/email) is implemented in later phases.
    """
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
                execute(
                    conn,
                    "INSERT INTO findings(customer_id,run_type,severity,category,title,details_md,url,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?)",
                    (
                        customer_id,
                        "daily",
                        "info",
                        "bootstrap",
                        "Daily check executed (bootstrap)",
                        "\
".join(
                            [
                                f"- URL: `{url}`",
                                f"- Status: `{data['status_code']}`",
                                f"- Final URL: `{data['final_url']}`",
                                f"- Content hash: `{data['content_hash']}`",
                                f"- Redirect chain: `{json.dumps(data['redirect_chain'])}`",
                            ]
                        )
                        + "\
",
                        url,
                        now_iso(),
                    ),
                )
    finally:
        conn.close()
