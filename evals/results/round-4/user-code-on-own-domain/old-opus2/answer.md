I wrote the plan to `docs/hosting-plan.md`. It's a document only (`apps/` and `packages/` are empty, so no code changed) and it isn't committed.

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