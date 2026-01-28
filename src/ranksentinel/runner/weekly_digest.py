from datetime import datetime, timezone

from ranksentinel.config import Settings
from ranksentinel.db import connect, execute, fetch_all, init_db


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(settings: Settings) -> None:
    """Bootstrap-level weekly run.

    Full weekly digest logic is implemented in later phases.
    """
    conn = connect(settings)
    try:
        init_db(conn)
        customers = fetch_all(conn, "SELECT id FROM customers WHERE status='active'")

        for c in customers:
            customer_id = int(c["id"])
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
