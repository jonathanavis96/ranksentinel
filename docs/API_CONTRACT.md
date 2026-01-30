# RankSentinel API Contract (Website ↔ Backend)

**Version:** 1.0  
**Last Updated:** 2026-01-30

This document defines the contract between the RankSentinel marketing website (Next.js) and the backend API (FastAPI). It ensures frontend/backend compatibility and prevents integration issues.

---

## Base URL Configuration

- **Local Development:** `http://localhost:8000`
- **Production:** TBD (will be configured via environment variable)

The website must support configurable base URLs via `NEXT_PUBLIC_API_BASE_URL` environment variable.

---

## CORS Configuration

### Backend Requirements

The FastAPI backend must configure CORS to allow requests from:

- **Development origins:**
  - `http://localhost:3000` (Next.js dev server)
  - `http://127.0.0.1:3000`

- **Production origins:**
  - `https://ranksentinel.com` (primary domain)
  - Any preview/staging domains (TBD)

### CORS Headers

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://ranksentinel.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

---

## Public Endpoints (Website-Facing)

These endpoints will be called by the marketing website and require no authentication.

### 1. Lead Capture (Homepage CTA)

**Endpoint:** `POST /public/leads`

**Purpose:** Capture early interest leads from homepage "Start monitoring" CTA.

**Request Body:**

```json
{
  "email": "user@example.com",
  "domain": "https://example.com",
  "key_pages": ["https://example.com/pricing", "https://example.com/features"],
  "use_sitemap": true
}
```

**Field Validation:**

- `email` (required): Valid email format, max 255 chars
- `domain` (required): Valid HTTP/HTTPS URL
- `key_pages` (optional): Array of valid URLs, max 20 items
- `use_sitemap` (optional): Boolean, default `true`

**Business Rules:**

- If `use_sitemap` is `true`: Allow empty `key_pages`
- If `use_sitemap` is `false`: Require at least 1 `key_pages` entry
- Implement honeypot field `website` (hidden from users, must be empty)
- Apply email canonicalization (see Anti-Abuse section)

**Response (201 Created):**

```json
{
  "status": "ok",
  "message": "Lead captured successfully",
  "lead_id": 123
}
```

**Error Responses:**

```json
// 400 Bad Request - Validation error
{
  "detail": "Email is required"
}

// 409 Conflict - Duplicate email (after canonicalization)
{
  "detail": "This email has already been registered"
}

// 429 Too Many Requests - Rate limit exceeded
{
  "detail": "Too many requests. Please try again later."
}
```

---

### 2. Start Monitoring (Trial/Signup Flow)

**Endpoint:** `POST /public/start-monitoring`

**Purpose:** Create a new customer account and trigger First Insight report.

**Request Body:**

```json
{
  "email": "user@example.com",
  "domain": "https://example.com",
  "sitemap_url": "https://example.com/sitemap.xml",
  "key_pages": ["https://example.com/pricing"],
  "honeypot": ""
}
```

**Field Validation:**

- `email` (required): Valid email format, max 255 chars
- `domain` (required): Valid HTTP/HTTPS URL
- `sitemap_url` (optional): Valid sitemap URL
- `key_pages` (optional): Array of valid URLs, max 20 items
- `honeypot` (required): Must be empty string (anti-spam)

**Response (201 Created):**

```json
{
  "status": "ok",
  "message": "Monitoring started",
  "customer_id": 456,
  "report_status": "queued"
}
```

**Error Responses:**

```json
// 400 Bad Request
{
  "detail": "Invalid email format"
}

// 409 Conflict
{
  "detail": "Account already exists for this email"
}

// 429 Too Many Requests
{
  "detail": "Rate limit exceeded"
}

// 503 Service Unavailable
{
  "detail": "Service temporarily unavailable. Please try again."
}
```

---

## Admin Endpoints (Existing)

These are for internal/admin use only and should NOT be exposed to the public website.

### Health Check

**Endpoint:** `GET /health`

**Response (200 OK):**

```json
{
  "status": "ok"
}
```

---

### Create Customer

**Endpoint:** `POST /admin/customers`

**Request Body:**

```json
{
  "name": "Example Corp"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "name": "Example Corp",
  "status": "active"
}
```

---

### List Customers

