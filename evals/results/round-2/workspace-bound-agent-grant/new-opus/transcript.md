**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-new-opus/work\" && git ls-files && cat docs/brief.md && ls docs"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5060 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md workspace-tenancy.md auth.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 24036 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-workspace-bound-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat agent-tool-design.md user-facing-errors.md | head -150; grep -n \"mcp\\|MCP\" domains.md naming.md monorepo-layout.md http-apis.md | head -30"}`

> Result: # Agent Tool Design  Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.  **Familiar operations first.** Shape the catalog around operations callers already know wherever they express the real domain. File  [... 7575 more characters]

**Tool call `Write`:** `<run>\builds\2-workspace-bound-agent-grant-new-opus\work\docs\agent-access.md`

````text
# Agent Access

How a consultant's agent gets authorized to reach Harbor Ledger over MCP, and how each call is checked. `docs/brief.md` is still the source of truth. Where this document had to decide something the brief does not, the call is listed under [Assumptions](#assumptions) for the owner to confirm.

## Constraints from the brief

1. Data from one firm can never be reached through a connection authorized for another firm.
2. A firm Admin approves each agent connection made into their workspace.
3. Firms audit those approvals.
4. Consultants belong to several firms' workspaces at once.
5. Auth is a managed provider with one provider organization per firm workspace. Roles are Admin, Preparer, and Reviewer.

Constraint 1 decides the scope. Constraint 2 adds an approval step that the OAuth consent screen does not provide on its own.

## Decision: workspace-bound grants

Every agent connection is bound to exactly one firm workspace, and that binding never changes.

- **One resource.** The MCP server is a single OAuth protected resource at `https://mcp.<domain>/mcp`. There are no per-firm paths, hosts, or resources.
- **One workspace per authorization.** During consent, the consultant picks one of their workspaces. The connection that results can only ever act in that workspace.
- **Another firm means another authorization.** To work with a second firm, the consultant authorizes the same resource again and picks the other workspace. That second connection needs its own approval from that firm's Admin.
- **No account-wide grants.** One credential covering all of a consultant's memberships would break constraint 1 by construction, so we don't offer one, not even as an option.

Known cost: some agent hosts keep one credential per server URL. A consultant on one of those hosts can't hold live connections to two firms under one server entry. They either add the server twice under different names, if the host allows it, or re-authorize when they switch firms. We accept this cost to meet the contract. We will not work around it by adding per-workspace URLs.

## Connection lifecycle

A **connection** is a product record: one consultant, one agent client, one workspace, one set of approved capabilities. The product owns it. The auth provider owns identity, membership, and token issuance. The connection record owns the binding, the approval, and the audit trail.

```
consent (consultant picks workspace) ──► pending ──► approved ──► revoked
                                            │                        ▲
                                            ├──► denied              │
                                            └──► expired     (Admin, consultant,
                                                              or membership loss)
```

1. **Authorize.** The agent host runs standard MCP OAuth against the provider: discovery, dynamic client registration, authorization code with PKCE. The consultant signs in at `/auth`.
2. **Choose a workspace.** A product-owned consent step lists the workspaces where the consultant has a live membership. They pick one, and see which capabilities the agent is asking for. The page says plainly that the connection reaches only this firm and needs approval from one of its Admins.
3. **Pending.** The token is issued and the connection record is created as `pending`. The OAuth flow finishes right away and does not wait for an Admin. While pending, every tool call returns the refusal `connection_pending_approval`: "This connection to <Firm> is waiting for a firm Admin to approve it."
4. **Notify.** Every Admin of the workspace is emailed and sees the request in the app's workspace settings under Agent connections. The request shows the consultant, their role in this workspace, the agent client's registered name and redirect host, the requested capabilities, and when it was requested.
5. **Approve or deny.** An Admin approves, and can narrow the capabilities (for example, read-only). Or the Admin denies. Either action is recorded with the Admin's identity.
6. **Expire.** A request still pending after 7 days becomes `expired`. The consultant has to authorize again.
7. **Revoke.** Any Admin of the workspace can revoke an approved connection, and so can the consultant. Revocation takes effect on the very next call, because every call rechecks the connection (see below). Revoking a connection doesn't touch the consultant's membership.

Refreshing a token doesn't create a new connection or need new approval. A new authorization does, even if it names the same client and workspace as an earlier one. "Each agent connection" means each authorization.

## Per-call authorization

The MCP server never trusts the advertised catalog, the host, or the consent screen as the boundary. Every tool call goes through the product's single authorization gate, the same gate the app UI uses, which:

