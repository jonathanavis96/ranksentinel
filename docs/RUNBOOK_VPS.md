# VPS Runbook (Hostinger) — RankSentinel

This runbook describes how to run RankSentinel autonomously on a Hostinger VPS using cron.

RankSentinel is designed to be **silent on success** and **noisy on failure** (operator alerting only).

## 1) Target layout

Recommended:

- Repo path: `/opt/ranksentinel`
- Logs: `/opt/ranksentinel/logs/`
- Database: `/opt/ranksentinel/ranksentinel.sqlite3`

## 2) System prerequisites

- Python 3.11+
- `git`
- `cron`

## 3) Install

```bash
sudo mkdir -p /opt/ranksentinel
sudo chown -R \"$USER\":\"$USER\" /opt/ranksentinel

cd /opt/ranksentinel
# clone your repository here (once GitHub is connected)
# git clone ... .

python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install -e \"./[dev]\"
```

## 4) Configuration

Create `/opt/ranksentinel/.env` based on `.env.example`.

Required:

- `MAILGUN_API_KEY`
- `MAILGUN_DOMAIN`
- `MAILGUN_FROM`
- `PSI_API_KEY`

Optional:

- `RANKSENTINEL_OPERATOR_EMAIL`

Security:

- Do not commit `.env`.
- Do not log secrets.

## 5) Cron setup

Edit crontab:

```bash
crontab -e
```

Add:

```bash
# Daily checks (01:15)
15 1 * * * cd /opt/ranksentinel && /bin/bash scripts/run_daily.sh

# Weekly digest (Monday 09:00)
0 9 * * 1 cd /opt/ranksentinel && /bin/bash scripts/run_weekly.sh
```

**Log configuration:**

The scripts accept the `RANKSENTINEL_LOG_DIR` environment variable (default: `./logs`).

To customize the log directory:

```bash
# Daily checks with custom log directory
15 1 * * * cd /opt/ranksentinel && RANKSENTINEL_LOG_DIR=/opt/ranksentinel/logs /bin/bash scripts/run_daily.sh

# Weekly digest with custom log directory
0 9 * * 1 cd /opt/ranksentinel && RANKSENTINEL_LOG_DIR=/opt/ranksentinel/logs /bin/bash scripts/run_weekly.sh
```

The scripts automatically:

- Create the log directory if it doesn't exist
- Write to date-stamped log files: `daily_YYYYMMDD.log` and `weekly_YYYYMMDD.log`
- Capture both stdout and stderr

## 6) Operational expectations

- Jobs must be idempotent.
- Jobs should retry transient network failures.
- Job failure must surface to operator:
  - write clear logs
  - optional operator email on repeated failures

## 7) Smoke test (manual)

Run once:

```bash
cd /opt/ranksentinel
bash scripts/run_daily.sh
bash scripts/run_weekly.sh
```

Check logs:

```bash
# View today's daily log
tail -n 200 /opt/ranksentinel/logs/daily_$(date +%Y%m%d).log

# View today's weekly log
tail -n 200 /opt/ranksentinel/logs/weekly_$(date +%Y%m%d).log
```
