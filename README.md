# CyTube

Synchronized video rooms — watch together, chat, and queue videos in channels.

## Stack

- **Worker** — Astro 7 SSR + Hono on Cloudflare (`/` pages, `/api/*`)
- **Tooling** — pnpm, Wrangler

## Quick start

```bash
pnpm install
pnpm db:migrate       # local D1
pnpm dev              # http://localhost:8787
pnpm db:studio        # Prisma Studio on a local D1 snapshot
```

- Origin: http://localhost:8787 (`/` HTML, `/api/health` probes D1, R2, KV)

## Deploy

```bash
pnpm db:migrate:remote:dev
pnpm deploy:dev           # cytube-dev.ishanto.com (own D1/R2/KV)
pnpm db:migrate:remote
pnpm deploy:production    # cytube.ishanto.com
```

## Commands

See `AGENTS.md` for the full command list and agent workflow.

## Agent workflow

Engineering lifecycle docs live in `blueprint/README.md`. AI agents should read
`AGENTS.md` first.
