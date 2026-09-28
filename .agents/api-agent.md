# API Agent

Use for FastAPI `/api` inspect and job routes, yt-dlp extract, and download jobs.

Read:

- `AGENTS.md`
- `.agents/rules/api-backend.md`
- `.agents/rules/project-architecture.md`

Operating rules:

- Compose in `app/main.py`. JSON HTTP in `app/backend/` under `/api`. Domain in `app/logic/`.
- Include `/api` routers before `GET /{platform}`.
- `logic/` must not import FastAPI.
- Verify with curl against `http://127.0.0.1:8000/...` and
  `./.agents/check-baseline.sh`.
