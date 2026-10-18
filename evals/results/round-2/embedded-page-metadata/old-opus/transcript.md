**Prompt:** Look at the open bugs in docs/issues.md and design how page icons, tab titles, and link previews should work for public, unlisted, and private Tessel pages, including preview images. Write it to docs/metadata.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-embedded-page-metadata-old-opus/work\" && git ls-files && cat docs/*.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5634 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-embedded-page-metadata-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat social-metadata.md seo.md public-discovery.md"}`

> Result: # Social Metadata  Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.  ## Favicon  Every surface ships a favicon. Set it deliberately rather than leaving the framewo [... 12867 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-embedded-page-metadata-old-opus/work/.claude/skills/web-repository-opinions/references\" && grep -il \"iframe\\|user-authored\\|untrusted\\|sandbox\\|crawler\\|prefetch\\|bot\" *.md; cat domains.md rendering.md | head -150"}`

> Result: ai-model-routing.md auth.md branches.md continuous-integration.md definition-of-done.md design-tokens.md interaction-feedback.md legal-pages.md object-storage.md product-ux.md provider-setup.md public-discovery.md quota.md rendering.md responsive-layout.md routing.md seo.md social-metadata.md # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex. [... 5642 more characters]

**Tool call `Write`:** `<run>\builds\2-embedded-page-metadata-old-opus\work\docs\metadata.md`

````text
# Page metadata: tab titles, icons, and link previews

This design covers how a Tessel page gets its browser tab title, its tab icon, and the preview card that appears when its link is pasted somewhere. It covers public, unlisted, and private pages. It fixes bugs 233, 240, 247, and 251 in `docs/issues.md`.

The repo has no app code yet (`apps/` and `packages/` are empty), so this is a design to build against, not a patch.

## Assumptions

The owner was away when this was written. Each of these is a call I made, and each can be reversed.

1. **The person's HTML runs in a sandboxed iframe on a separate content origin.** Tessel's wrapper page owns the address and the toolbar. The page's HTML loads in an iframe served from a different origin, so it can't read Tessel cookies or script the wrapper. This also explains bug 240: a `<title>` or `<link rel="icon">` inside an iframe never reaches the browser tab. If pages don't run this way today, they should, and the rest of this design still holds.
2. **One separator, chosen once:** tab and card titles read `{page title} · Tessel`.
3. **No screenshots in v1.** When a page has no preview image of its own, Tessel generates a template card instead of running the page headlessly and capturing it. Running untrusted JavaScript in a renderer is slow and nondeterministic, it can capture live data, and it's the same class of load that caused bug 251. Screenshots are listed as a possible later option below.
4. **An unlisted page gets a full, real preview card.** "Anyone with the link can open it" means a chat app holding the link can open it too. Hiding the card would protect nothing and would make sharing worse. Unlisted pages stay `noindex`.
5. **A private page's title may appear in the tab of a signed-in member.** That member is already looking at the page. The title still never appears in server-rendered HTML, a preview card, or a preview image (see "Private pages").
6. **The page's own HTML is the only input.** This follows from the decision that publishing takes one HTML file with no manifest and no preview image. Everything below is read from standard tags the page may already have and falls back cleanly when they're missing. If Tessel later adds an owner-editable title field, it takes precedence over values read from the HTML (owner edits beat extracted values, and extracted values beat defaults).

## Page metadata record

Each time a page is published, Tessel parses the HTML on the server without running it and stores a metadata record next to the page version:

| Field | Source, in priority order | Fallback |
| --- | --- | --- |
| `title` | owner-set title (if that field ever exists), `<title>`, `og:title`, first `<h1>` text | the page's address slug, made readable |
| `description` | `<meta name="description">`, `og:description`, text of the first non-empty `<p>` in the static HTML | `{title}: an interactive page by {author} on Tessel.` |
| `icon` | the best `<link rel="icon">` (prefer SVG, then the largest PNG), then `apple-touch-icon` | none, so Tessel's own icon is used |
| `image` | `og:image`, then `twitter:image` | a generated card (see "Preview images") |
| `robots` | `<meta name="robots">`, honored only when it is stricter than the visibility default | the visibility default |

Rules:

