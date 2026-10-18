I've written the design to `docs/metadata.md`. I didn't commit it.

**Why the bugs happen.** Your HTML runs inside Tessel's wrapper page, so browsers and link-preview tools only ever read the wrapper.
- **#240 (tab icon and title):** browsers ignore the icon and title set inside the embedded page.
- **#247 (blank previews):** preview tools don't run script, so they found no page details in the wrapper. A page built with JavaScript has nothing they can read either.
- **#233 (private title leak):** a signed-out request got page content.
- **#251 (phantom votes):** some preview tools, such as iMessage, load the page in a real browser and run its code.

**What the design does:**
- **Each page's title, description, icon and preview image are worked out once, when it's published.** They come from the HTML the author already wrote; nobody needs a manifest or an image. An author's own settings in Tessel win over anything detected, and detected values win over defaults.
- **Public and unlisted pages get a full preview card.** The default image is a generated card with the Tessel mark and the page title. An image the author declares in their HTML replaces it. Unlisted pages are hidden from search engines but still get the full card, since anyone with the link can see the page anyway.
- **Private pages never put content in the page Tessel sends back, even to members.** The tab title and icon are filled in by the browser after access is confirmed. Signed-out visitors and preview tools get a generic Tessel card. The page's own content address needs a short-lived signed token, and icon and image addresses check the page's current visibility on every request.
- **Pages built with JavaScript get a one-time background render** at publish, used only when the HTML has no title or description to read. In that render, saving data appears to work but nothing is stored.
- **Tab titles and icons stay live:** when a running page changes its own title or icon, the tab follows.
- **Saves wait until a person interacts with the page.** Saves made before that are held, and dropped if nobody ever interacts. This is the main fix for #251.

**Calls I made without you** (all listed in the doc):
- The tab shows the author's title alone, with no "· Tessel" on the end.
- The default preview image is a generated card, not a screenshot.
- The hold on saves applies to every page, with no opt-out. Any page that saves on load without interaction, such as a view counter, will now only count visitors who interact.
- I assumed pages run on a separate content domain and that the Tessel runtime runs inside every page.
- The size and length limits are starting guesses, not researched figures.

**Questions for you:**
- **Do private page addresses include words from the title?** If a private page's address were something like `/q3-layoffs-plan`, the pasted link itself leaks the title in every chat, and nothing in this design can fix that. Private pages should use opaque IDs.
- Should screenshots be offered as preview images, perhaps as a per-page option?
- What should the visibility setting say about cards that chat apps have already cached? After a page goes private, Tessel can't recall those.
- Should authors be able to opt out of the hold on saves?