1. **Verifies the token** with the provider's backend SDK. It checks the issuer, the expiry, and that the audience includes `https://mcp.<domain>/mcp`. A token without that audience is refused. MCP requires audience binding, so the provider must be configured to mint it.
2. **Resolves the connection** from a verified token fact (see [Binding the token to the connection](#binding-the-token-to-the-connection)). The connection supplies the workspace. Tool arguments, a remembered selection, or whatever the app UI last showed never supply it.
3. **Checks the connection state.** It must be `approved`. Pending, denied, expired, and revoked connections each get their own refusal.
4. **Checks the live membership.** The consultant must still be a member of the bound workspace right now, checked against the provider's membership data, and the role comes from that same check. If the membership is gone, the call fails closed and the connection is moved to `revoked` with reason `membership_ended`.
5. **Intersects capabilities.** The call proceeds only if three sets all allow it: what the consultant's current role allows, what the Admin approved for this connection, and the token's scopes.
6. **Scopes the data access.** Every query runs against the bound workspace. A workpaper ID from another workspace returns the same `not_found` as an ID that doesn't exist, so a connection can't even confirm that another firm's data exists.

This is how constraint 1 holds. No input to any tool can name a workspace, and the data layer can't read outside the connection's workspace.

### Capabilities and scopes

| Tool | Capability | OAuth scope | Roles that hold it |
| --- | --- | --- | --- |
| `list_workpapers { query?, cursor? }` | `workpapers.read` | `workpapers:read` | Admin, Preparer, Reviewer |
| `read_workpaper { id }` | `workpapers.read` | `workpapers:read` | Admin, Preparer, Reviewer |
| `annotate_workpaper { id, note }` | `workpapers.annotate` | `workpapers:annotate` | Admin, Preparer, Reviewer |

- The protected-resource metadata advertises exactly these two scopes, and the server requires them as advertised. A call that lacks a scope gets the protocol's insufficient-scope challenge, not a generic denial. An empty scope list is treated as no scopes.
- `list_workpapers` and `read_workpaper` are annotated read-only. `annotate_workpaper` is not.
- Every caller sees the same static catalog. A read-only connection still sees `annotate_workpaper`, and calling it returns a refusal saying the firm approved this connection for reading only.
- Annotations are attributed to the consultant and also record the connection ID, so the firm can tell agent-made notes apart from notes typed in the app.

### Binding the token to the connection

The gate has to get the connection, and therefore the workspace, from something the provider has verified. It can't use something the client asserts. The preferred design: the consent step puts the chosen organization into the authorization, and the provider mints it as a verified claim on the access token, or returns it in the introspection response for opaque tokens. The connection is keyed by the provider's grant identifier plus that organization.

Before implementing this, decode a real access token from our provider configuration and confirm which of these it actually carries: audience, organization, and a per-grant identifier. Build the check from what the token really contains. If the provider can't bind one token to one organization, a consultant who authorizes the same client for two firms could end up with tokens the gate can't tell apart. That would leave constraint 1 resting on our own bookkeeping rather than on a verified fact. In that case, stop and raise it with the owner before building a token service of our own. See open question 1.

### Enterprise-managed authorization

If the provider natively supports the MCP Enterprise-Managed Authorization extension (ID-JAG listed in `authorization_grant_profiles_supported`), enable it in addition to standard OAuth. We build no custom exchange to get it. It changes how the consultant's identity reaches us, but not the rules above. The connection still binds to one workspace and still needs approval from that firm's Admin, because the consultant's own identity provider can't approve access on a client firm's behalf.

## Audit

Firms audit approvals, so connection events go into an append-only log scoped to the workspace. Rows are never edited or deleted while the workspace exists.

| Event | Recorded |
| --- | --- |
| `connection.requested` | consultant, agent client name and ID, redirect host, requested capabilities, time |
| `connection.approved` | approving Admin, approved capabilities, time, whether the Admin approved their own connection |
| `connection.denied` | Admin, time, optional reason |
| `connection.expired` | time |
| `connection.revoked` | who (Admin, consultant, or system), reason (`admin`, `consultant`, `membership_ended`), time |
| `connection.capabilities_changed` | Admin, before and after, time |

We also keep a per-connection tool-call log: tool, workpaper ID, outcome, time. Note contents and workpaper contents are not logged. This lets a firm answer "what did this agent touch" alongside "who let it in."

Admins can see and export the log in workspace settings. Other roles see only their own connections.

## Errors

Refusals use typed outcome codes with product copy. They never carry provider or framework text. Every refusal names the firm and the next step:

- `connection_pending_approval`: waiting for a firm Admin. No action needed from the agent.
- `connection_denied`, `connection_expired`, `connection_revoked`: reconnect to request access again.
- `membership_ended`: you're no longer a member of this firm.
- `capability_not_approved`: this connection is approved for reading only.
- `not_found`: no workpaper with that ID in this firm.

An expired or invalid token gets the protocol's re-auth challenge, so the host can refresh the token or re-run OAuth.

## Assumptions

These are calls I made without the owner. Each one can be reversed.

1. **Where roles live.** The provider organization has only admin and member roles. A firm Admin is a provider admin. Preparers and Reviewers are provider members, and the product's gate holds the Admin/Preparer/Reviewer distinction. This follows our usual practice of keeping fine-grained roles out of the provider, and it doesn't change the brief's three roles.
2. **Who may annotate.** All three roles may read and annotate. The Admin's approval is what narrows a connection.
3. **"Each connection" means each authorization.** A token refresh doesn't need re-approval. A new authorization always does.
4. **Approval doesn't block OAuth.** The token is issued at consent, and calls are refused until approval. The OAuth flow isn't held open waiting on an Admin.
5. **Pending requests expire after 7 days.**
6. **Approvals don't expire.** An approved connection lasts until it's revoked or the membership ends. If firms want periodic re-approval (for example, every 90 days), it's an easy addition.
7. **Self-approval is allowed and flagged.** A consultant who is also an Admin of the firm can approve their own connection, and the audit row marks it. If firms require a second Admin, the change is small, but a firm with only one Admin would then need a fallback.
8. **Any one Admin is enough.** We don't require several Admins to sign off.
9. **Agent access is on every plan.** Plans are per firm, but the brief doesn't say agent access is a paid feature, so the authorization gate makes no plan check. If agent access becomes a plan feature, the check goes in billing, not here.
10. **The tool-call log is ours to add.** The brief requires auditing approvals. I added a log of what each connection accessed because audit firms will ask for it.

## Open questions for the owner

1. **Provider binding.** Can our provider bind an access token to one organization chosen at consent (see [Binding the token to the connection](#binding-the-token-to-the-connection))? If it can't, do we accept a product-run token layer, or change providers?
2. **Firm-level policy.** Should a firm be able to turn off agent connections entirely, or limit which agent clients are allowed?
3. **Self-approval.** Do firm contracts allow it, or do they require a second Admin?
4. **Hosts with one credential per server.** Is the reconnect-to-switch-firms cost acceptable for the hosts our consultants actually use? We should test the main ones before launch.

````

> Result: File created successfully at: <run>\builds\2-workspace-bound-agent-grant-new-opus\work\docs\agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/agent-access.md`. It isn't committed. One thing needs checking before anyone builds on it: whether our auth provider can tie an access token to the single firm the consultant picks (open question 1 below).

**Main decisions:**
- **One connection reaches one firm.** All agents use a single server address, `https://mcp.<domain>/mcp`. When a consultant connects, they pick one firm, and that connection can never act in another firm's workspace. To work with a second firm, they connect again, and that firm's Admin approves it separately. I ruled out a single connection covering all of a consultant's firms, because the firm contracts forbid it.
- **Admin approval is a record we own.** Connecting finishes straight away and creates a pending connection. The firm's Admins get an email and a request in workspace settings. Until one of them approves, the agent's calls are refused with a clear "waiting for approval" message. An Admin can approve, narrow the connection to read-only, deny it or revoke it later.
- **Every call is rechecked.** The server confirms the connection is approved, that the consultant is still a member of that firm, and that their role, the Admin's approval and the token's permissions all allow the action. The firm comes from the connection, never from what the agent sends. A workpaper ID from another firm gets the same "not found" as one that doesn't exist. Removing a consultant from a firm cuts off their connection on the next call.
- **Audit log.** There's a permanent, per-firm log of every request, approval, denial, expiry, revocation and permission change. I also added a log of what each connection accessed, though the brief only asks for approvals to be audited.

**Assumptions** (listed in the doc, each easy to reverse):
- Admin, Preparer and Reviewer are enforced by the product. In the auth provider, Admins are admins and everyone else is a plain member.
- All three roles can read and annotate; the Admin's approval is what narrows a connection.
- Refreshing a token doesn't need re-approval, but every new connection does.
- Pending requests expire after 7 days. Approvals don't expire.
- Any one Admin can approve. A consultant who is also an Admin can approve their own connection, and the log flags it.
- Agent access is on every plan.

**Open questions for you:**
1. **The provider check.** Before building, someone needs to inspect a real token and see what it carries. If the provider can't tie a token to one firm, the guarantee would rest on our own records rather than on the provider. In that case we'd need to decide between building our own token layer and changing providers. I stopped short of designing that layer.
2. Should firms be able to turn agent connections off entirely, or limit which agent apps are allowed?
3. Do firm contracts allow Admins to approve their own connections?
4. Some agent apps keep only one login per server address, so a consultant on one of them would have to reconnect each time they switch firms. That's the cost of keeping firms separate, and we should test the apps consultants actually use.

**Session ended:** success, 7 turns, 109898 ms
