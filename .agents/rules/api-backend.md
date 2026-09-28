# API Backend Rules

`app/main.py` only composes the app. JSON HTTP lives in `app/backend/`.
Extract and jobs live in `app/logic/` (no FastAPI).

## Runtime

- `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
- No Cloudflare bindings. Do not import `cloudflare:workers`.

## Structure

```
app/
  main.py                 include /api routers then web_router
  logic/extractor.py      PLATFORMS, get_formats, ydl options
  logic/jobs.py           DownloadJob, JobStore, run_download_job
  backend/schemas.py      InspectRequest, JobRequest
  backend/routes.py       inspect, jobs, events, file, cancel
  web/routes.py           HTML pages only
```

## Routes

| Path | Methods | Owner | Notes |
| --- | --- | --- | --- |
| `/` | GET, HEAD | web | 307 to `/youtube` |
| `/{platform}` | GET | web | platform page |
| `/api/{platform}/inspect` | POST | backend | JSON `{page_url, media}` or `{error}` |
| `/api/{platform}/jobs` | POST | backend | start download job |
| `/api/jobs/{id}/events` | GET | backend | SSE progress |
| `/api/jobs/{id}/file` | GET | backend | stream then delete temp |
| `/api/jobs/{id}/cancel` | POST | backend | stop job, destroy temp |

Unknown platforms and bad format ids return JSON errors (`400`/`404` `{error}`).

## Do not

- Render Jinja from `backend/`
- Import FastAPI from `logic/`
- Restore Prisma/D1/Hono/Astro without a spec
- Accept cookie files or private/login-walled URLs
- Put secrets in source; do not edit `.env`
- Keep unprefixed job or HTML inspect aliases
