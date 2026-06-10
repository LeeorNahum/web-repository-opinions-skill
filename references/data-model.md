# Data Model

Model entities around the product's core object and the ownership boundary that protects them.

When many users can reference the same object, model the shared object separately from each user's relationship and relationship-owned metadata. Define object deletion independently from relationship deletion.

Value precedence is fixed: user-edited values outrank generated values, and generated values outrank defaults. A generated name or summary never overwrites something the user authored.

Display name priority follows the same rule: show the user's name if set, otherwise the generated name, otherwise a stable default. Store all three rather than overwriting one with another.

User-facing status is coarse. Collapse internal pipeline steps into a few states a person understands. Keep fine-grained internal detail as metadata, not as user-visible states.

```text
recording -> saving -> transcribing -> ready
recording -> deleted
saving -> failed
transcribing -> failed
```

Prefer soft delete with an access or deletion timestamp when the object may be recovered, referenced, or audited. Hard delete only when there is no recovery or reference need.

Group with the lighter-weight concept that can later carry context, instructions, permissions, or behavior, rather than a rigid hierarchy chosen too early.

Do not store sensitive metadata, raw provider payloads, or location without a clear product reason.
