# Fix: JSON inspect API, then consume it from the page

**Type:** Fix
**Status:** completed
**Updated:** 2026-09-29
**Archived:** 2026-09-29 (`blueprint/history/fixes/json-inspect-api.md`)
**Branch:** `fix/json-inspect-api` (from dirty `main`; includes the uncommitted
FastAPI `web` / `logic` / `backend` split — user 2026-09-29)

Replaces the previous work item in this file. The `web` / `logic` / `backend`
split is already in the tree; this fix does not undo it.

## The problem

Inspect is HTMX posting to `POST /{platform}/inspect` and swapping an HTML
fragment. That mixes presentation into the only inspect “API”. Jobs are already
JSON, but inspect cannot be reused by another client without scraping HTML.

## The fix

Add a JSON inspect endpoint in `app/backend`, then have the platform page
`fetch` it and render the format table in `app/web/static/app.js`. Remove the
HTMX inspect post and the Jinja results/error partials used only for that swap.

Job HTTP already returns JSON. Mount those routes under `/api` as well so all
JSON lives in one prefix. Keep unprefixed job paths as aliases in step 1 so
downloads keep working, then point the client at `/api` and drop the aliases.

## Scope / owned paths

**May change:**

- `app/backend/schemas.py`
- `app/backend/routes.py`
- `app/web/routes.py`
- `app/web/templates/platform.html`
- `app/web/templates/base.html` (drop unused HTMX if nothing else uses it)
- `app/web/templates/partials/results.html` (delete once JS renders)
- `app/web/templates/partials/error.html` (keep if unknown-platform HTML still needs it)
- `app/web/static/app.js`
- `app/main.py` (router prefix only if needed)
- Agent docs: `AGENTS.md`, `.agents/rules/api-backend.md`,
  `.agents/rules/web-frontend.md`, `blueprint/context/project-overview.md`,
  `blueprint/context/coding-standards.md`, `blueprint/context/session-handoff.md`

**Do not:**

- Change yt-dlp extract/job domain logic beyond calling it from the new route
- Add a test framework
- Edit `.env` or secrets
- Restore Cloudflare Worker / HTMX inspect after this ships

## Approved decisions

- Inspect JSON: `POST /api/{platform}/inspect` with body `{ "url": "..." }`.
- Success: `200` `{ "page_url", "media" }` (`media` is today’s `get_formats` shape).
- Failure: `400`/`404` `{ "error": "..." }` (empty URL, bad host, extract error, unknown platform).
- Job JSON moves to `/api/{platform}/jobs` and `/api/jobs/{id}/events|file|cancel`.
- Platform pages stay `GET /{platform}` (HTML). No HTMX for inspect.

## Open questions

None. Approval locks the contracts above.

## Engineering review

| Dimension | Assessment |
| --- | --- |
| Contracts / module owner | New JSON inspect owned by `backend`. Web only consumes. Jobs already JSON; prefix `/api`. |
| Reuse / modularity | `get_formats` stays in `logic`. HTML table rendering moves to JS so API stays payload-only. |
| Scale / data | Same in-memory jobs; inspect still one yt-dlp extract per request. |
| Compatibility / recovery | Step 1 dual-mounts job routes. Step 2 removes HTML inspect and unprefixed job aliases. Rollback = restore HTMX inspect + old job paths. |
| Testing matrix | No test runner. Static gate + curl JSON + one browser/page check. |

## Build steps

- [x] **Step 1 — JSON API**
  Add inspect JSON under `/api`. Mount existing job handlers at `/api/...` and keep current unprefixed job URLs as aliases.
  *Done when:* `curl -s -X POST http://127.0.0.1:8000/api/youtube/inspect -H 'Content-Type: application/json' -d '{"url":""}'` returns `{ "error": ... }` (not HTML); unknown platform is 404 JSON; `POST /api/jobs/missing/cancel` returns `{ "ok": true }`; `./.agents/check-baseline.sh` exits 0.