- Trim whitespace and cap lengths: title at 120 characters, description at 300.
- **Icons are copied into Tessel storage at publish time**, whether they come from a `data:` URL, a file in the page bundle, or an absolute `https:` URL. The copy is sanitized: SVGs are re-serialized with no script or external references, and the size is capped at 256 KB. Tessel then serves the icon itself, which keeps it stable and stops viewers' browsers from contacting third-party hosts.
- An author's `og:image` is resolved to an absolute `https:` URL. If it points to a file in the bundle, it is served from Tessel storage.
- Extraction runs on the static HTML only. A page that builds all its content with JavaScript, as in bug 247, still gets a title and description from the fallbacks.
- The record is versioned with the page. A preview image URL includes a hash of the inputs it was generated from, so editing the title produces a new URL, and preview tools that cache by URL pick up the change.

## What each visibility serves

The wrapper renders on the server. It loads the page and its metadata record in a single lookup, which also decides visibility, and it writes the tags into the initial HTML. Preview tools read only that HTML and run no script.

| | Public | Unlisted | Private |
| --- | --- | --- | --- |
| Server-rendered `<title>` | `{title} · Tessel` | `{title} · Tessel` | `Tessel` |
| Server-rendered icon | page icon, or Tessel's | page icon, or Tessel's | Tessel's |
| `description`, `og:*`, `twitter:*` | page values | page values | generic Tessel values only |
| `og:image` | page image or generated card | page image or generated card | generic Tessel brand card |
| `twitter:card` | `summary_large_image` | `summary_large_image` | `summary` |
| `robots` | `index` (unless the page asks for stricter) | `noindex` | `noindex, nofollow` |
| In sitemap | yes | no | no |
| `Cache-Control` on the wrapper HTML | public, short TTL, purged on change | public, short TTL, purged on change | `private, no-store` |
| Tab after load (signed-in member) | live page title and icon | live page title and icon | page title and icon, after access is confirmed |

Every page also gets `og:url` (the canonical address), `og:site_name` = `Tessel`, `og:type` = `website`, and a base URL in the root layout so relative tags resolve to absolute ones. When a route overrides part of the metadata, check that the image, site name, and card type survive. A nested override commonly replaces the parent's whole metadata object instead of merging into it.

## Tab titles and icons (bug 240)

1. **First paint.** The server renders the tab title and icon from the metadata record, using the table above. A public or unlisted page shows its own title and icon before the iframe has even loaded.
2. **Live updates.** The Tessel runtime inside the page watches `document.title` and the icon `<link>` elements. When they change, it posts a message to the wrapper. The wrapper accepts the message only when it comes from its own iframe's window and from the content origin.
   - It applies the title as `{new title} · Tessel`, trimmed to 120 characters. The suffix is always present, so a page can't make its tab look like another site.
   - It applies an icon only if the icon is a `data:` image under the size cap or a file in the page's own bundle. Remote icon URLs are ignored.
   - If the page stops sending updates, the tab keeps the last value. It never falls back to `Tessel`.
3. **Navigation.** When the wrapper switches pages without a full reload, it resets the tab to the new page's server values right away, so the previous page's title never lingers. Because the wrapper's router may re-render `<head>`, the wrapper re-applies the live title and icon after any head change. Verify this after a client-side navigation, not only after a reload.

## Private pages (bug 233)

The private-page leak is closed at the server:

- **The server-rendered wrapper for a private page never contains the page's title, description, icon, or image.** This holds even when the request carries a valid member session. Some preview tools fetch on the sender's device, and a cached or forwarded copy of the HTML can travel. The rule is simple to test: for a private page, a fetch with no cookies and a fetch as a member return identical `<head>` content.
- After the wrapper checks access, it fetches the title, and the icon as a small `data:` URL, from the authorized API that also gates the iframe. Only then does it set the tab. Non-members, and anyone who is signed out, see the sign-in screen with the generic `Tessel` head.
- The generic card is the product's own brand card: Tessel's mark, the name "Tessel", and nothing about the page. A private page never gets a page-specific description or image, so no first paragraph can show up in a card.
- **The preview image URL enforces visibility too.** `/{page address}/preview-image/{hash}` returns the generated card only while the page is public or unlisted. Otherwise it returns the generic brand card with `Cache-Control: no-store`. Guessing or reusing an old image URL reveals nothing.
- **Visibility changes and deletion.** When a page becomes private or is deleted, Tessel purges the CDN entries for the wrapper HTML and the preview image. From then on the address serves the content-free fallback. A link that outlives its share can't keep naming what it pointed to.
- **Limit worth knowing:** cards that chat apps already built are cached on their side, and Tessel can't recall them. The card in the bug 233 report will probably stay in that chat until someone deletes the message there, or the app's cache expires, or someone uses the app's refresh option if it has one.

