# Routing

Route paths are product architecture. They live in code and docs, never in env.

Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.

## Full Names And Collection Prefixes

A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix is the collection view for what lives under it.

- A leaf page with no children uses its full word: a single about page, a pricing page, a frequently-asked-questions page, an auth page. There is no shorter form, because there is nothing nested to disambiguate.
- A surface that contains items or subpages uses a prefix, and visiting the bare prefix shows the collection. The items live directly under it.

```text
/[prefix]            the collection view for that entity type
/[prefix]/[id]       one item of that type
```

This keeps a single canonical model: one prefix that is both the list and the parent of each item, never a separate long collection path beside a short item path. The path already encodes the entity type, so the identifier does not repeat it.

## Segment Economy

Not every segment carries the same reading weight. A segment a person actually reads to know what they are looking at, a collection name, a tab, a view, stays a full word. A segment that exists only as routing scaffolding, one nobody reads and every eye skips past, compresses to a short, stable token, its first letter is a common choice. Shorten the segments nobody reads. Spell out the ones that name the view.

Private app routes nest the item prefix under the owning tenancy scaffold, itself compressed by the rule above:

```text
/[scope]/[scopeId]
/[scope]/[scopeId]/[prefix]
/[scope]/[scopeId]/[prefix]/[id]
```

`[scope]` is whatever this product calls its tenancy unit, a workspace, an organization, a project, a team, compressed to a short token because nobody reads it. `[prefix]` stays a full word because it is what a person reads to know where they are.

Public routes for a marketing site are full descriptive leaf paths:

```text
/pricing
/security
/help/uploads
```

Links must survive reorganization. Do not nest a stable entity under a reorganizable parent in the URL when moving the parent would break shared links. If an entity can move between parents, keep it at its own top-level prefix rather than under the parent's path.

## An Entity URL Resolves To Its Default View

A view has a URL. An entity has a URL too, and the two are not always the same URL. When an entity holds several child views (tabs, panels, modes), the bare entity URL has nothing of its own to render, so it resolves, with a history replace, to that entity's default child view. A tenancy root resolves to its default surface. An item with tabs resolves to its default tab.

- Link to the entity, never to its own computed default. The entity is the one place that decides its default view, so a caller, a list row, a search result, a notification, never needs to know the capability rules that pick it. When the default changes, every caller that links to the entity keeps working. Only the entity's own resolver changes.
- Resolve with a history replace, never a push, so the hop leaves no stop in the back button's history. Back from the resolved view returns to wherever the visitor actually came from, not to the bare entity URL.
- A bare entity URL that is typed, pasted, or bookmarked still resolves the same way. It is a legitimate, stable link to "this entity, however it currently presents itself," not a broken or transitional state.
- If an entity has exactly one child view and will only ever have one, that child collapses into the entity directly. There is no resolve-elsewhere hop, because there is nowhere else to go. The entity URL is the view.

## The Active Workspace Lives In The URL

The URL is the sole owner of which workspace (organization, team, account scope) a private app view addresses. Never hold the active workspace in provider session state, a cookie, or client memory as an authority the URL merely reflects.

- Every private route nests under the workspace prefix (`/[workspace]/...`), so any view is a shareable snapshot of exactly where it points, including the workspace.
- The workspace switcher is navigation: switching links to the same surface under the other workspace's prefix. It does not mutate session state and reload.
- When the auth provider carries its own active-organization session state, the app syncs that state to follow the URL segment on entry (activating the matching organization, or none for a personal workspace), then renders. A deep link into any workspace the user belongs to works from a cold session without bouncing through a chooser; the session follows the URL, never the other way around.
- The server still authorizes by verified identity and membership. The URL selects among the workspaces the caller can already reach; it never grants access, and an unknown or unauthorized workspace segment fails to a clear product-owned screen.

Owner-nest a public resource only when the owner is part of how people identify, browse, and verify it. In that case, the owner segment supplies meaningful public context rather than database lookup scope. Keep the child ID globally unique, give the resource one canonical owner-nested URL, and keep ownership stable for the lifetime of that URL.

Use a top-level route when the resource is understood independently, can move between owners, or would keep the same identity after an ownership change. Do not create a second short alias for an owner-nested canonical route unless a real migration or sharing requirement appears.

Same-app navigation uses relative paths. Cross-app navigation goes through origin helpers, never hardcoded hosts.
