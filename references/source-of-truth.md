# Source Of Truth

Pick one durable owner per fact. This is the single source of truth principle: one authoritative owner per fact, with every other copy a cache or a reference and never a competing authority. The app orchestrates between owners; it does not duplicate truth casually.

| Fact | Owner |
| --- | --- |
| App state, metadata, status, permissions, usage, jobs | Database |
| Raw bytes of large media | Object storage |
| Subscription and payment truth | Billing provider |
| Login identity | Auth provider |
| External resource identity, canonical metadata, and availability | Source provider |
| Pure product rules and constants | Domain package |
| Deploy and runtime env values | Hosting and provider stores |

The database references object keys; object storage never becomes a second app database. The app reads subscription truth from the billing provider rather than mirroring it as the authority.

When two systems seem to hold the same fact, decide which one is authoritative and make the other a cache or a reference, not a competing source.

## Derive, Do Not Store, A Computed Fact

A fact that is a pure function of an owned fact is derived from that owner on read, not written as its own copy. A stored copy drifts from its source and needs a job to keep it in step; a derived one stays correct for free and changes the moment the source does. Compute coverage, capability, capacity, status, and display values from the plan, host, role, or record they follow, rather than stamping a flag that a later change can leave stale.

Store a computed value only for a reason that derivation cannot serve: a point-in-time record where history is the value (what a plan or price was at the moment of a charge), an explicit cache for a cost you have measured (invalidated from its source, never the authority), a last-known mirror of an external system you cannot query on every read (reconciled by its webhooks), or a value that is itself authoritative input rather than a derivation.
