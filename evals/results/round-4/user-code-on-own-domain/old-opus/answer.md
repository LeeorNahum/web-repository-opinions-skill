I wrote the plan to `docs/hosting-plan.md`. I found a serious security problem, and fixing it before beta needs a decision from you.

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