---
name: implement
description: Build the approved current Blueprint feature, fix, or rollback in bounded reviewable steps. Persists checkpoints and handoff state, enforces CyTube engineering and manual-evidence gates, verifies each step, and stops with a review packet before complete, commit, merge, push, or deployment. Use when the user approves the current spec or asks to implement it.
---

# implement - execute the approved spec

## Contract

`blueprint/context/current-feature.md` is the boundary. Spec approval authorizes
all listed implementation steps without per-step prompts. It does not authorize
new scope, commits, merges, pushes, deploys, destructive actions, or product
decisions not recorded in the spec.

## Preflight

Read the bootstrap files from `AGENTS.md`, inspect git, then load only the active
`Context manifest`.

Stop before source edits when:

- there is no active approved spec (`Status: approved`)
- owned paths overlap unrelated dirty work without explicit approval
- the spec has unresolved material questions
- backend-classified work lacks `Backend testing` or a focused command
- migration/compatibility/recovery is missing for a data or contract change
- the current branch/worktree cannot safely represent this item

Create or reuse `feature/<name>`, `fix/<name>`, or `rollback/<name>`. Never strand
or overwrite unrelated work to switch branches. If baseline dirt prevents safe
branching, keep the user-authorized existing branch and record the exception.

## Engineering check

Before code, verify the spec's decisions against nearby code:

- owning module and public contracts are correct
- stable existing primitives are reused
- any new abstraction has a current repeated concept
- relevant query/index/bounds/transaction/idempotency risks are covered
- old/new readers and writers remain safe during migration
- unstable boundaries are injectable or mockable

If the approved approach is technically invalid, stop and update the spec for
review instead of improvising.

## Execute steps

For each first unchecked step:

1. Implement only that step inside owned paths.
2. Add/update colocated backend tests in the same diff when backend-classified.
3. Run the declared focused test command first. Missing, failing, or unrun
   backend tests block the step.
4. Run relevant lint/build/browser/API/migration evidence from the spec.
5. Review the diff for scope, tenant/authz boundaries, error paths, modularity,
   migration safety, performance, and docs/rules impact.
6. Repair clear in-scope failures and rerun affected checks. Stop after repeated
   attempts without new evidence.
7. Mark the step checked only after its done-when and required evidence pass.
8. Append one concise Execution ledger entry and Verification evidence.
9. Replace `session-handoff.md` with current work ID, branch, HEAD when
   available, last step, checks, blocker, relevant files, and exact next action.
10. Continue to the next step automatically.

Do not create checkpoint commits unless the user explicitly requests one in the
current conversation. `/complete` owns the work-level commit.

## Verification gate

This repo has no test framework. Do not introduce one to satisfy a step; that is
its own decision (see `.agents/rules/agent-workflow.md`). The gate is static
checks plus recorded manual evidence.

Static, and non-negotiable before a step is checked:

- `./.agents/check-baseline.sh`, which must exit 0
- `pnpm build` for build-sensitive changes

The repo does not start green: 206 `tsc` errors and 48 `eslint` errors at
adoption. The gate is **no new errors** against
`blueprint/context/adoption-baseline.md`, which `check-baseline.sh` enforces per
file. Re-recording the baseline (`--write`) needs the user's explicit approval;
never do it to quiet a red run.

`next.config.ts` does not silence TypeScript or ESLint in this repo. A green
`pnpm build` is valid evidence when build-sensitive.

Manual evidence, for any step that changes behavior:

- which app (web / API) and which route or endpoint
- which API call or page interaction you performed
- what you observed, quoted or described concretely
- at least one failure path: 404, empty list, or validation error

No step may be checked off while its declared checks are absent, red, or unrun,
or while its manual evidence is asserted rather than observed.

## Rollback safeguard

For `Type: Rollback`, preserve Blueprint/history files and reverse only approved
product paths from the exact recorded commit. Reconfirm commit ancestry and
product diff before applying. Stop on conflicts; never reset, broad-checkout, or
silently cascade into later work.

## Quality and findings

After all steps:

- run the post-implementation maintainability check
- run relevant acceptance evidence
- inspect `findings.md`
- repair open P0/P1 only as recorded extra steps, mark them `fixed`, and require
  a separate audit to close them

Do not waive findings on the user's behalf.

## Review packet

Stop before `/complete` with:

- branch and work item
- delivered behavior and changed files
- backend classification and focused test evidence
- other checks and observable results
- engineering review outcome
- migration/compatibility status
- docs/rules impact
- findings and remaining risks
- manual try path
- exact next action

## Hard stops

Stop for scope drift, unresolved decisions, baseline conflicts, destructive or
external mutation, missing migration safety, required check failure that cannot
be repaired in scope, P0/P1 gates, auth/entitlement denial, or repeated failure.
