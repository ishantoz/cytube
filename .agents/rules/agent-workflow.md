# Agent Workflow Rule

## Before Work

- Read the minimal bootstrap in `AGENTS.md`, inspect git, then only the active
  Context manifest or matching router files.
- Inspect nearby code before editing.
- Preserve unrelated user changes.
- Ask one short question only if a requirement blocks correct work.

## During Work

- Make the smallest correct change.
- Keep pages thin; logic in components, lib, or route modules.
- Use pnpm only.
- Do not edit `.env` or secrets.
- Do not run destructive git commands without explicit approval.
- After spec approval, execute listed steps without per-step prompts while the
  approved boundary remains valid.
- Stop on scope drift, unresolved material decisions, destructive or external
  actions, unrelated dirty-file conflicts, failed required checks, or P0/P1
  findings.
- At material checkpoints, update spec progress, evidence, exact next action,
  and `session-handoff.md`.

## Verification gate

**No test framework yet.** Do not claim tests were run.

Static, before any step is checked:

```bash
./.agents/check-baseline.sh   # tsc + lint for web and backend
pnpm build                    # build-sensitive changes only
```

The repo starts **green** at onboarding. The gate is "no NEW errors against
`blueprint/context/adoption-baseline.md`". Re-recording the baseline (`--write`)
needs explicit user approval.

Manual evidence, for any step that changes behavior:

- which app (web / API) and which route or endpoint
- what you observed (browser, curl, or API response)
- at least one failure path: 404, empty list, or validation error

## Scope Control

Do not, unless the task explicitly asks: refactor unrelated code; upgrade
dependencies; change frameworks; reformat files you did not modify; modify
global config; redesign architecture during a feature task.

## Git discipline

Before calling a task done:

```bash
git status
git diff
```

Never commit, merge, or push without explicit approval.

## Lifecycle skills

Canonical skills in `.agents/skills/`:

| Skill | Purpose |
| --- | --- |
| `status` | Read-only orientation |
| `prototype` | Lock UI theme (pre-build) |
| `feature` / `fix` | Write scoped spec |
| `implement` | Execute approved steps |
| `check` / `audit` | Verify and review |
| `complete` | Archive and propose commit |
| `handoff` / `resume` | Pause and resume |
| `onboard` / `adopt` | Setup or brownfield adoption |
| `overview` | Regenerate project overview |

## Prototype before first UI feature

Look is locked in `prototypes/theme.css` and HTML mockups. The first UI
`/feature` (6b) ports the theme into the app stylesheet.
