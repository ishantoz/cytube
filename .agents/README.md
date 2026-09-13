# CyTube AI Knowledgebase

This directory is generic AI-agent guidance. It is not tied to Cursor, Claude,
Codex, or any one tool.

Start with `AGENTS.md`, then read only the specialist brief or rule file that
matches the user request.

## Specialist Briefs

- `.agents/web-agent.md`: Next.js UI, pages, components, API client
- `.agents/api-agent.md`: Hono routes, Prisma, migrations, API design

## Rules

See `.agents/rules/README.md`.

## Skills

Canonical skills in `.agents/skills/`. Key lifecycle skills:

- `/prototype` — lock UI theme before building
- `/feature` — write a scoped spec for new work
- `/implement` — execute an approved spec
- `/check` — verify done-when criteria
