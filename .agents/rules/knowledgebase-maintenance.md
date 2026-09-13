# Knowledgebase Maintenance Rule

The project knowledgebase must evolve with the code. Future agents should not
need the user to re-explain architecture after each feature lands.

## When To Update Docs/Rules

Update the relevant documentation in the same task when work changes:

- Product scope or roadmap
- The module convention, the API surface factory, or auth/session storage
- Portal routes, the portal split, or tenant/slug resolution
- The design system, the dropdown rule, or shared composites
- Verification commands, package manager rules, or ignored scopes

## Files To Consider

- `AGENTS.md`
- `.agents/rules/*.md` (smallest matching file)
- `.cursor/rules/*.mdc` (thin routers only)
- `.agents/*.md` specialist briefs
- `blueprint/build-plan.md` when a capability ships
- `blueprint/reference/` when briefs exist

## Completion Gate

1. Did this change create behavior future agents need to know?
2. Did it add, rename, or remove routes, endpoints, or module conventions?
3. Did it change commands, env, or ignored folders?
4. If yes, update the matching files before claiming done.
5. If no, say why no knowledgebase update was needed.
