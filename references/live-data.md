# Live Data

Prefer a reactive backend whose queries push updates to the client, and wire it so the UI updates live. Convex is the default. Live updates are a core reason to choose a reactive backend, so realize that value rather than leaving it half-wired.

- Subscribe to data through the reactive client so a change on the backend reflects in every open view without a manual refetch or a page reload.
- Let the query layer own loading and live state. Do not re-fetch on an interval or rebuild state by hand when the backend already pushes changes.
- Wire the auth-to-backend connection cleanly so an authenticated client establishes its reactive session correctly on first load, not only after a refresh. If a first authenticated load needs a refresh to start receiving data, the connection order is wrong.
- Keep mutations going through the backend so every subscribed client sees the result, rather than mutating local state in isolation.

When a view depends on data that can change, assume another client or another process may change it, and let the live subscription keep the view current.
