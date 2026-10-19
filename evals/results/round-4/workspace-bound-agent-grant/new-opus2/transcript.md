**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus2/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5051 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md auth.md agent-tool-design.md"}`

> Result: <persisted-output> Output too large (31.1KB). Full output saved to: <run>\builds\4-workspace-bound-agent-grant-new-opus2\cfg\projects\C--tmp-wro-eval4-builds-4-workspace-bound-agent-grant-new-opus2-work\76e86da1-f6e4-4c11-affd-b245ee745314\tool-results\bbzacwkgt.txt  Preview (first 2KB): # Workspace Tenancy  Give a product workspaces when shared ownership, membership, or policy needs  [... 1853 more characters]

**Tool call `Read`:** `{"file_path": "<run>\\builds\\4-workspace-bound-agent-grant-new-opus2\\cfg\\projects\\C--tmp-wro-eval4-builds-4-workspace-bound-agent-grant-new-opus2-work\\76e86da1-f6e4-4c11-affd-b245ee745314\\tool-results\\bbzacwkgt.txt"}`

> Result: 1	# Workspace Tenancy 2	 3	Give a product workspaces when shared ownership, membership, or policy needs them now or is on the product's roadmap, because retrofitting an ownership boundary costs far more than carrying one early. A product whose data will only ever belong to one person keeps it on the user account, with no organization layer. When a product's collaboration model is workspaces, back  [... 31930 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md ids.md agent-plugins.md | head -c 20000"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 6036 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat routing.md domains.md | head -c 9000; cat ../../../../package.json"}`

> Result: # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix [... 8880 more characters]

**Tool call `Write`:** `<run>\builds\4-workspace-bound-agent-grant-new-opus2\work\docs\agent-access.md`

````text
# Agent access over MCP

How a consultant's agent gets authorized to reach a firm's workpapers through the Harbor Ledger MCP server. This builds on what `docs/brief.md` has decided. Anything the brief doesn't settle is marked as an assumption in [Assumptions and open questions](#assumptions-and-open-questions).

## The decision: one connection, one firm

**Every agent connection is bound to exactly one firm workspace for its whole life.** A consultant who works for three firms makes three connections. Each one is approved by that firm's Admin and is useful only inside that firm.

Why this scope and not an account-wide grant:

- The brief says firm contracts require that data from one firm can **never** be reached through a connection authorized for another firm. An account-wide grant would let one connection reach every firm the consultant belongs to. Its tokens could still be checked per call, but the connection itself would cross firms, and that is what the contracts forbid.
- The brief says a firm Admin approves **each** agent connection into their workspace. Firm A's Admin can't approve access to firm B, so an approval only makes sense when the connection is bound to one firm.
- Firms audit approvals. With one firm per connection, each approval record belongs to exactly one firm's audit trail.

The cost is that a consultant has to make one connection per firm. That cost is accepted.

## Endpoint and resource

