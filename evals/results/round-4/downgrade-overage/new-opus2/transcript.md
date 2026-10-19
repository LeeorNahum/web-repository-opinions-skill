**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-downgrade-overage-new-opus2/work\" && git ls-files | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5049 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-downgrade-overage-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat billing.md quota.md data-deletion.md source-of-truth.md"}`

> Result: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 10311 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-downgrade-overage-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat user-facing-errors.md uploads.md http-apis.md agent-tool-design.md | grep -v '^$' | head -300"}`

> Result: # User-Facing Errors Treat every provider, framework, transport, database, and backend error as internal data. Convert failures into product-owned outcomes before they reach visible UI. ## Boundary - Return typed outcome codes for expected failures. - Map outcome codes to concise, actionable copy at a shared presentation boundary. - Use one context-specific fallback for unexpected failures. - Keep [... 13511 more characters]

**Tool call `Write`:** `<run>/builds/4-downgrade-overage-new-opus2/work/docs/downgrade-policy.md`

````text
# Downgrade policy: Pro to Free

`docs/brief.md` takes precedence over this document. If they disagree, this document is out of date: fix it here and leave the code alone.

This document covers what happens when a Pro subscription ends and the account falls back to Free. The rule in one line: **nothing the user already has is deleted or hidden. Everything stays readable, downloadable, printable, and removable. What stops is growth beyond the Free allowances, plus editing of the books that don't fit in the Free book count.** When the account goes back to Pro, everything works again immediately.

## When it applies

- Cancelling Pro takes effect at the end of the paid period (brief). The account stays on Pro, with all Pro allowances, until the billing provider says the subscription has ended.
- From that point on, the account's plan is Free and Free limits apply on every request. Nothing runs at the moment of downgrade: no migration, no lock flag, no cleanup job. Coverage is worked out again on every gated request, from the current plan.
- Resubscribing reverses all of it instantly, for the same reason.

## Free allowances (from the brief)

| Allowance | Free | Pro |
| --- | ---: | ---: |
| Books | 25 | 60 |
| One uploaded photo | 40 MB | 120 MB |
| Total storage | 1.5 GB | 4 GB |

## Rules

### 1. Books over the count: oldest 25 stay editable, the rest become read-only

- **Covered books** are the account's 25 oldest books that are not in Trash, ordered by creation time, with the book ID breaking ties. Covered books work exactly as before, subject to the storage rules below.
- **Uncovered books** are every other book not in Trash. Their pages, photos, and history are all kept. On an uncovered book the user **can**:
  - open and view it in the browser, API, and MCP
  - download or export it, including original photos
  - order printed copies of it
  - move it to Trash, or delete it permanently
- On an uncovered book the user **can't**: edit pages, layout, or text; add or remove photos; rename it; or duplicate it. Each of these fails with `book_not_covered`.
- **Creating a book** needs fewer than 25 books outside Trash. Otherwise it fails with `book_limit_reached`.
- **The user chooses which books stay editable** by moving books to Trash. A trashed book drops out of the count, so the next-oldest uncovered book becomes covered. No setting is needed for this.
- **Restoring from Trash** is always allowed, so a downgrade never causes a book to be purged. A restored book takes its place in the creation-time order again. If it's older than the 25th covered book, it becomes covered and the newest covered book becomes uncovered. This is deterministic and shows in the UI (rule 5).

### 2. Storage over the allowance: keep everything, block growth

- Storage usage is the total bytes of stored photos, **including photos in books that are in Trash**, until Trash removes them permanently.
- When usage is at or over 1.5 GB:
  - Everything stays readable, downloadable, printable, and removable.
  - Edits that don't add bytes are still allowed on covered books. That includes reordering pages, changing layouts and text, placing photos the account already has, removing photos from pages, and deleting pages.
  - Anything that adds bytes is refused with `storage_full`. That covers uploading photos (browser, API, MCP URL import) and any copy that duplicates photo bytes.
- Growth is allowed again once usage is back below 1.5 GB, and an upload is accepted only if it fits in the space that remains.
- Moving a book to Trash **does not free storage**. Its bytes are freed when it's permanently deleted (by "Delete permanently" or "Empty Trash") or when Trash removes it after 14 days.

### 3. Photos over the per-photo limit: keep them, apply the limit only to new uploads

- A photo stored before the downgrade that's larger than 40 MB is kept and served as it is, at full original resolution. It can be viewed, downloaded, printed, placed on pages in covered books, and deleted.
- Each new upload must be 40 MB or smaller, otherwise it fails with `photo_too_large`. That includes uploading a replacement for an existing large photo.
- Large existing photos count toward storage at their full size.

### 4. Things a downgrade never does

- It never deletes, hides, re-compresses, or downsamples anything.
- It never changes the 14-day Trash timer.
- It never blocks reading, exporting, printing, or deleting.
- It never stores a "locked" marker on a book, photo, or account.

### 5. Where the user sees it

- A limit is shown only where it's hit. There's no standing banner or always-visible counter.
- Uncovered books show a read-only state when opened, with edit controls disabled. The note there says the book is read-only on Free because of the 25-book limit. It gives two remedies: move some books to Trash, or upgrade.
- An upload refused for storage names the 1.5 GB allowance and current usage. Its remedies are "Empty Trash" (when Trash holds anything), deleting photos or books, or upgrading.
- An upload refused for size names the 40 MB limit and the file's size.
- Offering an upgrade is honest in all three cases, because Pro raises every one of these ceilings.

## How the backend enforces it

There's no backend code in the repo yet. This is the contract the implementation must follow.

