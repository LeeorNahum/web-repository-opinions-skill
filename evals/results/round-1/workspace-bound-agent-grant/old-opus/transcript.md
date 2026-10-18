**Prompt:** not recorded by this session. The case in the committed `evals.json` may have changed since.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-workspace-bound-agent-grant-old-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5051 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md workspace-tenancy.md auth.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 21784 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-workspace-bound-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat agent-tool-design.md source-of-truth.md domains.md && grep -n -i \"rate\\|mcp\" http-apis.md abuse-resistance.md billing.md | head -60"}`

> Result: # Agent Tool Design  Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.  **Destructive scope is never controlled by an optional field.** An omitted argument must never widen what gets deleted or silently c [... 11530 more characters]

**Tool call `Write`:** `<run>\builds\1-workspace-bound-agent-grant-old-opus\work\docs\agent-access.md`

````text
# Agent access: authorizing MCP connections

`docs/brief.md` wins over this document. If they disagree, fix this one.

This covers how a consultant's agent gets access to a firm's workpapers over MCP, and how that access is checked. It follows two requirements from the firm contracts in the brief:

1. **Firm isolation.** Data from one firm can never be reached through a connection authorized for another firm.
2. **Admin approval.** A firm Admin approves each agent connection into their workspace, and firms audit those approvals.

## The model in one paragraph

Each MCP connection is authorized for exactly one firm workspace. The consultant picks that workspace when they consent, and the server only ever reads the workspace from the verified token, never from tool arguments. Consenting creates an **agent grant** in that workspace with status `pending`. The token is valid, but every tool call is refused until an Admin of that firm approves the grant. Each tool call is checked live against four things: the grant's status, the consultant's current membership and role in that firm, the capabilities the grant was approved for, and the token's scopes. A consultant who works for three firms has three separate grants, each approved by its own firm's Admin. None of them can see the others.

## Endpoint and resource

- One remote MCP endpoint: `https://mcp.<domain>/mcp`, served as its own protocol app (official MCP SDK, web-standard transport on Hono), stateless, buffered JSON responses.
- One canonical OAuth protected resource for every firm. There is no per-firm URL or path. Choosing a different firm means a new authorization of the same resource, which produces a new token bound to that other firm.
- Protected-resource metadata is served with `Cache-Control: no-store`. It points clients at the auth provider's own authorization-server metadata URL rather than proxying that document.
- The auth provider is the authorization server. Each firm is one provider organization, as the brief decides. Tokens are verified directly with the provider's backend SDK, not through framework MCP helpers.

## What a connection is bound to

A connection is the tuple **(consultant subject, OAuth client, firm workspace)**:

| Part | Source | Trusted because |
| --- | --- | --- |
| Consultant | Token `sub` | Signature verified with the provider |
| OAuth client | Token client ID (`azp`/`client_id`) | Signature verified, from the client registration |
| Firm workspace | Organization claim on the token, chosen at consent | Signature verified, or the provider's userinfo for opaque tokens |

Rules:

- **The workspace comes only from verified token context.** No tool takes a `workspace` or `firm` argument. Headers, query parameters, and unverified token bodies never select a workspace.
- **Fail closed.** If a token has no verified organization context, every call is refused with one product error: "This connection isn't linked to a firm. Reconnect and choose the firm you want this agent to work in."
- **Selection lists only current memberships.** The consent screen offers only the firms the consultant belongs to right now (this is the provider's organization selection).
- **Issuer is always enforced. Audience is enforced conditionally.** Require the resource as audience only when the token actually names one, and refuse a token that names a different resource. The code must say why this check is conditional (see `auth.md`'s guidance on verifying what the provider actually mints).

### Blocking verification before build

Firm isolation depends on the provider minting an access token whose organization was fixed at consent. Before writing the verifier, decode a real MCP OAuth token from our provider instance and confirm three things: it carries an organization claim, that claim reflects the consent-time choice rather than the user's last-active organization, and that claim cannot be changed on refresh. If any of these fails, the fallback is **not** to accept tokens without that context, and **not** to build our own token service. Tokens without verified organization context stay refused (fail closed), and the shortfall goes back to the owner as a decision. Write down any remaining exposure next to the verifier.

## Agent grants

An agent grant is a database record in the firm's workspace, and the database is its single owner.

```
AgentGrant
  id                 short stable id (shown in audit and the admin UI)
  workspaceId        the firm
  consultantSubject  provider subject id (not email)
  clientId           OAuth client id
  clientName         display name from client registration (informational only)
  capabilities       approved set, e.g. ["workpapers.read", "workpapers.annotate"]
  requestedCapabilities
  status             pending | approved | denied | revoked
  requestedAt, decidedAt, decidedBy (Admin subject), decisionNote?
  revokedAt?, revokedBy?, revokeReason?
```

- **One grant per (workspace, consultant, client).** If the consultant re-authorizes the same client for the same firm and the grant is `approved`, the existing grant is reused. If they ask for capabilities the grant doesn't cover, the extra capabilities go back to `pending` for approval. Anything already approved keeps working in the meantime.
- **A new client means a new grant.** Approval of one agent does not carry over to a different agent or a new client registration.
- **`denied` and `revoked` are final for that grant.** Trying again creates a new `pending` request. It never quietly reopens the old one.
- **Membership is not copied onto the grant.** Role and membership are read live from the provider-backed membership at every call, so removing someone from a firm, or changing their role, takes effect on the next call with no sync job. When the provider's membership-deleted webhook arrives, that member's grants are also marked `revoked` (reason `membership_ended`) so the audit trail says why access stopped.

### Approval flow

1. The consultant adds the server in their agent host and signs in. On consent they pick one firm and approve the requested scopes.
2. The server creates a `pending` grant, writes a `grant.requested` audit event, and notifies that firm's Admins (in-app and email).
3. Until a decision is made, every tool call returns a typed refusal: "Waiting for an Admin at <Firm> to approve this agent connection. You'll be able to use it once they do." No workpaper data is returned, and that includes list results.
4. An Admin opens **Settings → Agent connections** in that firm's workspace. They see the consultant, the agent's client name and ID, the requested capabilities, and when it was requested. They approve (all or some of the capabilities) or deny it, with an optional note.
5. Approval takes effect on the next call. The consultant doesn't need to reconnect.

Admins can revoke any grant at any time from the same page. Consultants can disconnect their own grants from their account page. Either action takes effect on the next call. That is the reason the gate reads grant status on every call and never caches it in the token.

## The gate

Every tool call goes through one authorization module, and every MCP path has to cross it. No tool handler touches workpaper data directly. The gate resolves the call in this order and stops at the first failure:

1. Verify the token (signature, issuer, conditional audience, expiry).
2. Resolve the workspace from verified organization context, or refuse.
3. Confirm the consultant is a current member of that workspace and look up their role.
4. Load the grant for (workspace, subject, client) and require `approved`.
5. Allow the call if the capability is in **role capabilities ∩ grant capabilities ∩ token scopes**. Otherwise refuse.
6. Run the product operation **scoped to that workspace**. Every query is filtered by `workspaceId` inside the operation itself, not only checked beforehand.

A workpaper ID that belongs to another firm returns the same "not found" as an ID that doesn't exist. Whether it exists elsewhere is never revealed.

The same gate (with the agent-grant step skipped for interactive sessions) serves the app UI, so roles mean the same thing on every surface.

### Capabilities, scopes, roles

| Tool | Capability | OAuth scope | Read-only annotation |
| --- | --- | --- | --- |
| `list_workpapers { query?, cursor? }` | `workpapers.read` | `workpapers:read` | yes |
| `read_workpaper { id }` | `workpapers.read` | `workpapers:read` | yes |
| `annotate_workpaper { id, note }` | `workpapers.annotate` | `workpapers:annotate` | no (additive) |

| Role | Capabilities |
| --- | --- |
| Admin | read, annotate |
| Preparer | read, annotate |
| Reviewer | read, annotate |

- The metadata and the `WWW-Authenticate` challenge advertise exactly these two scopes, and the server requires them. A missing scope returns `403` with `error="insufficient_scope"` and names the required scope. An empty scope list counts as no scopes.
- The catalog is the same static list of three tools for every caller. It doesn't change with grant state or role. A call the caller can't make reaches the gate and gets a clear refusal back, such as "Your approval at <Firm> covers reading workpapers, not annotating them. Ask an Admin to add annotation."
- Tool descriptions say that every result comes from the firm this connection was authorized for.

### Annotations carry who made them

An annotation written through MCP is stored with the consultant's subject, the grant ID, and the client name. In the app it shows as "<Consultant> via <agent name>". This lets a firm tell agent-written notes from human ones and trace each one back to the approval that allowed it.

## Audit

Firms audit approvals, so grant history is an append-only event log kept in the firm's workspace:

- `grant.requested`, `grant.approved`, `grant.denied`, `grant.capabilities_requested`, `grant.capabilities_changed`, `grant.revoked` (with actor and reason: `admin`, `consultant`, `membership_ended`)
- Each event records the actor's subject, the time, the grant ID, and the capability set before and after.
- Tool-call records per grant: the tool, the workpaper ID, the time, and the outcome. Reads are included, because for audit workpapers "who looked at what" matters. Note text and workpaper content are not copied into the log.

Admins can view and export both from **Settings → Agent connections**. Events are never edited. A correction is a new event.

## Other limits

- Rate limits on the MCP endpoint are applied at the edge or gateway, per token, and kept separate from any plan quota.
- Short-lived access tokens with refresh are fine. Revocation doesn't depend on tokens expiring, because the gate checks grant status on every call.
- Enterprise-Managed Authorization (ID-JAG) can be added alongside standard OAuth if the provider supports it natively. Recheck support whenever this area is touched. It doesn't replace firm Admin approval: a grant is still required.

## Assumptions made while the owner was away

1. **All three roles can read and annotate through an agent.** The brief names the roles but doesn't say what each can do. If Reviewers should be read-only, or Preparers shouldn't annotate, only the role table changes.
2. **"Each agent connection" means each (consultant, agent client, firm).** Token refreshes and reconnecting the same client need no new approval. A new client, or broader capabilities, does.
3. **An Admin can approve their own consultant connection.** It's still recorded as an approval by that Admin and marked as self-approval in the audit log. Change this if firms want approval by a second person.
4. **Grants don't expire on their own.** They last until revoked or until the membership ends. Periodic re-approval (for example, yearly per engagement) would be an easy addition if firms ask for it.
5. **The audit log includes reads**, not only approvals. This is stricter than the brief requires and was chosen because the product is regulated.
6. **Agent access isn't a paid plan feature.** Plans are per firm, but the brief doesn't tie MCP to a plan. If it becomes a paid feature, that check goes in billing, not in this gate.
7. **Approval doesn't pause the consultant's host.** The connection completes at once and calls are refused until approval, instead of holding the OAuth flow open. Hosts don't handle long-pending OAuth flows well.
8. **Some agent hosts allow only one connection per server URL.** In those hosts a consultant works with one firm at a time and reauthorizes to switch. We accept that rather than adding per-firm URLs, which would weaken the single-resource model.

## Open for the owner

- **Blocking:** confirm the provider's MCP OAuth tokens carry an organization claim fixed at consent (see "Blocking verification before build"). Firm isolation depends on it.
- Whether firms want a second Admin for self-approval, periodic re-approval, or read-only roles (assumptions 1, 3, 4).
- How long audit logs are kept, and whether a firm's audit log is kept or exported when the firm leaves.

````

> Result: File created successfully at: <run>\builds\1-workspace-bound-agent-grant-old-opus\work\docs\agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/agent-access.md`. One thing has to be checked before anyone builds it: keeping firms apart depends on our auth provider issuing an access token whose firm is fixed when the consultant connects. I haven't confirmed that the provider does this. The doc says to decode a real token first. If the firm isn't in the token, the server refuses every call rather than guessing, and the decision comes back to you.

**How it works:**
- **Each connection is tied to one firm.** There is one MCP endpoint, `mcp.<domain>/mcp`. The consultant picks a firm when they connect, and the server only ever reads the firm from the verified token. No tool takes a firm as an input, so a call can't reach into another firm.
- **An Admin approves each connection.** Connecting creates a pending approval record in that firm's workspace, and the firm's Admins are notified. Every tool call is refused with a clear "waiting for approval" message until an Admin approves. The Admin can approve all of what was asked or only part of it, deny it, or revoke it later. Changes apply on the next call.
- **Every call is checked again.** One gate checks the token, the firm, the consultant's current membership and role, and the approval status, then confirms the role, the approval and the token all allow the action. Queries are also filtered to that firm. A workpaper from another firm looks exactly like one that doesn't exist.
- **Firms can audit everything.** There is an append-only log of requests, approvals, denials and revocations. It also records each tool call (reads included) without copying workpaper content. Admins can export it. Notes written by an agent are labelled "<Consultant> via <agent>".

**What I assumed** (each is listed in the doc and easy to change):
1. Admin, Preparer and Reviewer can all both read and annotate through an agent.
2. "Each connection" means one consultant, using one agent, in one firm. Reconnecting the same agent needs no new approval. A new agent, or a request for more access, does.
3. An Admin may approve their own connection. It is marked as self-approval in the log.
4. Approvals don't expire. They last until revoked or until the consultant leaves the firm.
5. Agent access isn't tied to a paid plan.
6. In agent apps that allow only one connection per server address, a consultant works with one firm at a time and reconnects to switch.

Still open for you, besides the token check: whether self-approval should need a second Admin, whether approvals should be renewed periodically, and how long audit logs are kept. I haven't committed the file.

**Session ended:** success, 7 turns, 105259 ms
