# CyTube Project Plan

> Durable product direction. Edit deliberately; regenerate
> `context/project-overview.md` after any change here or in `build-plan.md`.

## Purpose

CyTube is a modern synchronized video-room application. Users join public or
private channels, watch videos together in sync, chat in real time, and build
shared playlists — inspired by [CyTube](https://github.com/calzoneman/sync) but
rebuilt with a current stack.

## Users

| User | Needs |
| --- | --- |
| Viewer | Join a channel, watch synced video, chat |
| Channel owner | Create/manage channels, control playback queue |
| Guest | Browse public channels without an account (future) |

## Boundaries

- **This app** owns the UI and API in **one Cloudflare Worker**. D1 is the
  system of record. Workers KV holds sessions (and later cache). R2 is reserved
  for file storage.
- **Video hosting** is external (YouTube, Vimeo, etc.). This app embeds and
  syncs playback state; it does not transcode or host video files.
- **Real-time sync** (WebSocket) is planned but not yet built. Current scaffold
  is REST + server-rendered pages.
- **OPFS** (Origin Private File System) for client-side caching/offline is a
  future direction under evaluation — see open questions. Do not implement
  without an approved spec.
- The Blueprint is a workflow overlay, not an app generator. Never run a
  framework scaffolder in this repository. Add Astro/Wrangler files by hand.

## Stack (committed)

Target after feature 6. The `web/` + `backend/` split is already gone.

| Layer | Tech |
| --- | --- |
| App | Astro 6/7 (`output: 'server'`) + `@astrojs/cloudflare` v13+ |
| API | Hono 4, mounted on the same Worker at `/api` |
| ORM | Prisma 7 (`prisma-client`, `runtime = "workerd"`) when models exist |
| Database | Cloudflare D1 (SQLite) |
| Sessions / cache | Workers KV (`SESSION` + `KV`) |
| Files | R2 binding `ASSETS` |
| Package | pnpm 11, **single package at repo root** |

## Durable engineering direction

- Thin Astro pages in `src/pages/`; reusable UI in `src/components/`.
- Hono in `src/backend/app.ts`, mounted via Astro `/api` catch-all. Same-origin
  fetches to `/api/*`.
- Bindings via `import { env } from "cloudflare:workers"` (not
  `Astro.locals.runtime`).
- Prisma schema is the source of truth. D1 SQL in `prisma/migrations/d1/`.
- UI theme is locked in `prototypes/theme.css`. 6b ports it into the app
  stylesheet before building pages against the mockups.

## Phased roadmap (high level)

1. **Same-origin Astro Worker** — collapse Next.js + Hono split; KV; one domain
2. **Prototype** — done (`prototypes/theme.css`, `home.html`, `room.html`)
3. **Core room UX** — 6b ports the theme; then player, playlist, chat
4. **Auth** — user registration, sessions (KV), channel ownership
5. **Real-time** — WebSocket for playback sync and live chat
6. **OPFS / offline** — evaluate and spec client-side storage if warranted

## Deployment

- Cloudflare Workers via Wrangler 4.
- Production hostname: `cytube.ishanto.com` (pages + `/api`).
- Preview: `cytube-dev.ishanto.com` (`pnpm deploy:dev`; own D1/R2/KV).
- Health: `GET /api/health`.
- Local: `astro dev` / `wrangler dev` on the Cloudflare workerd runtime.

## Open direction questions

Route these to the user; do not resolve them inside a feature task:

- WebSocket library choice (native WS, Socket.io, PartyKit, Durable Objects)
- Auth strategy beyond Astro Sessions + KV (OAuth vs password)
- Whether OPFS is needed for v1 or deferred
- Guest/anonymous access policy
- Whether to adopt a test framework, and when
- Exact cutover of leftover `api.cytube.ishanto.com` DNS if it still points
  at the old Worker
