**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work && git ls-files && cat docs/brief.md"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5049 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work/.claude/skills/web-repository-opinions/references && cat billing.md quota.md data-deletion.md source-of-truth.md"}`

> Result: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 8335 more characters]

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work/.claude/skills/web-repository-opinions/references && cat user-facing-errors.md uploads.md | head -120; cat ../../../../package.json"}`

> Result: # User-Facing Errors  Treat every provider, framework, transport, database, and backend error as internal data. Convert failures into product-owned outcomes before they reach visible UI.  ## Boundary  - Return typed outcome codes for expected failures. - Map outcome codes to concise, actionable copy at a shared presentation boundary. - Use one context-specific fallback for unexpected failu [... 3538 more characters]

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work/docs/downgrade-policy.md`

````text
# Downgrade policy: Pro to Free

What a cancelled Pro user can and can't do with what they already have once the paid period ends, and how the backend enforces it. `docs/brief.md` takes precedence over this document. If they disagree, fix this document.

## Principles

1. **Nothing is deleted or degraded because the plan ended.** All books, pages, photos, and order history stay exactly as they were, at full resolution.
2. **Free limits gate new things, not existing ones.** The book limit decides which books can still be edited. The storage and per-photo limits only gate new uploads.
3. **Coverage is derived, not stored.** No flags or locks get written when the plan changes. Every gate reads the current plan and the current account state, so re-subscribing restores everything immediately and there's nothing to reconcile.
4. **One gate for every client.** The browser, the public API, MCP, and background jobs all call the same backend checks and get the same answer.

## Timeline

- **From cancelling until the end of the paid period:** still Pro, nothing changes. The cancel confirmation shows what will happen to *this* account (for example "15 of your 40 books will become view-only").
- **When the paid period ends:** the billing provider reports the subscription as ended and the account's limits become the Free limits. No job runs and no data changes.
- **On re-subscribing:** Pro limits apply again right away. Every book becomes editable and uploads are allowed again.

## Rules

Free limits: 25 books, 40 MB per uploaded photo, 1.5 GB total storage.

### Books

- **Live books** are books that aren't in Trash. Only live books count toward the 25-book limit.
- **Covered books** are the 25 oldest live books, ordered by creation time with the book ID breaking ties. Covered books work normally.
- **Uncovered books** are all other live books. They are **view-only**:
  - Allowed: open, view, download or export, order printed copies, reorder past prints, rename? **no** (see below), move to Trash.
  - Blocked: any change to content or settings, including rename, adding, removing or reordering pages, placing, moving or removing photos, and layout or text edits. Duplicating is blocked too, because it creates a book.
- **Creating a book** (new or duplicate) is blocked while the account has 25 or more live books.
- **Moving a book to Trash** is always allowed, for any book. This is the main way to get back under the limit.
- **Restoring from Trash** is always allowed. The restored book counts as live again and takes its place in creation order. Restoring an older book can therefore uncover the newest covered book. The restore confirmation says so when that will happen.
- Coverage is recalculated on every request. If the user trashes 15 books, the next 15 oldest become editable immediately, with no waiting.

### Storage (1.5 GB)

- **Used storage** is the total size of every stored photo the account owns, *including photos that only exist in Trash*, because those bytes are still held. Bytes are released when Trash is purged after 14 days, or earlier if the user permanently deletes them.
- A photo used in several books is counted once. It's released only when nothing references it anymore.
- **An upload is allowed only if** used storage plus the new photo's size is 1.5 GB or less.
- Being over the storage limit **doesn't** make anything read-only. Covered books stay fully editable with photos already stored, including placing an already-stored photo on another page or in another covered book, because that adds no bytes.

### Per-photo size (40 MB)

- Applies only when uploading or replacing a photo. A new photo over 40 MB is rejected.
- Photos already stored that are bigger than 40 MB stay as they are: viewable, placeable in covered books, downloadable, and printable at full resolution. They're never shrunk or deleted.

### Trash

- The 14-day Trash rule is the same on every plan. Downgrading doesn't shorten it or empty Trash.

## Typical case

A cancelled user with 40 books, 2.6 GB stored (300 MB of it in Trash), and fifteen photos of 60–110 MB.

| Item | Situation on Free | Result |
| --- | --- | --- |
| 40 live books | 15 over the 25-book limit | The 25 oldest stay editable. The 15 newest become view-only, and the user can still view, export, and print them. Creating a book is blocked. |
| 2.6 GB used | 1.1 GB over 1.5 GB | Every upload is blocked. Nothing else is affected. |
| 300 MB in Trash | Counts toward storage | Purged on its normal 14-day schedule. After that the account uses 2.3 GB, still 0.8 GB over, so uploads stay blocked. |
| Fifteen 60–110 MB photos | Over 40 MB, but already stored | Unaffected wherever they're placed. Uploading a new photo like them would be rejected. |

How this user gets back to full use on Free without paying:

- **Editing every remaining book:** move 15 books to Trash. Right after that, all 25 live books are covered. Nothing has to be permanently deleted for this.
- **Uploading again:** get used storage under 1.5 GB minus the size of the next photo. That means freeing more than 1.1 GB through permanent deletion or Trash purge. Trashing books only frees bytes once those books leave Trash, and only for photos no other book uses.
- **Or:** re-subscribe, and everything is back immediately.

Checks against the principles: nothing is lost (all 40 books and every large photo are still there). The user always has a free way back (Trash and deletion are never blocked). The UI, API, and MCP all report the same 15 books as view-only.

## Backend enforcement

There's no application code yet. This is the contract the backend has to implement.

### Plan and limits

- The billing provider owns subscription truth. The backend keeps a last-known mirror of each account's subscription status and period end, updated by the provider's webhooks, and reconciles it from the provider when a webhook is missed. The mirror is a cache, never the authority.
- Plan limits are constants in the shared domain package (for example `PLAN_LIMITS.free = { books: 25, photoBytes: 40 MB, storageBytes: 1.5 GB }`), not env values or dashboard settings.
- `getPlan(account)` returns `pro` while the subscription is active (including after cancelling, until the period ends) and `free` otherwise.

### Gates

All of these live in one backend module, and every mutation path calls them: web app functions, public API handlers, MCP tools, and background jobs.

| Gate | Called by | Rule |
| --- | --- | --- |
| `assertBookEditable(account, bookId)` | Every book, page, and placement mutation | The book is live and in `coveredBookIds(account)`. Pro covers every book. |
| `assertCanCreateBook(account)` | Create and duplicate | Live book count is below the plan's book limit. |
| `assertCanUpload(account, sizeBytes)` | Upload intent, and again at finalize | `sizeBytes` is within the per-photo limit, and used storage plus `sizeBytes` is within the storage limit. |
| *(no gate)* | View, export, print order, move to Trash, restore, permanent delete | Always allowed. |

- `coveredBookIds(account)` is computed on read: the first *N* live books ordered by `(createdAt, id)`, where *N* is the plan's book limit. It's never stored on the book.
- Used storage comes from a per-account byte counter. Every path that adds or releases photo bytes keeps it accurate, including upload finalize, permanent delete, the Trash purge job, and abandoned-upload cleanup. A reconciliation job can recompute it from photo records.
- Uploads check the size when the upload is requested, using the declared size, before any bytes move. They check again at finalize, using the stored object's real size and the plan at that moment. If finalize fails the check, the object is deleted and no usage is recorded. Usage is recorded only after finalize succeeds.
- Background jobs that change a book (for example layout regeneration) call `assertBookEditable` when they run, not only when they're enqueued. Print rendering only reads, so it isn't gated.

### Errors

Gates return typed outcome codes. Each surface turns these into its own product copy, and the API and MCP return the code along with a short message:

- `book_view_only`: "This book is view-only on the Free plan, which includes 25 editable books. Move other books to Trash or upgrade to Pro to edit it."
- `book_limit_reached`: "The Free plan includes 25 books. Move a book to Trash or upgrade to Pro to create another."
- `storage_full`: "This photo doesn't fit in your 1.5 GB of storage. Permanently delete photos or upgrade to Pro for 4 GB."
- `photo_too_large`: "Photos can be up to 40 MB on the Free plan (120 MB on Pro)."

Upgrade is a valid remedy for all four, because Pro raises each of these limits. Limits only appear when they're hit, or on the plan and usage page. There's no standing "over limit" banner. The exception is the cancel confirmation described in the Timeline section.

## Assumptions to confirm

These were decided without the owner and are easy to change:

1. **Which books stay editable:** the 25 oldest by creation date. The alternatives are most recently edited, or letting the user choose. "Oldest" is stable and needs nothing stored. A user-chosen set would need a stored preference.
2. **Uncovered books can still be printed.** Prints are a separate purchase of something the user already designed. Blocking them would hold finished work hostage and lose order revenue. If printing should be a Pro benefit for books over the limit, add a gate on print orders.
3. **Trashed books don't count toward the book limit, but their photos count toward storage** until purge or permanent delete.
4. **A user can permanently delete from Trash early.** The brief only describes the 14-day purge. If that action doesn't exist, the only way to free storage is waiting out the purge.
5. **Photos are stored once and referenced from books**, so placing an existing photo adds no bytes and shared photos are counted once.
6. **Edits like crop or rotate are stored as settings on top of the original**, not as new uploaded bytes, so they don't hit the storage gate.
7. **Pages, photos per book, and print orders have no plan limits**, since the brief lists none.
8. **Units are binary** (1 MB = 2^20 bytes, 1 GB = 2^30 bytes), defined once in the plan constants.
9. **The same rules apply to any Pro-to-Free transition**, including failed payment once the billing provider marks the subscription ended. The billing provider's dunning/grace settings decide when that happens.

````

> Result: File created successfully at: C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work/docs/downgrade-policy.md (file state is current in your context — no need to Read it back)

**Assistant:** I left a stray "rename? **no**" in the allowed list; fixing it.

**Tool call `Edit`:** `C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work/docs/downgrade-policy.md`

Replaced:

````text
reorder past prints, rename? **no** (see below), move to Trash.
````

With:

````text
reorder past prints, move to Trash.
````

> Result: The file C:/tmp/wro-eval3/builds/3-downgrade-overage-old-opus/work/docs/downgrade-policy.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** I've written `docs/downgrade-policy.md`. It isn't committed. The repo has no backend code yet, so the enforcement section describes what the backend has to implement rather than code that exists.

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

**Session ended:** success, 8 turns, 103599 ms
