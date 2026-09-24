# Model Context Protocol

Give a remote MCP server one product-owned endpoint:

- Remote MCP: `https://mcp.<domain>/mcp`

Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backend SDK rather than through framework-specific MCP helpers, so the provider stays a swappable implementation of the authorization server role.

Use buffered JSON responses for ordinary serverless tool calls. Add a streaming or subscription path only when the feature requires it and the hosting runtime is proven to keep that path alive. Keep request handling stateless when the selected protocol revision carries all required context per request. Add shared session state only for a supported client revision or application feature that actually requires it.

Keep the application route at `/mcp`. MCP revision information belongs in the protocol fields defined by the selected revision, not in an application API path version.

## Revision Policy

Choose revision support from observed target-client behavior. A current-revision-only server is simpler, but it excludes clients that have not adopted that revision. Use the SDK's supported dual-revision or compatibility mode when those clients are part of the product contract, and publish the tested client matrix where users will find it.

Treat discovery and version negotiation as capabilities, not assumptions. In the current protocol, a client may call discovery before its first operation, but discovery is optional for the client. Test the exact client path you support, including fallback behavior when supporting an older lifecycle.

## Tool Catalogs

Expose the smallest useful tool set, mark read-only tools accurately, return shared product resource schemas, and document any client capability required to open returned URLs.

Exposure decides what a public surface advertises. It is never the security boundary. The authorization gate still enforces every call and returns a clean, instructive error in plain, protocol-neutral language naming what is unsupported.

Advertise one static catalog to every caller and authorize per call. Many clients cache the advertised surface on first connect and do not reliably re-fetch it, and a stateless transport has no channel to announce a change. A catalog that shifts with the caller's connected resources strands such a client on a stale surface, and a caller with no resources yet is the worst case, seeing almost nothing. Keep each verb independently useful, and let a call against a resource that cannot run it reach the gate and come back as that instructive error.

## Authorization

Published capability metadata is a promise. Advertise only scopes, grant types, response types, refresh behavior, extensions, and change notifications the server actually enforces or serves.

Serve the protected-resource metadata and other well-known documents with `no-store`, because hosts persist dynamic client registrations against them. Point clients at the authorization server's own metadata URL rather than proxying that document from the resource host: its issuer will not match the URL it came from, and a conforming client must discard it.

Enterprise-managed authorization is additive, not the default. For an authenticated MCP server, support the stable MCP Enterprise-Managed Authorization extension when the configured authorization provider supports it natively, and enable it alongside ordinary MCP OAuth so clients and organizations without it keep the standard flow. Check the provider's current documentation and authorization server metadata rather than assuming support either way. A provider that accepts the ID-JAG grant lists `urn:ietf:params:oauth:grant-profile:id-jag` in `authorization_grant_profiles_supported`. When the provider lacks native support, leave the existing OAuth flow unchanged. Build no custom ID-JAG exchange, token service, or enterprise federation layer solely to add it, and keep the provider choice independent of it. Recheck provider support whenever MCP authorization is touched, so native support that arrives later is enabled as an addition to standard OAuth.
