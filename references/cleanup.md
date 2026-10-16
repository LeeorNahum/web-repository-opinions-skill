# Cleanup

Treat the current intended product contract as truth. Prefer replacing wrong or unreleased behavior over layering shims on top of it.

Before removing something, understand why it exists. Remove it only once you can explain what it did and confirm the replacement covers it (Chesterton's fence). Leave each area you touch cleaner than you found it (the boy scout rule) without expanding into unrelated rewrites.

A workaround is a debt, not a feature. When a stopgap, shim, fallback, flag, or temporary branch goes in to get past a blocker, record what will remove it, and remove it the moment the underlying problem is solved. Never let a temporary path harden into permanent behavior by neglect: a stopgap that outlives its reason becomes clutter that reads as intentional, and the next reader cannot tell the difference. Solving the real problem includes deleting the scaffolding that stood in for it.

- Remove dead routes, stale compatibility paths, and unreferenced code.
- Compatibility requires an explicit supported contract: outside users depending on the old shape under terms someone can name, such as a published API, a client the owner does not control, durable user data, or an approved rollout.
- A product being live is not a contract. When the only people relying on a URL, route, host, or API shape are the owner and their own tools, as with a product that is live but not publicized, break the shape cleanly with no redirects, aliases, shims, or deprecated paths. Update every service, provider setting, environment value, and returned link until the product reads as if it had always used the new shape. Keep compatibility only when outside users depend on the old shape under a contract someone can name, and ask the owner when that is unclear.
- Name what the compatibility preserves and why before adding aliases, conversions, dual writes, fallbacks, or deprecated paths.
- Remove obsolete writers, migrations, helpers, and references after the replacement path is deployed and verified.

Temporary docs, prompts, screenshots, and audits are useful during a build session but should not live forever in the product repo. Each should end up one of:

- Committed intentionally as an archive, then removed from the active tree so it stays recoverable in history
- Kept outside the product repo
- Promoted into a durable docs location only if it remains true and useful

Do not let a production repo become a scrapbook of working artifacts. Keep the active tree to what is true and current.
