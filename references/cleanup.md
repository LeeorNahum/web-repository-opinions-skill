# Cleanup

Treat the current intended product contract as truth. Prefer replacing wrong or unreleased behavior over layering shims on top of it.

Before removing something, understand why it exists; remove it only once you can explain what it did and confirm the replacement covers it (Chesterton's fence). Leave each area you touch cleaner than you found it (the boy scout rule) without expanding into unrelated rewrites.

- Remove dead routes, stale compatibility paths, and unreferenced code.
- Add compatibility only for an explicit supported contract, deployed consumer, durable user data, or approved rollout.
- Name what the compatibility preserves and why before adding aliases, conversions, dual writes, fallbacks, or deprecated paths.
- Remove obsolete writers, migrations, helpers, and references after the replacement path is deployed and verified.

Temporary docs, prompts, screenshots, and audits are useful during a build session but should not live forever in the product repo. Each should end up one of:

- Committed intentionally as an archive, then removed from the active tree so it stays recoverable in history
- Kept outside the product repo
- Promoted into a durable docs location only if it remains true and useful

Do not let a production repo become a scrapbook of working artifacts. Keep the active tree to what is true and current.
