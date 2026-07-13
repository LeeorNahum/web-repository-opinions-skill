# Rendering

Choose a rendering posture per surface based on who reads it and whether search engines matter.

- Public pages render on the server or generate statically. They must be crawlable, fast on first paint, and shareable without JavaScript.
- Signed-in pages render on the client behind auth. They favor live data, fast transitions, and persistent state over crawlability.

Match the posture to the surface, not the framework. Both surfaces can use the same framework and still render differently.

Do not server-render private data that only one user can see when client rendering behind auth is simpler and safer. Do not client-render a marketing page that needs SEO.

When a public page needs both fresh data and SEO, prefer server rendering with caching over a client fetch after paint.

## Picking The Tool Per Surface, Not One Tool For The Whole Repo

A public, crawlable surface and a private, reactive surface answer to different constraints, so it is normal, and often correct, for one repo to run two different rendering tools side by side: a server-rendering framework for the public site, a pure client build for the signed-in app. Neither tool should be assumed to fit both jobs.

Ask what the posture actually buys before reaching for it:

- Server rendering buys crawlability and a fast, meaningful first paint for an anonymous visitor. A signed-in surface has no anonymous visitor and nothing meaningful to paint before the session verifies and a live connection subscribes, so server rendering buys it nothing. The client still authenticates and fetches after the shell arrives, regardless of where that shell rendered.
- A framework that "feels quicker" is not, by itself, a reason to move a private surface onto it. A perceived-slow boot is usually a loading-state defect, not a rendering-posture problem. Diagnose the actual sequencing and geometry first, then reach for a rendering-posture change only when the posture itself, not the transition into it, is the real constraint.
