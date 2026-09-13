# Browser Evidence Rules

How to drive a real browser when working on the web UI, or anything where the
answer is "what does it actually look like / do". With no test framework in this
repo, browser evidence is a large share of the verification gate.

## Tool of record: Playwright MCP

`.cursor/mcp.json` configures the `playwright` MCP server through one launcher,
`.agents/playwright-mcp.sh` (`@playwright/mcp`, Chrome, 1440x900). It is the
default and preferred way to open a page, click, resize, read console/network
errors, measure an element, and capture a screenshot.

Use it for all interactive and exploratory UI work.

## Never hand-roll a throwaway browser script

Do **not** write an ad-hoc `.mjs` / `.py` script that launches Chrome
(`puppeteer`, `puppeteer-core`, `playwright`, CDP, `chrome --headless`) just to
look at a page, measure a box, or grab a screenshot during development.

This is banned even when the script is deleted afterwards.

## This is enforced by a hook

One policy script, `.agents/hooks/no-adhoc-browser.py`, runs on every shell
command under both hosts: Cursor via `.cursor/hooks.json` and Claude Code via
`.claude/settings.json`.

Do not work around a block: fix the approach.

## Reaching the app

Playwright MCP restricts file system access to workspace roots and blocks
`file://` navigation by default. Serve over HTTP instead:

- `pnpm dev` — web at http://localhost:3000, API at http://localhost:3001
- Requires Postgres: `pnpm db:up` before testing data-dependent pages
- Demo channel: http://localhost:3000/r/lobby

Reuse a running server; do not start a duplicate.

## Never capture credentials

Do not screenshot tokens, paste credentials into evidence, or log auth secrets.
Describe the signed-in state, not the credential.

## If Playwright MCP is unavailable

1. Say plainly that Playwright MCP is not available.
2. Prefer non-browser evidence: `./.agents/check-baseline.sh`, or curl against
   `http://localhost:3001`.
3. State which path you used.

## Reporting

Name the tool that produced each piece of evidence. Screenshots and behavior
claims must be traceable to Playwright MCP or a named committed gate.
