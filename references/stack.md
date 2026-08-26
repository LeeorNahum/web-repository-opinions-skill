# Stack

Default building blocks for a serious web product. Swap any tool, keep the role it fills.

| Role | Default | Swap when |
| --- | --- | --- |
| Monorepo | Turborepo + pnpm | A single deployable with no shared packages |
| Rendered public or hybrid surface | Next.js App Router + TypeScript | Static-only site, or a non-React target |
| Private client SPA | Vite + TypeScript | Server rendering or framework routing is required |
| Protocol-only HTTP app | Hono + TypeScript | The runtime already provides an equally small standards-based router, or the protocol helper officially supports a different framework first |
| Styling | Tailwind + shadcn/ui + lucide-react | A design system already exists |
| App data + live sync | Convex | No realtime need, or an existing database |
| Auth | Clerk | Enterprise SSO requirements Clerk cannot meet |
| Billing | Stripe | A region or model Stripe does not serve |
| Heavy media | Cloudflare R2 | Already standardized on S3 or another store |
| Hosting | Vercel | A surface Vercel cannot host well |
| DNS | Cloudflare | Registrar lock-in |
| Email | Resend | An existing transactional provider |
| Rich text | BlockNote or block JSON | Plain text or markdown is enough |
| LLM calls | Vercel AI SDK over a hosting-aware gateway | The product needs a different routing or provider path |

Pick the role first, then the tool. Do not let a tool dictate architecture: the same product rules must hold if the tool changes.

Keep Hono as the default for HTTP APIs, OpenAPI surfaces, and edge-style protocol apps,
including MCP servers. The MCP SDK's v2 split (`@modelcontextprotocol/server` and siblings;
the old monolithic `@modelcontextprotocol/sdk` line ends at 1.30.0) hands you a
`fetch(request)` handler, so Hono's raw request goes straight in with no Node adapter, and
auth-provider verification runs directly against the provider's backend SDK rather than
through framework-specific helpers. The earlier Express hedge existed for Clerk's Express
helpers and is retired: the Hono shape is proven end to end against real hosts.

Two MCP decisions to make deliberately rather than inherit:

- **Revision policy.** Protocol revision 2026-07-28 removed the handshake and sessions.
  Serving only the current revision is the cheapest server and the cleanest serverless fit
  (json response mode, nothing streams, nothing held open), but host adoption lags by
  months: measure what each target client actually puts on the wire, publish that matrix
  where users will look, and accept that current-revision-only cuts off the laggards until
  they ship. A caller-dependent tool catalog cannot work on a stateless transport (there is
  no channel to announce a change), so keep the catalog static and authorize per call.
- **Advertised equals enforced.** Whatever scopes and metadata the resource publishes, the
  gate requires exactly, and the well-known documents are served with `no-store`, because
  hosts persist dynamic client registrations against them. Never proxy the authorization
  server's own metadata from the resource host: the issuer will not match the URL it came
  from, and a conforming client must discard it.

## Independently Deploying Services Move In Backend Order

When several services deploy independently but share one backend, a release that changes the
backend contract can publish a service against a backend that does not serve it yet. Two
disciplines close that:

- **A positive generation proof, fail-closed.** The backend exposes one unauthenticated
  query returning an exact per-generation marker value from the same source file the
  dependents pin. Each dependent's build preflight requires HTTP success, the exact success
  envelope, and the exact value; any other status, body, parse failure, timeout, or
  transport failure fails the build. Checking for the absence of an error message is not a
  proof, it is a false pass waiting for a 500 that parses.
- **Staged schema changes.** A schema store that validates every existing row on push cannot
  deploy a newly required field over old rows. Ship the field optional with an explicit safe
  reading for absence, backfill with a bounded resumable pass repeated to zero changes, and
  tighten to required only in a later release carrying the zero-change evidence.

Keep the chosen tool out of paradigm names. A folder is `auth`, not `clerk`. A module is `origins`, not `vercel-origins`. Name by what it does, not who provides it.

TypeScript is the floor, not a choice. Prefer one language across apps, packages, and backend so types and helpers cross boundaries cleanly.

Prefer the latest stable release of each tool, and follow its current conventions rather than an older major's. Keep the parts of the toolchain that must agree on the same major, so the config, build, types, and rendered runtime stay consistent.

## Serve Dependencies From Your Own Origin

Every dependency the browser executes is served from the product's own origin. No public CDN at runtime, for scripts, styles, fonts, or worker bundles.

The cost of a runtime CDN is not only latency and an availability dependency you do not control. It hands a third party a request, and therefore an IP address and a referrer, from every user on every session that touches that feature. On a product that sells privacy, that is the product contradicting itself. It also silently defeats version pinning: a loader with a default CDN URL will fetch whatever version that URL names, so the version in the lockfile can be a version that never runs.

Heavy editors and viewers are where this hides, because their loaders default to a CDN and work perfectly in development, so nothing ever fails. Check them specifically. Add the package as a real dependency, configure the loader at the product's own path, and verify in a browser's network panel that no third-party host is contacted. A dependency that is not in the manifest but appears in the network panel is the bug.
