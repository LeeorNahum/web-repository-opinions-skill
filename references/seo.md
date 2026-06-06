# SEO

SEO is a property of public pages only. Apply it to the marketing site, never to private app routes.

For public pages:

- Give each page a descriptive, stable, human-readable path
- Render on the server or statically so crawlers see real content
- Set a unique title and description per page
- Expose canonical URLs and avoid duplicate paths for the same content
- Keep one canonical host so link equity is not split

Private app pages get a generic, content-free metadata fallback. Never leak private content into titles, descriptions, or social previews of authenticated routes.

Descriptive SEO paths are correct for public pages (`/pricing`, `/security`, `/help/uploads`). They are wrong for private resources, which use short opaque IDs instead.
