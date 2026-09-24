# Stack

Pick the role first, then the tool. Do not let a tool dictate architecture: the same product rules must hold if the tool changes.

Keep each protocol's transport, revision, caching, discovery, and capability rules in its owning interface contract rather than treating the framework choice as the protocol design.

## Independently Deploying Services Move In Backend Order

When several services deploy independently but share one backend, a release that changes the backend contract can publish a service against a backend that does not serve it yet. Two disciplines close that:

- **A positive generation proof, fail-closed.** The backend exposes one unauthenticated query returning an exact per-generation marker value from the same source file the dependents pin. Each dependent's build preflight requires HTTP success, the exact success envelope, and the exact value. Any other status, body, parse failure, timeout, or transport failure fails the build. Checking for the absence of an error message is not a proof, it is a false pass waiting for a 500 that parses.
- **Staged schema changes.** A schema store that validates every existing row on push cannot deploy a newly required field over old rows. Ship the field optional with an explicit safe reading for absence, backfill with a bounded resumable pass repeated to zero changes, and tighten to required only in a later release carrying the zero-change evidence.

Keep the chosen tool out of paradigm names. A folder is `auth`, not `clerk`. A module is `origins`, not `vercel-origins`. Name by what it does, not who provides it.

TypeScript is the floor, not a choice. Prefer one language across apps, packages, and backend so types and helpers cross boundaries cleanly.

Prefer the latest stable release of each tool, and follow its current conventions rather than an older major's. Keep the parts of the toolchain that must agree on the same major, so the config, build, types, and rendered runtime stay consistent.

## Serve Dependencies From Your Own Origin

Every dependency the browser executes is served from the product's own origin. No public CDN at runtime, for scripts, styles, fonts, or worker bundles.

The cost of a runtime CDN is not only latency and an availability dependency you do not control. It hands a third party a request, and therefore an IP address and a referrer, from every user on every session that touches that feature. It also silently defeats version pinning: a loader with a default CDN URL will fetch whatever version that URL names, so the version in the lockfile can be a version that never runs.

Heavy editors and viewers are where this hides, because their loaders default to a CDN and work perfectly in development, so nothing ever fails. Check them specifically. Add the package as a real dependency, configure the loader at the product's own path, and verify in a browser's network panel that no third-party host is contacted. A dependency that is not in the manifest but appears in the network panel is the bug.
