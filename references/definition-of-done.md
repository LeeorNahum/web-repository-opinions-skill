# Definition Of Done

This is a completion summary across the skill. It is not the source of truth for the detailed rules below. Load the owning references for every category the work touches.

A feature is done only when its product contract, implementation, runtime, and verification agree. If one category is false or unknown, the work is locally edited, not done.

## Product Contract

- The user flow works end to end.
- Layout and interaction remain usable at the supported viewport sizes and with the supported input methods.
- The data state machine and authorization rules are explicit.
- Failure paths are actionable and use product-owned language.
- URLs, names, docs, prompts, and compatibility promises describe the current behavior.

## Code And Data

- Env contracts match the values every runtime reads.
- A new repository ships, from its first change, a CI workflow that runs its gates, each deployable app's hosting config, and beside each runtime that reads env its `.env.example` and setup document.
- Generated clients, schemas, and types are current.
- Migrations have been dry-run, executed only in approved environments, and independently verified.
- Stale names, route shapes, package paths, env keys, and compatibility branches have been removed.

## Runtime

- Provider state, domains, webhooks, schedules, storage, and backend functions match the code.
- Mail set up for a domain is finished at its mailbox provider: the product's picture, logo, and footer wherever they are the product's to set, and a send verified.
- The target branch and target runtime contain the same intended change.
- Deferred manual or approval-gated steps are named clearly.

## Verification

- Lint, typecheck, focused tests, and production builds pass for every affected app and package, and each deployable app defines real `lint`, `typecheck`, and `build` scripts that the workspace root runs.
- Behavioral tests cover changed contracts, failure paths, retries, partial success, and idempotency where applicable.
- Public pages remain useful without JavaScript and expose headings, links, canonical metadata, and structured data in rendered HTML.
- Every publicly reachable page expands into its own link preview card when pasted, and private routes expand into the content-free fallback.
- Sitemap entries use canonical public-page eligibility and exclude private, unavailable, deleted, authenticated, and arbitrary query pages.
- Generated OpenAPI matches runtime responses and shared schemas.
- MCP tools pass protocol-client or Inspector checks against the same shared resource contract.
- Source metadata parsers enforce limits, clear stale values, and update indexed fields.
- Every gate actually executed, and its output was read rather than its exit code.

Only run checks that apply to the feature, but never omit a category because the implementation happened in a different app or provider.

## Check It The Way A Person Meets It

A build that compiles has not been seen. Before calling any web surface done, verify the served production build yourself, the way a person meets it:

1. Serve the production build: the framework's start or preview command, or a static server over the output folder. The dev server is not the product.
2. Run the layout check script against it, passing every route the work added or changed, detail, settings, legal, and error routes included. It captures each page one screen at a time at 1440, 2560, 390, and 320 CSS pixels and fails on the layout rules it can measure, which its `--help` lists, such as sideways scroll, targets under 24 by 24, and pages over the length budget. Fix every failure and run it again until it passes.
3. Open the captures and look at them, the widest and the narrowest of each page side by side. Fix what reads wrong to a person even when no number caught it: crowding, clipped or cramped content, a pair that stacked, an empty or unfinished region, a control that looks broken.
4. Use every action the task asked for in the served build: submit, filter, sort, select, copy, bulk actions, and status changes. Reload after a filter, sort, or selection and confirm the view comes back from its URL.
5. Report the pages checked, what failed and was fixed, and anything left for the user, with the numbers.
