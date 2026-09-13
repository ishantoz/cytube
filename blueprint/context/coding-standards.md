# CyTube Coding Standards

These standards describe the current repository. Apply them proportionately to
the active scope and follow nearby code where it is more specific.

## Scope and commands

- **App:** Astro + Hono (`src/pages`, `src/backend/`, `wrangler.jsonc`).
- **Hono mount:** `src/pages/api/[...path].ts` only.
- Use **pnpm 11** only. `pnpm-lock.yaml` is authoritative.
- Dev: `pnpm dev` (Astro + Hono on :8787).
- Regression gate: `./.agents/check-baseline.sh`
- Build: `pnpm build` / `pnpm build:app` (Astro)
- Do not edit `.env` or commit secret values.

## TypeScript

- Strict mode. Root `tsconfig.json` covers `src/`.
- Prefer inference for locals; explicit types for exported contracts.

## Web architecture

- Astro pages in `src/pages/`. No Next channel list or `/r/[name]` unless a
  spec restores them.
- Theme tokens live in `prototypes/theme.css` until 6b ports them.

## API architecture

- Hono in `src/backend/app.ts` with `basePath("/api")`.
- Add endpoints as modules under `src/backend/modules/`, not as extra
  Astro file routes under `src/pages/api/`.
- Bindings: `c.env` / `cloudflare:workers`. No Prisma until models exist.

## Data and API

- Never invent endpoints or schema fields. Current contract is
  `GET /api/health` → `{ status, database, storage, kv }` (`ok` or
  `error`; HTTP 503 if any check fails) and JSON 404 for unknown `/api/*`.
- Return consistent JSON shapes from API routes.

## UI

- Dark media-room; match `prototypes/home.html` and `prototypes/room.html`.
- Use semantic HTML; accessible form labels and focus states.

## Reuse and modularity

- Search existing components and routes before adding new ones.
- Prefer reuse → extend → new abstraction.

## Verification

No test framework yet. Do not claim tests were run.

- `./.agents/check-baseline.sh` on every step (no new errors)
- `pnpm build` when build-sensitive
- Manual evidence: app, route/endpoint, observation, one failure path
- Re-recording the baseline needs explicit user approval

## Errors and security

- Return user-safe API errors. No stack traces in responses.
- Never commit, log, or echo secrets or `.env` values.

## Writing

- Concise, scannable markdown.
- Use project paths, identifiers, and commands exactly.

## Code quality

- Remove unused code and imports.
- Preserve existing behavior outside the approved scope.
- Every implementation ends with a docs/rules impact check.
