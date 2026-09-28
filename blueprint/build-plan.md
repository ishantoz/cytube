# CyTube Build Plan

> Shipped capabilities and living roadmap. `/complete` updates this file when a
> feature lands.

## Shipped capability groups

1–6a are leftover Cloudflare Worker history. The live app is the FastAPI
download portal (JSON inspect/jobs under `/api`, Jinja pages).

1. **Monorepo scaffold** — retired
2. **Database** — retired (no D1 in the current app)
3. **API** — retired Hono Worker; current JSON is FastAPI `/api`
4. **Web shell** — retired Next/Astro room UI
5. **Agent loop** — Blueprint overlay (`/onboard` complete)
6a. **Root Astro Worker + Hono mount** — retired; not the current runtime

## Data models

No database. Download jobs are in-memory with a temp directory per job.

## Active roadmap

- [x] 7. Local desktop shell — launching the app starts the FastAPI daemon, opens a window on the existing portal, and shows the local web URL

## Later (former Worker / room product; not the next FastAPI slice)

- [ ] 6. Same-origin Astro on Cloudflare
  - [x] 6a. Root Astro Worker + Hono mount
  - [ ] 6b. Astro UI shell
  - [ ] 6c. KV sessions
  - [ ] 6d. Retire leftover `api.cytube.ishanto.com` if it still serves the Worker
- [ ] Interactive chat (send messages)
- [ ] Playlist management (add/remove/reorder)
- [ ] Playback sync controls
- [ ] User auth (register/login)
- [ ] WebSocket real-time layer
- [ ] OPFS evaluation (if approved)

## Engineering invariants

- uv only; `uv.lock` is authoritative
- UI talks to `/api` on the same origin
- Gate on `./.agents/check-baseline.sh` (no new errors) plus manual evidence
- No test framework yet
- Do not run framework scaffolders in this repo
