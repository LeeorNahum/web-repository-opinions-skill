**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-downgrade-overage-old-opus2/work\" && git ls-files | grep -v node_modules | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5049 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-downgrade-overage-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat billing.md quota.md data-deletion.md"}`

> Result: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 5511 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-downgrade-overage-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat source-of-truth.md user-facing-errors.md && grep -n -i -A3 \"error\" http-apis.md agent-tool-design.md | head -80"}`

> Result: # Source Of Truth  Pick one durable owner per fact. This is the single source of truth principle: one authoritative owner per fact, with every other copy a cache or a reference and never a competing authority. The app orchestrates between owners. It does not duplicate truth casually.  | Fact | Owner | | --- | --- | | App state, metadata, status, permissions, usage, jobs | Database | | Raw b [... 5183 more characters]

**Tool call `Write`:** `<run>/builds/4-downgrade-overage-old-opus2/work/docs/downgrade-policy.md`

````text
# Downgrade policy: Pro → Free

What a cancelled Pro user can and can't do with what they already have once the paid period ends, and how the backend enforces it.

`docs/brief.md` is the source of truth for product decisions. This document applies those decisions to downgrades. If the two disagree, the brief wins and this file gets fixed. Calls that the brief did not settle are listed under [Assumptions to confirm](#assumptions-to-confirm).

## Principles

1. **Nothing is destroyed.** Downgrading never deletes, hides, or degrades a book, page, or photo. The only thing that ever permanently removes data is the 14-day Trash purge, which works the same on every plan.
2. **No stored lock.** We never stamp a "locked" or "over limit" flag on a book or photo. Whether something is covered is worked out from the current plan each time an operation runs. Resubscribing restores full access right away, with no migration or cleanup job.
3. **One gate.** The browser app, the public API, the MCP connection, and background jobs acting for the user all go through the same backend checks. If a control or tool happens to be reachable, that never grants something the plan does not cover.
4. **Removing is always allowed.** Any operation that only frees capacity (trash, permanently delete, remove a photo or page) works on every book whatever its coverage. That way the user can always get back under the limits on their own.

## When the downgrade happens

- The billing provider (Stripe) owns subscription truth. A cancelled subscription stays Pro until its current paid period ends, then becomes Free. There is no grace period beyond that.
- The backend reads the plan from the billing provider's subscription state. A webhook-fed copy in the database is fine as a cache, but it is never the authority. The plan is never stored on books or photos.
- Plan limits are constants in the domain package:

  | Limit | Free | Pro |
  | --- | ---: | ---: |
  | `books` (active, not in Trash) | 25 | 60 |
  | `photoBytes` (one uploaded photo) | 40 MB | 120 MB |
  | `storageBytes` (all stored bytes, Trash included) | 1.5 GB | 4 GB |

## The rules

### Books: the oldest 25 stay editable

On Free, the user's **25 oldest active books** are *covered*, ordered by creation time with book id as the tie-break. All other active books are *uncovered*. Books in Trash don't count toward the book limit.

Coverage is recalculated on every check. So if the user trashes or deletes a covered book, the next-oldest uncovered book becomes covered. Restoring a book from Trash can push the newest covered book out of coverage.

| Action | Covered book | Uncovered book |
| --- | :---: | :---: |
| Open, view, browse pages and photos | ✅ | ✅ |
| Download / export photos and the book | ✅ | ✅ |
| Order printed copies | ✅ | ✅ |
| Edit: pages, layout, text, placing or moving photos, title, settings | ✅ | ❌ `book_not_covered` |
| Add photos (also subject to the storage and photo-size rules) | ✅ | ❌ `book_not_covered` |
| Remove photos or pages | ✅ | ✅ |
| Move to Trash, restore from Trash, delete permanently | ✅ | ✅ |
| Duplicate | needs room for a new book (and bytes) | ❌ |

**Creating** a book (new, duplicate, or import) is refused with `book_limit_reached` while the user has 25 or more active books. **Restoring** from Trash is always allowed, because it is the user's own data coming back and not a new book. It just takes its place in the coverage order.

### Storage: no new bytes while over 1.5 GB

Usage counts every stored byte: photos in active books, uncovered books, and books in Trash. Bytes stop counting once Trash purges them (after 14 days) or the user deletes them permanently.

- Any operation that adds bytes (upload, import, replace a photo, duplicating a book or photo that copies bytes) is refused with `storage_limit_reached` unless `usage + new bytes ≤ 1.5 GB`.
- Operations that add no bytes keep working in covered books even when usage is over the limit: rearranging, editing text, placing photos that are already in the book.
- Being over storage never blocks viewing, downloading, printing, or removing anything.

### Photo size: limits uploads only, not existing photos

The 40 MB per-photo limit applies when a photo is **uploaded** (new upload, import, or replacing a photo). Photos already stored that are bigger than that are kept at full resolution. They stay fully usable in covered books (placing, moving, printing) and downloadable from any book. Their bytes count toward storage like any other photo.

The consequence the user should understand: if they delete one of those photos, they can't upload it again at the same size on Free.

## Walking through the typical case

The case from the brief: 40 books, 2.6 GB stored (300 MB of it in Trash), and fifteen photos between 60 and 110 MB. The 40 books are taken to be active, not in Trash.

When the paid period ends and the account becomes Free:

| | Has | Free limit | Result |
| --- | --- | --- | --- |
| Books | 40 active | 25 | The 25 oldest stay editable. The 15 newest are read-only: viewable, downloadable, printable, removable. No new books. |
| Storage | 2.6 GB | 1.5 GB | 1.1 GB over. No uploads. Edits that add no bytes still work in the 25 covered books. |
| Large photos | 15 × 60–110 MB | 40 MB per upload | All 15 kept at full size and usable wherever their book is covered. None of them could be uploaded again on Free. |
| Trash | 300 MB | (counts toward storage) | Purged on its normal 14-day schedule, or sooner if the user deletes it permanently. That brings usage to 2.3 GB, still 0.8 GB over. |

What the user can do next:

- **Keep everything as it is.** Nothing is lost. They can read, export, and print all 40 books and edit 25 of them.
- **Choose which books stay editable** by trashing books they no longer need to edit. Each book trashed brings the next-oldest into coverage. To edit one of the newest 15, they have to trash enough older books.
- **Upload again** by freeing about 1.1 GB plus the size of the new upload. Emptying Trash covers 300 MB. The 15 large photos alone add up to roughly 0.9–1.65 GB, so removing some of them is the quickest way back under the limit.
- **Resubscribe.** All 40 books become editable immediately, uploads open up to 4 GB and 120 MB per photo, and nothing has to be repaired.

The rules hold up on this case: no data is lost, every block has a remedy the user can carry out alone, and resubscribing reverses the downgrade without any state change.

## How the backend enforces it

All of this lives in one entitlement module in the backend (domain package plus backend functions). Clients never compute coverage for enforcement. They may only display it.

1. **Plan resolution.** `getPlan(userId)` reads the subscription state from the billing provider, through the webhook-reconciled cache. It returns `pro` while the subscription is active or cancelled-but-not-yet-ended, and `free` otherwise. Limits come from the plan constants in code.
2. **Book coverage.** `assertBookCovered(userId, bookId)` lists the user's active books ordered by `(createdAt, id)` and checks whether the book is within the first `limits.books`. Every book-mutating function calls it, except the removal operations listed above. That covers each browser mutation, each API write endpoint, each MCP write tool, and each job started on the user's behalf. Reads, exports, and print orders do not call it.
3. **Book creation.** `assertCanCreateBook(userId)` counts active books in the same transaction as the insert, so concurrent creates can't get past the limit.
4. **Uploads.** Checked before any bytes move (gate before, charge after):
   - When the upload URL is issued, the declared size is checked against `limits.photoBytes`, and against `limits.storageBytes` together with current usage and other pending uploads. The book being uploaded into must also be covered. The signed URL pins the content length.
   - On finalize, the stored object's actual size is verified against the size that was authorized. Usage is recorded only after this durable success. The plan is evaluated when the upload is authorized, so an upload authorized just before the period ends can still finish.
5. **Storage usage** is a per-user counter kept in the same transaction as every photo create and permanent delete, including the Trash purge job. Moving a book to Trash or restoring it doesn't change the counter.
6. **System jobs** (Trash purge, thumbnail/derivative generation for existing photos, print fulfilment) are not gated. They aren't the user adding or changing content.
7. **Errors** are typed, product-owned outcomes. The API and MCP return them as stable codes, and the UI maps them to copy at the shared presentation boundary. Each error names the limit and the measurement but leaves the remedy to the surface that shows it. There is no standing "you're over your plan" banner. The limit is shown where an action hits it, and on the plan/billing page.

   | Code | When | Includes |
   | --- | --- | --- |
   | `book_not_covered` | Editing a book outside the oldest-N on the current plan | plan book limit, active book count |
   | `book_limit_reached` | Creating a book at or over the limit | plan book limit, active book count |
   | `storage_limit_reached` | An upload or copy that would exceed storage | limit, current usage (Trash shown separately), requested bytes |
   | `photo_too_large` | Uploading one photo over the per-photo limit | limit, photo size |

   Upgrade is a real remedy for all four (Pro raises every one of these limits), so the surface may offer it alongside "free up space" or "move books to Trash".

## Assumptions to confirm

These are calls I made where the brief was silent:

1. **The oldest books stay editable, and the user can't pick.** Letting the user pin which 25 stay editable would mean storing a selection. Trashing books gives the same control without one. Picking the oldest favours books that are probably finished, though it could be argued either way (newest = what they're working on now).
2. **Printing uncovered books is allowed.** Ordering prints is treated as read-only use of existing content, and it is paid separately. This is the call most worth revisiting: it lets a former Pro user keep ordering prints of all 60 possible books indefinitely.
3. **Trash counts toward storage but not toward the book limit.** The brief's "2.6 GB stored (300 MB of it in Trash)" reads as Trash counting toward storage. Not counting trashed books keeps Trash useful for freeing a coverage slot.
4. **The 40 books in the typical case are all active.** If some are in Trash, there are fewer uncovered books and the conclusions still hold.
5. **The per-photo limit applies only at upload.** Existing oversized photos are never restricted, so a covered book never turns unprintable because of a photo it already holds.
6. **Removals are allowed on uncovered books.** Removing photos or pages from a read-only book is permitted because it only frees capacity.
7. **Units are binary** (1 GB = 1024³ bytes, 1 MB = 1024² bytes). This is the more generous reading for users.
8. **No grace period** beyond the paid period, and an upload authorized before the period ends can still finish. Failed-payment and dunning behaviour is out of scope here. It should resolve to the same `getPlan` answer once the billing provider ends the subscription.
9. **No notification or email** about the downgrade is specified here. Showing the limit is left to the moment an action hits it and to the billing page, per the "no standing ceiling" rule.

Changing any of the plan limits themselves is a billing decision and is not made here.

````

> Result: File created successfully at: <run>/builds/4-downgrade-overage-old-opus2/work/docs/downgrade-policy.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written `docs/downgrade-policy.md`. It's a policy document only: there's no backend code in the repo yet, so the enforcement section is a design to build, not a description of existing code. I haven't committed it.

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

**Session ended:** success, 7 turns, 115585 ms
