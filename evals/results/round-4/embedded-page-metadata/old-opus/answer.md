I wrote the design to `docs/metadata.md`. Nothing is committed, and there's no code in the repo yet, so this is a plan only and nothing has been built or tested.

**The root cause.** A page's address serves Tessel's own wrapper page, and the person's HTML runs in a frame inside it. Browser tabs and link previews only read the wrapper. Preview tools also don't run JavaScript. That one fact explains bugs 240, 247 and 233.

**What the design does:**
- **Where titles and icons come from (240, 247):** when a page is published, Tessel reads its HTML once, without running it, and saves the title, description, icon and preview image. The wrapper then sends these from the server, so tabs and preview cards are right without any JavaScript.
  - If the HTML doesn't set a value, there's a fallback chain: title falls back to the first heading, then the page's name, then "Untitled page".
  - Pages that change their title or icon while running are copied to the tab live.
  - Tabs read `{title} · Tessel`.
- **Preview images:** every public and unlisted page gets one automatically, in line with the brief's "nobody has to make a preview image."
  - If the HTML names its own image, Tessel stores a copy and uses that.
  - Otherwise Tessel generates a card with its logo and the page title.
  - I chose not to take screenshots of pages. That would mean running the page's code on Tessel's servers, which is exactly what causes bug 251.
- **Public vs unlisted:** they get the same full preview card, because anyone with the link can already open an unlisted page. The only difference is that unlisted pages are hidden from search engines and left out of the sitemap.
- **Private (233):** no response from the server ever contains anything from the page, even for a signed-in member.
  - The member's tab title and icon are filled in by the browser after sign-in. Preview tools never see them.
  - Signed-out visitors, non-members and missing pages all get the same "Tessel / Sign in" not-found page.
  - When a page is made private, Tessel's own caches are cleared and its old preview image stops loading.
  - Cards already cached by chat apps can't be pulled back, so the "make private" step will warn about that.
- **Viewing never writes (251):** loading a page never changes saved data. Saving through the page's data runtime only works after a real click or keypress on the page, and only once the page is visible on screen. Rejecting known bots and rate limiting sit behind that as a backstop.

**Calls I made for you to review** (each is listed at the end of the doc and can be reversed on its own):
- The ` · Tessel` suffix stays even when a page sets its own title, so a page can't pass itself off as another site. A page's own icon does replace Tessel's.
- Every page needs a click or keypress before it can save data, with no way to opt out yet. This would break a page that saves with no interaction, like a visit counter. That's the biggest open question.
- No screenshots, and no fields in Tessel for editing the title, description or image yet. The HTML is the only source.
- I assumed unlisted addresses can't be guessed, and that pages have a name in Tessel separate from their HTML.
- I couldn't confirm the actual cause of 233 because there's no code to inspect. The design closes all three likely ways it could have happened.
- The size and length limits are starting guesses, not measured values.