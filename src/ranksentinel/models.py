from pydantic import BaseModel, Field, HttpUrl


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class CustomerOut(BaseModel):
    id: int
    name: str
    status: str


class TargetCreate(BaseModel):
    url: HttpUrl
    is_key: bool = True


class TargetOut(BaseModel):
    id: int
    customer_id: int
    url: str
    is_key: bool


class CustomerSettingsPatch(BaseModel):
    sitemap_url: HttpUrl | None = None
    crawl_limit: int | None = Field(default=None, ge=1, le=5000)
    psi_enabled: bool | None = None
    psi_urls_limit: int | None = Field(default=None, ge=0, le=100)


class RunCoverageOut(BaseModel):
    """Model for run coverage statistics."""

    id: int
    customer_id: int
    run_id: str
    run_type: str
    sitemap_url: str | None
    total_urls: int | None
    sampled_urls: int | None
    success_count: int | None
    error_count: int | None
    http_429_count: int | None
    http_404_count: int | None
    broken_link_count: int | None
    created_at: str


class LeadCreate(BaseModel):
    """Model for lead capture from website form."""

    email: str = Field(min_length=1, max_length=200)
    domain: str = Field(min_length=1, max_length=500)
    key_pages: str | None = Field(default=None, max_length=10000)
    use_sitemap: bool = True


class LeadResponse(BaseModel):
    """Response for lead creation."""

    success: bool
    message: str
    lead_id: int | None = None


class StartMonitoringRequest(BaseModel):
    """Model for start monitoring request from website form."""

    email: str = Field(min_length=1, max_length=200)
    domain: str = Field(min_length=1, max_length=500)
    key_pages: str | None = Field(default=None, max_length=10000)
    use_sitemap: bool = True


class StartMonitoringResponse(BaseModel):
    """Response for start monitoring request."""

    success: bool
    message: str
    customer_id: int | None = None


class ScheduleUpdateRequest(BaseModel):
    """Model for schedule update request."""

    token: str = Field(min_length=1, max_length=500)
    digest_weekday: int = Field(ge=0, le=6, description="Day of week: 0=Monday, 6=Sunday")
    digest_time_local: str = Field(
        min_length=5, max_length=5, pattern=r"^\d{2}:\d{2}$", description="Time in HH:MM format"
    )
    digest_timezone: str = Field(min_length=1, max_length=100, description="IANA timezone name")


class ScheduleUpdateResponse(BaseModel):
    """Response for schedule update request."""

    success: bool
    message: str
    timezone: str
    utc_offset_minutes: int
    next_run_at_utc: str
    next_run_at_local: str | None = None
