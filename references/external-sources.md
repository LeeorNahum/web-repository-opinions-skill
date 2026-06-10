# External Sources

Use this pattern when the application indexes or references a resource whose identity and availability remain owned by another system. Preserve the application's stable identity while treating the source provider as authoritative.

## Identity

- Store the provider's stable resource ID separately from mutable names, paths, handles, and URLs.
- Use the stable provider ID to detect renames, ownership transfers, and canonical metadata changes.
- Preserve the application's ID, relationships, metrics, and public URL when provider metadata changes.
- Rebuild every derived key, title, URL, and search field after canonical metadata changes.
- Acquire missing stable IDs during normal checks when a global backfill would create unnecessary provider traffic.

Provider identity and application identity solve different problems. The provider ID follows the external resource. The application ID preserves the product's references and relationships.

## References And Paths

Track whether a reference follows the provider default or was explicitly chosen.

- Let default references follow the provider's current default.
- Keep explicit branches, tags, versions, and revisions explicit.
- Preserve the tracked path exactly.
- Treat a missing path as a source failure rather than guessing a move or rename.

Guessing creates a new resource under an old identity. Recovery must come from a confirmed canonical result or a new user choice.

## Checks

Run provider checks from meaningful access paths such as initial import, current-content access, stale detail access, and targeted recovery. Passive collection rendering must not create provider traffic.

Classify failures by certainty:

- Definitive failure proves the tracked repository, reference, object, or path is unavailable.
- Transient failure includes rate limits, authentication configuration, ambiguous authorization, provider outages, networks, and timeouts.

Only definitive failures advance destructive lifecycle state. Keep provider codes, retry schedules, and internal reasons out of user-facing copy.

## Recovery

Keep unavailable resources visible when their metadata, links, relationships, or recovery actions remain useful. A successful check restores the resource immediately and invalidates older scheduled work.

Let a user's primary fetch or use action perform an immediate recovery attempt when that action already requires fresh provider data. Avoid adding a separate manual health control unless it serves a distinct need.
