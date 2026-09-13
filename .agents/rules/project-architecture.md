# CyTube Architecture

Synchronized video-room app on one Cloudflare Worker: Astro pages + Hono at
`/api`. Single pnpm package at the repo root.

## Repository shape

```
cytube/
├── src/
│   ├── backend/
│   │   ├── app.ts                Hono app
│   │   └── modules/health/       first module (service, routes, …)
│   └── pages/
│       ├── index.astro          HTML stub
│       └── api/[...path].ts      catch-all Hono mount
├── prisma/                       D1 schema + migrations
├── prototypes/                  locked look (theme + mockups)
├── wrangler.jsonc
├── AGENTS.md
└── blueprint/
```

## Stack

- **App:** Astro 7 + `@astrojs/cloudflare` + Hono 4
- **DB:** Cloudflare D1 (`HealthCheck` probe table)
- **Storage:** R2 `ASSETS`, KV `SESSION` + `KV`
- **Package:** pnpm 11, one package

## Ports

| Service | Port | Command |
| --- | --- | --- |
| Combined Worker | 8787 | `pnpm dev` |

## Invariants

- Backend logic lives in `src/backend/modules/<name>/`.
- Mount Hono only through Astro `src/pages/api/[...path].ts`.
- Bindings via `import { env } from "cloudflare:workers"` / Hono `c.env`.
- Do not run `prisma generate` until a feature needs the client. Import from
  `src/backend/generated/prisma`, not `@prisma/client`.
- Real-time sync is **not built yet**. Do not add WebSocket code without a spec.

## Planned (not built)

- 6b Astro UI from `prototypes/` (do not port deleted Next UI)
- KV sessions (6c)
- Chat, playlist, playback, auth, WebSocket, OPFS

## Deployment

Cloudflare Worker `cytube-api` on `cytube.ishanto.com`. Preview Worker
`cytube-dev` on `cytube-dev.ishanto.com` (own D1/R2/KV).
