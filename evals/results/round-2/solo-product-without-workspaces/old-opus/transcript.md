**Prompt:** Plan the auth setup, data ownership, and URL structure for Marrow Journal's signed-in app, and write it to docs/architecture.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-old-opus/work\" && git ls-files && cat docs/brief.md && cat package.json 2>/dev/null"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5093 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in auth workspace-tenancy bootstrap data-model source-of-truth; do echo \"=== $f\"; cat $f.md; done"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in routing ids query-state app-surface domains origins; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === auth # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already h [... 22755 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in billing data-deletion search-indexing spa-feel live-data monorepo-layout naming admin; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === routing # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the [... 21111 more characters]

> Result: === billing # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed  [... 15423 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in rendering loading-states product-ux legal-pages stack modularity user-facing-errors; do echo \"=== $f\"; cat $f.md; done"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in environment branches provider-setup abuse-resistance test-identities object-storage; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === rendering # Rendering  Choose a rendering posture per surface based on who reads it and whether search engines matter.  - Public pages render on the server or generate statically. They must be crawlable, fast on first paint, and shareable without JavaScript. - Signed-in pages render on the client behind auth. They favor live data, fast transitions, and persistent state over crawlability. [... 18759 more characters]

> Result: === environment # Environment  Env setup should be boring, explicit, and hard to drift. An env example is a contract, not a secret store and not a deployment database. Each runtime owns its own contract. Deployed environments supply values through their host or provider.  Env is for secrets and true environment variance, not a general settings file. This is the twelve-factor posture: configura [... 25903 more characters]

**Tool call `Write`:** `<run>/builds/2-solo-product-without-workspaces-old-opus/work/docs/architecture.md`

````text
# Marrow Journal: Signed-In App Architecture

`docs/brief.md` wins over this file. Where they disagree, this file is stale and gets fixed. This file records how the brief's decisions are carried out for auth, data ownership, and URLs, plus calls made while the owner was away. Each of those calls is tagged **[Assumed]** and gathered in [Assumptions and open questions](#assumptions-and-open-questions).

Status: plan only. Nothing is built.

## Shape in one paragraph

Each Marrow Journal account belongs to exactly one person, and that person is the only one who can see its entries. The brief rules out sharing, teams, and collaborators permanently, so there is **no workspace, organization, or membership layer**. The account is the ownership boundary. Every entry belongs to exactly one account, and the backend works out which account from the verified sign-in on every call, never from anything the client sends. The signed-in app is a client-rendered SPA on its own subdomain. Today's entry is its home screen.

## Surfaces and stack

| Surface | Folder | Host | Rendering | Local |
| --- | --- | --- | --- | --- |
| Public site (pitch, pricing, `/privacy`, `/terms`) | `apps/site` | `marrowjournal.com` **[Assumed]** | Next.js, static/server | `localhost:3000` |
| Signed-in app | `apps/app` | `app.marrowjournal.com` **[Assumed]** | Vite SPA, client-only behind auth | `localhost:3001` |

Staging uses `preview.marrowjournal.com` and `preview.app.marrowjournal.com`. There is no `www`. If it exists, it redirects to the apex at the edge.

| Role | Tool | Notes |
| --- | --- | --- |
| Auth | Clerk | Brief: managed provider with social and email sign-in |
| App data, live sync, search | Convex (`packages/backend/convex`) | Reactive queries, so a second open device updates live |
| Billing | Stripe | Brief: subscription, one subscriber per account |
| Hosting | Vercel | One project per surface |

Packages:

```text
apps/site            public site
apps/app             signed-in SPA: routes, layouts, provider wiring only
packages/backend     Convex schema, functions, HTTP webhooks, provider adapters
packages/domain      ids, route builders, query-state parsers, origins, plans, calendar-date rules
packages/config      shared tsconfig / lint config
```

The app's private pages are not server-rendered. A journal page has no anonymous reader and nothing to crawl, and keeping private content out of server rendering removes a whole class of leaks.

## Auth

### Provider configuration (Clerk)

