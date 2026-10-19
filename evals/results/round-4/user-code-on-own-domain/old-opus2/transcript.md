**Prompt:** Before the beta opens, review how we serve people's apps (docs/hosting.md) and write the hosting and origin layout we should ship to docs/hosting-plan.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-user-code-on-own-domain-old-opus2/work\"; git ls-files; cat docs/brief.md docs/hosting.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5351 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-user-code-on-own-domain-old-opus2/work/.claude/skills/web-repository-opinions/references\"; cat domains.md origins.md auth.md object-storage.md dns.md"}`

> Result: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 26328 more characters]

**Tool call `Grep`:** `{"pattern": "(?i)untrusted|public suffix|user-authored|sandbox|cookie|same-site|user content", "path": "<run>\\builds\\4-user-code-on-own-domain-old-opus2\\work\\.claude\\skills\\web-repository-opinions", "output_mode": "content"}`

> Result: continuous-integration.md:10:- Use read-only workflow permissions by default. Grant release writes only to the release job, and keep secrets out of untrusted pull-request execution. interaction-feedback.md:26:Transient feedback must not reflow the surrounding interface. Reserve its space, replace content within a stable footprint, or use an overlay surface whose appearance does not move nearby con [... 1892 more characters]

**Tool call `Write`:** `<run>\builds\4-user-code-on-own-domain-old-opus2\work\docs\hosting-plan.md`

````text
# Hosting and origin plan for the beta

Status: proposal written while the owner was away. Items marked **Owner decision** need a yes/no before the beta opens. Everything else is a call made inside the current brief and the change freeze. Assumptions are listed at the end.

## The problem with today's layout

Plinth runs code that other people, and their AI agents, wrote. Today that code runs on `<name>.plinth.example`, which is the same site (same registrable domain) as `app.plinth.example`. The sign-in session also lives on `plinth.example` and is shared with every subdomain. So the browser treats every published app as a trusted neighbour of the signed-in product:

1. **Session theft.** The session cookie is scoped to `plinth.example`, so the browser attaches it to every `<name>.plinth.example` request too. If any cookie in that session is readable from JavaScript (managed providers commonly keep the short-lived session token readable so their frontend SDK can use it), then any signed-in person who opens a published app hands their session to whoever wrote it. That gives the author the visitor's account, including the visitor's own private apps. Even if every cookie were HttpOnly, the second and third problems below would still apply.
2. **Cross-site protections do nothing.** Browsers decide whether to send `SameSite` cookies by site, not by host. A published app is same-site with `app.plinth.example`, so `SameSite=Lax/Strict` does not stop a published app from sending forged requests (CSRF) to the product's API or framing the product for clickjacking.
3. **Cookie tossing.** Any published app can set a `Domain=plinth.example` cookie. Browsers then send that cookie to `app.plinth.example`. A published app can use this to log a visitor into the attacker's session, shadow the provider's cookies, or break sign-in for that visitor.
4. **Origin storage outlives ownership.** `localStorage`, IndexedDB, caches and service workers belong to the origin `https://<name>.plinth.example`, not to an owner. If a name is released and someone else claims it, the new owner can read every earlier visitor's data. A service worker can also keep serving content after the app is changed, made private, or taken down.
5. **Look-alike names.** `<name>` is chosen by users. Names like `app`, `login`, `accounts` or `clerk` would sit next to real product and auth hosts. Some auth providers also need their own subdomains (for example a frontend API host), and a published app must never be able to claim one.

What is safe today: different apps don't share `localStorage` with each other or with the product, because each app has its own origin. Problems 1–3 come from sharing a *site*, and problems 4–5 come from user-chosen *names*.

The proper fix is to serve user code from a separate registrable domain that is on the Public Suffix List. The freeze rules that out for the beta: it needs a new domain, a new zone and new certificates, and getting onto the list takes weeks or more and then waits on browser releases. A second level such as `<name>.apps.plinth.example` is ruled out too: it needs a new certificate (a wildcard only covers one level), and it gives up the short address the brief says people come for. So the beta keeps `<name>.plinth.example` and closes the holes on the edge and in the auth settings.

## Beta layout (ships inside the freeze)

No new domains, DNS zones, records or certificates. Every change is in edge code, product code, or auth provider settings.

| Host | Serves | Session posture |
| --- | --- | --- |
| `plinth.example` | Public site (assumed; see assumptions) | No user code, ever |
| `app.plinth.example` | Signed-in product, and the only place sign-in happens | Holds the user's session |
| `<name>.plinth.example` | One published app per name, files streamed by the edge | Never sees the user's session. Private apps use a per-app access cookie (below) |
| Reserved names | Product, auth provider, and future role hosts | Not claimable |

### 1. Keep the session off app hosts — **Owner decision**

The brief says sign-in "keeps the session on `plinth.example` and shares it across subdomains". This plan recommends changing that: **the session should only be valid on `app.plinth.example`**, which means narrowing the provider's session cookies to that host, or to the narrowest scope the provider supports. Today the only thing that uses the shared session outside the product is the private-app check, and section 2 replaces it.

