# Manual Validation: Task 0.10 - Per-Customer Isolation

## Goal
Verify that one customer failing does not abort the whole daily/weekly run.

## Acceptance Criteria
1. Errors are caught per customer and recorded (DB + logs)
2. The runner continues to process remaining customers
3. Job exit code reflects overall success/failure policy (decided in Phase 5.4)

## Test Setup

### 1. Create Test Database with Two Customers

```bash
# Use the existing ranksentinel.sqlite3 or create a test copy
cp ranksentinel.sqlite3 ranksentinel_test.sqlite3

# Set up test data
sqlite3 ranksentinel_test.sqlite3 <<EOF
-- Ensure we have two active customers
INSERT OR IGNORE INTO customers (id, name, email, status, created_at, updated_at) 
VALUES (99, 'Good Customer', 'good@test.com', 'active', datetime('now'), datetime('now'));

INSERT OR IGNORE INTO customers (id, name, email, status, created_at, updated_at) 
VALUES (100, 'Bad Customer', 'bad@test.com', 'active', datetime('now'), datetime('now'));

-- Add a valid target for customer 99
INSERT OR IGNORE INTO targets (customer_id, url, is_key, created_at, updated_at)
VALUES (99, 'https://example.com/', 1, datetime('now'), datetime('now'));

-- Add an INVALID target for customer 100 (will cause fetch to fail)
INSERT OR IGNORE INTO targets (customer_id, url, is_key, created_at, updated_at)
VALUES (100, 'https://invalid-domain-that-does-not-exist-12345.com/', 1, datetime('now'), datetime('now'));
EOF
```

### 2. Run Daily Check

```bash
export RANKSENTINEL_DB_PATH=ranksentinel_test.sqlite3
export PSI_API_KEY=""  # Empty for this test
export MAILGUN_API_KEY=""
export MAILGUN_DOMAIN=""
export MAILGUN_FROM=""

PYTHONPATH=src python3 -m ranksentinel.runner.__main__daily 2>&1 | tee daily_test_output.log
```

### 3. Verify Results

#### Check Console Output
The output should contain:
- `ERROR: Customer 100 processing failed:` (or similar error message)
- `SUMMARY: Processed 2 customer(s) - 1 succeeded, 1 failed`
- `Failed customers: 100`

```bash
grep -E "ERROR.*Customer 100|SUMMARY.*Processed|Failed customers" daily_test_output.log
```

#### Check Database for Customer 99 (should succeed)
```bash
sqlite3 ranksentinel_test.sqlite3 <<EOF
-- Should have a snapshot for customer 99
SELECT COUNT(*) as snapshot_count FROM snapshots WHERE customer_id=99;

-- Should NOT have error findings for customer 99
SELECT COUNT(*) as error_count FROM findings WHERE customer_id=99 AND category='system';
EOF
```

Expected output:
- snapshot_count: 1 (or more)
- error_count: 0

#### Check Database for Customer 100 (should have error recorded)
```bash
sqlite3 ranksentinel_test.sqlite3 <<EOF
-- Should have an error finding for customer 100
SELECT title, category, severity FROM findings 
WHERE customer_id=100 AND category='system' 
ORDER BY created_at DESC LIMIT 1;
EOF
```

Expected output:
- title: "Daily run processing error"
- category: "system"
- severity: "critical"

### 4. Run Weekly Check

```bash
PYTHONPATH=src python3 -m ranksentinel.runner.__main__weekly 2>&1 | tee weekly_test_output.log
```

### 5. Verify Weekly Results

Similar to daily, check:
- Console output has SUMMARY line
- Customer 99 has findings
- Customer 100 has error finding with category='system'

## Cleanup

```bash
# Remove test database
rm -f ranksentinel_test.sqlite3 daily_test_output.log weekly_test_output.log
```

## Success Criteria

✅ Daily run completes (exit code 0 or appropriate error code)
✅ Weekly run completes (exit code 0 or appropriate error code)
✅ Console shows "SUMMARY: Processed 2 customer(s) - 1 succeeded, 1 failed"
✅ Customer 99 (good) has normal snapshots/findings
✅ Customer 100 (bad) has error finding in database with category='system'
✅ Both customers were processed (one didn't block the other)
