# Public Discovery

Treat public discovery as a rendered-page contract. Every canonical public page must expose its useful identity and primary content in the initial HTML through server rendering or static generation.

A client without JavaScript must be able to read the primary heading, descriptive text, semantic links, canonical metadata, and applicable structured data. Client enhancement may improve interaction, but it cannot be the only source of indexable content.

Use one canonical URL per public resource. Apply `noindex` to arbitrary query combinations and omit them from sitemaps. Generate sitemap entries from the same eligibility function that decides whether a page is public, available, substantial, and canonical.

Give a sitemap entry a `lastmod` only from a reliable record of when the page's main text, links, or structured data last changed, and omit it where no such record exists, since search engines use the field only while it stays accurate. A build or deploy time claims a change on every deploy, and a hand-written date is wrong from the next edit on. Take the date from whatever owns the content: the record's own modified time for a page rendered from stored data, and for a page whose content lives in code, a fingerprint of its rendered text, links, and structured data taken from the production build, moved only when the fingerprint moves and checked so content cannot change without its date. Omit priority and change frequency, which Google ignores.

Keep `robots.txt` general and include the sitemap location. Add crawler-specific policy only when that crawler requires a genuinely different access rule.

Partition sitemaps only near protocol URL limits or demonstrated generation limits. Verify representative pages with JavaScript disabled, a plain HTTP client, and a scraper before calling discovery complete.
