# Domains

Lay out hosts around one canonical origin per surface, with the primary surface on the apex.

- Primary site on the apex: `example.com`. This is the default home, and it may itself be signed-in capable; signing out returns the user to the signed-out view of the same surface.
- Signed-in app on its own subdomain: `app.example.com`.
- Additional surfaces on their own role subdomain: `dashboard.example.com`, `admin.example.com`, `portal.example.com`.

The subdomain is the role word, matching the surface name. There is no need for generic alternatives like `application` or `dash`.

Use no `www`. Serve and link the apex directly. If a www host exists at the registrar, redirect it to the apex at DNS, hosting, CDN, or edge, never in app code. This is a one-time setup, not an ongoing concern in app logic.

## Every other domain you own is an alias, not a second home

`www` is only the most common case of a wider rule. A product usually accumulates other hosts: a second top-level domain bought defensively, a domain from an earlier name, a common misspelling, a short link domain. None of them is a place the product lives.

Point each one at the canonical origin with a permanent redirect that preserves path and query, so a deep link into an alias lands on the same page rather than the home page. Do it at DNS, hosting, CDN, or edge, never in app code, exactly as with `www`.

Never serve the same content on two domains. Two live copies split search ranking between them, force every canonical tag and share link to pick a side, and teach anyone who bookmarks the alias a name that is not the product's.

Attach aliases to the same hosting project as the canonical origin rather than parking them at the registrar. One project means one certificate story and one redirect rule, and the alias inherits the canonical host's configuration instead of drifting from it.

Two failures worth expecting, because both look like something else:

- **An alias cannot serve until its target can.** A redirect host has nothing to redirect to until the canonical origin has a successful production deployment. Before that, the alias may fail to complete a TLS handshake at all, which reads as a certificate or DNS fault and is neither. Deploy the canonical origin first, then judge the alias.
- **Proxying breaks automatic certificates.** Where the DNS provider offers to proxy a record, leave alias and canonical records unproxied unless the host documents otherwise, or certificate issuance silently never completes.

Verify an alias by requesting a path with a query string, not just the bare host. A redirect that drops the path looks correct on the home page and loses every real link.

Staging uses a `preview.` prefix on the production host so it has real, stable origins instead of random platform URLs:

| Surface | Production | Staging (`preview` branch) |
| --- | --- | --- |
| Site | `example.com` | `preview.example.com` |
| App | `app.example.com` | `preview.app.example.com` |

Use custom domains everywhere, including for staging origins, OAuth origins, and webhook URLs. Remove the auto-generated platform alias once custom domains are attached, and keep it out of any provider allowlist.

The canonical production origin is a code constant, not a fallback string hidden inside a route handler.

Ask before changing production domains or OAuth callback hosts.
