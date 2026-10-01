# CyTube Project Overview

> Generated from `blueprint/project-plan.md` and `blueprint/build-plan.md`.
> Regenerated 2026-09-29 after dropping the desktop window. The UI is the
> local website only.

Plan source fingerprint: cytube-2026-09-29-web-only

## Purpose and users

Public-URL download portal. Users paste a public YouTube, Instagram, Facebook,
TikTok, Dailymotion, or Bilibili link, list formats, and download
video+audio / video only / audio only. Private or login-walled posts are out
of scope. Open the local site in a browser. There is no desktop window.

## Default scope

Single Python package at the repo root:

- UI: `app/web/templates/` + `app/web/static/app.js`
- Pages: `app/web/routes.py`
- API: `app/backend/` inspect + job JSON under `/api`
- Extract / jobs: `app/logic/`
- Agent workflow: `blueprint/`, `.agents/`

## Stack

**Today:** FastAPI + Jinja2 + Flowbite/Tailwind CDN, uv, uvicorn `:8000`.
yt-dlp with curl-cffi Firefox impersonation where needed. The UI is the
browser at `http://127.0.0.1:8000`.

## Architecture

```
http://127.0.0.1:8000/           307 → /youtube
/{platform}                      inspect form (HTML)
POST /api/{platform}/inspect     JSON formats
POST /api/{platform}/jobs        start download
GET  /api/jobs/{id}/events       SSE
GET  /api/jobs/{id}/file         stream + delete
POST /api/jobs/{id}/cancel       stop job
```

## Data model

No database. Jobs are in-memory with a temp directory per download.

## Features

Shipped: public multi-platform inspect + concurrent downloads with
confirm-to-cancel and a bottom-right progress stack.

Later (own specs): rooms, chat, playlist, auth, WebSocket, OPFS, leftover
Worker items 6b–6d.

## UI / UX

Light published-site header/footer. Platform nav. Download cards stack at
the bottom right. Open it in a browser.

## Deployment

- Dev server: `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
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
