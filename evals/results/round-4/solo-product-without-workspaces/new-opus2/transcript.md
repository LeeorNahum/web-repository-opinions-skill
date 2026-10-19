**Prompt:** Plan the auth setup, data ownership, and URL structure for Marrow Journal's signed-in app, and write it to docs/architecture.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus2/work\" && git ls-files && cat docs/brief.md && cat package.json 2>/dev/null"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5093 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus2/work/.claude/skills/web-repository-opinions/references\" && for f in auth workspace-tenancy bootstrap data-model source-of-truth; do echo \"=== $f\"; cat $f.md; done"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus2/work/.claude/skills/web-repository-opinions/references\" && for f in routing ids query-state app-surface domains origins; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === auth # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already h [... 24463 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus2/work/.claude/skills/web-repository-opinions/references\" && for f in billing search-indexing data-deletion spa-feel monorepo-layout naming admin live-data; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === routing # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the [... 24479 more characters]

> Result: === billing # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed  [... 15925 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus2/work/.claude/skills/web-repository-opinions/references\" && for f in rendering stack legal-pages product-ux loading-states; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === rendering # Rendering  Choose a rendering posture per surface based on who reads it and whether search engines matter.  - Public pages render on the server or generate statically. They must be crawlable, fast on first paint, and shareable without JavaScript. - Signed-in pages render on the client behind auth. They favor live data, fast transitions, and persistent state over crawlability. [... 13314 more characters]

**Tool call `Write`:** `<run>\builds\4-solo-product-without-workspaces-new-opus2\work\docs\architecture.md`

````text
# Marrow Journal architecture: auth, data ownership, URLs

