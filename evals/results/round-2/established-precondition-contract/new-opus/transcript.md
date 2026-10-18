**Prompt:** Partners keep asking to change single rows (see docs/brief.md). Design the API addition and write it to docs/row-updates.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-established-precondition-contract-new-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5052 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-established-precondition-contract-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md versioning.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 2891 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-established-precondition-contract-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat ids.md failure-and-retries.md bulk-actions.md; grep -n -i -E \"etag|if-match|precondition|idempot|stale|conflict|row\" *.md | head -60"}`

> Result: # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.  ## Entity IDs  For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.  - Length: a fixed 12 characters. - Alphabet: Base58, the case-sensi [... 25417 more characters]

**Tool call `Write`:** `<run>/builds/2-established-precondition-contract-new-opus/work/docs/row-updates.md`

````text
# Single-row updates

Status: proposed, waiting for owner review. Assumptions are listed at the end.

## Problem

Partners can only change a price list with `PUT /v1/price-lists/{id}`, which replaces the whole document and needs the document's `ETag` in `If-Match`. To change one row they have to download a few hundred rows, edit one, and send them all back. Because several partners and our staff often edit the same list in the same hour, any edit to any row makes the document ETag stale. Unattended syncs then keep getting `412` for changes that never touched the row they care about.

## Decision

Add one sub-resource to v1: a single row of a price list, addressed by its stable row key, with its own ETag.

```
GET /v1/price-lists/{id}/rows/{rowKey}
PUT /v1/price-lists/{id}/rows/{rowKey}
```

This is an additive change to v1 (new paths only). The existing document `GET` and `PUT` keep their current behavior exactly.

### `GET /v1/price-lists/{id}/rows/{rowKey}`

- `200` with the row as JSON, in exactly the same shape it has inside the document.
- `ETag` header holding the row's ETag (opaque, strong).
- `404` if the price list or the row does not exist.

### `PUT /v1/price-lists/{id}/rows/{rowKey}`

Replaces one row. It follows the same rules as the document `PUT`: you send the whole row, and `If-Match` is required.

Request:

- Body: the complete row, in the same shape as in the document. If the body includes the key field, it must equal `{rowKey}`.
- `If-Match: <row ETag>` is required.

Responses:

| Status | When |
| --- | --- |
| `200` | Row replaced. Body is the stored row. `ETag` is the row's new ETag. |
| `404` | The price list or the row does not exist. This endpoint never creates rows. |
| `412 Precondition Failed` | This row changed since the caller read it. The caller re-reads the row and decides again. |
| `428 Precondition Required` | `If-Match` is missing. |
| `422` | The row fails the same validation a row gets inside a document `PUT`, or the key in the body doesn't match the path. |

Errors use the same typed error body that v1 already returns.

### Precondition semantics

The guard partners already know stays in place: no write lands blind. What changes is its scope.

- A row's ETag changes only when **that row's** content changes, whether by a row `PUT`, a document `PUT`, or a staff edit in the browser app.
- Any row change is a document change, so it also changes the **document** ETag. A stale whole-document `PUT` still gets `412`, just as it does today. Nothing in the existing contract gets looser.
- Two callers editing different rows of the same list no longer conflict. Two callers editing the same row still get the same `412` protection the document has today.
- `If-Match` on the row endpoint is checked only against the row's ETag. A document ETag sent there will not match and gets `412`. One validator per resource keeps the rule simple for partners to reason about.

### Retries

A row `PUT` is safe to retry automatically. Suppose the first attempt landed but the response was lost. The retry carries the old ETag, so it gets `412`. The caller re-reads the row, sees its own value, and stops. No idempotency key is needed.

### Implementation constraints

- The row write is a read-check-write on the stored document, inside the same transaction or lock the document `PUT` uses. A row write and a document write must never interleave.
- Store a per-row revision (or equivalent) so the row ETag is cheap to compute and changes only with that row. A document `PUT` bumps the revision only for rows whose content actually differs.
- The API's row endpoint and the browser app both call one shared product capability: "replace row, given expected row version". Validation and precondition rules then live in one place, and staff edits invalidate partner row ETags (and the other way round).
- Add both operations to `api.ledgerline.example/openapi.json` before implementing them. The row schema is the same schema used for rows inside the document, not a second definition.
- Rate limiting and auth are the same as for the document endpoints.

## Considered and not chosen

- **`PATCH` on the document (JSON Patch / Merge Patch) guarded by the document ETag.** This cuts payload size but keeps the main pain: any concurrent edit anywhere in the list causes `412`. JSON Patch addresses rows by array index, and an index shifts when a concurrent edit inserts or removes a row, so it can silently hit the wrong row.
- **Row `PATCH` with partial fields.** Rows are small, and full-row `PUT` matches the replace-with-`If-Match` model partners have used for two years. A partial update can come later if partners ask for it.
- **Putting row ETags inside the document body.** Partners send the document back on `PUT`, so this would add fields some partners' strict parsers or validators may reject. Leave the document shape alone.
- **Accepting the document ETag on the row endpoint too.** This would save a partner who already holds the document one `GET`. But it mixes two validators on one resource and brings back conflicts on unrelated rows. It can be added later without breaking anything if partners need it.

## Out of scope for this change

Adding and removing single rows (`POST .../rows`, `DELETE .../rows/{rowKey}`). Both fit the same model: `DELETE` with the row `If-Match`, and `POST` guarded by key uniqueness. Partners only asked to change existing rows, so these wait until the owner confirms they're wanted.

## Assumptions (please confirm)

1. **Rows have a stable, unique key** (for example a SKU or product code) that partners already know. This is the assumption the design depends on most. If rows have no such key, we first need server-assigned row IDs, exposed additively in the document, before this endpoint can exist. Array position is never acceptable as an identifier.
2. `{rowKey}` is that key value, URL-encoded. Keys are assumed not to change. Renaming a key is a delete plus an add.
3. The document `PUT` currently answers a missing `If-Match` with `428`. If it answers differently, the row endpoint copies whatever it does.
4. v1 already has a typed error body and per-row validation rules, and the row endpoint reuses both unchanged.
5. A row change is a normal document change in every other way: audit history, change notifications, and anything else triggered by a document `PUT` fires for row writes too.
6. Shipping this as an additive change within v1 is acceptable. No v2 is needed, because no existing request or response changes.

````

> Result: File created successfully at: <run>/builds/2-established-precondition-contract-new-opus/work/docs/row-updates.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/row-updates.md`. I didn't commit it, so it's waiting for your review.

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

**Session ended:** success, 7 turns, 103365 ms
