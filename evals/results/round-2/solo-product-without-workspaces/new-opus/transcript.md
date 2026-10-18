**Prompt:** Plan the auth setup, data ownership, and URL structure for Marrow Journal's signed-in app, and write it to docs/architecture.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-new-opus/work\" && git ls-files && cat docs/brief.md && cat package.json 2>/dev/null"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5093 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && for f in auth workspace-tenancy bootstrap data-model source-of-truth; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === auth # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already h [... 24390 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && for f in routing ids query-state app-surface domains origins spa-feel; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === routing # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the [... 24197 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && for f in billing data-deletion search-indexing monorepo-layout naming rendering stack live-data legal-pages; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === billing # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed  [... 21365 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && for f in admin loading-states product-ux environment provider-setup test-identities; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === admin # Admin  Admin is a gated internal surface, not a hidden corner of the user app. Gate it explicitly by an admin role checked on the server, never by an unlinked route or client-only check.  Keep the operator and admin allowlist the server checks against in versioned code, reviewed in code review. Who counts as internal staff is a product decision, so it lives with the code alongside  [... 22732 more characters]

**Tool call `Write`:** `<run>\builds\2-solo-product-without-workspaces-new-opus\work\docs\architecture.md`

````text
# Marrow Journal: Signed-In App Architecture

`docs/brief.md` wins over this document. If they disagree, the brief is right and this file needs fixing. This document covers the signed-in app's auth setup, data ownership, and URL structure. Calls not settled by the brief are marked **Assumed** and collected in [Assumptions and open questions](#assumptions-and-open-questions).

## Constraints from the brief

- Entries are visible only to their author. No sharing, teams, or collaborators, now or later.
- Managed auth with social sign-in and email.
- Subscription billing, one subscriber per account.
- App surfaces: today's entry, a calendar of past entries, an entry page, search, settings.

The "never shared" rule shapes most of the decisions below. There is no tenancy unit, so every fact belongs to one user account.

## Stack and layout

| Role | Choice |
| --- | --- |
| Auth | Clerk |
| App data, live sync, search, jobs | Convex |
| Billing | Stripe (Checkout and Customer Portal, hosted) |
| Signed-in app | Vite + React SPA, client-rendered |
| Public site | Next.js App Router, server-rendered or static |
| Hosting | Vercel |
| Entry body | BlockNote block JSON |

```text
apps/
  site/        public marketing, pricing, /privacy, /terms
  app/         signed-in journal
packages/
  backend/     Convex schema, functions, HTTP webhooks, jobs, provider adapters
  domain/      route builders, query-state parsers, entity ID helper, plan constants, origins, limits
  config/      shared TypeScript and tooling config
```

Folders and modules are named for their role, not the vendor: `auth`, `billing`, `search`, `origins`. Never `clerk` or `stripe`.

The app is client-rendered behind auth. Server rendering would add nothing here: there is no anonymous visitor, and private data shouldn't pass through a render server.

## Domains and origins

| Surface | Production | Staging (`preview` branch) | Local |
| --- | --- | --- | --- |
| Site | `<apex>` | `preview.<apex>` | `http://localhost:3000` |
| App | `app.<apex>` | `preview.app.<apex>` | `http://localhost:3001` |

- **Assumed:** the production domain isn't decided yet, so it appears as `<apex>`. It becomes the `CANONICAL_SITE_ORIGIN` and `CANONICAL_APP_ORIGIN` constants in `packages/domain/origins`.
- The site never signs anyone in. Its "Sign in" and "Start writing" buttons link to the app's `/auth` through `resolveAppOrigin()`, never a hardcoded host.
- No `www`. Any alias domain gets a path-preserving redirect at the edge.
- Branches: `dev` is local, `preview` is hosted staging on dev/test provider tiers, `main` is production. The repo's current default branch is `master`, so it needs to be renamed or mapped when deployment is wired.

## Auth setup

### Provider configuration (Clerk)

- **One Clerk application with two instances.** Development serves local and `preview`. Production serves `main`. Each instance has its own custom Google OAuth credentials, so redirect URIs never cross stages.
- **Sign-in methods. Assumed:** Google for social sign-in, with the account-selector prompt on. This requires custom OAuth credentials, even in development. Email is an identifier with a **one-time email code** and no password. Apple sign-in can be added later and needs no architectural change.
- **Organizations off entirely.** The product has no workspaces, so Clerk's personal-account mode is the only mode. There is no organization switcher, organization role, or organization claim anywhere.
- **Session JWT for Convex.** Clerk's Convex JWT template is named `convex`. That name is a code constant, not env. Convex's `auth.config.ts` trusts the Clerk issuer domain for the stage. Before writing the check, decode a real token from each instance and confirm which claims are actually minted (`iss`, `sub`, `aud`). Always enforce the issuer. Enforce the audience only because the template mints `aud: "convex"`, and say so in a comment.

