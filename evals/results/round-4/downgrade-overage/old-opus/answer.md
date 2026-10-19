I've written `docs/downgrade-policy.md`. It isn't committed. The repo has no backend code yet, so the enforcement section describes what the backend has to implement rather than code that exists.

**The rules.** Nothing is deleted or shrunk when Pro ends. The Free limits only control what's new or editable:
- **Books:** the 25 oldest books not in Trash stay editable. The rest become view-only: users can still view, export, print and move them to Trash, but not edit or duplicate them. Creating a new book is blocked while they have 25 or more.
- **Storage (1.5 GB):** photos in Trash still count until they're purged. Being over the limit only blocks new uploads; nothing becomes read-only because of it.
- **Per-photo limit (40 MB):** this only applies to new uploads. Photos already stored that are bigger stay usable and printable at full size.
- **Always allowed:** viewing, exporting, ordering prints, moving to Trash, restoring and permanent delete. Users can always get back under the limits without paying.

**Checked against the typical case:**
- **40 books:** the newest 15 become view-only. Moving 15 books to Trash makes all the remaining 25 editable immediately.
- **2.6 GB stored:** uploads are blocked. After the 300 MB in Trash is purged they're at 2.3 GB, still 0.8 GB over, so uploads stay blocked until they free more than 1.1 GB.
- **Fifteen 60–110 MB photos:** unaffected.

**Enforcement.** The billing provider stays the authority on the subscription, and the backend keeps a copy updated by its webhooks. The limits are constants in code. Three backend checks cover everything: editing a book, creating a book, and uploading a photo. The web app, API, MCP and background jobs all go through them. Which books are editable is worked out on every request from the current plan, so nothing is stored per book and re-subscribing restores everything instantly. The size check runs both when an upload starts and when it finishes. Each check returns its own error code with plain-language messages, and upgrading is offered in all of them because Pro raises each limit.

**Calls I made for you to confirm** (all listed at the end of the doc):
1. **Which books stay editable:** the oldest 25, rather than the most recently edited or ones the user picks.
2. **Printing:** view-only books can still be printed. Add a check on print orders if you'd rather not allow that.
3. **What counts toward which limit:** books in Trash don't count toward the 25, but their photos count toward storage.
4. **Deleting early:** users can permanently delete from Trash before the 14 days are up. The brief doesn't mention this, and without it the only way to free storage is waiting for the purge.
5. **How photos are stored:** a photo used in several books is stored and counted once, and edits like crop or rotate don't add storage.
6. **Other limits:** pages, photos per book and print orders have none, since the brief lists none.
7. **Units:** binary (1 GB = 2^30 bytes). Failed payments follow the same rules once the billing provider ends the subscription.