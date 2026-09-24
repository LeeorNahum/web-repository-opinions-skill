---
name: "web-repository-opinions"
description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environment and deployment, auth and data ownership, media and jobs, billing, public interfaces, and product UI. When unsure whether it applies, load it."
metadata:
  author: "Leeor Nahum"
  version: "1.34.0"
---

# Web Repository Opinions

A web product is more than its Git repo. The real product is code plus database, backend functions, object storage, provider dashboards, environment variables, webhooks, scheduled jobs, deployed app settings, and DNS. Keep those layers explicit so the product can build, deploy, and ship without hidden coupling.

Build around the thing the user came to do. A product should feel like its core workflow, not a generic dashboard with feature panels attached.

These are opinionated defaults, not a single product spec. Apply what fits the repo. The named tools below are swappable defaults. The paradigms around them are not.

## Default Stack

Prefer these unless the product has a stronger reason not to. Swap the tool, keep the paradigm.

| Role | Default | Swap when |
| --- | --- | --- |
| Monorepo | Turborepo with pnpm workspaces | A single deployable with no shared packages |
| Rendered public or hybrid surface | Next.js App Router with TypeScript | Static-only site, or a non-React target |
| Private client SPA | Vite with TypeScript | Server rendering or framework routing is required |
| Protocol-only HTTP app | Hono with TypeScript | The runtime already provides an equally small standards-based router |
| Styling | Tailwind CSS, shadcn/ui, lucide-react | A design system already exists |
| App data and live sync | Convex | No realtime need, or an existing database |
| Auth | Clerk | Enterprise SSO requirements Clerk cannot meet |
| Billing | Stripe | A region or model Stripe does not serve |
| Heavy media bytes | Cloudflare R2 | Already standardized on S3 or another store |
| Hosting | Vercel | A surface Vercel cannot host well |
| Physical commerce | Shopify, headless through its Storefront API | The catalog already lives on another commerce platform |
| DNS | Cloudflare | Registrar lock-in |
| Transactional email | Resend | An existing transactional provider |
| Rich text | BlockNote or equivalent block JSON | Plain text or markdown is enough |
| LLM calls | Vercel AI SDK over a hosting-aware, swappable gateway (production model and provider pools are product-specific) | The product needs a different routing or provider path |

## Reference Loading

This skill's substance lives in its references. The map below only points to them, so consult the skill for decisions and not just implementation. Before acting on any topic, read every reference that could touch it, in full, including the ones that seem only adjacent, and read deeply rather than skim. Bias hard toward loading: if a reference might cover what you are about to plan, decide, name, review, or build, read it rather than guess. Loading more references, and reading each completely, is cheap. Acting on a topic blind, or on a half-read reference, is not. Re-read the owning reference whenever a decision in its area comes back up.

Architecture:

- Read [references/stack.md](references/stack.md) when choosing or swapping tech building blocks.
- Read [AI model routing guidance](references/ai-model-routing.md) when a product calls LLMs, chooses production models or providers, designs model fallback, or accounts for model cost.
- Read [references/monorepo-layout.md](references/monorepo-layout.md) when creating or reorganizing apps and packages.
- Read [references/naming.md](references/naming.md) when naming folders, packages, slugs, surfaces, or workspace imports.
- Read [references/modularity.md](references/modularity.md) when designing how systems connect, naming integration boundaries, or keeping flows swappable.

Rendering and feel:

- Read [references/rendering.md](references/rendering.md) when choosing server rendering, static generation, or client rendering for a surface.
- Read [references/spa-feel.md](references/spa-feel.md) when making a signed-in app feel app-like while keeping stable URLs.
- Read [references/loading-states.md](references/loading-states.md) when designing skeletons, boot sequences, splash screens, or a dispatcher route that forwards into the product.

Surfaces:

- Read [references/marketing-site.md](references/marketing-site.md) when building the public site.
- Read [references/physical-commerce.md](references/physical-commerce.md) when a product sells physical goods, connects a commerce platform, or is asked to build inside a commerce platform's theme system.
- Read [references/app-surface.md](references/app-surface.md) when building the signed-in product.
- Read [references/seo.md](references/seo.md) when handling SEO for public pages.
- Read [references/public-discovery.md](references/public-discovery.md) when exposing public pages to crawlers, sitemaps, scrapers, and no-JavaScript verification.
- Read [references/legal-pages.md](references/legal-pages.md) when adding privacy, terms, or other trust pages required by providers.
- Read [references/contact-email.md](references/contact-email.md) when a page, manifest, or profile needs a contact address, or before any personal mailbox would appear on a public surface.
- Read [references/domain-mail.md](references/domain-mail.md) when setting up email for a domain: routing an alias to a monitored inbox, filtering routed mail, or sending and replying as the alias.
- Read [references/test-identities.md](references/test-identities.md) when creating or verifying an account that is not a person: for automated testing, for a store or platform reviewer, or for provider administration.
- Read [references/social-metadata.md](references/social-metadata.md) when building or reviewing any page a person can open without signing in, so it ships its favicon and the link preview card a pasted URL expands into.
- Read [references/badges.md](references/badges.md) when a public resource should appear in a README or other Markdown as a badge, a small image with a link behind it, or when offering copyable snippets beside a share link.

