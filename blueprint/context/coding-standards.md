# CyTube Coding Standards

These standards describe the current repository. Apply them proportionately to
the active scope and follow nearby code where it is more specific.

## Scope and commands

- **App:** FastAPI (`app/main.py` composes `app/web`, `app/logic`, `app/backend`).
- Use **uv** only. `uv.lock` is authoritative.
- Dev: `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`.
- Regression gate: `./.agents/check-baseline.sh`
- Do not edit `.env` or commit secret values.
- Point the IDE at `.venv` (`pyrightconfig.json` / `[tool.pyright]`).

## Python

- 3.12 (`requires-python` / `.python-version`).
- Prefer inference for locals; explicit types for exported contracts.
- Do not import `@prisma/client` or Cloudflare Worker APIs.

## Web architecture

- Jinja in `app/web/templates/`. Inspect and downloads in `app/web/static/app.js` via `/api`.
- Concurrent bottom-right stack; confirm before cancel.

## API architecture

- FastAPI composed in `app/main.py`. HTML in `app/web`. Domain in `app/logic`. JSON HTTP in `app/backend` at `/api`.
- Register `/api` routers before `GET /{platform}`.

## Data and API

- Never invent endpoints. Current contract is JSON inspect, jobs, events, file,
  cancel, and HTML platform pages.
- Return consistent JSON from `/api` inspect and job endpoints.

## UI

- Light published-site look; semantic HTML; labeled inputs.

## Reuse and modularity

- Search existing extract/job helpers before adding new ones.
- Prefer reuse → extend → new abstraction.

## Verification

No test framework yet. Do not claim tests were run.

- `./.agents/check-baseline.sh` on every step (no new errors)
- Manual evidence: app, route/endpoint, observation, one failure path
- Re-recording the baseline needs explicit user approval

## Errors and security

- Validate platform, URL host, and format id.
- Do not accept cookies or secrets in the UI.
- Delete temp files after stream or cancel.
