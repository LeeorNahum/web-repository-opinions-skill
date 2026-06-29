# Public Interfaces

Give each public protocol one product-owned role subdomain and one canonical endpoint shape:

- HTTP API: `https://api.<domain>/v1`
- OpenAPI document: `https://api.<domain>/openapi.json`
- Remote MCP: `https://mcp.<domain>/mcp`

Deploy API and MCP as separate protocol apps when they need independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for HTTP API surfaces, including OpenAPI-backed `/v1` apps. Use the official MCP SDK transport for MCP protocol behavior, and on serverless runtimes configure it for buffered JSON responses rather than SSE streaming. A serverless function can finalize before an asynchronously written SSE result event is flushed, which silently drops slow tool-call results even while fast handshakes like initialize and tools/list still return. Reserve SSE streaming for long-lived runtimes. Run that transport statelessly on serverless, with a fresh server and transport per request, because in-memory session state does not survive across function instances; add a shared session store only when the protocol genuinely needs server-held sessions.

When an MCP server uses Clerk's MCP helpers, prefer Express while Clerk's supported helper path is Express-specific and until a non-Express path is proven with real clients. Keep this as a protocol-specific compatibility choice, not a general rejection of Hono. Use the helpers only for auth and OAuth metadata, and construct the SDK transport yourself in JSON-response mode rather than delegating transport to a helper that forces SSE.

Version the HTTP API in its base path. Keep MCP at `/mcp`, because MCP negotiates protocol behavior through its transport and protocol contract rather than an application API path version.

Publish an OpenAPI contract for every public HTTP API, and design contract-first by settling that contract before implementing the surface. Keep one normalized product resource schema across search, direct lookup, collections, API responses, MCP tools, and Agent Skill guidance.

Public adapters call shared product capabilities. They translate protocol inputs and outputs but never expose provider payloads, backend-native identifiers, or duplicate product rules.

For credential-free read APIs:

- Allow public CORS only for required methods and headers.
- Use opaque cursor pagination with explicit default and maximum page sizes.
- Return stable typed errors.
- Cache public metadata briefly with stale revalidation.
- Apply rate limiting at the edge or gateway, not in product database tables.

Additive fields may stay in the current version. Breaking semantics require a new version.

Build an Agent Skill on the public API contract when agents need workflow guidance. The skill should teach narrow discovery, preserve canonical product and source URLs, and avoid loading unrelated resources. It must not become a second implementation of the product interface.

Expose the smallest useful MCP tool set. Mark read-only tools as read-only, return the shared resource schema, and document any client capability required to open returned URLs.

Keep provider-host boundaries explicit. First-party clients may use a provider's visible default endpoint for internal product transport. Public API and MCP callers use only the product-owned protocol domains. Configure a provider custom domain only when the provider endpoint itself must be product-owned.

## Preview And Private Access

Public protocol surfaces are public in every deployed stage. A preview API, MCP server, webhook receiver, or CLI distribution should be reachable by machine clients when the same production surface is reachable by machine clients. Do not rely on a browser-only deployment wall as the security boundary for these surfaces, because non-browser clients cannot satisfy it and will fail before they reach OAuth, token verification, protected-resource metadata, dynamic client registration, or stable protocol errors.

Preview should differ from production by runtime values, provider resources, and data, not by hidden behavior. Keep the same public contract, auth challenge behavior, and stable error shape across preview and production. A catalog or contract visible on preview should be a rehearsal of the production contract that will exist after promotion.

Unauthenticated discovery is still disclosure. Public contracts, protocol metadata, tool catalogs, CLI help, and public examples must not reveal internal names, unreleased product promises, provider payloads, private identifiers, secret-shaped values, or future work that is not acceptable to show publicly. If an upcoming capability is not ready to disclose, keep it out of public discovery until the same disclosure is acceptable in production.

When a public program intentionally needs no user authentication, design it as public from the first preview deploy: apply rate limits, narrow CORS, bounded pagination, stable typed errors, conservative caching, and abuse-aware logging before exposing it. A no-auth preview endpoint is not a safer category than a no-auth production endpoint. It is production-shaped behavior running against non-production resources.

Private, experimental, or local-only protocol access belongs behind an explicit private transport instead of a public preview endpoint. Use a provider-supported tunnel or private connector when a client must reach a private server without making that server part of the product-owned public contract.

## Capability Exposure

Exposure decides what a public surface advertises; it is never the security boundary. The authorization gate still enforces every call and returns a clean, instructive error in plain, protocol-neutral language naming what is unsupported.

A catalog that shifts with the set of connected resources fights how clients work: many clients cache the advertised surface on first connect, do not reliably re-fetch when the set changes, and on a stateless serverless protocol cannot be pushed an update. A fully dynamic catalog strands such a client on a stale surface, and a caller with no resources yet is the worst case, seeing almost nothing.

Resolve this by splitting the surface into a constant core and a conditional extension. Always advertise the core: the universal verbs any resource class can run, plus discovery, so a new or empty workspace always has a complete surface and a cached catalog can never collapse to nothing. Advertise an extension verb, one only some resource classes support, only to a caller who has a resource that supports it. The constant core anchors what clients cache: the floor never disappears, and the extension grows only by addition as supporting resources connect. Keep each core verb independently useful, and resolve the extension only when the client requests the catalog, so other calls add no lookup and reach the gate directly.

## API-First Clients

Design the product API first, then build each client as a thin layer over that same public API rather than a second implementation with its own rules. A thin client authenticates with a scoped key, mirrors the API's shape, and inherits its authorization and any audit behavior. The same surface can serve a person at a terminal, a script in CI, and an agent.

Match the client to the cost of context. A client that connects ahead of use and advertises its whole interface front-loads that interface into the consumer's context whether or not any of it is used; a client invoked on demand costs nothing until it runs, and then only its call and its result. When the consumer is a language agent and context is scarce, favor the on-demand client and reserve an always-connected one for when its persistent surface is worth the cost.
