I've written the plan to `docs/hosting-plan.md`. I haven't committed it.

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