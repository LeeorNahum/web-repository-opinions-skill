# Source Of Truth

Pick one durable owner per fact. The app orchestrates between owners; it does not duplicate truth casually.

| Fact | Owner |
| --- | --- |
| App state, metadata, status, permissions, usage, jobs | Database |
| Raw bytes of large media | Object storage |
| Subscription and payment truth | Billing provider |
| Login identity | Auth provider |
| Pure product rules and constants | Domain package |
| Deploy and runtime env values | Hosting and provider stores |

The database references object keys; object storage never becomes a second app database. The app reads subscription truth from the billing provider rather than mirroring it as the authority.

When two systems seem to hold the same fact, decide which one is authoritative and make the other a cache or a reference, not a competing source.