This is a production auth setting, so it needs the owner's sign-off. It also has to be confirmed with the provider: some providers fix the session cookie at the registrable domain for production instances. If the provider can't narrow it, see "If the session can't be narrowed" below.

### 2. Private apps use a per-app access cookie

The edge stops reading the product session. Instead:

1. A visitor without access requests `https://<name>.plinth.example/...`. The edge redirects them to `https://app.plinth.example/open/<name>?return=<path>`.
2. `app.plinth.example` checks the session (signing the visitor in at `/auth` if needed, then bringing them back) and checks that they're invited to that app. If they are, it redirects to `https://<name>.plinth.example/__plinth/callback?code=<code>&return=<path>`. The code is one-time use, bound to that app name, and expires within 60 seconds.
3. The edge exchanges the code server-side, then sets `__Host-plinth_access`: `Secure; HttpOnly; SameSite=Lax; Path=/`, with no `Domain` attribute. The cookie holds a signed token naming the visitor, the app and an expiry (assumed 1 hour). The edge verifies it on every request. If it has expired, navigations go back through step 1 and sub-resource requests get a 401.

Why it's built this way: the `__Host-` prefix means a cookie set by a sibling app can't overwrite or shadow it. HttpOnly means the app's own JavaScript can't read it. A token for one app opens nothing else. `return` must be validated as a same-origin relative path, or this becomes an open redirect. Removing someone's invitation takes effect within the token lifetime. The membership check runs again at every code exchange.

### 3. The edge owns a few things on every app host

- **Reserved path.** `/__plinth/*` is answered by the edge and never served from user files.
- **Edge-set headers.** Users can't set response headers. `Content-Type` comes from an allowlist of file extensions, `X-Content-Type-Options: nosniff` is always sent, and the edge never sends `Set-Cookie` except its own `__Host-plinth_access`.
- **Request cookies.** The edge removes every incoming `Cookie` value except `__Host-plinth_access` before doing anything else, so the edge ignores tossed or leaked cookies.
- **No service workers during the beta.** The edge refuses any request with the `Service-Worker: script` header, so no app can register one. This stops apps from outliving takedowns and from intercepting `/__plinth/callback`. It can be lifted once apps move to their own domain (or earlier, with a takedown path that returns 404 for the worker script).
- **Caching.** Private apps get `Cache-Control: private, no-store`. Public apps can be cached at the edge, but the cache must be purged when an app is published, made private or taken down.

### 4. Harden `app.plinth.example` against its same-site neighbours

Assume every published app is a hostile page on the same site.

- **CSRF.** Every state-changing request must carry an `Origin` that exactly matches `https://app.plinth.example`, or a CSRF token. Don't rely on `SameSite`.
- **CORS.** Never allow `*.plinth.example`, a suffix match, or a reflected origin. Allow exact origins only.
- **Framing.** Send `Content-Security-Policy: frame-ancestors 'self'` on every response. The public site on the apex should do the same.
- **Own cookies.** Product-owned cookies use the `__Host-` prefix.
- **Provider cookies.** Test sign-in after a sibling host has set a `Domain=plinth.example` cookie with the same name as each provider cookie. Record how the provider behaves.

### 5. Names

- **Format.** Lowercase `a-z`, `0-9` and `-`, 3–40 characters, no leading or trailing hyphen, no `--` in positions 3–4 (this blocks `xn--` punycode, so no look-alike Unicode names during the beta).
- **Reserved, not claimable.** Every label that already has a DNS record. Every host the auth provider needs (for example `clerk`, `accounts`). Plus `app`, `www`, `api`, `admin`, `auth`, `login`, `signin`, `signup`, `sso`, `oauth`, `account`, `billing`, `pay`, `security`, `status`, `docs`, `help`, `support`, `blog`, `mail`, `email`, `smtp`, `cdn`, `static`, `assets`, `files`, `dashboard`, `portal`, `preview`, `staging`, `dev`, `test`, `internal`, `plinth`. Keep the list in code next to the name validator and check it against the DNS zone in CI or at deploy time.
- **Never reassigned.** A deleted or renamed app leaves a tombstone, and the name stays unclaimable. A tombstoned name returns 410 with `Clear-Site-Data: "cache", "storage"`, so returning visitors' browsers drop the old origin's data.
- Moderation of misleading names (`paypal-login`, etc.) is out of scope here. It should be part of abuse handling.

### If the session can't be narrowed

If the provider can't keep the session off `<name>.plinth.example` during the freeze, problems 1 and 3 stay open. The plan can't close them while also keeping both shared-domain sign-in and `localStorage` working. The options, all **Owner decision**:

- **(a) Restrict who can publish** during the beta to vetted publishers, and accept the risk for that group. Recommended if (1) can't be done.
- **(b) Sandbox app documents.** The edge sends `Content-Security-Policy: sandbox allow-scripts allow-forms allow-popups allow-modals` (without `allow-same-origin`). App JavaScript then can't read or set any cookie, but `localStorage` throws and same-host `fetch` needs CORS. That breaks the typical app the brief describes, so this only makes sense as a temporary measure.
- **(c) Delay the beta** until apps move to their own domain.

