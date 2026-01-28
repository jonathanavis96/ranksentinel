# Project: RankSentinel
Location: ./tmp_rovodev_ranksentinel_out
Purpose: Automated weekly SEO regression reports (plus optional daily critical alerts) focusing on indexability and high-signal site health regressions (robots.txt, sitemap changes, canonicals, noindex, title changes, broken internal links, new 404s) with optional PageSpeed Insights regressions on key URLs.
Tech Stack: Python, FastAPI, SQLite, Mailgun, PageSpeed Insights API, cron (Hostinger VPS)
Goals: Bootstrap repo with dedicated Cortex+Ralph, create BOOTSTRAP operational spec, provide sample weekly report, scaffold minimal FastAPI admin endpoints and SQLite schema, stub daily/weekly runner entrypoints, include VPS runbook and cron schedule.
