# CyTube Project Overview

> Generated from `blueprint/project-plan.md` and `blueprint/build-plan.md`.
> Regenerated 2026-09-01 after 6a archive and prototype lock.

Plan source fingerprint: cytube-2026-09-01-proto

## Purpose and users

Synchronized video rooms. Viewers join channels, watch together, chat, and
share playlists. Channel owners manage rooms and the queue. Guests are future.

## Default scope

Single pnpm package at the repo root:

- UI: `src/pages/` (Astro stub until 6b)
- API: `src/backend/` modules, mounted at `/api` via Astro catch-all
- Schema: `prisma/schema.prisma` — `HealthCheck` probe table
- Look: `prototypes/theme.css` + `home.html` / `room.html`
- Agent workflow: `blueprint/`, `.agents/`

## Stack

**Today:** one Cloudflare Worker — Astro 7 SSR + `@astrojs/cloudflare` 14,
Hono at `/api`, D1 (`HealthCheck`), KV (`SESSION` + `KV`), R2 `ASSETS`.

## Architecture

```
cytube.ishanto.com/              production pages
cytube.ishanto.com/api/*         Hono
cytube-dev.ishanto.com/          `--env dev` (own D1/R2/KV)
GET /api/health                  `{ status, database, storage, kv }`
```

Production custom domain is `cytube.ishanto.com`. Preview Worker
`cytube-dev` uses `cytube-dev.ishanto.com` with separate D1 `cytube-dev`,
R2 `cytube-dev-assets`, and KV namespaces.

## Data model

### HealthCheck

- `kind` (string, id) — probe name (`database` / `storage` / `kv`)
- `checkedAt` (string) — last successful probe time
- table `health_checks`

No users/channels/playlist/chat until a later feature adds them.

## Features

Shipped: Blueprint loop, 6a combined Worker (Astro + Hono health).

1. **6. Same-origin Astro** — 6a done; next leaf is **6b** UI shell.
2. **6b. Astro UI** — port `prototypes/theme.css`, build pages from mockups.
3. **6c. KV sessions** — `SESSION` + a real `KV` read/write.
4. **6d. Domain cutover** — `cytube.ishanto.com`.
5. **Chat / playlist / playback / auth / WebSocket / OPFS** — later.

## UI / UX

Locked in `prototypes/`. Dark media-room: player primary, chat and playlist
secondary. Accent rose `#e11d48` for live/now-playing.

- `/` — channel directory (`prototypes/home.html`)
- `/r/...` (or equivalent) — watch room (`prototypes/room.html`)
- `/api/health` — Hono health

## Deployment

Cloudflare Workers, Wrangler 4. Production: D1 `cytube`, R2 `cytube-assets`.
Preview (`--env dev`): D1 `cytube-dev`, R2 `cytube-dev-assets`. Health:
`GET /api/health`. Dev: `pnpm dev` (workerd :8787). No test framework.

## Engineering invariants

- pnpm 11; gate `./.agents/check-baseline.sh`
- No framework scaffolder (`create-cloudflare` / `create astro`)
- Bindings: `import { env } from "cloudflare:workers"`
- Hono only through Astro `/api` catch-all
- Prisma client: `pnpm db:generate` → `src/backend/generated/prisma`
- Real-time and OPFS need their own specs

## Open questions / gaps

- `cytube.ishanto.com` vs leftover `api.cytube.ishanto.com` DNS: production
  Worker now targets `cytube.ishanto.com`; preview is `cytube-dev.ishanto.com`.
- Auth/WebSocket/OPFS/tests still open in the project plan.

## Lazy context routing

- Architecture: `.agents/rules/project-architecture.md`
- Web: `.agents/rules/web-frontend.md`
- API: `.agents/rules/api-backend.md`
- Browser: `.agents/rules/browser-evidence.md`
- Lifecycle: `.agents/rules/agent-workflow.md`