Identity and URLs:

- Read [references/routing.md](references/routing.md) when designing route paths.
- Read [references/query-state.md](references/query-state.md) when URL-addressing search, filters, sorting, views, pagination, or explicitly selected defaults.
- Read [references/ids.md](references/ids.md) when choosing URL identifiers for resources.
- Read [references/domains.md](references/domains.md) when laying out apex, subdomains, and the canonical host.
- Read [references/origins.md](references/origins.md) when generating links or callbacks across apps and stages.
- Read [references/http-apis.md](references/http-apis.md) when designing public HTTP APIs, OpenAPI contracts, protocol subdomains, CORS, caching, rate limits, or API-first clients.
- Read [references/agent-skills.md](references/agent-skills.md) when publishing workflow instructions for agents on top of a product interface.
- Read [references/agent-plugins.md](references/agent-plugins.md) when packaging skills and protocol connections for one or more agent hosts, or testing discovery and update pickup.
- Read [references/model-context-protocol.md](references/model-context-protocol.md) when building or versioning an MCP server, choosing its transport posture, designing its tool catalog, or setting up its authorization.
- Read [references/agent-tool-design.md](references/agent-tool-design.md) when defining tool names, schemas, annotations, identities, batch results, or mutation outcomes for any agent-facing interface.

Runtime and environment:

- Read [references/environment.md](references/environment.md) when creating, auditing, repairing, or filling env files, deciding which store holds a value, or keeping provider env separated by stage.
- Read [references/branches.md](references/branches.md) when mapping branches to deployment stages and provider credential tiers.
- Read [references/deployment.md](references/deployment.md) when configuring which branches deploy and how hosting is wired. Use the [deployment configuration asset](assets/vercel.json) when applying its branch-gating defaults.
- Read [references/continuous-integration.md](references/continuous-integration.md) when adding verification workflows, release automation, or checks required before promotion, or deciding which branches trigger artifact-building workflows.
- Read [references/dns.md](references/dns.md) when creating DNS records, proxy settings, or record comments.

Auth and data:

- Read [references/auth.md](references/auth.md) when wiring authentication and social sign-in posture.
- Read [references/workspace-tenancy.md](references/workspace-tenancy.md) when backing workspaces with the auth provider's organizations, shaping the home workspace, selecting a workspace over OAuth, or migrating existing workspaces onto organizations.
- Read [references/bootstrap.md](references/bootstrap.md) when ensuring user, workspace, and membership exist on authenticated entry.
- Read [references/data-model.md](references/data-model.md) when modeling entities, names, and value precedence.
- Read [references/source-of-truth.md](references/source-of-truth.md) when deciding which system owns which fact.
- Read [references/live-data.md](references/live-data.md) when wiring a reactive backend so the UI updates live.
- Read [references/search-indexing.md](references/search-indexing.md) when defining searchable fields, indexing fetched data, or running search migrations.
- Read [references/external-sources.md](references/external-sources.md) when importing, canonicalizing, checking, or recovering provider-owned resources.
- Read [references/integration-onboarding.md](references/integration-onboarding.md) when a user connects their own external system through the product UI.

Media and jobs:

- Read [references/object-storage.md](references/object-storage.md) when storing large files or deciding how stored bytes are delivered publicly.
- Read [references/uploads.md](references/uploads.md) when moving bytes from the browser to storage.
- Read [references/background-jobs.md](references/background-jobs.md) when running provider-backed or long-running work.
- Read [references/bulk-actions.md](references/bulk-actions.md) when one user action processes multiple independent items or supports partial success.
- Read [references/data-deletion.md](references/data-deletion.md) when one deletion operation must remove a dependent data graph across bounded steps.
- Read [references/quota.md](references/quota.md) when charging usage against limits.
- Read [references/abuse-resistance.md](references/abuse-resistance.md) when sizing internal quota ceilings, hardening upload or archive ingestion, or setting rate limiting posture.
- Read [references/failure-and-retries.md](references/failure-and-retries.md) when handling failed work and retry behavior.

