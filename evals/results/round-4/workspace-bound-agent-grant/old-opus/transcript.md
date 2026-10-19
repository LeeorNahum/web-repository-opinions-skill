**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-workspace-bound-agent-grant-old-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5051 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md workspace-tenancy.md auth.md agent-tool-design.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 26109 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && grep -il \"consent\\|grant\\|audit\\|revoc\" *.md; cat http-apis.md | head -80; cat admin.md | head -40"}`

> Result: agent-tool-design.md ai-model-routing.md auth.md billing.md cleanup.md continuous-integration.md data-model.md http-apis.md legal-pages.md model-context-protocol.md provider-setup.md routing.md seo.md workspace-tenancy.md # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https:/ [... 3066 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && grep -in -B1 -A3 \"consent\\|grant\\|audit\\|revoc\" data-model.md provider-setup.md billing.md routing.md cleanup.md | head -120; cat source-of-truth.md ids.md | head -100"}`

> Result: data-model.md-19- data-model.md:20:Prefer soft delete with an access or deletion timestamp when the object may be recovered, referenced, or audited. Hard delete only when there is no recovery or reference need. data-model.md-21- data-model.md-22-Group with the lighter-weight concept that can later carry context, instructions, permissions, or behavior, rather than a rigid hierarchy chosen too early [... 9731 more characters]

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-workspace-bound-agent-grant-old-opus/work/docs/agent-access.md`

````text
# Agent access over MCP

How a consultant's agent gets authorized to reach a firm's workpapers. `docs/brief.md` wins where this document disagrees with it.

## What the brief requires

1. Data from one firm can never be reached through a connection authorized for another firm.
2. A firm Admin approves each agent connection into their workspace.
3. Firms can audit those approvals.
4. A consultant often belongs to several firms' workspaces at once.

## The model in one paragraph

There is one MCP server at `https://mcp.<domain>/mcp`, and it is one OAuth protected resource. Each OAuth authorization is tied to exactly one firm workspace, which the consultant picks on the auth provider's consent screen. A consultant who works for three firms makes three connections: three separate authorizations of the same resource, each with its own token. A token alone is not enough to get in. Each one also needs a product-owned **agent connection** record for that workspace, and a firm Admin must have approved that record. Every tool call goes through one authorization gate. The gate takes the workspace only from the token's verified organization claim and rechecks membership, role, connection approval and scope on every call. No tool argument names a workspace, so a connection cannot be pointed at another firm.

## Identity and workspace binding

- **Organizations.** Each firm workspace is one auth provider organization, as decided. Personal-account mode stays off, so no token ever acts without an organization.
- **One resource, not one per firm.** There are no per-firm MCP URLs or paths. Picking a different firm means a new authorization of the same resource.
- **Where the workspace comes from.** It comes only from the verified organization claim in the access token. For opaque tokens, it comes from the provider's userinfo or introspection response. A decoded but unverified token body never selects a workspace, and neither do tool input, headers or the URL.
- **No organization means refusal.** If verified organization context is missing, the gate refuses with one product error: "This connection isn't tied to a firm workspace. Reconnect and choose a firm."
- **Token checks.** These run on the MCP app, using the provider's backend SDK rather than a framework MCP helper:
  - The issuer is always checked.
  - The audience is checked only when the token actually carries one, and a token naming a different resource is refused. The code says why this check is conditional.
  - Every advertised scope that the call needs must be present. An empty scope list counts as "no scopes", not "unrestricted".
- **Well-known documents.** Protected-resource metadata is served `no-store` and points at the provider's own authorization server metadata URL. The MCP app does not proxy that document.

## Scopes

| Scope | Allows |
| --- | --- |
| `workpapers:read` | `list_workpapers`, `read_workpaper` |
| `workpapers:annotate` | `annotate_workpaper` |

Advertise only these two, and only once the gate enforces both. Then confirm by running a real dynamic client registration that a dynamically registered client is actually allowed to hold them (see provider setup: advertised capability must match granted capability).

