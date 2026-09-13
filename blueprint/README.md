# CyTube AI Engineering Lifecycle

The Blueprint keeps engineering intent, active work, proof, and history in
project files so any supported agent can resume without loading old chats.

## Normal loop

```text
status -> feature/fix -> approve spec -> implement -> check/audit -> review -> complete
```

Pre-build (outside the feature loop):

```text
/onboard -> project-plan + build-plan -> /overview -> /prototype -> /feature -> build
```

- `status`: read-only orientation and exact next action
- `prototype`: lock UI theme before first real UI feature
- `feature` / `fix`: write one scoped spec and stop for approval
- `implement`: execute approved steps autonomously inside the boundary
- `check`: prove done-when behavior with evidence
- `audit`: review quality/security/performance and maintain findings
- `complete`: archive and ask before commit/merge; ask separately before push
- `handoff`: save a compact pause snapshot
- `resume`: reconstruct from spec and git in a fresh session

## Sources of truth

- `project-plan.md`: product purpose and durable direction
- `build-plan.md`: shipped capabilities and living roadmap
- `context/project-overview.md`: compact generated session bootstrap
- `context/current-feature.md`: one active approved work item
- `context/session-handoff.md`: replaceable resume snapshot
- `context/findings.md`: durable review findings
- `history/`: completed work and compact session handoffs

Chat history is not authoritative.

## Verification model

No test framework yet. The gate is:

- `./.agents/check-baseline.sh` on every step (no new errors)
- `pnpm build` when build-sensitive
- recorded manual evidence: app, route/endpoint, observation, failure path

## Context model

Fresh sessions read only:

1. `context/project-overview.md`
2. `context/current-feature.md`
3. `context/session-handoff.md`
4. git state
5. files named by the active Context manifest

Detailed rules (`.agents/rules/`) are lazy-loaded.