**Endpoint:** `GET /admin/customers`

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "Example Corp",
    "status": "active"
  }
]
```

---

### Add Target URL

**Endpoint:** `POST /admin/customers/{customer_id}/targets`

**Request Body:**

```json
{
  "url": "https://example.com/page",
  "is_key": true
}
```

**Response (200 OK):**

```json
{
  "id": 10,
  "customer_id": 1,
  "url": "https://example.com/page",
  "is_key": true
}
```

---

### List Target URLs

**Endpoint:** `GET /admin/customers/{customer_id}/targets`

**Response (200 OK):**

```json
[
  {
    "id": 10,
    "customer_id": 1,
    "url": "https://example.com/page",
    "is_key": true
  }
]
```

---

### Update Customer Settings

**Endpoint:** `PATCH /admin/customers/{customer_id}/settings`

**Request Body (all fields optional):**

```json
{
  "sitemap_url": "https://example.com/sitemap.xml",
  "crawl_limit": 100,
  "psi_enabled": true,
  "psi_urls_limit": 5
}
```

**Response (200 OK):**

```json
{
  "status": "ok"
}
```

---

### Trigger First Insight Report

**Endpoint:** `POST /admin/customers/{customer_id}/send_first_insight`

**Request Body:** None

**Response (200 OK):**

```json
{
  "status": "ok",
  "message": "First Insight report triggered for customer 1",
  "result": {
    "run_id": "fi_20260130_123456",
    "findings_count": 12,
    "email_sent": true
  }
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "customer not found"
}
```

---

## Error Handling Standards

### HTTP Status Codes

- `200 OK` - Successful GET/PATCH/POST with response body
- `201 Created` - Successful resource creation
- `400 Bad Request` - Client validation error
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Duplicate resource (e.g., email already registered)
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Service degraded/unavailable

### Error Response Format

All errors follow FastAPI's standard format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors with multiple fields:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Anti-Abuse & Email Canonicalization

### Email Canonicalization Rules

To prevent trial abuse via email variants (e.g., `user@gmail.com`, `u.s.e.r@gmail.com`, `user+tag@gmail.com`):

1. **Lowercase and trim:** `User@Example.COM` → `user@example.com`
2. **Gmail/Googlemail specific:**
   - Remove all dots from local part: `u.s.e.r@gmail.com` → `user@gmail.com`
   - Strip `+tag` suffix: `user+tag@gmail.com` → `user@gmail.com`
   - Normalize domain: `@googlemail.com` → `@gmail.com`

### Database Schema

Store both raw and canonical emails:

- `email_raw` - Original email as submitted
- `email_canonical` - Normalized email for deduplication

### Uniqueness Constraints

- `email_canonical` must be unique per customer account
- Return `409 Conflict` if duplicate canonical email detected

### Honeypot Field

All public forms must include a hidden `honeypot` field:

- Field name: `website` or `honeypot`
- Hidden from users via CSS (`display: none`)
- Must be empty string on submission
- If non-empty, silently reject (return 200 but don't create account)

---

## Rate Limiting (Future)

### Recommended Limits

- **Public endpoints:** 10 requests per IP per minute
- **Admin endpoints:** 100 requests per IP per minute

### Implementation Notes

- Use FastAPI middleware (e.g., `slowapi`)
- Return `429 Too Many Requests` with `Retry-After` header
- Log rate limit violations for abuse monitoring

---

## Security Considerations

1. **Input Validation:**
   - Sanitize all URL inputs
   - Validate email formats
   - Limit array sizes (max 20 key_pages)
   - Reject excessively long strings

2. **SQL Injection:**
   - Use parameterized queries (already implemented)
   - Never concatenate user input into SQL

3. **SSRF Protection:**
   - Validate domain/URL inputs
   - Block private IP ranges (127.0.0.1, 10.x.x.x, 192.168.x.x)
   - Implement request timeouts

4. **Secrets Management:**
   - Never log API keys, emails, or sensitive data
   - Use environment variables for configuration
   - Rotate API keys regularly

---

## Frontend Integration Guide

### Example: Lead Capture Form

```typescript
async function submitLeadForm(data: {
  email: string;
  domain: string;
  keyPages: string[];
  useSitemap: boolean;
}) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/public/leads`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: data.email,
      domain: data.domain,
      key_pages: data.keyPages,
      use_sitemap: data.useSitemap,
      honeypot: '', // Always empty for legitimate users
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit form');
  }

  return response.json();
}
```

### Error Handling

```typescript
try {
  const result = await submitLeadForm(formData);
  // Show success message
  showSuccessMessage(result.message);
} catch (error) {
  if (error.message.includes('already been registered')) {
    // Show duplicate email error
    showError('This email is already registered. Please sign in instead.');
  } else if (error.message.includes('Rate limit')) {
    // Show rate limit error
    showError('Too many attempts. Please try again in a few minutes.');
  } else {
    // Generic error
    showError('Something went wrong. Please try again.');
  }
}
```

---

## Testing Checklist

- [ ] CORS headers allow website origin
- [ ] Email canonicalization works for Gmail variants
- [ ] Honeypot field rejects spam submissions
- [ ] Duplicate email detection returns 409
- [ ] Validation errors return clear messages
- [ ] Rate limiting works (when implemented)
- [ ] Success responses match documented format
- [ ] Error responses match documented format

---

## Future Considerations

1. **Authentication:** OAuth2/JWT for customer portal
2. **Webhooks:** Payment provider integration (Stripe)
3. **Real-time Updates:** WebSocket for live report status
4. **API Versioning:** `/v1/`, `/v2/` path prefixes
5. **GraphQL:** Consider for complex data fetching needs

---

## Changelog

### v1.0 (2026-01-30)

- Initial API contract document
- Defined public endpoints: `/public/leads`, `/public/start-monitoring`
- Documented admin endpoints
- Specified CORS, error handling, and security requirements
- Added email canonicalization rules
- Included frontend integration examples
