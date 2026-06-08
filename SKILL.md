---
name: web-repository-opinions
description: Opinionated defaults for building TypeScript web products and any repo built on web technology, covering monorepo layout, rendering, surfaces, routing, IDs, domains, origins, env contracts, branches, deployment, DNS, auth, data ownership, media, jobs, billing, admin, responsive layout, fonts, product UX, and release operating philosophy. Use when planning, scaffolding, auditing, naming, or implementing a web app, marketing site, signed-in app, SaaS, extension, desktop, or mobile surface built with HTML, CSS, JS, or TS.
metadata:
  author: Leeor Nahum
  version: "1.2.1"
---

# Web Repository Opinions

A web product is more than its Git repo. The real product is code plus database, backend functions, object storage, provider dashboards, environment variables, webhooks, scheduled jobs, deployed app settings, and DNS. Keep those layers explicit so the product can build, deploy, and ship without hidden coupling.

Build around the thing the user came to do. A product should feel like its core workflow, not a generic dashboard with feature panels attached.

These are opinionated defaults, not a single product spec. Apply what fits the repo. The named tools below are swappable defaults; the paradigms around them are not.

## Default Stack

Prefer these unless the product has a stronger reason not to. Swap the tool, keep the paradigm.

- Monorepo: Turborepo with pnpm workspaces
- Framework: Next.js App Router with TypeScript
- Styling: Tailwind CSS, shadcn/ui, lucide-react
- App data and live sync: Convex
- Auth: Clerk
- Billing: Stripe
- Heavy media bytes: Cloudflare R2
- Hosting: Vercel
- DNS: Cloudflare
- Transactional email: Resend
- Rich text: BlockNote or equivalent block JSON
- LLM calls: Vercel AI SDK (model choice is product-specific, not a global default)

## Reference Loading

Always read every reference relevant to the task before acting on its topic. Bias toward loading: if a reference covers what you are about to do, read it rather than guessing. Loading more references is cheap; acting on a topic blind is not.

Architecture:

- Read `references/stack.md` when choosing or swapping tech building blocks.
- Read `references/monorepo-layout.md` when creating or reorganizing apps and packages.
- Read `references/naming.md` when naming folders, packages, slugs, surfaces, or workspace imports.
- Read `references/modularity.md` when designing how systems connect, naming integration boundaries, or keeping flows swappable.

Rendering and feel:

- Read `references/rendering.md` when choosing server rendering, static generation, or client rendering for a surface.
- Read `references/spa-feel.md` when making a signed-in app feel app-like while keeping stable URLs.

Surfaces:

- Read `references/marketing-site.md` when building the public site.
- Read `references/app-surface.md` when building the signed-in product.
- Read `references/seo.md` when handling SEO for public pages.
- Read `references/legal-pages.md` when adding privacy, terms, or other trust pages required by providers.

Identity and URLs:

- Read `references/routing.md` when designing route paths.
- Read `references/ids.md` when choosing URL identifiers for resources.
- Read `references/domains.md` when laying out apex, subdomains, and the canonical host.
- Read `references/origins.md` when generating links or callbacks across apps and stages.

Runtime and environment:

- Read `references/environment.md` when creating, auditing, or repairing env files and provider env separation.
- Read `references/branches.md` when mapping branches to deployment stages and provider credential tiers.
- Read `references/deployment.md` when configuring which branches deploy and how hosting is wired.
- Read `references/dns.md` when creating DNS records, proxy settings, or record comments.

Auth and data:

- Read `references/auth.md` when wiring authentication and social sign-in posture.
- Read `references/bootstrap.md` when ensuring user, workspace, and membership exist on authenticated entry.
- Read `references/data-model.md` when modeling entities, names, and value precedence.
- Read `references/source-of-truth.md` when deciding which system owns which fact.
- Read `references/live-data.md` when wiring a reactive backend so the UI updates live.

Media and jobs:

- Read `references/object-storage.md` when storing large files.
- Read `references/uploads.md` when moving bytes from the browser to storage.
- Read `references/background-jobs.md` when running provider-backed or long-running work.
- Read `references/quota.md` when charging usage against limits.
- Read `references/failure-and-retries.md` when handling failed work and retry behavior.

Money and admin:

- Read `references/billing.md` when implementing plans, subscriptions, and usage limits.
- Read `references/admin.md` when adding internal admin surfaces and gates.

Frontend and UI:

- Read `references/responsive-layout.md` when building or reviewing any layout across viewports.
- Read `references/font-loading.md` when choosing or loading fonts.
- Read `references/product-ux.md` when shaping the primary path, states, and product-native language.
- Read `references/design-tokens.md` when defining a design token layer.
- Read `references/social-metadata.md` when adding icons, favicons, and social embed metadata.

Operating philosophy:

- Read `references/provider-setup.md` when configuring OAuth, webhooks, CORS, or allowed origins.
- Read `references/runtime-truth.md` when deciding whether a change is actually complete.
- Read `references/promotion.md` when promoting work between deployment stages.
- Read `references/definition-of-done.md` when judging whether a feature is shippable.
- Read `references/versioning.md` when bumping versions or keeping version mentions in sync.
- Read `references/cleanup.md` when removing dead flows, stale docs, or temporary artifacts.

## Core Non-Negotiables

- The product feels like its core object first; secondary features attach to it.
- Every view is URL-addressable so any state can be linked, shared, and restored.
- One canonical route model per concept. Do not keep long and short versions alive at once.
- Short, stable, non-sensitive IDs in private URLs. Never slugs for private, renameable objects.
- Split the public site from the signed-in app by audience and runtime posture.
- Name and isolate integrations by role so any single system can be swapped without rewriting callers.
- Heavy bytes live in object storage. The database owns metadata and live state.
- A reactive backend is wired end to end so the UI updates live, not by manual refetch.
- One durable owner per fact. User-edited values outrank generated values; generated outrank defaults.
- Env holds secrets and true environment variance. Product decisions live in code.
- Same env key names across stages. Values change by store, not the key.
- Branches are deployment roles: `dev` is local, `preview` is hosted staging on dev resources, `main` is production.
- Charge quota before expensive work. Expensive jobs retry only on user action. Failed states must be actionable.
- A change is done when the runtime it depends on is true, not when TypeScript compiles.

## Web Repository Audit

When invoked to audit a web repo:

1. Classify public versus signed-in surfaces and whether their rendering posture matches.
2. Inspect URL ID strategy, route paths, and link stability across reorganization.
3. Check auth bootstrap, workspace creation, and permission-gated UI that hides unavailable actions.
4. Confirm per-runtime env contracts, no root env clutter, and same key names across stages.
5. Check the media versus database split, direct uploads, and coarse user-facing job states.
6. Verify no raw provider errors surface, no auto-retry on expensive jobs, and no UI freeze on upload or stop.
7. Confirm branch-to-stage mapping, deploy gating, DNS records, and provider setup are documented near the runtime contract.
8. Report mismatches by category and file area, never by leaking secret values or one-off product names.

Several references end with an "Ask before" line for their riskiest changes, such as production domains, DNS, credentials, billing mode, public sharing, and provider resources. Honor those where the topic lives.
