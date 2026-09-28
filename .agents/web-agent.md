# Web Agent

Use for Jinja templates, static JS, and `app/web/routes.py`.

Read:

- `AGENTS.md`
- `.agents/rules/web-frontend.md`
- `.agents/rules/project-architecture.md`
- `.agents/rules/browser-evidence.md` (for UI verification)

Operating rules:

- Keep templates thin; client behavior in `app/web/static/app.js`.
- Inspect `fetch`es `POST /api/{platform}/inspect` and renders in JS.
- Downloads use `/api` jobs + concurrent stack + SSE.
- Do not call yt-dlp from `web/`.
- Verify with `./.agents/check-baseline.sh` and Playwright MCP (or curl)
  against `http://127.0.0.1:8000`.
