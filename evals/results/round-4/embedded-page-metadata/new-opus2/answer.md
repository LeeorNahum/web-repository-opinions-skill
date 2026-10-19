I wrote the design to `docs/metadata.md`. It isn't committed, and nothing has been built or tested yet. All four bugs come from one fact: browsers and link-preview tools only look at Tessel's outer wrapper page, never at the person's HTML running inside it. So the design has Tessel work out every title, icon and preview card itself, on its own server.

**How it addresses each bug:**
- **233 (private title leaked):** pages that aren't open to everyone never put their own title or text into what the server sends. Anyone not signed in as a member, and every preview tool, gets a blank fallback that only says "Tessel". Missing and deleted pages get the exact same response, so nobody can probe which addresses exist. Members still see the real title in their tab, but it's filled in by the browser after sign-in, so even a preview tool that sends a member's login cookies sees only "Tessel".
- **240 (every tab says Tessel):** the tab shows the page's own title and icon, read from its HTML when it's published. If the page changes its title while running, it tells the wrapper, and the tab updates.
- **247 (blank previews):** title, description and icon are read from the page's HTML at publish time. Pages built entirely by JavaScript fall back in order: the first heading, then the first paragraph, then the page's name. Publishing then tells the author which fields were missing.
- **251 (votes from nobody):** Tessel never runs page code to make previews. On top of that, the wrapper only lets a page save data after a visitor has clicked or typed in it, and the page's own code can't get around that check. Simply loading a page never changes anything.

**Preview images:** Tessel uses the image the page declares, if any. Otherwise it generates a card showing the Tessel logo, "Tessel" and the page title. Only public and unlisted pages get images. Each time an image is requested, Tessel checks whether the page is still public or unlisted, so turning a page private or deleting it takes effect immediately. The one exception is cards chat apps have already saved, which can't be recalled, so the make-private and delete flows warn about that.

**Calls I made without you (listed in the doc):**
1. Tab and card titles end in " · Tessel". Letting authors drop the suffix would be a separate decision.
2. Members see a private page's title in their own tab, but the server never sends it.
3. No screenshot previews for now, because taking one means running the page's code.
4. Pages can't save data on load, before any click. That breaks things like view counters, but writing on load is exactly what caused 251.
5. Unlisted pages get full preview cards, since anyone with the link can already open them.
6. Authors can optionally override title, description, icon and image in page settings. It's never required, so publishing is still just one HTML file.
7. I assumed every page already loads the Tessel runtime and is served from a separate domain from Tessel's own pages. If either isn't true yet, live tab titles and the save gate depend on adding it.
8. Exact URLs for the image route and page addresses are left to whoever designs routing.

One technical claim needs checking in real browsers before relying on it: that a click inside the page shows up as user activity in Tessel's wrapper even though they're on different domains. The save gate in point 4 depends on it.