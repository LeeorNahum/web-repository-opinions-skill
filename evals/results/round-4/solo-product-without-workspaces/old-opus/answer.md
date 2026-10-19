I've written the plan to `docs/architecture.md`. It's a planning document only: nothing is built, and I haven't committed it. The main calls:

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