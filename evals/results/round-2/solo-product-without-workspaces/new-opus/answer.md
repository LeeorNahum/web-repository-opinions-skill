I've written the plan to `docs/architecture.md`. Nothing is committed. The doc says `docs/brief.md` wins if the two ever disagree.

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