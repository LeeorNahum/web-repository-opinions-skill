**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-downgrade-overage-new-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5049 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-downgrade-overage-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat billing.md quota.md"}`

> Result: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 5688 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-downgrade-overage-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat source-of-truth.md user-facing-errors.md data-deletion.md uploads.md | head -300"}`

> Result: # Source Of Truth  Pick one durable owner per fact. This is the single source of truth principle: one authoritative owner per fact, with every other copy a cache or a reference and never a competing authority. The app orchestrates between owners. It does not duplicate truth casually.  | Fact | Owner | | --- | --- | | App state, metadata, status, permissions, usage, jobs | Database | | Raw b [... 7939 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-downgrade-overage-new-opus/work\" && grep -n -i -E \"status|error|40[0-9]\" .claude/skills/web-repository-opinions/references/http-apis.md | head -40; grep -n -i -E \"error|outcome\" .claude/skills/web-repository-opinions/references/agent-tool-design.md | head -20; cat package.json pnpm-workspace.yaml; git log --stat -3 | head -40"}`

> Result: 20:- Return stable typed errors. 23:**HTTP acceptance is not durable landing.** Interpret success according to the endpoint contract. A synchronous success may report a landed mutation, while `202 Accepted` or a created background job proves only admission. Parse the success body instead of casting it, and verify job completion or durable state before reporting an asynchronous operation as landed. [... 3191 more characters]

**Tool call `Write`:** `<run>\builds\2-downgrade-overage-new-opus\work\docs\downgrade-policy.md`

````text
# Downgrade policy: Pro to Free

What a cancelled Pro user can and can't do with what they already have once the paid period ends, and how the backend enforces it.

