I wrote the plan to `docs/architecture.md`. I didn't commit it, and nothing has been built.

**The main decision: no workspaces at all.** The usual approach is to add a workspace layer early in case teams arrive later. Your brief rules out sharing and teams for good, so I left it out. Each user owns their own data, Clerk's organization feature stays off, and URLs carry no workspace segment. The doc says plainly that adding sharing later would contradict the brief.

**Auth**
- Clerk handles sign-in, with Google and Apple plus email sign-in by code or magic link, and no passwords.
- Sign-in lives at a single `/auth` page. After signing in, people land back on the page they were trying to open; only links within the app are accepted.
- On every visit, the app makes sure the person's account record exists before it loads any entries. It doesn't depend on a webhook having arrived first.

**Data ownership**
- Entries belong to the user. Every read and write goes through one check that takes the user from the verified session, never from anything the browser sends.
- If someone opens an entry that isn't theirs, they get the same "not found" as for an entry that doesn't exist. So nobody can learn whether an entry exists by guessing links.
- Search is limited to the person's own entries inside the search index itself, not filtered afterwards.
- Stripe is the authority on subscriptions; the app keeps a copy updated by Stripe's notifications.
- Deleting an account offers an export first, then removes everything in steps. A small record of the closed account stays so an old sign-in can't quietly recreate it.

**URLs** (on `app.marrowjournal.com`)
- `/` takes you to today's entry, or to a blank entry for today if none exists yet.
- `/entries` is the calendar, with `?month=2026-10` for the month shown.
- `/entries/[id]` is one entry. Each entry has a random short ID, and that is its only address.
- `/entries/new?date=…` starts an entry for an empty day. Once saved, the address switches to the entry's own.
- `/search?q=…` is search.
- `/settings/account` and `/settings/billing` are settings.
- Entries use IDs rather than dates in their links so links survive a corrected date or several entries a day later on.

**Assumptions to confirm** (all listed in the doc):
1. **Not end-to-end encrypted.** This is the biggest call. "Visible only to the writer" could mean "not even us." True end-to-end encryption would rule out search on our servers and make account recovery much harder. The plan instead relies on standard encryption at rest plus a rule that staff can never see entry content, which should also go on the privacy page.
2. **A lapsed subscription never locks people out of their entries.** They can still read, search, export and delete; only writing needs an active plan. Whether there's a free tier or trial is still open.
3. **One entry per day.** Past days can be filled in later; future days can't. "Today" follows a time zone the user can change.
4. **Smaller defaults:** Google and Apple for social sign-in, rich-text entries with no images, 30 days in the trash before deletion, and the domain `marrowjournal.com`, which I haven't checked is registered.