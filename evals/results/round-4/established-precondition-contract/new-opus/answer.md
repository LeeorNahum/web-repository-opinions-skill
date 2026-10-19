I've written the design to `docs/row-updates.md`. Nothing is committed, and no code or OpenAPI changes were made; it's a design document only.

**What it proposes:**
- **The current API stays exactly as it is.** `GET` and `PUT /v1/price-lists/{id}` keep the whole-document ETag, the required `If-Match`, and the `412` on a stale ETag. Everything new is added on top of `v1`.
- **Two new endpoints:** `GET /v1/price-lists/{listId}/rows/{rowId}` and `PATCH` on the same path. `GET` returns the row with its own row ETag. `PATCH` takes just the fields to change (JSON Merge Patch) and requires `If-Match` with that row ETag. A partner then gets `412` only when someone else changed *that row*, not when anyone touched any other row in the list.
- **A `PATCH` never returns the document ETag.** If it did, a partner could later send a whole-list `PUT` built from an out-of-date copy, pass the check, and silently overwrite other people's edits. After a `PATCH`, a partner must `GET` the full list again before sending a `PUT`.
- **Staff edits in the browser app go through the same single-row logic.** Otherwise staff would keep causing conflicts for partners, since they're among the people editing at the same time.
- **Retries are already safe.** A retried `PATCH` that had in fact landed gets `412`, so no idempotency key is needed.
- **Not included yet:** creating and deleting single rows, changing several rows in one request, and a `PUT` that merges instead of failing. Each has a short note on how it would work.

**Calls you should check (detailed at the end of the doc):**
1. **Row IDs.** I assumed rows have no stable unique key, so the server would add a new 12-character `id` to every row. If a SKU or similar is already unique and never changes, use that instead and skip the new field.
2. **Partners' parsers.** Adding `id` to the list response assumes partners' systems ignore fields they don't expect. Any partner with a strict schema would break.
3. **Partners dropping `id`.** If a partner's system strips `id` when sending a full `PUT`, those rows get new IDs. Other partners' row addresses then return `404`. That's safe but noisy.
4. **Extra request per change.** `PATCH` requires the row ETag rather than accepting the document ETag partners already hold. That costs one extra `GET` per change, but keeps the two ETags clearly separate. Accepting the document ETag could be added later without breaking anyone.
5. **Missing `If-Match` and error format.** I used `428` when `If-Match` is missing, and assumed the existing `v1` error format. The brief doesn't say what `PUT` does today, so match it if it differs.
6. **Same-row conflicts.** Two partners changing different fields of the same row still conflict. I chose that because it's simpler and safer for prices.