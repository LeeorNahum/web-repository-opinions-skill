I've written the design to `docs/row-updates.md`. It's a proposal only: no code, and nothing committed.

**The design**
- **New endpoints:** `GET` and `PATCH /v1/price-lists/{id}/rows/{rowKey}`. Each row has its own ETag. The patch uses the standard JSON Merge Patch format (`application/merge-patch+json`), so callers send only the fields they're changing.
- **Same conflict rule as today:** `PATCH` requires `If-Match` with the row's ETag. If the row changed since the caller read it, they get `412`, just like `PUT`. A missing header or `If-Match: *` gets `428`, so nobody can write without that check.
- **Existing contract unchanged:** every row write also changes the document's ETag. A `PUT` built from an older read still gets `412`, exactly as published.
- **Fewer conflicts:** partners editing different rows don't block each other. Only edits to the same row conflict.
- **Unattended retries:** a `412` response includes the current row, so a sync job can tell whether its timed-out write already landed, or re-apply its change, without an extra request.
- **No path around the check:** a `PATCH` response doesn't return the document ETag. Otherwise a caller could use it in a later `PUT` and overwrite changes it never saw.
- **One code path:** partners and the staff browser app use the same row-update logic. The change is additive, so it stays in `v1` with an OpenAPI update and a minor version bump.

**Assumptions for you to check** (the doc has the full list):
1. **The biggest one: each row has a stable unique key within its list, such as a SKU.** The brief doesn't describe the row shape and the repo has no schema, so I don't know which field this is. If rows have no such field, we need server-assigned row IDs first, and `PUT` would have to keep them stable. That needs its own design.
2. I assumed `PUT` returns `428` when `If-Match` is missing, and matched it. If it returns something else, `PATCH` should match `PUT`.
3. Full-document `PUT` jobs will get `412` more often once row edits exist. That's the contract working as designed, and the partner changelog should say so.
4. Merge Patch replaces arrays inside a row wholesale. If rows contain arrays that partners need to edit item by item, the format choice needs revisiting.

Adding rows, deleting rows, batch edits and change feeds are listed as out of scope, with notes on how they would follow the same rules.