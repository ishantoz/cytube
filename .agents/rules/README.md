# Canonical Agent Rules Index

The `.md` files in this directory are the canonical enforceable rule bodies.
Read only the files routed by `AGENTS.md` or an active work item's
`Context manifest`.

| File | Use For |
| --- | --- |
| `project-architecture.md` | Monorepo shape, packages, ports, invariants |
| `web-frontend.md` | Next.js pages, components, API client, styling |
| `api-backend.md` | Hono routes, Prisma 7, migrations, API conventions |
| `browser-evidence.md` | Playwright MCP; no hand-rolled browser scripts |
| `package-manager.md` | pnpm 11 workspace rules |
| `agent-workflow.md` | Agent workflow, verification gate, Blueprint loop |
| `knowledgebase-maintenance.md` | Docs/rules impact check |

## Tool adapters

| Asset | Canonical | Cursor | Claude Code |
| --- | --- | --- | --- |
| Rules | `.agents/rules/*.md` | `.cursor/rules/*.mdc` (routers) | `CLAUDE.md` -> `AGENTS.md` |
| Skills | `.agents/skills/` | `.cursor/skills` (symlink) | `.claude/skills` (symlink) |
| Shell hook | `.agents/hooks/no-adhoc-browser.py` | `.cursor/hooks.json` | `.claude/settings.json` |
| Playwright MCP | `.agents/playwright-mcp.sh` | `.cursor/mcp.json` | — |

When a canonical rule changes, update any affected thin adapter.
