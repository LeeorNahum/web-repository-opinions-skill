**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-old-opus2/work\" && git ls-files | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5051 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md workspace-tenancy.md auth.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 21784 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat agent-tool-design.md http-apis.md admin.md | head -400"}`

> Result: # Agent Tool Design  Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.  **Destructive scope is never controlled by an optional field.** An omitted argument must never widen what gets deleted or silently c [... 7169 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-workspace-bound-agent-grant-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat routing.md ids.md integration-onboarding.md agent-plugins.md | head -300; cat ../../../../package.json ../../../../pnpm-workspace.yaml"}`

> Result: # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix [... 11532 more characters]

**Tool call `Write`:** `<run>/builds/4-workspace-bound-agent-grant-old-opus2/work/docs/agent-access.md`

````text
# Agent access over MCP

How a consultant's agent gets authorized to reach a firm's workpapers over MCP, and how Harbor Ledger makes sure a connection only ever reaches the one firm that approved it.

Status: proposed design, written while the owner was away. Calls made without the owner are listed under [Assumptions](#assumptions), and the points that need sign-off are under [Open questions](#open-questions). `docs/brief.md` stays the source of truth. Where this doc and the brief disagree, the brief wins.

## Requirements from the brief

1. Each firm is one workspace, backed by one auth-provider organization. Roles are Admin, Preparer, and Reviewer.
2. Consultants belong to several firms' workspaces at once.
3. Data from one firm can never be reached through a connection authorized for another firm.
4. A firm Admin approves each agent connection made into their workspace.
5. Firms audit those approvals.
6. Agents use `list_workpapers`, `read_workpaper`, and `annotate_workpaper`.

## The model in one paragraph

An **agent connection** is one OAuth authorization of the Harbor Ledger MCP resource by one consultant, for one agent client, into **exactly one workspace**. The consultant picks the workspace on the provider's consent screen, and that choice is bound into the token. Making the connection only creates a **pending** connection. It does nothing until an Admin of that workspace approves it in the app. Every tool call goes through one authorization gate, which:

- resolves the workspace from the token's verified organization context,
- requires an approved, unrevoked connection for that exact (consultant, client, workspace),
- requires that the consultant is still a member, and
- runs every data read and write inside that workspace only.

To work for a second firm, the consultant makes a second connection, and that firm's Admin approves it separately.

## Endpoint and catalog

- One remote MCP endpoint: `https://mcp.<domain>/mcp`. It is its own protocol app (`apps/mcp`), built with Hono and the official MCP SDK's web-standard transport. Requests are stateless and responses are buffered JSON.
- There is **one canonical OAuth resource** for every workspace. We don't use per-workspace paths, subdomains, or resources. Picking a different workspace means a new authorization of the same resource ([workspace tenancy](../.claude/skills/web-repository-opinions/references/workspace-tenancy.md)).
- **Every caller sees the same static tool catalog**, whether its connection is pending, approved, or read-only. Many hosts cache the catalog on first connect, so a catalog that changed with approval state would leave them working from a stale list. Approval state is enforced per call, and a refusal comes back as a clear error.
- Tools and their annotations:

  | Tool | Scope | Annotation |
  | --- | --- | --- |
  | `list_workpapers { query?, cursor? }` | `workpapers:read` | read-only |
  | `read_workpaper { id }` | `workpapers:read` | read-only |
  | `annotate_workpaper { id, note }` | `workpapers:annotate` | not read-only, additive, not destructive |

- Every tool result carries `workspace: { id, name }`, so an agent working across several firm connections can always tell which firm a result came from. This is an addition to the result schema. No new tool is needed.

## Connection lifecycle

```text
consultant adds server in agent host
  → OAuth (dynamic client registration if the host uses it)
  → provider consent: consultant selects ONE workspace they belong to, sees requested scopes
  → token issued, bound to that organization
  → first MCP call: gate finds no connection row → creates it as `pending`, notifies that workspace's Admins
  → Admin approves (optionally narrowing scopes) or denies in the app
  → approved: calls succeed within approved scopes ∩ consultant's role
```

States: `pending` → `approved` | `denied`. From `approved` → `revoked`. Denied and revoked are final. To get access again, the consultant connects again, which creates a new pending connection with a new approval.

**What counts as "a connection"** is the tuple (provider user subject, OAuth client ID, workspace). It needs an Admin decision when:

- a consultant connects a new agent client,
- a consultant connects into a workspace they haven't connected to before, or
- a consultant reconnects after a denial or revocation.

Token refreshes, and re-consent by the same client into the same workspace while still approved, reuse the existing approved connection. A re-consent that asks for **more** scopes than were approved goes back to `pending` for the extra scopes, and the already-approved scopes keep working in the meantime.

### Where the connection row is created

The row is created by the gate on the first call that carries a verified token with no matching row. We don't rely on a post-consent hook from the provider, so the product's record doesn't depend on a provider callback arriving. That first call, and any call while the connection is pending, gets this refusal:

> This connection to *Firm Name* is waiting for approval by one of its Admins. Ask an Admin of *Firm Name* to approve it under Settings → Agent connections. No workpapers can be read until then.

Denied and revoked connections get their own clear messages that say how to request access again.

### Admin approval surface

- Route: `/w/[workspaceId]/settings/agent-connections`, which shows pending connections first. Each connection has its own page at `/w/[workspaceId]/settings/agent-connections/[connectionId]`. IDs are 12-character Base58 entity IDs.
- Each request shows:
  - the consultant (name, email, and their role in this firm),
  - the agent client's registered name and redirect host, so the Admin can tell what is connecting,
  - the requested scopes,
  - the time of the first call, and
  - whether this consultant has other connections into this workspace.

  The page never shows anything about the consultant's other firms.
- Admin actions:
  - **Approve**, with all requested scopes or narrowed to read-only.
  - **Deny.**
  - **Revoke** an approved connection at any time.
- Only Admins see this surface. The server checks the Admin role on every approve, deny, or revoke. Hiding the entry point is only a convenience.
- When a connection goes pending, all Admins of that workspace get an in-app notice plus a transactional email. The email links to the connection's page and contains no workpaper data.

### Automatic revocation

A connection is revoked automatically, with a recorded reason, when:

- the consultant is removed from the workspace's organization (handled from the provider's membership webhook, and also enforced live by the gate's membership check),
- the consultant's account is closed, or
- the workspace is deleted.

A **role change does not revoke** a connection. Effective access is recomputed on every call (see below), so a demotion takes effect immediately without a new approval.

## The authorization gate

There is one gate module, and every MCP tool call goes through it. The MCP app has no other path to workpaper data: the backend functions it calls take a gate-issued context object, not a raw workspace ID. On every call, in order:

1. **Verify the token** with the provider's backend SDK, not with a framework MCP helper:
   - Always enforce the issuer.
   - Enforce the audience only if the token actually carries one, and reject a token whose audience names a different resource. The code must say why this check is conditional.
   - Require the advertised scopes as listed. An empty scope list is not the same as a missing one.
   - An insufficient-scope refusal uses the protocol's insufficient-scope challenge, not a generic 403.
2. **Resolve the workspace only from verified organization context**, meaning verified token claims or the provider's userinfo endpoint. If there is no organization context, fail closed. A tool argument, cursor, header, or unverified token body never picks the workspace.
3. **Load the connection** for (subject, client ID, workspace). Missing → create as `pending` and refuse. Pending, denied, or revoked → refuse with the matching message.
4. **Re-check membership** live. If the consultant is no longer a member of the workspace, revoke the connection and refuse.
5. **Compute effective capability:** the connection's approved scopes ∩ the token's scopes ∩ what the consultant's role allows:

   | Capability | Admin | Preparer | Reviewer |
   | --- | --- | --- | --- |
   | `workpapers:read` | yes | yes | yes |
   | `workpapers:annotate` | yes | yes | yes |

   The role column is the place to hold back a verb later, for example read-only Reviewers. It is kept separate from plan or billing gating.
6. **Run the tool inside the workspace.** The gate hands the backend a context of (workspace, consultant, connection). Every query is indexed and filtered by that workspace inside the backend transaction. Data is never fetched first and filtered afterwards.
   - `read_workpaper` / `annotate_workpaper` with an ID that belongs to another workspace returns the same **not found** as an ID that doesn't exist. Whether something exists in another firm is itself firm data.
   - `list_workpapers` cursors are opaque and carry the workspace they were issued for. A cursor from another workspace is rejected as invalid.
   - Annotations are written with the workspace, consultant, and connection taken from the gate context, never from arguments.

The same gate also serves the app UI and any future HTTP API. MCP-specific logic only covers steps 1–3.

## Audit trail

Each workspace has an append-only `agentConnectionEvents` log, readable by that workspace's Admins and exportable as CSV for the firm's auditors. Events:

- `requested`, with requested scopes and client name.
- `approved`, with the approving Admin and the approved scopes. It records `selfApproved: true` when the approver is the consultant.
- `denied`, with the Admin who denied it.
- `scopes_requested`, for an escalation.
- `revoked`, with who revoked it or why it was revoked automatically: membership removed, account closed, or workspace deleted.

Each tool call is also recorded against its connection, with the tool, workpaper ID, outcome, and timestamp. Note text and workpaper content are not copied into the log. A firm's audit export only contains its own workspace's rows.

## Cross-firm guarantees, restated

| Path a leak could take | What blocks it |
| --- | --- |
| Token from Firm A's consent used against Firm B data | Workspace comes only from the token's verified org. B's data is never queried. |
| Guessing a Firm B workpaper ID | Workspace-scoped query; same not-found as nonexistent |
| Replaying a Firm B list cursor through a Firm A connection | Cursor bound to its workspace; rejected |
| Consultant approved at A connects to B | New connection, `pending` until a B Admin approves |
| Consultant leaves A | Live membership check refuses; connection auto-revoked |
| Approval UI or audit showing other firms | Pages and exports only read the current workspace's rows |

## Assumptions

Calls I made without the owner:

1. **Granularity:** a connection is (consultant, agent client, workspace). Refreshes don't need re-approval. A new client or a new workspace does.
2. **Approval happens after consent, not during it.** The provider's consent screen can't ask a firm Admin anything, so the token is issued and the product refuses calls until approval. No workpaper data moves before an Admin approves.
3. **Admins may narrow the scopes they approve** (approve read-only even though annotate was requested), but they can't grant more than was requested.
4. **All three roles may read and annotate through an agent**, the same as in the app. That matches the brief, which doesn't restrict either verb by role.
5. **A consultant who is also an Admin of a firm may approve their own connection.** It is flagged as `selfApproved` in the audit, so the firm can see it.
6. **Approvals don't expire on their own.** They last until revoked, either by an Admin or automatically.
7. **Admins are notified** in the app and by transactional email.
8. **Agent access is available on every plan.** Plans are per firm, but gating MCP by plan would be a billing decision, kept out of this gate.
9. **Tool-call usage is audited along with approvals.** Note text and workpaper content are left out of the log.
10. Route token `/w/` for the workspace scope and the `agentConnectionEvents` name are placeholders that follow repo conventions. Nothing exists in code yet.

## Open questions

These need the owner or the provider to settle them:

1. **The provider must carry the selected organization into the OAuth access token** (or its userinfo). This whole design depends on that.
   - Before building, decode a real token from our provider's OAuth flow and confirm the organization claim is present and verified.
   - If the provider cannot bind a consent to an organization, **stop and decide with the owner**. The fallback is a product-owned workspace-selection step tied to the OAuth client ID. That is weaker, and it adds a custom layer that the tenancy guidance tells us to avoid.
2. **Token-to-resource binding.** If the provider issues tokens without an audience, a token minted for another resource of ours could be presented here. The issuer check plus the connection row (keyed by client ID) contain this. Record the residual risk in the gate code if it is confirmed.
3. **Several connections to one server in a host.** Some agent hosts allow only one connection per server URL. A consultant on such a host would have to swap workspaces by re-authorizing, rather than holding all firms at once.
   - Test each supported host and publish the client matrix.
   - Don't fix this with per-workspace URLs. That would break the "one canonical resource" rule.
4. **Enterprise-managed authorization (ID-JAG).** Check whether our provider lists `urn:ietf:params:oauth:grant-profile:id-jag` in its authorization server metadata. If it does, enable it alongside standard OAuth. It doesn't replace firm-Admin approval: the connection still lands `pending` in the firm's workspace.
5. **Should firms be able to require periodic re-approval** (for example yearly, to match audit cycles)? That would be a per-workspace setting. I left it out for now.
6. **Should self-approval be blocked** for firms that want strict separation of duties?

````

> Result: File created successfully at: <run>/builds/4-workspace-bound-agent-grant-old-opus2/work/docs/agent-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/agent-access.md`. I haven't committed it, and nothing is built yet. The whole design depends on one thing I couldn't check: the auth provider must record which firm was chosen during sign-in inside the agent's access token. Someone needs to decode a real token and confirm that before building.

**How it works:**
- **One connection, one firm.** A connection is one consultant's agent, authorized into exactly one firm's workspace. The consultant picks the firm on the provider's consent screen. A consultant who works for three firms makes three connections, and each firm approves its own.
- **Admin approval.** A new connection is "pending" and can't read anything. The firm's Admins get an in-app notice and an email, and approve, approve as read-only, or deny on a settings page (`/w/[workspaceId]/settings/agent-connections`). Until then, the agent gets a plain message saying an Admin of that firm needs to approve it. Admins can revoke at any time. Connections are revoked automatically if the consultant leaves the firm, closes their account, or the workspace is deleted.
- **Keeping firms apart.** Every tool call is checked in one place. The firm comes only from the verified token, never from tool arguments. The check requires an approved connection and current membership. Every query runs inside that firm's data:
  - A workpaper ID from another firm returns the same "not found" as an ID that doesn't exist.
  - Paging positions from one firm's list don't work in another firm.
- **Audit.** Each firm gets an append-only log of connection requests, approvals, denials and revocations, plus a record of each tool call. Admins can export it. Note text and workpaper content are left out.
- **Tools.** All three existing tools stay the same for every caller, whatever the approval state. Results gain a `workspace: { id, name }` field so an agent can tell which firm a result came from.

**What I assumed (full list in the doc):**
- A new agent, a new firm, or reconnecting after a denial needs fresh approval. Token refreshes don't.
- Admins can narrow a request to read-only but can't grant more than was asked for.
- All three roles (Admin, Preparer, Reviewer) can read and annotate through an agent.
- A consultant who is also a firm's Admin can approve their own connection, and the log marks it as self-approved.
- Approvals don't expire on their own.
- Agent access is available on every plan.

**Questions for you:**
- If the provider can't tie a token to the chosen firm, the fallback is a weaker firm-selection step we'd build ourselves. I'd want your decision before taking that route.
- Some agent apps only allow one connection per server address. Consultants using those would switch firms by re-authorizing rather than staying connected to all of them. Is that acceptable?
- Should firms be able to require periodic re-approval, for example once per audit cycle?
- Should firms be able to block Admins from approving their own connections?

**Session ended:** success, 8 turns, 104183 ms
