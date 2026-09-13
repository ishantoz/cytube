# Feature: 6a Root Astro Worker + Hono mount

**From build-plan:** feature 6a
**Type:** Feature
**Status:** completed
**Branch:** none (no `.git` in this worktree)
**Updated:** 2026-09-01
**Archived:** 2026-09-01 (`blueprint/history/features/6a-root-astro-worker.md`)

## Goal

One Cloudflare Worker at the repo root: Astro SSR for `/`, Hono at `/api`
via an Astro catch-all. Domain schema, users/channels APIs, and Next UI were
removed so later features start clean. Production hostname stays
`api.cytube.ishanto.com`.

## In scope

- Root Astro 7 + `@astrojs/cloudflare` (`output: 'server'`).
- Root `wrangler.jsonc`, D1/R2/KV, production custom domain
  `api.cytube.ishanto.com`.
- Hono in `src/backend/app.ts`, mounted at `src/pages/api/[...path].ts`.
- Empty Prisma schema; no-op D1 migration.
- Stub Astro `/`.
- Single package: `web/` and `backend/` removed (user 2026-09-01).

## Out of scope

- Using KV in application code (6c).
- Custom domain `cytube.ishanto.com`.
- Restoring users/channels/playlist/chat UI or APIs.

## Approved decisions

- 2026-09-01: same-origin Astro + Hono + KV; drop `web/`+`backend/` split (parent 6).
- 2026-09-01: 6a must not bind `cytube.ishanto.com`.
- 2026-09-01: add files with `pnpm add`; no official scaffolder.
- 2026-09-01: user: strip schema/API/UI; Hono only through Astro catch-all.
- 2026-09-01: user: no CORS — same origin.
- 2026-09-01: user: `GET /api/health` probes D1, R2, and KV.

## Open questions

None.

## Engineering review

- **Contracts / module owner:** `GET /` HTML; `GET /api/health` JSON.
  Hono owner is `src/backend/`. Astro owns pages and the `/api` mount.
- **Reuse / modularity:** one Hono app; Astro file routes only dispatch.
- **Scale / data access:** no queries.
- **Migration / compatibility / recovery:** `0001_init.sql` is now a no-op.
  Remote D1 may still have old tables until a later cleanup. Rollback =
  restore previous schema/routes from history.
- **Testing matrix:** no test runner. Static gate + curl.

## Build steps

- [x] **Step 1 - Root Astro + Wrangler**
- [x] **Step 2 - Mount Hono** — originally `src/worker.ts`; replaced by Astro
  catch-all in step 4.
- [x] **Step 3 - Scripts, types, docs**
- [x] **Step 4 - Strip domain + catch-all Hono** - Remove Prisma models,
  users/channels routes, Next room UI. Hono only under `/api` via
  `[...path]`. *Done when:* `GET /` HTML; `GET /api/health` →
  `{ "status": "ok" }`; unknown `/api/does-not-exist` is JSON 404; no
  `backend/src/routes/`; `./.agents/check-baseline.sh` exits 0.

- [x] **Step 5 - Remove `web/` and `backend/`** - Single package. Prisma
  husk at `prisma/`. *Done when:* those directories are gone; `pnpm typecheck`
  and `./.agents/check-baseline.sh` exit 0.

## Files / areas

**May change:** `src/backend/`, `src/pages/`, `wrangler.jsonc`, `prisma/`,
`package.json`, AGENTS.md, rules, coding-standards, README, overview.

**Do not:** edit `.env`, deploy, bind `cytube.ishanto.com`.

## Data / contracts

| Method | Path | Shape |
| --- | --- | --- |
| GET | `/api/health` | `{ status, database, storage, kv }` (`ok`/`error`; 503 if any fail) |
| GET | `/api/*` unknown | 404 `{ error: "Not found" }` |
| GET | `/` | Astro HTML |

Bindings: `DB`, `ASSETS`, `SESSION`, `KV`.

## Static checks

- `./.agents/check-baseline.sh` — exit 0
- `pnpm astro build`

## Verification

1. Local Worker: `/` is HTML stub.
2. `curl /api/health` — `{ "status": "ok" }`.
3. `curl /api/does-not-exist` — JSON 404, not Astro HTML.
4. `curl /api/channels` — JSON 404 (route removed).

## Context manifest

- `blueprint/context/project-overview.md`
- `blueprint/context/coding-standards.md`
- `src/backend/app.ts`, `src/pages/api/[...path].ts`, `wrangler.jsonc`
- `.agents/rules/api-backend.md`
- `.agents/skills/wrangler/SKILL.md`
- `.agents/skills/workers-best-practices/SKILL.md`

## Execution ledger

- 2026-09-01: spec approved via `/implement`. No `.git`; skipped feature branch.
- 2026-09-01: Steps 1–3 — Astro Worker + original Hono dispatcher.
- 2026-09-01: Step 4 — user-directed strip: empty schema, Hono catch-all,
  UI stub. Did not deploy.
- 2026-09-01: Removed CORS middleware and `CORS_ORIGIN` vars (same origin).
- 2026-09-01: Health probes D1 (`health_checks`), R2 `ASSETS`, and `KV`.
- 2026-09-01: Health moved to `src/backend/modules/health`. Prisma client
  generates to `src/backend/generated/prisma`.
- 2026-09-01: Closed so `/prototype` and `/feature 6b` can start on a
  clean spec slot. No git commit (no repository in this worktree).

## Verification evidence

- App: combined Worker (`pnpm astro dev`) on http://localhost:8787
- GET `/` → `text/html`, `<h1>CyTube</h1>` (not JSON)
- GET `/api/health` → `{"status":"ok"}`
- Failure: GET `/api/does-not-exist` → 404 `{"error":"Not found"}` (JSON)
- GET `/api/channels` → 404 JSON (route removed)
- GET `/health` → Astro HTML 404 (Hono is only under `/api`)
- `./.agents/check-baseline.sh` → tsc 0 now 0, eslint 0 now 0
- `pnpm astro build` Complete; `pnpm typecheck` exit 0
- `web/` and `backend/` removed
- Did not deploy

## Exact next action

Archived. Next: `/prototype` then `/feature 6b`.
