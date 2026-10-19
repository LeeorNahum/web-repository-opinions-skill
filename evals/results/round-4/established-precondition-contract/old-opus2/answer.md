I've written the design to `docs/row-updates.md`. I didn't commit it. It's a design doc only: there's no code in the repo yet, so nothing was built or tested.

**What it adds:**
- **`PATCH /v1/price-lists/{id}/rows/{rowId}`**: changes one row. The body lists only the fields being changed, using the standard JSON Merge Patch format (`application/merge-patch+json`).
- **`GET /v1/price-lists/{id}/rows/{rowId}`**: returns one row with its own **row ETag**.
- **`If-Match` is still required**, as with today's `PUT`. Normally it carries the row ETag, so a partner only gets `412` if *that row* changed. That way, partners editing different rows of the same list in the same hour don't block each other.
- **Every row change also changes the document ETag.** Existing `PUT` clients holding an older document still get `412`, exactly as now. The current `GET`/`PUT` contract doesn't change at all, so this fits inside `v1`.
- **The success response deliberately leaves out the new document ETag.** Otherwise a client could patch its local copy, `PUT` it back with that ETag, and wipe out other people's changes to other rows.
- **A `412` response includes the row as it is now.** Unattended syncs can decide whether to reapply or skip without another request, and retries are safe without an idempotency key.
- **Out of scope for now:** adding, deleting or reordering rows one at a time, and batch updates. Callers keep using `PUT` for those.

**Assumptions to confirm (listed at the end of the doc):**
1. **Rows already have a stable `id`.** This is the one that matters most. If they don't, we'd have to start returning a server-assigned `id` on every row. That's a change partners would see in the existing endpoints, and it could break partners whose code rejects fields it doesn't recognise, so it needs your sign-off.
2. **`If-Match` also accepts the whole-document ETag**, as a stricter option for partners who already hold the document. Dropping this is easy if you'd rather have one rule.
3. **Anyone allowed to `PUT` a list can also patch its rows.** There's no new permission.
4. **v1 already returns typed error codes.** If it doesn't, the new codes are still additive.
5. **A missing `If-Match` returns `428`.** I assumed `PUT` does this today; if it does something else, `PATCH` should match it.
6. **The path and format names are my choice.** Nothing in the brief constrains them.