I've written the plan to `docs/architecture.md`. It isn't committed, and the top of the doc says `docs/brief.md` wins if the two ever disagree.

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