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

## The Homepage Names The Product

The public homepage carries exactly one `h1`, and the product's name is in it. A headline that states the value proposition without ever naming the product is a marketing habit that costs real things: automated reviewers read the `h1` as the app's name, and a mismatch against the registered name fails checks the product needs to pass. Providers' OAuth consent branding review does exactly this. So does anything else that has to identify a site without a human reading it.

Pair the heading with one server-rendered sentence near the top that names the product and says what it does, so a cold reviewer or a crawler understands the site without scrolling and without JavaScript. Neither line is keyword filler: write what a person would read aloud.

Register the site in the search provider's console for the canonical host, verify ownership by DNS record rather than by granting the search provider OAuth access to the whole DNS account, and submit the sitemap. Ownership verification is frequently a prerequisite for unrelated provider checks, so do it early and never remove the verification record.

Consent-screen and app-listing branding is reviewed against the live page, and passing it is quick once the page agrees with the registration. Two traps make it look otherwise. Saving anything on a branding form usually invalidates an existing verified result, so a later logo upload silently undoes an earlier verification. And a verified result often has to be published separately before users see it, and expires if it is not. Always finish by re-reading the status and confirming it says the branding is being shown, not merely that it verified.

## The Tab Title Leads With The Page

A tab title is read from the left. Tab strips, window switchers, and phone browsers truncate from the right, and the more tabs a person has open the fewer leading characters survive. So the page's own subject goes first and the site name goes last, with one separator chosen once and used everywhere.

Take the subject from the page's own main heading. A tab that says something the page never says is a second name for the same page, and the reader cannot tell which one the site means.

A page about one object leads with that object's own name, not with the name of its type. This is the trap worth naming: a detail route titled by its type gives every one of its pages an identical tab, so a person who opened six of them has six tabs that read the same and must visit each to find the one they wanted. The object's name is already on their screen, so the generic title conceals nothing and spends the only signal a tab strip can carry.

Within one object's routes the object keeps leading and the view inside it follows, so tabs group by object and the part after the name is what tells them apart. Name the file or section on screen, and add a word only for a mode that changes what the page does. The default reading view needs no word.

Private pages follow the same rule. The object's name in a tab is something the reader is already looking at, so it belongs there, while descriptions and social previews travel further than a tab does and stay free of private content, on routes that stay `noindex`.

When the object's name is not known to the server, because the URL addresses it by opaque ID or the view reads live data, the title still leads with it. Give the route a static title that names the type, as the value that stands until the data lands, then write the real title from the data the view already loaded rather than fetching it a second time. Two things have to hold and both are easy to miss. Reset to the placeholder whenever the identity changes, or the previous object's name stays in the tab while the next one loads. And treat the framework's own title as a competitor, because a router that re-renders the document head can supersede a title written imperatively: reassert the title when the head changes, and verify a tab after a client-side navigation rather than only after a reload.

Descriptive SEO paths are correct for public pages (`/pricing`, `/security`, `/help/uploads`). They are wrong for private resources, which use short opaque IDs instead.

Judge unavailable public pages by the content that remains. Keep a page indexable when its durable metadata still provides substantial, trustworthy value. Use `noindex` and omit it from the sitemap when the missing primary content would make the page thin, misleading, or temporarily unverifiable. Give unavailable pages a dedicated presentation instead of rendering provider errors or placeholder text that resembles real content.
