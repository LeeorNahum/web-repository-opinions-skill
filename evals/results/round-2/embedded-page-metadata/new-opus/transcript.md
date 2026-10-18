**Prompt:** Look at the open bugs in docs/issues.md and design how page icons, tab titles, and link previews should work for public, unlisted, and private Tessel pages, including preview images. Write it to docs/metadata.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-embedded-page-metadata-new-opus/work && git ls-files | head -100 && cat docs/brief.md docs/issues.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5634 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-embedded-page-metadata-new-opus/work/.claude/skills/web-repository-opinions/references && cat social-metadata.md domains.md public-discovery.md seo.md"}`

> Result: # Social Metadata  Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.  ## Favicon  Every surface ships a favicon. Set it deliberately rather than leaving the framewo [... 19349 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-embedded-page-metadata-new-opus/work/.claude/skills/web-repository-opinions/references && cat data-model.md object-storage.md background-jobs.md ids.md rendering.md abuse-resistance.md | head -400"}`

> Result: # Data Model  Model entities around the product's core object and the ownership boundary that protects them.  When many users can reference the same object, model the shared object separately from each user's relationship and relationship-owned metadata. Define object deletion independently from relationship deletion.  Value precedence is fixed: user-edited values outrank generated values, a [... 15326 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-embedded-page-metadata-new-opus/work/.claude/skills/web-repository-opinions/references && cat routing.md search-indexing.md live-data.md | head -200; cat ../../../../package.json ../../../../pnpm-workspace.yaml"}`

> Result: # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix [... 9560 more characters]

**Tool call `Write`:** `<run>\builds\2-embedded-page-metadata-new-opus\work\docs\metadata.md`

````text
# Page metadata: icons, tab titles, and link previews

