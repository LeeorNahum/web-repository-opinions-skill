# Domains

Lay out hosts around one canonical origin per surface, with the primary surface on the apex.

- Primary site on the apex: `example.com`. This is the default home. It may itself be signed-in capable, and signing out returns the user to the signed-out view of the same surface.
- Signed-in app on its own subdomain: `app.example.com`.
- Additional surfaces on their own role subdomain: `admin.example.com`, `portal.example.com`.

Use no `www`. Serve and link the apex as the canonical host, even where the hosting platform recommends `www` as primary. If a www host exists at the registrar, redirect it to the apex at DNS, hosting, CDN, or edge, never in app code. This is a one-time setup, not an ongoing concern in app logic.

## Aliases Redirect To The Canonical Host

`www` is only the most common case of a wider rule. A product usually accumulates other hosts: a second top-level domain bought defensively, a domain from an earlier name, a common misspelling, a short link domain. None of them is a place the product lives.

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

Ask before changing production domains or OAuth callback hosts.
