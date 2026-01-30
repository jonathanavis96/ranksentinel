# SKILL REQUEST: SQLite schema/test alignment + migration discipline

Created: 2026-01-29 16:51:24

## Problem

We introduced schema changes (e.g., `customers.created_at` / `customers.updated_at` as `NOT NULL`, and new tables like `snapshots`) and updated runtime code accordingly, but several tests still insert into tables without providing required columns and/or create raw SQLite connections without calling `init_db()`.

This led to failures such as:

- `sqlite3.IntegrityError: NOT NULL constraint failed: customers.created_at`
- `sqlite3.OperationalError: no such table: snapshots`

Additionally, behavioral tests (e.g., robots/sitemap artifact tests) can drift from the actual storage semantics if there isn’t a single “source of truth” helper for persistence.

## Requested Brain skill

Create a skill that teaches a consistent pattern for **SQLite schema evolution + pytest fixtures**:

1. **Schema invariants**
   - If a column is `NOT NULL`, all tests must provide it unless there is a DB default.
   - Prefer explicit timestamps in tests; avoid relying on SQLite defaults unless standardized.

2. **Migration discipline**
   - Any schema change must include:
     - an idempotent migration in `init_db()` (or a versioned migration system)
     - a test that proves migration from the “old schema” to the new schema

3. **Test DB creation contract**
   - Tests must create DBs via a shared fixture / helper that always calls `init_db(conn)`.
   - Avoid `sqlite3.connect()` directly unless the test explicitly validates pre-init behavior.

4. **Persistence helpers as API**
   - Tests should validate persistence via `ranksentinel.db.*` helpers (e.g., `store_artifact`, `get_latest_artifact`, `persist_fetch_results`) rather than duplicating SQL assumptions.

5. **Anti-patterns to warn about**
   - Creating new NOT NULL columns without updating test inserts.
   - Tests that depend on implicit ordering without `ORDER BY`.
   - Tests that create a bare SQLite DB and then call code that expects tables.

## Example acceptance checklist (for future PRs)

- [ ] `pytest -q` passes
- [ ] New NOT NULL columns are either backfilled + defaulted, or tests supply values
- [ ] A migration test exists proving old DBs can be upgraded
- [ ] Persistence semantics documented in one place and referenced by tests
