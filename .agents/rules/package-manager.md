# Package Manager Rule

Use **pnpm 11** only.

- Lockfile is `pnpm-lock.yaml` and it is authoritative.
- Do not use npm, yarn, or bun for this project.
- Translate npm/yarn/bun commands to pnpm.
- Do not create or commit `package-lock.json`, `yarn.lock`, or `bun.lockb`.

```bash
pnpm install
pnpm add <package>
pnpm dev
pnpm build
pnpm typecheck
```

Single package at the repo root. No `web/` or `backend/` workspaces.
