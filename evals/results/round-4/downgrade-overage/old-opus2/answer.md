I've written `docs/downgrade-policy.md`. It's a policy document only: there's no backend code in the repo yet, so the enforcement section is a design to build, not a description of existing code. I haven't committed it.

**The rules once the paid period ends:**
- **Nothing is deleted or degraded.** Only the normal 14-day Trash purge ever removes data. Resubscribing restores everything instantly, because nothing gets marked "locked" on a book or photo.
- **Books:** the 25 oldest active books stay fully editable. The rest become read-only, but the user can still view, download, print, trash and remove things from them. They can't create a new book until they have fewer than 25 active ones. Trashing a book lets the next-oldest one become editable.
- **Storage:** nothing that adds bytes is allowed while the account is over 1.5 GB. Bytes in Trash count until they're purged. Edits that add no bytes still work in the editable books.
- **Photo size:** the 40 MB limit applies only to new uploads. Existing larger photos stay at full size and usable, but couldn't be uploaded again on Free.
- **Enforcement:** one set of backend checks used by the browser app, the API, MCP and user-triggered jobs. Which books are editable is worked out from the current subscription each time an operation runs. Uploads are checked before any bytes move, and usage is counted after the upload succeeds. Blocks return one of four error codes, each naming the limit it hit.

**The typical case from the brief:** 15 of the 40 books become read-only, and uploads are blocked because 2.6 GB is 1.1 GB over the limit. Once Trash purges, usage is 2.3 GB, still 0.8 GB over. Removing some of the 15 large photos is the quickest way back under. Every block has something the user can do about it on their own, and nothing is lost.

**Assumptions to check tomorrow (all listed at the end of the doc):**
1. **Printing read-only books is allowed.** I treated a print order as read-only use. Of all the calls, this is the one I'd look at first: a former Pro user could keep ordering prints of up to 60 books indefinitely.
2. **The oldest books stay editable, and the user can't choose which.** They control it by trashing books instead.
3. **Trash counts toward storage but not toward the 25-book limit.**
4. **The 40 books in the typical case are all active, not in Trash.**
5. **Removing photos or pages from a read-only book is allowed.**
6. **"GB" and "MB" are read as binary units**, which is slightly more generous to users.
7. **No grace period after the paid period ends**, though an upload started just before it ends can still finish.
8. **No downgrade email or warning banner.** Limits are shown when an action hits them and on the billing page.

I didn't change any plan limits; those stay your call.