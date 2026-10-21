# Data Model

Model entities around the product's core object and the ownership boundary that protects them.

When many users can reference the same object, model the shared object separately from each user's relationship and relationship-owned metadata. Define object deletion independently from relationship deletion.

Value precedence is fixed: user-edited values outrank generated values, and generated values outrank defaults. A generated name or summary never overwrites something the user authored.

Display name priority follows the same rule. Store the user's name and the generated name in separate fields and derive the display name on read: the user's name, else the generated name, else a stable default.

User-facing status is coarse. Collapse internal pipeline steps into a few states a person understands. Keep fine-grained internal detail as metadata, not as user-visible states.

```text
uploading -> processing -> ready
uploading -> failed
processing -> failed
```

Prefer soft delete with an access or deletion timestamp when the object may be recovered, referenced, or audited. Hard delete only when there is no recovery or reference need.

Group with the lighter-weight concept that can later carry context, instructions, permissions, or behavior, rather than a rigid hierarchy chosen too early: a grouping entity of its own, referenced by ID through a membership relation rather than a fixed nested path.

Store sensitive metadata, raw provider payloads, and location only for a named product reason.
