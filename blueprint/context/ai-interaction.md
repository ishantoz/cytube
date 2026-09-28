# CyTube AI Interaction Policy

## Operating mode

Use a file-backed, bounded engineering loop. The user approves the spec once;
after approval the agent may execute all in-scope steps autonomously, update
state, and verify each step. It stops with a review packet before completion.

Do not require per-step approval unless scope or risk changes.

## Lifecycle

`status -> feature/fix -> approve spec -> implement -> check/audit -> review -> complete`

1. `feature`, `fix`, or `rollback` writes one active spec to
   `current-feature.md`.
2. The user reviews and approves that spec before source code changes.
3. `implement` creates or reuses the work branch and executes small reviewable
   steps inside the approved boundary.
4. After each material decision or completed step, update checkboxes, execution
   evidence, exact next action, and `session-handoff.md`.
5. `check` proves done-when criteria; `audit` reviews quality, security,
   performance, and standards.
6. Stop with a compact review packet.
7. `complete` performs final safety checks and asks before commit/merge. Ask
   separately before push.

## Specification gate

Every non-trivial work item must state:

- goal, scope, owned paths, and out-of-scope behavior
- approved decisions and unresolved questions
- reviewable steps with observable done-when criteria
- which package(s) the work touches (`app/` templates, static, or Python modules)
- endpoint/schema verification for API changes
- migration/compatibility/recovery plan where relevant
- the verification matrix: static commands plus the manual path
- minimal context manifest

## Verification gate

No test framework exists yet. Adopting one is an open decision in
`project-plan.md`, not something a feature task may do.

The repo starts **green** at onboarding. The gate is **no new errors**:

Every step declares and runs:

- `./.agents/check-baseline.sh`, which must exit 0
- `pnpm build` when build-sensitive

Re-recording the baseline (`--write`) requires the user's explicit approval.

Every behavior-changing step also records manual evidence: app (web/API), route
or endpoint, what was observed, and at least one failure path.

An agent may not mark a step done, pass `check`, or propose `complete` when a
declared check is missing, failing, or unrun.

## Autonomous boundary

After spec approval, continue without asking while:

- the work remains within the named scope and owned paths
- no new product or architecture decision is required
- actions are reversible and non-destructive
- unrelated baseline or user changes remain untouched
- required checks pass or a scoped fix is clear
- no open or fixed P0 or P1 finding blocks progress

Stop and ask one focused question when a missing choice materially changes
behavior, compatibility, data, security, cost, or destructive impact.

Never autonomously commit, merge, push, deploy, publish, send external messages,
change remote services, rotate credentials, reset data, or discard work.

## Durable low-token context

Chat history is not authoritative. Persist only durable, distilled state:

- `project-overview.md`: compact project truth
- `current-feature.md`: approved active spec and progress
- `session-handoff.md`: replaceable resume snapshot
- git: branch, changes, and commits
- history: completed work and sanitized session summaries

Fresh sessions load only the bootstrap files from `AGENTS.md`, inspect git, then
load the active `Context manifest`.

## Stop conditions

Stop bounded execution for:

- scope drift or overlap with unrelated dirty files
- an endpoint, schema field, or business rule that does not exist
- a request that implies a test framework or second state library without a spec
- destructive or externally mutating action
- repeated failure without new evidence
- a required check that fails and cannot be repaired in scope
- an open or fixed P0 or P1 finding

## Communication

- Lead with outcome or blocker.
- Be concise and use lists for sequences.
- Never claim verification that was not run.

## Completion review packet

Before `complete`, report:

- delivered behavior
- changed and owned files
- static checks with their real output
- manual evidence: app, route/endpoint, observation, failure path
- docs/rules impact
- remaining risks or manual try path
- exact next lifecycle action