- There is one MCP server for every firm: `https://mcp.<domain>/mcp`. It is deployed as its own protocol app (Hono with the official MCP SDK's web-standard transport) and is stateless per request.
- This URL is the single canonical OAuth resource. Connecting to a second firm is a **new authorization of the same resource**. It is never a per-firm URL, path, or subdomain.
- Every caller sees the same static tool catalog: `list_workpapers`, `read_workpaper`, `annotate_workpaper`. The catalog never changes with the caller's firms or approval state. Authorization is decided per call.
- None of the tools takes a workspace argument. The connection fixes the firm, so an agent can't name a different one.

## Actors and roles

| Actor | What they do |
| --- | --- |
| Consultant (any member: Admin, Preparer, or Reviewer) | Authorizes an agent, binds the connection to one of their firms, sees and revokes their own connections. |
| Firm Admin | Approves or denies connection requests into their firm, narrows the capabilities, revokes connections, reads the audit trail. |
| Agent (MCP client) | Calls tools with an access token. It acts only as the consultant, and only within the firm the connection is bound to. |

The provider organization holds membership and the built-in admin/member roles. Admin, Preparer, and Reviewer are mapped to capabilities in Harbor Ledger's own authorization gate (see [the gate](#the-gate-every-call)).

## Capabilities and scopes

| Tool | Capability | OAuth scope | Roles that hold it (assumed) |
| --- | --- | --- | --- |
| `list_workpapers` | `workpaper.read` | `workpapers:read` | Admin, Preparer, Reviewer |
| `read_workpaper` | `workpaper.read` | `workpapers:read` | Admin, Preparer, Reviewer |
| `annotate_workpaper` | `workpaper.annotate` | `workpapers:annotate` | Admin, Preparer, Reviewer |

On every call, the effective capability set is the **intersection** of:

1. the capabilities of the consultant's **current** role in the bound firm,
2. the scopes on the access token, and
3. the capabilities the Admin **approved** for this connection. An Admin can approve read-only even when the agent asked for annotate.

The protected-resource metadata advertises only these two scopes, and the server requires every scope it advertises for a tool. A missing scope gets the protocol's `403` with an `insufficient_scope` challenge naming the scope that was needed.

## Connection lifecycle

A connection is a product-owned record, stored in Harbor Ledger, not with the auth provider:

```text
connection {
  id                 12-char Base58 entity id
  workspaceId        the one bound firm (null only while unbound)
  userId             the consultant (provider subject stored on the user)
  providerGrantId    the provider's identifier for this authorization; stable across token refreshes
  clientId, clientName  the OAuth client as registered (display only, never trusted for authority)
  requestedCapabilities, approvedCapabilities
  status             unbound | pending | approved | denied | revoked | ended
  decidedBy, decidedAt, reason
}
```

States and transitions:

```text
unbound ──bind to firm──► pending ──Admin approves──► approved ──Admin/consultant revokes──► revoked
                             │                           │
                             └──Admin denies──► denied   └──membership lost / account closed──► ended
```

- `denied`, `revoked`, and `ended` are **terminal**. A connection never comes back to life. Getting access again takes a new authorization, which creates a new connection and a new approval.
- The binding can't be changed. Once a connection has a `workspaceId`, nothing can point it at another firm, so there is no code path that does so.
- A connection only ever moves to a less-privileged state on its own. A role downgrade narrows the effective capabilities live, because the gate intersects with the current role on every call. A role upgrade never widens the connection beyond its `approvedCapabilities`.

## Flow

1. **Add the server.** The consultant adds `https://mcp.<domain>/mcp` to their agent host. The host reads the protected-resource metadata (served `no-store`). That metadata points at the auth provider's own authorization-server metadata, which Harbor Ledger does not proxy.
2. **Authorize.** The host runs standard MCP OAuth against the provider: dynamic client registration where the host uses it, PKCE, and the requested scopes. The consultant signs in and consents. The access token names the MCP resource in its audience.
3. **Choose the firm.**
   - *Preferred:* the provider's consent step lets the consultant pick one organization and puts it into the token as a verified claim. The connection is then created `pending` and already bound on the first call.
   - *Fallback (Clerk, until confirmed otherwise):* the first call with an unknown `providerGrantId` creates an `unbound` connection and returns an instructive tool error: *"This agent connection isn't linked to a firm yet. Choose a firm at https://app.\<domain\>/agent-connections."* That page is signed in, sits outside any workspace prefix, and lists the consultant's own unbound connections by client name and time. The consultant must be the same subject as the token's. They pick exactly one firm from their live memberships, and the connection moves to `pending`.
   - Either way, no workpaper data is returned until step 4.
4. **Admin approval.** The firm's Admins are notified by email and in-app. They review at `https://app.<domain>/w/<workspaceId>/settings/agent-connections`, which shows the consultant, their current role, the client name, the requested capabilities, and when it was requested. They then approve (optionally narrowing capabilities) or deny, with an optional reason. While a connection is pending, calls return *"Waiting for an Admin of \<firm name\> to approve this connection."*
5. **Use.** Every call passes through the gate below.
6. **Revoke.** Any Admin of the firm, or the consultant, can revoke at any time. Where the provider supports it, the product also revokes the provider-side grant. The gate stops honoring the connection on the very next call either way, because it doesn't rely on token expiry. Later calls get `401` with a fresh `WWW-Authenticate` challenge, so the host can start a new authorization, which needs a new approval.

An Admin connecting their own agent also goes through `pending`. One Admin can approve their own request, and the audit trail marks it `self-approved` (an assumption, see below).

## The gate (every call)

All of this runs in the shared authorization gate, the same module the app UI and any future API go through. It does not live in the MCP adapter. It fails closed at each step:

1. **Token.** Verify the token with the provider's backend SDK, not a framework MCP helper. Check the signature or introspection, check the issuer every time, and **require** the MCP resource in the audience. Configure the provider to mint the audience, and reject any token without it. Before writing this check, decode a real token from our provider and build the rule from the claims it actually carries.
2. **Connection.** Look up the connection by `providerGrantId` and confirm it belongs to the token's subject. If it isn't `approved`, return the instructive error for its state.
3. **Firm binding.** The target workspace is always `connection.workspaceId`. Nothing in the request can override it. If the token carries an organization claim, it must equal the bound workspace, or the call is refused. A token's organization claim is never used to choose a workspace.
4. **Live membership.** The subject must currently be a member of the bound firm. Read their current role from verified provider data or our webhook-synced mirror. If the membership is gone, the connection moves to `ended` and the call is refused.
5. **Capability.** The tool's capability must be in the role ∩ scope ∩ approved intersection.
6. **Resource.** Every workpaper id and every list query is resolved **inside the bound workspace only**. An id belonging to another firm returns the same "not found" as an id that doesn't exist, so another firm's data isn't even confirmed to exist. List cursors are opaque, encode the workspace they were issued for, and are rejected anywhere else.
7. **Audit.** Record the call (see below), then act.

Nothing about firm A ever crosses into firm B's connection: not search, not cursors, not ids, not member lists, not error copy.

## Isolation guarantees, stated as tests

These are the checks that prove the contract. They run against the real gate:

- A connection approved for firm A gets "not found" when it reads a firm B workpaper id, even when the consultant is a member of B.
- `list_workpapers` through an A connection never returns a B row, whatever the query.
- A cursor issued to an A connection is rejected when presented by a B connection.
- A token whose organization claim names B, presented for an A-bound connection, is refused.
- `pending`, `denied`, `revoked`, and `ended` connections return no data. Revocation takes effect on a token that is still unexpired.
- Removing the consultant from firm A ends the A connection and leaves their B connection unaffected.
- Downgrading the consultant's role narrows the A connection's capabilities on the next call.
- A token without the MCP audience is rejected.

## Audit trail

Firms audit approvals, so every lifecycle event is an append-only record kept in the firm's workspace:

- `requested`, `approved` (with approved capabilities, and `self-approved` when it applies), `denied`, `revoked` (by whom and why), `ended` (membership lost or account closed). Each record stores the actor, the time, the connection id, the consultant, and the client name.
- **Tool calls** made through a connection: connection id, tool, workpaper id, and time. These hold no content. Annotations themselves record both the consultant and the connection they were made through, so a firm can tell agent-written notes from hand-written ones.

Firm Admins see only their own firm's records at `/w/<workspaceId>/settings/agent-connections`. The consultant's cross-firm `/agent-connections` page shows only their own connection metadata, never any workpaper content.

## Account closure and membership removal

- Removing a member (provider webhook, verified and deduplicated) moves every connection they had into that firm to `ended`. The gate also catches this on the next call even if the webhook is late, because step 4 rechecks membership live.
- When a consultant's account closes, all their connections move to `ended`. The auth reference's closure record keeps a token that is still valid from recreating anything.

## Plans

Plans are per firm. Agent calls count against the bound firm's plan, never the consultant's other firms. Whether agent access is a paid feature is a billing decision and is kept out of this gate. Today it is not gated.

## Enterprise-managed authorization

This is additive only. If the provider natively supports the MCP Enterprise-Managed Authorization extension (it lists `urn:ietf:params:oauth:grant-profile:id-jag` in `authorization_grant_profiles_supported`), enable it alongside standard OAuth. The firm-binding and Admin-approval rules above still apply to connections made that way. Don't build a custom token exchange for it. Recheck provider support whenever this area is touched.

## Assumptions and open questions

Calls I made while the owner was away. Each one is reversible unless noted otherwise.

1. **Workspace-bound, not account-wide.** I read this straight off the contract language in the brief. It's the one decision here I'd defend most strongly.
2. **The provider exposes a stable per-authorization identifier** (`providerGrantId`) that survives token refresh and differs between two authorizations by the same user and client. This is load-bearing: without it, two connections from one host to two firms can't be told apart. **Must be verified against a real token from our provider before implementation.** If the provider has no such identifier, the fallback is to require organization-scoped tokens selected at consent (flow step 3, preferred path), and the gap gets recorded here.
3. **Clerk's consent doesn't select an organization**, so I designed the product-owned "choose the firm" step as the fallback. If the provider can mint a verified organization claim chosen at consent, use that and drop the unbound state.
4. **All three roles can read and annotate.** The brief names the roles but not their permissions. If, say, Preparers shouldn't annotate, only the role-to-capability map changes.
5. **Admins can approve their own connection**, marked `self-approved` in the audit trail. Firms may want a second Admin instead. That would be a per-firm setting.
6. **Approvals don't expire.** They last until revoked or ended. Periodic re-approval (for example yearly, to match engagement terms) would be easy to add if firms want it.
7. **Any single Admin can approve.** No quorum.
8. **Tool calls are logged as metadata, not content.** Retention length is undecided and probably set by firm contract or regulation, so it needs the owner's answer.
9. **Hosts that allow only one connection per server URL** can't hold two firms at once. Consultants on those hosts re-authorize to switch firms, which creates a new connection that needs approval. A per-firm URL is deliberately *not* offered as a workaround, because it would make each firm a separate resource. This should be published in the client compatibility notes once tested.
10. **Agent access is not plan-gated** for now.
11. **Admin notification by email** uses the transactional email provider (Resend by default). The notification copy hasn't been written yet.

````

> Result: File created successfully at: <run>\builds\4-workspace-bound-agent-grant-new-opus2\work\docs\agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/agent-access.md`. It isn't committed yet. It's a design only: nothing is built, and none of it has been checked against a real token from our auth provider.

**The main decision:** each agent connection is bound to one firm for its whole life. A consultant who works for three firms makes three connections, and each one needs approval from that firm's Admin. I chose this because the brief says one firm's data can never be reached through a connection authorized for another firm, and because an Admin can only approve access to their own firm.

**What the doc covers:**
- **One server address for every firm:** `https://mcp.<domain>/mcp`. Connecting to another firm means authorizing again against the same address, not using a per-firm URL. No tool takes a firm argument, so an agent can't point a call at a different firm.
- **Connection states:** a connection starts unbound, then waits for approval, then is approved. Denied, revoked and ended are final, and a connection can never be moved to another firm. Until an Admin approves, calls return a plain message saying what's needed and no workpaper data.
- **Checks on every call:** the token must be valid and issued for our server, and the connection must be approved. The consultant must still be a member of the bound firm. What the agent can do is limited by three things at once: the consultant's current role, the token's permissions, and what the Admin approved. Workpaper lookups only search the bound firm. Another firm's workpaper looks exactly like one that doesn't exist, and list cursors don't work across firms.
- **Isolation tests** that prove the cross-firm guarantee.
- **The firm's audit trail:** a record of every request, approval, denial and revocation, plus a log of tool calls without workpaper content.
- **What happens when a consultant leaves a firm or closes their account,** and how the per-firm plans fit in.

**Assumptions** (the full list of 11 is at the end of the doc):
- **This one needs checking before anyone builds:** I assumed the auth provider gives each authorization a stable ID that is different for two firms authorized from the same agent. Without that ID, two connections from one agent can't be told apart. The doc gives a fallback if it doesn't exist.
- I assumed the provider's own sign-in consent can't pick a firm. So the design adds a Harbor Ledger page where the consultant picks the firm before any data flows. If the provider can pick the firm during sign-in, that page can go.
- All three roles (Admin, Preparer, Reviewer) can read and annotate.
- An Admin can approve their own connection, and the audit trail marks it as self-approved. Any one Admin can approve, and approvals don't expire.
- Agent access isn't limited by plan for now.

**Needs your answer:**
- How long tool-call logs are kept, which is probably set by firm contracts or regulation.
- Some agent apps allow only one connection per server address. Consultants using those can only work in one firm at a time and have to re-authorize to switch. I chose not to work around this with per-firm addresses.

**Session ended:** success, 9 turns, 131867 ms
