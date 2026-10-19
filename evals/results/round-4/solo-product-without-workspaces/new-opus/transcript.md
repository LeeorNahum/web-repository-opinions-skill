**Prompt:** Plan the auth setup, data ownership, and URL structure for Marrow Journal's signed-in app, and write it to docs/architecture.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus/work\" && git ls-files | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 4812 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat auth.md workspace-tenancy.md bootstrap.md"}`

> Result: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 20105 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat routing.md ids.md query-state.md app-surface.md domains.md"}`

> Result: # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix [... 20908 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat data-model.md source-of-truth.md billing.md search-indexing.md data-deletion.md origins.md"}`

> Result: # Data Model  Model entities around the product's core object and the ownership boundary that protects them.  When many users can reference the same object, model the shared object separately from each user's relationship and relationship-owned metadata. Define object deletion independently from relationship deletion.  Value precedence is fixed: user-edited values outrank generated values, a [... 14616 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-solo-product-without-workspaces-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat spa-feel.md rendering.md live-data.md modularity.md monorepo-layout.md naming.md | head -400; cat ../../../../package.json ../../../../pnpm-workspace.yaml"}`

> Result: # SPA Feel  A signed-in app should feel like one continuous application, not a series of full page loads, while keeping real URLs.  Achieve the feel with:  - Persistent layouts and shells that survive navigation - Client-side navigation between routes - Drawers, sheets, and modals for secondary flows instead of new pages - A persistent element where it fits the product, such as a mini-pla [... 13570 more characters]

**Tool call `Write`:** `<run>/builds/4-solo-product-without-workspaces-new-opus/work/docs/architecture.md`

````text
# Marrow Journal: signed-in app architecture

This covers auth, data ownership, and URL structure for the signed-in app. `docs/brief.md` holds the owner's decisions. If this document disagrees with the brief, the brief is right and this document needs fixing.