- **Personal accounts only. Organizations are turned off.** This is intentional and follows from the brief. The generic advice to "prefer workspaces early" applies only when teams or sharing are plausible, and the brief says they never will be. Do not add an org layer "for later".
- **Sign-in methods:** Google as the social provider, plus email as an identifier using an emailed one-time code. Passwords are off. **[Assumed]** The brief says "social sign-in and email" but doesn't name the providers or the email method. Apple is the obvious second social provider and can be added later without changing the architecture.
- Use custom OAuth credentials for each stage (a dev/test Clerk instance and a production instance), with the account-selector prompt turned on so a person can switch Google accounts after signing out.
- The Clerk-to-Convex token uses a JWT template named `convex`. The name is a code convention, not an env value.
- Before writing token verification, decode a real token from our Clerk instance. Always enforce the issuer. Enforce an audience only if Clerk actually mints one.

### One auth route

- `app.marrowjournal.com/auth` is the only auth route. It mounts Clerk's combined sign-in-or-up component with **virtual** routing, so Clerk's internal steps (code entry, factor choice) never show up as URL segments of their own.
- **Return-to:** any signed-out visit to a private route renders the auth screen in place, carrying the interrupted path as `/auth?next=/entries/8fK2mQx9TzLb`. `next` is accepted only if it is a same-origin relative path beginning with a single `/`. Anything else falls back to `/`. One helper in `packages/domain` derives and validates it. Every entry point is tested signed out.
- The public site's "Sign in" / "Start writing" links go to the app's `/auth` through the origin resolver, never through a hardcoded host.

### Bootstrap on every authenticated entry

On every route that can be opened directly:

1. The Clerk session is ready, and Convex has received the auth token (`ConvexProviderWithClerk`).
2. Call the `account.ensure` mutation. It finds the account by Clerk subject or creates it. On creation it records the timezone the browser reports.
3. Only after that, subscribe to entry queries.

A Clerk `user.created` webhook may pre-create the row as an optimization. It is never what creates the row. If a first sign-in ever needs a reload before it works, the ordering is wrong.

### One authorization gate

All Convex functions that touch private data go through one module, `packages/backend/convex/access.ts`:

- `requireAccount(ctx)` reads `ctx.auth.getUserIdentity()`, looks up the account by `authSubject`, rejects closed or closing accounts, and returns the account. No function accepts an `accountId` argument from the client.
- `requireOwnEntry(ctx, entryId)` loads the entry and checks that `entry.ownerId === account._id`. A missing entry and someone else's entry both get the **same** "not found" outcome, so the response never reveals whether an ID exists.
- Capabilities are named even though the only role is "owner of this account": `entry.read`, `entry.write`, `entry.delete`, `account.manage`, `billing.manage`, `data.export`. Plan entitlement is a **separate** check, in `packages/domain/plans`, and is not part of the authorization gate.
- Raw `query` / `mutation` builders are not exported for private tables. Private functions are built from wrapped builders that already ran `requireAccount`, so a function without a gate fails to compile.
- Scheduled jobs (deletion, export) carry the account ID they were created for. Each transaction they run checks again that the account is still live.

### Operator access

Because "visible only to the person who wrote them" is the product's positioning:

- No admin or support surface ever reads entry content. If an admin surface is added later (`admin.marrowjournal.com`, gated by a server-checked allowlist kept in code), it shows only account metadata, subscription state, and job failures.
- Entry text is never written to logs, error reports, or analytics. The app loads no third-party scripts at runtime, and all dependencies are served from our own origin.
- Production Convex deploy keys are limited to the owner.

**This is access control, not end-to-end encryption.** Convex encrypts data at rest, but the platform operator, and anyone holding the production deploy key, could technically read entries. See open question 1.

### Account closure and deletion

There are two ways an account closes, and both lead to the same bounded cleanup:

- **In-app**, at `/settings/data`, behind a product-owned confirmation dialog. The account is marked `closingAt` at once, which stops all reads. The Stripe subscription is canceled immediately. Then the bounded deletion job runs: entries in batches, then search and auxiliary rows, then the account row last. After that the backend deletes the Clerk user.
- **Clerk `user.deleted` webhook:** verify the Svix signature, deduplicate by event ID, treat a repeated delivery as success, and enqueue the same deletion job. Never delete the data graph inside the HTTP request itself.

