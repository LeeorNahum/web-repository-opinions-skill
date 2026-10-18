**Prompt:** Before the beta opens, review how we serve people's apps (docs/hosting.md) and write the hosting and origin layout we should ship to docs/hosting-plan.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-user-code-on-own-domain-new-opus/work\" && git ls-files && cat docs/brief.md docs/hosting.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5351 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-user-code-on-own-domain-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat domains.md origins.md auth.md object-storage.md"}`

> Result: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 27019 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-user-code-on-own-domain-new-opus/work/.claude/skills/web-repository-opinions/references\" && grep -n -i -B2 -A8 \"frame\\|users wrote\\|user-supplied\\|usercontent\" social-metadata.md seo.md public-discovery.md abuse-resistance.md dns.md http-apis.md | head -150"}`

> Result: social-metadata.md-5-## Favicon social-metadata.md-6- social-metadata.md:7:Every surface ships a favicon. Set it deliberately rather than leaving the framework default. social-metadata.md-8- social-metadata.md-9-First check whether a brand icon already exists in the repo or brand source, and reuse it. Prefer SVG, which scales cleanly, and pair it with a generated raster fallback, because search en [... 5236 more characters]

**Tool call `Write`:** `<run>/builds/2-user-code-on-own-domain-new-opus/work/docs/hosting-plan.md`

````text
# Hosting and origin plan for the beta

Status: proposal written while the owner was away (2026-10-18). Sources: `docs/brief.md` (decisions) and `docs/hosting.md` (how apps are served today). Calls I made on my own, and what I assumed to make them, are marked **Decision** and **Assumption**, and they're collected again at the end for review.

## The problem with how apps are served today

User code currently runs as the top-level document on `<name>.plinth.example`. That host is a subdomain of the domain that holds our sign-in session. A browser treats every HTTPS subdomain of `plinth.example` as the same site, so any app anyone publishes runs inside our trust boundary:

- **Session theft.** The auth provider keeps its session cookie on `plinth.example` and shares it across subdomains, so that cookie goes to every app host. If the cookie can be read by JavaScript (managed providers often leave the short-lived session token readable, because their front-end SDKs need it), a script in any published app can read `document.cookie` and send away the session of every signed-in visitor. Even if the cookie is `HttpOnly`, the same-site problems below still apply.
- **Cookie tossing and session fixation.** Script on `evil.plinth.example` can set a cookie with `Domain=plinth.example`. That can sign a visitor into the attacker's account on `app.plinth.example`, or mess with the private-app check at the edge.
- **Same-site requests.** A request from an app to `app.plinth.example` counts as same-site, so it carries `SameSite=Lax`/`Strict` cookies. That leaves our CSRF defences resting on the `SameSite` attribute alone.
- **Private apps make it worse.** The edge checks the session cookie before serving a private app, so the session reaches exactly the host where untrusted code runs.

This has to be fixed before the beta opens, because the beta is when strangers start publishing and visiting apps.

The proper fix is to serve user code from a separate registrable domain, framed by the short address. The change freeze rules that out until the beta ends ("no new domains, DNS zones, or certificates"). So the plan has two stages:

1. **Beta (inside the freeze):** keep `<name>.plinth.example`, but make user code run in an **opaque origin**. A product-owned shell page sits at the short address, and a storage bridge keeps `localStorage` apps working. This needs no new domains, DNS records, or certificates. It's only edge behavior and front-end code.
2. **After the freeze:** move user bytes to a dedicated content domain that the same shell frames. Visitors still see `<name>.plinth.example`.

## Host layout

| Host | Serves | Notes |
| --- | --- | --- |
| `plinth.example` | Public site | Assumption: the apex holds the public site, as the brief doesn't say otherwise. No `www`. If it exists, it redirects to the apex at the edge, keeping path and query. |
| `app.plinth.example` | Signed-in product | Unchanged. Sign-in lives at `/auth` here. |
| Auth provider's own subdomain(s) | Provider front-end API | Whatever exists today stays as it is. |
| `<name>.plinth.example` | **The app shell (our code)** plus user bytes under one reserved path | Keeps the short address the brief promises. |
| `<name>.<content-domain>` | User bytes, after the freeze | Not created until the freeze ends. See stage 2. |

### Reserved app names

**Decision:** app names come from a namespace that also holds our own hosts, so the name validator rejects a reserved list. Without it, someone could publish an app at `app`, `auth`, `login` or similar and serve a convincing fake of our sign-in page from our own domain. The list:

`app`, `www`, `api`, `auth`, `login`, `signin`, `account`, `accounts`, `admin`, `dashboard`, `preview`, `staging`, `dev`, `mail`, `status`, `docs`, `help`, `support`, `billing`, `cdn`, `static`, `assets`, `clerk`, `clkmail`, the auth provider's own subdomain names, and every hostname that already has an explicit DNS record.

The list is a code constant, not env. Before beta, check that no existing app holds one of these names. If one does, it's an owner decision.

## Stage 1 (beta): opaque-origin serving under the short address

### Request shape

Every path on `<name>.plinth.example` is the **shell**, except one reserved prefix:

```text
https://<name>.plinth.example/<any path>             -> shell (our HTML), frames that path
https://<name>.plinth.example/__plinth/c/<grant>/... -> the person's files (user bytes)
```

- `<grant>` is the published version ID for public apps. That gives each version immutable, cacheable URLs.
- For private apps, `<grant>` is a short-lived signed grant bound to app, version and viewer (see "Private apps" below).
- **Decision:** user files can't use the `/__plinth/` path themselves. Publishing rejects it, or the shell simply shadows it.

### The shell

The shell is a small, static page that we write. Its job:

- Load the app's `index.html`, or whichever path was requested, from the user-bytes prefix, and render it in an iframe as `srcdoc`, with `sandbox="allow-scripts allow-forms allow-popups allow-modals allow-downloads"`. The list never includes `allow-same-origin`, and also leaves out `allow-top-navigation`. Before rendering, the shell adds two things to the top of the document:
  - a `<base href>` pointing at the user-bytes prefix, so relative URLs keep working;
  - an inline storage shim (below) seeded with the app's current storage.
- Own the tab title, favicon and link-preview tags. Derive them on the server from the app's `<head>` at publish time, so link expanders read them from the first HTML. Private apps answer unauthorized requests, link expanders included, with a fallback that shows none of the content.
- Mirror navigation inside the frame into the address bar via `postMessage`, so deep links stay linkable. This can follow later in the beta. It's not a launch blocker.
- Run under its own strict CSP. The shell is our code on a host that receives the session cookie, so it must stay tiny and have no injection surface.

### User-bytes responses

The edge applies these headers at **one choke point** that every response of user bytes passes through:

- `Content-Security-Policy: sandbox allow-scripts allow-forms allow-popups allow-modals allow-downloads`. This is the enforced header, not report-only, and never with `allow-same-origin`. It sits on every response, not only HTML, so that opening any file directly as a top-level document (an `.html` under another name, an SVG, a misnamed file) still gets an opaque origin.
- `X-Content-Type-Options: nosniff`, with a content type from an allowlist derived from the file extension.
- `X-Robots-Tag: noindex`. The shell URL is the canonical one.
- `Referrer-Policy: no-referrer`, so a private grant in the path doesn't leak through `Referer`.
- No `Set-Cookie`, ever. Any `Set-Cookie` coming from upstream is stripped.

With an opaque origin, user code can't read or write `document.cookie`, can't reach our session, and can't set parent-domain cookies. Its requests to our hosts are treated as cross-site.

### Keeping `localStorage` apps working

An opaque origin has no `localStorage`, `sessionStorage`, IndexedDB, cookies or service workers. Apps that "often use `localStorage`" would break without help, so the shell provides a bridge:

- Each app's storage lives in the **shell's** `localStorage`. The shell is on `<name>.plinth.example`, so each app still gets its own isolated storage, as it does today.
- The injected shim replaces `window.localStorage` (and `sessionStorage`, in memory) with an object that implements the `Storage` interface. The shim starts out with the snapshot the shell inlined, so reads stay synchronous. Writes update the in-memory copy at once and are sent to the shell with `postMessage`.
- The shell accepts storage messages only when `event.source` is its own iframe's `contentWindow`. It doesn't check `origin`, which is `"null"` here. The shell persists only that app's keys, and it handles storage writes and navigation messages and nothing else.
- **Limits that remain:** storage syncs across tabs only through the shell (it listens to `storage` events and forwards them), the quota is the shell origin's usual ~5 MB, and IndexedDB and service workers aren't available. These limits go into the publish docs and the agent-facing guidance as beta limitations.
- **Migration:** apps already published today have data in their real `<name>.plinth.example` origin. That's the same origin the shell now runs on, so the shell finds the existing keys in its own `localStorage` and seeds them into the frame. Nothing gets lost. I'm assuming apps use plain keys. If we want to keep shell-internal keys apart, the shell namespaces its own keys and leaves the app's keys raw.

### Private apps

Requests from inside the sandboxed frame are cross-site, so the session cookie (usually `SameSite=Lax`) won't come with subresource requests. The private check therefore splits in two:

1. The shell request is a top-level navigation and carries the session as usual. The edge checks that the session belongs to an invited person, as it does today. If it doesn't, the edge returns the fallback with no content, or sends the visitor to `/auth` on `app.plinth.example` with a validated return path, so they land back on the app.
2. On success, the edge puts a signed grant (app ID, version, viewer pseudonym, expiry) into the shell's HTML. The shell uses `/__plinth/c/<grant>/` as the base. The edge validates the grant on every user-bytes request, with no cookie needed.

**Decision:** grants last 12 hours, and every shell load issues a fresh one. If someone leaks a grant, the exposure is that version of that app for at most 12 hours. That's less than what an invited viewer could already share by copying the files.

### Release gates before the beta opens

These checks run against the deployed edge, not just in unit tests:

- Load a test app that tries to read `document.cookie`, set a `Domain=plinth.example` cookie, call `fetch` with credentials against `app.plinth.example`, and touch `top.location`. Each attempt must fail or carry no session, in Chromium, Firefox and Safari.
- Open a user `.html`, `.svg` and `.txt` file directly as top-level documents. Each must show `self.origin === "null"`.
- Check that a `localStorage` counter app keeps its value across reloads, and that an app published before this change keeps its existing data.
- Load a private app as an invited viewer, as a viewer who isn't invited, and signed out. Repeat with an expired grant, and with a grant for another app or version.
- Try to publish a reserved name and a file under `/__plinth/`. Both must be rejected.
- Fetch a public app and a private app with a link expander and check the preview each one shows.

## Stage 2 (after the freeze): dedicated content domain

As soon as the freeze lifts:

- Register a separate registrable domain only for user bytes, for example `plinthusercontent.example`. The owner picks the name. Serve each app at `<name>.<content-domain>`, so each app has its own real origin.
- The shell on `<name>.plinth.example` frames `https://<name>.<content-domain>/` instead of `srcdoc`. Visitors still see the short address. Drop `allow-same-origin`'s absence only on the content domain: there the frame gets a real origin with real browser storage, and our session can't reach it.
- Send top-level navigations straight to the content domain (`Sec-Fetch-Dest: document`) back to the shell URL. Keep the content domain `noindex`. Browsers partition framed storage by top-level site, so the storage an app sees stays the same only if it's always framed by the shell.
- Migrate storage once: the shell hands the bridged keys to the new frame, the frame writes them into its real `localStorage`, and then the bridge is removed.
- Apply for the content domain's spot in the private section of the Public Suffix List once it meets the criteria. Rely on it only after browsers ship the entry. Until then, any cookie we set there is host-only with the `__Host-` prefix.
- If an app's code ever needs to know who its viewer is, give it a pseudonym derived per app on the server. It never gets a Plinth user ID or email.
- Staging for apps (`<name>.preview.<content-domain>` and a matching preview shell host) is set up at the same time. It needs certificates the freeze doesn't allow today.

