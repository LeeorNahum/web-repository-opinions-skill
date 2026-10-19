**Prompt:** Partners keep asking to change single rows (see docs/brief.md). Design the API addition and write it to docs/row-updates.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-new-opus/work\" && git ls-files && cat docs/brief.md"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5052 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md versioning.md ids.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 5685 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat agent-tool-design.md bulk-actions.md user-facing-errors.md modularity.md data-model.md failure-and-retries.md"}`

> Result: # Agent Tool Design  Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.  **Familiar operations first.** Shape the catalog around operations callers already know wherever they express the real domain. File  [... 17416 more characters]

**Tool call `Write`:** `<run>/builds/4-established-precondition-contract-new-opus/work/docs/row-updates.md`

````text
# Single-row updates for price lists

Status: proposal, written while the owner was away. Assumptions and open questions are listed at the end and need owner sign-off before the OpenAPI contract is published.

## Problem

Partners can only change a price list by sending the whole document with `PUT /v1/price-lists/{id}` and `If-Match`. Several partners and our staff often edit the same list within the same hour. Because the precondition covers the whole document, any edit anywhere in the list makes everyone else's ETag stale. Partners who only want to change one price get `412`, have to re-`GET`, re-apply, and retry, and they also send a few hundred rows to change one.

The fix should let a caller change one row, and only fail when that same row changed under them.

## Design

### Constraints we keep

- The published v1 contract does not change. `GET` and `PUT /v1/price-lists/{id}` keep their current behavior, including the whole-document `ETag`, required `If-Match`, and `412` on a stale ETag. Partners have built against this for two years.
- Everything new is additive inside `/v1`. Nothing a current integration sends or relies on changes meaning.
- Concurrency is still enforced by the server with standard HTTP preconditions, the mechanism partners already use.

### Row identity

A row needs a stable address that survives reordering, inserts, and deletes. An array index does not.

- Each row in the document gets a read-only `id`: a 12-character Base58 string minted by the server (the shared entity-ID helper). Existing rows are backfilled once.
- `GET /v1/price-lists/{id}` includes `id` on every row. This is an additive response field.
- On `PUT`, a row whose `id` matches an existing row keeps that `id`. A row with no `id`, or an unknown one, gets a new `id`. Existing rows missing from the body are removed, as they are today. The rest of `PUT` works as before.

If price-list rows already have a key that is unique and stable within a list, such as a SKU, use that key instead and skip adding `id` (see A1).

### New endpoints

```
GET   /v1/price-lists/{listId}/rows/{rowId}
PATCH /v1/price-lists/{listId}/rows/{rowId}
```

**`GET …/rows/{rowId}`** returns the row in the same shape it has in the document, with a row `ETag` header. Row ETags are opaque strong validators, different from document ETags. The row ETag changes whenever that row's content changes, whether through `PATCH`, `PUT`, or the browser app.

**`PATCH …/rows/{rowId}`**

- Body: JSON Merge Patch (RFC 7396), `Content-Type: application/merge-patch+json`. Fields that are present get replaced, `null` clears an optional field, and fields that are absent stay unchanged. `id` cannot be changed.
- `If-Match` is required and must hold the row's current ETag.
  - Missing `If-Match`: `428 Precondition Required`.
  - Stale row ETag: `412 Precondition Failed`. This happens only when this row changed since the caller read it. Edits to other rows never cause a `412`.
  - A document ETag sent here does not match, so the result is `412`. The error body says that a row ETag is required (see "Errors").
- The patched row passes the same validation as a row inside a `PUT`. If it is invalid, the whole patch is rejected with `422`.
- On success: `200` with the full updated row and its new row `ETag`.
- The row update and the document version bump happen in one transaction. The document's ETag changes, as it does for any write.

**The `PATCH` response never carries the document ETag.** That is deliberate. The caller has not seen what other writers changed elsewhere in the document since their last full `GET`. If we gave them a fresh document ETag, a later `PUT` built from their stale copy would pass `If-Match` and silently wipe out other people's edits. A caller that wants to `PUT` after a `PATCH` must `GET` the document first. The only write that returns a document ETag is a `PUT`, because there the caller sent the whole document.

### How a partner uses it

```
GET   /v1/price-lists/pl8xK2mQ7rTz/rows/Rw3nH5bJ9cVd
  -> 200, ETag: "r:7f3a…"
PATCH /v1/price-lists/pl8xK2mQ7rTz/rows/Rw3nH5bJ9cVd
  If-Match: "r:7f3a…"
  Content-Type: application/merge-patch+json
  {"unitPrice": "12.40"}
  -> 200, ETag: "r:91bc…", body = updated row
```

The `id` values above are illustrative only. Sync jobs that already pull the full document can find row `id`s there. They still do a row `GET` to get the row ETag. That costs one small extra request and keeps document and row validators clearly separate (see A4).

### Retries

`PATCH` with `If-Match` is safe to retry. If a request timed out but did land, the retry gets `412` because the row ETag changed. The client should then `GET` the row and check whether it already holds the intended values. The OpenAPI description states this. No idempotency key is added, because the precondition already prevents a duplicate write.

