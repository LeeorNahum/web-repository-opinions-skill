# Data Deletion

Use a bounded, resumable deletion job when one operation must remove a dependent data graph and cannot safely fit one transaction or function budget.

## Visibility

Define when the object stops appearing in normal reads. Mark it as deleting before dependent rows are removed when exposing a partially deleted graph would be invalid or misleading.

## Phases

Process the graph in explicit bounded phases:

1. Remove dependent relationships and child rows.
2. Remove deduplication, index, aggregate, cache, and auxiliary state.
3. Remove the primary record last when it anchors the remaining cleanup.

Every phase is idempotent. Persist progress, schedule the next bounded step, and let repeated invocation resume safely. This bounded, resumable sequence is a saga: each phase commits its own step, and where a step cannot simply be retried forward it carries a compensating action that undoes partial work and keeps counters and aggregates correct.

Keep counters and aggregate state accurate on every deletion path. Test interruption and repeated execution at each phase boundary.
