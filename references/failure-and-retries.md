# Failure And Retries

`failed` alone is not enough. Keep the user-facing status simple, but store the failure kind internally so the right recovery is offered.

```text
failed + upload
failed + media_missing
failed + quota_exceeded
failed + processing
failed + abandoned
```

Choose the recovery from the kind:

- Retry processing when the source media still exists
- Ask the user to upload again when media is missing
- Explain the limit clearly when quota failed
- Allow playback or partial use when the source exists even though a later step failed

A failed state is never a dead end. There is always a next action or a clear explanation.

Do not auto-retry expensive jobs. Transcription, LLM calls, media processing, and other paid provider work retry only on explicit user action. A manual retry reuses the same code path, resets the visible status when appropriate, avoids starting a duplicate run, keeps the raw provider error internal, and shows clean copy.

Cheap, idempotent, transient operations may retry automatically with backoff. Expensive or billable ones may not.