Status: draft, written while the owner was away. Calls made without the owner are tagged **[Assumed]** and gathered in [Open questions](#open-questions) at the end.

## Shape of the product

- The app has one owner per journal. The brief rules out sharing, teams, and collaborators permanently, so there are **no workspaces and no organizations**. All data belongs to the user account. No tenancy segment appears in URLs, and the auth provider's organization feature stays off.
- The core object is the **entry**. Today's entry is the home screen. The calendar, search, and settings exist to lead back to entries.
- **[Assumed]** Each user gets at most **one entry per calendar day**. "Today's entry" in the brief and "a calendar of past entries" both read as day-keyed.

## Surfaces and hosts

| Surface | Folder | Host (prod) | Host (staging) | Rendering |
| --- | --- | --- | --- | --- |
| Public site (marketing, pricing, privacy, terms) | `apps/site` | `<apex>` | `preview.<apex>` | Next.js, static or server-rendered |
| Signed-in app | `apps/app` | `app.<apex>` | `preview.app.<apex>` | Vite SPA, client-rendered behind auth |

Shared code lives in packages:

- `packages/backend`: Convex schema, functions, the auth gate, Stripe and Clerk adapters, and jobs.
- `packages/domain`: route builders, query-state parsers, entry-ID helper, capability names, plan constants, origin resolvers, and the date and "today" rules.
- `packages/config`: shared TypeScript and tooling config.

**[Assumed]** The domain hasn't been chosen, so `<apex>` stands in for it. The site gets the apex and the app gets `app.`, with no `www` (redirect it at the edge if it exists). Canonical origins are constants in `packages/domain`, and cross-surface links always go through its resolvers.

The app is never server-rendered. Entries are visible to one person only, so no server render, edge cache, or prerender should ever hold entry content.

## Auth

**Provider: Clerk**, used as a managed provider. The product never stores passwords and never verifies email itself.

- **One route: `/auth`** on the app host. It uses Clerk's combined sign-in-or-up component, with no separate sign-up or callback paths.
- **Returning to the original page:** any signed-out hit on a private route goes to `/auth?redirect=<path>`. The destination is derived once in the app's auth guard from the interrupted URL, and it's accepted only as a same-origin relative path (it must start with a single `/`, with no scheme or host). Anything else falls back to `/today`.
- **Sign-in methods:**
  - **[Assumed]** Social sign-in is Google and Apple. Apple matters if a mobile app ever ships.
  - Email is enabled as an identifier, using **[Assumed]** email verification codes with passwords **off**. That leaves no password-reset surface and fits the privacy positioning. Turning passwords on is a single Clerk setting and causes no architecture change.
  - Account linking works by verified email, so Google and email sign-in with the same address land in one account.
- **OAuth credentials:** each social provider and each Clerk instance (development and production) gets its own custom credentials, so the account-selector prompt works and a leak in one stage doesn't spread to the other.
- **Clerk Organizations:** off.
- **Account UI:** `/settings/account` is a page the product owns. It opens Clerk's `UserProfile` in **modal** mode for email, connected accounts, and sessions. That keeps Clerk's internal sub-routes out of our URL contract.

### Bootstrap on every authenticated entry

Every route that can be opened directly runs these steps in order:

1. Wait for Clerk's session, then connect the Convex client with the Clerk JWT, before any query subscribes.
2. Call `ensureUser`. It finds the app user by Clerk subject or creates one, records the browser time zone on first creation, and refuses if a closure tombstone exists for that subject (see [Deletion](#deletion)).
3. Only then subscribe to entry queries.

The Clerk `user.created` webhook is an optimization and not the source of the row. If the first login ever needs a page refresh to work, that's an ordering bug.

### One authorization gate

All entry and account access goes through Convex functions built from a single wrapper in `packages/backend`, and raw `query`/`mutation` aren't exported for product data. The wrapper:

- verifies identity from the Clerk-issued JWT. The issuer is always checked. **[Assumed]** The audience is checked only if our JWT template mints one, and the code comments explain why.
- resolves the app user by subject and checks it isn't closed.
- checks a named **capability**. There's only one role (the account owner), but capabilities are still named so every client asks the same question: `entry.read`, `entry.write`, `entry.delete`, `account.export`, `account.delete`, `billing.manage`. Unknown capabilities fail closed.
- for anything that addresses an entry, loads it and requires `entry.userId === caller.id`.

**Missing entries and entries owned by someone else return the same product-owned "not found".** The app never reveals whether another user's entry ID exists.

Plan gating (what a subscription unlocks) is a separate billing check and is kept out of this gate.

## Data ownership

### Who owns which fact

| Fact | Owner |
| --- | --- |
| Login identity, emails, connected accounts, sessions | Clerk |
| Subscription and payment state | Stripe (a last-known mirror on the user row, updated by webhooks, is used only for gating reads) |
| Entries, user preferences, closure tombstones, derived search text | Convex |
| Route shapes, ID format, plan names and limits, "what day is today" rule | `packages/domain` (code, not env) |
| Per-stage keys and origins | Hosting and provider env stores, with the same key names in every stage |

**[Assumed]** Entries are text only for now (BlockNote block JSON), so there's no object storage. If images or audio are added later, the bytes go to R2 and Convex keeps the keys.

### Schema sketch

```text
users
  id               12-char Base58 (shared helper), never shown in URLs today
  authSubject      Clerk subject; indexed, unique
  timeZone         IANA name, auto-detected at creation, editable in settings
  stripeCustomerId optional
  subscription     last-known mirror: { status, planKey, currentPeriodEnd } | null
  createdAt
  deletingAt       optional; set when account deletion starts (hides everything)

entries
  id               12-char Base58, the URL identity
  userId           owner; every index starts with it
  date             "YYYY-MM-DD" in the owner's time zone at creation; unique per userId
  body             block JSON
  searchText       derived by one builder from body; never written independently
  createdAt, updatedAt

closedAccounts
  subjectHash      one-way hash of the Clerk subject
  closedAt
  origin           "provider" | "product" (required, no default)
  expiresAt        set only for origin "provider"
```

Indexes: `entries.by_user_date (userId, date)` for today, the calendar, and uniqueness. `entries.search_text` is a search index on `searchText` with `userId` as a required filter field, so a search can never cross users.

### Rules

- **Today** is computed from `users.timeZone` in the domain package and is never stored. An entry's `date` is fixed when it's created. Changing time zone later doesn't move existing entries.
- **[Assumed]** Past days can be written into (backfilled). Future days are refused.
- **Search covers the full entry text.** Indexing only metadata would make search useless for a journal. The privacy cost is accepted on these conditions: `searchText` is built by one helper used on every write, it's scoped by `userId` inside the index, it's deleted along with its entry, and it's never logged.
- **Privacy rules in code:** entry bodies and search queries are never written to logs, error reports, analytics, or job payloads. Jobs carry IDs only. No admin or support surface can read entry content, and an admin surface is out of scope for v1.
- **[Assumed]** Deleting an entry is a **hard delete** after an in-app confirmation, with no trash. That fits "only you can see it", and it means no copy is kept that the user didn't ask for.

### Billing

- Stripe subscription, one subscriber per account: the Stripe customer maps 1:1 to the app user, and the user ID is stored in Stripe customer metadata.
- Checkout and the customer portal are Stripe-hosted, reached from `/settings/billing`. Stripe webhooks are signature-verified, deduplicated by event ID, and update only the `subscription` mirror.
- Test mode in dev and preview, live mode only in production.
- **[Assumed]** Losing or never having a subscription never blocks **reading, searching, exporting, or deleting** your own entries. A journal held hostage would contradict the product's pitch. What the paid plan unlocks is still open (see questions).

### Deletion

- **Account deletion** starts in `/settings/data`. The app deletes the Clerk user. Clerk's `user.deleted` webhook (signature-verified, deduplicated by event ID, idempotent on redelivery) then:
  1. sets `deletingAt`, which immediately hides all data from every query.
  2. cancels the Stripe subscription.
  3. writes a `closedAccounts` tombstone with origin `provider`, set to expire well beyond the longest Clerk token lifetime.
  4. schedules a bounded, resumable job that deletes entries in batches (search text goes with each row) and deletes the `users` row last.
- If the product ever closes an account while the Clerk identity still exists (for example, an abuse ban), the tombstone origin is `product` and it **never expires**.
- **Export:** `/settings/data` offers a full export of the user's entries. **[Assumed]** The format is Markdown files in a zip, plus JSON. Export isn't gated by plan.

## URL structure

All of these are on `app.<apex>`. IDs are 12-character Base58 entry IDs. Route builders and query parsers live in `packages/domain`. Same-app links are relative.

| Path | What it is |
| --- | --- |
| `/` | Resolves with a **history replace** to `/today`. |
| `/auth` | Clerk sign-in-or-up. Accepts `?redirect=<same-origin path>`. |
| `/today` | Resolver, replaced in history. If today's entry exists it goes to `/entries/<id>`, otherwise to `/entries/new?date=<today>`. Safe to bookmark, and always means "today". |
| `/entries` | The entries collection, shown as the **calendar**. `?month=YYYY-MM`, omitted for the current month. The nav label is "Calendar", but there's no separate `/calendar` path. |
| `/entries/new?date=YYYY-MM-DD` | Blank composer for a day. The first save creates the entry and **replaces** the URL with `/entries/<id>`. If an entry already exists for that date, it replaces straight to it. A future or malformed date replaces to `/today`. |
| `/entries/<id>` | One entry, read and edit in place, with autosave and live updates. It has no tabs, so this URL is the view. Not-found looks the same as not-yours. |
| `/search?q=…` | Full-text search over your entries. Typing updates `q` with history replace (debounced). An empty `q` is omitted. Results link to `/entries/<id>`. |
| `/settings` | Resolves with a replace to `/settings/account`. |
| `/settings/account` | Name, time zone, and a button that opens Clerk's `UserProfile` modal. |
| `/settings/billing` | Plan status, plus links out to Stripe Checkout or the portal. Stripe return URLs come back here. |
| `/settings/data` | Export and account deletion. |

Why the URLs look like this:

- **Entry URLs use opaque IDs, not dates.** A date-keyed URL would turn the URL into the entry's identity and lock in the one-per-day rule. An ID keeps each entry at one stable canonical link. The calendar and `/today` both link by ID.
- **There's no tenancy segment**, because there's no tenancy. If the brief ever changed on sharing (it says it won't), that would be a new design and not a URL tweak.
- **No public URLs exist for entries**, and none will be added. Sharing is excluded by positioning, and a short ID in a private URL doesn't make anything shareable.
- The app shell (navigation for Today, Calendar, Search, Settings) persists across client-side navigation. Destructive confirmations are modals over the current URL.

## Environment notes

- Two Clerk instances (development and production), two Convex deployments (dev, used by local and preview, and prod), and Stripe test and live modes. Env key names are identical in every stage.
- OAuth redirect URIs, Clerk allowed origins, and webhook endpoints use the custom domains above, including `preview.app.<apex>`. Platform-generated hostnames are never used.
- Local ports: site on `3000`, app on `3001`.

## Open questions

Each of these needs a decision from the owner. The current default is in brackets.

1. **End-to-end encryption.** The brief says "visible only to the person who wrote them." This plan reads that as access control plus encryption at rest on the provider, with operators kept out by policy and tooling. It does **not** read it as cryptographic zero-access. Real E2EE would rule out server-side search, rule out live sync as designed, and make lost-key recovery impossible. This is the biggest call in the document. [Not E2EE]
2. **What the paid plan unlocks**, and whether there's a free tier or a trial. [Undecided. Whatever happens, reading, export, and deletion are never gated]
3. **One entry per day** compared with multiple entries per day. [One per day. Entry URLs are ID-based, so changing this later doesn't break links]
4. **Backfilling past days.** [Allowed. Future days refused]
5. **Entry deletion**: hard delete compared with a recoverable trash. [Hard delete after confirmation]
6. **Social providers** and whether passwords are allowed. [Google and Apple, plus email codes. No passwords]
7. **Production domain.** [`<apex>` placeholder, with the app on `app.`]
8. **Export format.** [Markdown and JSON in a zip]

````

> Result: File created successfully at: <run>/builds/4-solo-product-without-workspaces-new-opus/work/docs/architecture.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/architecture.md`. It isn't committed, and the top of the doc says `docs/brief.md` wins if the two ever disagree.

**Decisions I made:**
- **No workspaces or organizations.** Your brief permanently rules out sharing, so every piece of data belongs to the user account. URLs have no team or workspace segment, and Clerk's organization feature stays off.
- **Sign-in:**
  - Clerk handles it on a single `/auth` page with one combined sign-in-or-sign-up form. After signing in, people go back to the page they were trying to open.
  - Each stage (development and production) gets its own Google and Apple login credentials.
  - Email sign-in uses one-time codes, with passwords off.
  - Every data access goes through one server-side check: is this person signed in, is the account still open, and do they own this entry? Asking for someone else's entry gives the same "not found" as an entry that doesn't exist, so nobody can tell whether it's real.
- **Data:**
  - Clerk holds login identity, Stripe holds subscription state, and the Convex database holds entries and settings. Entries are keyed by user and date, one per day.
  - "Today" is worked out from the user's saved time zone rather than stored.
  - Search covers the full text of entries, but only ever searches your own.
  - Entry text never goes into logs, error reports, or analytics, and there's no admin view that can read it.
  - Deleting an account runs as a background cleanup job and leaves a record that blocks the old login from silently recreating the account.
- **URLs:**

  | Path | What it is |
  | --- | --- |
  | `/` | Redirects to `/today` |
  | `/today` | Opens today's entry, or a blank page for today if it hasn't been written yet |
  | `/entries?month=YYYY-MM` | The calendar |
  | `/entries/new?date=…` | Blank page for a given day; the first save gives it a permanent address |
  | `/entries/<id>` | One entry, addressed by a short random ID rather than its date |
  | `/search?q=…` | Search |
  | `/settings/account`, `/settings/billing`, `/settings/data` | Settings pages |

  The site is on the main domain and the app is on `app.<your domain>`.

**Main assumptions:** these are tagged in the doc and listed under "Open questions":
1. **End-to-end encryption.** I read "visible only to the person who wrote them" as strict access control plus the hosting provider's standard encryption. It doesn't mean even you can't read the data. True end-to-end encryption would rule out server-side search and the live-sync design, and a lost key would mean lost entries. This is the call I'd most like you to confirm.
2. **What the paid plan unlocks** is still undecided. Whatever you choose, I've assumed reading, searching, exporting and deleting your own entries are never behind the paywall.
3. **Entries:**
   - One entry per day.
   - Past days can be filled in later; future days can't.
   - Deleting an entry is permanent after a confirmation, with no trash.
4. **Sign-in options:** Google and Apple, plus email codes, with no passwords.
5. **Domain:** not chosen yet, so the doc uses a placeholder.
6. **Export:** a zip of Markdown and JSON files.

**Session ended:** success, 9 turns, 120590 ms
