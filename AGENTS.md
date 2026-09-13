# CyTube Agent Guide

This is the single cross-tool entrypoint for AI work in this repository. Claude
imports it through `CLAUDE.md`; Codex, Cursor, OpenCode, and other tools should
read it directly.

## Scope

- **CyTube** is a synchronized video-room app: users join channels, watch videos
  together in sync, chat, and manage playlists.
- **App:** one Cloudflare Worker at the repo root (Astro 7 SSR + Hono at
  `/api`). Single pnpm package.
- **Database** — Cloudflare D1. Probe model `HealthCheck` for `/api/health`.
  Do not import `@prisma/client`; use `src/backend/generated/prisma`.
- The **AI Blueprint** is a workflow overlay, not an app generator. Never run a
  framework scaffolder inside this repository.

## Minimal session bootstrap

Read these first, in order:

1. `blueprint/context/project-overview.md`
2. `blueprint/context/current-feature.md`
3. `blueprint/context/session-handoff.md`
4. Git status and the active branch

Then load only files named in the active work item's `Context manifest`. Do not
scan all project knowledge or depend on previous chat history. Durable decisions
and progress belong in Blueprint files.

## Focused context routing

- Architecture: `.agents/rules/project-architecture.md`
- Web frontend: `.agents/rules/web-frontend.md`, `.agents/web-agent.md`
- API backend: `.agents/rules/api-backend.md`, `.agents/api-agent.md`
- Browser evidence: `.agents/rules/browser-evidence.md`
- Lifecycle: `.agents/rules/agent-workflow.md`,
  `.agents/rules/knowledgebase-maintenance.md`
- Package manager: `.agents/rules/package-manager.md`

`.agents/rules/*.md` and `.agents/skills/` are canonical. `.cursor` and
`.claude` are adapters, not independent sources. Both hosts get the same
enforcement: one hook script (`.agents/hooks/no-adhoc-browser.py`), one
Playwright launcher (`.agents/playwright-mcp.sh`), and `.claude/skills` /
`.cursor/skills` symlinked to `.agents/skills`.

## Commands

- Package manager: **pnpm 11** only (`pnpm-lock.yaml` is authoritative)
- Install: `pnpm install`
- Combined Worker (Astro + Hono): `pnpm dev` (workerd :8787)
- Local D1: `pnpm db:migrate` / remote prod: `pnpm db:migrate:remote` / remote dev: `pnpm db:migrate:remote:dev`
- Prisma Studio (local D1 snapshot): `pnpm db:studio`
- Deploy: `pnpm deploy` (local bindings) / `pnpm deploy:dev` (`cytube-dev.ishanto.com`) / `pnpm deploy:production` (`cytube.ishanto.com`)
- Typecheck: `pnpm typecheck`
- **Regression gate: `./.agents/check-baseline.sh`**
- Build: `pnpm build` / `pnpm build:app` (both run `astro build`)
- Do not edit `.env` files.

## Architecture invariants

### Combined Worker

- Astro pages in `src/pages/` stay thin. Hono is `src/backend/app.ts`.
- Backend features are modules under `src/backend/modules/`.
- Mount Hono with Astro catch-all `src/pages/api/[...path].ts`.
- Bindings via root `wrangler.jsonc` (D1, R2 `ASSETS`, KV `SESSION`/`KV`,
  static `STATIC`). Production hostname is `cytube.ishanto.com`. Preview is
  `cytube-dev.ishanto.com` (`--env dev`).

### Prisma husk (`prisma/`)

- Probe model `HealthCheck` for `/api/health`. D1 `0001_init.sql` is a no-op;
  `0002_health_checks.sql` creates the table.
- Do not restore users/channels/playlist/chat until a spec asks.
- Prisma client: `pnpm db:generate` → `src/backend/generated/prisma`.

### Cross-cutting

- Real-time sync (WebSocket) is planned but not yet implemented. Do not add a
  second HTTP client stack or duplicate state libraries without a spec decision.
- OPFS client storage is a future direction; do not implement without an
  approved spec.

## Engineering quality gate

Every non-trivial spec must assess module ownership, reuse, scale,
compatibility, recovery, and verifiability. Apply only relevant checks.

## Verification

**No test framework yet.** Do not claim tests were run unless a real test command
exists.

The gate is **no new errors**:

```bash
./.agents/check-baseline.sh    # must exit 0
```

It runs root typecheck and compares per-file error counts against
`blueprint/context/adoption-baseline.md`.

Every behavior-changing step also records manual evidence:

- which app (web / API) and which route or endpoint
- what you observed in the browser or via curl
- at least one failure path: 404, empty list, or validation error

## Lifecycle

Use one file-backed work item at a time:

`status -> feature/fix -> approve spec -> implement -> check/audit -> review -> complete`

- `feature` and `fix` write `blueprint/context/current-feature.md`.
- Spec approval authorizes bounded implementation. Stop for scope drift,
  unresolved product choices, destructive actions, unrelated dirty-file conflicts,
  failed required checks, or open P0/P1 findings.
- After each completed step, update the active spec, evidence, and
  `session-handoff.md`.
- `complete` alone archives work and proposes commit/merge. Commit, merge, push,
  and destructive operations require approvals in
  `blueprint/context/ai-interaction.md`.

Canonical skills live under `.agents/skills/<name>/SKILL.md`.

**Next planned step:** `/feature` 6b (Astro UI from `prototypes/`; do not
port the removed Next channel/room UI).

## Browser evidence

Use the configured `playwright` MCP server for UI inspection. Never write a
throwaway script that launches a browser; `.agents/hooks/no-adhoc-browser.py`
blocks it. Details in `.agents/rules/browser-evidence.md`.

## Safety

- Check git status before edits and preserve unrelated user work.
- Do not edit `.env` or secrets.
- Do not use destructive git commands without explicit approval.
- Every implementation includes a docs/rules impact check.
