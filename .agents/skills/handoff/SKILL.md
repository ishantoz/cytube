---
name: handoff
description: Save a compact, sanitized, resumable snapshot of the active Blueprint work item without copying chat. Use when pausing work, changing tools, clearing context, or asking to save progress.
---

# handoff - save durable resume state

Read the active spec and git. Replace
`blueprint/context/session-handoff.md` with:

- updated timestamp
- work-item ID/type/status
- branch and HEAD when available
- baseline/worktree caveats
- last completed and first unchecked step
- approved decisions made this session
- current blocker or none
- exact checks run and results
- only currently relevant files
- one exact next action

Before writing, update the active spec's checkboxes, Approved decisions,
Execution ledger, Verification evidence, and Exact next action.

Do not copy chat, exploration chatter, secrets, tokens, signed URLs, command
output with sensitive values, or large diffs. The snapshot must stay within the
line budget in `blueprint/project-config.json`.

If no work item is active, write an idle snapshot with branch, baseline warning,
and the next lifecycle command.
