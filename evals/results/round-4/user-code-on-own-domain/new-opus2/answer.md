I wrote the plan to `docs/hosting-plan.md`. It isn't committed.

**The main problem:** each app's code runs directly on `<name>.plinth.example`. The sign-in session is on `plinth.example` and shared with every subdomain, so any app's script can read a visitor's session if the provider exposes it to script, which many do. It can also plant a cookie that signs visitors into someone else's account on `app.plinth.example`. Private apps make this worse, because their visitors are all signed in. I don't think we should open the beta with this as it is.

**What I planned:**
- **Beta, within the freeze:** short addresses stay. On every response from an app address, the edge adds a header that sandboxes the page so it runs with no origin of its own. App code then can't read or set our cookies. This needs no new domains, DNS or certificates.
- **Edge rules for the beta:**
  - The header goes on every response, including SVGs, error pages and redirects.
  - The edge decides content types and never sets cookies on app addresses.
  - For private apps, the edge checks the session cookie but never logs it, passes it on or caches with it.
  - Leftover service workers from before the change get cleared out.
  - App addresses aren't indexed by search engines.
- **Reserved app names:** names like `clerk`, `accounts`, `app` and `api` are blocked, plus a test against the DNS records. Otherwise an app called `clerk` could take over the sign-in provider's addresses.
- **Hardening on `app.plinth.example`:** it refuses requests from the sandboxed pages, and other sites can't embed it.
- **After the freeze:** a separate domain only for app code (`plinthusercontent.example` is a placeholder name). `<name>.plinth.example` becomes a small page of ours that shows the app in an embedded frame from that domain, so visitors still see the short address. Each app gets its own browser storage, and there's a design for private-app access across the two domains.

**Decision for you — the big tradeoff:** the beta sandbox turns off `localStorage`, which the brief says apps often use. I chose security over it. I recommend asking for one freeze exception before launch, for one new domain, its DNS zone and one wildcard certificate. That lets the final setup ship on day one and keeps `localStorage` working. The other options are telling beta users storage comes later, or delaying the beta.

**What I assumed:**
- `*.plinth.example` already reaches our edge and is covered by a wildcard certificate.
- Apps are static files only, so the edge controls every response header.
- Apps have been served from these addresses before, which is why the service-worker cleanup is included.
- No preview/staging addresses for apps during the freeze, since they'd need a new certificate.

The rest of the open questions are in the doc: the real name for the app-code domain, and whether public apps should be indexable. Nothing in the plan changes production DNS, domains, certificates or sign-in settings without your sign-off.