**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-downgrade-overage-old-opus/work && git ls-files | grep -v node_modules | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5049 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-downgrade-overage-old-opus/work/.claude/skills/web-repository-opinions/references && cat billing.md quota.md data-deletion.md source-of-truth.md"}`

> Result: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 8335 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-downgrade-overage-old-opus/work/.claude/skills/web-repository-opinions/references && grep -il \"plan\\b\\|downgrade\\|cancel\\|trash\\|over the limit\\|over-the-limit\" *.md; cat user-facing-errors.md | head -60; grep -n -i \"trash\\|plan\\|limit\" uploads.md object-storage.md abuse-resistance.md product-ux.md http-apis.md model-context-protocol.md agent-to [... 25 more characters]`

> Result: abuse-resistance.md ai-model-routing.md animation-runtime.md auth.md billing.md environment.md physical-commerce.md provider-setup.md source-of-truth.md workspace-tenancy.md # User-Facing Errors  Treat every provider, framework, transport, database, and backend error as internal data. Convert failures into product-owned outcomes before they reach visible UI.  ## Boundary  - Return typed outc [... 4746 more characters]

**Tool call `Write`:** `<run>/builds/2-downgrade-overage-old-opus/work/docs/downgrade-policy.md`

````text
# Downgrade policy: Pro to Free

What a cancelled Pro user can and cannot do with what they already have once the paid period ends, and how the backend enforces it.

`docs/brief.md` is the source of truth. If this document contradicts it, the brief wins and this document gets fixed. Calls made here without an owner decision are marked **[Assumed]** and listed again under [Assumptions to confirm](#assumptions-to-confirm).

## Principles

1. **Cancelling never destroys anything.** Every book, page, photo, and print-ready original stays stored with its full history. The only thing that ever permanently deletes data is the existing Trash rule (14 days after the user deletes something), and that rule works exactly the same on both plans.
2. **Coverage is computed, never stored.** We never set a "locked" flag on a book or photo. Every gate works out the answer from the current plan and the current data each time it runs. Re-subscribing restores everything immediately, with no job and nothing to reconcile.
3. **One gate for every client.** The browser app, the public API, MCP, and background jobs all call the same capability functions. A client never gets access the plan doesn't allow just because it could reach a control or endpoint.
4. **Limits only stop things that add to usage.** Free limits stop actions that would add books or bytes. They never stop the user from reading, exporting, rearranging, or deleting what they already have.

## When the downgrade happens

- After the user cancels they keep full Pro until the end of the paid period. The billing provider's subscription state decides this (brief: "Billing provider owns subscription truth").
- The account becomes Free at the moment the provider says the subscription has ended. We have no grace period of our own and no countdown. **[Assumed]**

## The rules on Free, with existing Pro-era data

### Books (Free allowance: 25)

- **Covered books** are the 25 oldest books that aren't in Trash, ordered by creation time with the book ID as tie-breaker. **[Assumed: oldest-first; the user doesn't pick]** The order is stable, so the covered set changes only when the user changes their books.
- **Books beyond the allowance** stay read-only:

| Action on a book beyond the allowance | Allowed |
| --- | --- |
| Open, view, page through | Yes |
| Export or download the book and its original photos | Yes |
| Order printed copies | Yes **[Assumed]** |
| Move to Trash, restore from Trash, delete permanently | Yes |
| Edit pages, layout, text, or photo placement | No: `book_not_covered` |
| Add photos | No: `book_not_covered` |
| Duplicate | No: `book_limit_reached` (it creates a book) |

- **Creating a book** works only while the account has fewer than 25 books outside Trash. Books in Trash don't count toward the 25. **[Assumed]**
- **Restoring from Trash** always works, so the plan never forces a book into permanent deletion. After a restore, coverage is recalculated: restoring an older book can push the newest covered book past the allowance. The restore confirmation says so when that would happen.
- Moving a covered book to Trash brings the next-oldest uncovered book into coverage. That's how the user chooses which books stay editable.

### Total storage (Free allowance: 1.5 GB)

- All stored bytes count, including items in Trash, until they're permanently removed. **[Assumed: Trash bytes are still stored, so they count]**
- If usage is over 1.5 GB, **every upload fails** with `storage_limit_reached` until usage is low enough for that upload to fit. Nothing else is blocked. Editing covered books with photos that are already uploaded still works.
- The user can free space right away by permanently deleting items from Trash. They don't have to wait for the 14-day purge. **[Assumed: an empty-Trash / delete-permanently action exists or will exist]**

### Single uploaded photo (Free allowance: 40 MB)

- This limit only applies when an upload starts. Photos already stored above 40 MB stay exactly as they are, at full resolution. They display, print, export, and can be placed or moved anywhere in a covered book.
- A new upload over 40 MB fails with `photo_too_large`. That includes replacing an existing photo with a new file.
- Crop, rotate, and similar edits are stored as metadata on the original and don't upload new bytes, so the size limit doesn't apply to them. **[Assumed]**

## Check against the typical case

From the brief: 40 books, 2.6 GB stored (300 MB of it in Trash), fifteen photos of 60–110 MB.

| | Pro (until period end) | Free (after period end) |
| --- | --- | --- |
| Books | 40 of 60, all editable | 25 oldest editable; 15 newest read-only (view, export, order, delete) |
| Create a book | Yes | No, until the count drops to 24 or fewer (16 books to Trash) |
| Storage | 2.6 of 4 GB | 2.6 GB vs. 1.5 GB: over by 1.1 GB, so **no uploads anywhere** |
| After Trash purges (≤14 days) | | 2.3 GB: still over by 0.8 GB, so still no uploads |
| The 15 large photos | Usable | Still stored, usable, and printable at full resolution; wherever they sit in a covered book they can be moved and re-placed |
| Upload a 60 MB photo | Yes | No, over the 40 MB per-photo limit (and over storage anyway) |

