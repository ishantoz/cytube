# CyTube Architecture

Public-URL download portal: FastAPI + Jinja2, one Python package at
the repo root.

## Repository shape

```
cytube/
├── app/
│   ├── main.py              compose FastAPI, static, routers
│   ├── web/                 templates, static, HTML pages
│   ├── logic/               extract + jobs (no FastAPI)
│   └── backend/             JSON inspect, jobs, SSE, file, cancel
├── pyproject.toml
├── uv.lock
├── AGENTS.md
└── blueprint/
```

## Stack

- **App:** FastAPI, Jinja2, Flowbite/Tailwind CDN
- **Client:** `app/web/static/app.js` consumes `/api`
- **Extract/download:** yt-dlp (+ curl-cffi Firefox impersonate for some hosts)
- **Package:** uv  (`uv.lock`)

## Ports

| Service | Port | Command |
| --- | --- | --- |
| Download portal | 8000 | `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` |

## Invariants

- `logic/` does not import FastAPI. `web/` does not call yt-dlp. `backend/` does not render Jinja.
- HTML in `app/web/templates/`, behavior in `app/web/static/app.js`.
- Platform allowlists live in `app/logic/extractor.py`.
- Job lifecycle lives in `app/logic/jobs.py`.
- Include `/api` routers before `GET /{platform}`.
- Public URLs only — no cookie/login-walled extraction without a spec.
- Bind is `127.0.0.1` only unless a later spec says otherwise. The UI is the browser at that URL. No native window launcher.

## Planned (not built)

- Synchronized video rooms, chat, playlist, auth, WebSocket, OPFS — later,
  behind their own specs. Do not mix that architecture into this portal
  without an approved spec.

## Deployment

Local uvicorn on :8000. No Wrangler deploy for this app.
