# Public Interfaces

Give each public protocol one product-owned role subdomain and one canonical endpoint shape:

- HTTP API: `https://api.<domain>/v1`
- OpenAPI document: `https://api.<domain>/openapi.json`
- Remote MCP: `https://mcp.<domain>/mcp`

Deploy API and MCP as separate protocol apps when they need independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for HTTP API surfaces, including OpenAPI-backed `/v1` apps. Use the official MCP SDK transport for MCP protocol behavior, and on serverless runtimes configure it for buffered JSON responses rather than SSE streaming. A serverless function can finalize before an asynchronously written SSE result event is flushed, which silently drops slow tool-call results even while fast handshakes like initialize and tools/list still return. Reserve SSE streaming for long-lived runtimes.

When an MCP server uses Clerk's MCP helpers, prefer Express while Clerk's supported helper path is Express-specific and until a non-Express path is proven with real clients. Keep this as a protocol-specific compatibility choice, not a general rejection of Hono. Use the helpers only for auth and OAuth metadata, and construct the SDK transport yourself in JSON-response mode rather than delegating transport to a helper that forces SSE.

Version the HTTP API in its base path. Keep MCP at `/mcp`, because MCP negotiates protocol behavior through its transport and protocol contract rather than an application API path version.

Publish an OpenAPI contract for every public HTTP API. Keep one normalized product resource schema across search, direct lookup, collections, API responses, MCP tools, and Agent Skill guidance.

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
