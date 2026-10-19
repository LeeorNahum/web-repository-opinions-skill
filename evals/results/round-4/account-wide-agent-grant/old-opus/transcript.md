**Prompt:** Design the authorization model behind our MCP tools, including the create tool we still need, and the workspace handling on the library page. Write it to docs/workspace-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-account-wide-agent-grant-old-opus/work\" && git ls-files | grep -v node_modules | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5601 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-account-wide-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md agent-tool-design.md"}`

> Result: # Workspace Tenancy  When a product's collaboration model is workspaces, back every workspace with the auth provider's organization object, the user's first workspace included. One organization per workspace gives every workspace the same membership, invitation, role, and token contract from day one, and the provider's verified organization context becomes the one workspace authority every surfa [... 14276 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-account-wide-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat app-surface.md routing.md query-state.md auth.md bootstrap.md"}`

> Result: # App Surface  The signed-in app owns the core workflow and private state. It should not carry public SEO routes without a deliberate reason.  Responsibilities:  - Authentication and session - Private data and product workflows - Account and billing - Admin - Provider-backed actions - Private routing  The app surface feels like its core object first. Secondary features attach to that  [... 23809 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-account-wide-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat product-ux.md ids.md data-model.md quota.md source-of-truth.md"}`

> Result: # Product UX  Design every screen around a real human path, not a template average of nearby patterns. A product surface can be locally correct and globally incoherent. Judge the whole, not just the parts.  For each page, decide what the viewer should notice first, next, and last, then build to that order.  - Give every page one clear primary path or action. No dead-end screens. - Hide acti [... 11639 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-account-wide-agent-grant-old-opus/work\" && cat package.json pnpm-workspace.yaml; ls docs"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*" brief.md

**Tool call `Write`:** `C:\tmp\wro-eval3\builds\3-account-wide-agent-grant-old-opus\work\docs\workspace-access.md`

````text
# Workspace access

