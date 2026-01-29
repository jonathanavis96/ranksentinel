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
