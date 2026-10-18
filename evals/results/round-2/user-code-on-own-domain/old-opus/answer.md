I wrote the plan to `docs/hosting-plan.md`. The main finding is that the current way we serve apps shouldn't open to the public as it is. The fix needs a new domain, which the change freeze doesn't allow, so that part is waiting on your decision.

**The problem.** Every app runs its author's own code on `<name>.plinth.example`. That makes each app part of the same site as `app.plinth.example`, and the sign-in session is stored in a cookie shared across all of `plinth.example`. So every app receives the session of every signed-in person who opens it.
- **If page scripts can read that cookie:** any app can steal the account of anyone who visits it. Some managed auth providers make their session cookie readable on purpose so their own scripts can use it.
- **Even if they can't:** an app can still overwrite the cookie to sign people out or into another account. It can also get around the browser's usual protection against forged requests to `app.plinth.example`.

There is no browser-side workaround that keeps `localStorage`. Blocking an app's access to cookies also breaks its `localStorage`, which most apps rely on.

**What I'm recommending:**
- **A new domain only for published apps**, never used for anything of ours, and listed on the Public Suffix List so browsers treat each app as its own site. Addresses stay short (`<name>.<apps-domain>`), and the product, sign-in and session stay on `plinth.example`.
- **Do it before the beta.** Each app's `localStorage` belongs to its address, so moving apps after launch would wipe every visitor's saved data in every app.
- **Private apps** get their own short-lived pass for that one app, issued by `app.plinth.example` and readable only by our edge, so the main session never reaches app code.
- **Rules that apply either way:**
  - Names like `app`, `api`, `accounts` and `login` are reserved.
  - Our edge owns the `/__plinth/` path on every app.
  - A released name is never given to a new owner, because old data and background scripts stay in visitors' browsers.
  - Only the edge sets response headers.
  - Edge logs never record cookies.

**Decisions for you:**
1. **The beta.** In order of preference: a freeze exception for one domain, one wildcard certificate and one DNS zone; delaying the beta (the freeze is tied to it, so this may not conflict); or opening with each app visible only to its author. I advise against opening as it is.
2. **Which domain to use.** I also considered the reverse: keep apps on `plinth.example` and move the product and sign-in to a new domain. I rejected it as the default because it needs many more DNS records and certificates, plus changes to production sign-in. It's written up as the fallback if `<name>.plinth.example` itself is non-negotiable.

**Assumptions:**
- No outside users' apps with real visitor data exist on `<name>.plinth.example` yet.
- "Short addresses" in the brief means short, not specifically under `plinth.example`.
- You're fine with names never being reused, even though the pool of good short names will shrink over time.

**Quick check for you:** sign in on `app.plinth.example` and look at the session cookie in devtools. If it's marked `HttpOnly` (unreadable by page scripts), the risk drops from account takeover to the sign-out and forged-request problems. The new domain is still needed, just less urgently.

I didn't edit `docs/brief.md`. If you accept the plan, its first "Decided" item needs changing. Nothing is committed.