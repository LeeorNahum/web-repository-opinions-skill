I wrote the plan to `docs/hosting-plan.md`. I didn't commit it, and nothing was built or tested. The review found a serious security problem we need to fix before the beta opens.

**The problem:** people's code runs on `<name>.plinth.example`. Browsers treat that as the same site as `app.plinth.example`, and the auth provider's session is shared across all `plinth.example` subdomains. So any published app can likely read a visitor's session and take over their account. "Likely" because I assumed the session cookie is readable by page scripts, as Clerk's is; that still needs checking. Apps can also plant a cookie that signs a visitor into a different account. Private apps make it worse, because the edge needs that shared session cookie on every app host.

**What I recommend for the beta (works within the freeze):** only edge code and response headers change. The edge adds a `sandbox` security header to every response on app hosts. This cuts apps off from cookies, service workers and browser storage, and makes them count as a different site from the product. The short addresses stay. The plan also covers:
- **Private apps:** after checking the visitor's session, the edge gives them an access cookie that only that one app's address receives.
- **Product hosts:** the signed-in product and its API reject requests coming from app hosts.
- **Reserved names:** people can't claim app names like `app`, `clerk` or `accounts`.
- **Cleanup at the switch:** old service workers are removed and old app storage is cleared.

**The cost:** apps get no `localStorage` for the roughly two months of the beta. The brief says apps often rely on it, so many won't keep their state between visits. Private apps also can't load their own files with `fetch()` or ES modules without changes.

**After the freeze:** register a separate domain for people's code. The short address `<name>.plinth.example` then becomes a product page that shows the app in an iframe from the new domain, so visitors still see the short address and `localStorage` works again.

**What I assumed:**
- The freeze covers only domains, DNS and certificates; edge code and headers can still change.
- A wildcard DNS record and certificate for `*.plinth.example` already exist.
- Some apps were already served before the beta and may have registered service workers.
- The apex (`plinth.example`) serves the public site.
- Losing `localStorage` for the beta is acceptable compared with the account-takeover risk.

**Decisions for you:**
- **Storage during the beta:** my pick is to ship the sandbox as written. If infrastructure will allow a freeze exception for one new domain, I'd do that instead: the new-domain setup could ship for the beta and keep `localStorage`. The other options are delaying the beta or building a storage workaround, which is new product work. Shipping as things are today isn't on the list.
- **The new domain:** its name, and your approval to register it and set up its DNS and certificate when the freeze lifts.
- **Pre-beta testers:** whether wiping their saved app data at the switch is fine.
- **Sessions:** whether to sign everyone out once at the switch.

The plan ends with five checks to run in Chrome, Safari and Firefox before launch. The riskiest is whether Safari sends the private-app access cookie. If it doesn't, private apps would be limited to inline-only assets for the beta.