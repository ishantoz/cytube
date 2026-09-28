# Adoption Baseline

Recorded 2026-09-01 at Blueprint onboarding.
Updated 2026-09-29 for the FastAPI download portal (no TypeScript app).

The gate is a *delta* gate: no new errors against the numbers below.

## Static checks

| Check | Command | Result |
| --- | --- | --- |
| Compile + import | `uv run python -m compileall -q app` and `from app.main import app` | **0 errors** |
| Tests | none | no test framework |

Per-file counts are in `blueprint/.state/py-baseline.txt` and
`blueprint/.state/eslint-baseline.txt` (both empty when green).

## The delta gate

```bash
./.agents/check-baseline.sh
```

Compile-checks `app/` and imports `app.main`. Fails if either command fails.

Re-recording (`./.agents/check-baseline.sh --write`) requires explicit user
approval.
