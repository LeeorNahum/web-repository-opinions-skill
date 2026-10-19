**Prompt:** Partners keep asking to change single rows (see docs/brief.md). Design the API addition and write it to docs/row-updates.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-old-opus2/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5052 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md versioning.md agent-tool-design.md | head -400"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 7216 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-old-opus2/work/.claude/skills/web-repository-opinions/references\" && grep -il \"etag\\|if-match\\|concurren\\|optimistic\\|patch\\|compatib\" *.md; cat ids.md data-model.md bulk-actions.md | head -250"}`

> Result: agent-plugins.md ai-model-routing.md bulk-actions.md cleanup.md continuous-integration.md definition-of-done.md design-tokens.md http-apis.md live-data.md loading-states.md model-context-protocol.md object-storage.md responsive-layout.md spa-feel.md versioning.md workspace-tenancy.md # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers f [... 6275 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-established-precondition-contract-old-opus2/work\" && cat package.json pnpm-workspace.yaml; grep -n -i \"etag\\|if-match\\|precondition\\|concurren\" .claude/skills/web-repository-opinions/references/{live-data,failure-and-retries,user-facing-errors,source-of-truth}.md | head -30"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*"

**Tool call `Write`:** `<run>\builds\4-established-precondition-contract-old-opus2\work\docs\row-updates.md`

````text
# Row updates for price lists

Status: proposed, waiting for owner review. The assumptions this design depends on are listed at the end.

## Problem

Partners want to change one row of a price list without sending the whole document (see `docs/brief.md`). The v1 contract partners have built against for two years has two endpoints:

- `GET /v1/price-lists/{id}` returns the document with an `ETag`.
- `PUT /v1/price-lists/{id}` replaces the document and requires `If-Match`. A stale ETag gets `412 Precondition Failed`.

Several partners and our staff often edit the same list in the same hour, and many partners sync unattended every few minutes. So a row update must:

1. Never silently overwrite someone else's change. This is the same guarantee `PUT` gives today.
2. Not fail just because a *different* row changed. Otherwise row updates would conflict as often as whole-document `PUT`s, and partners would gain almost nothing.
3. Leave the existing `GET`/`PUT` contract exactly as it is.

## Design summary

- Add one endpoint, `PATCH /v1/price-lists/{id}/rows/{rowId}`. It changes one row's fields with a JSON Merge Patch body.
- Add `GET /v1/price-lists/{id}/rows/{rowId}`, which returns one row with its own **row ETag**.
- `If-Match` is required on `PATCH`, the same as on `PUT`. It accepts either:
  - the **row ETag**, which fails only if *this row* changed (the normal path), or
  - the **document ETag**, which fails if *anything in the list* changed (strict, and needs no extra request for clients that already hold the document).
- Every row change also changes the document ETag. A partner holding an older document still gets `412` on `PUT`, as today. That is how the existing contract protects their whole-document writes from row edits made by others.
- This is an additive change inside `v1`. No existing request or response changes.

## Row identity

A row is addressed by a stable `rowId`, never by its array position. Positions shift when another writer inserts, removes, or reorders rows, so an index-addressed update made under concurrency could change the wrong row.

**Assumption A1:** each row in the document already carries a stable, server-unique `id` field. If it doesn't, see "If rows have no IDs" below.

`rowId` is opaque to callers. Clients copy it from the document and never construct it.

## Endpoints

### `GET /v1/price-lists/{id}/rows/{rowId}`

Returns `200` with the row object, in exactly the shape it has inside the document, and these headers:

- `ETag`: the row ETag, a strong, opaque validator that changes whenever this row's content changes.

Also supports `If-None-Match` and returns `304` when the row is unchanged. This keeps polling cheap.

Errors: `404 price_list_not_found`, `404 row_not_found`.

### `PATCH /v1/price-lists/{id}/rows/{rowId}`

Request:

```http
PATCH /v1/price-lists/pl_7Hk2.../rows/r9QxW... HTTP/1.1
Host: api.ledgerline.example
Content-Type: application/merge-patch+json
If-Match: "<row ETag or document ETag>"

