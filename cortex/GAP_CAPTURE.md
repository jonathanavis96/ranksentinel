# Gap Capture - PROJECT_NAME

Local gap capture for this project. Gaps are synced to brain's
`skills/self-improvement/GAP_BACKLOG.md` via marker file protocol.

## How It Works

1. **Capture:** When you discover a knowledge gap, add it below using the format
2. **Mark:** Create `.gap_pending` marker: `touch cortex/.gap_pending`
3. **Sync:** Brain's Cortex detects pending gaps and runs `sync_gaps.sh`
4. **Clear:** After sync, this file is cleared and marker removed

## Format

```markdown
### YYYY-MM-DD HH:MM — <Suggested Skill Name>
- **Type:** Knowledge / Procedure / Tooling / Pattern / Debugging / Reference
- **Why useful:** <1–2 lines>
- **When triggered:** <what you were trying to do>
- **Evidence:** <paths, filenames, snippets, observations>
- **Priority:** P0 / P1 / P2
- **Project:** PROJECT_NAME
```

## Captured Gaps

<!-- Add new gap entries below this line -->

### 2026-01-29 18:04 — SQLite schema/test alignment + migration discipline (created_at, snapshots, artifacts)
- **Type:** Pattern / Debugging / Procedure
- **Why useful:** Prevent regressions where runtime DB schema evolves but pytest fixtures + tests drift, causing `NOT NULL` and missing-table failures; ensure migrations and tests stay in lockstep.
- **When triggered:** After adding 0K/0S/0R/0E work, `pytest -q` showed failures like missing `snapshots` table and `customers.created_at` NOT NULL violations; robots artifact tests also drifted from persistence contract.
- **Evidence:**
  - Failing tests/errors:
    - `tests/test_sitemap_fetch.py` → `sqlite3.IntegrityError: NOT NULL constraint failed: customers.created_at`
    - `tests/test_page_fetcher.py::test_persist_fetch_results_placeholder` → `sqlite3.OperationalError: no such table: snapshots`
    - `tests/test_robots_fetch.py` assertions mismatched vs current artifact storage semantics
  - Schema contract lives in `src/ranksentinel/db.py` (`customers.created_at`/`updated_at` are `NOT NULL`; `snapshots` table expected by page fetch persistence)
  - Suggested corrective pattern:
    - tests must create DB via a shared fixture that calls `init_db(conn)`
    - if schema adds `NOT NULL` columns, either add safe DB defaults/backfill or update all test inserts
    - tests should assert artifact persistence via `ranksentinel.db` helpers (e.g. `get_latest_artifact`) rather than duplicating SQL assumptions
- **Priority:** P0
- **Project:** RankSentinel
