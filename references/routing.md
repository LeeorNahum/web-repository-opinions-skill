# Routing

Route paths are product architecture. They live in code and docs, never in env.

Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.

## Full Names And Surface Prefixes

A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a short prefix, and the bare prefix is the collection view for what lives under it.

- A leaf page with no children uses its full word: a single about page, a pricing page, a frequently-asked-questions page, an auth page. There is no shorter form, because there is nothing nested to disambiguate.
- A surface that contains items or subpages uses a short prefix, and visiting the bare prefix shows the collection. The items live directly under it.

Derive the short prefix from the entity itself, usually its first letter, kept stable and unique within its parent. The bare prefix is the collection view; each item lives one level under it.

The test: would the long collection word ever exist as a page on its own, with nothing referenced inside it? If not, the long word is redundant, so the surface uses the short prefix and the prefix itself is the list.

```text
/[prefix]            the collection view for that entity type
/[prefix]/[id]       one item of that type
```

This keeps a single canonical model: one prefix that is both the list and the parent of each item, never a separate long collection path beside a short item path. The path already encodes the entity type, so the identifier does not repeat it.

Private app routes nest the item prefix under the owning workspace:

```text
/[workspace]
/[workspace]/[prefix]
/[workspace]/[prefix]/[id]
```

Public routes for a marketing site are full descriptive leaf paths:

```text
/pricing
/security
/help/uploads
```

Links must survive reorganization. Do not nest a stable entity under a reorganizable parent in the URL when moving the parent would break shared links. If an entity can move between parents, keep it at its own top-level prefix rather than under the parent's path.

## The Active Workspace Lives In The URL

The URL is the sole owner of which workspace (organization, team, account scope) a private app view addresses. Never hold the active workspace in provider session state, a cookie, or client memory as an authority the URL merely reflects.

- Every private route nests under the workspace prefix (`/[workspace]/...`), so any view is a shareable snapshot of exactly where it points, including the workspace.
- The workspace switcher is navigation: switching links to the same surface under the other workspace's prefix. It does not mutate session state and reload.
- When the auth provider carries its own active-organization session state, the app syncs that state to follow the URL segment on entry (activating the matching organization, or none for a personal workspace), then renders. A deep link into any workspace the user belongs to works from a cold session without bouncing through a chooser; the session follows the URL, never the other way around.
- The server still authorizes by verified identity and membership. The URL selects among the workspaces the caller can already reach; it never grants access, and an unknown or unauthorized workspace segment fails to a clear product-owned screen.

Owner-nest a public resource only when the owner is part of how people identify, browse, and verify it. In that case, the owner segment supplies meaningful public context rather than database lookup scope. Keep the child ID globally unique, give the resource one canonical owner-nested URL, and keep ownership stable for the lifetime of that URL.

Use a top-level route when the resource is understood independently, can move between owners, or would keep the same identity after an ownership change. Do not create a second short alias for an owner-nested canonical route unless a real migration or sharing requirement appears.

Same-app navigation uses relative paths. Cross-app navigation goes through origin helpers, never hardcoded hosts.
