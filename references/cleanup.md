# Cleanup

Before a product ships, prefer replacing wrong flows over layering shims on top of them.

- Remove dead routes, stale compatibility paths, and unreferenced code.
- Do not keep a compatibility layer for an unreleased mistake. Fix the contract directly.
- Do not add backwards compatibility, format conversions, or fallback logic that hides the real issue unless the user explicitly approves it after hearing the tradeoff.

Temporary docs, prompts, screenshots, and audits are useful during a build session but should not live forever in the product repo. Each should end up one of:

- Committed intentionally as an archive, then removed from the active tree so it stays recoverable in history
- Kept outside the product repo
- Promoted into a durable docs location only if it remains true and useful

Do not let a production repo become a scrapbook of working artifacts. Keep the active tree to what is true and current.
