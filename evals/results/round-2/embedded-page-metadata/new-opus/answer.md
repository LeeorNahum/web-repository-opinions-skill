I've written the design to `docs/metadata.md`. I didn't commit it. The repo has no code yet (`apps/` and `packages/` are empty), so this is a design for the first build, not a fix to existing code.

**What's causing the bugs:** browsers and link-preview tools only ever see Tessel's wrapper page. They never see the person's HTML running inside it, and preview tools don't run JavaScript. That one fact accounts for all four bugs.

**The design:**
- **Tab titles and icons (#240):** the wrapper sets the tab title and icon itself, using what the page declares. Tessel reads the page's own `<title>` and icon when it's saved. The title falls back to the first heading, then "Untitled page"; the icon falls back to Tessel's. Tabs read like `Q3 roadmap – Tessel`. If a page changes its title or icon while running, the Tessel runtime passes that on to the tab.
- **Link previews and images (#247):** public and unlisted pages get a real card with title, description and image, built from what was stored when the page was saved, so pages built with JavaScript work too. The image is one the page declares, or a generated Tessel-branded card with the page's title. Nobody has to make one, which matches the brief. Unlisted pages get the same card as public ones but aren't indexed or listed in the sitemap.
- **Private pages (#233):** every private page sends the same blank Tessel page to everyone. That page has no title, description or preview, and it's the same response as for a deleted page or one that doesn't exist. Members still see the real title in their tab, but only after they've signed in. The card already cached in that team chat won't disappear on its own; someone has to remove or refresh it there.
- **Votes from nobody (#251):** showing a preview never runs the page's code. Preview images are made when the page is saved, in an isolated renderer that can't save data. The page only loads for a real, visible view, and saving data requires the visitor to have clicked or tapped first.

**Calls I made that you should check** (all listed at the end of the doc):
1. There's no settings screen for title, description or image yet; the page's own HTML is where authors set them.
2. Generated preview images are a branded card, not a screenshot of the page. Screenshots of interactive pages often catch them half-loaded and can show other people's poll answers.
3. **Pages that save data without any interaction will break.** For example, a "last opened" counter would stop working. That's the cost of fixing #251.
4. A private page, a deleted page and a missing page all return a "not found" status with a sign-in option. This hides whether a page exists, but a member who isn't signed in yet also sees "not found" at first.
5. Tessel adds its runtime to every page automatically, so authors don't have to include it.
6. I picked the en dash (–) as the title separator.

**Needs you:** the product domain and the separate domain that runs people's HTML aren't decided, so the doc uses placeholders for both. Registering that second domain is your call.