{ "unitPrice": "12.40", "minQuantity": 10 }
```

Body semantics follow JSON Merge Patch (RFC 7396), applied to the one row:

- A field that is present gets that value.
- A field set to `null` removes it, but only for fields that the row schema marks optional. Removing a required field fails with `422`.
- An absent field stays unchanged.
- `id` cannot be changed. A body that includes a different `id` fails with `422 row_id_immutable`.
- The patched row must validate against the same row schema that `PUT` enforces. There is one row schema, shared by `PUT`, `PATCH`, the row `GET`, and the browser app.

Other content types get `415`. Merge Patch was chosen over JSON Patch (RFC 6902) because a row is a small, flat-ish record. "Send the fields you're changing" is what partners asked for, and Merge Patch has no array-index paths that could cause the problem described in "Row identity".

Success: `200` with the full updated row as the body, and these headers:

- `ETag`: the row's new ETag. The client can chain further `PATCH`es to the same row with this value.

The response intentionally does **not** include the new document ETag. A client that patched its local copy and then `PUT` the whole document with that ETag would overwrite rows that other writers changed between its `GET` and its `PATCH`. A client that needs to `PUT` again must re-`GET` the document first. This is what the current contract already expects.

A patch that changes no values succeeds with `200`, and neither the row ETag nor the document ETag changes.

### Preconditions and errors

| Situation | Status | `code` |
| --- | --- | --- |
| `If-Match` missing | `428 Precondition Required` | `precondition_required` |
| `If-Match` is a row ETag and this row changed since then | `412 Precondition Failed` | `row_changed` |
| `If-Match` is a document ETag and the document changed since then | `412 Precondition Failed` | `price_list_changed` |
| `If-Match` is a row ETag for a different row, or an unrecognized value | `412 Precondition Failed` | `precondition_mismatch` |
| `If-Match: *` | `428` | `precondition_required` (a wildcard would allow blind writes) |
| List or row doesn't exist (including a row deleted by a `PUT`) | `404` | `price_list_not_found` / `row_not_found` |
| Body is not a valid merge patch, or the result fails the row schema | `422` | `invalid_row`, with the failing field paths |
| Wrong content type | `415` | `unsupported_media_type` |

Error bodies use the same typed error shape as the rest of v1 (A4). The `412` responses on this endpoint also include a `current` member with the row as it is now, and an `ETag` header with its current row ETag. An unattended sync can then decide whether to reapply its change or skip it without an extra round trip.

Retries are safe without an idempotency key. If a client retries a `PATCH` whose first attempt landed but whose response was lost, the retry gets `412 row_changed` with `current` already showing its own values. Client guidance in the API docs will say: on `412`, compare `current` with what you meant to write before reapplying.

## Interaction with the existing contract

- **Document ETag:** every landed row change produces a new document ETag. `GET /v1/price-lists/{id}` returns the patched row and the new ETag. `PUT`s against the old ETag get `412`, as they do today.
- **Row ETag after `PUT`:** when a `PUT` replaces the document, the server matches rows by `id`. A row whose content is unchanged keeps its row ETag. A changed row gets a new one. A row the `PUT` removed returns `404` on later `PATCH`es. This prevents a whole-document sync that only touched other rows from invalidating row-level writers.
- **Ordering and atomicity:** each `PATCH` is one transaction on the list. It checks the precondition, applies the patch, validates it, and bumps both the row version and the document version together. It is serialized against `PUT`s on the same list, so a `PATCH` and a `PUT` can never interleave halfway.
- **Live updates:** the browser app sees the change through the same reactive subscription it uses for document edits. Staff edits in the app go through the same row-update capability, not a separate code path.

## Implementation shape (for when we build it)

- There is one product capability, `updatePriceListRow(listId, rowId, patch, precondition)`. The Hono `v1` route and the browser app both call it. Authorization is enforced inside that capability, at the same scope as `PUT` on the list (A3).
- Storage keeps a monotonically increasing `version` per row and per list. ETags are derived from these versions and encoded so the server can tell row ETags from document ETags. Callers must treat both as opaque.
- The OpenAPI document at `api.ledgerline.example/openapi.json` gets both new operations, the shared row schema, and the error codes above. That contract is settled before implementation.
- Rate limiting is the same gateway policy as other v1 writes.

## Out of scope for this addition

These are left out deliberately, so the first addition stays small and matches what partners asked for:

- Creating, deleting, or reordering rows individually. Callers keep using `PUT` for these. They can come later as `POST /rows` and `DELETE /rows/{rowId}` with the same precondition rules.
- Batch row updates. If partners need them, a batch endpoint would return one result per row, in input order, with conflicts reported inline.
- Any change to `GET`/`PUT` behavior.

## Assumptions (please confirm or correct)

- **A1. Rows have stable IDs.** I assumed each row already has a stable, unique `id`. **If rows have no IDs:** we start returning a server-assigned `id` on every row in `GET`. This is additive, but strict partner parsers that reject unknown fields would break, so it needs a heads-up to partners. On `PUT`, rows sent without an `id` get a new one. This would be the only change partners can see in the existing endpoints, so it needs your sign-off.
- **A2. Accepting the document ETag in `If-Match` is worth it.** It gives partners who already hold the document a zero-extra-request path, at the cost of more `412`s on busy lists. If you'd rather have one rule, drop it and require row ETags only. The rest of the design is unchanged.
- **A3. The same permission covers both.** I assumed whoever may `PUT` a list may patch its rows, with no new partner scope.
- **A4. A typed error body already exists in v1.** If v1 returns errors without a `code`, the new endpoints will still return the codes above. That's additive.
- **A5. `428` for a missing `If-Match`.** I assumed `PUT` returns `428` for a missing `If-Match` today. If it returns something else, `PATCH` should match `PUT`.
- **A6. The `/rows/{rowId}` path and the `merge-patch+json` media type** are my choice of names. Nothing in the brief constrains them.

````

> Result: File created successfully at: <run>\builds\4-established-precondition-contract-old-opus2\work\docs\row-updates.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/row-updates.md`. I didn't commit it. It's a design doc only: there's no code in the repo yet, so nothing was built or tested.

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

**Session ended:** success, 8 turns, 87523 ms
