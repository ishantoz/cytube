# CyTube Project Plan

> Durable product direction. Edit deliberately; regenerate
> `context/project-overview.md` after any change here or in `build-plan.md`.

## Purpose

CyTube is a public-URL download portal. Users paste a public YouTube,
Instagram, Facebook, TikTok, Dailymotion, or Bilibili link, list formats, and
download video+audio / video only / audio only. Private or login-walled posts
are out of scope.

A local desktop shell can start the same FastAPI daemon, show the portal in a
window, and leave the web UI at `http://127.0.0.1:8000` for a browser.

Synchronized rooms, chat, playlist, and auth remain later product directions
and need their own specs. They are not the current app.

## Users

| User | Needs |
| --- | --- |
| Downloader | Paste a public link, pick a format, download to their device |
| Local operator | Run the portal on their machine via the desktop app; download in the window or in a browser at the local URL |

## Boundaries

- **This app** owns one Python package: Jinja pages, JSON `/api`, yt-dlp extract,
  temp download jobs. No login cookies.
- **Local desktop** is a thin shell around that app. It starts and stops uvicorn
  and shows the same portal. It does not add a second extract/download client.
- **Video files** are fetched from public hosts and streamed through, then the
  server temp copy is deleted. This app does not host a video library.
- The Blueprint is a workflow overlay, not an app generator. Never run a
  framework scaffolder in this repository.

## Stack (committed)

| Layer | Tech |
| --- | --- |
| App | FastAPI + Jinja2 + Flowbite/Tailwind CDN |
| JSON API | `app/backend/` at `/api` (inspect, jobs, SSE, file, cancel) |
| Domain | `app/logic/` (yt-dlp, in-memory jobs) |
| Desktop shell | pywebview window + spawned `uvicorn app.main:app` (same `app/` package, uv) |
| Package | uv, **single package at repo root** |

## Durable engineering direction

- Compose in `app/main.py`. HTML in `app/web`. JSON in `app/backend`. Domain in
  `app/logic` (no FastAPI).
- Desktop code must not call yt-dlp or duplicate inspect/job HTTP.
- Bind the daemon to `127.0.0.1` only unless a later spec says otherwise.
- Public hosts only. Pylance uses `.venv`.

## Phased roadmap (high level)

1. **FastAPI portal** — shipped: inspect + concurrent downloads
2. **Local desktop shell** — daemon + window on the existing portal + exposed URL
3. **Later** — rooms, chat, playlist, auth, WebSocket, OPFS; each needs a spec

## Deployment

- Local uvicorn: `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
- Local desktop: launch binds `127.0.0.1:8000` (or reuses it if already up),
  shows that URL, quitting stops a daemon this process started.
- Not a Cloudflare Worker.

## Open direction questions

Route these to the user; do not resolve them inside a feature task:

- Whether to adopt a test framework, and when
- Installer / tray / LAN bind (`0.0.0.0`) for the desktop shell
- Whether synchronized rooms return, and on what stack
