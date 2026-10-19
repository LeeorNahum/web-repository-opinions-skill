**Prompt:** Plan the auth setup, data ownership, and URL structure for Marrow Journal's signed-in app, and write it to docs/architecture.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-solo-product-without-workspaces-old-opus/work\" && git ls-files && cat docs/brief.md && cat package.json 2>/dev/null"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5093 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in auth workspace-tenancy bootstrap data-model source-of-truth; do echo \"=== $f\"; cat $f.md; done"}`

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in routing ids query-state app-surface domains; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === auth # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already h [... 22755 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in billing search-indexing data-deletion origins spa-feel; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === routing # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the [... 17604 more characters]

> Result: === billing # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed  [... 10662 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-solo-product-without-workspaces-old-opus/work/.claude/skills/web-repository-opinions/references\" && for f in admin rendering monorepo-layout naming legal-pages live-data stack product-ux; do echo \"=== $f\"; cat $f.md; done"}`

> Result: === admin # Admin  Admin is a gated internal surface, not a hidden corner of the user app. Gate it explicitly by an admin role checked on the server, never by an unlinked route or client-only check.  Keep the operator and admin allowlist the server checks against in versioned code, reviewed in code review. Who counts as internal staff is a product decision, so it lives with the code alongside  [... 19105 more characters]

**Tool call `Write`:** `C:\tmp\wro-eval3\builds\3-solo-product-without-workspaces-old-opus\work\docs\architecture.md`

````text
# Marrow Journal: Architecture

This covers auth, data ownership, and URL structure for the signed-in app. `docs/brief.md` is the source of truth for product decisions. If this file contradicts the brief, the brief wins and this file gets fixed.

Items marked **[Assumed]** are calls made without the owner. They are collected again at the end, along with the questions that need an answer before the work they block can start.

## Shape of the product

- **One person, one account, one private journal.** The brief rules out sharing, teams, and collaborators permanently. Every user-generated record belongs to exactly one user, and nothing in the system can point a second person at it.
- **No workspace layer.** The usual default is to put a workspace or organization between a user and their data, so that teams can be added later. Here that default is deliberately not followed: teams are ruled out, and a tenancy layer with one member would only add complexity and an extra URL segment. The account is the ownership boundary. If the brief ever changes, adding a workspace layer becomes a planned migration (see "If the brief changes" at the end).

## Surfaces and layout

```text
apps/
  site/       public site: home, pricing, /privacy, /terms (Next.js, server-rendered or static)
  app/        signed-in journal (Vite + React SPA, client-rendered behind auth)
packages/
  backend/    Convex: schema, queries/mutations, webhooks, scheduled jobs
  domain/     pure rules: entity IDs, route builders, query-state parsers, dates, plans, origins
  config/     shared TypeScript and tooling config
```

| Surface | Production | Staging (`preview` branch) | Local |
| --- | --- | --- | --- |
| Site | `https://<apex>` | `https://preview.<apex>` | `http://localhost:3000` |
| App | `https://app.<apex>` | `https://preview.app.<apex>` | `http://localhost:3001` |

- **[Assumed]** The domain hasn't been chosen yet, so `<apex>` stands in for it. Once it's chosen, it goes in `packages/domain` as the `CANONICAL_SITE_ORIGIN` / `CANONICAL_APP_ORIGIN` constants. It does not go in env.
- The app is client-rendered. Private entries are never server-rendered, because a server render would gain nothing for a page only its owner can see.
- Every link between the site and the app is built through the origin resolvers in `packages/domain`. Hosts are never hardcoded.
- Defaults: Clerk for auth, Convex for data and live sync, Stripe for billing, Vercel for hosting. Code names each module after its role (`auth`, `billing`, `search`), never after the vendor.

## Auth

### Provider and sign-in methods