### The one auth route

- `/auth` on the app origin hosts Clerk's combined sign-in-or-up component. There are no separate `/sign-in`, `/sign-up`, or callback routes, and no env keys for auth paths.
- **Return to where they were.** Any signed-out request for a private route renders the auth gate in place and carries the requested path as `/auth?return=/entries/7Hq2…`. The return value must be a same-origin relative path (it starts with a single `/`, has no scheme or host, and isn't `//`). Otherwise the user goes to `/`. One helper in `packages/domain` builds and validates this. Test it signed out from every route below.
- Terms agreement uses Clerk's own sign-up consent checkbox, linked to `<apex>/terms` and `<apex>/privacy`. Both pages must exist on the site before the Google OAuth consent screen can be verified.

### Bootstrap on every authenticated entry

Every route in the app goes through the same sequence, in this order:

1. Clerk reports a session, and the Convex client is authenticated through `ConvexProviderWithClerk`.
2. The `account.ensure` mutation finds the app user by Clerk subject or creates it. It refuses if a closure tombstone exists for that subject (see [Account deletion](#account-deletion)). On creation it seeds `timeZone` from the browser.
3. Only then do entry queries subscribe.

The Clerk `user.created` webhook is not needed to create anything. If a first sign-in ever needs a refresh to show data, the order above is wrong.

### The authorization gate

All reads and writes go through Convex functions, and every public Convex function is built from one constructor in `packages/backend/convex/auth/`:

- `ownerQuery` and `ownerMutation` resolve the verified identity to the app user. They fail closed with one product error when there's no identity, no user row, or a tombstoned subject, and they pass `viewer` to the handler.
- Entry access goes through one loader, `loadOwnedEntry(ctx, viewer, id)`. It returns the entry only if `entry.ownerId === viewer._id`. A missing entry and someone else's entry return the **same** "entry not found" result, so the response never confirms that an ID exists.
- Capabilities are named so they stay checkable even with one role: `entry.read`, `entry.write`, `entry.delete`, `account.manage`, `billing.manage`. Any signed-in owner holds all of them over their own data and no one else's. An unknown capability fails closed.
- Plain `query` and `mutation` aren't exported from the module the app imports. The only exceptions are webhook HTTP actions and internal functions, which can't be called from a client.
- Scheduled jobs (deletion, purges) carry the owner's user ID and re-check that the owner exists in every transaction they run. They never rely on a check made when the job was scheduled.

### No reader besides the author

The positioning is "only you can see it", so the architecture adds these rules:

- **No admin or support capability reads entry content.** An admin surface, if one is ever built, sees account, billing, and job metadata only. The admin allowlist lives in code.
- Entry text never goes to Clerk, Stripe, analytics, or error reporting. Error reports and logs carry entry IDs, never bodies or titles.
- The signed-in app loads no third-party scripts at runtime. Every dependency, including the editor, is served from the app origin.
- `document.title` never contains entry text, because browser history and tab sync would store it. Entry pages are titled by date, for example "October 18, 2026 · Marrow Journal".
- Every app response carries `noindex` and gets no link-preview metadata beyond the generic app card.

## Data ownership

### Who owns which fact

| Fact | Owner | Copy in Convex |
| --- | --- | --- |
| Login identity, email, social links | Clerk | Only `authSubject`. Email is not copied. |
| Subscription and payment status | Stripe | Last-known mirror on `billingAccounts`, updated by webhooks. Stripe is the authority. |
| Entries, preferences, deletion jobs | Convex | Owner |
| Plan names, entitlements, entry size limit | `packages/domain` | None. These are code constants. |
| Today's date for a user | Derived from `users.timeZone` and the clock | Never stored |

### Tables

Every row that holds user data has an `ownerId`, and every index starts with it.

```text
users
  authSubject      Clerk subject (stable), unique index
  timeZone         IANA zone, user-editable in preferences
  weekStartsOn     preference
  createdAt

entries
  id               12-char Base58 public ID (URL identity), unique index
  ownerId          -> users
  day              "YYYY-MM-DD" in the owner's time zone at creation
  body             BlockNote block JSON
  searchText       derived from body by the one search builder
  createdAt, updatedAt
  indexes: by_owner_day (ownerId, day) unique-by-logic, by_owner_id
  search index: searchText, filterFields [ownerId]

billingAccounts
  ownerId          -> users, one per user
  customerRef      Stripe customer ID
  subscriptionStatus, planKey, currentPeriodEnd   last-known mirror

accountClosures
  subjectHash      one-way hash of the Clerk subject
  closedAt
  expiresAt        set when the provider deleted the identity (see below)

webhookEvents
  eventId          provider event ID, for deduplication
```

- **No workspaces, no organizations, no membership table.** Nothing needs them, and the brief rules out every future use for them.
- **One entry per day per user. Assumed.** "Daily journal" and "today's entry" suggest it. The backend enforces this with the `by_owner_day` lookup inside `entries.create`. A second create for the same day returns the existing entry.
- **`day` is set when the entry is created. Assumed:** it can't be edited in v1. Moving an entry to another day can come later without changing any URL, because the URL uses `id`, not the date.
- **Search covers full entry text.** For a journal, searching metadata alone wouldn't be useful. `searchText` is a stored derived field, built only by `buildEntrySearchText(body)` in `packages/backend/convex/search/`. Create, update, and every migration call that builder. Every search query filters on `ownerId` first, so search can never cross users.
- **Entry size.** A per-entry byte limit, a domain constant, is checked on write as a bound against abuse. The editor shows the limit before it's reached and never trims text silently.
- **No media in v1. Assumed.** If images are ever added, the bytes go to object storage under owner-scoped keys and are delivered by short-lived signed URLs. They are never public.

### Entry deletion

**Assumed:** deleting an entry is a hard delete, after a product-owned confirmation dialog. There's no trash in v1. For a privacy product, "deleted means deleted" is simple and true. The search index entry goes away with the row, since it's part of the same document. If the owner wants a trash, the change is a `deletedAt` field plus a purge job. That adds no new URL family beyond a trash view.

### Account deletion

There's one path, whoever starts it:

1. In `/settings/account`, the "Delete account" action calls a backend action that deletes the user in Clerk. Deleting the account from Clerk's own UI ends up in the same place.
2. Clerk sends `user.deleted` to the auth webhook. The handler verifies the signature, deduplicates on the event ID (a repeat delivery counts as success), writes the `accountClosures` tombstone, and enqueues the deletion job.
3. The deletion job runs in bounded, resumable phases. It cancels the Stripe subscription immediately, deletes `entries` in batches, deletes `billingAccounts`, and deletes the `users` row last.
4. Because Clerk deleted the identity, the tombstone gets an `expiresAt` comfortably past the longest session-token lifetime. Until then, `account.ensure` refuses that subject, so a lingering token can't recreate the account.

If the product ever closes an account while the Clerk identity still exists (for example, suspending it for abuse), that tombstone has no `expiresAt` and is never purged. The closure origin is a required argument with no default.

### Billing

- One Stripe customer per user, created the first time they open checkout. Checkout and the Customer Portal are hosted by Stripe. They are reached from `/settings/billing` and return to `/settings/billing`.
- The Stripe webhook verifies the signature, deduplicates, and updates the `billingAccounts` mirror. The app derives entitlements from the mirror's `planKey` and status at the authorization gate, using constants in `packages/domain`. It never relies on per-entry flags.
- Use test mode for local and `preview`, and live mode only on `main`.
- **A lapsed plan never locks anyone out of their own writing.** Existing entries stay readable, searchable, and deletable. Which features are paid is still an open question (see below).

### Webhook endpoints

These are Convex HTTP actions on the backend deployment, named by role: `/webhooks/auth` and `/webhooks/billing`. There's one per stage, and each points at that stage's Convex deployment. **Assumed:** the default Convex site URL is used until a custom API domain is chosen. Moving to a custom domain later is a provider settings change.

## URL structure

All paths are on the app origin. With no tenancy unit there's no scope prefix: every private route sits at the top level, and ownership comes from the session, never from the URL.

| Path | What it is |
| --- | --- |
| `/` | Entry dispatcher. It runs the same resolver as `/today` in place. |
| `/auth` | Combined sign-in or sign-up. Optional `?return=` path. |
| `/today` | Dispatcher. If today's entry exists, replace to `/entries/[id]`. Otherwise replace to `/entries/new`. |
| `/entries` | The entries collection, shown as a calendar. `?month=YYYY-MM`. |
| `/entries/new` | Composer for a new entry. `?day=YYYY-MM-DD`, omitted means today. |
| `/entries/[id]` | One entry: read and edit in place. |
| `/search` | Full-text search over your entries. `?q=`. |
| `/settings` | Replaces to `/settings/account`. |
| `/settings/account` | Profile, sign-in methods (Clerk `UserProfile` in modal mode), delete account. |
| `/settings/preferences` | Time zone, week start. |
| `/settings/billing` | Plan, Checkout, and Customer Portal links. |

### Rules behind the table

- **The calendar is the entries collection.** Following the prefix rule, the bare `/entries` is the list of everything under it, and the calendar is how that list is shown. The navigation label says "Calendar". Item pages live directly under it, so there's no separate `/calendar` path beside `/entries/[id]`. If a list layout is added later, it becomes `?view=list` on the same route.
- **"Today" is a link to a concept, not a second home for an entry.** Navigation links to `/today`. The resolver replaces it with the canonical URL, so Back skips the hop and each entry has exactly one URL: `/entries/[id]`. The root `/` and the post-auth landing run the same resolver in place, rather than redirecting through `/today`.
- **Creation is a URL.** `/entries/new` (and `?day=` for filling in a past day from the calendar) can be opened and restored. Nothing is stored until the first keystroke is saved. At that point `entries.create` runs and the URL is replaced with `/entries/[id]`. If an entry already exists for that day, `/entries/new?day=…` replaces to it.
- **Entry IDs** are 12-character Base58, generated by the shared helper in `packages/domain/ids`, with no prefix. They're never the date. The date is a field that may become editable later, and a stable opaque ID keeps links valid if it does. The 3-character `new` can't collide with a 12-character ID.
- **Unknown or not-yours.** `/entries/[id]` for a missing ID or another user's ID shows the same product-owned "entry not found" screen, with a way back to `/today`. Unknown `/settings/*` children replace to `/settings/account`.
- **Search** is its own leaf page rather than a filter on the calendar. Its results are a ranked list, not a month grid. It's also the target of the global search shortcut.

### Query-state contract

The parsers and serializers live in `packages/domain/query-state`, and the UI consumes typed state.

| Route | Params, in canonical order | Absent means | History |
| --- | --- | --- | --- |
| `/entries` | `month=YYYY-MM`, `view=calendar\|list` (later) | current month in the owner's time zone | push per month step |
| `/entries/new` | `day=YYYY-MM-DD` | today | n/a |
| `/search` | `q` | empty search page | replace while typing (debounced) |
| `/auth` | `return` | `/` | n/a |

- An explicitly chosen current month is kept in the URL once picked.
- Malformed values (`month=2026-13`, a future `day`) are rejected and resolve to the default, not kept as a contract.
- Contract tests cover parsing, exact serialization, omitting untouched state, and rejecting bad formats.

### App feel

The shell (navigation for Today, Calendar, and Search, plus a settings entry) persists across routes. Regions load independently behind skeletons sized to the real content. Saves are optimistic over Convex's live queries, so a second open tab updates live. Clerk's `UserProfile` opens as a modal from `/settings/account`, so its internal tabs never put provider-named segments into the product's URLs.

## Env contract (key names only)

Key names are the same in every stage. The values come from each stage's store.

```text
apps/app/.env.example
  VITE_CONVEX_URL
  VITE_CLERK_PUBLISHABLE_KEY
  VITE_SITE_ORIGIN               cross-surface origin override

apps/site/.env.example
  NEXT_PUBLIC_APP_ORIGIN         cross-surface origin override

packages/backend/.env.example    (values live in each Convex deployment's env)
  CLERK_JWT_ISSUER_DOMAIN
  CLERK_SECRET_KEY               used only to delete the Clerk user on account deletion
  CLERK_WEBHOOK_SIGNING_SECRET
  STRIPE_SECRET_KEY
  STRIPE_WEBHOOK_SIGNING_SECRET
  STRIPE_PRICE_ID                differs between test and live mode
  APP_ORIGIN                     Checkout and Portal return URLs
```

Route paths, the JWT template name, plan keys, and limits stay in code.

## Assumptions and open questions

### Calls made without the owner

1. **Domain:** `<apex>` is a placeholder. The site goes on the apex and the app on `app.<apex>`.
2. **Sign-in methods:** Google plus a one-time email code. No passwords and no Apple at launch.
3. **One entry per calendar day**, with the day set when the entry is created and not editable in v1.
4. **"Today" uses a stored user time zone**, seeded from the browser and editable in preferences.
5. **Full-text search** over entry bodies, stored as a derived `searchText` field.
6. **Hard delete for entries**, with no trash.
7. **Text-only entries.** No images or attachments in v1.
8. **Entry text is readable by the server, not end-to-end encrypted.** Convex encrypts at rest, and no product capability, admin included, reads it.
9. **Rich text** uses BlockNote block JSON.
10. **Settings tabs:** account, preferences, billing.
11. **A lapsed subscription keeps every entry readable, searchable, and deletable.**
12. **Package scope** is `@marrow-journal/*`. The root `package.json` name `product-web` was left unchanged.

### Needs the owner's decision

- **End-to-end encryption.** The product is sold on privacy, and assumption 8 is the biggest one. E2EE would make the "only you" promise hold against the operator too. It would also remove server-side search (search would move to the client) and complicate the live sync model. Decide this before any entry is stored, because switching later means migrating every entry.
- **What the paid plan unlocks**, and whether there's a free tier or a trial. The gate and the mirror are designed for it, but entitlements aren't set. Lapsed accounts keep read and delete access either way.
- **Export.** For a privacy product, a "download all my entries" feature in `/settings/account` seems strongly implied. It isn't in the brief.
- **Trash or undo for deleted entries.** See assumption 6.
- **Production domain, and the Google OAuth consent-screen branding.** These need the owner before any production provider setup.

````

> Result: File created successfully at: <run>\builds\2-solo-product-without-workspaces-new-opus\work\docs\architecture.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/architecture.md`. Nothing is committed. The doc says `docs/brief.md` wins if the two ever disagree.

**Auth**
- Clerk handles sign-in on a single `/auth` page that covers both sign-in and sign-up. After signing in, people return to the page they asked for; the return path is checked so it can't send them to another site.
- Organizations are turned off completely, since the brief rules out sharing for good.
- On every visit, the backend makes sure the user's account row exists before showing any data, so a first sign-in never needs a refresh.
- Every backend function goes through one owner check. Someone else's entry looks exactly like a missing one, so the app never confirms that an entry exists.
- Because the product is sold on privacy, I added some rules:
  - No admin or support role can read entry text.
  - Entry text never goes to Clerk, Stripe or logs.
  - The app loads no third-party scripts.
  - Browser tab titles show only the date, never entry text.

**Data ownership**
- Every row belongs to one user; there are no workspaces.
- Clerk owns identity, and only its user ID is stored. Stripe owns subscription status, with a copy kept up to date by its notifications. Plan rules live in code.
- Search covers full entry text and is always limited to the signed-in user's own entries.
- Account deletion follows one path: delete the user in Clerk, then a background job removes everything in stages. A short-lived record of the closed account stops an old login from recreating it.

**URLs**
- `/today` sends you to today's entry, or to a blank composer if there isn't one yet.
- `/entries` is the calendar. Each entry has one URL, `/entries/[id]`, using a 12-character random ID rather than the date. New entries start at `/entries/new?day=…` and switch to their own URL on the first save.
- Search is `/search?q=`. Settings has three tabs: account, preferences and billing.

**Calls I made on your behalf** (all listed in the doc):
- The domain is a placeholder for now: the public site on the main domain, the app on `app.`.
- Sign-in is Google plus an emailed one-time code, with no passwords.
- One entry per day, and its date can't be changed in v1.
- Deleting an entry is permanent, with no trash.
- Entries are text only.
- If a subscription lapses, all entries stay readable, searchable and deletable.

**Decisions I need from you:**
- **End-to-end encryption.** This is the biggest one. I assumed the server can read entry text, because that's what makes server-side search and live sync work. Encryption would make "only you can see it" hold against us as well, but search would have to move into the browser. It's much cheaper to decide before any entries are stored.
- **The paid plan:** what it unlocks, and whether there's a free tier or trial.
- **Export:** whether to add "download all my entries". It seems implied for a privacy product, but it isn't in the brief.
- **Trash:** whether deleted entries should be recoverable.
- **Domain and Google sign-in branding**, before any production setup.

**Session ended:** success, 9 turns, 184390 ms
