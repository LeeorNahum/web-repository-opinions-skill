# Definition Of Done

This is a completion summary across the skill. It is not the source of truth for the detailed rules below. Load the owning references for every category the work touches.

A feature is done only when its product contract, implementation, runtime, and verification agree. If one category is false or unknown, the work is locally edited, not done.

Use this file as the first completion index:

- Product behavior and failure states: `product-ux.md`, `interaction-feedback.md`, `user-facing-errors.md`
- URLs and public discovery: `routing.md`, `query-state.md`, `public-discovery.md`, `seo.md`
- Public protocols and agent access: `public-interfaces.md`
- Data, migrations, and external sources: `data-model.md`, `source-of-truth.md`, `external-sources.md`, `search-indexing.md`
- Runtime and deployment: `environment.md`, `branches.md`, `deployment.md`, `runtime-truth.md`, `provider-setup.md`
- Responsive UI and visual contracts: `responsive-layout.md`, `design-tokens.md`, `social-metadata.md`

## Product Contract

- The user flow works end to end.
- The data state machine and authorization rules are explicit.
- Failure paths are actionable and use product-owned language.
- URLs, names, docs, prompts, and compatibility promises describe the current behavior.

## Code And Data

- Env contracts match the values every runtime reads.
- Generated clients, schemas, and types are current.
- Migrations have been dry-run, executed only in approved environments, and independently verified.
- Stale names, route shapes, package paths, env keys, and compatibility branches have been removed.

## Runtime

- Provider state, domains, webhooks, schedules, storage, and backend functions match the code.
- The target branch and target runtime contain the same intended change.
- Deferred manual or approval-gated steps are named clearly.

## Verification

- Lint, typecheck, focused tests, and production builds pass for every affected app and package.
- Behavioral tests cover changed contracts, failure paths, retries, partial success, and idempotency where applicable.
- Public pages remain useful without JavaScript and expose headings, links, canonical metadata, and structured data in rendered HTML.
- Sitemap entries use canonical public-page eligibility and exclude private, unavailable, deleted, authenticated, and arbitrary query pages.
- Generated OpenAPI matches runtime responses and shared schemas.
- MCP tools pass protocol-client or Inspector checks against the same shared resource contract.
- Source metadata parsers enforce limits, clear stale values, and update indexed fields.

Only run checks that apply to the feature, but never omit a category because the implementation happened in a different app or provider.