### Interaction with `PUT`

- Row patches change the document ETag, so a partner holding an old document ETag will get `412` on `PUT`, exactly as today when anyone else edits. That is the existing contract, not a regression. Partners who move to row patches will hit it less often, not more.
- We are not changing `PUT` into a server-side merge. That would change the semantics of a published endpoint. It is a possible later addition (see "Deferred").

### Errors

Use the existing v1 error body shape, with stable typed codes:

| Status | Code | Meaning / next step |
| --- | --- | --- |
| 404 | `price_list_not_found` / `row_not_found` | The ID is wrong, or the row was removed by a `PUT`. Re-read the document. |
| 412 | `row_changed` | The row changed since it was read. `GET` the row and re-apply. |
| 412 | `row_etag_required` | `If-Match` held a document ETag. Use the row ETag from `GET …/rows/{rowId}`. |
| 415 | `unsupported_media_type` | Send `application/merge-patch+json`. |
| 422 | `invalid_row` | Names the failing field and the rule, without echoing the whole value. |
| 428 | `precondition_required` | Send `If-Match` with the row ETag. |

Error bodies never include internal or database detail.

### Implementation shape

- Add one product capability, `updatePriceListRow(listId, rowId, expectedRowVersion, patch, actor)`. It owns validation, the row-version check, the document-version bump, and the audit entry. It runs in one transaction.
- The v1 API adapter maps HTTP onto it: `If-Match` becomes the expected version, the merge-patch body becomes the patch, and outcomes become status and code.
- **The browser app's row edits use the same capability.** Staff editing one cell then stop invalidating partners' document ETags for unrelated reasons, and they get `row_changed` conflicts instead of whole-document ones. This matters as much as the partner endpoint, because staff are among the concurrent editors.
- Store a per-row version. The row ETag is derived from the row id plus the version. `PUT` bumps the version only for rows whose content actually changed, so a partner's full-document sync that re-sends identical rows does not invalidate other callers' row ETags.
- Authorization is the same capability check as `PUT` on that list, enforced in the capability rather than only in the adapter.
- Update the OpenAPI document (`api.ledgerline.example/openapi.json`) before implementing. This is a backward-compatible minor version bump of the API contract.

## Deferred, not in this change

- **Create and delete single rows** (`POST …/rows`, `DELETE …/rows/{rowId}` with a row `If-Match`). The request is about changing rows. Add these as separate methods when partners ask. Never make deletion a side effect of a patch argument.
- **Batch row patch.** If partners need several rows at once: `POST …/rows:batch-update` with per-item `If-Match` values and one typed result per item, in input order, so a partial success is reported item by item. Add it only if there is real demand. Looping single `PATCH` calls works today.
- **Merging `PUT`.** A `PUT` with a stale ETag could merge if the caller only changed rows nobody else touched. That would change published semantics, so it would need an opt-in or a v2.

## Assumptions (please confirm)

- **A1. Row key.** I assumed rows have no guaranteed stable, unique key, so the server mints `id`. If a SKU or similar is already unique within a list and never changes, address rows by it and drop the new `id` field.
- **A2. Additive fields are safe.** Adding `id` to rows in the `GET` response assumes partner parsers tolerate unknown fields. A partner with a strict schema would break. We could check with the noisiest partners first, or gate the field behind a request header for a transition period.
- **A3. Partners round-trip `id` on `PUT`.** A partner whose system drops unknown fields will `PUT` rows without `id`. Those rows then get new IDs, and other callers' row addresses go stale, which shows up as `404 row_not_found`. That is safe but noisy. If it turns out to be common, `PUT` could fall back to matching rows by content or position, but I have not designed that.
- **A4. Separate row and document validators.** I chose to require the row ETag, not the document ETag, on `PATCH`. That costs one extra `GET`. The alternative is to accept a document ETag and succeed when that row hasn't changed since that document version. It saves the request, but the server would need to keep history of document versions, and one header would carry two meanings. It can be added later without breaking anything.
- **A5. Error body shape and missing-`If-Match` status.** The brief does not say what the current `PUT` returns when `If-Match` is missing, or what the error body looks like. I used `428` and "the existing v1 shape". If `PUT` already uses something else, match it.
- **A6. Row-level, not field-level, conflicts.** Two callers changing different fields of the same row still conflict (`412`). That is simpler and safer for prices. Field-level merge can be revisited if it causes friction.

````

> Result: File created successfully at: <run>/builds/4-established-precondition-contract-new-opus/work/docs/row-updates.md (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-new-opus/work\" && sed -i 's/pl8xK2mQ7rTz/pN8xK2mQ7rTz/g' docs/row-updates.md && grep -c pN8x docs/row-updates.md && git status --short"}`

> Result: 2 ?? docs/row-updates.md

**Assistant:** I've written the design to `docs/row-updates.md`. Nothing is committed, and no code or OpenAPI changes were made; it's a design document only.

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

**Session ended:** success, 8 turns, 104617 ms
