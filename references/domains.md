# Domains

Lay out hosts around one canonical origin per surface, with the primary surface on the apex.

- Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The apex carries sign-in only when its public pages are the product itself, so a signed-out visitor uses the same surface a signed-in one does and signing in only adds to it.
- Signed-in app on its own subdomain: `app.example.com`.
- Additional product surfaces on their own role subdomain: `dashboard.example.com`, `admin.example.com`, `portal.example.com`.

When the apex uses the `.app` TLD or a native mobile app is planned, prefer `web.` for the browser app unless a different subdomain better matches its role, so `app` never names two things at once. A native mobile app takes no subdomain.

Use no `www`. Serve and link the apex as the canonical host, even where the hosting platform recommends `www` as primary. If a www host exists at the registrar, redirect it to the apex at DNS, hosting, CDN, or edge, never in app code. This is a one-time setup, not an ongoing concern in app logic.

## Aliases Redirect To The Canonical Host

`www` is only the most common case of a wider rule. A product usually accumulates other hosts: a second top-level domain bought defensively, a domain from an earlier name, a common misspelling, a short link domain. None of them is a place the product lives. A former domain that only the owner and their own tools ever used is retired with its name rather than kept as an alias. The domain for user-supplied code, below, is a serving origin of its own, not an alias.

Point each one at the canonical origin with a permanent redirect that preserves path and query, so a deep link into an alias lands on the same page rather than the home page. Do it at DNS, hosting, CDN, or edge, never in app code, exactly as with `www`.

Never serve the same content on two domains. Two live copies split search ranking between them, force every canonical tag and share link to pick a side, and teach anyone who bookmarks the alias a name that is not the product's.

Attach aliases to the same hosting project as the canonical origin rather than parking them at the registrar. One project means one certificate story and one redirect rule, and the alias inherits the canonical host's configuration instead of drifting from it.

Give the canonical origin a successful production deployment before judging an alias, because a redirect host has nothing to redirect to until its target serves.

Verify an alias by requesting a path with a query string, not just the bare host. A redirect that drops the path looks correct on the home page and loses every real link.

## Staging Hosts

Staging uses a `preview.` prefix on the production host so it has real, stable origins instead of random platform URLs:

| Surface | Production | Staging (`preview` branch) |
| --- | --- | --- |
| Site | `example.com` | `preview.example.com` |
| App | `app.example.com` | `preview.app.example.com` |

Use custom domains everywhere, including for staging origins, OAuth origins, and webhook URLs. Remove the auto-generated platform alias once custom domains are attached, and keep it out of any provider allowlist.

## User-Supplied Code Runs On Its Own Domain

When the product serves HTML or JavaScript its users supply, serve it from a separate registrable domain, never from a subdomain of the product's own. Every HTTPS subdomain of one registrable domain is the same site to a browser, and script on any of them can set a cookie for the parent domain, so user code on a sibling can plant or reach the session a managed auth provider shares across subdomains. The product's domain serves only its own pages. Where visitors should see the product's address, a page there frames the content.

- Give each item its own subdomain on the content domain, so each item has its own origin and its own storage.
- When the product frames an item, frame it by its URL on the content domain. Markup written into the product's own page, inline or through `srcdoc`, runs as the product.
- Request the content domain's entry in the private section of the Public Suffix List, and until browsers ship it, set every cookie the product issues on the content domain host-only with the `__Host-` prefix, because until then every item on it is one site.
- When an item's code needs to know its viewer, give it a pseudonym the server derives per item, so no identifier follows a viewer across items.
- When the product frames its items, keep the content domain out of search, with the framing page's address as the canonical one.
- Where no separate domain is available yet, serve the content with an opaque origin through an enforced `Content-Security-Policy: sandbox` response header without `allow-same-origin`, at the cost of browser storage.

Ask before changing production domains or OAuth callback hosts.