- **Clerk** is the managed provider. The product never stores passwords and never verifies email addresses itself.
- **[Assumed]** Sign-in methods are **Google**, **Apple**, and **email with a one-time code** (no password). The brief says "social sign-in and email" but doesn't name the providers. Google and Apple cover most people. Email codes avoid a password surface while still letting anyone without a social account sign in.
- The email identifier stays on in every configuration. Clerk uses it to merge a social sign-in and a verified email into one account.
- Every social provider uses **our own OAuth credentials, created separately for each stage** (dev/test vs. production). With our own credentials, the Google account-selector prompt can be turned on, so someone who signs out can switch accounts. Clerk's shared dev credentials don't allow that.
- **Clerk Organizations stay disabled.** No session ever has an organization context.

### Routes

- `app.<apex>/auth` is the only auth route. It uses Clerk's combined sign-in-or-up component. There are no separate sign-in, sign-up, or callback routes, and no env keys for auth paths.
- **Signing in returns the person to the page they were trying to open.** The protected-route guard records the interrupted path once, as `/auth?return=/entries/7Kp3xQ9mVbZt`, and the redirect only follows a value that is a same-origin relative path (it must start with `/`, must not start with `//`, and has no scheme). Anything else falls back to `/today`.
- Signing out goes to the site's home page (`<apex>/`), not to `/auth`.
- The site's "Sign in" and "Start writing" links point to `app.<apex>/auth` through the app-origin resolver.

### Token verification and the authorization gate

- Convex validates Clerk JWTs through Clerk's `convex` JWT template. The issuer is always enforced. Before the audience check is written, a real token from our instance gets decoded so the check matches what Clerk actually issues.
- **There is one authorization gate.** Every public Convex function is built with one of two wrappers in `packages/backend`, `userQuery` and `userMutation`. The wrapper resolves the verified identity to the user's row, rejects closed accounts, and passes `user` to the handler. The plain `query`/`mutation` builders are not used for anything that reads user data, and a lint rule enforces that. The lint rule only catches mistakes. The wrapper is the actual security boundary.
- **The entry loader is the only way to read an entry by ID.** It is one helper, `loadOwnedEntry(ctx, user, entryId)`. If the entry doesn't exist, or belongs to someone else, it returns the same product-owned "not found" result. The response never reveals whether an ID exists.
- An ID in the URL selects a record. It never grants access to it.
- Capabilities are simple because there is one role, the owner: `entry.read`, `entry.write`, `entry.delete`, `account.manage`, `billing.manage`. Whether the current plan allows writing is a separate check in billing (see below), not part of this gate.
- Background jobs (cleanup, deletion) carry the owner's user ID and re-check that the account is still active in every transaction where they act.

### Bootstrap

Every authenticated entry into the app runs these steps before showing any data:

1. Read the Clerk identity.
2. Call `users.ensure`, a mutation that finds or creates the `users` row by Clerk subject. On first creation it records the browser's IANA timezone.
3. Read the data the page needs.

The workspace and membership steps from the default bootstrap order don't exist here. Clerk's `user.created` webhook can create the row early, but it's only an optimization. `users.ensure` is what guarantees the row exists. If someone's first sign-in ever needs a refresh to work, the order is wrong somewhere.

## Data ownership

### Which system owns each fact

| Fact | Owner |
| --- | --- |
| Login identity, credentials, linked social accounts, email | Clerk |
| Subscription and payment status | Stripe (Convex keeps a last-known copy, updated by webhooks) |
| Users, entries, settings, search index, job state | Convex |
| Plan names, limits, entity ID format, route builders, date rules | `packages/domain` (code) |
| Origins, keys, secrets per stage | Vercel / Convex env stores |

There is no object storage, because the brief has no photos or attachments. If attachments are added, the bytes go to R2 under the user's ID prefix, and Convex stores only the object keys.

### Tables (Convex)

