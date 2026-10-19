I've written the design to `docs/metadata.md`. It isn't committed. The repo has no app code yet, so the causes it gives for each bug are worked out from the bug reports and the brief, not from code.

**The four bugs:**

- **240 (every tab shows the Tessel icon and "Tessel"):** browsers show the title and icon of Tessel's wrapper page, not those of the person's HTML running inside it. The fix:
  - When a page is published, Tessel reads its `<title>` and icon and puts them in the wrapper.
  - The tab reads `{page title} · Tessel`.
  - When the page changes its title or icon while running, the Tessel runtime passes the change up to the wrapper.
- **247 (blank link previews):** preview tools only read the wrapper's first response and run no JavaScript. The fix:
  - The wrapper always includes the page's title, description and preview image in that first response.
  - If the page sets these in its HTML, those win.
  - If it builds its content with JavaScript, a background job loads the page once, without saving anything, to find a title and description.
  - If neither works, defaults are used.
- **233 (private page title leaked):** access is checked before anything about the page goes into the response. A private page never gets a description or preview image, for anyone. For members, the page's title appears in their tab only after the wrapper's script runs, so even a preview tool that carries a member's cookies sees just "Tessel". To anyone without access, a private page looks exactly like an address that doesn't exist.
- **251 (votes from nobody):** the runtime refuses to save data until a real person has clicked or typed on the page. Preview tools that load the page never interact with it, so they can no longer vote.

**Preview images:** pages that are public or unlisted get a generated 1200×630 card showing the Tessel mark, the name and the page title. If the author's HTML declares its own preview image, that's used instead. There are no screenshots in v1: they freeze live data like vote counts and need the page loaded on every publish. When a page becomes private or is deleted, its card stops being served.

**Public vs unlisted:** both get the same full preview. Unlisted pages aren't indexed and are left out of the sitemap.

**Calls I made that you should confirm** (all ten are listed at the end of the doc):

- The person's HTML runs in a sandboxed frame on a separate domain from Tessel. This is required for security and for the title passing to work.
- The HTML file is the only place an author sets title, description and image. There's no Tessel settings form for them in v1.
- Tabs and previews are titled `{page title} · Tessel`.
- There's no "request access" screen for private pages, since one would confirm the page exists.
- No saving before a user interaction means a pure visit counter isn't possible.
- The visibility setting warns that previews already posted in other apps can't be recalled.

The doc also has a checklist for testing in real chat apps, which still needs doing once this is built.