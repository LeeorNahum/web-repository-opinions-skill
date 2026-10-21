# Data Deletion

Use a bounded, resumable deletion job when one operation must remove a dependent data graph and cannot safely fit one transaction or function budget.

## Visibility

Define when the object stops appearing in normal reads. Mark it as deleting before dependent rows are removed when exposing a partially deleted graph would be invalid or misleading.

## Phases

Process the graph in explicit bounded phases:

1. Remove dependent relationships and child rows.
2. Remove deduplication, index, aggregate, cache, and auxiliary state, and the stored objects, found through the write ledger rather than the rows being deleted.
3. Remove the primary record last when it anchors the remaining cleanup.

Run each phase as a bounded, idempotent job step that persists its progress and schedules the next, so a repeated invocation resumes safely. That makes the sequence a saga: where a step cannot simply be retried forward, it carries a compensating action that undoes partial work, so counters and aggregate state stay accurate on every deletion path. Test interruption and repeated execution at each phase boundary.
