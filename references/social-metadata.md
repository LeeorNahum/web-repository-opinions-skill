# Social Metadata

Every surface declares its identity for browsers and for the link-preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.

## Favicon

Every surface ships a favicon. Set it deliberately rather than leaving the framework default.

- First check whether a brand icon already exists in the repo or the brand source, and reuse it. Prefer an SVG icon, which scales cleanly across all sizes.
- If none exists, create an SVG icon from the brand identity and use it.
- Place the icon at the framework's expected path so the favicon links are emitted automatically.
- Use the canonical brand asset, never a placeholder or a redrawn copy.

## Link Preview Cards

Every publicly reachable page produces a correct preview card when its URL is shared. This is the embed that renders a title, description, and image on chat apps, social platforms, and document tools. Implement it on the public site as a first-class feature, not an afterthought.

- Set a base URL in each surface's root so relative metadata resolves to absolute URLs.
- Give each public page a real title, a description, and a share image at standard card dimensions in brand colors.
- Provide both the open-graph and the platform-specific card fields so the card renders across tools.
- Verify a real shared link renders the card, rather than assuming the tags are correct.

## Public Versus Private

Public pages earn rich, specific metadata and preview cards. Private, dynamic pages get a generic, content-free fallback. Never leak private content into a title, description, or preview image. The split mirrors the SEO posture: detail in public, opacity in private.
