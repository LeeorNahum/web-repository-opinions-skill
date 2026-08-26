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

## Agent Tool Design

Rules for any tool surface an agent calls: MCP tools, function-calling schemas, CLI subcommands an agent drives. An agent misreads differently than a person, so the surface is designed against agent failure modes, not human ones.

**Destructive scope is never controlled by an optional field.** An omitted or forgotten argument must never widen what gets deleted and must never silently create. A write addressed by ID where a missing ID mints a new resource turns a typo into a duplicate instead of an error. When a merge of two tools requires an optional field to carry the difference between editing and creating, or between one file and the whole resource, keep the two tools.

**Prefer an extra tool over a conditional schema.** Agents pick wrong arguments more often than wrong tools. Two tools whose names carry the split (`delete_thing_file` versus `remove_things`) beat one tool whose behavior forks on which optional fields arrived. Destructive siblings do not cross-reference each other in their descriptions; the object noun in each name is what carries the split, and two tools explaining they are not each other is a symptom of a bad split, not documentation.

**No confirmation arguments.** Approval is the harness's job, signaled through annotations such as `destructiveHint`; a tool demanding its own confirm flag reimplements the execution side in the backend, and the caller that forgot it simply retries with it set, so it costs a round trip without adding safety. Every tool must be safe in an unattended scheduled run: nothing may require a human mid-call.

**Annotations stay truthful, measured against the worst thing the tool can do.** A destructive hint of false means additive-only, so a tool that can refresh or replace existing state carries true even when the common case is additive and even when the replaced bytes came from the user's own source. Where possible, derive annotation checks from the tool's own declared output (an output schema that admits a "replaced" outcome may not carry the additive annotation) rather than restating the hint in a test beside it.

**Any operation that can rename or re-identify a resource returns the resulting identity.** When a write to a file is also the rename, because the name lives in that file, the response carries the name that resulted; a caller not told holds a stale handle and misses its next name-addressed call. Thread the identity from the same derivation that stored it, so what is reported is by construction what was landed, and have tests read the stored row back rather than trusting the echo.

**Reads may resolve names; anything destructive takes stable IDs only.** Names collide and move; an ambiguous name may never decide what gets destroyed. Enforce at the product gate every client crosses and again in the backend transaction, with the tool-side check as defense in depth that answers in the model's own loop. A name matching several resources answers every candidate with its ID, never a coin flip.

**Batches are transport in the adapter.** A list-taking tool loops the single-item product route rather than growing a batch rule at the API, so each item keeps its own quota check and its own failure and the API stays one item, one call. The result contract follows the bulk-actions rules: one variant-typed result per item, in input order, failures inline where their item was rather than in a sibling array that invites reading only the successes. Cap the array with the same number the product's own UI batch uses, because one product concept has one number; loops running from the user's machine need no cap, since each request is separately rate-limited. Reads stay singular even beside batch writes: a read's output is instructions or content the model is about to use, and batching reads invites flooding context.

**A 2xx is a landing before its body is judged.** Parse the upstream success body instead of casting it, and answer a drifted or unreadable success as that item's honest unknown-outcome failure naming the read that disambiguates, never as a thrown exception and never as a success missing its facts. Mark the item landed the moment the upstream said yes, because the operation happened whatever shape the answer came back in. An authorization refusal aborts the whole call only while nothing has landed, through the path that carries the re-auth challenge; after any landing it reports inline, because work that happened must be reported.

**Teach on the error path.** Prose in a description costs tokens on every correct call, while a refusal costs them only when someone is already wrong, so put discovery and correction into typed refusals that name what was found, the measurement, and the next move. Error copy quotes the measurement, never echoes the whole rejected value.

**The first sentence is the retrieval document.** When tools load behind deferred search, the opening sentence is what gets matched, so it carries the verbs a caller reaches for (add, import, install; remove, delete, uninstall) while the body stays documentation. Naming is imperative verb then noun, held consistent within the server; conventions are silent on plurality, so the surface's own precedent binds.

**Keep derived keys printable.** Compose internal delimiters from characters a closed enum can never contain, never from raw control bytes: one literal NUL in a source string makes Git classify the whole file as binary, and a security-bearing handler that renders as `Bin` in every diff has disappeared from review.

## API-First Clients

Design the product API first, then build each client as a thin layer over that same public API rather than a second implementation with its own rules. A thin client authenticates with a scoped key, mirrors the API's shape, and inherits its authorization and any audit behavior. The same surface can serve a person at a terminal, a script in CI, and an agent.

Match the client to the cost of context. A client that connects ahead of use and advertises its whole interface front-loads that interface into the consumer's context whether or not any of it is used; a client invoked on demand costs nothing until it runs, and then only its call and its result. When the consumer is a language agent and context is scarce, favor the on-demand client and reserve an always-connected one for when its persistent surface is worth the cost.