## What I assumed

- **Assumption:** edge code and response headers can still be deployed during the freeze. Only new domains, DNS zones and certificates are frozen. If edge deploys are frozen too, stage 1 can't ship, and the beta should open only after the owner accepts the session-theft risk explicitly, in writing.
- **Assumption:** a wildcard certificate and DNS record for `*.plinth.example` already exist (today's serving implies they do). Stage 1 adds none.
- **Assumption:** the apex `plinth.example` holds the public site and `www` doesn't serve content. The brief is silent on both.
- **Assumption:** "short addresses" means the URL visitors see and share. The bytes moving under a reserved path (stage 1), or to another domain (stage 2), doesn't break that promise.
- **Assumption:** apps don't depend on IndexedDB, service workers, cookies or `document.domain`. Any that do will break in stage 1 and need to be found before beta (scan the published files for those APIs).
- **Decision:** I kept the provider's session on `plinth.example` as the brief decides. Making it host-only on `app.plinth.example` would shrink the exposure, but the same-site and cookie-tossing problems remain, and the edge's private-app check needs the cookie on app hosts. Isolating user code fixes the actual cause.
- **Decision:** no app staging host during the freeze, because `*.preview.plinth.example` would need a new certificate.

## Questions for the owner

1. Is the plan acceptable as beta scope, given that stage 1 adds the shell, the bridge and private grants to the beta's critical path? If it can't be ready, the alternative is to delay the beta, not to open it with user code sharing our session's site.
2. The name of the content domain for stage 2.
3. Whether any existing app holds a name on the reserved list.
4. Whether an exception to the freeze for one new domain and certificate is possible. It would let us skip the stage 1 storage bridge.

````

> Result: File created successfully at: <run>/builds/2-user-code-on-own-domain-new-opus/work/docs/hosting-plan.md (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `<run>/builds/2-user-code-on-own-domain-new-opus/work/docs/hosting-plan.md`

Replaced:

````text
Visitors still see the short address. Drop `allow-same-origin`'s absence only on the content domain: there the frame gets a real origin with real browser storage, and our session can't reach it.
````

With:

````text
Visitors still see the short address. Only on the content domain can the frame's sandbox add `allow-same-origin`: the content domain is a separate site from our session, so the frame gets a real origin with real browser storage and our session still can't reach it.
````

> Result: The file <run>/builds/2-user-code-on-own-domain-new-opus/work/docs/hosting-plan.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** I've written the plan to `docs/hosting-plan.md`. I haven't committed it.

**The main finding is a security problem that should block the beta.** People's apps run as the main page on `<name>.plinth.example`, and the sign-in session is shared across every subdomain of `plinth.example`. To the browser, that puts every app on the same site as `app.plinth.example`. As a result:
- **Stolen sign-ins:** if the provider's session cookie can be read by scripts (common with managed providers), any published app can take the session of every signed-in person who visits it.
- **Planted cookies:** any app can set cookies across the whole domain, which can sign a visitor into the wrong account.
- **Private apps:** the edge checks the session on the same host where untrusted code runs, so the session goes exactly where it shouldn't.

The right fix is to serve people's code from a separate domain, but the change freeze rules out new domains until the beta ends. So the plan has two stages:

1. **Beta (inside the freeze):**
   - **Shell:** every path on `<name>.plinth.example` serves a small page we write.
   - **Isolation:** that page loads the person's files in an iframe that browsers treat as belonging to no site. The same header goes on every file response, so a file opened directly is isolated too. User code can't read or set cookies or get at the session.
   - **`localStorage`:** a small bridge keeps saved data working. Each app's data lives in the shell page's own storage, so data in already-published apps carries over.
   - **Private apps:** the session is checked when the page loads, and the files are then served through a signed link that lasts 12 hours.
   - **Reserved names:** names like `app`, `auth` and `login` can't be used for apps, so nobody can fake our sign-in page on our own domain.
   - **Short addresses:** visitors still see `<name>.plinth.example`.
2. **After the freeze:** move the files to a separate content domain that the same shell page loads in its frame, and drop the storage bridge. The plan also covers the one-time data move and adding that domain to the Public Suffix List (the list browsers use to treat each subdomain as its own site).

**Assumptions to check** (all listed in the doc):
- **Edge deploys:** changes to edge code and headers are still allowed during the freeze; only domains, DNS and certificates are frozen. If edge changes are frozen too, stage 1 can't ship.
- **Certificate:** a wildcard certificate for `*.plinth.example` already exists.
- **Apex:** `plinth.example` holds the public site, and `www` serves nothing.
- **Browser features:** published apps don't rely on IndexedDB, service workers or cookies, which won't work in the isolated frame. We should check this by scanning the published files.
- **Session:** I kept the provider's session on `plinth.example`, as the brief decides. Isolating user code fixes the actual cause; moving the session alone wouldn't.
- **Staging:** no staging host for apps during the freeze, since it would need a new certificate.

**Decisions for you:**
- **Beta timing:** is stage 1 acceptable as beta scope? If it can't be ready next week, I recommend delaying the beta rather than opening with apps on the same site as the sign-in session.
- **Freeze exception:** could one new domain and certificate be allowed? That would let us skip the storage bridge.
- **Content domain name** for stage 2.
- **Reserved names:** does any existing app already use one of them?

**Session ended:** success, 8 turns, 166107 ms
