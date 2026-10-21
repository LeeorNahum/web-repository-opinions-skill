# Failure And Retries

`failed` alone is not enough. Keep the user-facing status simple, but store the failure kind internally so the right recovery is offered.

Record why it failed: the input never arrived, the input is gone, a limit stopped it, processing failed, or the user abandoned it. Offer the recovery that fits: retry when the input still exists, ask for the input again when it is gone, show the quota stop when a limit stopped it, and keep whatever already succeeded usable.

A failed state is never a dead end. There is always a next action or a clear explanation. A failure that cannot move forward still lands somewhere observable and actionable, the application's equivalent of a dead-letter queue, never a silent drop.

Retry expensive jobs only on explicit user action. LLM calls, media processing, and other paid provider work count as expensive. Many provider SDKs retry on their own (the default LLM SDK retries twice unless told otherwise), so set the retry count to zero on those calls. A manual retry reuses the same code path, resets the visible status when appropriate, avoids starting a duplicate run, keeps the raw provider error internal, and shows clean copy.

Cheap, idempotent, transient operations may retry automatically with backoff. Expensive or billable ones may not. Auto-retry is safe only when the operation is idempotent, landing the same result whether it runs once or many times, so make the retried path idempotent before allowing any automatic retry.
