I wrote the plan to `docs/hosting-plan.md`. It found a security problem that has to be handled before the beta opens. Nothing is committed, and I didn't change `docs/hosting.md` or `docs/brief.md`.

**The problem:** the code people publish runs on `<name>.plinth.example`, under the same domain as the signed-in product and the shared sign-in session. To the browser, every user's app and `app.plinth.example` count as one site. So:
- The session is sent to every app.
- If any session cookie can be read by JavaScript, an app's author could take over the account of anyone who opens their app.
- Apps can plant cookies the product will read.
- Browser protections based on same-site cookies (`SameSite`) don't stop apps from sending requests to the product.
- Private apps depend on the edge reading that shared session on app hosts.

**What fits inside the freeze** (no new domains, DNS or certificates; we keep `<name>.plinth.example`):
- **Sign-in session:** only `app.plinth.example` gets the session. It's no longer shared across subdomains.
- **Private apps:** instead of the edge reading the session, `app.plinth.example` checks the invite and issues a one-time code. The edge swaps that code for a sign-in cookie that only works on that one app.
- **Product hardening:** `app.plinth.example` checks exactly where each request comes from and only allows exact host names. It also can't be embedded in a frame by an app.
- **App names:** some names are reserved, and a deleted name is never given to someone else. A visitor's saved data, background scripts and permissions stay tied to the name, so a new owner would inherit them.
- **What the edge serves:** it sets content types and headers itself, so files people upload can't. It also never logs cookies.

**One decision is yours** (section 7). The real fix is a separate domain for people's apps, and the freeze blocks that. Moving later costs a lot: each app's saved browser data stays tied to the old address, so visitors would lose it. My recommendation:
- **First choice:** get a freeze exception for one domain and one wildcard certificate, and launch apps on it.
- **Otherwise:** ship on `plinth.example` with the fixes above, and tell beta users that app addresses and saved data may not carry over after the beta.

**Hard stop:** if the auth provider sets a session cookie on `plinth.example` that JavaScript can read, and the provider can't limit it to `app.plinth.example`, we shouldn't let people publish public apps in the beta. This is the first item on the pre-beta checklist, and it means looking at the real production cookies.

**What I assumed:**
- A wildcard certificate already covers the app addresses.
- Changing the auth provider's settings and the edge code doesn't count as infrastructure under the freeze. If it does, the session change needs an exception too.
- Apps are static files only.
- `app.plinth.example` is the only signed-in part of the product.
- Staging for apps waits until the freeze ends.
- The endpoint names, cookie names and timeouts are proposals and can change.