What this user sees: they can still open, export, and order all 40 books, and nothing gets deleted. They can keep editing their 25 oldest books using photos they've already uploaded. To upload again they must get under 1.5 GB: delete about 0.8 GB beyond what's already in Trash, then empty Trash or wait for the purge. To make a different set of books editable, or to create a book, they move books to Trash. Those books still count toward storage until they're purged.

The rules hold up for this case: no data loss, no surprise lockout of books they can still read, and each blocked action has a clear remedy. Freeing space or re-subscribing fixes every block.

## Enforcement

### Entitlement

- `getPlan(account)` in the domain package returns `free` or `pro`. It reads the subscription state that the billing provider's webhooks write to a last-known mirror. That mirror is a cache of the provider's truth, never an authority of its own. A cancelled subscription is still `pro` until the provider reports it ended.
- Plan limits are constants in the domain package (brief: "Plan limits are constants in code"):

```ts
export const PLAN_LIMITS = {
  free: { books: 25, photoBytes: 40 * MB, storageBytes: 1.5 * GB },
  pro:  { books: 60, photoBytes: 120 * MB, storageBytes: 4 * GB },
} as const;
```

### Gates

Every mutation goes through one capability layer. UI handlers, API routes, MCP tools, and jobs call it; they never touch data directly. Each gate works out its answer when it runs:

| Gate | Check | Failure code |
| --- | --- | --- |
| `assertBookCovered(book)` | book is among the first `limits.books` non-Trash books by `(createdAt, id)` | `book_not_covered` |
| `assertCanCreateBook()` | non-Trash book count < `limits.books` | `book_limit_reached` |
| `assertCanUpload(size)` | `size ≤ limits.photoBytes` and `storedBytes + reservedBytes + size ≤ limits.storageBytes` | `photo_too_large` / `storage_limit_reached` |

- **Which operations call which gate:** edits to a book's pages, layout, text, or photos call `assertBookCovered`. Create and duplicate call `assertCanCreateBook`. Getting a signed upload URL calls `assertCanUpload`, and so does finalizing the upload. Reads, export, orders, Trash, restore, and permanent delete call none of them.
- **Storage accounting:** `storedBytes` is a per-account counter in the database. It goes up only after an upload is confirmed in object storage, and down only when bytes are permanently removed (Trash purge or permanent delete). It doesn't change when something moves into or out of Trash. Uploads in progress hold a short-lived reservation (`reservedBytes`) so parallel uploads can't jointly exceed the limit. The size is checked before bytes move and only counted once the upload succeeds.
- **Upload finalize re-checks:** if the plan changed during an upload, finalizing fails and the object is deleted. No bytes beyond the limit are ever counted.
- **Covered-set lookup:** reading the first N non-Trash books comes from an index on `(accountId, trashedAt, createdAt, id)`. That's one bounded query per gate check. We don't store a coverage cache.
- **Background jobs** (print rendering, export, Trash purge) run the same gates as the user action that started them. Printing and export aren't gated, so they work for books beyond the allowance. The Trash purge ignores plan state entirely.

### Errors

Gates return typed outcome codes, not exceptions. Each surface turns them into product-owned copy that names the limit and offers a remedy that actually works:

- `book_not_covered`: "This book is view-only on the Free plan, which includes 25 editable books. Move another book to Trash or upgrade to Pro to edit it."
- `book_limit_reached`: "The Free plan includes 25 books. Move a book to Trash or upgrade to Pro to create another."
- `storage_limit_reached`: "Your photos use 2.6 GB of the Free plan's 1.5 GB. Delete photos or empty Trash, or upgrade to Pro, to upload more."
- `photo_too_large`: "Photos on the Free plan can be up to 40 MB. This one is 85 MB. Upgrade to Pro for photos up to 120 MB."

Pro raises all three limits, so offering the upgrade is honest in each message. The API and MCP return the same codes with a machine-readable `limit` and `current` value.

### UI posture

- No permanent banner or counter. A limit is shown where it's hit. Books beyond the allowance also show a quiet "View-only" marker in the library, so their edit controls are hidden instead of being offered and then failing. The usage-against-limits panel appears on the billing and settings page.
- Before the period ends, the cancellation confirmation and the billing page show what will change: which books will become view-only and whether uploads will stop. **[Assumed]**

## Assumptions to confirm

1. **Who picks the covered books:** the 25 oldest by creation date, with no user selection. The user steers coverage by moving books to Trash. An alternative is letting the user pin books, but that means storing per-book state.
2. **Printed orders stay available for books beyond the allowance.** Orders are paid separately and add no plan usage. Blocking them would hold up a sale for no benefit.
3. **Trash bytes count toward storage**, and **trashed books don't count toward the book allowance**.
4. **Permanently deleting items from Trash is a user action** (or will be added), so a user over the storage limit can free space without waiting 14 days.
5. **No grace period** beyond the paid period. The account is Free the moment the provider says the subscription has ended. Failed-payment (past-due) handling isn't covered here and follows whatever the provider reports.
6. **Crops and rotations are metadata**, so they don't count as uploads.
7. **Being over the storage limit doesn't block editing** with existing photos. It only blocks new uploads.
8. **A pre-period-end notice** goes on the cancellation flow and billing page. Whether to also send an email is an open question.

Each of these affects what customers get after paying, so they need the owner's sign-off before this ships.

````

> Result: File created successfully at: <run>/builds/2-downgrade-overage-old-opus/work/docs/downgrade-policy.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written `docs/downgrade-policy.md` and left it uncommitted. The repo has no app code yet, so the enforcement section is a design for the backend, not a description of code that exists.

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

**Session ended:** success, 7 turns, 100804 ms