## Link previews and preview images (bug 247)

Bug 247 comes from preview tools reading only the initial HTML. The wrapper didn't put the page's metadata there, and the page's own content appears only after JavaScript runs. With server-rendered tags from the metadata record, every public and unlisted page gets a real card, including pages built entirely with JavaScript.

**Preview image:**

- If the page declares `og:image`, that image is used for public and unlisted pages.
- Otherwise, Tessel generates a 1200×630 PNG card in Tessel's colors and type. It shows the Tessel mark, the name "Tessel", the page title (the same subject as the tab), and the author's display name. If the page has its own icon, the card shows it beside the title.
- Cards are generated in a background job after publish, and again when the title, author name, or icon changes. They are stored in object storage, keyed by page and input hash, and served from a URL that includes the hash. If the image isn't ready yet, the endpoint renders the card on demand once and stores it, so the first paste after publishing still shows an image.
- A private page uses only the generic brand card.

**Description:** the extracted description, or the `{title}: an interactive page by {author} on Tessel.` fallback. Including the title and author means that, in practice, no two pages share a description.

**Later option (not in v1):** page screenshots as the default preview image. Before adopting them, check that the "page loads never write" rules below hold inside the screenshot renderer, that the renderer is isolated from Tessel credentials, and that the cost per publish is acceptable.

## Page loads never write data (bug 251)

Something that loads the page, such as a link scanner, a headless preview tool, a search crawler that runs JavaScript (public pages are indexed), or browser prefetch, ran the poll's script, and the script saved a vote. Loading a page must never change its data. The rule is enforced in the Tessel runtime, not left to each page author:

1. **Runtime writes require a real person's interaction.** The wrapper relays write calls from the page's runtime, and it refuses them until the page has had a user activation: a click, a tap, or a key press. Activation inside the iframe also counts for the wrapper. Reads are always allowed. A refused write fails with a clear runtime error that the page can handle. It does not fail silently. A poll that votes on a click is unaffected. A page that writes on load stops doing so.
2. **The server refuses writes without a live viewer session.** The wrapper gets a short-lived write token for the current page view. The write endpoint rejects requests that have no valid token. It also rejects requests from known preview and crawler user agents, and requests marked as prefetch or prerender (`Sec-Purpose: prefetch`). The user-activation check in step 1 is the primary defense. This step is defense in depth.
3. **Prerendering waits.** While `document.prerendering` is true, the wrapper doesn't mount the iframe. It mounts the iframe on activation instead.
4. **Fetches stay side-effect free.** Fetching the wrapper, the page HTML, or the preview image only reads.

Deduplicating votes per person stays the page author's job. This rule only guarantees that a vote comes from someone who actually interacted with the page.

## Verification

Treat each of these as a check before calling the work done:

- **Public page built only with JavaScript:** a plain HTTP fetch with no JavaScript returns the page title, description, `og:image`, and `twitter:card` in `<head>`. Paste a real link into a real chat app while signed out, and use the tool's refresh when re-checking.
- **Unlisted page:** shows the same full card, plus `noindex`, and is absent from the sitemap.
- **Private page:** with no cookies, the `<head>` holds only generic Tessel values, and it matches the `<head>` a member gets byte for byte. The preview image URL returns the generic card. A real chat paste shows only "Tessel".
- **Making a page private:** a fresh fetch of the old wrapper and its preview image shows only generic content.
- **Tab title and icon:** after a reload and after a client-side navigation, the tab shows the page's title and icon. It never shows a previous page's title. A live `document.title` change shows up in the tab with the `· Tessel` suffix.
- **Poll page:** loading it in a headless browser, through a link-preview tool, and via prefetch adds no votes. One click adds one vote.

## Open questions for the owner

- The `·` separator, and whether "Tessel" in titles should be the product name or the author's name.
- Whether unlisted pages should have an owner option to hide card content, for example "unlisted, quiet preview". The default above is a full card.
- Whether an owner-editable page title should exist alongside the HTML `<title>`.
- Whether to tell the bug 233 reporter that the card already in their chat has to be removed on the chat app's side.

````

> Result: File created successfully at: <run>\builds\2-embedded-page-metadata-old-opus\work\docs\metadata.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/metadata.md`. The repo has no app code yet, so it's a plan to build against, not a fix, and nothing has been tested. I haven't committed it.

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

**Session ended:** success, 7 turns, 139810 ms