Status: proposal, written 2026-10-18 while the owner was away. `docs/brief.md` wins wherever the two disagree. Calls made without the owner are collected under [Assumptions to confirm](#assumptions-to-confirm), most consequential first.

This document covers:

1. The single authorization gate shared by the app and the MCP tools.
2. How an MCP connection reaches workspaces (one connection covers all of them).
3. The MCP tool catalog, including the new `create_document` and `list_workspaces`.
4. Workspace handling on the library page, which replaces the beta's active-workspace switcher.

## Facts this builds on (from the brief)

- One provider organization per workspace, including the one created at sign-up. Roles: Owner, Editor, Viewer.
- Every document belongs to exactly one workspace.
- A document can be shared with one person by email. That person sees that document only.
- Storage is priced per paying owner. Each workspace has a flat 25-member cap as an abuse limit.
- Two problems from the beta: a header switcher led people to create documents in the wrong workspace, and studio leads lost track of changes across clients.
- Studio leads want one agent connection that works across their client workspaces.

## 1. One gate

Every surface goes through one backend module: the signed-in app, the MCP server, and any future API or job. The rest of the codebase calls only this:

```ts
authorize(principal, capability, target) -> Allowed | Refusal
```

### Principal

```ts
type Principal =
  | { kind: "session"; userId: string }
  | { kind: "agent"; userId: string; connectionId: string }
```

An agent always acts **as a person**. It never gets more than that person has, and it can be narrowed further (see §2). Wherever we record who changed something, the record stores both the user and the connection.

### Capabilities

| Capability | Owner | Editor | Viewer | Share: edit | Share: view |
| --- | --- | --- | --- | --- | --- |
| `workspace.list` (see the workspace exists, name, own role) | yes | yes | yes | no | no |
| `document.list` | yes | yes | yes | that document only | that document only |
| `document.read` | yes | yes | yes | yes | yes |
| `document.create` | yes | yes | no | no | no |
| `document.update` | yes | yes | no | yes | no |

Capabilities not covered here (sharing, deletion, members, billing) go into the same table when they're designed. A capability missing from the table is refused.

### Decision order (every call, nothing cached across calls)

1. **Identity.** Session: verify it with the auth provider. Agent: verify the access token with the provider's backend SDK. Always check the issuer. Check the audience only if the token actually carries one, and add a code comment explaining why. Require every scope we advertise (§2). Refuse accounts that have been closed.
2. **Target → workspace.** For a document, use the document's stored workspace. For a create, use the explicit `workspace` id the caller passed. Never use a default, a last-used workspace, or session state.
3. **Access path.**
   - **Membership:** the user's current role in that workspace, read from the membership mirror. Provider organization webhooks keep that mirror up to date.
   - **Direct share:** a share row for (document, user), carrying `view` or `edit`.

   If neither path exists, refuse as **not found**. The response must not reveal that the workspace or document exists.
4. **Role/share term:** the capability table above.
5. **Agent-only terms** (skipped for `session`):
   - The connection's workspace allowlist includes this workspace, or includes "shared with me" for a shared document (§2).
   - The connection's access level allows this capability (`read` covers list/read; `read-write` adds create/update).
   - The document's workspace allows connected agents (§2, workspace policy).
6. **Plan term, create/update only:** a storage check against the **workspace owner's** plan, not the caller's. This is a quota check, kept separate from authorization: refuse before writing if the content can't fit, and record usage only after the write is durable.

Access is the intersection of every term. Removing someone from a client workspace takes effect on their agent's next call, with no token revocation needed. Residual risk: if the membership mirror lags a webhook, a removed member's agent may keep access for those seconds. That's accepted for v1. Write-heavy paths may re-read the membership from the provider if that ever matters.

Defense in depth: the UI and the MCP adapter hide or reject actions they know will fail. The gate still decides.

## 2. MCP connection model: one grant across workspaces

### Decision

A user connects their agent **once**. The grant identifies the user, not one workspace. On each call the gate works out which workspace the call touches (step 2 above) and checks it against the user's live membership. A workspace the user joins later is reachable with no reconnect. That's what the brief's feedback asks for.

This departs on purpose from the repo skill's default (consent picks one organization, switching means re-authorizing). It keeps that default's safety property: **the workspace is always resolved from verified identity plus verified membership.** A `workspace` argument works like a workspace segment in a URL: it chooses among workspaces the caller can already reach, and it never grants access.

### Endpoint and protocol

- One remote endpoint: `https://mcp.<domain>/mcp`, served as its own protocol app (Hono + the official MCP SDK, stateless, buffered JSON).
- One OAuth protected resource. Serve its metadata with `no-store`, and point clients at the auth provider's own authorization-server metadata.
- Scopes: advertise only what the provider actually issues and what we enforce. Before writing the check, decode a real token. If the provider can issue custom scopes, use `documents:read` and `documents:write`, both enforced. If it can't, advertise none and use the connection's access level (below) for read-only. Write down whichever applies in the MCP app.
- Enterprise-Managed Authorization (ID-JAG): enable it in addition to standard OAuth only if the provider supports it natively. Don't build our own exchange.

### Connection record (product-owned)

On a user's first agent call from an OAuth client, create a row keyed by (user, OAuth client id):

| Field | Default | Meaning |
| --- | --- | --- |
| `workspaces` | `all` | `all` (includes future workspaces) or an explicit list of workspace ids |
| `includeShared` | `true` | Whether documents shared directly with the user are reachable |
| `access` | `read-write` | `read` or `read-write` |
| `revokedAt` | — | Revoking also revokes the provider grant. The row stays for history. |

Users manage these under **Account → Connected agents**: list connections, narrow them, revoke them. A narrowed or revoked connection stays listed and marked as such; it doesn't disappear.

### Workspace policy (owner control)

Each workspace has the setting **"Allow members' connected agents"**, default **on**, and only Owners can change it. When it's off, every agent principal is refused for that workspace's documents, including documents shared directly from it. Session use isn't affected. This gives a client a way to say "people can work in our workspace, but their AI agents can't".

### Why the wider grant is acceptable

- An agent can never do more than its person could do by hand in the app.
- Membership, role, share, owner policy, and connection narrowing are all checked live, on every call.
- Every agent write is attributed (user + connection), so the cross-client view (§4) shows what an agent changed and where.
- The main new risk is **cross-client exfiltration**. One agent session can read client A and write into client B, for example after prompt injection from a document's content. Owner policy and connection narrowing are the mitigations. We don't try to block content from moving between workspaces in the gate. Those mitigations are the reason the setting and the "Connected agents" page ship in v1 and aren't left for later.

## 3. MCP tool catalog

Every caller sees the same static catalog. Each call is authorized individually. A tool the caller can't use still appears in the catalog; calling it returns an instructive refusal.

| Tool | Input | Annotations | Change |
| --- | --- | --- | --- |
| `list_workspaces` | `{}` | read-only | **new** |
| `list_documents` | `{ query?, workspace?, cursor? }` | read-only | adds the optional `workspace` filter |
| `read_document` | `{ id }` | read-only | result now includes workspace |
| `create_document` | `{ workspace, title, content? }` | not read-only, not destructive, not idempotent | **new** |
| `update_document` | `{ id, content }` | destructive (replaces content), idempotent | result now includes workspace |

### `list_workspaces`

Opening sentence of the description: "List the workspaces you can reach, with their ids, names, and your role." Each item: `{ id, name, role, agentAccess: "read" | "read-write" | "blocked", blockedReason? }`. Every workspace the user belongs to is listed, including blocked ones, which carry the reason (owner policy or connection narrowing). Agents need this to get a workspace id for `create_document`.

### `list_documents`

With no `workspace`, it returns everything the connection can reach: member workspaces plus shared documents. An omitted optional field only *widens a read* here; it never widens a write. Each item: `{ id, title, workspace: { id, name } | null, shared: boolean, access: "view" | "edit", updatedAt, updatedBy }`. A shared document's `workspace` is `null`. The recipient never sees the owning workspace's name, keeping to "that document only". `updatedBy` says when a change came through a connected agent.

### `read_document`

Unchanged input. It stays singular, so documents aren't read in batches.

### `create_document`

- `workspace` is **required** and must be a stable workspace id. There's no default and no name matching. This is exactly the beta's wrong-workspace bug, so the agent has to say where the document goes.
- If the id is unknown or the caller isn't a member, the refusal reads: "No workspace with that id is available to you. Call list_workspaces for valid ids." Not-a-member and nonexistent get the same message.
- Viewer, blocked, or a read-only connection: the refusal names which term blocked it.
- Storage over the owner's plan: the refusal names the measured shortfall and says the workspace owner can raise their plan.
- Returns `{ id, title, workspace: { id, name }, url }`, with `url` = the document's app URL (§4).
- Document ids use the shared 12-character Base58 generator.

### `update_document`

Unchanged input (stable `id`; documents aren't resolved by name). Returns `{ id, workspace, updatedAt }`. Its annotation says destructive because it replaces content.

### Refusals (all tools)

Error codes are typed and use plain, protocol-neutral copy: `not_found`, `role_insufficient`, `agent_blocked_by_workspace`, `connection_excludes_workspace`, `connection_read_only`, `storage_limit_reached`. Each one names the next step. None of them echo document content or reveal workspaces the caller can't see.

## 4. Library page

### Decision: no active workspace

The beta's header switcher is removed, and nothing replaces it as hidden state. The library is a single view across all workspaces. "Which workspace" is a filter in the URL or an explicit field on create. It's never ambient session state.

### Routes

| Path | View |
| --- | --- |
| `/documents` | Library: every document the user can reach, across all workspaces plus "Shared with me" |
| `/documents/[id]` | A document |
| `/w/[workspaceId]` | Workspace entity. Resolves with a history *replace* to `/documents?workspace=[workspaceId]` |
| `/w/[workspaceId]/settings` | Workspace settings and members (provider panel, relabeled in our vocabulary), including the agent policy |
| `/account/agents` | Connected agents |

Document URLs sit at the top level, not under a workspace, because:

- direct-share recipients aren't workspace members and must never see a workspace URL;
- a document link should keep working if moving documents between workspaces ever ships.

Each document header shows its workspace (or "Shared with you"). Unknown or unauthorized ids show the same product-owned "not found" screen.

### Query state (canonical order)

`q` → `workspace` → `sort` → `new`

- `q`: search text.
- `workspace`: a workspace id, or the reserved value `shared` for "Shared with me". It can't collide with an id, since ids are always 12 characters. Omitted = all.
- `sort`: `updated` (default, omitted when untouched) or `title`.
- `new=true`: opens the create dialog (see below).
- Parsing and serialization live in one shared module with contract tests. Unknown values are rejected.

### Layout

- The toolbar holds search, a **workspace filter** (All · each workspace · Shared with me), and sort.
- Rows show title, a workspace badge, last edited time, and who edited it, e.g. "Dana via Claude" for an agent edit. Default sort is most recently updated across everything. That's the answer to "lost track of what changed across clients."
- No counts or sizes on rows unless they change what the viewer does next.

### Creating a document

- **New document** opens `/documents?new=true`. The dialog's first field is **Workspace**, followed by the title.
- Which workspace is preselected:
  - if the library is filtered to one workspace where the user can create, preselect that one, visibly;
  - if the user can create in exactly one workspace, preselect it;
  - otherwise nothing is preselected, and the user has to choose before Create is enabled.

  Never preselect a "last used" workspace.
- Only workspaces where the user is Owner/Editor are offered. With none (e.g. shared-only users), **New document** is hidden rather than disabled.
- The same gate as `create_document` handles authorization. Error copy and quota behavior match too.

## Out of scope here

- Moving documents between workspaces.
- Share permission management UI.
- Deletion.
- Seat/billing mechanics. Per the brief, the flat 25-member cap applies, and **connected agents never count as members**.

## Assumptions to confirm

1. **One account-wide agent grant** (§2) instead of one grant per workspace. It contradicts our own skill's default, but it's what the brief's feedback asks for. If you prefer per-workspace grants, the gate keeps the same shape: the connection's `workspaces` becomes the single consented workspace, and `list_workspaces` returns one entry.
2. **Workspace owners can block members' agents, default on (agents allowed).** The alternative is default off for workspaces the user doesn't own. That's safer for clients, but it brings back the per-client friction.
3. **Connections can be narrowed (workspaces, read-only) on our side** and default to everything plus read-write.
4. **Direct shares carry `view` or `edit`.** The brief doesn't say which. If shares are view-only, drop the edit column.
5. **Shared documents are reachable by agents** (`includeShared` defaults to true), and their owning workspace's name is hidden from the recipient.
6. **Viewers can't create, Editors can.** Owners can do everything listed. Owner-only capabilities come later (settings, policy).
7. **Storage on create/update is charged to the workspace owner's plan**, not to whoever is acting. That's how I read "priced by storage per paying owner."
8. **The library is account-level at `/documents`**, documents live at top-level `/documents/[id]`, and there's no per-workspace library route. The workspace is a URL filter.
9. **Auth provider is Clerk** (the repo skill's default; the brief only says "managed provider"). Nothing here depends on Clerk-specific features. Token claims and scope support still have to be checked against a real token before the MCP verifier is written.
10. **"Last edited by" / agent attribution** is new data (user + connection on each write). It's needed for the cross-client view and for auditing agent writes.

````

> Result: File created successfully at: C:\tmp\wro-eval3\builds\3-account-wide-agent-grant-old-opus\work\docs\workspace-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/workspace-access.md`. I haven't committed it, and no code exists yet; the repo is an empty scaffold.

**Decisions I made**

1. **One gate for everything.** The app and the MCP server both call a single `authorize(principal, capability, target)` check. An agent always acts as its person and can never do more than that person could. Every call re-checks:
   - the person's current role in the workspace, or a direct share on the document;
   - the connection's limits;
   - whether the workspace allows agents at all;
   - storage against the workspace owner's plan, for create and update.
2. **One agent connection covers all workspaces.** A studio lead connects once and reaches every workspace they belong to, including ones they join later. Each call works out its workspace from the document, or from an explicit workspace id, and checks it against real membership. Being removed from a client workspace cuts off their agent on its next call.
3. **Safeguards for the wider connection:**
   - Workspace owners get an "Allow members' connected agents" setting.
   - Each person gets a Connected agents page where they can limit a connection to some workspaces, make it read-only, or revoke it.
   - Every agent edit is recorded as "Name via Agent".
4. **Tools.**
   - New `list_workspaces`, so an agent can look up workspace ids.
   - New `create_document { workspace, title, content? }`. The workspace id is required, with no default and no matching by name, because creating in the wrong workspace was the beta's bug.
   - `list_documents` gets an optional workspace filter.
   - All results now say which workspace a document is in. People who were only sent a single document by email never see that workspace's name.
5. **Library page.**
   - The header workspace switcher is gone.
   - `/documents` shows one library across all workspaces plus "Shared with me", newest changes first, with a workspace badge on each row. The workspace filter lives in the URL.
   - The New document dialog has Workspace as its first field. It's only pre-filled when the choice is clear (the library is filtered to one workspace, or you can only create in one), never from "last used".
   - Documents get their own top-level link, `/documents/[id]`, so people sent a document by email never see a workspace link.

**Assumptions to confirm** (the doc's last section lists all ten)

- **The one-connection decision, above all.** It goes against our own skill's default of one connection per workspace, which I set aside because the brief's feedback says reconnecting per client was the top complaint. The main new risk is one agent session copying content from one client into another, for example if a document contains instructions aimed at the agent. The safeguards above limit this but don't prevent it. If you'd rather have one connection per workspace, the design switches over cleanly.
- **Agents are allowed by default** in workspaces the person doesn't own. Defaulting to off would protect clients more but bring back the per-client friction.
- **Email shares can be either view or edit.** The brief doesn't say.
- **Storage is charged to the workspace owner's plan**, not to whoever makes the edit.
- **The auth provider is Clerk.** That's the skill's default; the brief only says "managed provider". Before writing the token check, we still need to look at a real token to see what claims and scopes it carries.

**Session ended:** success, 9 turns, 178069 ms
