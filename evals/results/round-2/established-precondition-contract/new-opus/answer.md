I've written the design to `docs/row-updates.md`. I didn't commit it, so it's waiting for your review.

**The design:** each row becomes its own small resource with its own `ETag`, addressed by a stable row key:

- `GET /v1/price-lists/{id}/rows/{rowKey}` returns one row and its row ETag.
- `PUT /v1/price-lists/{id}/rows/{rowKey}` replaces one row and requires `If-Match` with the row ETag.
  - Responses: `200` on success, `412` if that row changed since the caller read it, `428` if `If-Match` is missing, `404` if the row doesn't exist (this endpoint never creates rows), `422` if validation fails.

**The calls I made:**

- **Same safety rules as today, applied per row.** Partners keep the replace-with-`If-Match` model they've built against for two years, and no write can overwrite someone else's change unseen. Edits to *different* rows no longer conflict, which is the real pain with several editors in the same hour.
- **The existing contract doesn't change.** Any row change also changes the document ETag, so a stale whole-document `PUT` still gets `412`. Because it only adds new paths, it ships inside v1 without a v2.
- **No row IDs by array position.** Concurrent inserts and removals would shift positions and could silently update the wrong row. That's also why I didn't choose JSON Patch on the whole document.
- **Retries are safe without an idempotency key.** If a write landed but the response was lost, the retry gets `412`, the caller re-reads and sees its own value.
- **One shared path for writes.** Partner row writes and staff edits in the browser app go through the same code path and the same lock as document writes, so their row ETags stay in step.
- **Left for later:** adding and deleting single rows, and partial-field `PATCH`. Partners only asked to change existing rows.

**What I assumed (all listed at the end of the doc):**

1. **Rows already have a stable, unique key**, such as a SKU, that partners know. The whole design depends on this. If no such key exists, we first need to add server-assigned row IDs to the document.
2. The document `PUT` answers a missing `If-Match` with `428`. If it actually does something else, the row endpoint should copy it.
3. The row endpoint can reuse v1's existing error format and per-row validation unchanged.
4. Row writes should trigger the same audit history and notifications as a document `PUT`.