```text
users
  id               12-char Base58 (internal; never appears in URLs)
  authSubject      Clerk user ID (stable subject); unique index
  timezone         IANA zone, e.g. "Europe/Lisbon"; user-editable
  stripeCustomerId optional; unique index
  createdAt

entries
  id               12-char Base58, the URL identity; unique index
  userId           owner; every index starts with userId
  date             local calendar date "YYYY-MM-DD" in the owner's timezone at creation; immutable
  body             BlockNote block JSON
  searchText       plain text derived from body by one builder function; search index field
  wordCount        derived from body by the same builder
  createdAt, updatedAt
  indexes: by_id, by_user_date (userId, date) unique, search_body (searchText, filter userId)

subscriptions      last-known copy of Stripe status, one row per user
  userId, stripeSubscriptionId, status, planKey, currentPeriodEnd, updatedAt

webhookEvents      deduplication: provider + event ID, processedAt
accountClosures    hashed Clerk subject, closedAt, origin, expiresAt?
```

- **[Assumed] One entry per calendar day per user.** The brief has "today's entry" and "a calendar of past entries", which suggests one entry per day. A unique `(userId, date)` index enforces it. The date can't change, so the calendar never has to deal with two entries on one day.
- **"Today" is the user's own calendar day,** computed from `users.timezone` and not from UTC. The client sends the date it wants. The server checks that "today" really is today in the user's timezone (with one day of slack either side for travel), and accepts any earlier date when filling in a past day.
- **[Assumed] Entries use BlockNote rich text** (the default). `searchText` and `wordCount` are stored instead of computed on read, because Convex's search index has to have a stored field. A single builder function writes them on every save, so they never fall out of sync with `body`.
- **Empty entries:** opening a day creates its row (see "Today" under URL structure). The calendar and search hide entries with an empty `searchText`. A daily scheduled job deletes empty entries more than a day old.
- **[Assumed] Deleting an entry is permanent, after a confirmation dialog the product owns.** There is no trash. For a product sold on privacy, "deleted" should mean the data is gone. Adding a 30-day trash later would be a small change.

### Search

Search covers the **full text of entries**, which the brief requires. Searching titles alone would be useless for a journal. It runs on a Convex search index over `searchText`, and every query filters on `userId`. That filter is inside the search helper, so no caller can drop it. Search sits behind a `search` module in `packages/backend`, so the engine can be replaced without changing callers. Because the index is part of the entry row, deleting an entry or an account also removes it from search.

### Privacy posture

- No other user can reach an entry. That is enforced by the single gate described above, not by each surface.
- **No operator access to entry content through the product.** No admin function, support tool, or log line returns or records entry bodies. A future admin surface can show accounts, subscription status, and failed jobs, but never entry content. Logs and error reports cut every entry field down to its ID.
- The data is encrypted at rest by Convex. People with access to the database can still technically read entries, though. See the first open question.

### Billing ownership

- **Stripe customer is one-to-one with the user.** The customer is created at the user's first checkout and linked through `users.stripeCustomerId`, with `metadata.userId` also set on the Stripe customer.
- Stripe is the source of truth. The `subscriptions` row is a copy of the last status Stripe reported, kept current by signature-verified, deduplicated webhooks. Whether a user is allowed to do something is worked out from that row by the gate at request time. No "is paid" flag is stored on the user.
- **[Assumed] A lapsed subscription never locks anyone out of their own writing.** Reading, searching, and deleting entries, and deleting the account, keep working on every plan state. What a lapse turns off is a plan decision (see open questions).
- Plan names and limits are code constants in `packages/domain`. Test mode runs everywhere except production.

### Account deletion

There is one deletion pipeline. It can be started from two places, but it always runs the same way:

- From settings: the user confirms, and the backend deletes the Clerk user through Clerk's API.
- From Clerk directly: a `user.deleted` webhook arrives.

In both cases the webhook handler then does the following:

1. Verifies the Svix signature and deduplicates on the event ID. A repeated delivery returns success.
2. Marks the user as deleting, so the gate starts rejecting them immediately.
3. Cancels the Stripe subscription.
4. Schedules bounded, resumable batches that delete `entries`, then `subscriptions`, and finally the `users` row.
5. Writes an `accountClosures` record holding a one-way hash of the subject, with `origin: "provider_deleted"` and an expiry set comfortably past the longest token lifetime. `users.ensure` refuses any subject that has a closure record, so a token issued before the deletion can't recreate the account.

