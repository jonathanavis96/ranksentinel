import sqlite3
from pathlib import Path
from typing import Any, Iterable

from ranksentinel.config import Settings


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('active','past_due','canceled')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS targets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  is_key INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS settings (
  customer_id INTEGER PRIMARY KEY,
  sitemap_url TEXT,
  crawl_limit INTEGER NOT NULL DEFAULT 100,
  psi_enabled INTEGER NOT NULL DEFAULT 1,
  psi_urls_limit INTEGER NOT NULL DEFAULT 5,
  psi_confirm_runs INTEGER NOT NULL DEFAULT 2,
  psi_perf_drop_threshold INTEGER NOT NULL DEFAULT 10,
  psi_lcp_increase_threshold_ms INTEGER NOT NULL DEFAULT 500,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  run_id TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  status_code INTEGER NOT NULL,
  final_url TEXT NOT NULL,
  redirect_chain TEXT NOT NULL,
  title TEXT,
  canonical TEXT,
  meta_robots TEXT,
  content_hash TEXT NOT NULL,
  error_type TEXT,
  error TEXT,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_lookup ON snapshots(customer_id, run_type, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_run ON snapshots(customer_id, run_id);

CREATE TABLE IF NOT EXISTS findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  run_id TEXT NOT NULL,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  severity TEXT NOT NULL CHECK(severity IN ('critical','warning','info')),
  category TEXT NOT NULL,
  title TEXT NOT NULL,
  details_md TEXT NOT NULL,
  url TEXT,
  dedupe_key TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id),
  UNIQUE(dedupe_key)
);

CREATE TABLE IF NOT EXISTS deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  sent_at TEXT NOT NULL,
  recipient TEXT NOT NULL,
  subject TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_message_id TEXT,
  status TEXT NOT NULL CHECK(status IN ('sent','skipped','failed')),
  error TEXT,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS psi_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  fetched_at TEXT NOT NULL,
  perf_score INTEGER,
  lcp_ms INTEGER,
  cls_score REAL,
  inp_ms INTEGER,
  is_regression INTEGER NOT NULL DEFAULT 0,
  is_confirmed INTEGER NOT NULL DEFAULT 0,
  regression_type TEXT,
  raw_json TEXT,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE INDEX IF NOT EXISTS idx_psi_results_lookup ON psi_results(customer_id, url, fetched_at DESC);

CREATE TABLE IF NOT EXISTS broken_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  source_url TEXT NOT NULL,
  target_url TEXT NOT NULL,
  status_code INTEGER NOT NULL,
  error_message TEXT,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  detected_at TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE INDEX IF NOT EXISTS idx_broken_links_lookup ON broken_links(customer_id, run_type, detected_at DESC);

CREATE TABLE IF NOT EXISTS artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  kind TEXT NOT NULL,
  subject TEXT NOT NULL,
  artifact_sha TEXT NOT NULL,
  raw_content TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE INDEX IF NOT EXISTS idx_artifacts_lookup ON artifacts(customer_id, kind, subject, fetched_at DESC);

CREATE TABLE IF NOT EXISTS run_coverage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  run_id TEXT NOT NULL,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  sitemap_url TEXT,
  total_urls INTEGER,
  sampled_urls INTEGER,
  success_count INTEGER,
  error_count INTEGER,
  http_429_count INTEGER,
  http_404_count INTEGER,
  broken_link_count INTEGER,
  created_at TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id),
  UNIQUE(customer_id, run_id, run_type)
);

