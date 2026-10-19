**Prompt:** Partners keep asking to change single rows (see docs/brief.md). Design the API addition and write it to docs/row-updates.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-established-precondition-contract-old-opus/work\" && git ls-files && cat docs/brief.md", "description": "List files and read brief"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5052 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-established-precondition-contract-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md versioning.md agent-tool-design.md | head -600; wc -l http-apis.md versioning.md agent-tool-design.md bulk-actions.md ids.md", "description": "Read HTTP API and versioning references"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 7330 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-established-precondition-contract-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat ids.md bulk-actions.md data-model.md source-of-truth.md modularity.md failure-and-retries.md", "description": "Read related references"}`

> Result: # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.  ## Entity IDs  For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.  - Length: a fixed 12 characters. - Alphabet: Base58, the case-sensi [... 13834 more characters]

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-established-precondition-contract-old-opus/work/docs/row-updates.md`

````text
# Single-row updates for price lists

Status: proposed, waiting for owner review. `docs/brief.md` takes precedence over this document wherever they disagree.

## Problem

Partners can only change a price list by sending the whole document back with `PUT /v1/price-lists/{id}`. To change one row they have to download a few hundred rows, edit one, and upload all of them. If anyone else wrote to the list in the meantime, they get `412` and have to start over. Several partners, plus our staff in the browser app, often edit the same list in the same hour, so a partner that only wanted to touch one row keeps running into conflicts over rows it never changed.

## Constraints we keep

- The v1 contract partners have built against for two years stays exactly as it is. `GET` and `PUT` on `/v1/price-lists/{id}` keep their shapes, headers, and status codes.
- Writes keep requiring a precondition. v1 has always protected against lost updates with `If-Match`, so the new endpoint does too. Nothing writes without one.
- Every write moves the document's ETag. When a row changes, the document has changed, so the document ETag must change too. Then an unattended sync that does a whole-document `PUT` with an ETag it read earlier gets `412`, as it does today, and doesn't silently overwrite a row someone else just changed. This is what keeps the new endpoint safe for partners who never adopt it.

## The addition

These are additive endpoints under the current `v1` base path. They don't change the meaning of anything that already exists, so no `v2` is needed.

### Read one row

```
GET /v1/price-lists/{id}/rows/{rowId}
```

- `200` with the row as JSON, using the same row shape as in the document.
- `ETag` header: the **row ETag**. It is strong and opaque, and it changes whenever that row's content changes.
- `404` if the list or the row doesn't exist, or isn't visible to the caller.

### Replace one row

```
PUT /v1/price-lists/{id}/rows/{rowId}
If-Match: <row ETag or document ETag>
Content-Type: application/json
```

The body is the complete row, in the same shape it has inside the document. Fields left out of the body are left out of the stored row. This is replace semantics, the same as the existing document `PUT`, just applied to one row.

`If-Match` is required, and it accepts either of two ETags:

| `If-Match` value | Check performed | When to use |
| --- | --- | --- |
| Row ETag (from `GET .../rows/{rowId}`) | Passes if **this row** is unchanged since it was read. Concurrent edits to other rows don't block it. | The normal path. It allows concurrent editing of the same list. |
| Document ETag (from `GET /v1/price-lists/{id}`) | Passes only if **the whole document** is unchanged since it was read. | Partners who already hold the document ETag from their sync and want to change a row without an extra read, and who accept the stricter check. |

The server can tell the two kinds apart because it mints both. Clients treat both as opaque.

Responses:

| Status | Meaning |
| --- | --- |
| `200` | The row was stored. The body is the stored row. `ETag` is the new row ETag. `Ledgerline-Document-ETag` is the document ETag right after this write. |
| `400` | The body isn't a JSON object, or the body's row `id` doesn't match `{rowId}`. A row can't be renamed or moved through this endpoint. |
| `404` | The list or row doesn't exist, or isn't visible to the caller. |
| `412` | The precondition failed: the row changed (row ETag), or the document changed (document ETag). |
| `422` | The row fails the same validation the document `PUT` applies to rows. The error names the field and the rule that failed. |
| `428` | `If-Match` is missing. Assumption: this should be whatever the document `PUT` returns today for a missing `If-Match` (see Assumptions). |

Errors use the existing v1 error body shape and stable error codes, for example `row_not_found`, `precondition_failed`, `precondition_required`, `row_id_mismatch`, and `row_invalid`.

### What happens to everything else after a row write