## URL structure (app.`<apex>`)

There is no tenancy segment. Every route in the app belongs to the signed-in user, and there is only ever one possible account for any URL, so a segment like `/u/[id]/...` would carry no information. Paths start directly at the product nouns.

```text
/                          → replace → /today
/auth                      sign in or sign up (Clerk), ?return=<relative path>
/today                     resolver: today's entry → replace → /entries/[id]
/entries                   collection view: the calendar, ?month=YYYY-MM
/entries/[id]              one entry: read and edit
/search                    full-text search, ?q=<text>
/settings                  → replace → /settings/preferences
/settings/preferences      timezone, editor and display preferences
/settings/account          profile, sign-in methods (Clerk panel in modal mode), delete account
/settings/billing          plan, checkout, Stripe Customer Portal
```

The site at `<apex>` carries `/`, `/pricing`, `/privacy`, and `/terms`. Google's OAuth verification needs `/privacy` and `/terms` to exist and be public before sign-in can go live.

### Decisions

- **Entries are addressed by a 12-character Base58 ID** (`/entries/7Kp3xQ9mVbZt`). The ID is minted by a single helper in `packages/domain`. Dates like `/entries/2026-10-18` were considered and rejected. They are easier to read, but they would make the day-uniqueness assumption a permanent part of every bookmarked link, and they put the date of a private record into URLs, browser history, and logs. Opaque IDs avoid both problems.
- **`/today` is a resolver, not a second URL for an entry.** It calls `entries.ensureForDate(today)`, which is idempotent, and then navigates with a history replace to `/entries/[id]`. So Back never lands on `/today`, and every entry has exactly one canonical URL. Clicking an empty past day in the calendar calls the same mutation and pushes `/entries/[id]`.
- **The calendar is the `/entries` collection**, following the convention that the bare prefix shows the collection and items live directly under it. The month is URL state: `?month=2026-10`, omitted when it's the current month. Rendering it as a calendar is a presentation choice. If a list view is added later, it becomes `?view=list` on the same route, not a new path.
- **Search is a leaf page, `/search?q=…`.** `q` is updated with history replace while the user types (debounced), so the search stays shareable and survives a reload. Search results link to `/entries/[id]`.
- **Settings has three tabs, and the bare `/settings` resolves to `/settings/preferences`.** Clerk's profile panel opens in modal mode over `/settings/account`, so Clerk's own sub-routes never become part of our URLs.
- All query-string parsing and serialization (`month`, `q`, `return`) lives in `packages/domain`, with contract tests. Unknown formats are rejected and fall back to defaults.
- A bad or someone else's entry ID shows the product's own "This entry isn't here" screen, with a link to `/today`.
- Navigation inside the app is client-side and uses relative paths. The app shell (header and nav) stays mounted between routes. The editor saves as the user types, with optimistic updates and the Convex live subscription keeping state in sync, so a second open tab updates live.

## Assumptions (made without the owner)

1. The domain is not chosen yet. The plan uses the apex for the site and `app.` for the app.
2. The social providers are Google and Apple, plus passwordless email codes.
3. There is one entry per calendar day, and an entry's date never changes.
4. Entries are rich text (BlockNote), with no attachments.
5. Deleting an entry is permanent after a confirmation dialog, with no trash.
6. A lapsed subscription never blocks reading, searching, deleting, or account deletion.
7. "Visible only to the person who wrote them" is enforced against other users and against operator tooling, with encryption at rest from the provider. It is not end-to-end encryption (see question 1).
8. The private app is a Vite SPA and the public site is Next.js, deployed separately.

## Open questions for the owner

