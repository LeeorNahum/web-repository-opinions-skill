I've written `docs/downgrade-policy.md`. It isn't committed, since you didn't ask for that. The repo has no backend code yet, so the enforcement section describes how the backend should work rather than code that exists.

**The rules in short.** When the paid period ends, nothing is deleted or locked. The user keeps everything but can't grow past Free limits or change books that Free doesn't cover.
- **Books (25):** the 25 oldest books by creation date stay editable. The rest become read-only: the user can still view, export, order prints of, trash, restore and permanently delete them. Creating a new book needs fewer than 25 active books. Trashing an editable book makes the next-oldest read-only book editable.
- **Photos (40 MB):** this limit only applies to new uploads. Photos already stored at up to 120 MB keep working.
- **Storage (1.5 GB):** includes Trash. While over the limit, any upload is refused. Editing that doesn't add photos still works.

**Your typical case.** The 25 oldest books stay editable and the 15 newest become read-only. All uploads are blocked: emptying Trash brings them to 2.3 GB, so they'd still need to delete 0.8 GB more. The fifteen large photos stay usable, nothing is lost, and resubscribing makes everything editable again straight away. Every rule gave a clear answer for this case without needing an exception.

**Enforcement.** The billing provider decides whether the user is on Pro. Whether a book is editable is worked out on every request; there's no "locked" flag stored and no job that sets one. A single set of checks sits inside the backend actions that the web app, public API, MCP connection and background jobs all go through. Refusals use set error codes with your own wording, and the user sees them only where they hit the limit, with two options: upgrade or free up space. Two edge cases are covered:
- An upload that was approved before the cutoff can still finish after it.
- If the billing provider's "subscription ended" notice arrives late, the user still drops to Free at the period end. A late renewal notice never downgrades a paying user.

**Calls I made for you** (listed at the end of the doc, each easy to reverse):
1. **Oldest 25 stay editable, not newest:** the books added beyond the Free allowance are the ones that freeze. Letting users pick their 25 would mean storing their choice.
2. **Read-only books can still have prints ordered:** export is allowed anyway, so blocking orders would only send print sales elsewhere.
3. **Trash counts toward storage but not the book count.**
4. **Restoring from Trash is always allowed:** otherwise the 14-day Trash would become data loss. The catch is that restoring an old book can make a newer one read-only.
5. **The 40 MB limit only applies when uploading.**
6. **No grace period or reminder emails:** neither is in the brief.
7. **The API refuses with error code 403** rather than 402.
8. **The same rules apply to any end of Pro,** such as a failed payment, not only a cancellation.