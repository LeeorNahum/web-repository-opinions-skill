**Prompt:** not recorded by this session. The case in the committed `evals.json` may have changed since.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-solo-product-without-workspaces-old-opus/work\" && git ls-files && cat docs/brief.md && cat package.json 2>/dev/null"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5093 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in auth workspace-tenancy bootstrap data-model source-of-truth; do echo \"=== $f\"; cat $f.md; done"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in routing ids app-surface domains query-state; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === auth # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already h [... 22755 more characters]

> Result: === routing # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the [... 17604 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in billing search-indexing data-deletion origins spa-feel rendering; do echo \"=== $f\"; cat $f.md; done"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in monorepo-layout naming stack modularity live-data admin legal-pages; do echo \"=== $f\"; cat $f.md; done; cat ../../../../pnpm-workspace.yaml"}`

> Result: === billing # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed  [... 12705 more characters]

> Result: === monorepo-layout # Monorepo Layout  Use `apps/` for deployable entry points and `packages/` for shared libraries. Nothing else earns a top-level slot by default.  ```text product-slug/   apps/     site/      public marketing, SEO, docs, pricing, legal, help     app/       signed-in product, private routes, account, billing, admin   packages/     backend/   backend functions, jobs, pro [... 16564 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat product-ux.md loading-states.md | head -150"}`

> Result: # Product UX  Design every screen around a real human path, not a template average of nearby patterns. A product surface can be locally correct and globally incoherent. Judge the whole, not just the parts.  For each page, decide what the viewer should notice first, next, and last, then build to that order.  - Give every page one clear primary path or action. No dead-end screens. - Hide acti [... 6159 more characters]

**Tool call `Write`:** `<run>\builds\1-solo-product-without-workspaces-old-opus\work\docs\architecture.md`

````text
# Marrow Journal architecture: auth, data ownership, URLs

`docs/brief.md` holds the owner's decisions and wins over this document. If the two ever disagree, fix this file to match the brief. This file records the technical plan and the assumptions made while writing it. Assumptions are marked **(assumed)** and listed again under [Open questions](#open-questions-for-the-owner).

Nothing is built yet. This is a plan, not a description of running code.

## The rule everything follows

Every entry belongs to exactly one person, and only that person can ever reach it. The brief rules out sharing, teams, and collaborators permanently, as positioning. So:

- **No workspace or organization layer.** The usual default for a SaaS is a workspace boundary from day one in case teams come later. The brief says teams will never come, so that layer would be dead weight, and an unused "members" concept is a privacy risk. The user is the tenant.
- **No share links, public entries, or invitations**, including "harmless" ones like a read-only link. A private URL is never a capability: opening `/entries/<id>` while signed in as someone else shows the same screen as an entry that doesn't exist.
- **Operators don't read entries either.** No admin or support tool shows entry content (see [Operator access](#operator-access)).

## Surfaces and stack

| Surface | Directory | Host | Rendering | Tool |
| --- | --- | --- | --- | --- |
| Public site (marketing, pricing, legal) | `apps/site` | apex | Server or static | Next.js App Router |
| Signed-in app | `apps/app` | `app.` subdomain | Client, behind auth | Vite + React SPA |
| Backend (schema, functions, webhooks, jobs) | `packages/backend` | Convex deployment | n/a | Convex |
| Pure product rules (IDs, routes, query state, dates, origins, plan rules) | `packages/domain` | n/a | n/a | TypeScript |

Auth goes through Clerk and billing through Stripe, each behind an adapter named for its role (`auth`, `billing`), not for the vendor.

**Domain (assumed):** none has been chosen yet. Below, `<apex>` stands for the production domain. The app lives at `app.<apex>`, and staging at `preview.<apex>` / `preview.app.<apex>`. Canonical origins are constants in `packages/domain/origins`, with one resolver per surface (`resolveSiteOrigin`, `resolveAppOrigin`). Local ports are site `3000` and app `3001`.

The site never renders private data. The app has no SEO pages and is served with `noindex`.

## Auth

### Provider setup

- **Clerk**, one development instance (local and preview) and one production instance, each with its own OAuth credentials.
- **Organizations off.** Personal accounts only. This matches the no-teams rule, and it means no session ever carries an organization context.
- **Social sign-in: Google (assumed),** using our own OAuth client ID and secret per stage so the account-selector prompt can be turned on and people can switch Google accounts after signing out. Apple is a likely second provider (see open questions).
- **Email as an identifier: on.** Sign-in by email verification code. **Passwords off (assumed):** codes are enough, and this keeps one less credential to reset. Turning passwords on later is only a dashboard change.
- Clerk owns credentials, verification, sessions, and MFA. We never store passwords, and we don't treat email as an identity key.

