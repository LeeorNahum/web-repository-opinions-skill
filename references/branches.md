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

When a surface is public in production, treat its preview deployment as public too. Anything advertised by preview discovery should be acceptable to advertise after promotion. Preview proves upcoming production behavior. It should not hide untested promotion changes behind special branch conditionals.

Ask before pointing staging at production provider resources instead of the shared dev/test resources.
