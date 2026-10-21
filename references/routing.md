# Routing

Every meaningful view and state has its own URL that a reload, a copied link, and Back restore. Route paths are product architecture. They live in code and docs, never in env.

Use one canonical route model per concept: one path per thing, never a long path and a short path alive together.

## Full Names And Collection Prefixes

A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix is the collection view for what lives under it.

- A leaf page with no children uses its full word: a single about page, a pricing page, a frequently-asked-questions page, an auth page. There is no shorter form, because there is nothing nested to disambiguate. An initialism readers already say as a word, such as faq, counts as the full word.
- A surface that contains items or subpages uses a prefix, and visiting the bare prefix shows the collection. The items live directly under it.

```text
/[prefix]            the collection view for that entity type
/[prefix]/[id]       one item of that type
```

This keeps a single canonical model: one prefix that is both the list and the parent of each item, never a separate long collection path beside a short item path. The path already encodes the entity type, so the identifier does not repeat it.

## Segment Economy

Not every segment carries the same reading weight. A segment a person actually reads to know what they are looking at, a collection name, a tab, a view, stays a full word. A segment that exists only as routing scaffolding, one nobody reads and every eye skips past, compresses to a short, stable token, its first letter is a common choice. Shorten the segments nobody reads. Spell out the ones that name the view.

In a product with a tenancy unit, private app routes nest the item prefix under the owning tenancy scaffold, itself compressed by the rule above:

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

## An Entity URL Resolves To Its Default View

A view has a URL. An entity has a URL too, and the two are not always the same URL. When an entity holds several child views (tabs, panels, modes), the bare entity URL has nothing of its own to render, so it resolves, with a history replace, to that entity's default child view. A tenancy root resolves to its default surface. An item with tabs resolves to its default tab.

- Link to the entity, never to its own computed default. The entity is the one place that decides its default view, so a caller, a list row, a search result, a notification, never needs to know the capability rules that pick it. When the default changes, every caller that links to the entity keeps working. Only the entity's own resolver changes.
- Resolve with a history replace, never a push, so the hop leaves no stop in the back button's history. Back from the resolved view returns to wherever the visitor actually came from, not to the bare entity URL.
- A bare entity URL that is typed, pasted, or bookmarked still resolves the same way. It is a legitimate, stable link to "this entity, however it currently presents itself," not a broken or transitional state.
- A child view URL the entity cannot serve, one naming a view this instance lacks or no view at all, resolves through the same replace to the entity's default rather than a dead end. When instances of one entity type offer different view sets, the entity's resolver absorbs the difference.
- If an entity has exactly one child view and will only ever have one, that child collapses into the entity directly. There is no resolve-elsewhere hop, because there is nowhere else to go. The entity URL is the view.

## The Active Workspace Lives In The URL

The URL selects which workspace (organization, team, account scope) a private app view addresses. Read the active workspace from the URL, and let provider session state, cookies, and client memory follow it.

- Every private route that addresses one workspace nests under the workspace scaffold (`/[scope]/[scopeId]/...`), so any such view is a shareable snapshot of exactly where it points, including the workspace.
- A view that spans workspaces, such as a library across all of them, lives outside the scaffold and carries its workspace filter as query state. It needs no active workspace at all.
- A workspace switcher, where the product has one, is navigation: switching links to the same surface under the other workspace's scaffold. It does not mutate session state and reload.
- When the auth provider carries its own active-organization session state, the app syncs that state to follow the URL segment on entry (activating the matching organization), then renders. A deep link into any workspace the user belongs to works from a cold session without bouncing through a chooser. The session follows the URL, never the other way around.
- The server still authorizes by verified identity and by membership or an individual share. The URL selects among what the caller can already reach and never grants access. A workspace segment that gives the caller neither a membership nor a share of the addressed resource fails to a clear product-owned screen.

## Stable Links

Links must survive reorganization. Give an entity that can move between parents its own top-level prefix rather than a place under the parent's path, so moving the parent never breaks a shared link.

Owner-nest a public resource only when the owner is part of how people identify, browse, and verify it. In that case, the owner segment supplies meaningful public context rather than database lookup scope. Keep the child ID globally unique, give the resource one canonical owner-nested URL, and keep ownership stable for the lifetime of that URL.

Use a top-level route when the resource is understood independently, can move between owners, or would keep the same identity after an ownership change. Give an owner-nested resource that one URL, and add a short alias only when a real migration or sharing requirement appears.