### One auth route

- `app.<apex>/auth` hosts Clerk's combined sign-in-or-sign-up component. There are no separate `/sign-in`, `/sign-up`, or `/callback` paths, and no env keys for auth paths.
- **Return to where you were:** when a signed-out visit hits a private route, the app sends the person to `/auth?redirect_url=<path+query>`. That value is derived once in the app's auth guard from the interrupted location. It is accepted only if it is a same-origin relative path (starts with a single `/`, no scheme, no `//`). Anything else falls back to `/today`.
- The site's "Sign in" and "Start writing" buttons link to the app's `/auth` through `resolveAppOrigin()`. The host is never hardcoded.
- Terms are agreed to at sign-up through Clerk's legal-consent step, which links the site's `/terms` and `/privacy`. Both pages have to exist before Google OAuth verification.

### Backend trust

- Convex verifies Clerk's JWT (the Convex JWT template) on every call. The template name is a code constant, not an env value.
- **Before writing the issuer and audience checks, decode a real token from each Clerk instance and build the checks from what it actually contains.** Enforce the issuer every time. Enforce the audience only if the token actually carries one.
- The user's stable key is the Clerk subject (`sub`), stored as `users.authSubject`. Email and name are never used as keys.

### Bootstrap on every authenticated entry

Every route that can be opened directly runs the same order inside the app shell:

1. Wait for Clerk to report a session, then for Convex to report an authenticated connection (`ConvexProviderWithClerk`).
2. Call the `ensureUser` mutation. It finds or creates the `users` row by `authSubject`, creates it with the browser's time zone as the initial `timeZone`, and refuses if the subject has a closure record.
3. Only after that, subscribe to entries and other private data.

A Clerk `user.created` webhook may call the same upsert as an optimization, but it is never what creates the row. If a first sign-in needs a refresh to show data, the order of operations is wrong.

### One authorization gate

All private Convex functions are built from two wrappers in `packages/backend`: `ownerQuery` and `ownerMutation`. Each one:

1. reads the verified identity, or fails with one product error ("You've been signed out"),
2. loads the `users` row by `authSubject` and checks it is live (not closing or closed),
3. passes `ctx.user` to the handler.

Private handlers never import Convex's raw `query`/`mutation`. A lint rule flags it, but the lint rule is only hygiene. The real boundary is that the wrappers are the only exported way to build a private function, and every handler reads data by `ctx.user._id`.

The ownership rule for a single entry: load it by public `id`, and if it doesn't exist **or** `entry.userId !== ctx.user._id`, return the same `not_found` result. The two cases are never distinguishable.

There is a single role (the account owner), so capabilities are only named, not assignable: `entries.read`, `entries.write`, `entries.delete`, `account.manage`, `subscription.manage`. Plan gating ("does this plan include X") is a separate billing check that the gate calls into. The two are not merged.

Background work (the account-deletion cleanup) carries the `userId` it was scheduled for. Each step checks that user's state again in its own transaction instead of trusting the check made when it was scheduled.

### Account deletion and closure

- The person deletes their account from `/settings/account` through a product-owned confirmation dialog. The backend marks the user `closing`, which immediately stops it from passing the gate, then deletes the identity through the Clerk API.
- The Clerk `user.deleted` webhook handler (a Convex HTTP action) verifies the signature, deduplicates by event ID (a repeat delivery counts as success), and enqueues bounded cleanup. It never deletes the whole account inside the HTTP request.
- Cleanup steps, each idempotent and resumable: cancel the Stripe subscription immediately → delete entries in batches → delete webhook-dedupe rows and other auxiliary rows → delete the `users` row last.
- A **closure record** keeps a one-way hash of the subject and the time of closure. `ensureUser` refuses that subject, so a still-valid old JWT cannot recreate the account. Because every deletion path goes through Clerk deleting the identity, the record has an expiry comfortably longer than the longest token lifetime. If a product-side closure that leaves the Clerk identity alive is ever added, that origin must never expire. The origin is a required argument with no default.

## Data ownership

### Which system owns which fact

| Fact | Owner | Other copies |
| --- | --- | --- |
| Identity, sign-in methods, email, sessions | Clerk | `users.authSubject` reference only. No email mirror. |
| Entries, user preferences, account state | Convex | none |
| Subscription and payment status | Stripe | `subscriptions` row: the last-known mirror, reconciled by Stripe webhooks, never the authority over Stripe |
| Plan names, what each plan includes | `packages/domain` (code) | none. Not env, not the Stripe dashboard. |
| "Today" for a person | Derived from `users.timeZone` + current time | never stored |
| Search text | Derived from `entries.body` by one builder | stored only because the search index needs it |

### Tables (Convex)

