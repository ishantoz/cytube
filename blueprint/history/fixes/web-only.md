# Fix: Web only — drop the desktop window

**Type:** Fix
**Status:** completed
**Updated:** 2026-10-02
**Archived:** 2026-10-02 (`blueprint/history/fixes/web-only.md`)
**Branch:** `fix/web-only`

## The problem

`uv run cytube` opens a native pywebview window on the portal. The app should
only be the local website. Users open `http://127.0.0.1:8000` in their own
browser. There should be no standalone window and no auto-opened browser.

## The fix

Remove `app/desktop.py`, the `cytube` script, and the `pywebview` dependency.
Keep FastAPI + uvicorn as the only way to run the UI.

Do not replace the window with `webbrowser.open` or another launcher.

## Scope / owned paths

**May change:**

- `app/desktop.py` (delete)
- `pyproject.toml`
- `uv.lock`
- `README.md`
- `AGENTS.md`
- `.agents/rules/project-architecture.md`
- `.agents/rules/package-manager.md`
- `blueprint/context/coding-standards.md`
- `blueprint/context/project-overview.md`
- `blueprint/context/session-handoff.md`

**Do not:**

- Change inspect, jobs, or page behavior
- Add a browser auto-opener
- Uncheck or rewrite archived feature 7 history
- Edit `.env` or add a test framework

## Approved decisions

Approved by `/implement` on 2026-09-29:

- Run command stays `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
- Bind stays `127.0.0.1:8000`
- No `uv run cytube`

## Open questions

None.

## Engineering review

| Dimension | Assessment |
| --- | --- |
| Contracts / module owner | Delete `app/desktop.py` only. `web` / `logic` / `backend` stay. |
| Reuse | N/A — removal, no new abstraction. |
| Scale / data | N/A — no job or schema change. |
| Compatibility / recovery | `uv run cytube` stops existing. Web URL and `/api` stay. Rollback = restore desktop module. |
| Testing | No test runner. Baseline + curl `/youtube` + confirm `cytube` script is gone. |

## Build steps

- [x] **Step 1 — Remove the window launcher**
  Delete `app/desktop.py`. Drop `pywebview` and `[project.scripts] cytube`. Update docs so the only launch path is uvicorn.
  *Done when:* `uv run cytube` is not a command; `GET http://127.0.0.1:8000/youtube` is still HTML 200 via uvicorn; `./.agents/check-baseline.sh` exits 0; README/AGENTS do not tell people to open a desktop window.

## Verification

1. `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` then `GET /youtube` → 200 HTML
2. Failure: `POST /api/not-a-platform/inspect` → 404 JSON
3. `uv run cytube` fails (no such script)

## Context manifest

- `app/desktop.py`
- `pyproject.toml`
- `README.md`
- `AGENTS.md`
- `blueprint/context/coding-standards.md`
- `.agents/rules/project-architecture.md`

## Execution ledger

- 2026-09-29: spec written via `/fix`. Implementation blocked on approval.
- 2026-09-29: Step 1 — deleted `app/desktop.py`, dropped `pywebview` and the `cytube` script. Docs point at uvicorn only.
- 2026-10-02: `/complete` rechecked baseline, `uv run cytube` exit 2, `GET /youtube` 200, unknown-platform inspect 404. Unrelated `run.js` (API key) was removed and is not part of this fix.

## Verification evidence

- `uv run cytube` → exit 2, `Failed to spawn: cytube` / `No such file or directory`
- Web `GET /youtube` via `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` → HTTP 200 `<!DOCTYPE html>`
- API `POST /api/not-a-platform/inspect` → HTTP 404 `{"error":"Unknown platform."}`
- `./.agents/check-baseline.sh` exit 0 (`py 0/0`, `eslint 0/0`) on 2026-10-02

## Exact next action

Archived. Next lifecycle: `/feature`, `/fix`, or `/rollback`.