`docs/brief.md` wins over this document. If they disagree, fix this one. Calls made here without the owner are listed under [Assumptions to confirm](#assumptions-to-confirm).

## Principles

1. **Nothing is deleted or degraded because a plan ended.** Every book, page, and photo stays stored, at its original size and resolution, for as long as the user keeps it. Trash keeps its normal 14-day schedule. Nothing else is removed.
2. **Existing content stays readable and removable. Growth stops.** Over an allowance, the user can view, download, print, and delete what they have. They can't add more until they are back under.
3. **Coverage is computed, not stored.** Whether a book is editable comes from the current plan and the user's books every time it's checked. No lock flag is written on any book, so there's nothing to reconcile. Resubscribing restores everything right away.
4. **One gate for every client.** The browser app, the public API, the MCP connection, and background jobs all call the same backend checks and get the same answer and error code.

## Allowances after the period ends

| Allowance | Free limit | Rule when the user already holds more |
| --- | ---: | --- |
| Books | 25 | The 25 oldest active books, by creation time, are **covered** and fully editable. The rest are **read-only**: they're kept and can be viewed, downloaded, printed, and moved to Trash, but not edited. No new book can be created or restored from Trash while 25 or more books are active. |
| One uploaded photo | 40 MB | Existing photos over 40 MB are kept and served unchanged, including in prints. Each new upload must be 40 MB or less. |
| Total storage | 1.5 GB | Uploads are refused until usage, Trash included, is back under 1.5 GB with room for the new file. Edits that add no stored bytes are still allowed. Viewing, downloading, printing, and deleting are always allowed. |

### What counts

- **Active books** are books not in Trash. Trashed books don't count toward the 25-book limit, so moving a book to Trash frees a book slot right away.
- **Storage** is every stored byte the user owns, including books in Trash, until those bytes are permanently removed (when Trash is emptied, a book is deleted from Trash, or the 14-day purge runs). Moving a book to Trash does **not** free storage.
- **Covered books** only matter when there are more than 25 active books. That can only happen through a downgrade, because creating and restoring books are both gated at 25. At 25 or fewer active books, every book is covered.
- **Coverage order** is book creation time, oldest first, with book ID breaking ties. Editing, renaming, or reordering doesn't change it. When a covered book goes to Trash, the next-oldest read-only book becomes covered.

### Operation matrix (on Free, over one or more allowances)

| Operation | Covered book | Read-only book |
| --- | --- | --- |
| View, browse, share links the user already had | Yes | Yes |
| Download originals or export | Yes | Yes |
| Order printed copies | Yes | Yes |
| Move the book to Trash, or permanently delete it | Yes | Yes |
| Remove a photo or page | Yes | Yes (deleting only shrinks storage) |
| Edit layout, captions, page order, title, or cover | Yes | No: `book_not_covered` |
| Place a photo already stored in this book on another page | Yes | No: `book_not_covered` |
| Upload a photo | Only if it is ≤ 40 MB **and** fits under 1.5 GB | No: `book_not_covered` |
| Create or duplicate a book | Only with fewer than 25 active books (and duplicating must fit in storage) | — |
| Restore a book from Trash | Only with fewer than 25 active books | — |

Replacing a photo counts as an upload followed by a removal, so it's refused while storage is over the limit. Print orders placed before the period ended are fulfilled as normal.

## The typical case, checked

The brief's typical cancelling user: 40 books, 2.6 GB stored (300 MB of it in Trash), and fifteen photos between 60 and 110 MB.

The day after the paid period ends:

| Allowance | Holds | Free limit | Result |
| --- | ---: | ---: | --- |
| Books | 40 active | 25 | Oldest 25 covered, newest 15 read-only. Can't create a book. |
| Storage | 2.6 GB | 1.5 GB | 1.1 GB over. Every upload is refused, whatever its size. |
| Photo size | 15 photos at 60–110 MB | 40 MB | All 15 kept at full size, still shown and printed. |

What they can still do:

- Open all 40 books, download any photo (including the 110 MB ones), and order prints of any book.
- Rearrange pages, edit captions, and move existing photos around in their 25 oldest books. None of that adds stored bytes, so the storage overage doesn't block it.
- Delete anything.

What they can't do, and the error they get:

- Edit any of the 15 newest books: `book_not_covered`.
- Create, duplicate, or restore a book: `book_limit_reached` (40 of 25).
- Upload any photo, even a 2 MB one: `storage_limit_reached` (2.6 GB of 1.5 GB).
- Upload a 60 MB photo even after getting under storage: `photo_too_large` (60 MB, limit 40 MB).

How things change if they don't resubscribe:

- **Within 14 days, with no action:** the 300 MB in Trash purges on schedule, leaving 2.3 GB. Still 0.8 GB over, so uploads stay blocked. Books are unchanged.
- **To edit every book:** move 15 books to Trash. That leaves 25 active books, all covered. Creating one more needs a 16th book in Trash (24 active).
- **To upload again:** get stored bytes under 1.5 GB, with room for the file. Moving books to Trash isn't enough on its own; Trash must also be emptied or purged. The fifteen large photos alone hold 0.9–1.65 GB, so removing them would cover most or all of the 0.8 GB gap. Which photos to remove is the user's choice. The product never picks.
- **Resubscribe to Pro at any point:** 40 of 60 books and 2.6 of 4 GB are both within Pro, and the largest photo is 110 MB, under 120 MB, so everything is editable and uploadable again immediately. Nothing was changed, so nothing needs restoring.

The rules hold up here: nothing they stored is lost, every path back under a limit is something the user controls, and resubscribing undoes the downgrade completely.

## How the backend enforces it

There's no backend code in the repository yet. This is the contract the implementation must meet.

### Plan resolution

- The billing provider owns subscription truth. The backend keeps a last-known mirror of each account's subscription status and period end, updated from billing webhooks. The mirror is a cache, never the authority.
- The effective plan is Pro while the provider reports an active subscription for the current period, including one set to cancel at period end. Once the period ends and the provider reports the subscription ended, the effective plan is Free. There's no grace period on top of the paid period.
- Plan limits are constants in a shared domain package (for example `packages/plans`), never in env or the billing dashboard: `books`, `maxPhotoBytes`, and `storageBytes` for each plan.

### Pure rules (domain package)

These are pure functions with no I/O, used by every gate and every UI hint:

- `effectivePlan(subscription) -> 'free' | 'pro'`
- `coveredBookIds(plan, activeBooks)`: the oldest `limits.books` by `(createdAt, id)`
- `canCreateBook(plan, activeBookCount)`
- `canUpload(plan, usedBytes, reservedBytes, fileBytes)`: checks both the per-photo limit and storage

### Gates

Each gate runs inside the backend function every client calls. No client-side check is trusted.

| Gate | Where | Check |
| --- | --- | --- |
| Book edit | Every mutation that changes a book's content or metadata, except removing photos or pages, moving to Trash, and deleting | Book is in `coveredBookIds`, else `book_not_covered` |
| Book count | Create, duplicate, restore from Trash | Active books < plan limit, else `book_limit_reached` |
| Upload start | Before signing an upload URL | Declared size ≤ per-photo limit, else `photo_too_large`. Then reserve `fileBytes` atomically against `storageBytes − used − open reservations`, else `storage_limit_reached`. Reservations expire, so an abandoned upload frees its space. |
| Upload finalize | After bytes land in object storage | Re-check the measured size against the per-photo limit (reject and delete the object if it's over). Then charge the measured bytes to usage once, idempotently, and release the reservation. |
| Background jobs | Any job that edits a book or adds bytes (imports, MCP batch edits) | Runs the same gates when the job executes, not just when it's queued, because the plan can change in between. |

Read, download, print ordering, Trash, deletion, and the Trash purge job have no plan gate, only normal ownership checks.

Storage usage is a per-account byte total, updated in the same transaction as upload finalize and permanent deletion. It's a counter of measured bytes, not a plan flag, so the plan changing never touches it.

### Errors

Plan refusals are typed outcomes: `book_not_covered`, `book_limit_reached`, `storage_limit_reached`, and `photo_too_large`. Each one carries the measured value and the limit (for example `{ used: 2.6 GB, limit: 1.5 GB }`). The HTTP API returns them as `403` with the code in the body. MCP returns them as tool errors with the same code and copy. Raw provider or framework messages never reach the user.

The surface that hits the limit names it and offers only remedies that clear it:

- `book_not_covered` and `book_limit_reached`: move books to Trash, or upgrade (Pro allows 60).
- `storage_limit_reached`: free space (and point out that Trash counts until it's emptied), or upgrade (Pro allows 4 GB).
- `photo_too_large`: use a smaller file, or upgrade (Pro allows 120 MB per photo).

There's no standing "you're over your plan" banner across the app. Two exceptions: read-only books carry a quiet read-only marker so their missing edit controls make sense, and the cancellation screen in billing settings shows the user's current usage against Free limits before they confirm.

## Assumptions to confirm

These are calls I made without the owner, safest-for-the-user where there was a choice:

1. **Printing read-only books is allowed.** Ordering prints doesn't grow anything, and blocking a paying print customer seemed worse than the lost edit. If prints should be a covered-only action, it's a one-line gate change.
2. **Coverage is oldest-first, not user-chosen.** It's stable and can't be gamed. The user picks indirectly by trashing books. Letting users pin which 25 stay editable would be a later feature.
3. **Trashed books count toward storage but not toward the book limit.** Otherwise deleting a book wouldn't free a slot for 14 days.
4. **"40 books" in the typical case means 40 active books, with the 300 MB of Trash held by other, already-trashed books.** If the 40 includes trashed books, the user has fewer active books and the walkthrough is easier, not harder.
5. **Removing a photo from a book frees its bytes permanently.** The brief only defines Trash for whole books.
6. **Photos placed on several pages are stored once**, so placing or duplicating doesn't add bytes. If duplicating a book copies bytes, it also has to pass the storage gate (already reflected in the matrix).
7. **GB and MB are decimal** (1.5 GB = 1,500,000,000 bytes).
8. **No grace period beyond the paid period, and failed-payment (past due) handling is undecided.** I assumed the plan follows whatever the billing provider reports. A dunning window, if wanted, belongs in `effectivePlan` alone.
9. **No proactive email at period end.** Limits show up where they're hit and on the cancellation screen. Sending an "your plan ended, here's what changed" email is the owner's call.

````

> Result: File created successfully at: <run>\builds\2-downgrade-overage-new-opus\work\docs\downgrade-policy.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written `docs/downgrade-policy.md`. I didn't commit it, and I left `docs/brief.md` untouched since that's your record. There's no backend code in the repo yet, so the enforcement section is a contract for whoever builds it, not a description of existing code.

**The rules once the paid period ends:**
- **Nothing is deleted or shrunk.** Every book and photo is kept at full size, and Trash keeps its normal 14-day schedule.
- **Books (Free allows 25):** the 25 oldest books stay fully editable. The rest become read-only: they can still be viewed, downloaded, printed and moved to Trash, but not edited. No new or restored books while 25 or more are active. Moving a book to Trash frees a slot right away.
- **Storage (Free allows 1.5 GB, Trash included):** while over, all uploads are refused. Edits that don't add bytes still work, and viewing, downloading, printing and deleting always do.
- **Photo size (Free allows 40 MB):** existing larger photos are kept and still print. New uploads must be 40 MB or less.
- **Resubscribing** restores everything instantly. Editability is worked out from the current plan each time rather than stored as a lock on each book, so there's nothing to undo.

**The typical case from the brief:** the 15 newest books become read-only and all uploads stop, since 2.6 GB is 1.1 GB over. The 15 large photos stay as they are. Trash purges on its own within 14 days, leaving 2.3 GB, still 0.8 GB over. The 15 large photos alone take 0.9–1.65 GB, so the user can get back under by their own choices. Their whole account fits within Pro again (40 of 60 books, 2.6 of 4 GB, largest photo 110 MB under 120 MB), so resubscribing fully reverses the downgrade.

**How the backend enforces it:** the plan comes from the billing provider, with a local copy kept current by its notifications. Plan limits are constants in a shared code package. One set of checks covers the browser, the API, MCP and background jobs. Refusals return one of four error codes with the measured value and the limit, and each error suggests only fixes that actually clear it.

**Calls I made that you should confirm (all listed at the end of the doc):**
1. Read-only books can still be printed.
2. The oldest books are the ones that stay editable; users don't pick.
3. Books in Trash count toward storage but not the 25-book limit.
4. I read "40 books" as 40 outside Trash, with the 300 MB in Trash coming from other books.
5. Removing a photo from a book deletes it permanently, since the brief only defines Trash for whole books.
6. A photo used on several pages is stored only once.
7. GB and MB are decimal units.
8. There's no grace period after the paid period, and how to handle failed payments is still undecided.
9. No email goes out when the plan ends.

**Session ended:** success, 8 turns, 140226 ms