```text
users
  id              12-char Base58 public id
  authSubject     Clerk subject, unique index
  timeZone        IANA zone, e.g. "Europe/London"
  state           "active" | "closing"
  createdAt

entries
  id              12-char Base58 public id (URL identity)
  userId          -> users (owner, immutable)
  date            local calendar date "YYYY-MM-DD" in the owner's zone when written
  body            block JSON (BlockNote)
  searchText      output of buildEntrySearchText(body)
  createdAt, updatedAt
  indexes: by_user_date (userId, date) unique-by-code, by_public_id
  search index: searchText, filterFields [userId]

subscriptions     (one per user: "one subscriber per account")
  userId          -> users, unique
  stripeCustomerId, stripeSubscriptionId
  status, planKey, currentPeriodEnd   last-known mirror from Stripe webhooks

webhookEvents     provider event id, for dedupe
closures          subjectHash, closedAt, expiresAt
```

Decisions inside the schema:

- **One entry per person per calendar date (assumed).** "Today's entry" and "a calendar of past entries" both read as a daily journal with one page per day. Uniqueness is enforced in the create mutation against `by_user_date`. Writing for a past empty day is allowed from the calendar.
- **`date` is fixed when the entry is created.** Changing the time zone later doesn't move existing entries. "Today" is always computed from the user's current zone.
- **Rich text as BlockNote block JSON (assumed).** `buildEntrySearchText` turns it into plain text. Every write calls it, and so does any future migration.
- **Text only in v1 (assumed).** No images or attachments, so there is no object storage yet. If attachments arrive, the bytes go to R2 under per-user keys, are served only through short-lived signed URLs minted after the owner check, and are deleted in the account cleanup.
- **Deleting an entry is a hard delete (assumed),** after a product-owned confirmation. A privacy-first journal should mean it when it says "deleted". There is no trash.
- **Full-content search is in scope.** Searching a journal by metadata alone is useless. The index is filtered by `userId` on every query, so it can never search across users. Deleting an entry removes it from the index in the same transaction.
- No location, device, or raw provider payloads are stored. Stripe and Clerk webhook bodies are verified, turned into the few fields above, and thrown away.
- Edits go through Convex mutations with optimistic updates, so every open tab updates live. The editor autosaves with a debounce. There is no save button.

### Billing

- The Stripe customer is created for the user on first checkout. The person goes to Stripe Checkout and the Customer Portal from `/settings/subscription`, and both return there.
- Whether someone is subscribed is derived at the gate from the `subscriptions` mirror and the plan rules in code, never stamped onto entries.
- **What the paid plan unlocks is not decided.** The architecture leaves room for any answer, with one constraint I'd treat as non-negotiable: losing a subscription never locks someone out of reading, searching, or deleting what they already wrote. Only new writing (or whatever the paid feature is) is gated.
- Test mode on local and preview. Live mode on production only.

### Operator access

- Admin tooling is not part of this plan. If it's added later, it shows account, subscription, and job state only, never entry bodies or search text.
- **Residual exposure:** anyone with production Convex dashboard access can read stored rows. Keep production dashboard access to the smallest possible set of people, and state this honestly in `/privacy`. Encryption at rest is the provider's. End-to-end encryption is an open question below, because it changes search and sync.

## URL structure

### Signed-in app (`app.<apex>`)

| Path | What it is |
| --- | --- |
| `/` | Dispatcher. Replaces itself with `/today` when signed in, or `/auth` when signed out. No history stop. |
| `/auth` | Combined sign-in / sign-up. `?redirect_url=` takes a relative path only. |
| `/today` | Stable "today, whatever date that is" link. If today's entry exists, replaces itself with `/entries/<id>`. If not, renders the blank editor in place, and the first autosave creates the entry and replaces the URL with `/entries/<id>`. |
| `/entries` | The entries collection, shown as the calendar. `?month=YYYY-MM`. With no `month`, it shows the current month. Moving between months is a history push. |
| `/entries/<id>` | One entry, readable and editable. The canonical URL for every entry, including today's. |
| `/search` | Full-text search over your entries. `?q=` holds the text, history replace while typing. Results link to `/entries/<id>`. |
| `/settings` | Replaces itself with `/settings/account`. |
| `/settings/account` | Sign-in methods (opens Clerk's profile in **modal** mode so Clerk's own sub-routes stay out of our URLs), sign out, delete account. |
| `/settings/subscription` | Plan, status, Stripe Checkout / Customer Portal, return target. |
| `/settings/preferences` | Time zone and any future preferences. |

Rules behind the table:

