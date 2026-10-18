**Prompt:** Partners keep asking to change single rows (see docs/brief.md). Design the API addition and write it to docs/row-updates.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cat docs/brief.md; echo ----; git ls-files | head -100"}`

> Result: # Ledgerline  Ledgerline keeps shared price lists for wholesale suppliers. A price list is a JSON document of a few hundred rows.  ## Public HTTP API v1  Partners' own systems integrate with `api.ledgerline.example/v1`, and many of them sync price lists unattended every few minutes. Our published contract, which partners have built against for two years:  - `GET /v1/price-lists/{id}` returns the d [... 5057 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references; cat http-apis.md versioning.md; grep -il \"etag\\|If-Match\\|patch\\|precondition\\|concurren\" *.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 3043 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-established-precondition-contract-old-opus/work/.claude/skills/web-repository-opinions/references; cat bulk-actions.md agent-tool-design.md ids.md failure-and-retries.md modularity.md data-model.md | head -400"}`

> Result: # Bulk Actions  Design bulk work as independent per-item outcomes unless the operation is inherently atomic.  ## Result Contract  Return one structured result for every requested item. Include the stable input identity and a small product-level state such as completed, unchanged, or failed. Where the result shape is typed, give each state its own variant carrying exactly the facts it promise [... 15335 more characters]

**Tool call `Write`:** `<run>\builds\2-established-precondition-contract-old-opus\work\docs\row-updates.md`

````text
# Single-row updates for price lists

Status: proposal, waiting for owner review. Assumptions are listed at the end. Anything marked **Decide** needs an owner call before implementation starts.

## Problem

Partners can only change a price list by sending the whole document back with `PUT /v1/price-lists/{id}` and `If-Match`. They want to change one row without sending the rest.

The constraint that shapes everything here is the contract partners have built against for two years. Every write is guarded by an ETag, and a stale ETag gets `412 Precondition Failed`. Several partners and our staff edit the same list in the same hour, and many partners sync unattended. That guard is the only thing keeping one writer from silently overwriting another. The new operation must not weaken it, for its own callers or for existing `PUT` callers.

## Design summary

- Add a **row sub-resource** with its own ETag: `GET` and `PATCH /v1/price-lists/{id}/rows/{rowKey}`.
- `PATCH` takes a JSON Merge Patch (RFC 7396) of one row and **requires `If-Match` with the row's ETag**. If the row has changed since the caller read it, the server returns `412`, just as `PUT` does today.
- Every successful row write **also changes the document ETag**. A `PUT` built from an older read still gets `412`, so the existing contract holds exactly as published.
- Row ETags are scoped to the row. Two writers changing **different** rows don't conflict. Two writers changing the **same** row do, and the later one gets `412`. Without this, adding a row-level write would only add more `412`s for everyone.
- The change is additive, so it ships inside `v1` and the OpenAPI document. No new API version.

## Endpoints

### `GET /v1/price-lists/{id}/rows/{rowKey}`

Returns one row, in the same row shape the document already uses, with a strong `ETag` header for that row.

- `200` with the row and `ETag: "<row-etag>"`.
- `404` with a typed error: `price_list_not_found` or `row_not_found`.

Partners already poll the whole document. Reading one row before patching it is a small extra request, and it gives them the ETag the patch needs.

### `PATCH /v1/price-lists/{id}/rows/{rowKey}`

Request:

```http
PATCH /v1/price-lists/{id}/rows/{rowKey}
Content-Type: application/merge-patch+json
If-Match: "<row-etag>"

{ "price": "12.40", "minQuantity": 10 }
```

Semantics, applied in one transaction:

1. Load the list and the row. If either is missing, return `404` (`price_list_not_found` or `row_not_found`).
2. Compare `If-Match` with the row's current ETag. If they differ, return `412` (see the response body below). Nothing is written.
3. Apply the merge patch to the row. Fields not in the patch are left alone. `null` removes an optional field.
4. Validate the resulting row with the same validation `PUT` uses for rows. If it fails, return `422` with the field errors. Nothing is written.
5. Store the row. This produces a new row ETag and a new document ETag.

Responses:

| Status | When | Body |
| --- | --- | --- |
| `200` | Patch applied | Full updated row. `ETag` header holds the new **row** ETag. |
| `400` | Body isn't valid JSON or isn't an object | Typed error `invalid_body` |
| `404` | List or row missing | `price_list_not_found` / `row_not_found` |
| `412` | `If-Match` is stale | `precondition_failed` plus the current row and its ETag |
| `415` | Content type isn't `application/merge-patch+json` | `unsupported_media_type` |
| `422` | The patched row fails validation, the patch changes the row key, or it removes a required field | `invalid_row` plus field errors |
| `428` | `If-Match` is missing, or is `*` | `precondition_required` |

Details:

- **No unconditional writes.** `If-Match: *` is rejected with `428`, the same as a missing header. Unattended syncers would otherwise use it as an easy way around conflicts, which brings back the lost-update problem. `If-None-Match` isn't supported on `PATCH`.
- **The `412` body carries the current row and its ETag.** The caller can re-apply its change to the fresh row and retry without another `GET`. Error bodies use the API's stable typed-error shape, and the HTTP status stays authoritative.
- **The patch response does not return the document ETag.** If it did, a caller could feed it into a later `PUT` and overwrite changes from other writers that it never saw. Before a `PUT`, the caller must `GET` the document.
- **The row key can't change** through `PATCH`. Re-keying is a different operation (see Out of scope).

