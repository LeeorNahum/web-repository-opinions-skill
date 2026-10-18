I've written the design to `docs/row-updates.md`. It's a proposal only: there's no code or OpenAPI file in the repo yet, and I haven't committed anything.

**The design:**
- **New row endpoints:** `GET` and `PUT` on `/v1/price-lists/{id}/rows/{rowId}`. The `PUT` replaces one whole row, which matches how the existing full-document `PUT` works and makes timed-out requests safe to retry for partners' unattended syncs.
- **Conflicts are checked per row:** each row has its own ETag, and a row `PUT` needs `If-Match` with that row ETag. If row edits had to match the document ETag instead, staff and partners editing the same list in the same hour would keep rejecting each other's edits.
- **The existing two-year-old contract keeps working:** every row edit also changes the document ETag. A partner holding an old copy of the document still gets `412` on their next full `PUT`, so they can't overwrite someone's row edit without noticing.
- **Rows get a stable `id`, minted by the server:** position in the list and natural keys (like a product code) both break when other people insert, reorder or rename rows. The doc sets out how full-document `PUT` keeps, assigns or rejects ids.
- **It stays in `/v1`:** everything is additive, so it's a minor version bump of the API contract, with the OpenAPI change settled before implementation.
- **The staff browser app uses the same single-row edit path**, so staff and partners follow the same conflict rules.
- **Out of scope for now:** creating or deleting single rows, editing individual fields within a row, and changing several rows in one call.

**What I assumed, all listed in the doc:**
1. Rows have no stable id today. If they already have one, we use it instead.
2. Adding `id` to each row in `GET` responses won't break partners who validate responses strictly.
3. A missing `If-Match` returns `428`, and error bodies follow the existing v1 shape. These should match whatever the current `PUT` actually does.
4. Row edits need the same permission as full-document edits.
5. It's acceptable that row edits will cause more `412`s for partners doing full-document `PUT`s. That's the existing contract working as designed, but partners will notice and should be warned in the changelog.

**Questions for you tomorrow:**
- Do rows already have an id, or a natural key partners rely on?
- Do any partners validate strictly enough that a new `id` field would break them?
- Should creating and deleting single rows ship in the same release?
- Do partners want to change several rows in one call soon?