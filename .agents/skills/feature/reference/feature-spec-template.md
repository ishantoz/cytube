# Feature: <name>

**From build-plan:** feature <n>
**Status:** draft
**Branch:** feature/<name>
**Updated:** <YYYY-MM-DD>

Use `draft` until the user explicitly approves the spec, then set
`Status: approved`. Implementation may start only after approval.

## Goal

What this feature delivers, in a sentence or two. Why it matters.

## Design reference

For a visual or replication feature (recreating a design, matching a mockup),
link the reference image(s) here, stored in `blueprint/reference/`. A screenshot
pins down what prose can't, so build against it, not a guess. Omit this section
when the feature has no visual target.

## In scope

- The specific things this feature includes.

## Out of scope

- What it deliberately doesn't touch (deferred to a later feature).

## Approved decisions

- Consequential answer, date, and short rationale.

## Open questions

- Only choices that block or materially change implementation.

## Engineering review

- **Contracts / module owner:** affected public contracts and owning module.
- **Reuse / modularity:** existing primitives used and any new seam.
- **Scale / data access:** relevant bounds, indexes, transactions, retries, or N/A with reason.
- **Migration / compatibility / recovery:** safe sequence and rollback limits, or N/A with reason.
- **Testing matrix:** unit, integration, browser, and explicit exemptions.

## Build steps

Small, reviewable units. Each ends with something working. `/implement` checks
these off as it finishes them, so progress survives a context clear: a fresh
session reads which boxes are ticked and resumes from the first unchecked step.

- [ ] **Step 1 - <step>** - what you build. *Done when:* <observable criteria>.
- [ ] **Step 2 - <step>** - what you build. *Done when:* <observable criteria>.

## Files / areas

- Owned paths this work may create or change.

## Data / contracts

- Schema, types, or API shapes involved, or "none yet."

## Static checks

Required for every step.

- `./.agents/check-baseline.sh` - must exit 0 (no new tsc or eslint errors
  against `blueprint/context/adoption-baseline.md`)
- `pnpm build` when the change is build-sensitive

The repo starts red by design; the gate is no-new-errors. `next.config.ts`
silences TypeScript and ESLint during `next build`, so a green build is not
evidence.

## Verification

- How to verify: what to click through, and the observable done-when per step.
- If a test runner is configured, name the in-scope logic that needs a test
  (parsers, formatters, validators, server actions - not components or
  integration/render routes), so each logic-bearing step ships its test. If no
  runner is configured, say so and rely on screenshot plus build evidence. See the
  Testing gate in `coding-standards.md`.

## Context manifest

- Only rule, context, and source files needed to implement or resume this item.

## Execution ledger

- Material checkpoints only: date, step, files, command/result, blocker.

## Verification evidence

- Exact commands and observed results.

## Exact next action

- One deterministic next step.