- The document's `ETag` changes. Any whole-document `PUT` that holds the earlier document ETag gets `412`, which is the existing behavior and protects that row write.
- Other rows' ETags don't change.
- `GET /v1/price-lists/{id}` returns the document with the new row in place. The document body itself doesn't change shape.

## Client guidance (for the partner docs)

1. To change one row: `GET` the row, edit it, then `PUT` the row with `If-Match` set to the row ETag.
2. On `412`: `GET` the row again, reapply your change to the fresh row, and retry. Only that row's conflict matters now, not the whole list's.
3. If a request times out and you don't know whether it landed, retrying with the old ETag gives `412` when it did land. `GET` the row and compare it with what you sent before you reapply anything.
4. Keep using whole-document `PUT` for bulk replacement. Expect it to hit `412` more often if other integrators move to row writes, because each row write still changes the document ETag. That's correct: the `412` is what stops you overwriting their change.

## Implementation notes

- Build one product capability, *update price-list row*. It takes a list ID, a row ID, a precondition (row or document), and the new row, and it returns the stored row plus both new ETags. The public API adapter, the staff browser app, and any future MCP tool or job all call this capability, so every writer shares one concurrency model and one set of validation rules. Staff edits in the browser app should move onto this path so they stop conflicting with partner syncs over unrelated rows.
- The precondition check and the write happen in one transaction against the stored list, so two concurrent row writes can't both pass a check against the same version.
- Row ETags may be a content hash of the canonical row, or a per-row version counter. Either works as long as the ETag is strong and changes whenever the row's content changes. With a content hash, an unrelated write that puts back identical content isn't a conflict, which is harmless.
- Document ETags keep their current derivation. The only requirement is that they change on every row write.
- Publish both endpoints in `api.ledgerline.example/openapi.json` before implementing them. The row schema is shared with the document's row schema, so there is one definition.
- Rate limiting stays at the edge and gateway, as it is today. Row writes are cheap, so they shouldn't count against the document-sized budget. Partners who switch from a full `PUT` to a row write should not lose throughput.
- The API change is a minor, backward-compatible change. Bump the API package's minor version in the same change that ships it.

## Out of scope for this change

- **Adding or deleting rows.** Partners asked to *change* one row. Adding rows (`POST .../rows`) and deleting them (`DELETE .../rows/{rowId}` with `If-Match`) follow naturally from this design, but they need decisions about ordering and soft delete, so they come in a follow-up.
- **Partial-field patch** (`PATCH` with JSON Merge Patch). Replacing the whole row with a row-level precondition already covers "change the price on one row" without a second patch dialect. Add it only if partners ask for it.
- **Batch row updates.** If they're needed later, a list-taking endpoint would loop the single-row capability and return one result per row, in input order, with failures inline. It wouldn't be one all-or-nothing transaction.

## Assumptions to confirm

1. **Rows have a stable, unique `id` inside a list.** The brief doesn't describe the row shape. This design addresses rows by ID and never by array position, because positions shift under concurrent edits. If rows don't have IDs today, we need to mint them: 12-character Base58, from the shared ID helper, added to the existing documents, and returned in `GET` as an additive field. We would also need to decide what a whole-document `PUT` does with rows that come in without an `id`. **This is the biggest open question.**
2. **The response to a missing `If-Match` matches the document `PUT`.** I wrote `428` here, but if the document `PUT` already returns something else, the row endpoint should copy it so partners see one behavior.
3. **The existing v1 error body shape and auth scopes apply unchanged.** A key that can `PUT` a list can `PUT` its rows. No new scope is introduced.
4. **Row order inside the document is meaningful but out of scope.** Replacing a row keeps its position.
5. **Validation rules for a single row are the same as the per-row rules inside the document `PUT`.** Any rule that spans rows, such as "no duplicate SKUs", is checked against the whole list inside the same transaction, and a violation returns `422`.
6. **Accepting the document ETag as an alternative precondition is worth its small extra complexity.** If you'd rather have one way to do it, drop that row of the table and require the row ETag only.
7. **`Ledgerline-Document-ETag` is a new response header name.** Rename it to match any existing naming convention for our custom headers.

````

> Result: File created successfully at: C:/tmp/wro-eval3/builds/3-established-precondition-contract-old-opus/work/docs/row-updates.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/row-updates.md`. It's a proposal only: I didn't change any code or commit anything.

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

**Session ended:** success, 7 turns, 84158 ms
