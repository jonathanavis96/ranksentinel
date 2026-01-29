from datetime import datetime, timezone

from ranksentinel.email_utils import canonicalize_email

from fastapi import Depends, FastAPI, HTTPException

from ranksentinel.config import Settings, get_settings
from ranksentinel.db import connect, execute, fetch_all, fetch_one, init_db
from ranksentinel.models import (
    CustomerCreate,
    CustomerOut,
    CustomerSettingsPatch,
    LeadCreate,
    LeadResponse,
    ScheduleUpdateRequest,
    ScheduleUpdateResponse,
    StartMonitoringRequest,
    StartMonitoringResponse,
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


@app.post("/public/leads", response_model=LeadResponse)
def create_lead(payload: LeadCreate, conn=Depends(get_conn), settings: Settings = Depends(get_settings)):
    """
    Public endpoint for lead capture from website form.
    
    Creates a lead entry in the database and sends a sample report email.
    Does NOT create a customer or start monitoring immediately.
    """
    from ranksentinel.mailgun import MailgunClient
    from ranksentinel.reporting.email_templates import render_sample_report
    
    ts = now_iso()
    
    # Validate email format (basic check)
    email_raw = payload.email.strip().lower()
    if not email_raw or "@" not in email_raw:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    # Canonicalize email to prevent abuse via Gmail dot/plus tricks
    email_canonical = canonicalize_email(email_raw)
    
    # Validate domain format (basic check)
    domain = payload.domain.strip()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    
    # Check if customer already exists (any status) using canonical email
    existing = fetch_one(
        conn,
        "SELECT id, status FROM customers WHERE email_canonical=?",
        (email_canonical,),
    )
    
    if existing:
        return LeadResponse(
            success=True,
            message="We already have your information. We'll be in touch soon!",
            lead_id=existing["id"],
        )
    
    # Create new customer with 'active' status (lead tracking happens via other means)
    # Note: 'lead' is not a valid status per DB schema; using 'active' as default
    lead_id = execute(
        conn,
        "INSERT INTO customers(name,email_raw,email_canonical,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
        (email_raw, email_raw, email_canonical, "active", ts, ts),
    )
    
    # Store domain and key pages in settings table
    execute(conn, "INSERT OR IGNORE INTO settings(customer_id) VALUES(?)", (lead_id,))
    
    # Store domain as sitemap_url placeholder (will be processed later)
    sitemap_url = domain if domain.startswith("http") else f"https://{domain}"
    execute(
        conn,
        "UPDATE settings SET sitemap_url=? WHERE customer_id=?",
        (sitemap_url, lead_id),
    )
    
    # If key pages provided, store them as targets
    if payload.key_pages:
        key_pages_list = [url.strip() for url in payload.key_pages.split("\n") if url.strip()]
        for url in key_pages_list:
            execute(
                conn,
                "INSERT INTO targets(customer_id,url,is_key,created_at) VALUES(?,?,?,?)",
                (lead_id, url, True, ts),
            )
    
    # Send sample report email (if Mailgun configured)
    email_sent = False
    if settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN:
        try:
            mailgun_client = MailgunClient(settings)
            message = render_sample_report(domain)
            
            # Send to the lead's email
            mailgun_client.send_email(
                to=email_raw,
                subject=message.subject,
                text=message.text,
                html=message.html,
            )
            email_sent = True
        except Exception as e:
            # Log error but don't fail the request
            # TODO: Add proper logging
            print(f"Failed to send sample report email: {e}")
    
    return LeadResponse(
        success=True,
        message="Thank you! Check your email for a sample report. Ready to start monitoring? Visit ranksentinel.com/schedule",
        lead_id=lead_id,
    )


@app.post("/public/start-monitoring", response_model=StartMonitoringResponse)
def start_monitoring(payload: StartMonitoringRequest, conn=Depends(get_conn), settings: Settings = Depends(get_settings)):
    """
    Public endpoint for immediate trial provisioning from website form.
    
    Creates a trial customer with limited monitoring caps and sends confirmation email.
    Trial limits: 3-5 key pages, 25-50 sitemap URLs, 0-1 PSI pages, critical-only daily checks.
    """
    from ranksentinel.mailgun import MailgunClient
    from ranksentinel.reporting.email_templates import render_trial_confirmation
    
    ts = now_iso()
    
    # Validate email format (basic check)
    email_raw = payload.email.strip().lower()
    if not email_raw or "@" not in email_raw:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    # Canonicalize email to prevent abuse via Gmail dot/plus tricks
    email_canonical = canonicalize_email(email_raw)
    
    # Validate domain format (basic check)
    domain = payload.domain.strip()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    
    # Check if customer already exists using canonical email
    existing = fetch_one(
        conn,
        "SELECT id, status FROM customers WHERE email_canonical=?",
        (email_canonical,),
    )
    
    if existing:
        # Customer already exists, return appropriate message based on status
        customer_id = existing["id"]
        status = existing["status"]
        
        if status == "trial":
            message = "Your trial is already active!"
        elif status in ("paywalled", "previously_interested"):
            message = "Welcome back! Your monitoring is reactivating."
        else:
            message = "Your monitoring is already set up!"
        
        return StartMonitoringResponse(
            success=True,
            message=message,
            customer_id=customer_id,
        )
    else:
        # Create new trial customer with both raw and canonical email
        customer_id = execute(
            conn,
            "INSERT INTO customers(name,email_raw,email_canonical,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (email_raw, email_raw, email_canonical, "trial", ts, ts),
        )
        execute(conn, "INSERT OR IGNORE INTO settings(customer_id) VALUES(?)", (customer_id,))
    
    # Apply trial limits to settings
    # Key pages max: 5, Sitemap crawl: 50 URLs, PSI: 1 page
    execute(
        conn,
        "UPDATE settings SET crawl_limit=?, psi_enabled=?, psi_urls_limit=? WHERE customer_id=?",
        (50, 1, 1, customer_id),
    )
    
    # Store domain as sitemap_url
    sitemap_url = domain if domain.startswith("http") else f"https://{domain}"
    execute(
        conn,
        "UPDATE settings SET sitemap_url=? WHERE customer_id=?",
        (sitemap_url, customer_id),
    )
    
    # If key pages provided, store them as targets (limit to 5 for trial)
    if payload.key_pages:
        key_pages_list = [url.strip() for url in payload.key_pages.split("\n") if url.strip()]
        # Enforce trial limit of 5 key pages
        key_pages_list = key_pages_list[:5]
        
        for url in key_pages_list:
            # Check if target already exists
            existing_target = fetch_one(
                conn,
                "SELECT id FROM targets WHERE customer_id=? AND url=?",
                (customer_id, url),
            )
            if not existing_target:
                execute(
                    conn,
                    "INSERT INTO targets(customer_id,url,is_key,created_at) VALUES(?,?,?,?)",
                    (customer_id, url, True, ts),
                )
    
    # Send trial confirmation email (if Mailgun configured)
    email_sent = False
    if settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN:
        try:
            mailgun_client = MailgunClient(settings)
            message = render_trial_confirmation(domain, email_raw)
            
            mailgun_client.send_email(
                to=email_raw,
                subject=message.subject,
                text=message.text,
                html=message.html,
            )
            email_sent = True
        except Exception as e:
            # Log error but don't fail the request
            # TODO: Add proper logging
            print(f"Failed to send trial confirmation email: {e}")
    
    return StartMonitoringResponse(
        success=True,
        message="Your 7-day trial has started! Check your email for details.",
        customer_id=customer_id,
    )


@app.post("/public/schedule", response_model=ScheduleUpdateResponse)
def update_schedule(payload: ScheduleUpdateRequest, conn=Depends(get_conn)):
    """
    Public endpoint for updating digest schedule (token-protected).
    
    Returns authoritative next run time with DST-safe timezone handling.
    """
    from datetime import timedelta
    from zoneinfo import ZoneInfo
    from ranksentinel.db import update_customer_schedule, validate_schedule_token, mark_schedule_token_used
    
    # Validate token and find customer
    token_info = validate_schedule_token(conn, payload.token)
    
    if not token_info:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    
    customer_id = token_info["customer_id"]
    
    # Mark token as used (single-use pattern)
    mark_schedule_token_used(conn, payload.token)
    
    # Validate timezone
    try:
        tz = ZoneInfo(payload.digest_timezone)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {payload.digest_timezone}")
    
    # Validate time format (already validated by Pydantic pattern, but check range)
    try:
        hour, minute = map(int, payload.digest_time_local.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Time out of range")
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {payload.digest_time_local}")
    
    # Calculate next run time with DST-aware timezone handling
    now = datetime.now(tz)
    
    # Calculate days until target weekday
    days_ahead = (payload.digest_weekday - now.weekday()) % 7
    
    # If it's the target weekday today, check if time has passed
    if days_ahead == 0:
        target_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now >= target_today:
            # Already passed today, schedule for next week
            days_ahead = 7
    
    # Calculate next run time
    next_run = now + timedelta(days=days_ahead)
    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Convert to UTC for storage
    next_run_utc = next_run.astimezone(ZoneInfo("UTC"))
    
    # Get UTC offset at the next run time (DST-aware)
    utc_offset_minutes = int(next_run.utcoffset().total_seconds() / 60)
    
    # Update customer schedule in database
    update_customer_schedule(
        conn,
        customer_id,
        payload.digest_weekday,
        payload.digest_time_local,
        payload.digest_timezone,
    )
    
    return ScheduleUpdateResponse(
        success=True,
        message="Schedule updated successfully",
        timezone=payload.digest_timezone,
        utc_offset_minutes=utc_offset_minutes,
        next_run_at_utc=next_run_utc.isoformat(),
        next_run_at_local=next_run.isoformat(),
    )
