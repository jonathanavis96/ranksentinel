from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException

from ranksentinel.config import Settings, get_settings
from ranksentinel.db import connect, execute, fetch_all, fetch_one, init_db
from ranksentinel.models import (
    CustomerCreate,
    CustomerOut,
    CustomerSettingsPatch,
    TargetCreate,
    TargetOut,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn(settings: Settings = Depends(get_settings)):
    conn = connect(settings)
    try:
        init_db(conn)
        yield conn
    finally:
        conn.close()


app = FastAPI(title="RankSentinel Admin API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/admin/customers", response_model=CustomerOut)
def create_customer(payload: CustomerCreate, conn=Depends(get_conn)):
    ts = now_iso()
    customer_id = execute(
        conn,
        "INSERT INTO customers(name,status,created_at,updated_at) VALUES(?,?,?,?)",
        (payload.name, "active", ts, ts),
    )
    execute(conn, "INSERT OR IGNORE INTO settings(customer_id) VALUES(?)", (customer_id,))
    row = fetch_one(conn, "SELECT id,name,status FROM customers WHERE id=?", (customer_id,))
    return CustomerOut(**dict(row))


@app.get("/admin/customers", response_model=list[CustomerOut])
def list_customers(conn=Depends(get_conn)):
    rows = fetch_all(conn, "SELECT id,name,status FROM customers ORDER BY id DESC")
    return [CustomerOut(**dict(r)) for r in rows]


@app.post("/admin/customers/{customer_id}/targets", response_model=TargetOut)
def add_target(customer_id: int, payload: TargetCreate, conn=Depends(get_conn)):
    cust = fetch_one(conn, "SELECT id FROM customers WHERE id=?", (customer_id,))
    if not cust:
        raise HTTPException(status_code=404, detail="customer not found")

    ts = now_iso()
    tid = execute(
        conn,
        "INSERT INTO targets(customer_id,url,is_key,created_at) VALUES(?,?,?,?)",
        (customer_id, str(payload.url), 1 if payload.is_key else 0, ts),
    )
    row = fetch_one(conn, "SELECT id,customer_id,url,is_key FROM targets WHERE id=?", (tid,))
    return TargetOut(**dict(row))


@app.get("/admin/customers/{customer_id}/targets", response_model=list[TargetOut])
def list_targets(customer_id: int, conn=Depends(get_conn)):
    rows = fetch_all(
        conn,
        "SELECT id,customer_id,url,is_key FROM targets WHERE customer_id=? ORDER BY id DESC",
        (customer_id,),
    )
    return [TargetOut(**dict(r)) for r in rows]


@app.patch("/admin/customers/{customer_id}/settings")
def patch_settings(customer_id: int, payload: CustomerSettingsPatch, conn=Depends(get_conn)):
    cust = fetch_one(conn, "SELECT id FROM customers WHERE id=?", (customer_id,))
    if not cust:
        raise HTTPException(status_code=404, detail="customer not found")

    existing = fetch_one(conn, "SELECT * FROM settings WHERE customer_id=?", (customer_id,))
    if not existing:
        execute(conn, "INSERT INTO settings(customer_id) VALUES(?)", (customer_id,))

    updates: list[str] = []
    params: list[object] = []

    if payload.sitemap_url is not None:
        updates.append("sitemap_url=?")
        params.append(str(payload.sitemap_url))

    if payload.crawl_limit is not None:
        updates.append("crawl_limit=?")
        params.append(payload.crawl_limit)

    if payload.psi_enabled is not None:
        updates.append("psi_enabled=?")
        params.append(1 if payload.psi_enabled else 0)

    if payload.psi_urls_limit is not None:
        updates.append("psi_urls_limit=?")
        params.append(payload.psi_urls_limit)

    if not updates:
        return {"status": "no changes"}

    params.append(customer_id)
    execute(conn, f"UPDATE settings SET {', '.join(updates)} WHERE customer_id=?", params)
    return {"status": "ok"}


def trigger_first_insight_for_customer(
    customer_id: int,
    conn,
    settings: Settings,
) -> dict:
    """Internal hook for triggering First Insight report on payment success.

    This function is designed to be called by payment webhook handlers
    (e.g., Stripe webhook) when a customer successfully completes payment.

    Args:
        customer_id: ID of the customer who completed payment
        conn: Database connection
        settings: Application settings with API keys and email config

    Returns:
        Dict with run_id, findings count, and email delivery status

    Raises:
        ValueError: If customer_id is invalid or customer not found

    Example:
        # From a future Stripe webhook handler:
        def handle_payment_success(stripe_customer_id: str, conn, settings):
            customer_id = get_customer_id_from_stripe(stripe_customer_id)
            result = trigger_first_insight_for_customer(customer_id, conn, settings)
            return result
    """
    # Import here to avoid circular dependencies
    from ranksentinel.mailgun import MailgunClient
    from ranksentinel.runner.first_insight import trigger_first_insight_report

    # Validate customer exists
    cust = fetch_one(conn, "SELECT id FROM customers WHERE id=?", (customer_id,))
    if not cust:
        raise ValueError(f"Customer {customer_id} not found")

    # Initialize Mailgun client if configured
    mailgun_client = None
    recipient_email = None
    if settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN and settings.MAILGUN_TO:
        try:
            mailgun_client = MailgunClient(settings)
            recipient_email = settings.MAILGUN_TO
        except Exception:
            pass  # Will run without email if Mailgun not configured

    result = trigger_first_insight_report(
        conn,
        customer_id,
        psi_api_key=settings.PSI_API_KEY,
        mailgun_client=mailgun_client,
        recipient_email=recipient_email,
    )

    return result


def send_first_insight(customer_id: int, conn, settings: Settings | None = None) -> dict:
    """Trigger a First Insight report for a customer.

    Notes:
    - This is intentionally callable as a plain function (tests call it directly).
    - The FastAPI endpoint wrapper is defined below and uses dependency injection.
    """
    if settings is None:
        settings = get_settings()

    # Keep endpoint behavior stable: 404 uses a consistent message.
    cust = fetch_one(conn, "SELECT id FROM customers WHERE id=?", (customer_id,))
    if not cust:
        raise HTTPException(status_code=404, detail="customer not found")

    result = trigger_first_insight_for_customer(customer_id, conn, settings)
    return {
        "status": "ok",
        "message": f"First Insight report triggered for customer {customer_id}",
        "result": result,
    }


@app.post("/admin/customers/{customer_id}/send_first_insight")
def send_first_insight_endpoint(
    customer_id: int, conn=Depends(get_conn), settings: Settings = Depends(get_settings)
):
    """Admin endpoint wrapper for `send_first_insight()` (FastAPI dependency injection)."""
    return send_first_insight(customer_id=customer_id, conn=conn, settings=settings)
