# Domains

Lay out hosts around one canonical origin per surface, with the primary surface on the apex.

- Primary site on the apex: `example.com`. This is the default home, and it may itself be signed-in capable; signing out returns the user to the signed-out view of the same surface.
- Signed-in app on its own subdomain: `app.example.com`.
- Additional surfaces on their own role subdomain: `dashboard.example.com`, `admin.example.com`, `portal.example.com`.

The subdomain is the role word, matching the surface name. There is no need for generic alternatives like `application` or `dash`.

Use no `www`. Serve and link the apex directly. If a www host exists at the registrar, redirect it to the apex at DNS, hosting, CDN, or edge, never in app code. This is a one-time setup, not an ongoing concern in app logic.

Staging uses a `preview.` prefix on the production host so it has real, stable origins instead of random platform URLs:

| Surface | Production | Staging (`preview` branch) |
| --- | --- | --- |
| Site | `example.com` | `preview.example.com` |
| App | `app.example.com` | `preview.app.example.com` |

Use custom domains everywhere, including for staging origins, OAuth origins, and webhook URLs. Remove the auto-generated platform alias once custom domains are attached, and keep it out of any provider allowlist.

The canonical production origin is a code constant, not a fallback string hidden inside a route handler.

Ask before changing production domains or OAuth callback hosts.
