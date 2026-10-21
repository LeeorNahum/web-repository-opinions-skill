# Public Discovery

Treat public discovery as a rendered-page contract. Every canonical public page must expose its useful identity and primary content in the initial HTML through server rendering or static generation.

A client without JavaScript must be able to read the primary heading, descriptive text, semantic links, canonical metadata, and any structured data the page declares. Client enhancement may improve interaction, but it cannot be the only source of indexable content.

Use one canonical URL per public resource. Apply `noindex` to arbitrary query combinations and omit them from sitemaps, unless a combination is a deliberate landing page with durable intent. Generate sitemap entries from the same eligibility function that decides whether a page is public, available, substantial, and canonical.

Judge unavailable public pages by the content that remains. Keep a page indexable when its durable metadata still provides substantial, trustworthy value. Use `noindex` and omit it from the sitemap when the missing primary content would make the page thin, misleading, or temporarily unverifiable. Give unavailable pages a dedicated presentation instead of rendering provider errors or placeholder text that resembles real content.

Keep `robots.txt` general and include the sitemap location. Add crawler-specific policy only when that crawler requires a genuinely different access rule.

Partition sitemaps only near the protocol's limits of 50,000 URLs or 50 MB per file, or near demonstrated generation limits. Verify representative pages with JavaScript disabled, a plain HTTP client, and a scraper before calling discovery complete.

Register the site in the search provider's console for the canonical host, verify ownership by DNS record rather than by granting the search provider OAuth access to the whole DNS account, and submit the sitemap. Ownership verification is frequently a prerequisite for unrelated provider checks, so do it early and never remove the verification record.
