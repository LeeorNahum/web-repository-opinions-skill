# SEO

SEO is a property of public pages only. Apply it to the marketing site, never to private app routes.

For public pages:

- Give each page a descriptive, stable, human-readable path
- Render on the server or statically so crawlers see real content
- Set a unique title and description per page
- Expose canonical URLs and avoid duplicate paths for the same content
- Keep one canonical host so link equity is not split
- Noindex arbitrary query combinations unless they are deliberate landing pages with durable intent
- Exclude deleting records and pages that intentionally return not found from sitemaps

Private app pages get a generic, content-free metadata fallback. Never leak private content into titles, descriptions, or social previews of authenticated routes.

Descriptive SEO paths are correct for public pages (`/pricing`, `/security`, `/help/uploads`). They are wrong for private resources, which use short opaque IDs instead.

Judge unavailable public pages by the content that remains. Keep a page indexable when its durable metadata still provides substantial, trustworthy value. Use `noindex` and omit it from the sitemap when the missing primary content would make the page thin, misleading, or temporarily unverifiable. Give unavailable pages a dedicated presentation instead of rendering provider errors or placeholder text that resembles real content.
