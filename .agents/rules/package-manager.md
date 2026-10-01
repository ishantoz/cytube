# Package Manager Rule

Use **uv** only for this Python app.

- Lockfile is `uv.lock` and it is authoritative (`pyproject.toml` lists deps).
- Do not use pip, poetry, conda, npm, yarn, pnpm, or bun for app dependencies.
- Translate install commands to `uv add` / `uv sync`.

```bash
uv sync
uv add <package>
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
uv run python -c "from app.main import app"
```

Single package at the repo root. No `web/` or `backend/` workspaces.
Pylance must resolve packages from `.venv` via `pyrightconfig.json`.
