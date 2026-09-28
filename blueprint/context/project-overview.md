# CyTube Project Overview

> Generated from `blueprint/project-plan.md` and `blueprint/build-plan.md`.
> Regenerated 2026-09-29 for the local desktop shell.

Plan source fingerprint: cytube-2026-09-29-desktop-shell

## Purpose and users

Public-URL download portal. Users paste a public YouTube, Instagram, Facebook,
TikTok, Dailymotion, or Bilibili link, list formats, and download
video+audio / video only / audio only. Private or login-walled posts are out
of scope.

Local operators can launch a desktop shell that starts the same daemon, shows
the portal in a window, and keeps the web UI at `http://127.0.0.1:8000`.

## Default scope

Single Python package at the repo root:

- UI: `app/web/templates/` + `app/web/static/app.js`
- Pages: `app/web/routes.py`
- API: `app/backend/` inspect + job JSON under `/api`
- Extract / jobs: `app/logic/`
- Desktop: `app/desktop.py` (pywebview + uvicorn subprocess)
- Agent workflow: `blueprint/`, `.agents/`

## Stack

**Today:** FastAPI + Jinja2 + Flowbite/Tailwind CDN, uv, uvicorn `:8000`.
yt-dlp with curl-cffi Firefox impersonation where needed.

**Desktop:** pywebview window on the existing pages; same `app/` package;
`uv run cytube`.

## Architecture

```
http://127.0.0.1:8000/           307 → /youtube
/{platform}                      inspect form (HTML)
POST /api/{platform}/inspect     JSON formats
POST /api/{platform}/jobs        start download
GET  /api/jobs/{id}/events       SSE
GET  /api/jobs/{id}/file         stream + delete
POST /api/jobs/{id}/cancel       stop job
desktop `uv run cytube`          start/reuse daemon + native window
```

## Data model

No database. Jobs are in-memory with a temp directory per download.

## Features

Shipped: public multi-platform inspect + concurrent downloads with
confirm-to-cancel and a bottom-right progress stack.

Shipped: **7** local desktop shell (daemon + window + exposed local URL).

Later (own specs): rooms, chat, playlist, auth, WebSocket, OPFS, leftover
Worker items 6b–6d.

## UI / UX

Light published-site header/footer. Platform nav. Download cards stack at
the bottom right. The desktop window is that same portal; the window title
includes the local URL.

## Deployment

- Dev server: `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
- Desktop: `uv run cytube` — bind `127.0.0.1:8000` or reuse if already up;
  quit stops a daemon this process started
- Not a Cloudflare Worker

## Engineering invariants

- uv; gate `./.agents/check-baseline.sh`
- No framework scaffolder
- Public hosts only; localhost bind for the daemon
- Pylance uses `.venv` (`pyrightconfig.json`)

## Lazy context routing

- Architecture: `.agents/rules/project-architecture.md`
- Web: `.agents/rules/web-frontend.md`
- API: `.agents/rules/api-backend.md`
- Browser: `.agents/rules/browser-evidence.md`
- Lifecycle: `.agents/rules/agent-workflow.md`
