I've written the plan to `docs/architecture.md`. It's a document only: nothing is built, committed, or set up with any provider.

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