# NEURONS.md — RankSentinel Repository Map (Cortex)

This file exists so Cortex chat entrypoints can always load a repo map even if they
expect `cortex/NEURONS.md`.

> Canonical repo map (often more detailed): `../NEURONS.md`.

## Quick Map

```text
ranksentinel/
├── NEURONS.md                  # Root repo map (preferred)
├── cortex/
│   ├── cortex-ranksentinel.bash # Cortex interactive entrypoint
│   ├── cortex.bash             # Compatibility shim (calls cortex-ranksentinel.bash)
│   ├── one-shot.sh
│   ├── snapshot.sh
│   └── cleanup_cortex_plan.sh
└── workers/ralph/
    ├── NEURONS.md              # Ralph-side repo map (bootstrap/generator)
    └── loop.sh
```
