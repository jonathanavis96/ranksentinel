# NEURONS.md — RankSentinel Repository Map

A quick map of the RankSentinel repo structure.

## Purpose

RankSentinel monitors SEO regressions and sends low-noise daily critical alerts plus weekly digests.

## Structure

```text
ranksentinel/
├── BOOTSTRAP.md                 # Operational spec (scope/schedule/schema/severity/cron)
├── README.md
├── .env.example
├── pyproject.toml
├── src/ranksentinel/            # Application (FastAPI + runner stubs)
├── scripts/                     # Local run scripts
├── docs/                        # Runbook + sample report
├── cortex/                      # Cortex planning layer (scripts + docs)
└── workers/ralph/               # Ralph execution loop + verifier
```

## Key entrypoints

- Admin API: `src/ranksentinel/api.py`
- Daily job: `src/ranksentinel/runner/daily_checks.py`
- Weekly job: `src/ranksentinel/runner/weekly_digest.py`

## Agent workflow

- Cortex planning: `bash cortex/snapshot.sh`, `bash cortex/one-shot.sh`
- Ralph execution: `bash workers/ralph/loop.sh`

Cortex and Ralph must treat `BOOTSTRAP.md` as the operational spec.
