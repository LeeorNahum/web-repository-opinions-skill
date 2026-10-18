**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-old-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5051 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md workspace-tenancy.md agent-tool-design.md auth.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 26109 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md agent-plugins.md bootstrap.md source-of-truth.md domains.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 10738 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-old-opus/work\" && cat package.json pnpm-workspace.yaml && cat .claude/skills/web-repository-opinions/references/modularity.md | head -40"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*" # Modularity  Build the product as connected capabilities, not one long imple [... 3483 more characters]

**Assistant:** Now writing the design.

**Tool call `Write`:** `<run>\builds\2-workspace-bound-agent-grant-old-opus\work\docs\agent-access.md`

````text
# Agent access: authorizing MCP connections

Status: proposed design, written while the owner was away. `docs/brief.md` wins wherever this doc disagrees with it. Calls I made without the owner are listed under [Assumptions](#assumptions) and [Open questions](#open-questions).

## The problem

A consultant can belong to several firm workspaces at once. Their agent connects over MCP to read and annotate workpapers. The brief adds two contract rules:

1. **Isolation.** A connection authorized for one firm can never reach another firm's data.
2. **Admin approval.** An Admin of the firm approves every agent connection into that workspace, and firms audit those approvals.

Neither rule holds if a connection is "the consultant". A connection has to be "this consultant, this agent client, this one firm, approved by that firm's Admin".

## Core decision: one connection, one workspace, fixed for life

An **agent connection** is the unit of authorization. It is identified by:

| Part | Source |
| --- | --- |
| User | Provider subject, from the verified access token |
| Workspace | The provider organization chosen at consent, from verified token claims (see [Binding the workspace](#binding-the-workspace)) |
| Agent client | OAuth `client_id` the token was issued to |

The workspace is fixed when the connection is created and never changes. It is **never** resolved from the consultant's current or last-active organization in the web app. If it were, switching firms in a browser tab would quietly retarget a running agent at another firm's data, which is exactly the leak the contract forbids.

A consultant who works for three firms has three connections, each approved separately by that firm's Admin. Moving an agent to another firm means authorizing again and choosing that firm. That creates (or reuses) a different connection. It never changes the existing one.

## Endpoint and OAuth shape

- One product-owned MCP endpoint: `https://mcp.<domain>/mcp`, deployed as its own protocol app (`apps/mcp`, Hono + official MCP SDK, web-standard transport, stateless, buffered JSON).
- One canonical OAuth protected resource. There is no per-workspace path or per-firm resource. Choosing a workspace is part of consent, as `workspace-tenancy` recommends.
- The managed auth provider is the authorization server. Protected-resource metadata is served with `no-store` and points at the provider's own authorization-server metadata URL. We don't proxy it.
- Tokens are checked directly with the provider's backend SDK:
  - Issuer: always enforced.
  - Audience: enforced only if the provider actually puts a resource in the token. A token naming a different resource is refused. The code must say why this check is conditional.
  - Scopes: enforced, using exactly the set we advertise.
- Scopes (advertised and enforced, nothing else):
  - `workpapers:read`: `list_workpapers`, `read_workpaper`
  - `workpapers:annotate`: `annotate_workpaper`
- If the provider supports MCP Enterprise-Managed Authorization (ID-JAG) natively, turn it on alongside standard OAuth, since firms with an enterprise IdP will probably want it. We don't build our own version. Check this again whenever MCP auth is touched.

## Binding the workspace

The isolation guarantee depends on the workspace arriving in **verified** token data. A readable, unverified token body never chooses a workspace.

**Path A (preferred): the provider binds it.** Consent asks the consultant to choose one of their organizations, and the issued access token carries that organization as a verified claim, or the provider's userinfo endpoint returns it for opaque tokens. The gate reads the organization from there and nowhere else.

**Path B (fallback, only if the provider can't do A): the product binds it.** The first call from an unbound `(user, client_id)` gets an instructive refusal with a link to `https://app.<domain>/connect/<connectionId>`. There the consultant, signed in as the same subject, picks the workspace. That choice is stored on the connection and can't be changed. Under Path B a `(user, client_id)` pair has at most one live connection, so changing firms means revoking and reconnecting. **Residual exposure under B:** the token itself is not cryptographically bound to the workspace. The binding is only as strong as our connection record and the gate that reads it. This must be noted in the gate's code.

Before implementation, mint a real token from the provider instance and list its claims (per `auth.md`). Choose A or B from what the token actually contains, not from what the documentation promises.

## Connection lifecycle

```
            consent + first call          Admin approves
 (none) ─────────────────────────▶ pending ──────────────▶ approved
                                     │                        │
                        Admin denies │                        │ Admin revokes / consultant disconnects /
                                     ▼                        │ consultant leaves firm / connection deleted
                                  denied                      ▼
                                                           revoked
```

- **pending:** created by the first authenticated MCP call that resolves a new `(user, workspace, client_id)`. Every tool call is refused with an instructive error, for example: "This connection to *Firm name* is waiting for approval from one of its Admins. You'll be able to use it once they approve." All Admins of that workspace get notified (in-app and email).
- **approved:** an Admin of **that workspace** approves it. The Admin sees:
  - the consultant
  - the agent client name, shown as unverified because dynamically registered names are self-asserted
  - the `client_id`
  - the requested scopes
  - the creation time

  The Admin can approve with fewer capabilities than requested, for example read-only. Token refreshes under the same `client_id` keep the approval.
- **denied / revoked:** terminal. Reconnecting later creates a new pending connection that needs a new approval. Approval is never carried over.
- **Membership ended:** if the consultant leaves the workspace or is removed from it, every connection they have into it is revoked. The per-call membership check already blocks those connections before the revocation event lands. The event exists for the audit trail.
- A new `client_id` is a new connection. Hosts that re-register dynamically get a new pending connection, and that's on purpose: the Admin approved one specific agent client, not any client the consultant might use.

Approval and revocation are product state in the database. That database is the authority for whether a connection may act. If the provider exposes token or grant revocation, we call it on revoke as defense in depth, but the gate never relies on it.

## The gate (every call)

Every MCP call, and every other client that reaches workpapers, goes through the same capability gate. MCP is a thin adapter over the shared workpaper capabilities. It doesn't make its own rules. The order:

1. Verify the token (issuer, conditional audience, scopes). Fail closed.
2. Get the workspace from verified context (Path A claim, or the Path B connection record). If there isn't one, fail closed with one clear product error.
3. Load the connection by `(user, workspace, client_id)`. It must be `approved`.
4. Check that the user is a member of that workspace **right now** and read their current role. Capabilities come from the live role, not a stored copy.
5. Effective capability = role capability ∩ token scope ∩ the capabilities approved on the connection.
6. Run the capability **scoped to the connection's workspace**:
   - `list_workpapers` only searches that workspace.
   - Cursors are opaque, include the workspace, and are refused if they come back under a different connection.
   - `read_workpaper` and `annotate_workpaper` look up the id inside the connection's workspace. An id belonging to another firm returns the same "not found" as an id that doesn't exist, so other firms' ids are never confirmed.
7. Record the call in the workspace's access log and update `lastUsedAt`.

Steps 3–6 run inside the same backend transaction as the read or write. A cached "approved" result is never trusted across transactions, because an Admin's revoke has to take effect on the very next call.

The tool catalog is static. All three tools are advertised to every caller, including pending ones. Authorization happens per call, and a refused call teaches the caller what to do next instead of hiding the tool.

The workspace check is structural. Workpaper capabilities take a `WorkspaceScope` that can only be built by the gate module, and no unscoped query helper exists for adapters to call. Lint rules and types count as hygiene. The runtime check in step 6 is the actual boundary.

### Role capabilities (assumed, see below)

| Capability | Admin | Preparer | Reviewer |
| --- | --- | --- | --- |
| Read workpapers | ✓ | ✓ | ✓ |
| Annotate workpapers | ✓ | ✓ | ✓ |
| Approve / deny / revoke agent connections | ✓ | | |
| View agent connection audit log | ✓ | | |

## Audit

Firms audit approvals, so approval history is an append-only record owned by the workspace.

- `agentConnectionEvents` (append-only): `requested`, `approved` (with approved capabilities), `capabilitiesChanged`, `denied`, `revoked` (reason: `admin`, `consultant`, `membershipEnded`), `selfApproved` flag. Each event records the acting user, the workspace, the connection, and the time.
- Access log: one row per tool call with connection, tool, workpaper id (when there is one), outcome, and time. Annotations also carry the connection id, so every agent-written note can be traced to its approval.
- Admins see both at `app.<domain>/<workspace>/settings/agent-connections` and can export them as CSV. Consultants see their own connections in each workspace and can disconnect them. They can't approve them.

## Data model (sketch)

```
agentConnections
  id                    short public id (used in URLs)
  workspaceId           immutable
  userId                app user; provider subject stored on the user
  oauthClientId
  clientName            self-asserted, shown as unverified
  requestedScopes
  approvedCapabilities  subset of requestedScopes, set on approval
  status                pending | approved | denied | revoked
  createdAt, decidedAt, decidedBy, revokedAt, revokedBy, revokeReason
  lastUsedAt
  unique (workspaceId, userId, oauthClientId) among non-terminal rows

agentConnectionEvents   append-only, see Audit
agentAccessLog          append-only, see Audit
```

## Where it lives

- `apps/mcp`: protocol adapter (Hono, MCP SDK, token verification via the provider's backend SDK, protected-resource metadata).
- `packages/` access gate module: connection lookup, live membership and role, capability intersection, `WorkspaceScope` construction. Every surface (MCP, app, any future API) calls through it.
- Signed-in app: the Admin approvals and audit page, the consultant's connections page, and the Path B `/connect/<connectionId>` page if it's needed.

## Assumptions

Calls I made so the design is complete. Each one can be reversed.

1. **Connection identity is `(user, workspace, client_id)`.** Token refreshes keep the approval. A new client registration, or reconnecting after a revoke or deny, needs a new approval.
2. **An Admin can approve their own agent's connection.** The event is marked `selfApproved` so auditors can see it. Requiring a second Admin would lock out single-Admin firms.
3. **Any one Admin of the workspace is enough** to approve. There's no quorum.
4. **All three roles can read and annotate through an agent**, the same as I assume they can in the app. Only Admins manage connections. The brief lists roles but not what each role is allowed to do.
5. **Admins can narrow capabilities at approval** (for example read-only). Scopes are `workpapers:read` and `workpapers:annotate`.
6. **Approval doesn't expire on its own.** It ends on revoke, deny, or the consultant leaving the firm.
7. **The access log records every tool call**, not only approvals. The brief only requires that approvals be auditable. Per-call logging looked like the obvious next thing a regulated firm would ask for.
8. **Agent access is not a plan gate.** Plans are per firm, but nothing in the brief says MCP is a paid feature. The gate stays separate from billing either way.
9. **Path A is the target** for workspace binding. Path B is used only if a real token shows the provider can't carry a verified organization claim.

## Open questions

- Does the firm contract require approvals to expire or be re-certified periodically (for example every 90 days)? The model supports it (an `expiresAt` field and a re-approval event), but I didn't add it.
- Should approval require a second Admin when the requester is an Admin (see assumption 2)?
- How long must audit records be kept, and in what export format do the firms' auditors want them?
- Should a firm be able to block agent connections entirely, or allow only specific agent clients?
- Do Reviewers really annotate, or only read and sign off? This changes the role table.
- Does the chosen auth provider support MCP Enterprise-Managed Authorization today?

````

> Result: File created successfully at: <run>\builds\2-workspace-bound-agent-grant-old-opus\work\docs\agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/agent-access.md`. It's not committed; I left that for you to review first.

**The design:**
- **One connection is tied to one firm, and that never changes.** An agent connection is identified by (consultant, firm workspace, agent client). The workspace is picked when the consultant authorizes the connection and comes from verified token data. It's never taken from whichever firm the consultant last had open in the app, because otherwise switching firms in a browser tab would point a running agent at another firm's data. A consultant in three firms has three connections, each approved separately.
- **One MCP endpoint for everyone:** `mcp.<domain>/mcp`, with no per-firm URL. There are two permission scopes, `workpapers:read` and `workpapers:annotate`, and the server only offers what it actually enforces.
- **Admin approval:** a new connection starts as pending. Every call is refused with a clear "waiting for an Admin of *Firm*" message until an Admin of that firm approves it. The Admin can approve with fewer permissions than requested, for example read-only. If the connection is denied or revoked, reconnecting needs a fresh approval. If the consultant leaves the firm, their connections into it are revoked.
- **Check on every call:**
  - The token is valid.
  - The connection is approved.
  - The consultant is still a member of the firm, with their current role.
  - What they can do is whatever their role, their token and the Admin's approval all allow.
  - Every query is limited to the connection's firm. A workpaper ID from another firm returns the same "not found" as an ID that doesn't exist, and list results can't be paged across firms.

  All of this runs in the same transaction as the read or write, so a revoke takes effect on the very next call.
- **Audit:** an append-only log of requests, approvals, denials and revocations, plus a log of every tool call. Admins can view and export both, and agent-written notes are traced back to the approval behind them.

**Needs checking before anyone builds it:** firm isolation works best if the auth provider's token carries the chosen firm as a verified value. I haven't confirmed that it does. Someone needs to get a real token from the provider and look at what's in it. If the firm isn't there, the doc has a fallback where the consultant picks the firm on a page in our app. That's weaker, because the token itself isn't tied to the firm and only our own records hold the link. The doc says so.

**Calls I made without you (listed in the doc so you can reverse them):**
- A connection keeps its approval when the token refreshes. A new agent client, or reconnecting after a revoke, needs a new approval.
- An Admin can approve their own agent; the log marks it as self-approved.
- Any one Admin of the firm can approve; no second sign-off.
- All three roles can read and annotate through an agent.
- Approvals don't expire on their own.
- Every tool call is logged, not just approvals.
- Agent access isn't tied to the firm's plan.

**Open questions for you:**
- Do approvals need to expire or be re-confirmed periodically?
- Should an Admin's own connection need a second Admin to approve it?
- How long must audit records be kept, and in what format?
- Should a firm be able to block agents entirely, or only allow certain ones?
- Can Reviewers annotate, or only read?
- Does our auth provider support enterprise-managed sign-in for agents yet?

**Session ended:** success, 8 turns, 117204 ms