Both paths end with the Clerk identity deleted, so the closure record is a tombstone: a SHA-256 of the Clerk subject plus `closedAt`, kept longer than the longest-lived session token and then dropped. The closure function takes the origin (`provider` | `product`) as a **required** argument. If a future flow closes the account while keeping the Clerk identity, that record must never expire.

The Stripe customer and invoices stay in Stripe, because Stripe owns payment records. We keep no link to that customer after the account row is deleted.

## Data ownership

### Who owns which fact

| Fact | Owner | Our copy |
| --- | --- | --- |
| Identity, email, name, avatar, sign-in methods | Clerk | Only `authSubject`. **Email is not stored in Convex** **[Assumed]**. It is read from the verified identity when needed (for example, to prefill Stripe Checkout). |
| Account, preferences, entries, search text, jobs | Convex | — |
| Subscription and payment | Stripe | A last-known mirror on the account (`stripeCustomerId`, `subscriptionStatus`, `currentPeriodEnd`) that only the billing webhook updates. Entitlement is computed from that mirror at the gate and never stamped onto entries. |
| Plan names, limits, what each plan unlocks | `packages/domain/plans` | — |
| Calendar-date rules (what "today" is) | `packages/domain` | — |

### Entities (Convex)

```text
accounts
  _id                     internal
  authSubject             Clerk subject (indexed, unique)
  timezone                IANA zone; defaults from the browser on create, editable in settings
  weekStartsOn            preference
  stripeCustomerId?       mirror
  subscriptionStatus?     mirror
  currentPeriodEnd?       mirror
  closingAt?              set when closure starts; hides everything

entries
  _id                     internal
  id                      12-char Base58 public URL id (indexed, unique)
  ownerId                 -> accounts._id
  date                    calendar date "YYYY-MM-DD" in the owner's timezone at the time of writing
  title?                  user-authored, optional
  body                    BlockNote block JSON
  searchText              derived by buildEntrySearchText(title, body); never written any other way
  createdAt, updatedAt
  index by_owner_date (ownerId, date)       unique per owner+date
  searchIndex search_text on searchText, filterFields [ownerId]

closures
  subjectHash, closedAt, origin, expiresAt?

webhookEvents
  provider, eventId (unique)  for deduplicating deliveries
```

Rules:

- **One entry per calendar day per account. [Assumed]** "Today's entry" in the brief suggests this. `date` is a calendar date, not a timestamp, so changing timezone later never moves an entry to a different day.
- The entry ID comes from the one shared helper in `packages/domain/ids` (12 characters, Base58, no prefix). The Convex `_id` never appears in a URL.
- **Display name precedence:** the user's title, otherwise the formatted date ("Saturday, 18 October 2026"). No title is ever generated. There are no AI features in the brief, so none are planned.
- Deleting an entry is a hard delete. **[Assumed]** For a privacy product, "deleted" should mean deleted. An undo toast that holds off the commit for a few seconds covers accidental deletes. A trash or restore feature would be a product decision.
- There are no attachments in v1. **[Assumed]** If images arrive, they go in a per-stage R2 bucket under opaque keys, with the write-ahead ledger so account deletion actually removes the bytes.
- No field, table, or route anywhere represents sharing, visibility, collaborators, or public links. The brief makes their absence permanent.

### Search

Search covers each entry's full content: its title and body text. That is the only useful search for a journal. It comes with obligations:

- `buildEntrySearchText` is the only code that builds `searchText`. Creates, edits, and any later migration all call it.
- Every search query is filtered by `ownerId` inside the search index itself, not filtered after the results come back.
- Deleting an entry deletes its `searchText` with it, because both live in one row. There is no separate index to fall out of sync.
- Search terms and results never go to analytics or logs.

### Billing gate

- Stripe Checkout and the Stripe Customer Portal, reached from `/settings/billing` through a plain link to a same-origin backend route that creates the session and redirects. Both return to `/settings/billing`.
- Test mode on local and preview. Live mode only on `main`.
- **When a subscription lapses, the person never loses their own words.** Reading, the calendar, search, export, and account deletion work on every plan, always. What the plan gates is writing new entries and editing existing ones. **[Assumed]** Whether there is a free tier or trial at all is still open (question 3).

