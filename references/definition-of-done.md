# Definition Of Done

This is a completion summary across the skill. It is not the source of truth for the detailed rules below. Load the owning references for every category the work touches.

A feature is done only when its product contract, implementation, runtime, and verification agree. If one category is false or unknown, the work is locally edited, not done.

Use this file as the first completion index:

- Product behavior and failure states: `product-ux.md`, `interaction-feedback.md`, `user-facing-errors.md`
- URLs and public discovery: `routing.md`, `query-state.md`, `public-discovery.md`, `seo.md`, `social-metadata.md`, `badges.md`
- Public protocols and agent access: `public-interfaces.md`
- Data, migrations, and external sources: `data-model.md`, `source-of-truth.md`, `external-sources.md`, `search-indexing.md`
- Runtime and deployment: `environment.md`, `branches.md`, `deployment.md`, `runtime-truth.md`, `provider-setup.md`
- Responsive UI and visual contracts: `responsive-layout.md`, `design-tokens.md`

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
- Every publicly reachable page expands into its own link preview card when pasted, and private routes expand into the content-free fallback.
- Sitemap entries use canonical public-page eligibility and exclude private, unavailable, deleted, authenticated, and arbitrary query pages.
- Generated OpenAPI matches runtime responses and shared schemas.
- MCP tools pass protocol-client or Inspector checks against the same shared resource contract.
- Source metadata parsers enforce limits, clear stale values, and update indexed fields.

Only run checks that apply to the feature, but never omit a category because the implementation happened in a different app or provider.

## Verify Against The Task Runner You Actually Have

A gate you run wrong is a gate you did not run, and the failure is silent: the command exits zero and you believe the check passed.

- **Know what your runner's cache flags mean before repeating them.** In Turborepo, `--force` is not "ignore the cache", it is `--cache=local:w,remote:w`: writes stay on, reads are skipped. Every forced run therefore writes a fresh entry to disk, so a habit of passing it on every gate grows the cache without bound. One repository reached 40 GB of `.turbo` this way. When you want a cold run without hoarding the result, pass the write-nothing form (`--cache=local:`) instead, and prune the cache on a schedule rather than trusting it to bound itself.
- **A flag on the workspace script is not always a flag on the runner.** Package managers forward extra arguments to the underlying script, so the same flag can land on the task runner in one invocation and on the tool inside a package in another, where it is an unknown option. Check where it landed rather than assuming.
- **A fresh worktree is not a working checkout.** Reviewing a snapshot in a detached worktree requires installing dependencies there first; otherwise every gate fails for a reason that has nothing to do with the change, and the review reports on the runner instead of the code.

Prefer the smallest command that proves the thing, and read its output rather than its exit code.