1. **End-to-end encryption.** Does the privacy promise extend to *us*? If it does, entries have to be encrypted on the device, which means:
   - server-side full-text search goes away (it would have to run on the device over decrypted entries);
   - a lost key means lost entries;
   - the data model and search plan above change.

   This is the biggest open decision and it should be made before the entry schema is built. My recommendation is to ship v1 as described here and to word the marketing claim precisely ("no one else can see your entries; we never read them"), unless E2E encryption is meant to be a selling point.
2. **What does the paid plan unlock, and is there a free tier or trial?** That decides what the billing gate turns off when a subscription lapses (assumption 6 limits it).
3. **Multiple entries per day?** If yes, `/today` becomes a list of the day's entries, and the calendar shows a count per day. The URLs stay the same.
4. **Data export** (Markdown or JSON download). It isn't in the brief, but it backs up a privacy pitch. If added, it goes under `/settings/account`.

## If the brief changes

If sharing or teams are ever added, that's a migration. Entries would be re-keyed from `userId` to a workspace backed by Clerk Organizations, and routes would gain a `/w/[workspaceId]` prefix, with redirects from the current paths. The brief says this will not happen, so nothing here is built for it.

````

> Result: File created successfully at: C:\tmp\wro-eval3\builds\3-solo-product-without-workspaces-old-opus\work\docs\architecture.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/architecture.md`. It's a planning document only: nothing is built, and I haven't committed it. The main calls:

**Auth**
- Sign-in uses Clerk, with Google, Apple and email one-time codes (no passwords).
- There's a single `/auth` page on `app.<domain>`. After signing in, people return to the page they were trying to open.
- Each environment (dev and production) gets its own OAuth credentials. Clerk's Organizations feature stays off.
- Every backend function goes through one shared check that confirms who the user is and that they own the record.
- If an entry belongs to someone else, the response is the same as if it doesn't exist.
- On every sign-in the app finds or creates the user's record, rather than relying on Clerk's webhook alone.

**Data ownership**
- **The account is the ownership boundary.** I didn't add a workspace or team layer, because the brief rules out sharing for good.
- Clerk owns identity and Stripe owns subscription status. Convex (the database) owns users, entries, settings and search.
- Each user has one Stripe customer.
- Search covers the full text of entries, but only ever within the signed-in user's own entries.
- No admin tool or log ever exposes what someone wrote.
- Deleting an account is one process, whether it starts in settings or in Clerk. It deletes everything in batches and keeps a small record so an old sign-in token can't recreate the account.

**URLs**
| Path | What it shows |
| --- | --- |
| `/` | Goes to `/today` |
| `/today` | Opens today's entry at `/entries/[id]` |
| `/entries?month=YYYY-MM` | The calendar of past entries |
| `/entries/[id]` | One entry |
| `/search?q=` | Search |
| `/settings/{preferences,account,billing}` | Settings |

Entry links use a short random ID rather than the date. Date-based links would lock "one entry per day" into every saved link and put a private record's date into browser history and logs.

**Assumptions I made** (all listed in the doc):
- The domain isn't chosen yet, so the doc uses a placeholder.
- Google and Apple are the social sign-in options.
- One entry per day, and an entry's date can't change.
- Entries are rich text, with no attachments.
- Deleting an entry is permanent after a confirmation, with no trash.
- A lapsed subscription never blocks reading, searching or deleting your own entries.
- "Private" means no other user and no admin tooling can see entries. It doesn't mean encryption on the device.

**Questions for you:**
1. **Should the privacy promise extend to us?** If entries must be unreadable even to us, they need to be encrypted on the device. That breaks server-side search, means a lost key loses the entries, and changes how entries are stored. This is the most important decision, and ideally it's made before entries are built.
2. **What does the paid plan unlock?** Is there a free tier or a trial?
3. **Can someone write more than one entry per day?** The URLs above would still work either way.
4. **Do you want a data export?** It isn't in the brief, but it would back up the privacy pitch.

**Session ended:** success, 9 turns, 147048 ms
