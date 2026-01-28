# RankSentinel

Automated weekly SEO regression reports (plus optional daily critical alerts) focusing on indexability and high-signal site health regressions (robots.txt, sitemap changes, canonicals, noindex, title changes, broken internal links, new 404s) with optional PageSpeed Insights regressions on key URLs.

## Tech Stack

Python, FastAPI, SQLite, Mailgun, PageSpeed Insights API, cron (Hostinger VPS)

## Goals

Bootstrap repo with dedicated Cortex+Ralph, create BOOTSTRAP operational spec, provide sample weekly report, scaffold minimal FastAPI admin endpoints and SQLite schema, stub daily/weekly runner entrypoints, include VPS runbook and cron schedule.

## Development

**Default workflow:**
- Work happens on the `ranksentinel-work` branch (never directly on main)
- Use `ralph/pr-batch.sh` to create PRs back to main
- Run `ralph/loop.sh` to start AI-assisted development

### Getting Started

```bash
cd workers/ralph
bash loop.sh --iterations 5
```

## 🧠 Built with Ralph Brain

This project uses [Ralph Brain](https://github.com/jonathanavis96/brain) for AI-assisted development.

Ralph integration is optional - the project works standalone.