## URL structure

All private routes are on `app.marrowjournal.com`. There is no tenancy segment: with one owner per account and no teams ever, a `/w/[id]` or `/u/[id]` prefix would carry no information. The account is always the signed-in person, worked out on the server.

```text
/                              Today: today's entry, editable (home)
/entries                       Calendar of past entries (the entries collection)
/entries?month=2026-10         Calendar showing a given month
/entries/[id]                  One entry
/search?q=rain                 Full-text search across all entries
/settings                      → replaces to /settings/preferences
/settings/preferences          timezone, week start
/settings/account              sign-in methods and email (Clerk UserProfile, opened as a modal)
/settings/billing              plan, Stripe Checkout / Portal links
/settings/data                 export, delete account
/auth                          sign in or sign up (?next= return path)
```

Decisions behind the table:

- **`/` is Today, a real view and not a redirect.** "Today" is a moving pointer, not a particular entry, so a home-screen bookmark should always open the current day. The view shows today's entry if it exists, or an empty editor that creates the entry on the first keystroke. No empty entries get created just by visiting. The date is fixed when the view loads. If the clock passes midnight while someone is writing, the entry stays put and a quiet "It's a new day" affordance appears.
- **`/entries` is the collection and `/entries/[id]` the item**, one prefix for both, which follows the collection-prefix rule. The collection is shown as a calendar. In the UI it is labelled "Calendar". Clicking a day with an entry goes to `/entries/[id]`. Clicking today goes to `/`.
- **Entry URLs use the opaque ID, not the date.** A date is readable, but an ID keeps the URL stable if the one-entry-per-day rule changes or an entry's date gets corrected.
- **`/search` is its own leaf page.** It shows a ranked list across all time, which is a different view from a month grid. A global shortcut (`/` key or ⌘K) opens it.
- **Query state:** `month=YYYY-MM` (left out when it's the current month) on `/entries`, and `q` on `/search`. Parsing and serializing live in `packages/domain`, with contract tests. Typing in search replaces the history entry instead of pushing a new one. Unknown formats fall back to the default view rather than being kept.
- **`/settings` has child views**, so the bare path replaces to its default child. Clerk's profile UI opens as a modal over `/settings/account` so Clerk's own sub-routes never enter our URL contract. Stripe pages are external and only ever reached through a redirect route.
- **No public, shared, or short-link routes exist, and none will.** Opening someone else's entry URL while signed in shows the same "not found" screen as a nonexistent ID.
- Navigation inside the app uses relative paths. Links to the site and Stripe/Clerk return URLs go through `resolveAppOrigin()` / `resolveSiteOrigin()` in `packages/domain/origins`.
- The persistent shell (nav: Today, Calendar, Search, Settings) renders before any data arrives. Each region shows its own skeleton.

## Environment contract (keys only)

```text
apps/app/.env.example
  VITE_CLERK_PUBLISHABLE_KEY
  VITE_CONVEX_URL
  VITE_SITE_ORIGIN            only where it differs from the canonical constant

packages/backend/.env.example   (values live in each Convex deployment)
  CLERK_JWT_ISSUER_DOMAIN
  CLERK_SECRET_KEY            to delete the Clerk user on in-app closure
  CLERK_WEBHOOK_SECRET
  STRIPE_SECRET_KEY
  STRIPE_WEBHOOK_SECRET
  APP_ORIGIN                  Stripe return URLs
```

Webhooks are Convex HTTP actions named by role, not by vendor: `/webhooks/auth` and `/webhooks/billing`, one set per stage. Plan IDs, route paths, and the JWT template name live in code.

## Assumptions and open questions

Calls I made without the owner. Each one can be reversed cheaply now, and gets more expensive once something is built.

1. **Privacy model: access control, not end-to-end encryption.** This is the biggest question. Today, Convex (as the platform) and anyone holding the production deploy key could technically read entries. If the brief's "visible only to the person who wrote them" has to hold even against the operator, entries need client-side encryption. That would mean: search moves to the client (a local index), no server can ever recover a forgotten key (a lost key means a lost journal), and export and deletion work differently. Marketing and `/privacy` copy must match whichever model is chosen. **Please decide before anything is built.**
2. **Domain:** `marrowjournal.com` / `app.marrowjournal.com` are placeholders. Nothing is registered or configured.
3. **Plan shape:** is there a free tier or a trial? I assumed lapsed accounts stay readable, searchable, and exportable, and only writing is gated. Prices and plan names are not decided.
4. **Sign-in methods:** Google plus an emailed one-time code, no passwords. Is Apple wanted at launch? Mobile Safari users will expect it.
5. **One entry per day.** If several entries per day are wanted, the unique index becomes a plain index, Today becomes a list for the day, and URLs are unaffected.
6. **Rich text:** BlockNote JSON rather than plain text or markdown.
7. **Hard delete** for entries, with a brief undo. No trash.
8. **No email stored in our database.** Clerk stays the only holder of it.
9. **Export** (`/settings/data`) is in scope even though the brief doesn't list it. For a privacy journal, being able to leave with your words seems essential. Format to be decided (Markdown zip or JSON).
10. **No attachments or images** in v1.
11. **`q` in the URL:** search terms show up in the address bar and, after a reload, in the hosting request logs. I kept `q` in the URL for restorable search, on the condition that request logging and any analytics strip query strings. If that's not acceptable, search can keep `q` in client state only, at the cost of shareable/restorable search URLs (which matter less in a product with no sharing).

````

> Result: File created successfully at: <run>/builds/2-solo-product-without-workspaces-old-opus/work/docs/architecture.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/architecture.md`. It's a plan only: nothing is built and nothing is committed. Each call I made without you is tagged **[Assumed]**, and the doc ends with a numbered list of assumptions and open questions.

**What I decided:**
- **No workspace or team layer.** Your brief rules out sharing and teams permanently, so each account is the boundary around its own entries. Organizations are turned off in the auth provider (Clerk), and URLs carry no account segment.
- **Auth:** Clerk with Google plus an emailed one-time code, and no passwords. There's a single `/auth` page that sends people back to where they were. The account record is created the first time someone signs in, not only when a webhook arrives.
- **One access check for all private data.** The backend works out the account from the verified sign-in and never accepts an account ID from the browser. Opening someone else's entry looks exactly like opening one that doesn't exist.
- **Who owns what:** Clerk holds identity and email (I don't store email in our database). Stripe holds the subscription, and we keep only a copy updated by its webhooks. Convex holds accounts and entries, one entry per calendar day.
- **Search:** search covers full entry text, always limited to the signed-in account.
- **Lapsed subscriptions:** people can still read, search, export and delete their own entries. Only writing and editing are paid features.
- **Deleting an account** removes the data in stages, cancels the subscription, and then deletes the Clerk user.
- **URLs:** the app's home page `/` is Today. `/entries` is the calendar (with `?month=` to pick a month), `/entries/[id]` is a single entry, `/search?q=` is search, `/settings/{preferences,account,billing,data}` is settings, and `/auth` is sign-in. There are no public or share links, and none are planned.

**Questions for you, most important first:**
1. **Access control or end-to-end encryption.** As planned, the hosting platform and anyone with the production keys could technically read entries. If "visible only to the person who wrote them" has to hold even against you as the operator, entries need encrypting in the browser. That would move search into the browser and mean a lost key is a lost journal. This needs deciding before anything is built, and your marketing and privacy-policy wording should match the choice.
2. **Free tier or trial**, and prices.
3. **Apple sign-in at launch?**
4. **Smaller calls that are easy to change now:**
   - one entry per day
   - rich text rather than plain text or markdown
   - deleting an entry is permanent, with a short undo and no trash
   - export is included even though the brief doesn't list it
   - no images in v1
   - search terms in the URL: they would show up in hosting logs unless logging and analytics strip query strings
5. **Domain:** `marrowjournal.com` is a placeholder.

One thing outside this task: your working branch is `master`, while the repo's main branch is `main`. I left the branches alone.

**Session ended:** success, 10 turns, 175109 ms
