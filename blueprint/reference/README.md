# Blueprint reference

Durable product and domain reference material for humans and AI agents.
Lifecycle state stays in `blueprint/context/`; enforceable rules stay in
`.agents/rules/`; native skills stay in `.agents/skills/`.

| Path | Role |
| --- | --- |
| [`briefs/`](./briefs/) | Approved long-form product/domain briefs |
| [`playbooks/`](./playbooks/) | Repeatable storefront procedure playbooks |
| [`raws/`](./raws/) | Unprocessed sourced inputs (never authoritative) |
| [`research/`](./research/) | Dated investigations (promote conclusions) |

Load only files named by the active work item's Context manifest. Do not scan
this tree by default.