### Effect on existing endpoints

- `GET /v1/price-lists/{id}`: unchanged. Its `ETag` changes after any row patch.
- `PUT /v1/price-lists/{id}`: unchanged contract. A `PUT` whose `If-Match` predates a row patch gets `412`, as it would after any other write. A successful `PUT` gives every row it changed a new row ETag. Rows it leaves byte-identical keep theirs (see "Row ETags" below).

## Row ETags

- The row ETag is a strong ETag: a hash of the list id, the row key, and the canonical serialization of the row's content.
- Because it is content-derived, a `PUT` that rewrites the whole document but leaves a row unchanged does not invalidate patches other partners are preparing for that row. This matters because unattended syncers often `PUT` the full document every few minutes.
- Known trade-off (ABA): if a row goes from A to B and back to A, a patch prepared against A still succeeds. The caller's view of that row matches the stored content exactly, so no one's edit is lost. That makes it acceptable.
- The document ETag keeps its current derivation and changes on any write.

## Retrying safely (unattended clients)

A row `PATCH` with `If-Match` is safe to retry in the sense that matters: it can never overwrite someone else's change. If a request times out and the client retries, the retry gets `412` when the first attempt actually landed, because the row ETag has moved. The documented recovery is:

1. On `412`, read the current row from the `412` body.
2. If it already has the values the client meant to set, treat the write as done.
3. Otherwise re-apply the change to the current row and `PATCH` again with the new ETag.

This goes in the public docs next to the endpoint, with a code sample. No `Idempotency-Key` header is needed for this operation.

## Implementation shape

- One shared product capability, `updatePriceListRow(listId, rowKey, expectedRowEtag, patch)`, owns the transaction, the precondition check, validation, and ETag derivation. The Hono `/v1` route is a thin adapter over it. The staff browser app calls the **same** capability, so staff and partner edits follow one concurrency rule. Staff edits to a single row should move to it rather than re-saving the whole document.
- Row validation is extracted from the existing `PUT` path and shared, so a row valid through one endpoint is valid through the other.
- The OpenAPI document at `api.ledgerline.example/openapi.json` gains the two operations, the `application/merge-patch+json` request body, and the new typed error codes. Settle the contract there before building the route.
- Rate limits: same gateway policy as `PUT`. The endpoint exists to reduce payload size, not to raise request budgets.
- Bump the API package minor version (additive capability) and add a changelog entry for partners.

## Out of scope for this change

These come up next, but the request was to change one row:

- Adding rows (`POST /v1/price-lists/{id}/rows`) and deleting rows (`DELETE .../rows/{rowKey}` with `If-Match`). They follow the same rules: row-scoped preconditions and a document ETag change on every write.
- Changing several rows in one atomic request. If partners need it, add a dedicated batch endpoint later. Don't widen `PATCH`.
- Changing a row's key.
- Change feeds or webhooks that would let syncers stop polling.

## Assumptions (please check)

1. **Rows have a stable unique key within a list.** The brief doesn't describe the row shape, and the repo has no schema yet. I assumed each row already carries a field that is unique and stable within its list, such as a SKU or product code, and used it as `{rowKey}` (percent-encoded in the path). **Decide:** which field that is. If rows have no such field, we need a server-assigned row `id` first. Then `PUT` has to keep ids stable for rows that partners send back, which is a bigger change and needs its own design. Array-index addressing was rejected: an index shifts when anyone inserts or removes a row, so a patch could land on the wrong row.
2. **`PUT` without `If-Match` returns `428` today.** The brief says `If-Match` is required but doesn't give the status for a missing header. I matched `PATCH` to `428 Precondition Required`. If `PUT` returns something else, such as `400`, `PATCH` should return the same, for consistency.
3. **Existing ETags are strong and opaque.** Partners only echo them back. Changing how often the document ETag changes is not a contract change, because any write could already change it.
4. **More `412`s on `PUT` are acceptable.** Once row patches exist, the document will change more often, and full-document syncers will see `412` more often. That is the contract working as designed, not a regression. The changelog should say so and point full-document writers to the row endpoint.
5. **The row shape in responses equals the row shape inside the document.** No row-level metadata is added to the document body. Row ETags are exposed only through the row endpoint's `ETag` header, so partners who round-trip documents through `PUT` see no body change.
6. **Merge Patch is enough.** Rows are flat or shallow objects. If rows contain arrays that partners need to edit element by element, Merge Patch replaces the whole array, and we would need to revisit (for example, JSON Patch, RFC 6902, scoped to the row).
7. **Same authorization as `PUT`.** A caller allowed to replace a list may patch its rows, and a caller allowed to read it may read a row. No new scope.

````

> Result: File created successfully at: <run>\builds\2-established-precondition-contract-old-opus\work\docs\row-updates.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/row-updates.md`. It's a proposal only: no code, and nothing committed.

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

**Session ended:** success, 7 turns, 90602 ms
