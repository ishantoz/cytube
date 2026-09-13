# API Agent

Use for Hono work mounted under Astro `/api`.

Read:

- `AGENTS.md`
- `.agents/rules/api-backend.md`
- `.agents/rules/project-architecture.md`

Operating rules:

- App is `src/backend/app.ts`. Features live in `src/backend/modules/`.
- Mount is `src/pages/api/[...path].ts`.
- Verify with curl against `http://localhost:8787/api/...` and
  `./.agents/check-baseline.sh`.
