I've written the design to `docs/metadata.md`. The repo has no app code yet, so it's a design only: nothing is built or tested, and I didn't commit it.

**The core rule:** the browser and link-preview tools only ever read Tessel's wrapper page, never the author's HTML running inside it. So the wrapper's own server-rendered HTML sets the tab title, icon and preview tags, using values pulled from the page's HTML when it's published. Answering a preview request never runs the page.

**By visibility:**
- **Public:** tab reads `{page title} · Tessel` with the page's own icon, plus a full preview card. Indexed.
- **Unlisted:** the same full card, but marked not-to-be-indexed and left out of the sitemap. Anyone with the link can already open the page, and chat tools ignore that marker anyway.
- **Private:** the server always sends a card and tab title that say only "Tessel", even to signed-in members. The real title and icon are filled in by the browser after the member is authorized. Deleted and nonexistent pages get the same response, so a pasted link can't confirm a private page exists.

**How each bug is handled:**
- **240 (every tab shows the Tessel icon):** the page's title and icon are read from its `<head>` at publish, and the page's code inside the frame passes later title or icon changes up to the wrapper.
- **247 (blank previews):** the wrapper puts all the preview tags in its server-rendered HTML. If a page sets no title, Tessel uses its first heading, then "Untitled page". Publishing warns the author when the title or description is missing, but nothing extra is required.
- **Preview images:** made once, at publish. If the page declares an image, Tessel fetches it safely and keeps its own copy. Otherwise it draws a branded card with the page title. A failed image never blocks publishing.
- **233 (private title leaked):** private content never appears in server-rendered HTML.
- **251 (votes from nobody):** Tessel never runs a page to build a preview. Each save has to carry a short-lived token issued when a real person loads the page. By default the runtime also refuses saves until the visitor has clicked or typed something on the page. Pages that need to save on load, like view counters, opt in.

**Calls I made that need your OK** (all listed at the end of the doc):
1. **Saves need a click or keypress by default.** This changes how the runtime behaves for every page, so it's the one I'm least sure of.
2. **I haven't reproduced 251.** The cause is my best guess: something that builds previews ran the page and the runtime accepted a save on load. Check the poll page's code and the logs before closing it.
3. **The tab always keeps the "· Tessel" suffix.** It reads naturally and stops a page from posing as another site in the tab.
4. **Private tab titles only appear after the sign-in check.** Members see "Tessel" for a moment first.
5. **Unlisted links get full preview cards.**
6. **Tessel doesn't run pages in a headless browser** to read titles that a script sets, at least in the first version.
7. **Page addresses and the separate domain for author HTML are placeholders,** since neither is decided in the brief.

The doc also has a step-by-step check for each bug and a few open questions for you.