This doc covers how a Tessel page gets its browser tab title, its tab icon, and the preview card that shows up when someone pastes its link, for public, unlisted, and private pages. It answers open bugs 233, 240, 247, and 251 in `docs/issues.md`. The calls I made without the owner are listed under [Assumptions](#assumptions) and [Open questions](#open-questions).

The repo has no implementation yet (`apps/` and `packages/` are empty), so this is a design for the first build. It does not patch existing code.

## Constraints from the brief

- Tessel serves its own wrapper page at the page's address, and the person's HTML runs inside it in a frame.
- A simple page is one HTML file. Nobody has to write a manifest or make a preview image. So every piece of metadata must be derived automatically, and anything the page declares is an optional upgrade.
- Visibility is public (indexed), unlisted (anyone with the link, not indexed), or private (invited members, signed in).

## Why the bugs happen

All four bugs have one cause. The browser and every link-expanding tool only ever see the **wrapper**, which is Tessel's document. They never see the framed page.

- **240 (every tab shows the Tessel icon):** the tab shows the outer document's `<title>` and icon. The page's own `<title>` and `<link rel="icon">` sit inside a cross-origin frame, so the browser ignores them.
- **247 (blank previews):** link-expanding tools read the initial HTML of the URL and run no script. They get the wrapper, and if the wrapper doesn't carry the page's tags, the card is empty. A page that builds its content with JavaScript has nothing a tool could read even if the tool fetched the page's HTML directly.
- **233 (private title leaked):** something answered an unauthenticated request for a private page with tags built from its content. Tools fetch signed out, so any content in a response to an unauthorized request is a leak.
- **251 (votes from nobody):** something that isn't a person loaded the page and ran its code: a link scanner, a prefetch or prerender, a headless preview renderer, or a Tessel render step that ran at paste time. The runtime accepted a write from it.

The fix: **the wrapper owns the tab title, the icon, and the preview tags.** Tessel works them out on the server, when the page is saved, from the page's own head plus an isolated render. It serves them only to requests that are allowed to know them. Page code never runs because someone asked for a preview.

## Visibility matrix

| | Public | Unlisted | Private (member) | Private, unauthorized, deleted, or not found |
| --- | --- | --- | --- | --- |
| Tab title | `{subject} – Tessel`, server-rendered | `{subject} – Tessel`, server-rendered | `{subject} – Tessel`, set by the client after auth | `Tessel` |
| Tab icon | Page's icon, or the Tessel icon | Page's icon, or the Tessel icon | Page's icon after auth, the Tessel icon before | Tessel icon |
| `og:title` / `twitter:title` | Same as tab title | Same as tab title | — (the shell has no page tags) | `Tessel` |
| Description | Page-specific | Page-specific | — | Generic Tessel line |
| Preview image | Declared or generated card | Declared or generated card | — | Tessel brand image |
| Robots | `index`, canonical, in sitemap | `noindex` (meta and `X-Robots-Tag`), not in sitemap | `noindex` | `noindex` |
| Initial HTML differs per page | Yes | Yes | **No** | No |

Unlisted pages get their real card. "Not indexed" is a search engine directive, and link-expanding tools ignore it. Anyone with an unlisted link can open the page anyway, so the card reveals nothing extra.

## Private pages (bug 233)

- **The initial HTML of a private page is one static, content-free shell, the same for everyone, members included.** It has the title `Tessel`, the Tessel icon, a generic description and brand image, and `noindex`. Tessel does not server-render private metadata even when the request carries a member session, because some unfurlers and in-app previewers send cookies. The safe rule is that no response the server writes for a private page contains its content.
- After the shell loads, the authenticated client fetches the page through the authorized API. Only then does it set `document.title` to `{subject} – Tessel` and swap in the page's icon. A member's tab still shows the page name, since they're already looking at it, but no preview can.
- A private page, a deleted page, and an ID that never existed all return the same response: the same shell, the same status (404), and a sign-in action. A link that outlives its access can't reveal what it pointed at, and the response doesn't reveal whether the page exists.
- Tessel never generates a preview image for a private page. The preview image URL of a page that became private returns 404 (see [Visibility changes](#visibility-changes)).
- The private page's framed content on the content domain is served only with a short-lived frame token that the authorized client gets from the API. Without the token, the content domain returns nothing.

Note for the bug 233 reporter: the chat app has already cached the leaked card by URL. This design stops new leaks, but the existing card has to be removed or refreshed in that chat app.

## Where metadata comes from

Each page revision has one stored metadata record, owned by the page record in the database and keyed to the content revision. Fields follow the fixed precedence (authored, then generated, then default). All three layers are stored, and none overwrites another.

### Subject (tab title and card title)

1. `<title>` as the page left it: the static `<title>`, or the rendered `document.title` once the render step finishes.
2. `og:title`, if the page declared one and has no `<title>`.
3. The page's first `<h1>`, static or rendered.
4. `Untitled page`.

Tessel trims whitespace, removes control characters, and stores the subject capped at 120 characters. The tab title and the card title are both `{subject} – Tessel`, with the en dash as the site-wide separator. A page whose subject already ends in "Tessel" is left alone rather than doubled.

### Description

1. `<meta name="description">`, then `og:description`.
2. The first meaningful paragraph of rendered text, cut to about 200 characters on a word boundary.
3. `{subject}: an interactive page on Tessel.`

### Icon (bug 240)

1. The page's `<link rel="icon">` (or `apple-touch-icon`), whether it's an inline `data:` URL, a file next to the page, or an external URL.
2. The Tessel icon.

Declared icons are fetched once at save time with the safe fetcher (see [Isolation](#isolation)). The renderer **rasterizes** them to PNG at 32, 48, and 180 px, and Tessel serves those PNGs from its own origin at the page address (for example `{page address}/icon-32.png?v={revision}`). Tessel's origin never serves bytes from a user-supplied SVG or image directly. A user SVG served from the product origin is script on the product origin.

The icon endpoints use the same authorization as the page. Public and unlisted icons can be fetched by anyone. A private page's icon is fetched by the authorized client, and every other request gets the Tessel icon.

### Live title and icon changes

Some pages change `document.title` or their icon while they run (unread counts, timers). The Tessel runtime, which Tessel injects into every served page, watches the frame's `<title>` and icon links and posts changes to the wrapper. The wrapper:

- accepts the message only if `event.source` is its own frame and `event.origin` is that page's content origin;
- caps the title at 120 characters and strips control characters;
- accepts icons only as `data:image/png|gif|jpeg|x-icon|svg+xml` up to 64 KB (a tab icon is drawn as an image, so an SVG there runs no script);
- uses these updates **for the tab only**. They never feed stored metadata, the preview card, or search.

The wrapper also reasserts its title after its own client-side navigations, so a framework head update can't overwrite it.

### Preview image (bug 247)

1. The page's declared `og:image` / `twitter:image`. Tessel fetches it once at save time with the safe fetcher, checks that it's an image, re-encodes it to PNG or JPEG at no more than 1200 px wide, and rehosts it. Tools never hot-link the author's URL.
2. A **generated card** at 1200×630. It shows the Tessel mark, "Tessel", and the page's subject (the same string as the title) in Tessel's colors and type, plus the page's own icon if it has one. A generated card's text comes from the subject only, so it can't show anything the title doesn't already show.

The preview image URL is `{page address}/preview.png?v={revision}`. Tessel serves it from storage through the CDN, with long caching per version. The site-wide Tessel brand image appears only on the homepage and in the content-free fallback.

### Tags the wrapper writes (public and unlisted)

The server renders these into the initial HTML of every public or unlisted wrapper, in the same lookup that resolves the page:

- `<title>`, `<meta name="description">`, `<link rel="icon">` (PNG sizes) and `apple-touch-icon`
- `og:title`, `og:description`, `og:image` (absolute URL, with width and height), `og:url` (canonical page address), `og:type=website`, `og:site_name=Tessel`
- `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`
- `<link rel="canonical">` pointing at the Tessel page address (never the content domain)
- robots per the matrix

The server-rendered toolbar also shows the page's subject as text, so a client without JavaScript sees the page's name as well as its tags.

## The pipeline

Metadata is worked out **at save time, never at request time.** Serving a wrapper or a preview reads stored fields and never runs page code.

1. **Static parse (synchronous on save).** Tessel parses the saved HTML's head and body without running it, and pulls out the declared title, description, `og:*`, the icon link, and the first `<h1>` and paragraph. Metadata is ready right away, before any rendering.
2. **Render job (background, public and unlisted only).** An isolated headless browser loads the page in snapshot mode, waits for the network to go quiet or 5 s (whichever comes first), and reads the final `document.title`, the first `<h1>`, and the first paragraph. It also rasterizes the icon, re-encodes any declared image, and draws the generated card. The job carries the content revision as a generation token, and drops its results if a newer revision has superseded it. Saves are debounced so a burst of agent saves renders once, at the latest revision.
3. **Results.** The job writes the rendered fields and stored-image keys onto the metadata record. Image bytes go to object storage under opaque keys, registered in the write-ahead ledger before upload. Then the job purges the page's wrapper and image from the CDN.

If the render fails or times out, the static-parse values and the generic fallbacks stand. The owner's status shows a simple "preview ready / preview unavailable", not renderer internals.

## Isolation

- **Content domain.** Page HTML runs on its own registrable domain, with one subdomain per page, never on a subdomain of Tessel's domain. That domain sends `X-Robots-Tag: noindex, indexifembedded` for public pages, so search engines index the content as part of the Tessel address, and `noindex` for all other pages.
- **Renderer.** It holds no session, cookie, or credential. It can't write Tessel data: it returns results to the job over a narrow channel, and the job does the writing. It reaches the public internet only through an egress proxy that blocks loopback, private, link-local, and metadata addresses after resolving each host. It has caps on wall-clock time, memory, and bytes.
- **Safe fetcher** for declared icons and images: byte cap, timeout, a bounded number of redirects with every hop rechecked, the same address blocking, and checking of the bytes actually received rather than the type it was told.

## Phantom writes (bug 251)

Several layers, each closing a different path:

1. **Previews never run page code.** Tags and images come from storage, so link-expanding tools that fetch only HTML never reach the runtime.
2. **The renderer's runtime is read-only.** In snapshot mode, reads return live data (so a poll can render its current results) and writes are thrown away while appearing to succeed to the page. Rendering happens on save, not on paste.
3. **The frame loads only for a real, visible view.** The wrapper doesn't mount the page frame while the document is prerendering (it waits for `prerenderingchange`), and it ignores `Sec-Purpose: prefetch` requests. Content-domain frame URLs need a short-lived frame token that the wrapper's script gets, so a client that runs no script never loads the page.
4. **Writes need a person.** The runtime sends a write only after the frame has had user activation (`navigator.userActivation.hasBeenActive`). Before that, a write is rejected with a runtime error the page can see (`needs-interaction`). The server also requires the view's write token, which is minted per page view. Link scanners that run headless browsers load the page but don't click, so they can't vote.

Deliberate vote stuffing by a real script is abuse, not this bug. Rate limits at the edge and per-view write tokens handle it separately.

## Visibility changes

- **Becomes private, or is deleted:** the wrapper drops to the content-free shell, the preview image and icon URLs return 404 or the fallback, and Tessel purges the page's CDN entries right away. The page leaves the sitemap. Cards that tools already cached can't be recalled. The sharing UI should say so when a page goes from public or unlisted to private.
- **Private to unlisted or public:** Tessel queues a render job and serves the real tags as soon as the static parse results exist.
- **Public to unlisted:** the real card stays. The page gets `noindex` and leaves the sitemap.
- **Sitemap:** public pages only. `lastmod` is the time of the page's last content revision, which is the record's own modified time, not the deploy time.

## Verification

A change here is done only when it holds in real tools, not when the tags look right:

- `curl` each visibility, signed out, with a plain user agent and with unfurler user agents. Private, deleted, and nonexistent pages must return the same bytes. Public and unlisted pages must contain the page's title, description, and absolute image URL.
- Paste real links, signed out, into Slack, Discord, iMessage, X, LinkedIn, and WhatsApp. Re-check after changes using each tool's refresh, because tools cache by URL.
- For a page that builds its content with JavaScript, the card must show its rendered title.
- Paste a poll page's link into each tool and into an email client that scans links. The vote count must not move.
- Open a page with its own icon and title: the tab shows them on load and after a client-side navigation. A page that changes `document.title` updates the tab.
- A signed-in member's private tab shows the page name. The same URL with no session shows `Tessel`.

## Assumptions

Calls I made without the owner. Each one can be reversed without redesign.

1. **No metadata override UI in v1.** The page's own `<head>` is where authors (and their agents) set title, description, icon, and image. A Tessel-side override field would rank above the head if it's added later.
2. **Generated cards are a branded template (mark, "Tessel", subject, page icon), not a screenshot of the page.** Screenshots of interactive pages often catch loading states and can show live data, such as other people's poll answers.
3. **Members' private tabs show the page title**, but only through the client after auth. The server never renders it.
4. **Unauthorized private, deleted, and nonexistent pages all return 404 with a sign-in action.** This hides whether a page exists, at the cost of a 404 status for a member who isn't signed in yet.
5. **Runtime writes need prior user activation.** This breaks pages that write on load without interaction (for example "last opened" counters). I judged that acceptable against bug 251. If the owner disagrees, the fallback is to keep the gate only for writes from views the server marks as likely automated.
6. **The en dash `–` is the one title separator.** The fallback subject is `Untitled page`.
7. **Tessel injects its runtime into every served page**, so live title and icon relay needs no author work.
8. **The render job waits up to 5 s** for network quiet. Only public and unlisted pages are rendered.
9. **Placeholder hosts.** The Tessel product domain, the separate content domain, and the page URL shape (`{page address}`) are not decided in the brief. This design assumes only that page content runs on a separate registrable domain.

## Open questions

- **Domains (needs the owner):** registering the content domain, and later submitting it to the private section of the Public Suffix List. Production domain choices are the owner's call.
- Should owners see a preview of their card in the sharing UI? It's cheap given the pipeline, and it catches bad declared images.
- Should public pages also offer oEmbed? It's out of scope here.
- Unlisted page addresses can leak through the `Referer` header on outbound links from the framed content. That belongs in the sharing design, not this one.

````

> Result: File created successfully at: <run>\builds\2-embedded-page-metadata-new-opus\work\docs\metadata.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/metadata.md`. I didn't commit it. The repo has no code yet (`apps/` and `packages/` are empty), so this is a design for the first build, not a fix to existing code.

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

**Session ended:** success, 8 turns, 191561 ms
