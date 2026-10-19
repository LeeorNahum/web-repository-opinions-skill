**Prompt:** Look at the open bugs in docs/issues.md and design how page icons, tab titles, and link previews should work for public, unlisted, and private Tessel pages, including preview images. Write it to docs/metadata.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "git ls-files && cat docs/brief.md docs/issues.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5634 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references && cat social-metadata.md domains.md public-discovery.md seo.md"}`

> Result: # Social Metadata  Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.  ## Favicon  Every surface ships a favicon. Set it deliberately rather than leaving the framewo [... 20126 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references 2>/dev/null || true; cat ids.md routing.md rendering.md object-storage.md data-model.md background-jobs.md abuse-resistance.md | head -c 60000"}`

> Result: # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.  ## Entity IDs  For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.  - Length: a fixed 12 characters. - Alphabet: Base58, the case-sensi [... 22145 more characters]

**Tool call `Write`:** `<run>\builds\4-embedded-page-metadata-new-opus2\work\docs\metadata.md`

````text
# Page metadata: icons, tab titles, and link previews

Status: proposed. Written while the owner was away; every call made without them is listed under [Assumptions](#assumptions-to-confirm).

This covers how a Tessel page gets its browser tab title, its tab icon, and the preview card that shows up when its link is pasted into a chat or social app. It covers public, unlisted, and private pages, and it fixes bugs 233, 240, 247, and 251 in `docs/issues.md`.

## Why the bugs happen

Tessel serves its own wrapper page at a page's address, and the person's HTML runs in a frame inside it. Two facts follow from that:

- **The browser only uses the outer document.** The tab title and icon come from Tessel's wrapper, never from the framed HTML. That is why every tab shows "Tessel" and the Tessel icon (240).
- **Link-preview tools only read the wrapper's initial HTML, and they usually run no script.** They never see the framed page, and they never see anything that JavaScript builds. That is why the cards are blank (247). Some tools and link scanners do run a full browser, though, and that browser runs the page's code, which casts the poll vote (251).

Bug 233 is a separate failure. The wrapper put a private page's own metadata into a response that was not checked for authorization, and preview tools fetch without the viewer's session.

So Tessel's wrapper has to own all of this metadata. It works it out on the server from the page's HTML, decides per visibility and per request what it may reveal, and never runs page code to get it.

## Principles

1. **The wrapper owns the tab title, the icon, and the card.** They come from the page's own HTML, worked out on the server, so publishing still needs nothing beyond one HTML file (brief: "Decided").
2. **Metadata is extracted when the page is saved, not when it is requested.** It comes from the static HTML only. Tessel never runs a page's code to extract metadata or make a preview image.
3. **The server only puts page-specific metadata into a response it has already authorized.** Private pages never put page-specific metadata into server HTML at all, not even for members.
4. **Loading a page never writes data.** Runtime writes need a real user interaction, and Tessel's wrapper enforces that rule, not the page's code.

## Visibility matrix

| | Public | Unlisted | Private: signed-out, non-member, or preview tool | Private: authorized member |
| --- | --- | --- | --- | --- |
| Tab title (server HTML) | `{title} · Tessel` | `{title} · Tessel` | `Tessel` | `Tessel` |
| Tab title (after load) | live title from the page | live title from the page | `Tessel` | `{title} · Tessel`, then the live title |
| Tab icon | the page's icon, else Tessel's | the page's icon, else Tessel's | Tessel's | Tessel's in HTML, then the page's icon set by the client |
| `description`, Open Graph and card tags | full | full | none except the fallback below | none except the fallback below |
| Preview image | declared image or generated card | declared image or generated card | none | none |
| Indexing | indexable, canonical, in sitemap | `noindex` (meta and `X-Robots-Tag`), not in sitemap | `noindex` | `noindex` |
| Cache | shared cache, purged when the metadata version changes | same as public | `Cache-Control: private, no-store` | `private, no-store` |

Unlisted pages get a full card. Anyone holding the link can already open the page, and preview tools ignore `noindex`. A card would show them nothing they couldn't already see.

### The content-free fallback

This is what goes out for every response that isn't authorized to see a page: private pages, missing pages, deleted pages, and pages that used to be public or unlisted.

```html
<title>Tessel</title>
<meta property="og:site_name" content="Tessel">
<meta property="og:title" content="Tessel">
<meta name="twitter:card" content="summary">
<meta name="robots" content="noindex">
<link rel="icon" href="(Tessel icon)">
```

- It has no description, no image, no owner name, and no page address in the text.
- A private page, a missing page, and a deleted page all return the same fallback, so nobody can probe which addresses exist.

## Where the metadata comes from

Extraction runs when a page is published or saved. It parses the static HTML, runs no script, and stores the results on the page record as a new **metadata version**. For each field, the first source in the list that has a value wins:

| Field | Sources, highest precedence first |
| --- | --- |
| Title | 1. Override set in Tessel's page settings (optional, never required) 2. `og:title` 3. `<title>` 4. first `<h1>` in the static body 5. the page's name in Tessel (from its address) |
| Description | 1. Settings override 2. `og:description` 3. `<meta name="description">` 4. first non-empty `<p>` in the static body 5. `"{title}, an interactive page by {owner display name} on Tessel"` |
| Icon | 1. Settings override 2. `<link rel="icon">` or `<link rel="shortcut icon">`, preferring SVG 3. `<link rel="apple-touch-icon">` 4. none, so Tessel's icon is used |
| Preview image | 1. Settings override 2. `og:image` or `twitter:image` 3. a generated card |

This follows the repo-wide precedence rule: values the user edited beat values the page declares, and those beat derived values and defaults. All three layers are stored separately, so a later save can't wipe out an override.

### Sanitization

The values are text the user controls, and they get rendered into Tessel's own origin.

- Strip tags and control characters, and collapse whitespace.
- Cap the title at 200 characters and the description at 300.
- Always render them through the framework's escaping. Never write them into the wrapper as raw HTML.

### Asset re-hosting

Declared icons and images are never hotlinked.

- **Fetching:** at save time, Tessel copies `data:` URLs and absolute `https:` URLs into its own object storage. Fetches use the shared safe fetcher, which has a byte cap, a timeout, and bounded redirects, and refuses private, loopback, link-local, and metadata addresses.
- **Validation:** Tessel checks the actual bytes, not the type the server claimed.
- **Re-encoding:** icons become a PNG set and keep their SVG if it sanitizes. Images are resized or cropped to 1200×630.
- **Why re-host:** preview tools and viewers then never contact a third-party host, which can't track them or swap the image after publishing.
- **When the fetch fails:** the page falls back to the next source in the list, and the publish result tells the author.

### JavaScript-built pages (247)

A page that builds everything with script may have no static title or text. It still gets a usable card, because the fallback chain ends in the page's name and a description built from the owner's name.

To get a better card, the publish response says which fields were missing, for example "This page has no `<title>`; previews will show 'poll-demo'." The guidance Tessel gives authors and their AI agents also says to put a static `<title>`, `<meta name="description">`, and optionally `og:image` and an icon link in the `<head>`. None of these are required.

## Tab title and icon in the wrapper (240)

### Server-rendered head

- Public and unlisted pages render `<title>{title} · Tessel</title>` and the re-hosted icon links from the current metadata version.
- Private pages render the fallback head.

The separator is ` · ` with the page's subject first. Tabs get cut off from the right, so the page's name has to come first. The same string is used for `og:title`, so the card and the tab always agree.

### Live updates from the page

The Tessel runtime is already in the framed page. It watches `document.title` and the page's icon `<link>` elements and posts any change to the wrapper, which checks the sender before accepting a message.

- **Title:** the wrapper sanitizes and caps the text, then sets `document.title` to `{live title} · Tessel`.
- **Icon:** the wrapper only accepts `data:` image URLs and URLs on the page's own content-domain origin. Anything else is ignored, so a page can't use its icon to load a tracking URL.
- **Scope:** live values only change the tab. They never reach stored metadata or cards.

### Private pages

The server sends the fallback head even to members. Once the wrapper's authorized session confirms access, the client sets the title to `{title} · Tessel` and the icon to a blob URL fetched through the authorized API. After that, live updates work as described above.

A preview tool that carries the member's cookies but runs no script therefore still only sees "Tessel". Showing the page's name in the tab is fine, because the member is already looking at it. Descriptions and cards travel further than a tab, so they never carry private content.

## Link preview cards (247, 233)

### Tags for public and unlisted pages

- `og:title` and `twitter:title` are both `{title} · Tessel`.
- `og:description`, `twitter:description`, and `<meta name="description">` carry the page's description.
- `og:image` and `twitter:image` are absolute URLs to the Tessel-hosted 1200×630 image, with `og:image:width`, `og:image:height`, and `og:image:alt` set to the title.
- `og:url` is the page's canonical Tessel address. Public pages also get `<link rel="canonical">`.
- `og:site_name` is `Tessel`, `og:type` is `website`, and `twitter:card` is `summary_large_image`.
- The tags are rendered on the server from the same lookup that resolves the page and its visibility, so authorization and metadata can't fall out of step.
- The metadata layout is defined once and fills in every field. Route-level overrides must not drop the image, the site name, or the card type.

### The generated preview image

When a page declares no image, Tessel makes one.

- **Contents:** the Tessel mark, "Tessel", and the page title, in Tessel's colors and type, at 1200×630.
- **Rendering:** a template rendered by a background job when a new metadata version is saved, then stored in object storage. It is drawn from data and never screenshots the page, so no page code runs.
- **When:** only public and unlisted pages get one. Private pages never get a preview image.

### Serving images

Images are served from a Tessel-owned route keyed by page ID and metadata version, not from a public bucket URL.

- Each request checks the page's current visibility. A private or deleted page gets a 404, with no Tessel brand image as a stand-in.
- Responses can be cached, because a new version means a new URL. When visibility changes, the CDN is purged for that page.

### Turning a page private or deleting it

- Every Tessel surface drops to the fallback immediately: the wrapper, the card tags, and the image route.
- Cards that chat apps already cached can't be recalled, because the apps cache by URL. The "make private" and delete flows say so in one line, so authors know that previews already posted may still show the old title.

### The content domain

The frame's own URL on the user-content domain can also be pasted into a chat.

- Content-domain responses send `X-Robots-Tag: noindex` and a `Link: <tessel address>; rel="canonical"` header.
- Private HTML is served there only against a short-lived signed token that the wrapper mints after authorization. Without a valid token, the content domain returns a content-free response.

## Loading a page never writes (251)

Tessel no longer runs page code for previews at all. Third-party link scanners and preview tools that use a real browser still will, and Tessel can't detect them reliably. So runtime writes are gated, and the gate sits in Tessel's wrapper, where page code can't fake it.

1. The runtime in the frame sends writes, for example `vote`, to the wrapper by `postMessage`. The wrapper then calls Tessel's API.
2. The wrapper forwards a write only after the visitor has interacted with the page, using `navigator.userActivation.hasBeenActive`.
   - User activation inside a frame also activates its ancestors, so the wrapper sees a real click in the frame even though it is cross-origin.
   - A write made before any interaction is rejected with a clear runtime error code (`interaction_required`), so authors understand what happened.
3. The wrapper and runtime also hold back writes while the document is prerendering (`document.prerendering`), and they ignore hidden or prefetch loads.
4. A `GET` of the wrapper or the content never changes data.
5. Defense in depth on the server: write endpoints are rate-limited per viewer pseudonym and per IP at the edge. Whether a poll allows one vote per viewer is up to the page, but the per-page viewer pseudonym makes that possible.

This blocks the reported case: a preview tool that loads the page and leaves. A headless browser that deliberately clicks can still write, which is the same exposure as any public form.

## Data model additions (page record)

- `metadataOverride`: optional `{ title, description, iconKey, imageKey }`, set by the author in settings.
- `metadataVersion`: current version ID, bumped on each save that changes extracted metadata.
- `extracted`: `{ title, titleSource, description, descriptionSource, iconKeys, imageKey, imageSource, missing[] }`, keyed to `metadataVersion`.
- Object storage keys are opaque and keep no filenames. The database maps each version to its keys, and old versions are swept after their CDN lifetime.

## Verification before calling this done

- Paste a public, an unlisted, and a private link into real tools, signed out: Slack, Discord, iMessage, X, LinkedIn. Use each tool's refresh after changes.
- Check expected results:
  - Public and unlisted links show a full card.
  - Private links show only "Tessel".
  - A JavaScript-only page shows its name and the generated image.
- Fetch each kind of page with `curl`, with no cookies and then with a member's cookies, and check the private head is the fallback both times.
- Open a page that sets its own title and icon. The tab should show both, including after the page changes its title at runtime.
- Paste a poll link into tools that render with a full browser, and confirm the vote count doesn't move.
- Make a public page private, then check the wrapper, the tags, and the image URL all fall back right away.

## Assumptions to confirm

1. **The tab and card title end with " · Tessel".** This follows the convention of page name first, product name last. Authors who want their exact title with no suffix would need a separate decision, possibly a plan feature.
2. **Private pages show their title in a member's tab, set only by the client after authorization.** The server never sends it, even to members. That trade-off comes from bug 233.
3. **The fallback for private, missing, and deleted pages is identical and says only "Tessel".** It doesn't say "private page", and it doesn't tell a signed-out visitor whether the address exists. How the sign-in prompt behaves on those addresses should match this.
4. **No screenshot previews in this version.** Preview images are the declared image or a generated title card, so Tessel never runs user code to make them. Screenshots could come later, but only in an isolated renderer with no session, no write access, and no access to internal networks.
5. **A runtime write needs a prior user interaction.** This breaks pages that write on load with no gesture, such as a view counter. I judged that acceptable because writing on load is exactly what bug 251 is. If the owner wants on-load writes, they would need an explicit, separately designed option.
6. **The runtime is already injected into or loaded by every page, and pages are served from a separate user-content domain.** If either is not true yet, the live-title and write-gate parts depend on it.
7. **Unlisted pages get a full, rich card.** Anyone holding the link can already open the page, which is what makes it unlisted.
8. **An optional metadata override in page settings is fine.** It never blocks publishing, so it stays within "nobody should have to write a manifest".
9. **The exact URL of the preview-image route, and the page address format, are left to the routing design.** This document only says the image route is Tessel-owned and keyed by page ID and metadata version.

````

> Result: File created successfully at: <run>\builds\4-embedded-page-metadata-new-opus2\work\docs\metadata.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/metadata.md`. It isn't committed, and nothing has been built or tested yet. All four bugs come from one fact: browsers and link-preview tools only look at Tessel's outer wrapper page, never at the person's HTML running inside it. So the design has Tessel work out every title, icon and preview card itself, on its own server.

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

**Session ended:** success, 7 turns, 165633 ms