- [x] **Step 2 — Consume the API from the page**
  Platform form `fetch`es `/api/{platform}/inspect`, renders title/formats/download buttons in JS (same layout as today’s table). Download JS uses `/api/{platform}/jobs` and `/api/jobs/{id}/...`. Remove `POST /{platform}/inspect` HTML and HTMX attributes. Drop job URL aliases.
  *Done when:* empty inspect on `/youtube` shows the error text in `#results`; a valid public URL still lists Video/Audio download buttons; start-download still hits `/api/.../jobs`; `./.agents/check-baseline.sh` exits 0.

- [x] **Step 3 — Sync agent docs**
  Overview, coding standards, API/web rules: JSON inspect, `/api` prefix, no HTMX inspect.
  *Done when:* those files describe `POST /api/{platform}/inspect` and JS consumption; handoff next action is `/check`.

## Data / contracts

| Method | Path | Shape |
| --- | --- | --- |
| GET | `/{platform}` | HTML page |
| POST | `/api/{platform}/inspect` | `{ page_url, media }` or `{ error }` |
| POST | `/api/{platform}/jobs` | `{ job_id, label }` or `{ error }` |
| GET | `/api/jobs/{id}/events` | SSE |
| GET | `/api/jobs/{id}/file` | octet-stream or 404 JSON |
| POST | `/api/jobs/{id}/cancel` | `{ ok: true }` |

## Static checks

- `./.agents/check-baseline.sh` — exit 0 (2026-09-29: `py 0/0`, `eslint 0/0`)

## Verification

1. Empty inspect JSON → `{ "error": "Paste a video URL first." }` (or same message as today)
2. `GET /youtube` still shows the URL form (no HTMX attrs)
3. Failure: `POST /api/not-a-platform/inspect` → 404 JSON
4. Failure: `GET /api/jobs/not-a-job/file` → 404 JSON

## Context manifest

- `blueprint/context/project-overview.md`
- `blueprint/context/coding-standards.md`
- `app/backend/routes.py`
- `app/backend/schemas.py`
- `app/web/routes.py`
- `app/web/templates/platform.html`
- `app/web/static/app.js`
- `.agents/rules/api-backend.md`
- `.agents/rules/web-frontend.md`

## Execution ledger

- 2026-09-29: spec written via `/fix`. Implementation blocked on approval.
- 2026-09-29: Step 1 — `inspect_router` + jobs under `/api`. Empty inspect 400 JSON; unknown platform 404 JSON; missing cancel `{ok:true,status:gone}`. Baseline 0/0.
- 2026-09-29: Step 2 — form `fetch` + JS tables; HTMX and unprefixed job aliases removed. Empty URL error in `#results`; zoo inspect showed Video/Audio download buttons (`data-download` count 18). Downloads post `/api/{platform}/jobs`.
- 2026-09-29: Step 3 — agent docs describe `POST /api/{platform}/inspect` and JS consumption.
- 2026-09-29: `/check` passed all done-whens (curl JSON + Cursor browser).
- 2026-09-29: `/complete` archived on `fix/json-inspect-api` with the FastAPI split included (user yes).

## Verification evidence

- API `POST /api/youtube/inspect` `{"url":""}` → HTTP 400 `{"error":"Paste a video URL first."}`
- API `POST /api/not-a-platform/inspect` → HTTP 404 `{"error":"Unknown platform."}`
- API `POST /api/jobs/missing/cancel` → HTTP 200 `{"ok":true,"status":"gone"}`
- API `GET /api/jobs/not-a-job/file` → HTTP 404 `{"error":"File is no longer available."}`
- Web `GET /youtube` HTTP 200; page source has no `hx-` / `htmx`
- Web `/youtube` empty Fetch formats → `#results` text `Paste a video URL first.`
- Web `/youtube` public zoo URL inspect → Video/Audio tables; 18 `[data-download]` buttons
- Browser start-download posted `/api/youtube/jobs`; SSE `/api/jobs/{id}/events`
- `./.agents/check-baseline.sh` exit 0

## Exact next action

Archived. Next lifecycle: `/feature`, `/fix`, or `/rollback`.
