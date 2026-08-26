# Social Metadata

Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.

## Favicon

Every surface ships a favicon. Set it deliberately rather than leaving the framework default.

First check whether a brand icon already exists in the repo or brand source, and reuse it. Prefer SVG, which scales cleanly. If none exists, create one from the brand identity. Use the canonical brand asset, never a placeholder or a redrawn copy.

For **Next.js App Router**, ship two files in `app/` and nothing else:

- `app/icon.svg` - Next.js auto-generates `<link rel="icon">` and serves it at `/icon.svg`. Use `/icon.svg` for in-page references such as the site header logo and OG image renderer.
- `app/apple-icon.png` - the same icon as a 180x180 PNG. Next.js auto-generates `<link rel="apple-touch-icon">` for iOS home screen bookmarks.

Do not add `metadata.icons` in `layout.tsx`. The files above handle it automatically with no configuration. Do not copy the icon into `public/` unless the product has additional brand assets beyond the favicon. Do not use `rel="shortcut icon"` - it is deprecated.

Keep the in-page path in a named constant so all callers stay in sync if the path ever changes.

## Link Preview Cards

Every publicly reachable page produces a correct preview card when its URL is shared. Some tools call the card an unfurl. The tool builds it from the page's Open Graph tags and its platform-specific card tags, reading the initial HTML and running no script. Implement it as a first-class feature of every public page, not an afterthought.

Publicly reachable means anyone holding the link can open the page signed out. An unlisted share route that stays `noindex` is still publicly reachable and still gets its real card, because a link-expanding tool ignores indexing directives.

A correct card contains:

- The page's own subject as the title, then the product name after the site's one separator, exactly as the tab is titled.
- A description of that page in particular, specific enough that no two pages share one.
- A generated image at the standard card size showing the product mark, the product name, and the page's subject, in the product's colors and type, built from the same subject the title uses. The site-wide brand image belongs to the homepage alone, and a placeholder belongs nowhere.

Getting the tags onto the page:

- Set a base URL in each surface's root so relative metadata resolves to absolute URLs.
- Provide both the Open Graph fields and the platform-specific card fields, including the large-image card type, so the card renders across tools.
- Render the tags on the server for every page, including one whose body is client-rendered, and resolve the page's subject in the same server lookup that resolves the page.
- When a route overrides part of the metadata, confirm the image, the site name, and the card type survive, because a nested override commonly replaces the parent's whole object rather than merging into it, and the card quietly loses its image.
- Verify by pasting a real link into a real tool, signed out, rather than assuming the tags are correct. Tools cache a card by URL, so re-check after a change with the tool's own refresh.

## Public Versus Private

Public pages earn rich, specific metadata and preview cards. Private pages produce no card about their content: a generic, content-free fallback names the product and nothing else. Never leak private content into a title, description, or preview image. The split mirrors the SEO posture: detail in public, opacity in private.

A page that stops being public, because sharing was turned off or the resource was removed, drops to the same content-free fallback, so a link that outlives its share cannot keep naming what it pointed at.
