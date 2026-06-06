# IDs

Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.

## Entity IDs

For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.

- Length: a fixed 12 characters.
- Alphabet: Base58, the case-sensitive set that drops the visually ambiguous characters (zero, capital O, capital I, lowercase L) and keeps the rest. This gives roughly 70 bits of entropy at 12 characters, which is collision-resistant and safe to expose.
- No prefix: the route path identifies the entity type, so the ID string carries no type marker.
- Stable and opaque: never a name or user-generated slug for a private, renameable, or sensitive object, because names change and URLs should not.

Generate these from one shared helper in a shared package so the length, alphabet, and entropy are standardized everywhere an entity ID is minted. Do not hand-roll the format per call site.

Expose one app-facing URL ID field, named `id`. Keep database-native IDs for internal relationships when useful, but do not expose them as the URL identity if they carry meaning or are guessable in a sensitive way.

Slugs are acceptable only when public SEO is the point of the page, such as a blog post or a docs article.

A private link is shareable only as a deliberate product feature. A short ID in a URL is not the same as public sharing; sharing is designed, not a side effect of copying a link. Ask before making a private object publicly shareable.

## Credential IDs

For secret keys, webhook signing secrets, restricted keys, and any token that must be identifiable out of context.

- A prefix identifies the credential type, and often its environment.
- A long random body follows the prefix: a UUID or a 32-or-more character secret.

Prefixes belong here, and not on entity IDs, because credentials appear in env files, logs, and dashboards with no route path to give them context. The prefix lets a human or a tool tell key types apart at a glance and prevents passing one kind of credential where another is expected. Never reuse the short fixed-length entity format for a credential body; a credential needs full-length opaque randomness.
