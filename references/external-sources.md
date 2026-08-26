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

## Discover, Review, Then Commit

An import points at something the product does not control, so the user rarely knows what is inside it. Do not make them guess and then punish the guess with an error.

Split the flow: a free, idempotent discovery read that reports what was actually found, a review step that shows it in the product's own language, and only then the commit. Discovery names each candidate by its real identity, read from the source itself, rather than by its path or by an assumption about how the source is laid out.

Accept every level of the address a user might reasonably paste, not only the one canonical shape. If a location contains several importable things, offer them all and let the user choose any subset, because dependencies between them are the user's knowledge and not the product's. A location containing exactly one is the same flow with the review step collapsed, never a different code path.

Charge quota for the whole selected batch in one decision before starting, or a per-item check will admit a batch that the limit was written to prevent.

## Skip, Do Not Abort

A source contains entries the product cannot use: links, submodules, oversized files, unsupported types, junk. Each of these is a reason to leave that entry out and say so, not a reason to fail the whole import. One unusable file in a corner of a repository must never be able to reject everything the user asked for.

Apply the scope filter first. An entry outside what the user is importing cannot be a reason to reject anything, and checking it before scoping turns unrelated content into a failure.

When two code paths can reach the same source, such as a public fetch and an authenticated install, they must classify entries identically. A path that hardcodes an assumption the other path actually checks will make the same import succeed or fail depending on how the user connected.
