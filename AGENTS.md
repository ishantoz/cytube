# CyTube Agent Guide

This is the single cross-tool entrypoint for AI work in this repository. Claude
imports it through `CLAUDE.md`; Codex, Cursor, OpenCode, and other tools should
read it directly.

## Scope

- **CyTube** here is a public-URL download portal: paste a YouTube, Instagram,
  Facebook, TikTok, Dailymotion, or Bilibili link, list formats, download
  video+audio / video only / audio only. Server fetches with yt-dlp, streams
  the file, then deletes temp copies. No login cookies.
- **App:** one Python package at the repo root (`app/`). FastAPI + Jinja2 +
  Flowbite/Tailwind CDN. JSON inspect/jobs under `/api`; the page consumes them in JS.
- The **AI Blueprint** is a workflow overlay, not an app generator. Never run a
  framework scaffolder inside this repository.
- The old Cloudflare Worker / Astro / Hono / D1 stack is **not** the current
  app. Do not restore it without a spec. Installed Cloudflare skills in
  `skills-lock.json` are leftover; do not apply Wrangler/Workers rules here.

## Minimal session bootstrap

Read these first, in order:

1. `blueprint/context/project-overview.md`
2. `blueprint/context/current-feature.md`
3. `blueprint/context/session-handoff.md`
4. Git status and the active branch

Then load only files named in the active work item's `Context manifest`. Do not
scan all project knowledge or depend on previous chat history. Durable decisions
and progress belong in Blueprint files.

## Focused context routing

- Architecture: `.agents/rules/project-architecture.md`
- Web frontend: `.agents/rules/web-frontend.md`, `.agents/web-agent.md`
- API backend: `.agents/rules/api-backend.md`, `.agents/api-agent.md`
- Browser evidence: `.agents/rules/browser-evidence.md`
- Lifecycle: `.agents/rules/agent-workflow.md`,
  `.agents/rules/knowledgebase-maintenance.md`
- Package manager: `.agents/rules/package-manager.md`

`.agents/rules/*.md` and `.agents/skills/` are canonical. `.cursor` and
`.claude` are adapters, not independent sources. Both hosts get the same
enforcement: one hook script (`.agents/hooks/no-adhoc-browser.py`), one
Playwright launcher (`.agents/playwright-mcp.sh`), and `.claude/skills` /
`.cursor/skills` symlinked to `.agents/skills`.

## Commands

- Package manager: **uv** only (`uv.lock` and `pyproject.toml` are authoritative)
- Install: `uv sync`
- Dev server: `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
- Typecheck / import smoke: `uv run python -c "from app.main import app"`
- **Regression gate: `./.agents/check-baseline.sh`**
- Do not edit `.env` files.

## Architecture invariants

### FastAPI portal (`app/`)

- `app/main.py` — compose FastAPI, mount `/static`, include routers
- `app/web/` — Jinja templates, static JS, HTML pages (`GET /{platform}`)
- `app/logic/` — platform allowlists, yt-dlp extract, download jobs (no FastAPI)
- `app/backend/` — JSON inspect, jobs, SSE, file stream, cancel (mounted at `/api`)
- Include `/api` routers before `GET /{platform}`
- Public hosts only (see `PLATFORMS` in `app/logic/extractor.py`)

### Downloads

- Process in a temp folder, stream to the client, then delete
- Concurrent jobs; UI is a bottom-right progress stack with confirm-to-cancel

### Cross-cutting

- Do not add a second HTTP client stack or a Worker/Astro app without a spec.
- Do not restore users/channels/playlist/chat until a spec asks.

## Engineering quality gate

Every non-trivial spec must assess module ownership, reuse, scale,
compatibility, recovery, and verifiability. Apply only relevant checks.

## Verification

**No test framework yet.** Do not claim tests were run unless a real test command
exists.

The gate is **no new errors**:

```bash
./.agents/check-baseline.sh    # must exit 0
```

It compile-checks `app/` and imports `app.main`.

Every behavior-changing step also records manual evidence:

- which app (web / API) and which route or endpoint
- what you observed in the browser or via curl
- at least one failure path: 404, empty list, or validation error

## Lifecycle

Use one file-backed work item at a time:

`status -> feature/fix -> approve spec -> implement -> check/audit -> review -> complete`

- `feature` and `fix` write `blueprint/context/current-feature.md`.
- Spec approval authorizes bounded implementation. Stop for scope drift,
  unresolved product choices, destructive actions, unrelated dirty-file conflicts,
  failed required checks, or open P0/P1 findings.
- After each completed step, update the active spec, evidence, and
  `session-handoff.md`.
- `complete` alone archives work and proposes commit/merge. Commit, merge, push,
  and destructive operations require approvals in
  `blueprint/context/ai-interaction.md`.

Canonical skills live under `.agents/skills/<name>/SKILL.md`.

## Browser evidence

Use the configured `playwright` MCP server for UI inspection. Never write a
throwaway script that launches a browser; `.agents/hooks/no-adhoc-browser.py`
blocks it. Details in `.agents/rules/browser-evidence.md`.

## Safety

- Check git status before edits and preserve unrelated user work.
- Do not edit `.env` or secrets.
- Do not use destructive git commands without explicit approval.
- Every implementation includes a docs/rules impact check.
- Pylance/Pyright must use `.venv` (`pyrightconfig.json` / `[tool.pyright]`).