1. **Plan truth comes from the billing provider.** `resolvePlan(account)` returns `free` or `pro` from the subscription state. That state is either read from the billing provider or taken from a last-known mirror that the provider's webhooks keep current. A subscription that is cancelling but still in its paid period resolves to `pro`. Once it has ended, it resolves to `free`. Nothing else in the app decides the plan.
2. **Limits are constants in the domain package** (`PLAN_LIMITS.free`, `PLAN_LIMITS.pro`), as the brief requires. They are not env values or dashboard settings.
3. **Coverage is derived, never stored.** `coveredBookIds(account)` = the first `PLAN_LIMITS[plan].books` books not in Trash, ordered by `(createdAt, id)`. It's computed when the gate runs, so subscribing, cancelling, trashing, or restoring changes it immediately and nothing needs reconciling.
4. **One gate, used by every client.** The browser app, public HTTP API, MCP tools, print-order flow, and background jobs all call the same product capabilities. Those capabilities run these checks before any work:
   - `assertBookWritable(account, bookId)`: the book is covered, otherwise `book_not_covered`. Every mutation of book content calls it.
   - `assertCanCreateBook(account)`: the count of books not in Trash is below the limit, otherwise `book_limit_reached`.
   - `reserveStorage(account, bytes)`: one atomic reservation against `limit − usage − open reservations`, otherwise `storage_full`. The reservation has an expiry, and the signed upload URL expires no later than the reservation does.
   - `assertPhotoSize(account, bytes)`: checks against the current plan's per-photo limit, otherwise `photo_too_large`.
   Read, export, print-order, trash, restore, and permanent-delete capabilities don't call the coverage or growth gates.
5. **Uploads are checked twice.** Once when the upload is requested, using the declared size. Again at finalize, using the measured size against the plan *at finalize time*. So an upload that started on Pro and finishes after the paid period ends is held to Free limits. Usage is recorded once, at a durable finalize, from the measured size.
6. **Usage counts Trash.** The storage usage counter (owned by the database) goes down only when bytes are permanently removed, not when a book is moved to Trash.
7. **Typed refusals.** Each gate returns a stable error code: `book_not_covered`, `book_limit_reached`, `storage_full`, or `photo_too_large`. The error includes what was measured (limit, current usage, file size). The HTTP API returns these as 403 with the code in the body. MCP returns them as tool errors that name the measurement and the next step. The UI turns codes into product copy at one shared boundary, and raw provider or framework errors are never shown.

## Check against the typical case

From the brief: a Pro user cancels with **40 books**, **2.6 GB stored (300 MB of it in Trash)**, and **fifteen photos between 60 and 110 MB**. After the paid period ends:

| Area | Result |
| --- | --- |
| Books | 40 books outside Trash against a limit of 25. The 25 oldest stay editable and the 15 newest become read-only. All 40 can be viewed, exported, printed, and deleted. Making all 40 editable means trashing 15 books, upgrading, or a mix. Creating a new book needs at least 16 trashed (count below 25). |
| Storage | 2.6 GB against 1.5 GB, so 1.1 GB over. Nothing is lost. Uploads are refused. Rearranging, retexting, and re-placing existing photos in covered books still work. |
| Trash | Its 300 MB counts. Emptying Trash (or waiting up to 14 days) brings usage to 2.3 GB, still 0.8 GB over. To upload again, the user must permanently delete at least another 0.8 GB, plus room for the new photos, or upgrade. Trashing books alone frees nothing until they're permanently removed. |
| Large photos | All fifteen (60–110 MB, each over 40 MB) are kept at full resolution, print normally, and can be placed in covered books. They're already counted in the 2.6 GB. New uploads must be ≤ 40 MB. |
| Data loss | None. The only things removed are the 300 MB the user had already put in Trash, which goes on the existing 14-day schedule, and anything the user deletes themselves. |

Nothing in the case breaks a rule, and every state in it leads to a clear action. The book rule and the storage rule are independent. Trashing 15 books makes them all editable but doesn't unblock uploads.

## Assumptions (for the owner to confirm)

1. **Coverage order is oldest-first by creation time.** Another option is most-recently-edited first, which would favor active work but would shift as the user edits. Oldest-first is stable, and the user can still choose which books are covered by trashing others.
2. **Books in Trash don't count toward the book limit** (they do count toward storage). The brief doesn't say.
3. **Uncovered books can still be ordered as prints.** Printing adds no storage, and blocking it would hold the user's own finished work hostage. Change this if prints should require a covered book.
4. **"Storage" means stored photo bytes.** Thumbnails, print renditions, and other derived files the product generates are product overhead and aren't counted.
5. **Restore from Trash is always allowed,** even when it uncovers another book, so a downgrade can never cause a purge.
6. **The UI offers "Empty Trash" and "Delete permanently".** The storage rules depend on them as the way to free space immediately. If they don't exist yet, they're needed.
7. **Failed payments are out of scope.** Whatever subscription status the billing provider reports decides the plan, and "not active" is treated as Free under these same rules. Any grace period for failed payments needs its own decision.
8. **Error transport.** Gate refusals are HTTP 403 with a typed code.
9. **The account owns the books.** The brief doesn't mention workspaces or shared books. If books later belong to a shared workspace, coverage follows whoever's plan pays for that workspace.

None of this changes prices or the plan allowances in the brief. It only defines what those allowances mean once someone already holds more than Free allows.

````

> Result: File created successfully at: <run>/builds/4-downgrade-overage-new-opus2/work/docs/downgrade-policy.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written `docs/downgrade-policy.md`. I haven't committed it.

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

**Session ended:** success, 7 turns, 106595 ms
