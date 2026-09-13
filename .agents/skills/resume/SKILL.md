---
name: resume
description: Resume Blueprint work in a fresh or cleared session from project files and git, validating or reconstructing stale handoff state with minimal context loading.
---

# resume - reconstruct and continue safely

1. Read the bootstrap files in `AGENTS.md`.
2. Inspect branch, HEAD, status, recent local log, and active spec checkboxes.
3. Compare `session-handoff.md` work ID, branch, HEAD, last step, and next action
   with the spec and git.
4. If consistent, load only the active `Context manifest`.
5. If stale, reconstruct from the active spec, git diff/log, checked steps, and
   last valid Execution ledger entry. Report any uncertainty and replace the
   snapshot before implementation.
6. Check baseline overlap and required backend testing state.
7. State the exact first action, then follow `implement` only when the user asked
   to continue execution. Otherwise provide status and stop.

Never depend on prior chat or scan all knowledge folders. Never assume a checked
step is valid when its required evidence is absent.
