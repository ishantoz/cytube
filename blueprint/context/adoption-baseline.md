# Adoption Baseline

Recorded 2026-09-01 at Blueprint onboarding onto the CyTube monorepo.
Updated 2026-09-01 after collapsing to a single root package.

The gate is a *delta* gate: no new errors against the numbers below.

## Static checks

| Check | Command | Result |
| --- | --- | --- |
| Typecheck | `pnpm typecheck` | **0 errors** |
| Build | `pnpm build` | passes |
| Tests | none | no test framework |

Per-file counts are in `blueprint/.state/tsc-baseline.txt` and
`blueprint/.state/eslint-baseline.txt`.

## The delta gate

```bash
./.agents/check-baseline.sh
```

Runs root typecheck, compares per-file error counts against the recorded
baseline, and fails when any file gains errors.

Re-recording (`./.agents/check-baseline.sh --write`) requires explicit user
approval.