Status: draft, written 2026-10-19 while the owner was away. `docs/brief.md` wins over this file. If they disagree, fix this file. Every call made here without the owner is listed under [Assumptions](#assumptions-to-confirm) and [Open questions](#open-questions).

## The shape in one paragraph

Marrow Journal belongs to one person per account. The brief rules out sharing, teams, and collaborators for good, so the product has **no workspace or organization layer**. Every row belongs to the user account directly, no route has a tenancy segment, and the authorization rule is always the same: the caller must be the owner. The core object is the **entry**, and every surface in the signed-in app is a view of the caller's own entries: today, calendar, one entry, search. Settings is attached to the account.

## Surfaces and layout

| Surface | Path in repo | Tool | Origin (prod) | Rendering |
| --- | --- | --- | --- | --- |
| Public site | `apps/site` | Next.js App Router | `https://<domain>` (apex) | Static / server, crawlable |
| Signed-in app | `apps/app` | Vite + React SPA | `https://app.<domain>` | Client, behind auth |
| Backend | `packages/backend` (`convex/` inside) | Convex | Convex deployment | Reactive queries |
| Domain rules | `packages/domain` | Plain TS | n/a | n/a |
| Tooling config | `packages/config` | n/a | n/a | n/a |

- Staging: `preview.<domain>` and `preview.app.<domain>` (from the `preview` branch). `main` is production, and `dev` is local.
- Local ports: site `3000`, app `3001`.
- `packages/domain` owns route builders, the entity ID helper, query-state parsers, calendar-date logic, plan constants, capability names, and origin resolvers (`CANONICAL_SITE_ORIGIN`, `CANONICAL_APP_ORIGIN`, `resolveSiteOrigin()`, `resolveAppOrigin()`, `absoluteUrl()`).
- No `packages/ui` until there are real shared primitives.
- **The public site does not load the auth SDK.** It links to `app.<domain>/auth` for sign-in, so a privacy-first marketing page makes no auth-provider requests. The site serves `/privacy` and `/terms`, which Google OAuth verification and the subscription checkout both need.

## Auth

### Provider and methods

- **Clerk**, one application per provider stage: a development instance for local and preview, and a production instance for `main`.
- **Personal accounts only. Clerk Organizations stay disabled.** The brief rules out shared ownership permanently, so no organization object is created, required, or synced.
- Sign-in methods:
  - **Google**, with custom OAuth credentials per stage and the account-selector prompt turned on, so a person can switch Google accounts after signing out.
  - **Apple**, with custom credentials per stage. Assumed: a journal's audience is heavily on iPhone.
  - **Email** as an enabled identifier, signing in with a **one-time email code**. Passwords are off (assumed). The product never stores or verifies a credential itself.
  - Clerk links a social sign-in and a verified email that match to one account.
- At sign-up, the person agrees to the linked `/terms` and `/privacy` through Clerk's own consent step.

### Routes

- **One auth route: `/auth`** on the app origin, rendering Clerk's combined sign-in-or-up component. There are no separate `/sign-in`, `/sign-up`, or callback paths, and no env keys for auth paths.
- **Return destination:** whenever an app route meets a signed-out visitor, it sends them to `/auth?next=<path+query>`. `next` comes from the interrupted request in one place, the app's auth guard. It is honored only when it is a same-origin relative path (starts with a single `/`, not `//`, and has no scheme). Anything else falls back to `/`. Test this signed out from `/`, `/entries/<id>`, `/search?q=…`, and `/settings/billing`.
- A signed-in visitor who opens `/auth` goes to `next`, or to `/`, by history replace.

### Backend identity

- Convex validates the Clerk JWT through Convex's Clerk integration. The JWT template name (`convex`) is a code convention, not env. Before writing the issuer and audience checks, decode a real token from each instance and check its claims. Enforce the issuer every time. Enforce the audience only if the token actually carries one, and say why in the code.
- The app user row stores the Clerk **subject** (`authSubject`). Webhooks and cleanup always resolve by subject, never by email.

### Bootstrap on every authenticated entry

Every app route can be opened cold, so the app shell runs this order before reading data:

1. Wait for the Clerk session and the authenticated Convex connection.
2. Call `users.ensureCurrent`, an idempotent mutation that finds or creates the user row by subject. It also records the browser time zone the first time.
3. Only then subscribe to entry queries.

The Clerk `user.created` webhook is an optimization and never the only way the row gets created. If a first sign-in ever needs a refresh, the ordering is wrong.

### One authorization gate

- Every public Convex function is built from a small set of wrappers in `packages/backend/convex/auth/`: `ownerQuery`, `ownerMutation`, `ownerAction`. The wrapper resolves the verified identity to the app user and **fails closed** when either is missing. Exporting raw `query`/`mutation` for client-callable functions is not allowed. A lint rule backs this up, but the wrappers are the real boundary.
- **No function takes a `userId` argument.** The owner always comes from the verified identity.
- Entry access goes through one helper, `getOwnedEntry(ctx, user, id)`. An entry that does not exist and an entry owned by someone else both return the same **"Entry not found"**, so the app never reveals that another person's ID exists.
- Capabilities are named in `packages/domain` even though there is a single role (owner): `entries.read`, `entries.write`, `entries.delete`, `entries.export`, `account.manage`, `billing.manage`. A future scoped token, such as an export token, would intersect with these. Today the owner holds all of them.
- What a plan sells is checked separately, by the billing entitlement (see below), not by this gate.
- Background jobs (purge, account deletion, export) carry the owner's user ID. Each transaction re-checks that the user row still exists and is not closing before it acts. A signed export download link re-checks the owner just before it is issued.

### Account deletion and closure

- Started from `/settings/data`, after a product-owned confirmation dialog (never `window.confirm`). The person is offered an export first.
- Flow: mark the user `closingAt`, so all reads fail closed immediately. A bounded, resumable job then removes entries, search state, and billing linkage in batches. It cancels the Stripe subscription, deletes the Clerk user, and deletes the user row last.
- A closure record (a one-way hash of the subject plus `closedAt`, and an `origin` argument that has no default) blocks lingering tokens from recreating the account. When the product closed the account, the record has no expiry until Clerk confirms the deletion. When Clerk deleted the identity, it becomes a tombstone that expires after the longest credential lifetime. Expiry scans cover only records that have an expiry field.
- The Clerk `user.deleted` webhook: verify the signature, dedupe by event ID, treat redelivery as success, and enqueue the same bounded cleanup instead of deleting inside the request.

## Data ownership

### Who owns which fact

| Fact | Owner |
| --- | --- |
| Login identity, sign-in methods, sessions | Clerk |
| User row, settings, entries, search text | Convex |
| Subscription and payment truth | Stripe (Convex keeps a last-known mirror, updated by webhooks) |
| Plan names, entitlements, limits, capability names, routes | `packages/domain` (code) |
| Origins, keys, secrets per stage | Hosting/provider env stores |

### Tables (Convex)

```text
users
  id               12-char Base58, app-facing          (not used in URLs today)
  authSubject      Clerk subject, unique index
  timeZone         IANA zone; user-edited outranks browser-detected
  timeZoneSource   "user" | "detected"
  weekStart        "monday" | "sunday" (default from locale)
  closingAt?       set when deletion starts
  createdAt

entries
  id               12-char Base58, unique index — the URL identity
  ownerId          -> users
  entryDate        "YYYY-MM-DD" calendar date in the owner's time zone at creation
  body             BlockNote block JSON (rich text)
  searchText       plain text derived from body by one builder
  createdAt, updatedAt
  deletedAt?       soft delete (see below)
  indexes:         by_owner_date (ownerId, entryDate), by_public_id (id)
  search index:    searchText, filterFields [ownerId, deletedAt]

billingAccounts   (one per user)
  userId, stripeCustomerId, status mirror, currentPeriodEnd, planKey, lastEventId

webhookEvents     (dedupe by provider event ID)
closures          (subject hash, closedAt, origin, expiresAt?)
```

- **One live entry per owner per calendar date** (assumed, see below). `entries.createForDate` checks `by_owner_date` inside its transaction and returns the existing entry if there is one, so two tabs racing still produce one entry.
- **"Today"** is computed from the user's `timeZone`. The server rejects dates in the future, allowing up to +14h of time-zone skew. When a person starts writing at 23:58, the entry belongs to the date they started on, because that date is fixed when the entry is created.
- `searchText` is built only by `buildEntrySearchText(body)`. Create, update, and any future migration all call it.
- Entity IDs come from one helper in `packages/domain` (12 chars, Base58, no prefix). Convex `_id` is never put in a URL.
- Edits autosave through a mutation with an optimistic update. Every open tab sees the change live through its subscription.

### Privacy posture (what "visible only to the writer" means in the system)

- Only the owner gate ever returns entry `body` or `searchText`. **No admin or support tool reads entry content.** A future admin surface sees only account, billing, and job metadata.
- Entry content never appears in logs, error reports, analytics events, or job payloads. Error reporting scrubs request bodies and function arguments for entry mutations.
- No third-party scripts or CDNs on the app. Fonts and the editor are served from the product's own origin.
- Entries are encrypted at rest by the providers, and the server can read them. That is what makes server-side search and account recovery possible. End-to-end encryption is a separate product decision (see open questions).
- Search covers full entry content, because searching your own journal is the feature. Every search is filtered by `ownerId` inside the backend, and deleted entries are excluded.

### Deletion of a single entry

Deleting an entry is a soft delete. It sets `deletedAt` and immediately removes the entry from today, the calendar, and search. The entry stays restorable from `/trash` for 30 days, and a scheduled bounded job hard-deletes it after that. Restoring an entry onto a date that now has a newer live entry is refused with a product message that links to the existing entry. Deleted entries count toward any storage allowance until they are purged.

### Billing

- Stripe has one customer per user and at most one active subscription per user, matching the brief's "one subscriber per account". Checkout uses Stripe Checkout, and management uses the Stripe Customer Portal, both opened from `/settings/billing`.
- Entitlement is **derived** at the gate from the mirrored subscription status plus the plan constants in code. It is never a flag stamped on entries.
- **Losing the paid plan never hides or deletes an entry.** Reading, search, export, and deletion always stay available. Only whatever the paid plan sells stops working, and the action that hits that limit shows a product-owned message.
- Stripe test mode on local and preview. Live mode only on `main`. Webhook: `POST /webhooks/billing` (Convex HTTP action), signature verified and deduped by event ID.

## URL structure (app origin)

All private routes sit at the top level. There is no tenancy segment, because there is no tenancy unit.

| Path | View | Notes |
| --- | --- | --- |
| `/auth` | Sign in or sign up | `?next=` is a validated relative return path |
| `/` | **Today (dispatcher)** | Resolves with history replace: to `/entries/<id>` when today's entry exists, otherwise to `/entries/new?date=<today>`. Not a page of its own. The "Today" nav item links here. |
| `/entries` | **Calendar** of the caller's entries | `?month=YYYY-MM`. Omitted means the current month. A current month the person explicitly picked stays in the URL. Month changes push history. |
| `/entries/new?date=YYYY-MM-DD` | Composer for one day | The first save creates the entry and replaces the URL with `/entries/<id>`. If that date already has an entry, it replaces to that entry. A future date, missing date, or invalid date replaces to `/`. Clicking an empty past day in the calendar opens this, for backfilling. |
| `/entries/<id>` | **One entry** (read and edit) | The single canonical URL for an entry, today's included. There is one view, so the entity URL is the view. Unknown or not-owned IDs show the "Entry not found" screen. |
| `/search?q=…` | Search across the caller's entries | `q` first. Typing replaces history after a debounce. Empty `q` is omitted. Results link to `/entries/<id>`. |
| `/trash` | Recently deleted entries | Restore, or delete permanently. Purged after 30 days. |
| `/settings` | Resolves (replace) to `/settings/journal` | |
| `/settings/journal` | Time zone, week start | |
| `/settings/account` | Sign-in methods and security | Product page that opens Clerk's `UserProfile` in **modal** mode, so Clerk's internal tabs never enter the URL contract |
| `/settings/billing` | Plan, checkout, portal | Stripe pages are external redirects that return here |
| `/settings/data` | Export, delete account | |

Rules applied:

- **One canonical URL per entry.** "Today" is a pointer to an entry, not a second address for it. Calendar cells, search results, and any future email reminder link to `/entries/<id>` (or to `/`, meaning "today, whatever that is").
- **IDs, not dates, identify an entry in the URL.** The date is a property of the entry and could become editable. The 12-char opaque ID stays stable, and it doesn't expose when someone wrote through a pasted link.
- Path segments are full words (`entries`, `search`, `settings`). There is no scaffolding to compress.
- Query state is parsed, validated, and serialized in `packages/domain` with contract tests. Unknown formats are rejected, not kept.
- Navigation stays client-side inside a persistent shell (nav plus the editor region), and each region has its own skeleton. Every view keeps its real URL.
- **No route makes an entry visible to anyone but its owner.** A copied link opened by someone else, signed in or not, gets "Entry not found" (after `/auth` if they are signed out). Public sharing will not be built (brief).

Public site origin (apex): `/`, `/pricing`, `/privacy`, `/terms`, `/security` (assumed useful for a product sold on privacy), and later `/help/...`. Cross-origin links (the site's "Sign in" and "Open app" buttons, the app's link to the terms) go through the origin resolvers.

## Webhooks and env (summary)

- Convex HTTP actions: `POST /webhooks/auth` (Clerk), `POST /webhooks/billing` (Stripe). Separate signing secrets per stage.
- Key names are the same on every stage; only the stored values differ:
  - `apps/app`: `VITE_CLERK_PUBLISHABLE_KEY`, `VITE_CONVEX_URL`, `VITE_SITE_ORIGIN` (override only).
  - `apps/site`: `NEXT_PUBLIC_APP_ORIGIN` (override only).
  - Convex: `CLERK_JWT_ISSUER_DOMAIN`, `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `APP_ORIGIN`.
- Routes, plan names, the JWT template name, the trash window, and the time-zone skew allowance are code constants, not env.

## Assumptions to confirm

1. **One entry per calendar day.** This keeps "today's entry" and the calendar simple. If several entries per day are wanted, the routes stay the same. Only the `/` resolver and the calendar cell rendering change, and the uniqueness check is dropped.
2. **Backfilling past days is allowed** from the calendar via `/entries/new?date=`. Future dates are not.
3. **An entry's day is fixed when it is created**, in the user's chosen time zone. Travelling does not move old entries.
4. **Sign-in methods: Google + Apple + email code, no passwords.** Apple needs an Apple Developer account.
5. **Soft delete with a 30-day `/trash`** rather than immediate permanent deletion.
6. **Rich text via BlockNote JSON.** Plain text or markdown would also fit, and the search builder hides the difference.
7. **No images or attachments in v1.** If added: private object storage (R2), keys per owner, short-lived signed URLs issued only after an owner check, bytes never in Convex.
8. **What the paid plan unlocks is undefined**, and so is whether a free tier exists. The architecture only fixes that downgrading never hides, locks, or deletes entries.
9. **App subdomain is `app.`** (it becomes `web.` if the domain is a `.app` TLD). The domain itself is unknown and written as `<domain>`.
10. **The marketing site does not load Clerk** and has no signed-in state.
11. **No admin surface in v1.** If one is added, it never reads entry content.

## Open questions

- **End-to-end encryption?** This is the biggest decision left. The product is sold on privacy, and with E2EE even the operator could not read entries. Trade-offs: search would move into the client (local index), a lost key would mean lost entries unless there is a recovery scheme, and server-side features over content would become impossible. This draft assumes no E2EE, with strict owner-only access and no operator access to content. Changing it later means migrating every stored entry, so it should be decided before launch.
- Product domain, and whether Convex webhook and backend URLs get custom domains (Convex needs a paid plan for that).
- Whether to also offer a data export format beyond JSON + Markdown (assumed for `/settings/data`).

Not done without the owner (per the "ask before" rules): no domains, DNS, OAuth apps, Clerk or Stripe instances, or billing settings were created or changed. Nothing is built yet. This is a plan only.

````

> Result: File created successfully at: <run>\builds\4-solo-product-without-workspaces-new-opus2\work\docs\architecture.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/architecture.md`. It's a document only: nothing is built, committed, or set up with any provider.

**Decisions I made:**
- **No workspace or organization layer.** The brief rules out sharing, teams and collaborators for good, so all data belongs to the user account and private URLs have no tenancy segment. Clerk's Organizations feature stays off.
- **Auth:** Clerk is the sign-in provider, with a single `/auth` page on the app's subdomain. Sign-in options are Google, Apple and an emailed one-time code, with no passwords. After signing in, a person returns to the page they were trying to open; that return path is checked to be on the same site.
- **Account setup on every sign-in:** the user's record is created or found each time they enter the app, so a missed or late signup webhook can't break first sign-in.
- **One access check:** every backend function goes through one wrapper that checks the caller owns the data. No function accepts a user ID from the client. Someone else's entry and a missing entry both show the same "Entry not found".
- **Who owns what:**
  - Clerk owns identity.
  - Convex (the backend) owns the user record, entries and search text.
  - Stripe owns subscription truth; Convex keeps a copy updated by webhooks.
  - Plan rules live in code.
- **Privacy:** no admin or support tool ever reads entry content, and entry text never goes into logs, error reports or analytics. Losing the paid plan never hides or deletes an entry.
- **URLs:**
  - `/` always sends you to today's entry, or to a blank one if you haven't written today.
  - `/entries` is the calendar.
  - Each entry has exactly one address, `/entries/<id>`, using a short random ID rather than the date.
  - `/entries/new?date=…` writes for a given day.
  - Search is `/search?q=…`, deleted entries are in `/trash`, and settings are under `/settings/…` (journal, account, billing, data).

**Assumptions to confirm (all listed in the doc):**
- One entry per calendar day, with writing for past days allowed but not future ones.
- An entry's date is fixed when it's created, in the person's chosen time zone.
- Google, Apple and email code are the sign-in methods. Apple needs an Apple Developer account.
- Deleted entries can be restored for 30 days.
- Rich text editing (BlockNote), and no images or attachments in v1.
- The marketing site doesn't load Clerk at all.
- The app lives on `app.<domain>`. I don't know the domain, so it's a placeholder.
- No admin area in v1.

**Decisions only you can make:**
- **End-to-end encryption.** This is the biggest one. It fits the privacy pitch, because even you couldn't read entries. But search would have to run on the user's device, and a lost key could mean lost entries. The plan assumes no end-to-end encryption, with strict owner-only access instead. It's much harder to change after launch.
- **What the paid plan unlocks, and whether there's a free tier.** The brief doesn't say.
- **The product domain.**

**Session ended:** success, 9 turns, 163781 ms
