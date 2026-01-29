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


@app.post("/admin/customers/{customer_id}/send_first_insight")
def send_first_insight(customer_id: int, conn=Depends(get_conn)):
    """Trigger a First Insight report for a customer (admin-only endpoint).
    
    This endpoint sends an immediate onboarding report to help new customers
    see value quickly without waiting for the weekly schedule.
    """
    cust = fetch_one(conn, "SELECT id FROM customers WHERE id=?", (customer_id,))
    if not cust:
        raise HTTPException(status_code=404, detail="customer not found")
    
    # Import here to avoid circular dependencies
    from ranksentinel.runner.first_insight import trigger_first_insight_report
    
    trigger_first_insight_report(conn, customer_id)
    
    return {"status": "ok", "message": "First Insight report triggered"}
