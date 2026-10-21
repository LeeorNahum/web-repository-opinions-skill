# Model Context Protocol

Give a remote MCP server one product-owned endpoint:

- Remote MCP: `https://mcp.<domain>/mcp`

Use the official MCP SDK's current major for protocol behavior, whose server package implements the current revision, served on Hono through the SDK's own Hono adapter or its web-standard transport. Check its package names with the package manager, because the SDK's older single package stays published beside the current ones. Verify tokens directly with the auth provider's backend SDK rather than through framework-specific MCP helpers, so the provider stays a swappable implementation of the authorization server role.

Use buffered JSON responses for ordinary serverless tool calls. Add a streaming or subscription path only when the feature requires it and the hosting runtime is proven to keep that path alive. Keep request handling stateless when the selected protocol revision carries all required context per request. Add shared session state only for a supported client revision or application feature that actually requires it.

Keep the application route at `/mcp`. MCP revision information belongs in the protocol fields defined by the selected revision, not in an application API path version.

## Revision Policy

Choose revision support from observed target-client behavior. A current-revision-only server is simpler, but it excludes clients that have not adopted that revision. Use the SDK's supported dual-revision or compatibility mode when those clients are part of the product contract, and publish the tested client matrix where users will find it.

Implement `server/discover`, which the protocol requires of servers, and answer every request without a prior discover call, since clients may skip it. Test the exact client path you support, including fallback behavior when supporting an older lifecycle.

## Tool Catalogs

Give each distinct product capability an agent needs one tool, with no two tools reaching the same operation. Mark read-only tools accurately, and state in each tool's description what a client needs to open the URLs it returns, such as a sign-in or an expiry. A tool that returns a product resource declares an `outputSchema` built from the same shared schema the HTTP API's contract uses, and returns the resource in `structuredContent` beside its text form. A tool input the shared schema rejects comes back as a tool execution error, `isError: true` with the typed refusal, so the model can correct and retry, rather than as a protocol error in the SDK's own words.

Exposure decides what a public surface advertises. It is never the security boundary. The authorization gate still enforces every call and returns a clean, instructive error in plain, protocol-neutral language naming what is unsupported.

Advertise one static catalog to every caller and authorize per call. The protocol keeps list results from varying per connection, and many clients cache the advertised surface on first connect and refresh it only on a change notification they may never subscribe to. A catalog that shifts with the caller's connected resources strands such a client on a stale surface, and a caller with no resources yet is the worst case, seeing almost nothing. Each tool takes every identifier it needs as an argument, so no tool depends on state an earlier call set. A call against a resource that cannot run it reaches the gate and comes back as that instructive error.

## Authorization

Published capability metadata is a promise. Advertise only scopes, grant types, response types, refresh behavior, extensions, and change notifications the server actually enforces or serves. Challenge and advertise only scopes every registered client can obtain, in the 401 `WWW-Authenticate` `scope` and the protected resource metadata's `scopes_supported`, because a host requests what is advertised and a scope it cannot hold fails after sign-in, where the host shows only a generic connection error. When the authorization provider advertises scopes its registered clients cannot hold, fix the provider's configuration rather than each host.

Serve the protected-resource metadata and other well-known documents with `no-store`, because clients key the credentials they persist to the issuer they discover there. Point clients at the authorization server's own metadata URL rather than proxying that document from the resource host: its issuer will not match the URL it came from, and a conforming client must discard it.

Enterprise-managed authorization is additive, not the default. For an authenticated MCP server:

- Enable the stable MCP Enterprise-Managed Authorization extension alongside ordinary MCP OAuth when the configured authorization provider supports it natively, so clients and organizations without it keep the standard flow. Check the provider's current documentation and authorization server metadata rather than assuming support either way. A provider that accepts the ID-JAG grant lists `urn:ietf:params:oauth:grant-profile:id-jag` in `authorization_grant_profiles_supported`.
- When the provider lacks native support, keep the existing OAuth flow unchanged. Build no custom ID-JAG exchange, token service, or enterprise federation layer solely to add it, and keep the provider choice independent of it.
- Recheck provider support whenever MCP authorization is touched, so native support that arrives later is enabled as an addition to standard OAuth.
