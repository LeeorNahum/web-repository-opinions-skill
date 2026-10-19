**Prompt:** Before the beta opens, review how we serve people's apps (docs/hosting.md) and write the hosting and origin layout we should ship to docs/hosting-plan.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work\" && git ls-files && cat docs/*.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5351 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat domains.md origins.md object-storage.md"}`

> Result: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 13095 more characters]

**Tool call `Grep`:** `{"pattern": "(?i)user.?content|untrusted|public suffix|registrable|sandbox|cookie", "output_mode": "content", "path": "C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work/.claude/skills/web-repository-opinions"}`

> Result: continuous-integration.md:10:- Use read-only workflow permissions by default. Grant release writes only to the release job, and keep secrets out of untrusted pull-request execution. legal-pages.md:12:- Provide a privacy policy at `/privacy` when the product, or a service acting for it, collects anything that can be tied to a person, or when a provider it uses requires one. Analytics, forms, cookie [... 1549 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat auth.md dns.md http-apis.md | head -250"}`

> Result: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 15170 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work\" && cat package.json pnpm-workspace.yaml; git log --stat -3 | head -40"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*" commit 07a716a38ddd8588380f8292165e51870cf23f6d Author: eval <eval@example.inva [... 2226 more characters]

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work/docs/hosting-plan.md`

````text
# Hosting and origin plan

Status: proposal written while the owner was away. One decision is still open for the owner (see "Owner decision needed"). Everything else is a call made here, and the reasons are written down so it can be overruled.

Inputs: `docs/brief.md` (decided), `docs/hosting.md` (current state and freeze).

## The problem with how apps are served today

Plinth serves code that it did not write and does not review. People and their AI agents write it. That code runs as the top-level document on `<name>.plinth.example`. These three facts together are an account-takeover hole:

1. **The product session is visible to every app.** The brief says the auth provider keeps the session on `plinth.example` and shares it across subdomains, and private apps check that same cookie at the edge, so the cookie definitely reaches app hosts. Managed providers usually keep the short-lived session token in a cookie that JavaScript can read, so it can work client-side. If that is true here, any app's script can read `document.cookie` and send the token somewhere else. That token can then call `app.plinth.example` and its backend as the visitor. Every signed-in person who opens any app is exposed, including the people invited to private apps.
2. **Same-site does not protect us.** Every `<name>.plinth.example` is *same-site* with `app.plinth.example`. `SameSite` cookies are still sent on requests from an app to the product, so a CSRF defence based on SameSite does nothing here. If the provider's frontend API accepts any subdomain of the instance domain as an allowed origin, an app's script may be able to mint fresh session tokens directly.
3. **Apps can plant cookies on the whole domain (cookie tossing).** Any app can set `Domain=plinth.example` cookies. These can shadow or fix the product's own cookies and break or hijack sign-in.

Also, because `plinth.example` is one registrable domain:

- **One bad app can block the whole domain.** If Safe Browsing or a corporate filter flags a phishing app, it can block `plinth.example` as a whole, including `app.` and sign-in.
- **App names can be used for phishing.** An app named `login`, `accounts`, or `app-plinth` looks like ours.

What is already right and must be kept: each app has **its own origin**. That keeps `localStorage`, IndexedDB, and service workers isolated between apps without extra work. Never move apps onto paths under one shared host.

## Target layout (what we should ship)

The rule: **user code and Plinth's credentials never share a registrable domain.** The brief says short addresses are the main reason people choose Plinth, so the short addresses stay. The signed-in product and its auth move instead.

| Surface | Host | Notes |
| --- | --- | --- |
| User apps | `<name>.plinth.example` | Unchanged for users. One origin per app. No Plinth credentials on this domain. |
| Apex | `plinth.example` | Permanent redirect (path and query kept) to the product's public site. No cookies. |
| Public site | `<product-domain>` | Apex of the new domain. |
| Signed-in product | `app.<product-domain>` | Replaces `app.plinth.example`. Old host redirects here permanently. |
| Auth provider frontend | provider's CNAMEs on `<product-domain>` | Production instance moved to the new domain. The session is shared across `<product-domain>` only. |
| Staging | `preview.<product-domain>`, `preview.app.<product-domain>`, apps on `<name>.preview-plinth.example` or a second app domain | Settled after the freeze. Needs certificates. |

`<product-domain>` is a placeholder. Choosing it is the owner's call.

After the move, put `plinth.example` on the Public Suffix List. Each app then becomes its own *site*. Apps can no longer plant cookies on each other, SameSite starts to hold between apps, and reputation systems judge each app separately. PSL inclusion needs a `_psl` TXT record and takes a long time to reach browsers, which pick it up in their releases over weeks to months. Treat it as hardening that follows the move. The move does not depend on it.

### Private apps without the product session

The edge stops reading the provider session cookie on app hosts. Instead it uses a per-app access grant:

1. A visitor opens private `<name>.plinth.example/some/path`. If there is no valid grant, the edge redirects to a single authorization route on the product: `app.<product-domain>/apps/<appId>/open?return=/some/path`.
2. The product checks the visitor's session and whether they are invited. That check uses the product's one authorization gate. If they are allowed, the product redirects to `<name>.plinth.example/__plinth/grant?ticket=…`. The ticket is single-use, short-lived (about 60 s), and signed. It is bound to that app and that person.
3. The edge redeems the ticket and sets a `__Host-plinth_grant` cookie with `Secure; HttpOnly; Path=/; SameSite=Lax`, no `Domain`, and a lifetime of hours, not weeks. Then it redirects to the validated relative `return` path.
4. On each request the edge checks the grant's signature and expiry. On a short interval it re-checks that the app is still private and the person is still invited, so revoking access takes effect within that interval.

Why it is shaped like this: app JavaScript cannot read the grant (`HttpOnly`). Sibling apps cannot overwrite it (`__Host-`). Even if it leaks, it opens one app for one person for a few hours, never the account. The `return` value must be a same-origin relative path, or the flow becomes an open redirect. Reserve `/__plinth/` on every app host so no app file can be served from it.

### Edge rules for app hosts

- Strip the `Cookie` header before any logging or storage lookup. Only the edge's own `__Host-plinth_grant` is read.
- Never send `Set-Cookie` from user content. Only `/__plinth/grant` sets cookies.
- Add `Origin-Agent-Cluster: ?1`, `X-Content-Type-Options: nosniff`, and `Referrer-Policy: strict-origin-when-cross-origin`. Do not add a restrictive CSP to user HTML, because their code is theirs to run.
- Look up the content type from Plinth's own allowlist by file extension. Never take the content type from the uploader.
- Only names that resolve to an existing app are served. Unknown names get a Plinth-owned "no app here" page. App hosts never fall through to the product.

### Product rules (`app.<product-domain>`, and `app.plinth.example` until the move)

- Every state-changing request checks that `Origin` is **exactly** the product origin, not "same site" and not `*.plinth.example`.
- The auth provider's allowed origins are exact product hosts only. Never use a wildcard over the app domain.
- The product never embeds or fetches user content with credentials. It links to apps through `resolveUserAppOrigin(name)` (see below).

### Reserved app names

Refuse these as app names, no matter who asks: every label that has, or may get, a DNS record in the `plinth.example` zone (today at least `app`, plus the provider's frontend and mail CNAMEs such as `clerk`, `accounts`, `clkmail`), and `www`, `api`, `admin`, `auth`, `login`, `signin`, `signup`, `account`, `billing`, `dashboard`, `portal`, `preview`, `staging`, `status`, `docs`, `help`, `support`, `security`, `mail`, `smtp`, `mta-sts`, `autodiscover`, `cdn`, `static`, `assets`, `ns1`, `ns2`. Also refuse labels starting with `xn--` (to stop lookalike Unicode names) and anything that is not a lowercase letters-digits-hyphen DNS label. Keep the list in code, next to name validation. Adding a record to the zone means adding its name to the list first.

## Origins in code

There is no app code yet. When there is, one shared package owns origin resolution as described in the skill's origins reference:

```text
CANONICAL_SITE_ORIGIN       https://<product-domain>      (https://plinth.example until the move)
CANONICAL_APP_ORIGIN        https://app.<product-domain>  (https://app.plinth.example until the move)
USER_APP_DOMAIN             plinth.example
resolveSiteOrigin() / resolveAppOrigin() / resolveUserAppOrigin(name) / absoluteUrl(path, origin)
```

`resolveUserAppOrigin` builds `https://<name>.<USER_APP_DOMAIN>` from a name that has already been validated. Moving the product later then only changes constants, not call sites.

## Owner decision needed: what ships for beta under the freeze

The target layout needs a new domain and certificates, and the freeze forbids both until the beta ends in about two months. No layout that stays on `plinth.example` meets all of these at once: short addresses, a product session shared on `plinth.example`, user code as a normal top-level page with `localStorage`, and no new domains or certificates. One of them has to give before the beta opens.

| Option | What gives | Effect |
| --- | --- | --- |
| **A. One freeze exception (recommended)** | The freeze: one new domain, its zone, and certificates | The target layout ships for beta. Before beta is the cheapest time to move the product host: few sessions, links, and OAuth callbacks exist yet. Afterwards every move breaks links and sign-ins people already have. |
| B. Delay beta until the freeze ends | The date | Same layout as A, about two months later. |
| C. Sandbox user code on its current hosts | How apps behave | A Plinth shell is the top-level page. The user's HTML runs in a frame served with `Content-Security-Policy: sandbox allow-scripts allow-forms allow-popups allow-modals` (no `allow-same-origin`), so it has an opaque origin and cannot see cookies. The cost: `localStorage`, IndexedDB, cookies, and service workers throw unless we build a bridge. Same-host `fetch` becomes cross-origin. The address bar stops following in-app navigation. That is a lot to build in a week, and it breaks the typical app the brief describes. |
| D. Ship as is | Safety | Any app can probably take over the account of any signed-in visitor. Not recommended, and not a call made here. |

Whichever option is chosen, the per-app grant for private apps, the edge rules, the exact-origin checks, and reserved names apply. They need no new domain, DNS zone, or certificate, so work on them can start now. They make the hole smaller but do not close it while the product session lives on `plinth.example`.

## Assumptions to verify (in this order)

1. **Look at the real production cookies** on `app.plinth.example`: name, `Domain`, `HttpOnly`. If the session token is readable by JavaScript and scoped to `plinth.example`, problem 1 is confirmed. If it turns out to be host-only and only a non-secret marker is shared, the urgency drops. Then also check how the edge validates private apps today, because a check based only on a marker cookie could be forged.
2. Find out whether the auth provider's frontend API accepts requests from arbitrary `*.plinth.example` origins.
3. The existing certificate is a single-level wildcard `*.plinth.example`. I assumed this because every app host works today. So deeper names such as `<name>.apps.plinth.example` would need a new certificate. They would not help anyway, because they are still on the same registrable domain.
4. "No new domains, DNS zones, or certificates" still allows **records** inside the existing zone (for example the PSL `_psl` TXT). I made no DNS changes.
5. Users do not reach apps through a custom domain of their own. Nothing in the docs mentions one.

## Not done here

No DNS, provider, or infrastructure changes were made, and none should be until the owner decides: production domains, OAuth callback hosts, and production DNS all need the owner's approval. `docs/brief.md` was left unchanged. If option A or B is chosen, its "signed-in product is `app.plinth.example`" line needs updating by the owner.

````

> Result: File created successfully at: C:/tmp/wro-eval3/builds/3-user-code-on-own-domain-old-opus/work/docs/hosting-plan.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the plan to `docs/hosting-plan.md`. I found a serious security problem, and fixing it before beta needs a decision from you.

**The problem:** people's own code runs on `<name>.plinth.example`, and the sign-in session is shared across all of `plinth.example`. So the code in any published app can probably read a visitor's Plinth session and act as them on `app.plinth.example`. That includes the people invited to private apps. Same-site cookie protections don't help, because every app counts as the same site as the product. Apps can also plant cookies on the whole domain. And if one phishing app gets flagged by browser blocklists, sign-in and the product can be blocked along with it.

**What I recommend shipping (target layout):**
- Your short app addresses stay exactly as they are. The signed-in product and sign-in move to a new domain instead, and `plinth.example` keeps no Plinth logins. Later, `plinth.example` goes on the Public Suffix List, the list browsers use to treat each subdomain as a separate site, so apps are cut off from each other too.
- Private apps stop reading the session at the edge. Instead, the product checks the invite and hands the visitor a pass for that one app only. App code can't read the pass, and other apps can't overwrite it. If it leaks, it opens one app for a few hours, not the account.

**Calls I made that work under the freeze:** rules for the edge, exact-origin checks in the product, a list of reserved app names (`app`, `login`, `accounts`, …), and one shared code module for building URLs. These need no new domain, DNS zone or certificate, so work can start now. They make the hole smaller, but they don't close it while the session lives on `plinth.example`.

**Decision for you:** the freeze bans the new domain and certificates the fix needs, so something has to give before beta:
- **A (my recommendation):** one freeze exception for a new domain. Moving the product before beta is the cheapest it will ever be.
- **B:** delay beta until the freeze ends, about two months.
- **C:** run app code in a locked-down frame. This breaks `localStorage` and a lot else, and it's a big build for one week.
- **D:** ship as is. I don't recommend it and didn't choose it.

**What I assumed (to check first):**
- **The cookie itself:** look at the real cookie on `app.plinth.example`. If the session token turns out not to be readable by app code, this is much less urgent.
- **The sign-in provider:** whether its frontend API accepts requests from any `*.plinth.example` origin.
- **The certificate:** that the current certificate covers only one level of subdomain.
- **DNS records:** that adding records inside the existing zone is allowed during the freeze.
- **Custom domains:** that users don't reach apps through custom domains of their own.

I made no DNS, provider or infrastructure changes and didn't edit `docs/brief.md`. If you pick A or B, its "signed-in product is `app.plinth.example`" line will need updating. I didn't commit anything.

**Session ended:** success, 9 turns, 181989 ms