## After the freeze: the target layout

Move published apps to their own registrable domain, put it on the Public Suffix List, and keep the addresses short: `<name>.<short-user-domain>`. Then each app is its own site, `SameSite` and cookie scoping work as designed, and the hardening in sections 2–4 becomes a second layer of defence instead of the only one. The other shape, putting `plinth.example` on the list and moving the product and session to another domain, keeps the brand on app addresses but moves sign-in and every product URL. That's an owner call about the brand. Either way:

- **Plan it now.** Choose the domain and submit to the Public Suffix List as soon as the freeze allows. The submission is the slow step.
- **Moving later costs visitors' data.** Changing origin strands every visitor's `localStorage` from the beta. Every week on `plinth.example` adds data that has to be moved. The move needs a one-time bridge: a page on the old origin reads its storage and `postMessage`s it to the new origin, where the app's storage is imported, followed by permanent redirects that keep path and query. If the owner can get a freeze exception for registering one domain, the cheapest time to switch is before the beta opens.
- **Same staging pattern.** Staging hosts for app serving follow the `preview.` pattern once certificates can be issued again. The beta adds none.

## Assumptions

- The apex `plinth.example` serves the public site, or nothing. In either case it never serves user code.
- A wildcard certificate and wildcard DNS for `*.plinth.example` already exist, because apps are served that way today. More specific records (`app`, provider hosts) take precedence over the wildcard, and the edge also refuses reserved names.
- At least one provider session cookie on `plinth.example` may be readable by JavaScript. This hasn't been checked against the production instance. Check it first: if every cookie is HttpOnly, problem 1 is less severe but problems 2–3 remain, and section 1 is still recommended.
- The private-app access token lasts 1 hour and the code lasts 60 seconds. Both are guesses to adjust.
- Blocking service workers during the beta is acceptable for "small web apps". If some beta apps need offline support, revisit.
- Changing the session cookie scope counts as a production auth change, not "infrastructure" under the freeze. If the owner disagrees, the fallback options apply.
- No code exists in `apps/` or `packages/` yet, so this plan changes no code. It describes what the edge, the product and the auth settings must do.

````

> Result: File created successfully at: <run>\builds\4-user-code-on-own-domain-old-opus2\work\docs\hosting-plan.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the plan to `docs/hosting-plan.md`. It's a document only (`apps/` and `packages/` are empty, so no code changed) and it isn't committed.

**The main finding:** the current setup isn't safe to open as-is. People's apps run on `<name>.plinth.example`, which browsers treat as the same site as `app.plinth.example`, and the sign-in session is shared across every subdomain. So any published app can:
- **Take over visitors' accounts.** If any session cookie is readable from JavaScript (I haven't checked), every signed-in visitor gives their session to the app's author.
- **Act on the product as the visitor.** It can send forged requests to `app.plinth.example`; `SameSite` cookie settings don't block this between same-site hosts.
- **Plant cookies across the whole domain.** These can break or hijack sign-in.

On top of that, a released name that gets reclaimed gives the new owner earlier visitors' `localStorage`.

The proper fix is a separate domain for user apps, listed on the Public Suffix List. The freeze rules that out, so the plan keeps the short `<name>.plinth.example` addresses and makes these calls:
- **Session stays on `app.plinth.example` only.** This needs your sign-off.
- **Private apps stop reading the session.** Instead, a quick redirect through `app.plinth.example` checks the visitor is invited, then gives them an access cookie for that one app only, which the app's own JavaScript can't read.
- **The edge controls headers and cookies.** Users can't set response headers, and the edge drops incoming cookies other than its own access cookie.
- **No service workers during the beta.** This stops apps from outliving takedowns.
- **`app.plinth.example` treats published apps as hostile.** It checks the exact `Origin` on every change, allows only exact CORS origins, and refuses to be framed.
- **Name rules.** Reserved names (including the auth provider's hosts), no look-alike Unicode names, and names are never reassigned.

**Decisions for you:**
1. **Session scope.** The brief says the session is shared across subdomains; I'm recommending limiting it to `app.plinth.example`. I treated this as an auth setting rather than infrastructure under the freeze. It still needs confirming with the provider.
2. **If the provider can't narrow the session:** restrict publishing to vetted people during the beta (my recommendation), sandbox apps (this breaks `localStorage`), or delay the beta.
3. **Move to a separate domain early if you can.** Every week on `plinth.example` adds visitor data tied to these addresses, and that data has to be carried over when apps move. If you can get a freeze exception to register one domain, before the beta is the cheapest time. Otherwise, submit to the Public Suffix List as soon as the freeze ends, because that's the slow step.

**What I assumed** (all listed at the end of the doc):
- The root `plinth.example` serves the public site.
- The `*.plinth.example` wildcard certificate already exists.
- The private-app access cookie lasts 1 hour and the sign-in code 60 seconds; both are guesses to adjust.
- Small beta apps don't need offline support, so blocking service workers is acceptable.

The first thing to check is whether the production session cookie can be read by JavaScript. That decides how urgent the account-takeover risk is.

**Session ended:** success, 7 turns, 145885 ms
