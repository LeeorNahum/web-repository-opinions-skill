# Social Metadata

Every surface declares its identity for browsers and for the link-preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.

## Favicon

Every surface ships a favicon. Set it deliberately rather than leaving the framework default.

First check whether a brand icon already exists in the repo or brand source, and reuse it. Prefer SVG, which scales cleanly. If none exists, create one from the brand identity. Use the canonical brand asset, never a placeholder or a redrawn copy.

For **Next.js App Router**, ship two files in `app/` and nothing else:

- `app/icon.svg` - Next.js auto-generates `<link rel="icon">` and serves it at `/icon.svg`. Use `/icon.svg` for in-page references such as the site header logo and OG image renderer.
- `app/apple-icon.png` - the same icon as a 180x180 PNG. Next.js auto-generates `<link rel="apple-touch-icon">` for iOS home screen bookmarks.

Do not add `metadata.icons` in `layout.tsx`. The files above handle it automatically with no configuration. Do not copy the icon into `public/` unless the product has additional brand assets beyond the favicon. Do not use `rel="shortcut icon"` - it is deprecated.

Keep the in-page path in a named constant so all callers stay in sync if the path ever changes.

## Link Preview Cards

Every publicly reachable page produces a correct preview card when its URL is shared. This is the embed that renders a title, description, and image on chat apps, social platforms, and document tools. Implement it on the public site as a first-class feature, not an afterthought.

- Set a base URL in each surface's root so relative metadata resolves to absolute URLs.
- Give each public page a real title, a description, and a share image at standard card dimensions in brand colors.
- Provide both the open-graph and the platform-specific card fields so the card renders across tools.
- Verify a real shared link renders the card, rather than assuming the tags are correct.

## Public Versus Private

Public pages earn rich, specific metadata and preview cards. Private, dynamic pages get a generic, content-free fallback. Never leak private content into a title, description, or preview image. The split mirrors the SEO posture: detail in public, opacity in private.
