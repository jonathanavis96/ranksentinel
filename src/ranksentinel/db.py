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
  fetched_at TEXT NOT NULL,
  status_code INTEGER NOT NULL,
  final_url TEXT NOT NULL,
  redirect_chain TEXT NOT NULL,
  title TEXT,
  canonical TEXT,
  meta_robots TEXT,
  content_hash TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  run_type TEXT NOT NULL CHECK(run_type IN ('daily','weekly')),
  severity TEXT NOT NULL CHECK(severity IN ('critical','warning','info')),
  category TEXT NOT NULL,
  title TEXT NOT NULL,
  details_md TEXT NOT NULL,
  url TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
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
