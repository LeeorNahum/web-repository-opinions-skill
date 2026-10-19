I've written the design to `docs/row-updates.md`. It's a proposal only: I didn't change any code or commit anything.

**The design**
- **Two new endpoints in v1:** `GET` and `PUT` on `/v1/price-lists/{id}/rows/{rowId}`. Nothing in the existing contract changes, so there's no need for a v2.
- **Each row gets its own `ETag`.** A row update requires `If-Match` with that row's ETag. Partners and staff editing different rows of the same list no longer conflict, and two people editing the same row still get `412`.
- **A row update still changes the document's `ETag`.** This is the decision that matters most. Partners who keep syncing with whole-document `PUT` get a `412` instead of silently overwriting someone else's row change. Their behavior stays exactly as it is today.
- **`If-Match` can also take the document's ETag.** That's a stricter check, and it lets a sync that already holds the document ETag change a row without first reading it.
- **Responses:**
  - `200` returns the stored row with its new row ETag, plus a new `Ledgerline-Document-ETag` header.
  - `412` means a conflict.
  - `428` means `If-Match` is missing.
  - The doc also covers `400`, `404` and `422`, and includes partner guidance for retries and timeouts.
- **One shared row-update operation.** The public API and the staff browser app should both use it, so both enforce the same conflict and validation rules.

**Left out for now:** adding or deleting rows, partial-field `PATCH`, and updating several rows in one request. The doc notes how each would follow later.

**Assumptions for you to check (all listed in the doc):**
1. **Rows have a stable `id`.** This is the big one, because the brief doesn't describe the row shape. If rows don't have IDs, we'd have to add them to existing documents first. We'd also need to decide what a whole-document `PUT` does with rows that come in without one.
2. A missing `If-Match` on a row update should return whatever the document `PUT` returns today. I wrote `428` as a placeholder.
3. The current error format and API key permissions carry over: a key that can update a list can update its rows.
4. Accepting the document ETag as an alternative is optional. If you'd rather have one way to do it, drop it.
5. The new header's name is a placeholder; rename it to match our other custom headers.