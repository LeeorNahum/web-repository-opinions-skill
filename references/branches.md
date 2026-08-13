# Branches

Branches are deployment roles, not just code lines. Use `main`, never `master`, as the production branch.

| Branch | Stage | Provider credentials | Deploys |
| --- | --- | --- | --- |
| `dev` | local development | dev/test | never |
| `preview` | hosted staging | dev/test | yes, staging |
| `main` | production | production | yes, production |

Two provider stages exist, not three: dev/test and production.

- Local and staging share dev/test resources (test billing mode, dev backend deployment, development auth instance, `*-dev` provider keys).
- `main` alone uses production resources (live billing, prod backend deployment, production auth instance, `*-prod` keys).
- Same env key names everywhere; values change by store.
- Staging differs from local mainly by origin URLs, not by a different set of API keys.

Agent Git rules:

- Default commit target is `dev` unless the user asks for `preview` or `main`.
- Merge `dev` into `preview` for a hosted staging deploy.
- Merge `preview` into `main` only for production releases with explicit approval.
- Never commit `.env.local`, filled temp env files, or secrets.
- Push only with explicit user approval.

The point of the system: every change lands on `dev` first, `preview` proves it on real hosted infrastructure while still using safe dev/test resources, and `main` is the only place production credentials and live data are touched.

## Preview Parity

Preview is not a private feature branch runtime. It should run the same product posture as production, with dev/test credentials, staging origins, and non-production data. Keep authentication, route exposure, catalogs, and branch-specific behavior production-capable unless the product intentionally supports the same behavior in production behind a normal feature or authorization gate.

Parity is about behavior, not about who can reach it. Preview proves upcoming production behavior, so it should not hide untested promotion changes behind special branch conditionals. That is a different question from whether the public should be able to load it.

## Preview Is Not Public

Keep preview reachable only by the team. Turn on the hosting platform's access protection for every browser-facing preview deployment and leave it on.

Preview exists to look at what has not shipped. Anyone who can load it can read unreleased copy, unannounced features, version numbers that are not out yet, and prices that are not final. None of that is secret in the security sense, and all of it is wrong to publish early. Access protection is the difference between staging and a second front door.

Regardless of the gate, treat preview as if the gate could be lifted:

- Serve `Disallow: /` from `robots.txt` and a `noindex` on every page. A gate can be turned off for a debugging session and forgotten, and a preview host that gets indexed is a duplicate of the whole site competing with the canonical one.
- Name no sitemap from a host that must not be crawled.
- Keep the canonical tag pointing at the production origin from both hosts.

The one carve-out is machine-facing surfaces. An API, MCP, or webhook project answers programmatic requests, and a browser-only gate turns every machine call into an auth failure the client cannot resolve. Those projects need a protection story their clients can actually satisfy, such as a token, rather than a browser session gate. `references/deployment.md` owns that case.

Ask before pointing staging at production provider resources instead of the shared dev/test resources.
