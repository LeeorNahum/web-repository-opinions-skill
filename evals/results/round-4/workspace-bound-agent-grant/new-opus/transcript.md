**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5051 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md auth.md"}`

> Result: # Workspace Tenancy  Give a product workspaces when shared ownership, membership, or policy needs them now or is on the product's roadmap, because retrofitting an ownership boundary costs far more than carrying one early. A product whose data will only ever belong to one person keeps it on the user account, with no organization layer. When a product's collaboration model is workspaces, back ever [... 24078 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat agent-tool-design.md http-apis.md admin.md modularity.md"}`

> Result: # Agent Tool Design  Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.  **Familiar operations first.** Shape the catalog around operations callers already know wherever they express the real domain. File  [... 13765 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat routing.md ids.md user-facing-errors.md | head -150"}`

> Result: # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix [... 11084 more characters]

**Tool call `Write`:** `<run>/builds/4-workspace-bound-agent-grant-new-opus/work/docs/agent-access.md`

````text
# Agent access over MCP

How a consultant's agent gets authorized to reach a firm's workpapers through the Harbor Ledger MCP server. `docs/brief.md` stays the source of truth. This doc builds on it, and every assumption made here is listed at the end for the owner to confirm.

## Contract requirements this design has to meet

From the brief:

1. Data from one firm can never be reached through a connection authorized for another firm.
2. A firm Admin approves each agent connection made into their workspace.
3. Firms audit those approvals.
4. Consultants belong to several firms' workspaces, and plans are per firm.

## Decision: one connection reaches one firm workspace

Each agent connection is **workspace-bound**. When the consultant gives consent, they pick exactly one firm workspace. Every token issued under that authorization can reach that workspace and nothing else.

A consultant who works for three firms makes three connections. Each one is a separate authorization of the **same** MCP resource, and each one is approved separately by that firm's Admin.

We rejected an account-wide grant, which would cover all of a consultant's memberships. Requirement 1 rules it out because such a token can reach every firm. Requirement 2 also has no single Admin who could approve it.

Two things are deliberately **not** done:

- **No per-firm MCP URL** (for example `/mcp/<firm>`) and no second resource. There is one canonical resource, `https://mcp.<domain>/mcp`. The workspace lives in the grant, not in the path.
- **No workspace argument on tools, and no "selected workspace" setting.** A tool argument, a remembered selection, or whatever firm the consultant last viewed in the web app never picks the target. The connection's binding is the only thing that does.

## Components

| Piece | Owner | Role |
| --- | --- | --- |
| Authorization server | Managed auth provider (one provider organization per firm workspace, per the brief) | OAuth 2.1 with dynamic client registration and PKCE. Handles sign-in, the consent screen with the workspace picker, and token issuance with the MCP resource as audience. |
| MCP server | Product protocol app at `https://mcp.<domain>/mcp` (Hono and the official MCP SDK, stateless, buffered JSON) | Verifies tokens with the provider's backend SDK, then calls the product's single authorization gate. |
| Authorization gate | Product backend | The one place that decides each call. The MCP server, the web app, and any future API all go through it. |
| Agent connection record | Product backend (owned by the product, not the provider) | Holds the approval state, the approved scopes, and the link to the audit trail for each authorization. |

### Agent connection record

```text
agentConnection
  id                  12-char Base58 entity id (shown in the Admin UI and URLs)
  workspaceId         the firm workspace this connection is bound to (never changes)
  userId              the consultant (provider subject stored on the app user)
  grantKey            the verified token fact that identifies this authorization (see "Binding")
  clientName          the agent host's registered client name, for display only
  requestedScopes     scopes the consultant consented to
  approvedScopes      scopes the Admin approved (a subset of requestedScopes)
  status              pending | approved | denied | revoked
  requestedAt, decidedAt, decidedBy, revokedAt, revokedBy, revokeReason
```

`workspaceId` never changes after creation. A different firm always means a new record.

## Scopes and capabilities

The scopes are the minimum set the existing tools actually use:

