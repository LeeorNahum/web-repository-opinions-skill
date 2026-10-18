# Domains

Lay out hosts around one canonical origin per surface, with the primary surface on the apex.

- Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The apex carries sign-in only when its public pages are the product itself, so a signed-out visitor uses the same surface a signed-in one does and signing in only adds to it.
- Signed-in app on its own subdomain: `app.example.com`.
- Additional product surfaces on their own role subdomain: `dashboard.example.com`, `admin.example.com`, `portal.example.com`.

When the apex uses the `.app` TLD, prefer `web.` for the browser app unless a different subdomain better matches its role.

The subdomain is the role word, matching the surface name. There is no need for generic alternatives like `application` or `dash`.

Use no `www`. Serve and link the apex directly. If a www host exists at the registrar, redirect it to the apex at DNS, hosting, CDN, or edge, never in app code. This is a one-time setup, not an ongoing concern in app logic.

## Every other domain you own is an alias, not a second home

`www` is only the most common case of a wider rule. A product usually accumulates other hosts: a second top-level domain bought defensively, a domain from an earlier name, a common misspelling, a short link domain. None of them is a place the product lives. A former domain that only the owner and their own tools ever used is retired with its name rather than kept as an alias. A domain with a distinct security role, such as the domain for code users supply below, is a serving origin of its own and gets no redirect.

Point each one at the canonical origin with a permanent redirect that preserves path and query, so a deep link into an alias lands on the same page rather than the home page. Do it at DNS, hosting, CDN, or edge, never in app code, exactly as with `www`.

Never serve the same content on two domains. Two live copies split search ranking between them, force every canonical tag and share link to pick a side, and teach anyone who bookmarks the alias a name that is not the product's.

Attach aliases to the same hosting project as the canonical origin rather than parking them at the registrar. One project means one certificate story and one redirect rule, and the alias inherits the canonical host's configuration instead of drifting from it.

One failure worth expecting, because it looks like something else:

- **An alias cannot serve until its target can.** A redirect host has nothing to redirect to until the canonical origin has a successful production deployment. Before that, the alias may fail to complete a TLS handshake at all, which reads as a certificate or DNS fault and is neither. Deploy the canonical origin first, then judge the alias.

Verify an alias by requesting a path with a query string, not just the bare host. A redirect that drops the path looks correct on the home page and loses every real link.

Staging uses a `preview.` prefix on the production host so it has real, stable origins instead of random platform URLs:

| Surface | Production | Staging (`preview` branch) |
| --- | --- | --- |
| Site | `example.com` | `preview.example.com` |
| App | `app.example.com` | `preview.app.example.com` |

Use custom domains everywhere, including for staging origins, OAuth origins, and webhook URLs. Remove the auto-generated platform alias once custom domains are attached, and keep it out of any provider allowlist.

The canonical production origin is a code constant, not a fallback string hidden inside a route handler.

## Code Your Users Supply Runs On Its Own Domain

When the product serves HTML or JavaScript its users supply, serve it from a separate registrable domain, never from a subdomain of the product's own. A browser treats every HTTPS subdomain of one registrable domain as the same site, so same-site requests carry same-site cookies, and script on any subdomain can also set a cookie for the parent domain. A managed auth provider that shares its session across subdomains is then exposed to whatever runs on a sibling, which can plant a session cookie that signs a visitor into another account or reach the session itself. The product's domain serves only the product's own pages, and the page at the product's address frames the content by its URL on the content domain, so visitors still see that address. Content written into the product's own page, inline or as a source document, inherits that page's policies and, unless sandboxed, its origin, so it gets none of this isolation.

- Give each item its own subdomain on the content domain, so each item has its own origin and its own storage.
- Request the content domain's inclusion in the private section of the Public Suffix List once it meets the list's criteria, and rely on it only after browsers ship the entry. Until then every subdomain on it is one site and one item can set a cookie the others receive, so keep the product's own cookies there host-only with the `__Host-` prefix.
- When an item's code needs to know its viewer, give it a pseudonym the server derives per item, so no identifier follows a viewer across items.
- Keep the content domain out of search, with the product's address as the canonical one.
- Where no separate domain is available yet, serve the content with an opaque origin: the serving edge sets an enforced `Content-Security-Policy` response header whose `sandbox` directive omits `allow-same-origin`, granting only the permissions the content needs, and the content loses browser storage. Where code already ran on that host, unregister its service workers and clear its storage first, because a worker registered earlier keeps the host's origin and bypasses the header.

Ask before changing production domains or OAuth callback hosts.
