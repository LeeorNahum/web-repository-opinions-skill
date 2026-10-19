I wrote the design to `docs/row-updates.md`. It's a document only: no code is written, and nothing is committed.

**The design:** two new endpoints, added to v1 without changing anything partners already use.
- `GET /v1/price-lists/{id}/rows/{rowId}` returns one row and an `ETag` for that row.
- `PATCH /v1/price-lists/{id}/rows/{rowId}` changes only the fields sent (standard JSON Merge Patch). It requires `If-Match` with the row's ETag. A stale ETag gets `412`, and a missing one gets `428`.

**Main calls I made:**
- **Same conflict rule, applied per row.** Partners keep the read → `If-Match` → `412` pattern they've used for two years. The difference is that an edit to another row no longer causes a conflict. I didn't use last-write-wins: partners and staff edit the same lists in the same hour, so the server needs to know what the caller last saw.
- **Rows get a stable `id`.** Rows are addressed by that `id`, never by their position in the list, because positions shift when someone else adds or removes a row. The `id` is a new field on the existing `GET` document.
- **A `PATCH` response returns only the new row ETag, not the document's ETag.** Otherwise a partner holding an older full copy could `PUT` it with the fresh ETag and silently overwrite other people's changes.
- **Retries are safe without an idempotency key.** If a `PATCH` times out after it actually landed, the retry gets `412`. Re-reading the row shows whether the change is already there.
- **One shared row-update path.** `PUT`, `PATCH` and staff edits in the browser app all go through the same validation and permissions. The rollout also covers backfilling row IDs, publishing the change in the OpenAPI document before building, and a minor version bump.

**Assumptions to confirm tomorrow (listed in the doc):**
- I assumed rows have no stable ID today. If they already do, the backfill isn't needed.
- With the new IDs, a `PUT` that sends rows without `id` gives every row a new ID, so row IDs a caller saved for that list stop working.
- Scope is changing existing rows only. Adding, deleting and batch-updating single rows are deferred.
- I assumed v1 already has a typed error format to reuse.
- The field names in the examples (`unitPrice`, `currency`) are placeholders, since the brief doesn't define what a row contains.

**Left for you to decide:** whether `PUT` should later stop rejecting edits that touch different rows and merge them instead. That would change behavior partners have relied on for two years, so the design leaves `PUT` exactly as it is.