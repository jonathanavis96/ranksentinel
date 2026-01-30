# RankSentinel

RankSentinel sends automated **weekly SEO regression reports** (and optional daily critical alerts) for a website.

## MVP promise

Weekly email report:

- What changed
- What broke
- What regressed (SEO + PageSpeed Insights on key URLs)
- What to do first (prioritized, low-noise)

Daily critical checks:

- Only high-severity regressions (avoid spam)

## Differentiation

This is not generic page monitoring. RankSentinel focuses on SEO regressions and indexability risk:

- `robots.txt` changes
- sitemap changes (hash + URL count delta)
- canonical changes
- `noindex` changes
- title changes
- broken internal links + new 404s
- optional PSI regressions on key URLs only (two-run confirmation)

## Stack (v1)

Python, FastAPI, SQLite, Mailgun, PageSpeed Insights API, cron (Hostinger VPS)

## Key docs

- `BOOTSTRAP.md` — operational spec (schedule, severity model, schema outline, normalization)
- `docs/SAMPLE_REPORT.md` — example weekly email output
- `docs/RUNBOOK_VPS.md` — Hostinger VPS + cron runbook

## Quick start (local)

1) Create a virtualenv and install deps:

```bash
python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install -e ".[dev]"
```

2) Run tests:

```bash
./.venv/bin/pytest -q
```

3) Copy environment file:

```bash
cp .env.example .env
```

3) Run the admin API:

```bash
bash scripts/run_local.sh
```

4) Seed a customer and targets:

- Open: `http://127.0.0.1:8000/docs`
- Use:
  - `POST /admin/customers`
  - `POST /admin/customers/{customer_id}/targets`
  - `PATCH /admin/customers/{customer_id}/settings`

5) Run jobs locally:

```bash
bash scripts/run_daily.sh
bash scripts/run_weekly.sh
```

## Development (Ralph)

**Default workflow:**

- Work happens on the `ranksentinel-work` branch (never directly on main)
- Use `workers/ralph/pr-batch.sh` to create PRs back to main
- Run `workers/ralph/loop.sh` to start AI-assisted development

```bash
cd workers/ralph
bash loop.sh --iterations 5
```

## 🧠 Built with Ralph Brain

This project uses [Ralph Brain](https://github.com/jonathanavis96/brain) for AI-assisted development.

Ralph integration is optional — the project works standalone.
