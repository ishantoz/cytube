# Feature 7: Local desktop shell

**Type:** Feature
**Status:** completed
**Updated:** 2026-09-29
**From build-plan:** 7
**Archived:** 2026-09-29 (`blueprint/history/features/7-local-desktop-shell.md`)
**Branch:** `feature/local-desktop-shell`

## Goal

Launching one desktop command starts (or reuses) the existing FastAPI daemon
on `127.0.0.1:8000`, opens a native window on the current portal pages, and
shows the local web URL so a browser can use the same app.

## Approved decisions

- Window loads `http://127.0.0.1:8000/youtube`.
- Daemon: `127.0.0.1:8000`, no reload in the desktop child.
- Reuse an already-up portal; do not kill it on quit.
- If this process started the child, quit stops the child.
- Window title includes `http://127.0.0.1:8000`.
- Start/wait failure shows an HTML error window.
- Entry: `uv run cytube`.

## Build steps

- [x] **Step 1 — Launcher** — `app/desktop.py`, pywebview, `uv run cytube`
- [x] **Step 2 — Docs** — AGENTS, architecture, package-manager, coding-standards

## Verification evidence

- `ensure_portal` with free port → `GET /youtube` HTTP 200 HTML; child then stopped
- Reuse: second `ensure_portal` returned `child is None`
- Blocked port (raw socket on 8000) → `PortalError` in ~2s
- `POST /api/not-a-platform/inspect` → 404 `{"error":"Unknown platform."}`
- `uv run cytube` printed `CyTube web UI: http://127.0.0.1:8000`; curl `/youtube` 200; `/instagram` 200; quit stopped the child (`./.agents/check-baseline.sh` exit 0, `py 0/0`)

## Contracts

| Surface | Contract |
| --- | --- |
| CLI | `uv run cytube` |
| URL | `http://127.0.0.1:8000` |
| Child | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` |

## Exact next action

Archived. Next: `/feature`, `/fix`, or `/rollback`.
