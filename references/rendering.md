# Rendering

Choose a rendering posture per surface based on who reads it and whether search engines matter.

- Public pages render on the server or generate statically. They must be crawlable, fast on first paint, and shareable without JavaScript.
- Signed-in pages render on the client behind auth. They favor live data, fast transitions, and persistent state over crawlability.

Match the posture to the surface, not the framework. Both surfaces can use the same framework and still render differently.

Do not server-render private data that only one user can see when client rendering behind auth is simpler and safer. Do not client-render a marketing page that needs SEO.

When a public page needs both fresh data and SEO, prefer server rendering with caching over a client fetch after paint.
