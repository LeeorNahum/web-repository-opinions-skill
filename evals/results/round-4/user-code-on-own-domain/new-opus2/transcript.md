**Prompt:** Before the beta opens, review how we serve people's apps (docs/hosting.md) and write the hosting and origin layout we should ship to docs/hosting-plan.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-user-code-on-own-domain-new-opus2/work\" && git ls-files && cat docs/*.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5351 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-user-code-on-own-domain-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat domains.md origins.md dns.md"}`

> Result: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 10921 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-user-code-on-own-domain-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat social-metadata.md object-storage.md auth.md | head -300; grep -il \"user-supplied\\|users supply\\|content domain\\|sandbox\" *.md"}`

> Result: # Social Metadata  Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.  ## Favicon  Every surface ships a favicon. Set it deliberately rather than leaving the framewo [... 23946 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-user-code-on-own-domain-new-opus2/work/.claude/skills/web-repository-opinions/references\" && grep -n -i -B2 -A8 \"user-supplied\\|users supply\\|content domain\\|sandbox\" provider-setup.md uploads.md; cat search-indexing.md | head -40; grep -n -i \"noindex\\|robots\" seo.md public-discovery.md | head -20"}`

> Result: provider-setup.md-28-## Provider Shape provider-setup.md-29- provider-setup.md:30:Map the product's stages onto each provider's own isolation model before creating anything. Prefer the provider's native environments, modes, sandboxes, deployments, or credential scopes inside one canonical project when they keep stages independently configurable and safe. Create separate projects or accounts only w [... 5093 more characters]

**Tool call `Write`:** `<run>\builds\4-user-code-on-own-domain-new-opus2\work\docs\hosting-plan.md`

````text
# Hosting and origin plan

Status: proposed for the beta. Written while the owner was away. Assumptions and open decisions are at the end.

## The problem with how apps are served today

Each user's `index.html` is the top-level document on `<name>.plinth.example`. Our signed-in product is `app.plinth.example`. The auth session lives on `plinth.example` and is shared across all subdomains. Browsers treat every HTTPS subdomain of `plinth.example` as the same site, so today:

- **Session theft.** A visitor's session cookie is sent to every `<name>.plinth.example`. If the provider makes the session token readable by script (many managed providers do, so their client SDKs can read it), any app can read a visitor's session and send it somewhere else.
- **Session planting (cookie tossing).** Script on any app can set a cookie for `Domain=plinth.example`. That can sign a visitor into the attacker's account on `app.plinth.example`, or override the real session.
- **Same-site requests.** Requests from an app to `app.plinth.example` count as same-site, so `SameSite=Lax/Strict` gives no CSRF protection against them.
- **Private apps make it worse.** The visitors who are signed in are exactly the ones whose sessions get exposed.

So before the beta opens, an app's code must not run with a `plinth.example` origin. The usual fix is to serve user code from a separate registrable domain. The change freeze (no new domains, zones, or certificates for about two months) rules that out for the beta, so the plan has two phases.

## Phase 1: beta, inside the freeze

Short addresses stay as they are: `<name>.plinth.example`. Every response the edge sends from an app host gets an **opaque origin** through an enforced response header:

```
Content-Security-Policy: sandbox allow-scripts allow-forms allow-modals allow-popups allow-downloads
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

`allow-same-origin` and `allow-top-navigation*` are deliberately left out. The browser then runs the document with a unique opaque origin instead of `https://<name>.plinth.example`. That means:

- `document.cookie` throws, so script can't read the session or plant cookies on `plinth.example`.
- Requests from the app to `app.plinth.example` are cross-site, so `SameSite=Lax` session cookies aren't attached.
- Service worker registration is blocked.
- **`localStorage`, `sessionStorage`, IndexedDB, and other storage are unavailable** (accessing them throws). This is the main cost. See the open decisions.

Edge rules that go with it:

1. **The header goes on every response from an app host**: HTML, SVG, XML, every other file type, 404s, error pages, and redirects. A file the header misses (for example an uploaded `.svg` opened directly) runs as `plinth.example`. It must be a response header. A `<meta>` CSP can't sandbox, and user files can't remove the header.
2. **The edge decides content types.** Content-Type comes from an allowlist keyed by extension. Anything unknown is `application/octet-stream`. Users get no control over response headers. In particular the edge never emits a `Set-Cookie` on an app host.
3. **The session cookie is only used, never passed on.** For private apps, the edge reads the provider session from the request, verifies it, checks the visitor is invited to that app, and then serves the file. The cookie is never logged, never forwarded to object storage, and never part of a cache key. Private responses are `Cache-Control: private, no-store`.
4. **Denied private requests get a content-free answer.** If a private app is requested without permission, the edge redirects to `https://app.plinth.example/auth` with the app's short address as the return destination. That page's title, description, and preview tags name Plinth and nothing about the app. The return destination is validated by shape, so it must be `https://<valid-app-name>.plinth.example/<path>` and nothing else, which keeps it from being an open redirect.
5. **Clean up workers left from before the sandbox.** Apps were already served same-origin, so any of them could have registered a service worker, and that worker would keep answering navigations and never see the new header. On every app host, answer any request that carries `Service-Worker: script` with a replacement worker that deletes its caches and unregisters itself. Once requests reach the edge again, send `Clear-Site-Data: "storage"` on app hosts. Run this for the whole beta.
6. **App names can't be search-indexed by accident.** App hosts send `X-Robots-Tag: noindex` by default during the beta. Public discovery of apps is a later product decision.

Hardening on `app.plinth.example` (cheap, and it holds in both phases):

