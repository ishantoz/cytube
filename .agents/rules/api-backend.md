# API Backend Rules

Hono runs **inside the Astro Worker** under `src/backend/`.

## Runtime

- Same Cloudflare Worker as Astro (`pnpm dev` → :8787).
- Bindings: D1 `DB`, R2 `ASSETS`, KV `SESSION`/`KV`, static `STATIC`.
- Access env via `cloudflare:workers` or Hono `c.env`.

## Structure

```
src/backend/
  app.ts                      Hono app (basePath /api)
  env.ts                      Bindings type
  modules/<name>/
    index.ts                  register<Name>Module(app)
    <name>.routes.ts
    <name>.handler.ts
    <name>.service.ts
    <name>.providers.ts
    <name>.dto.ts
    <name>.schema.ts
```

- `src/pages/api/[...path].ts` — mounts `handleApi` for `/api/*`
- `prisma/` — D1 SQL; Prisma models stay in sync with module schemas

Do **not** add a custom `src/worker.ts` dispatcher or extra Astro file routes
under `src/pages/api/`.

## Prisma / D1

- Probe model: `HealthCheck` (`health_checks`) owned by the health module.
- Client output: `src/backend/generated/prisma` (`pnpm db:generate`).
  Do not import `@prisma/client`.
- SQL migrations: `prisma/migrations/d1/`.
- Apply locally: `pnpm db:migrate`. Remote prod: `pnpm db:migrate:remote`.
  Remote preview: `pnpm db:migrate:remote:dev`.
- Prisma Studio: `pnpm db:studio` (http://localhost:5555).

## Routes

| Prefix | Methods | Notes |
| --- | --- | --- |
| `/api/health` | GET | `{ status, database, storage, kv }` — 200 or 503 |
| `/api/*` | * | unknown paths → JSON 404 `{ error: "Not found" }` |

Add new API as a module under `src/backend/modules/` and register it in
`src/backend/app.ts`.

## Workers best practices

- Access bindings via `c.env` — never hardcode credentials.
- Run `wrangler types` after config changes.
- D1 does not support transactions — design accordingly.

## Do not

- Import Node-only servers (`@hono/node-server`) in Worker code
- Put secrets in `wrangler.jsonc` vars
- Reintroduce users/channels/playlist/chat until a spec asks for them
