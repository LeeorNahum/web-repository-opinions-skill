# Cleanup

Treat the current intended product contract as truth. Prefer replacing wrong or unreleased behavior over layering shims on top of it.

Before removing something, understand why it exists. Remove it only once you can explain what it did and confirm the replacement covers it (Chesterton's fence). Leave each area you touch cleaner than you found it (the boy scout rule) without expanding into unrelated rewrites.

A workaround is a debt, not a feature. When a stopgap, shim, fallback, flag, or temporary branch goes in to get past a blocker, record what will remove it, and remove it the moment the underlying problem is solved. A stopgap that outlives its reason hardens into clutter that reads as intentional, and the next reader cannot tell the difference. Solving the real problem includes deleting the scaffolding that stood in for it.

- Remove dead routes, stale compatibility paths, and unreferenced code.
- Add compatibility only for an explicit supported contract, deployed consumer, durable user data, or approved rollout.
- Name what the compatibility preserves and why before adding aliases, conversions, dual writes, fallbacks, or deprecated paths.
- Remove obsolete writers, migrations, helpers, and references after the replacement path is deployed and verified.

Commit only docs that describe current behavior, such as the README, agent instructions, design tokens, a changelog, and durable guides. Keep session notes, prompts, plans, audit reports, and screenshots outside the product repo, or commit them once as an archive and remove them from the active tree so they stay recoverable in history. Promote a working note into durable docs only if it remains true and useful. Keep the active tree to what is true and current.
