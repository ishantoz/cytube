# Web Agent

Use for Astro pages at `src/pages/`.

Read:

- `AGENTS.md`
- `.agents/rules/web-frontend.md`
- `.agents/rules/project-architecture.md`
- `.agents/rules/browser-evidence.md` (for UI verification)

Operating rules:

- Pages in `src/pages/` stay thin.
- Do not restore the old Next room/channel UI unless a spec asks.
- Verify with `./.agents/check-baseline.sh` and Playwright MCP for UI changes.
