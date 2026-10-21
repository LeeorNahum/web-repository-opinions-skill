# Rendering

Choose a rendering posture per surface based on who reads it and whether search engines matter.

- Public pages render on the server or generate statically. They must be crawlable, shareable without JavaScript, and fast on first paint, with Largest Contentful Paint at or under 2.5 seconds on a mobile profile.
- Signed-in pages render on the client behind auth. They favor live data, fast transitions, and persistent state over crawlability.

Match the posture to the surface, not the framework. Both surfaces can use the same framework and still render differently.

When a public page needs both fresh data and SEO, prefer server rendering with caching over a client fetch after paint.

## Picking The Tool Per Surface, Not One Tool For The Whole Repo

A public, crawlable surface and a private, reactive surface answer to different constraints, so it is normal, and often correct, for one repo to run two different rendering tools side by side: a server-rendering framework for the public site, a pure client build for the signed-in app. Neither tool should be assumed to fit both jobs.

Ask what the posture actually buys before reaching for it. Server rendering buys crawlability and a fast, meaningful first paint for an anonymous visitor. A signed-in surface has no anonymous visitor and nothing meaningful to paint before the session verifies and a live connection subscribes, so server rendering buys it nothing. The client still authenticates and fetches after the shell arrives, regardless of where that shell rendered.
