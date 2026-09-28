---
name: cytube
description: Route CyTube work to the smallest relevant canonical rules while preserving FastAPI web/logic/backend boundaries, uv conventions, and context-budget constraints.
---

# cytube - focused project routing

Start from `AGENTS.md` and the active Context manifest.

- Web UI, templates, JS inspect/download stack: `web-frontend.md`, `web-agent.md`
- JSON `/api` inspect and jobs: `api-backend.md`, `api-agent.md`
- Extract/jobs domain: `app/logic/`
- Architecture: `project-architecture.md`
- Browser/UI evidence: `browser-evidence.md`
- Lifecycle and verification: `agent-workflow.md`

Do not load every file in a category. Pick the smallest set that answers the
active scope and record it in `current-feature.md`.

Always preserve:

- `app/main.py` composes only; `web` / `logic` / `backend` stay separate
- Public-host allowlists in `app/logic/extractor.py`
- Temp-dir jobs that stream then delete
- uv commands (`uv.lock`)
- `./.agents/check-baseline.sh` as the regression gate

This repo has no test framework yet. The gate is `./.agents/check-baseline.sh`
(Python compile + import), plus recorded manual verification. See
`agent-workflow.md` and `blueprint/context/adoption-baseline.md`.
