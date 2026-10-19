I've written `docs/downgrade-policy.md`. I haven't committed it.

**The policy:** when the paid period ends, the user keeps everything. It all stays viewable, downloadable, printable and deletable. What stops is growth beyond the Free limits, plus editing of the books that don't fit in Free's 25.

- **Books:** the 25 oldest books not in Trash stay editable. The rest become read-only: they can still be viewed, exported, ordered as prints, trashed and deleted, but not edited. Creating a book needs fewer than 25 books outside Trash. The user picks which books stay editable by trashing others.
- **Storage:** at or over 1.5 GB, uploads are refused, but edits that don't add bytes still work, such as rearranging pages or reusing photos already uploaded. Trash counts toward storage until it is permanently emptied.
- **Large photos:** anything over 40 MB that's already stored is kept at full size and still prints. Only new uploads must be 40 MB or less.
- **Enforcement:** the plan is read from the billing provider and the limits are constants in code. Which books stay editable is worked out on every request, so no "locked" flag is ever stored. The browser app, API, MCP connection and background jobs all go through the same four checks, each with its own error code. Uploads are checked again when they finish, so one that started on Pro and lands after the period ends meets Free limits. Resubscribing restores everything instantly.

There's no backend code in the repo yet, so the enforcement section is a contract for whoever builds it, not a description of existing code.

**Checked against the typical case in `docs/brief.md`:**
- **Books:** 25 of the 40 stay editable and 15 become read-only. Creating a new book means trashing 16.
- **Storage:** 2.6 GB is 1.1 GB over the limit. Emptying Trash brings it to 2.3 GB, still 0.8 GB over, so uploads stay blocked until more is permanently deleted.
- **Large photos:** all fifteen are kept as they are.
- Nothing is lost except the 300 MB the user had already put in Trash.

**Calls I made (listed in the doc for you to confirm):**
1. Which books stay editable is decided by oldest first, not most recently edited.
2. Books in Trash don't count toward the 25-book limit, but do count toward storage.
3. Read-only books can still be ordered as prints.
4. Storage means uploaded photo bytes only. Thumbnails and print files the product generates don't count.
5. Restoring from Trash is always allowed, even if that makes a different book read-only.
6. "Empty Trash" and "Delete permanently" need to exist, because they're the only way to free space immediately.
7. Failed payments follow whatever status the billing provider reports. Any grace period needs its own decision.
8. Refusals come back from the API as HTTP 403 with an error code.
9. Books belong to one account, with no shared workspaces.

The ones most likely to need your call are 1 and 3.