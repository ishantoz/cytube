# CyTube Build Plan

> Shipped capabilities and living roadmap. `/complete` updates this file when a
> feature lands.

## Shipped capability groups

Scaffold completed 2026-09-01. Groups 1–4 were the old Next + `web/`/`backend/`
split; they were retired when 6a collapsed the repo to one Worker.

1. **Monorepo scaffold** — retired (was pnpm workspaces, `web/` + `backend/`)
2. **Database** — Prisma 7 + D1; now a `HealthCheck` probe table only
3. **API** — Hono in the root Worker at `/api` (health only)
4. **Web shell** — retired Next channel/room UI; Astro stub at `/`
5. **Agent loop** — Blueprint overlay synced to this project (`/onboard` complete)
6a. **Root Astro Worker + Hono mount** — Astro SSR, Hono catch-all, D1+R2+KV

## Data models (Prisma)

- `HealthCheck` (`kind`, `checkedAt`) — probe table for `/api/health`

## Seed data

None. `prisma/seed.sql` is a no-op.

## Active roadmap

Look is locked in `prototypes/` (pre-build, not a `/feature` target). 6b ports
`prototypes/theme.css` on its first step.

- [ ] 6. Same-origin Astro on Cloudflare — one root app, Hono at `/api`, Workers KV
  - [x] 6a. Root Astro Worker + Hono mount — Astro SSR at repo root, Hono at `/api`, D1+R2+KV bindings
  - [ ] 6b. Astro UI shell — new pages in `src/pages` from `prototypes/` (old Next channel/room UI was removed)
  - [ ] 6c. KV sessions — Astro Sessions on `SESSION`; app `KV` used for a real read/write
  - [ ] 6d. Retire leftover `api.cytube.ishanto.com` if it still serves the Worker
- [ ] Interactive chat (send messages)
- [ ] Playlist management (add/remove/reorder)
- [ ] Playback sync controls
- [ ] User auth (register/login)
- [ ] WebSocket real-time layer
- [ ] OPFS evaluation (if approved)

## Engineering invariants

- pnpm 11 only; `pnpm-lock.yaml` is authoritative
- Prisma client: `pnpm db:generate` → `src/backend/generated/prisma`
- UI talks to `/api` on the same origin
- Gate on `./.agents/check-baseline.sh` (no new errors) plus manual evidence
- No test framework yet
- Do not run `create-cloudflare` / `create astro` in this repo
