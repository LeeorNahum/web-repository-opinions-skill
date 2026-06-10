# Search Indexing

Define search as a product contract rather than appending whatever data happens to be available.

## Search Surface

List the fields search covers and keep one backend helper responsible for constructing the indexed text or search document. New writes, canonical metadata updates, and migrations all call the same builder.

Index metadata by default. Add full-content search only when users need it and the product accepts the storage, privacy, freshness, ranking, and deletion obligations.

Keep fetched contents temporary when they exist only to satisfy the current request. A fetch must not silently expand durable search or storage scope.

## Query Behavior

Normalize case and whitespace consistently. Choose token matching, phrase matching, ranking, and field weighting deliberately, then test those semantics as domain behavior.

Search implementation belongs behind a product-level interface so the storage engine or provider can change without rewriting callers.

## Migration Sequence

When changing indexed material:

1. Deploy code that writes only the new search shape.
2. Define a resumable migration using the canonical builder.
3. Dry-run it in a non-production environment.
4. Run it in each approved environment.
5. Verify every record equals builder output.
6. Confirm removed material no longer matches.
7. Remove obsolete indexing functions and references.

Do not wipe primary objects, relationships, metrics, or public IDs to rebuild a derived search field.

## Verification

Provide an independent verification query or command. Migration completion proves traversal finished, not that every derived field is correct.
