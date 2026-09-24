# HTTP APIs

Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:

- HTTP API: `https://api.<domain>/v1`
- OpenAPI document: `https://api.<domain>/openapi.json`

Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript protocol app, including an OpenAPI-backed `/v1` app.

Version the application API in its base path. Additive fields may stay in the current version. Breaking semantics require a new version or an explicit migration contract.

Publish an OpenAPI contract for every public HTTP API, and settle the contract before implementing the surface. Keep one normalized product resource schema across search, direct lookup, collections, API responses, agent tools, and workflow guidance.

Public adapters call shared product capabilities. They translate protocol inputs and outputs but never expose provider payloads, backend-native identifiers, or duplicate product rules.

For credential-free read APIs:

- Allow public CORS only for required methods and headers.
- Use opaque cursor pagination with explicit default and maximum page sizes.
- Return stable typed errors.
- Cache public metadata briefly with stale revalidation.
- Apply rate limiting at the edge or gateway, not in product database tables.

Public callers use the product-owned API origin. Keep a provider's visible default endpoint inside its adapter unless that provider endpoint itself must become a product-owned public surface.

## API-First Clients

Design the product API first, then build each client as a thin layer over that API rather than a second implementation with its own rules. A thin client authenticates with a scoped key, mirrors the API's shape, and inherits its authorization and audit behavior. The same surface can serve a person at a terminal, a script in CI, and an agent.

Match the client to its observed context delivery. Some agent hosts inject a connected interface eagerly, while others defer tools behind search or another retrieval layer. Measure what the supported host actually places in model context, then favor an on-demand client only when it proves cheaper and the value of a persistent surface does not justify its cost.