CREATE INDEX IF NOT EXISTS idx_run_coverage_lookup ON run_coverage(customer_id, run_type, created_at DESC);
"""


def connect(settings: Settings) -> sqlite3.Connection:
    db_path = Path(settings.RANKSENTINEL_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def fetch_all(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
    cur = conn.execute(sql, tuple(params))
    return list(cur.fetchall())


def fetch_one(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
    cur = conn.execute(sql, tuple(params))
    return cur.fetchone()


def execute(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> int:
    cur = conn.execute(sql, tuple(params))
    conn.commit()
    return int(cur.lastrowid)


def get_latest_artifact(
    conn: sqlite3.Connection, customer_id: int, kind: str, subject: str
) -> sqlite3.Row | None:
    """Get the most recent artifact for a given (customer_id, kind, subject).
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        kind: Artifact kind (e.g., 'robots_txt', 'sitemap')
        subject: Artifact subject (e.g., URL or identifier)
    
    Returns:
        Row with artifact data or None if no baseline exists
    """
    return fetch_one(
        conn,
        "SELECT id, artifact_sha, raw_content, fetched_at "
        "FROM artifacts "
        "WHERE customer_id=? AND kind=? AND subject=? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (customer_id, kind, subject),
    )


def store_artifact(
    conn: sqlite3.Connection,
    customer_id: int,
    kind: str,
    subject: str,
    artifact_sha: str,
    raw_content: str,
    fetched_at: str,
) -> int:
    """Store a new artifact snapshot.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        kind: Artifact kind (e.g., 'robots_txt', 'sitemap')
        subject: Artifact subject (e.g., URL or identifier)
        artifact_sha: SHA256 hash of the raw_content
        raw_content: The actual artifact content
        fetched_at: ISO timestamp of when artifact was fetched
    
    Returns:
        ID of the inserted artifact row
    """
    return execute(
        conn,
        "INSERT INTO artifacts(customer_id, kind, subject, artifact_sha, raw_content, fetched_at) "
        "VALUES(?,?,?,?,?,?)",
        (customer_id, kind, subject, artifact_sha, raw_content, fetched_at),
    )


def generate_finding_dedupe_key(
    customer_id: int,
    run_type: str,
    category: str,
    title: str,
    url: str | None,
    period: str,
) -> str:
    """Generate a deterministic dedupe key for a finding.
    
    Args:
        customer_id: Customer ID
        run_type: 'daily' or 'weekly'
        category: Finding category (e.g., 'indexability', 'performance')
        title: Finding title
        url: URL associated with the finding (optional)
        period: Period identifier (e.g., '2026-01-29' for daily, '2026-W05' for weekly)
    
    Returns:
        SHA256 hash of the dedupe components
    """
    import hashlib
    
    components = f"{customer_id}|{run_type}|{category}|{title}|{url or ''}|{period}"
    return hashlib.sha256(components.encode("utf-8")).hexdigest()


def insert_run_coverage(
    conn: sqlite3.Connection,
    customer_id: int,
    run_id: str,
    run_type: str,
    sitemap_url: str | None,
    total_urls: int | None,
    sampled_urls: int | None,
    success_count: int | None,
    error_count: int | None,
    http_429_count: int | None,
    http_404_count: int | None,
    broken_link_count: int | None,
    created_at: str,
) -> int:
    """Insert or update run coverage statistics.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        run_id: Unique run identifier
        run_type: 'daily' or 'weekly'
        sitemap_url: URL of the sitemap being monitored
        total_urls: Total URLs found in sitemap
        sampled_urls: Number of URLs sampled (based on crawl_limit)
        success_count: Number of successful fetches
        error_count: Number of failed fetches
        http_429_count: Number of 429 rate limit responses
        http_404_count: Number of 404 responses
        broken_link_count: Number of broken links detected
        created_at: ISO timestamp of when the run was created
    
    Returns:
        ID of the inserted/updated row
    """
    return execute(
        conn,
        """INSERT INTO run_coverage(
            customer_id, run_id, run_type, sitemap_url, total_urls, sampled_urls,
            success_count, error_count, http_429_count, http_404_count, 
            broken_link_count, created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(customer_id, run_id, run_type) DO UPDATE SET
            sitemap_url=excluded.sitemap_url,
            total_urls=excluded.total_urls,
            sampled_urls=excluded.sampled_urls,
            success_count=excluded.success_count,
            error_count=excluded.error_count,
            http_429_count=excluded.http_429_count,
            http_404_count=excluded.http_404_count,
            broken_link_count=excluded.broken_link_count,
            created_at=excluded.created_at
        """,
        (
            customer_id, run_id, run_type, sitemap_url, total_urls, sampled_urls,
            success_count, error_count, http_429_count, http_404_count,
            broken_link_count, created_at
        ),
    )


def get_latest_run_coverage(
    conn: sqlite3.Connection,
    customer_id: int,
    run_type: str,
) -> sqlite3.Row | None:
    """Get the most recent run coverage for a customer.
    
    Args:
        conn: Database connection
        customer_id: Customer ID
        run_type: 'daily' or 'weekly'
    
    Returns:
        Row with coverage data or None if no coverage exists
    """
    return fetch_one(
        conn,
        """SELECT id, customer_id, run_id, run_type, sitemap_url, total_urls,
                  sampled_urls, success_count, error_count, http_429_count,
                  http_404_count, broken_link_count, created_at
           FROM run_coverage
           WHERE customer_id=? AND run_type=?
           ORDER BY created_at DESC LIMIT 1""",
        (customer_id, run_type),
    )