| Scope | Tools | Capability in the gate |
| --- | --- | --- |
| `workpapers:read` | `list_workpapers`, `read_workpaper` | `workpaper.read` |
| `workpapers:annotate` | `annotate_workpaper` | `workpaper.annotate` |

On every call, the gate allows the action only when all of the following hold:

```
the consultant has a live membership in connection.workspaceId
  AND their role in that workspace grants the capability
  AND the token's scopes include it
  AND connection.approvedScopes include it
  AND connection.status = approved
```

All scopes are published in the protected-resource metadata and in the `WWW-Authenticate` challenge, and the server enforces each one. A token missing a required scope gets the protocol's `insufficient_scope` response, not a generic denial. Watch for an empty scope list: it is not the same as a missing scopes field, and it must fail.

Role-to-capability defaults live in the product gate, not in the provider:

| Role | `workpaper.read` | `workpaper.annotate` | Approve agent connections |
| --- | --- | --- | --- |
| Admin | yes | yes | yes |
| Preparer | yes | yes | no |
| Reviewer | yes | yes | no |

Plans are a billing concern and stay out of this gate. See the assumptions.

## Flow

### 1. The consultant connects

1. The consultant adds `https://mcp.<domain>/mcp` to their agent host. The host finds the authorization server through the protected-resource metadata (served `no-store`, pointing at the provider's own metadata URL and not a proxied copy). The host then registers itself and starts OAuth with `resource=https://mcp.<domain>/mcp`.
2. The consultant signs in at the provider. The consent screen lists the scopes being requested and asks them to **choose one firm workspace** from their live memberships. It states plainly: "This connection can only reach *<Firm>*. An Admin of *<Firm>* must approve it before it works."
3. Tokens are issued with `aud` set to the MCP resource and the chosen workspace bound in a way the server can verify (see "Binding").
4. On the first verified call that carries a grant the product hasn't seen before, the product creates the `agentConnection` with `status = pending` and notifies the firm's Admins (in the app, and by email through the transactional provider).

### 2. A firm Admin approves

- Admins see pending, active, and past connections under workspace settings: `/w/<workspaceId>/settings/agent-connections`, with each one at `/w/<workspaceId>/settings/agent-connections/<connectionId>`.
- For each connection the page shows the consultant, the agent client name, the requested scopes, and when it was requested.
- The Admin can **approve** (optionally with fewer scopes, for example read-only), **deny**, or later **revoke**. Only the Admin role sees these controls, and the server checks the role again on every action.
- The consultant gets an in-app and email notice of the decision.

### 3. Calls

For every MCP request:

1. Verify the token with the provider's backend SDK: signature, issuer, expiry, and **audience must include the MCP resource**. A token without the audience is refused. That includes a token issued for the web app, or one issued for another resource.
2. Resolve `grantKey` and the bound workspace from **verified** token facts only. An unverified token body never picks a workspace.
3. Load the `agentConnection` and run the gate check above. The membership and role come from live data on every call, so removing a member or changing a role affects existing tokens on their next call with no wait for token expiry.
4. Run the tool **inside the bound workspace**:
   - `list_workpapers` searches only that workspace. Cursors are opaque and carry the workspace, and a cursor issued under another connection is rejected.
   - `read_workpaper { id }` and `annotate_workpaper { id, note }` look up the id within the bound workspace. An id from any other firm gives the **same "not found" result** as an id that doesn't exist, so the error doesn't reveal that the id exists elsewhere.
   - Annotations record `authorUserId` and `agentConnectionId`, so a firm can tell which notes came from an agent and through which approved connection.

The tool catalog stays the same for every caller. Authorization happens per call, and refusals come back as product-owned, protocol-neutral errors with one next step:

| Situation | Message to the agent (summary) |
| --- | --- |
| Connection pending | "This connection to *<Firm>* is waiting for a firm Admin to approve it." |
| Denied or revoked | "*<Firm>* has revoked access for this connection. Ask a firm Admin, or connect again." |
| Membership gone | "You're no longer a member of *<Firm>*." |
| Role or scope lacks capability | "This connection can read but can't annotate in *<Firm>*." |
| Id not in bound workspace | "No workpaper with that id in *<Firm>*." |

Raw provider and framework errors go only to logs.

### 4. Lifecycle

- **Refresh** continues the same authorization (same `grantKey`) and does not need a new approval.
- **A new authorization** creates a new connection that must be approved again. That includes re-adding the server, choosing a different firm, or consenting to more scopes.
- **Revocation** by an Admin, by the consultant (from their own account page listing their connections across firms), or automatically when the membership ends takes effect on the next call. Where the provider supports it, the product also revokes the provider grant, but the gate check is what guarantees the cut-off.
- If the consultant's account closes, all of their connections are revoked, and the closure record stops old tokens from coming back to life.

## Binding a token to one workspace

The guarantee depends on one fact that the server can verify on every call: **which authorization this token belongs to, and which workspace that authorization chose.**

Preferred: the provider binds the organization the consultant chose at consent into the access token (or into the introspection response for opaque tokens), together with a stable grant identifier. The server then keys `agentConnection` on `(grant id)` and refuses any token whose bound organization differs from `connection.workspaceId`.

Matching on `(user, client_id)` alone is **not enough**. A consultant who connects one agent host to two firms will usually reuse the same registered client, and the two connections would collapse into one.

**Before building, check this against real tokens.** Decode a real access token from the configured provider after a consent with an organization chosen, and confirm that the organization and a grant identifier are both present and verified. If the provider can't bind an organization at consent:

- Don't fall back to choosing the firm on the first call, by tool argument, or from the web app's active organization. Each of those breaks requirement 1.
- Write the gap down in the MCP server code and escalate to the owner. The options are a provider that supports organization-bound OAuth consent, or using the provider's Enterprise-Managed Authorization support if that carries the organization. A hand-built token service just to work around the gap is not on that list.

When the provider natively supports MCP Enterprise-Managed Authorization (it would list `urn:ietf:params:oauth:grant-profile:id-jag` in `authorization_grant_profiles_supported`), enable it **alongside** ordinary OAuth for firms that manage identity centrally. The Admin approval and gate rules stay exactly the same.

## Audit

Approvals are a contractual audit object, so their log is append-only and kept per workspace:

- Connection events: `requested`, `approved` (with scopes), `scopes_changed`, `denied`, `revoked` (by Admin, by the consultant, or automatically on membership end or account closure), each with actor, time, connection id, and consultant.
- Access events: one row per tool call, with connection id, tool, workpaper id (or the list query), and the outcome (allowed, or the refusal code). Notes are not copied into this log, because the annotation itself holds them.
- Firm Admins can view and export both from the connection detail page and a workspace-wide audit view. Raw diagnostics stay on the internal admin surface.

## Isolation checks to automate

- A token bound to Firm A calling `read_workpaper` with a Firm B id gets "not found", identical to a made-up id.
- A Firm A cursor replayed on a Firm B connection is rejected.
- Pending, denied, and revoked connections can't call any tool. After a revoke, the very next call fails.
- After a membership is removed, the next call fails even though the token hasn't expired.
- A token whose audience is missing or different is refused. So is a token whose bound organization differs from the connection's workspace, and so is a token with an empty scope list.
- A read-only approval can't annotate, even when the token holds `workpapers:annotate`.
- One consultant with two connections from the same agent host to two firms ends up with two separate records, each limited to its own firm.

## Assumptions to confirm

1. **Roles.** I read "Admin, Preparer, Reviewer" as product roles held in the app's gate, with the provider organization keeping only its built-in admin and member roles (provider admin = firm Admin). If you meant all three as provider roles, the gate logic doesn't change, but the role mapping does.
2. **Role capabilities.** All three roles can read and annotate. Only Admins approve connections. If Reviewers should be read-only, change one row in the gate table.
3. **Self-approval.** A consultant who is also an Admin of that firm can approve their own connection, and the audit log records that it was self-approved. Requiring a second Admin would lock out firms with only one Admin. Tell me if contracts require a separate approver.
4. **No approval expiry.** An approved connection stays approved until it's revoked or the membership ends. Periodic re-approval (for example yearly) would be easy to add if firms want it.
5. **Plans.** Agent connections are allowed on every firm plan, and any MCP usage counts against the **bound firm's** plan, never the consultant's or another firm's. Whether agent access is a paid feature is a billing decision and stays out of the authorization gate.
6. **Access logging.** I added a per-call access log alongside the approval log, assuming regulated firms will want to see what an approved agent actually read. The brief only requires auditing approvals.
7. **Agent writes.** `annotate_workpaper` is the only write, and it's additive, so it gets its own scope rather than a confirmation step. Each tool call stands alone and is safe to run unattended.
8. **Provider binding (blocker if false).** The managed provider can bind the chosen organization and a grant id into the MCP access token. This has to be checked against real tokens before implementation, as described in "Binding a token to one workspace".
9. **Pending state.** Tokens are issued right away and refused until an Admin approves, rather than holding up the OAuth flow. This works with hosts that time out long authorizations, and it lets the agent tell the consultant why calls are failing.

````

> Result: File created successfully at: <run>/builds/4-workspace-bound-agent-grant-new-opus/work/docs/agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/agent-access.md`. It's a design only: no code was written, nothing was tested against a real provider, and nothing is committed.

**What I decided:**
- **One connection reaches one firm.** When the consultant signs in to connect their agent, they pick one firm workspace. A consultant working for three firms makes three separate connections, and each firm's Admin approves its own. A single connection covering all of a consultant's firms would break the contract rule that one firm's connection can never reach another firm's data.
- **Same server address for every firm.** All connections use `https://mcp.<domain>/mcp`. The firm is fixed when the connection is authorized. It isn't part of the URL, it isn't a tool argument, and it doesn't follow whatever firm the consultant is viewing in the web app.
- **Admin approval.** A new connection starts as pending and every call is refused until a firm Admin approves it. The Admin can also approve it as read-only. Admins can deny or revoke a connection, consultants can revoke their own, and leaving the firm revokes it automatically. Each takes effect on the next call, because permissions are checked live on every call.
- **Permissions.** There are two: `workpapers:read` (list and read workpapers) and `workpapers:annotate`. A call goes through only if the consultant is still a member, their role allows the action, their consent and the Admin's approval both include it, and the connection is approved.
- **Firm separation in the tools.** All three existing tools only see the connection's firm. Asking for a workpaper id from another firm returns the same "not found" as an id that doesn't exist, so it doesn't reveal that the workpaper exists. Annotations record which connection made them.
- **Audit.** There's an append-only, per-firm log of approval events, plus one entry per tool call. Firm Admins can view and export both.

**One possible blocker:** this only works if the auth provider's access tokens record which firm the consultant chose and which authorization they belong to, and the server can verify both. Matching on the user and agent app alone isn't enough: one agent app connected to two firms would merge into a single connection. Someone needs to check this against a real token before building. If the provider can't do it, the doc says not to work around it by choosing the firm on the first call or from a tool argument, since both break the contract.

**Assumptions for you to confirm** (all listed at the end of the doc):
1. Admin, Preparer and Reviewer are roles the app manages itself, with the auth provider keeping only its own admin and member roles.
2. All three roles can read and annotate, and only Admins approve connections.
3. A consultant who is also an Admin of that firm can approve their own connection, and the log marks it as self-approved.
4. Approvals don't expire.
5. Agent access is allowed on every firm plan, and usage counts against the plan of the firm the connection belongs to.
6. I added the per-call access log; the brief only requires auditing approvals.
7. Annotating gets its own permission rather than a confirmation step.
8. Tokens are issued straight away and refused until an Admin approves, rather than making the sign-in wait.

**Session ended:** success, 8 turns, 113107 ms