Money and admin:

- Read [references/billing.md](references/billing.md) when implementing plans, subscriptions, and usage limits.
- Read [references/admin.md](references/admin.md) when adding internal admin surfaces and gates.

Frontend and UI:

- Read [references/responsive-layout.md](references/responsive-layout.md) when building or reviewing any layout across viewports, or when anything depends on display scale, DPI, or `devicePixelRatio`.
- Read [references/font-loading.md](references/font-loading.md) when choosing or loading fonts.
- Read [references/product-ux.md](references/product-ux.md) when shaping the primary path, states, and product-native language.
- Read [references/path-display.md](references/path-display.md) when showing file paths, directory listings, breadcrumbs, or a browsable tree's root.
- Read [references/interaction-feedback.md](references/interaction-feedback.md) when coordinating action states, selection surfaces, bulk feedback, or global search shortcuts.
- Read [references/user-facing-errors.md](references/user-facing-errors.md) when presenting failures from providers, frameworks, backend functions, validation, or unexpected exceptions.
- Read [references/design-tokens.md](references/design-tokens.md) when defining a design token layer, or when a surface leaves a large flat region of one color, which is where the product's ambient texture belongs.

Operating philosophy:

- Read [references/provider-setup.md](references/provider-setup.md) when onboarding providers or standing up a stage, deciding the order providers are wired, or configuring OAuth, webhooks, CORS, or allowed origins.
- Read [references/runtime-truth.md](references/runtime-truth.md) when deciding whether a change is actually complete.
- Read [references/promotion.md](references/promotion.md) when promoting work between deployment stages.
- Read [references/definition-of-done.md](references/definition-of-done.md) before implementing or reviewing a shippable feature. Use its verification categories to identify every other reference the work must load.
- Read [references/versioning.md](references/versioning.md) when bumping versions or keeping version mentions in sync.
- Read [references/cleanup.md](references/cleanup.md) when removing dead flows, stale docs, or temporary artifacts.

## Core Non-Negotiables

- The product feels like its core object first. Secondary features attach to it.
- Every view is URL-addressable so any state can be linked, shared, and restored.
- One canonical route model per concept. Do not keep long and short versions alive at once.
- Short, stable, non-sensitive IDs in private URLs. Never slugs for private, renameable objects.
- Split the public site from the signed-in app by audience and runtime posture.
- Name and isolate integrations by role so any single system can be swapped without rewriting callers.
- Build product capabilities with product-shaped inputs and outputs so UI, API, MCP, jobs, and webhooks can compose them without owning their rules.
- Enforce authorization once at the boundary every client crosses, capability-granular.
- Heavy bytes live in object storage. The database owns metadata and live state.
- A reactive backend is wired end to end so the UI updates live, not by manual refetch.
- One durable owner per fact. User-edited values outrank generated values, and generated values outrank defaults.
- Compatibility requires an explicit supported contract. Current intended behavior replaces unreleased mistakes.
- Env holds secrets and true environment variance. Product decisions live in code.
- Same env key names across stages. Values change by store, not the key.
- Branches are deployment roles: `dev` is local, `preview` is hosted staging on dev resources, `main` is production.
- Charge quota before expensive work. Expensive jobs retry only on user action. Failed states must be actionable.
- User-facing failures use product-owned copy. Raw exception, provider, framework, request, and stack details stay internal.
- A change is done when the runtime it depends on is true, not when TypeScript compiles.

## Web Repository Audit

When invoked to audit a web repo:

1. Classify public versus signed-in surfaces, whether their rendering posture matches, and whether every publicly reachable page ships a favicon and a correct link preview card.
2. Inspect URL IDs, route paths, query-state restoration, and link stability across reorganization.
3. Check auth bootstrap, workspace creation, and permission-gated UI that hides unavailable actions.
4. Confirm per-runtime env contracts, no root env clutter, and same key names across stages.
5. Check ownership boundaries, external sources, search scope, media storage, and bounded data work.
6. Verify user-facing failures, partial results, feedback, and responsive interaction states remain coherent.
7. Confirm branch-to-stage mapping, deploy gating, migrations, webhooks, DNS records, and provider setup are documented near the runtime contract.
8. Report mismatches by category and file area, never by leaking secret values or one-off product names.

Several references end with an "Ask before" line for their riskiest changes, such as production domains, DNS, credentials, billing mode, public sharing, and provider resources. Honor those where the topic lives.
