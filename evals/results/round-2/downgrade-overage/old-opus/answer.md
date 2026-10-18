I've written `docs/downgrade-policy.md` and left it uncommitted. The repo has no app code yet, so the enforcement section is a design for the backend, not a description of code that exists.

**The rules:**
- **Nothing is deleted because of cancelling.** The user keeps full Pro until the billing provider says the paid period has ended. After that, the only thing that ever deletes data is the existing 14-day Trash rule.
- **Books (Free allows 25):** the 25 oldest books not in Trash stay fully editable. The rest become read-only: the user can still view, export, order prints of, move to Trash and delete them, but can't edit them. A new book can only be created once the user has fewer than 25.
- **Storage (Free allows 1.5 GB):** while over the limit, uploads are blocked. Editing with photos already uploaded still works.
- **Photo size (Free allows 40 MB per photo):** the limit only applies to new uploads. Larger photos already stored stay at full resolution and still print.
- **Enforcement:** there are three checks in one shared layer that the browser app, API, MCP and background jobs all call. Each works out the answer from the current plan every time; no "locked" flag is stored on anything. Re-subscribing restores everything instantly. A blocked action returns a clear error that names the limit and how to clear it.

**The typical case from the brief** (40 books, 2.6 GB with 300 MB in Trash, fifteen 60–110 MB photos): after the period ends, 25 books are editable and 15 are view-only. All uploads stop because they're 1.1 GB over. Even after the Trash empties itself they're still at 2.3 GB, so they need to delete about 0.8 GB more before uploading again. All 15 large photos stay usable. To create a book they'd need to move 16 books to Trash.

**Calls I made without you** (all listed at the end of the doc for your sign-off):
1. The oldest 25 books stay editable, and users can't pick which ones. They can change the set by moving books to Trash.
2. Printed copies can still be ordered for read-only books, since orders are paid separately and use no plan allowance.
3. Photos in Trash count toward storage until permanently removed. Books in Trash don't count toward the 25.
4. Users can empty Trash themselves rather than wait 14 days. That action may not exist yet.
5. There's no grace period after the paid period. Failed payments are out of scope.
6. Crops and rotations don't count as uploads.
7. Being over the storage limit only blocks uploads, not editing.
8. The cancellation screen and billing page warn the user what will change. Whether to also send an email is still open.

One combined effect to look at first: because photos in Trash still count, moving books to Trash to get under 25 doesn't free any storage until the Trash is emptied.