- Never answer CORS for `Origin: null` or for any `*.plinth.example` app host. Reject state-changing requests whose `Origin` is `null`.
- Confirm the session cookie is `Secure`, `SameSite=Lax` or stricter, and as narrow as the provider allows.
- Send `Content-Security-Policy: frame-ancestors 'self'` so apps can't frame the product to clickjack it.

### Reserved names

Apps and our own role and provider hosts share one namespace, so an app called `clerk` or `accounts` would take over the auth provider's hosts. Reject these as app names in code (one list in a shared package), before any DNS or edge lookup:

`app`, `www`, `api`, `admin`, `dashboard`, `portal`, `auth`, `accounts`, `clerk`, `clkmail`, `mail`, `email`, `preview`, `status`, `docs`, `help`, `support`, `cdn`, `static`, `assets`, `files`, `blog`, plus anything starting with `_` and any label already present as a record in the `plinth.example` zone. Ship a test that loads the zone's record names and fails if an app name could collide with one.

## Phase 2: after the freeze — user code on its own domain

When the freeze ends, register a separate registrable domain only for user content. The placeholder name used below is `plinthusercontent.example`; the owner picks the real one. It gets its own DNS zone and wildcard certificate. Short addresses don't change.

| Host | Serves |
| --- | --- |
| `plinth.example` | Product's public site (apex) |
| `app.plinth.example` | Signed-in product |
| `<name>.plinth.example` | Product-owned outer page for the app (the address visitors see and share) |
| `<name>.plinthusercontent.example` | The app's own files, one origin per app |

- **Outer page.** `<name>.plinth.example` serves a small page we write. It holds only an `<iframe src="https://<name>.plinthusercontent.example/...">` that fills the viewport, with the path and query passed through. We never write the user's markup into our page inline or via `srcdoc`.
- **Metadata belongs to the outer page.** Its title, favicon, and Open Graph or preview tags are taken on the server from the app's own `<head>` when the app is saved. Private apps get the content-free fallback on every request that isn't authorized, link-preview bots included. Preview images, if generated, are rendered in an isolated renderer with no credentials and no network reach.
- **Storage comes back.** Each app is its own origin, so `localStorage` works again and is kept separate per app. Browsers partition iframe storage by the top-level site, so storage is consistent when the app is opened through its short address, which is the supported way. Since Phase 1 had no storage at all, there's nothing to migrate.
- **Content domain posture.**
  - Apply to the private section of the Public Suffix List once the domain meets its criteria. Until browsers ship the entry, every app on it is still one site, so any cookie we set there is host-only with a `__Host-` prefix.
  - `robots.txt` disallows everything. Responses send `X-Robots-Tag: noindex`, and the canonical address is the short address.
  - Requests that aren't framed by the matching outer page are redirected to the short address: check `Sec-Fetch-Dest` and `Sec-Fetch-Site` at the content edge, and send `frame-ancestors https://<name>.plinth.example` from the content host.
- **Private apps across the two domains.** The content domain never gets the `plinth.example` session. After the outer page passes its edge check, it puts a short-lived signed grant (scoped to app + viewer) in the iframe URL. The content edge swaps the grant for a host-only `__Host-` cookie that is `Partitioned; Secure; SameSite=None`. Before Phase 2 ships, check this works in Safari's and Firefox's third-party cookie handling. The fallback is a grant on every request.
- **Viewer identity, if apps ever need it.** Give each app a per-app pseudonym the server derives, never the account ID, so a viewer can't be tracked from one app to another.
- **Phase 1 sandbox comes off only on the content domain.** `<name>.plinth.example` stays product-only for good.

## Origins in code

Put a shared origins module in `packages/` with `CANONICAL_SITE_ORIGIN`, `CANONICAL_APP_ORIGIN`, a resolver for app short addresses (`resolveAppAddress(name)`), and in Phase 2 `resolveAppContentOrigin(name)`. These are code constants. Env overrides use the same key names in every stage. The edge, the product UI, and any copyable URL all build hosts through this module. App-host matching (for return destinations and reserved names) lives here too.

## Assumptions

- `*.plinth.example` already resolves to our edge through a wildcard record, and a wildcard certificate already covers it. Phase 1 needs no DNS or certificate change, so it fits the freeze.
- The auth provider's session cookie is `Domain=plinth.example`, as the brief says, and may be readable by script. Phase 1 is safe either way.
- Apps are static files only, with no server code we run, so the edge controls every response header.
- Apps have been served same-origin before today, so the service-worker cleanup is needed.
- No staging host for apps is added during the freeze. Staging for apps (`<name>.preview.plinth.example` would need a new certificate) waits for Phase 2.
- `plinthusercontent.example` is a placeholder name.

## Open decisions for the owner

1. **`localStorage` during the beta.** The brief says apps often use it, and Phase 1 turns it off. I chose security, because leaving apps same-origin exposes every signed-in visitor's session on a domain that's shared across subdomains. Options:
   - (a) Accept it. Tell beta users that storage arrives with Phase 2, and show it in the publish flow when an app's code references `localStorage`.
   - (b) **Recommended:** ask for one freeze exception before the beta opens: one new domain, its zone, and one wildcard certificate. That lets Phase 2 ship at launch and skip Phase 1.
   - (c) Delay the beta.

   Leaving apps same-origin with the shared session isn't on the list.
2. The real name for the content domain.
3. Whether public apps should be indexable under their short addresses. The default here is `noindex`.

Nothing in this plan changes production DNS, domains, certificates, or auth settings. Each of those steps needs the owner's sign-off before it's done.

````

> Result: File created successfully at: <run>\builds\4-user-code-on-own-domain-new-opus2\work\docs\hosting-plan.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the plan to `docs/hosting-plan.md`. It isn't committed.

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

**Session ended:** success, 8 turns, 126982 ms
