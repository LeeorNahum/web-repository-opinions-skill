# Public Discovery

Treat public discovery as a rendered-page contract. Every canonical public page must expose its useful identity and primary content in the initial HTML through server rendering or static generation.

A client without JavaScript must be able to read the primary heading, descriptive text, semantic links, canonical metadata, and applicable structured data. Client enhancement may improve interaction, but it cannot be the only source of indexable content.

Use one canonical URL per public resource. Apply `noindex` to arbitrary query combinations and omit them from sitemaps. Generate sitemap entries from the same eligibility function that decides whether a page is public, available, substantial, and canonical.

Keep `robots.txt` general and include the sitemap location. Add crawler-specific policy only when that crawler requires a genuinely different access rule.

Partition sitemaps only near protocol URL limits or demonstrated generation limits. Verify representative pages with JavaScript disabled, a plain HTTP client, and a scraper before calling discovery complete.
