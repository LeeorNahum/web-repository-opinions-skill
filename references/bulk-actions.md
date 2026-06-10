# Bulk Actions

Design bulk work as independent per-item outcomes unless the operation is inherently atomic.

## Result Contract

Return one structured result for every requested item. Include the stable input identity and a small product-level state such as completed, unchanged, or failed.

- Preserve successful and unchanged results when sibling items fail.
- Validate every item against the authorized scope at execution time.
- Process provider-backed work with bounded concurrency.
- Preserve the user's input order in returned results and combined output.
- Retry only unresolved items.

Remove completed items from pending retry state and keep failed items actionable. Do not roll back independent successes to simplify the UI.

## Partial Versus Atomic

Choose semantics from the operation:

- Use partial success when each item performs an independent fetch, conversion, import, or write.
- Use all-or-nothing behavior when one shared side effect cannot be meaningfully divided.

When partial output is allowed, include only successful items and no error placeholders. If no item succeeds, leave the destination unchanged.

## Side Effects And Metrics

Record metrics, usage, and deduplication only for items included in the successful durable side effect. Run non-critical accounting with settled promises so it cannot reverse a completed primary action.

Keep concurrency limits conservative and explicit. The limit protects provider quotas, browser resources, and backend execution without changing result order.

## Retry Experience

After partial failure:

- Keep failed items selected or otherwise ready to retry.
- Remove successful items from the pending set.
- Clear old per-item states when the source or scope changes.
- Submit only the remaining failures on retry.

Use compact per-item feedback. A large summary panel is justified only when the user must inspect or export detailed results.
