I've written the design to `docs/metadata.md`. The repo has no app code yet, so it's a plan to build against, not a fix, and nothing has been tested. I haven't committed it.

**How each bug gets fixed:**
- **240, every tab shows the Tessel icon:** when a page is published, Tessel reads its title, description, icon and preview image from the HTML without running it. The wrapper puts these into the tab title and icon, which read `{page title} · Tessel`. If the page changes its title or icon later, the Tessel runtime passes the change to the wrapper. The ` · Tessel` suffix is always kept, so a page can't make its tab look like another site.
- **247, blank link previews:** the preview-card tags are now in the HTML the server sends, so pages built entirely with JavaScript get a real card. The description falls back to `{title}: an interactive page by {author} on Tessel.` If a page has no preview image of its own, Tessel generates a 1200×630 card showing the Tessel mark, the page title and the author. Nobody has to make an image, which fits the brief.
- **233, private title leaked:** a private page's server HTML contains only generic "Tessel" values, even for signed-in members. A member's tab shows the real title only after their access is confirmed. The preview-image link also checks visibility, so an old image link reveals nothing. When a page goes private or is deleted, Tessel clears its cached copies. One thing Tessel can't do: the card already posted in that team chat stays until someone removes it there.
- **251, phantom poll votes:** loading a page must never save data. The runtime refuses saves until someone has clicked, tapped or typed on the page. The server also requires a short-lived token for that viewing, and rejects known preview tools, crawlers and prefetch requests.

**Calls I made, all noted in the doc:**
- The page's HTML runs in a sandboxed iframe on a separate domain. That's also why its own title and icon never reached the tab.
- The separator is `·`.
- Unlisted pages get a full, real preview card, since anyone with the link can open them anyway. They stay out of search and the sitemap.
- A signed-in member may see a private page's title in their own tab.
- No screenshot previews for now, because they mean running the page's code in a headless browser, the kind of load behind bug 251. They're listed as a later option.
- If an owner-editable page title is ever added, it overrides whatever is read from the HTML.

**Questions for you,** also listed at the end of the doc:
- Is the `·` separator right?
- Should unlisted pages have an option for a preview card that doesn't show the page's content?
- Do you want an owner-editable page title?
- Should we tell the person who reported bug 233 that the card already in their chat has to be removed in the chat app?