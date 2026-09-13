---
name: cytube
description: Route CyTube monorepo work to the smallest relevant canonical rules while preserving web/API boundaries, Prisma conventions, and context-budget constraints.
---

# cytube - focused project routing

Start from `AGENTS.md` and the active Context manifest.

- Web UI, pages, components, API client: `web-frontend.md`, `web-agent.md`
- Hono routes, Prisma, migrations: `api-backend.md`, `api-agent.md`
- Architecture and monorepo shape: `project-architecture.md`
- Browser/UI evidence: `browser-evidence.md`
- Lifecycle and verification: `agent-workflow.md`

Do not load every file in a category. Pick the smallest set that answers the
active scope and record it in `current-feature.md`.

Always preserve:

- Hono in `src/backend/app.ts`, mounted only via Astro `/api` catch-all
- New API as `src/backend/modules/<name>/`
- Prisma: `HealthCheck` probe only; no users/channels until a spec
- Client import: `src/backend/generated/prisma`, not `@prisma/client`
- pnpm 11 commands
- `./.agents/check-baseline.sh` as the regression gate

This repo has no test framework yet. The gate is `./.agents/check-baseline.sh`
(no new tsc/eslint errors), `pnpm build` when build-sensitive, plus recorded
manual verification. See `agent-workflow.md` and
`blueprint/context/adoption-baseline.md`.

Look is locked in `prototypes/`. `/feature 6b` ports `theme.css` first.