## Agent connections

An **agent connection** is the unit an Admin approves. It is keyed by:

- the consultant's provider subject,
- the workspace's organization ID,
- the OAuth client ID from the token, which comes from the host's client registration.

Fields:

- `id`: a 12-character Base58 entity ID
- the three keys above
- `clientName`: a snapshot of the name the client registered with. It is self-asserted, and the UI says so.
- `status`: `pending`, `approved`, `denied` or `revoked`
- `capabilities`: what the Admin approved, either `read` or `read` + `annotate`
- `requestedAt`, `decidedAt`, `decidedBy`, `revokedAt`, `revokedBy`, `lastUsedAt`

Lifecycle:

1. The consultant adds the server in their agent host, signs in, and picks a firm on consent.
2. The first verified call with that token creates the connection as `pending`. The call is refused with: "This connection to *Firm* is waiting for a firm Admin to approve it." The product cannot see inside the provider's OAuth flow, so the first verified call is the earliest point where it can create the record.
3. Every Admin of that workspace is notified in the app and by email. The workspace settings page **Agent connections** lists pending, active and past connections with the consultant, client name, client ID, requested time and requested scopes.
4. The Admin either approves with a capability set, which can be narrower than what the token's scopes would allow, or denies. Both decisions are final for that connection. Connecting again from a new client registration creates a new pending connection.
5. Any Admin can revoke at any time. So can the consultant, for their own connection. Revocation takes effect on the next call, because the gate reads the connection on every call and does not wait for the token to expire.
6. If the consultant is removed from the firm, the membership-deleted webhook revokes all their connections in that workspace. The per-call membership check is the actual guarantee; the webhook keeps the record tidy.

Refreshing a token or re-consenting with the same client to the same workspace keeps the same connection, and it stays approved. A different client ID or a different workspace is always a different connection.

## The gate

There is one gate, in the backend, shared by the app UI and MCP. The MCP app verifies the token and then calls backend product capabilities with the verified principal `{ subject, organizationId, clientId, scopes }`. It authenticates to the backend with an internal service secret. The MCP app has no authorization rules of its own.

For every call, in one transaction:

1. The user exists and has not been closed.
2. The user is a current member of `organizationId` and has a role there.
3. An agent connection exists for `(subject, organizationId, clientId)` and its status is `approved`.
4. The capability the call needs is in all three of: what the member's role allows, what the connection was approved for, and what the token's scopes allow.
5. Every read and write is filtered by `organizationId`. `list_workpapers` searches only that workspace. If `read_workpaper` or `annotate_workpaper` gets an ID that belongs to another workspace, it returns the same "not found" as an ID that doesn't exist, so it doesn't reveal that the workpaper exists.

The gate fails closed on any unknown capability, status or missing fact. Refusals are typed and instructive, and they never include another firm's data or name.

Role permissions:

| Role | read | annotate |
| --- | --- | --- |
| Admin | yes | yes |
| Preparer | yes | yes |
| Reviewer | yes | yes |

## Tool catalog

All three tools are advertised to every caller, whatever their connection status. Hosts cache the catalog, so it must not change per caller. A pending, denied or revoked connection reaches the gate and gets the instructive refusal. `list_workpapers` and `read_workpaper` are annotated read-only. `annotate_workpaper` is not. Annotations are attributed to the consultant and stamped with the agent connection ID, so the firm can see "added by *Consultant* via agent connection *X*".

## Audit

- **Approval log.** `agentConnectionEvents` is append-only and never edited. It records `requested`, `approved`, `denied`, `revoked` and `membership_removed`, each with actor, time, capability set and an optional reason. A workspace's Admins can read and export the log for their workspace only.
- **Usage log.** Every `annotate_workpaper` call is logged with its connection ID. `lastUsedAt` is updated on reads.
- **Retention.** Connection rows and events are soft-retained after revocation so that the audit trail survives. Deleting a workspace deletes them along with it.

## Enterprise-managed authorization

