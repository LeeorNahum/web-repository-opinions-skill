I've written the plan to `docs/architecture.md`. I didn't commit it, so it's waiting for your review. The main decisions:

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