- **No tenancy segment.** A workspace-based product would use `/w/<workspaceId>/entries/<id>`. There is exactly one possible owner here, the signed-in user, so the scope segment would carry nothing. Ownership comes from the verified session, never from the URL.
- **IDs:** entries use a 12-character Base58 `id` made by one helper in `packages/domain/ids`. Convex `_id` values never appear in URLs. **Dates are not URL identities (assumed):** `/entries/2026-10-17` would read nicely, but a date says when someone wrote, sits in history and logs, and would tie the URL to a value the entry might later be corrected to. The calendar handles navigation by date.
- **Calendar as the collection view:** the nav label is "Calendar". It lives at `/entries` because a bare prefix is its collection view, so there is no separate `/calendar` path to keep in sync. A future list view would be `?view=list`, not a new route.
- An unknown, deleted, or someone-else's `<id>` shows one product-owned "This entry isn't here" screen with a link to `/today`.
- Query state (`month`, `q`, later `view`) is parsed and serialized in `packages/domain` in a fixed order `q → month → view`, with contract tests.
- Navigation inside the app is client-side with a persistent shell (sidebar: Today, Calendar, Search, Settings). The shell renders before data, and each region shows its own skeleton.

### Public site (`<apex>`)

`/`, `/pricing`, `/privacy`, `/terms`, and `/security` (assumed: worth having, given the product is sold on privacy). Each one has a favicon and a link preview card. No `www`: it redirects to the apex at the edge.

## Open questions for the owner

Each of these has a working assumption above. Confirm or override:

1. **Domain.** What is the production apex? (`app.` subdomain assumed for the app.)
2. **Social providers.** Google only, or Google + Apple? (Google assumed.)
3. **Passwords.** Email codes only, or passwords as well? (Codes only assumed.)
4. **One entry per day.** Is a day one page, or can someone write several entries on one date? Several entries per day changes `/today` into "new entry" and the calendar into day lists. (One per day assumed.)
5. **Backfilling past days.** May people write for a past empty date? (Allowed assumed.)
6. **Deletion.** Hard delete with no trash, or a recoverable trash period? (Hard delete assumed.)
7. **Paid plan.** What does the subscription unlock, and is there a free tier? (Undecided. Reading, searching, and deleting own entries are never gated.)
8. **End-to-end encryption.** It would strengthen the privacy pitch, but server-side search, live multi-tab sync, and account recovery all get harder or go away. (Not planned. Encryption at rest is the provider's.)
9. **Attachments.** Text-only for v1? (Assumed.)
10. **Data export.** Not in the brief. For a privacy product I'd recommend an export in `/settings/account`, but it isn't planned until you decide.

````

> Result: File created successfully at: <run>\builds\1-solo-product-without-workspaces-old-opus\work\docs\architecture.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/architecture.md`. I didn't commit it, so it's waiting for your review. The main decisions:

**Ownership model**
- Each journal belongs to one person, with no shared workspace layer above it. The usual default is to set up shared workspaces from day one in case teams come later. Your brief rules out sharing and teams for good, so that layer would be unused, and an idle "members" concept is a privacy risk.
- Every backend function goes through one check that compares the entry's owner with the signed-in person. Opening someone else's entry shows the same screen as an entry that doesn't exist.
- No support or admin tool will show entry content. The doc also notes that anyone with access to the production database can still read stored entries. That access should stay limited to as few people as possible, and the privacy page should say so.

**Auth (Clerk)**
- Sign-in uses Google plus email codes, with team accounts switched off. Sign-in and sign-up share one page at `/auth`, which returns people to the page they were trying to open.
- The account is created or checked on every visit, rather than relying on a sign-up message from Clerk.
- Account deletion is cleaned up in safe, repeatable steps. A small closure record keeps an old sign-in token from quietly recreating a deleted account.

**URLs (app on its own `app.` subdomain)**
- `/today` always means today. If today's entry exists, it forwards to `/entries/<id>`. If not, it shows a blank page, and the entry is created when you first start typing.
- `/entries` is the calendar (`?month=2026-10`), and each entry lives at `/entries/<id>`.
- `/search?q=` searches the full text of entries, only ever within your own.
- `/settings` has three sections: account, subscription and preferences.
- Entry URLs use short random IDs, not dates.

**Assumptions to confirm** (all 10 are listed at the end of the doc):
- One entry per day, and you can write for past days that were left empty.
- Deleting an entry is permanent, with no trash.
- Text only for now: no images or attachments.
- No passwords: email codes only.
- The production domain isn't chosen yet.
- What the paid plan unlocks is undecided. I set one rule I'd treat as non-negotiable: losing a subscription never stops someone reading, searching or deleting what they already wrote.
- End-to-end encryption isn't planned, because it would make search and syncing between open tabs much harder. Since the product is sold on privacy, that's your call.

**Session ended:** success, 10 turns, 141947 ms