Check whether the configured provider's authorization server metadata lists `urn:ietf:params:oauth:grant-profile:id-jag`. If it does, enable the extension alongside standard OAuth. If it doesn't, change nothing and build nothing custom. Even when ID-JAG is enabled, the connection still needs Admin approval in the product. The extension changes how the token is obtained, not whether the firm has approved the connection.

## Assumptions to confirm

1. **The provider is Clerk.** The brief says "managed provider". Clerk is the repo's default.
2. **The provider can bind an OAuth token to one organization chosen at consent.** This is the design's load-bearing assumption. Before writing the gate, decode a real token and confirm the verified org claim (or userinfo field) is there. If the provider can't do this, **do not ship MCP access**. A product-side workspace picker can't safely replace it, because hosts often reuse one client registration across connections, so the client ID can't tell firms apart. Record the gap and pick another provider path.
3. **All three roles may read and annotate through an agent.** The brief doesn't say which roles may use agents. Changing that table is a one-line change.
4. **An Admin may approve their own connection.** The event is recorded as self-approved so firms can see it in the audit. Firms that require separation of duties might want a second Admin instead. That would need a rule for workspaces with only one Admin.
5. **Approvals don't expire.** They last until someone revokes them or membership ends. A per-firm expiry policy can be added later.
6. **Agent access isn't a paid feature.** Plans are per firm, but nothing decides that MCP access is gated by plan. If it becomes one, the check goes in the billing gate, not this one.
7. **Approval is per client registration, not per agent instance.** A consultant reusing the same host registration for the same firm is one connection. MCP can't reliably tell instances apart below the OAuth client.
8. **Admins are notified by email and in the app.** Email uses the transactional provider. This assumes those surfaces exist when this ships.

````

> Result: File created successfully at: C:/tmp/wro-eval3/builds/3-workspace-bound-agent-grant-old-opus/work/docs/agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/agent-access.md`. Nothing is committed yet, and none of it is built or tested; the document is the design only.

**How it works:**
- **One MCP server, one firm per connection.** All agents use a single server address. When a consultant signs in, they pick one firm, and the token they get is tied to that firm. A consultant in three firms makes three separate connections.
- **The firm comes only from the token.** No tool takes a firm as an argument. Every lookup is filtered to the token's firm. Asking for a workpaper that belongs to another firm returns the same "not found" as one that doesn't exist, so it doesn't even confirm the workpaper is there. This is what keeps one firm's data out of another firm's connection.
- **An Admin approves each connection.** A connection's first call creates a pending request and is refused with a clear "waiting for a firm Admin" message. The firm's Admins are notified, then approve it (read-only, or read plus annotate) or deny it. Any Admin can revoke it later, and so can the consultant.
- **Every call is rechecked.** Each call confirms the consultant is still a member of the firm, still has their role, the connection is still approved, and the token allows the action. A revocation or removal from the firm takes effect on the next call, not when the token expires.
- **Approvals are auditable.** Requests, approvals, denials and revocations go into a log that is never edited, and each firm's Admins can export their own firm's entries. Annotations are recorded as made by the consultant through that connection.

**Assumptions I made, which you can change:**
1. **The provider can tie a token to one firm.** This is the one the whole design depends on. Before building, someone needs to look inside a real token and confirm the firm is in it. If it isn't, I recommend not shipping agent access rather than letting the agent say which firm it means. Agent apps often reuse one registration across connections, so nothing else would reliably tell the firms apart.
2. The managed auth provider is Clerk, the repo's default.
3. Admins, Preparers and Reviewers can all read and annotate through an agent.
4. An Admin can approve their own connection, and the log marks it as self-approved. You may prefer to require a second Admin, which needs a rule for firms that have only one Admin.
5. Approvals don't expire; they last until revoked or until the consultant leaves the firm.
6. Agent access is not tied to a firm's plan.
7. A connection is one sign-in from one agent app, not one agent. Two agents sharing the same sign-in count as one connection.
8. Admins are notified by email and in the app.

**Session ended:** success, 8 turns, 92975 ms
