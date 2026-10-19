**Prompt:** Design the authorization model behind our MCP tools, including the create tool we still need, and the workspace handling on the library page. Write it to docs/workspace-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus2/work\" && git ls-files | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5601 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md agent-tool-design.md"}`

> Result: # Workspace Tenancy  Give a product workspaces when shared ownership, membership, or policy needs them now or is on the product's roadmap, because retrofitting an ownership boundary costs far more than carrying one early. A product whose data will only ever belong to one person keeps it on the user account, with no organization layer. When a product's collaboration model is workspaces, back ever [... 19441 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus2/work/.claude/skills/web-repository-opinions/references\" && cat query-state.md app-surface.md routing.md auth.md ids.md user-facing-errors.md"}`

> Result: # Query State  Put shareable collection state in the URL so a reload, copied link, browser navigation, and server render restore the same view.  ## Parameter Contract  - Use `q` for the primary free-text search query. - Use readable enum values and `true` or `false` for booleans. - Omit empty values and state the user has not chosen. - Preserve an explicitly selected default when that cho [... 28317 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus2/work\" && cat package.json pnpm-workspace.yaml && cat .claude/skills/web-repository-opinions/references/quota.md | head -60"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*" # Quota  Check quota before doing expensive work, reserve it when concurrent  [... 2259 more characters]

**Tool call `Write`:** `<run>\builds\4-account-wide-agent-grant-new-opus2\work\docs\workspace-access.md`

````text
# Workspace Access

How Alderdocs decides who and what may touch a document: the authorization gate, the MCP agent grant and its tools (including the new `create_document`), and how the library page handles workspaces.

This builds on the decisions in [brief.md](brief.md). Choices the owner hasn't confirmed yet are marked **Assumption** and gathered in [Open assumptions](#open-assumptions) at the end.

## Principles

1. **One gate.** Every surface (web app, MCP, any future API or CLI) calls the same product functions, and all authorization happens inside them. MCP tools are thin adapters and never make their own access decisions.
2. **Every call says which workspace or document it targets, and the server checks it.** No surface has an "active workspace" that decides where a call lands. A browsing filter, a remembered selection, or a token's organization claim never picks the target.
3. **Every call rechecks live access.** Revoking a membership or a share affects existing sessions and agent tokens on their next call, with no reconnecting or token expiry needed.
4. **Fail closed.** Missing identity, an unknown capability, or a target with no covering membership or share gives one clear product error.

## Principals and access sources

A caller is always a **verified Alderdocs user**: a web session, or an MCP access token issued to that user. A caller reaches a document through exactly one of these:

| Source | Grants | Never grants |
| --- | --- | --- |
| **Membership** in the document's workspace, with role Owner, Editor, or Viewer | Capabilities of that role across the workspace's documents | Anything in another workspace |
| **Individual share** of that document, with a share role | Capabilities of the share role on that one document | The workspace's other documents, its member list, its name beyond what the share view shows, or creating anything in it |

If a caller has both a membership and a share on the same document, they get the union of the two.

### Roles and the provider

- The brief decided on one provider organization per workspace (Clerk Organizations by default), including the workspace created at sign-up. That first workspace is an ordinary workspace with no special flag, and personal-account (no-organization) mode is turned off.
- **Assumption:** the provider only holds its built-in roles. The workspace Owner is the provider's `admin`, and everyone else is `member`. Owner, Editor, and Viewer are product roles stored on the app's membership row and enforced by the gate. This keeps capabilities ours whichever provider holds membership. I read "Roles: Owner, Editor, Viewer" in the brief as the product's roles, not a requirement to create custom provider roles.
- The provider owns membership. The app keeps a mirror of memberships that provider webhooks update (signature-verified, deduplicated by event ID, idempotent), and the gate reads that mirror. A removal takes effect when its webhook lands, normally within seconds.
- **Member cap 25:** enforced at the product's membership gate and mirrored onto the provider's per-organization membership cap, so invitations past 25 fail at send time (the provider also counts pending invitations). The instance default cap is 1, so a workspace whose mirror hasn't synced fails closed. **Assumption:** share recipients aren't members and don't count toward the 25.

### Capabilities

Every action maps to a named capability. Access = capability granted by the role or share ∩ the token's scope (for MCP).

| Capability | Owner | Editor | Viewer | Share: Editor | Share: Viewer |
| --- | --- | --- | --- | --- | --- |
| `document.list` (see it in listings) | ✓ | ✓ | ✓ | that doc only | that doc only |
| `document.read` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `document.update` | ✓ | ✓ | – | ✓ | – |
| `document.create` (in the workspace) | ✓ | ✓ | – | – | – |
| `document.share` | ✓ | ✓ | – | – | – |
| `workspace.manage_members` / settings | ✓ | – | – | – | – |

**Assumption:** a share has a role (Viewer or Editor) that the sharer picks, defaulting to Viewer. The brief only says a document "can be shared with one person by email".

**Assumption:** a share sent to an email with no Alderdocs account is held as a pending share. It's claimed when someone signs in with that **verified** email, and it's never matched on an unverified address.

## Agent grant (MCP)

### Scope: account-wide

Studio leads want one connection that works across their client workspaces, and reconnecting per client was the top complaint about a competitor. So **the MCP grant is account-wide.** It covers:

- every workspace the user is a member of now,
- every workspace they join later, with no reconnecting,
- every document shared with them individually.

It's limited throughout by the user's live role or share on each target, and by the token's scopes. Leaving a workspace or losing a share removes the agent's access on its next call.

The consent screen states this plainly, for example: *"Let <client> read and edit Alderdocs documents in every workspace you belong to, including ones you join later, and documents shared with you."*

**Not built now:** a workspace-bound grant (consent picks one workspace) for customers whose policy says a connection must never reach another client. If it's needed later, it's a second authorization of the **same** OAuth resource with a workspace restriction recorded on the grant, never a per-workspace MCP URL or a second resource.

### OAuth scopes

Only scopes the server actually enforces are advertised:

- `documents:read`: `list_workspaces`, `list_documents`, `read_document`
- `documents:write`: `create_document`, `update_document`

**Assumption:** the default consent requests both scopes. A client may request only `documents:read`. A call that's missing a required scope gets the protocol's `insufficient_scope` challenge (HTTP 403 with `WWW-Authenticate`), not a generic denial.

### Server and token verification

- One endpoint: `https://mcp.<domain>/mcp`, deployed as its own protocol app (Hono with the official MCP SDK's web-standard transport), stateless, with buffered JSON responses.
- Tokens are verified with the auth provider's backend SDK. Issuer is always checked. The MCP resource **must** be in the token's audience, and the provider is configured to issue it. A token without it is rejected.
- The token's subject is the user. **Any organization claim in the token is ignored for authorization.** The target is resolved and checked per call as described below.
- Protected-resource metadata is served with `Cache-Control: no-store` and points at the authorization server's own metadata URL, which is not proxied.
- Enterprise-Managed Authorization (ID-JAG) is enabled alongside standard OAuth **only** if the provider supports it natively (it lists `urn:ietf:params:oauth:grant-profile:id-jag` in `authorization_grant_profiles_supported`). Nothing custom is built for it.

### Per-call resolution

Every tool call runs these steps:

1. Verify the token (issuer, audience, expiry) and load the user by provider subject. If the user is unknown or the account is closed → `unauthorized`.
2. Check the tool's scope against the token → `insufficient_scope`.
3. Resolve the target:
   - Document-addressed calls (`read_document`, `update_document`): load the document, then find the caller's live membership in **its** workspace or a live share of **it**.
   - Workspace-addressed calls (`create_document`): use the `workspaceId` argument, then find the caller's live membership in it. Shares never count here.
   - Listing calls: compute the set of workspaces where the caller is a member, plus their shared documents.
4. Check the role or share capability → `insufficient_role`, or `not_found` if there's no membership or share at all.
5. Run the product operation, which checks again inside its own transaction (defense in depth; the transaction is the boundary).

A document that doesn't exist and a document the caller can't reach both return the same `not_found`, so IDs can't be used to probe for existence.

### Tool catalog

Every caller sees the same static catalog. A caller with no write access to anything still sees the write tools, and calls to them reach the gate and return an instructive error. A catalog that shifts per caller strands clients that cache it on first connect.

| Tool | Scope | Annotations |
| --- | --- | --- |
| `list_workspaces {}` **(new)** | read | readOnly |
| `list_documents { query?, workspaceId?, cursor? }` (adds optional `workspaceId`) | read | readOnly |
| `read_document { id }` | read | readOnly |
| `create_document { workspaceId, title, content }` **(new)** | write | not readOnly, not destructive, not idempotent |
| `update_document { id, content }` | write | not readOnly, **destructive** (replaces content), idempotent |

**`list_workspaces`**: returns each workspace the caller is a member of: `id`, `name`, `role`, and `canCreate`. The agent needs this to get a stable `workspaceId` for `create_document`, including for a new workspace that has no documents yet. Workspaces the caller only reaches through shares aren't listed.

**`list_documents`**: account-wide by default. It returns documents from every membership plus documents shared with the caller, sorted by most recently updated, so "what changed across clients" is one call. Each result carries `id`, `title`, `updatedAt`, a `url`, and an `access` field:

- `{ kind: "member", workspaceId, workspaceName, role }`
- `{ kind: "shared", role, sharedBy }`

For shared results, no workspace name or ID is included (consistent with "sees that document only"). `workspaceId` narrows the list to one workspace the caller is a member of. It's a filter on what's returned, not authority, and a `workspaceId` the caller isn't a member of returns `not_found`.

**`read_document`**: unchanged arguments. It returns the shared document resource schema, including `access`, and records which version it served to this grant (used by `update_document`).

**`update_document`**: unchanged arguments. The server refuses with `conflict` if the document changed since the version it last served to this grant in a complete read, or if this grant has never read it. The error asks for a fresh `read_document`. No revision-token argument is added. A retry is safe because it writes the same content.

**`create_document`**:

- `workspaceId` is **required**, a stable ID (no name lookup). It doesn't default to the sign-up workspace, the last workspace used, or the token's organization. Leaving it out is a schema error that tells the agent to call `list_workspaces`. This is the agent-side fix for the beta's "created in the wrong workspace" problem.
- Requires `document.create` in that workspace (Owner or Editor). A Viewer gets `insufficient_role`, which names the role the agent has. Shares never authorize a create.
- `title` and `content` use the same content format as `update_document`. **Assumption:** title is a separate field from content. If the document model derives the title from the content, drop `title`.
- Checks storage first: content size is checked against the **workspace owner's** plan storage allowance (plans are priced by storage per paying owner) and reserved atomically, and usage is recorded only after the document is durably stored. Over the limit → `storage_limit`, naming the workspace and saying the owner's plan is full.
- Returns the created document in the same resource shape as `read_document`, with `id`, `workspaceId`, and `url`.
- The tool description says plainly that **retrying after a timeout can create a duplicate**, and to check `list_documents` first. No idempotency key: a duplicate draft is cheap to notice and delete, and a required key would cost every call.

**Not in the catalog:** delete, share, and member management. Those are separate destructive or permission boundaries, and each would get its own tool if agents need it later.

### Errors

These are typed outcomes, shown in plain, product-owned wording that doesn't depend on the protocol. Raw provider or framework errors are never shown.

| Code | When | Copy points to |
| --- | --- | --- |
| `unauthorized` | Bad token, unknown user, or closed account | Reconnect Alderdocs |
| `insufficient_scope` | Token lacks `documents:write` | Reconnect with edit access |
| `not_found` | No such document or workspace, or no membership or share covering it | Call `list_documents` / `list_workspaces` |
| `insufficient_role` | Membership or share exists but the role can't do this | States the role, e.g. "You're a Viewer in Acme Studio" |
| `conflict` | Document changed since this grant's last complete read | Call `read_document` again |
| `storage_limit` | Owner's storage allowance exhausted | The workspace owner needs more storage |
| `invalid_input` | Schema or size violation | Names the field and the measured limit |

## Library page

### What the beta taught us

The header's active-workspace switcher was ambient state. People created documents in whichever workspace happened to be active, and nothing showed changes across clients. So:

- **No active-workspace switcher, and no active workspace.** The library spans every workspace by default.
- **Creating a document always names its workspace explicitly**, in the create form itself.

### Routes

```text
/library                                  all documents the user can reach (cross-workspace)
/w/[workspaceId]/documents/[documentId]   one document
/w/[workspaceId]                          resolves (history replace) to /library?workspace=[workspaceId]
/w/[workspaceId]/settings                 workspace settings (Owner)
/w/[workspaceId]/members                  members (Owner manages; 25-member cap shown)
```

- IDs are 12-character Base58 entity IDs from the shared helper. No slugs.
- `/library` is outside the workspace prefix because it spans workspaces. The workspace is query state there, never session state.
- **Assumption:** documents never move between workspaces (the brief says each document belongs to exactly one). That's what makes nesting the document URL under its workspace safe. If moving documents becomes a feature, documents move to a top-level `/documents/[id]` so links survive the move.
- On entering a `/w/[workspaceId]/...` route, the app activates that provider organization if the user is a member, so a cold deep link works without a chooser. For a document opened through a share, it leaves the session's organization alone, and the page shows nothing of the workspace beyond the document. A workspace the user can reach neither by membership nor by a share of the addressed document shows a product-owned "You don't have access" screen.
- Web data queries authorize by user identity and membership or share, never by the session's active organization claim.

### Library query state

These are parsed and serialized by one shared module, in this fixed order, mirroring the controls left to right:

| Param | Values | Default (omitted) |
| --- | --- | --- |
| `q` | free text | none |
| `workspace` | a workspace ID the user belongs to, or `shared` (shared with me) | all workspaces and shares |
| `sort` | `updated`, `title`, `created` | `updated` |
| `create` | `true` opens the create dialog | closed |

- An unknown `workspace` value, or one the user isn't a member of, is ignored with a quiet notice, and the view falls back to all. Malformed params are rejected and dropped, not interpreted.
- Search and filter changes replace history. Opening a document pushes history.
- "Load more" isn't stored in the URL.
- **Assumption:** a single-value workspace filter is enough for now. Multi-select can come later as repeated `workspace` params.

### What the library shows

- One list across every workspace, newest change first, so a studio lead sees what changed across all clients at a glance. Each row shows the title, the **workspace name** (or "Shared by <name>" for shares), the last editor, and when it was updated.
- The workspace filter is a control in the page, not in the header. It lists the user's workspaces plus "Shared with me".
- Actions a row's role or share doesn't allow (edit, share) are hidden. The server still enforces them.

### Creating a document in the UI

- "New document" opens the dialog at `/library?create=true` (URL-addressable, so onboarding and help links can deep-link into it).
- The dialog has a **visible, required workspace picker** listing only workspaces where the user is Owner or Editor.
  - When the library is filtered to exactly one such workspace, or the user has only one, the picker is pre-selected and still visible.
  - Otherwise nothing is pre-selected and the user must choose. It never pre-selects from a remembered or last-used workspace.
- The request sends `workspaceId` explicitly to the same `document.create` product function that MCP uses, which runs the same checks (role, storage).
- After creating, the user goes to `/w/[workspaceId]/documents/[documentId]`.

## Open assumptions

Each of these is a decision I made in the owner's absence. Confirm or overturn them.

1. **Grant scope is account-wide** (all current and future memberships plus shares). A workspace-bound option is deferred until a customer policy needs it.
2. **Owner, Editor, and Viewer are product roles** in the app's gate. The provider holds only `admin` (Owner) and `member`.
3. **Shares carry a role** (Viewer or Editor, default Viewer). Only Owners and Editors can share.
4. **Share recipients don't count** toward the 25-member cap, and they never see the workspace's name, members, or other documents.
5. **Pending shares to emails without an account** are claimed only through a verified email at sign-in.
6. **Two OAuth scopes**, `documents:read` and `documents:write`, with both requested by default.
7. **`create_document` takes a separate `title`**, uses the same content format as `update_document`, and has no idempotency key (duplicates are possible on retry, and the description says so).
8. **Storage for a new or updated document counts against the workspace owner's plan.**
9. **Documents never move between workspaces.** If that changes, the document route moves to the top level.
10. **`update_document` gets server-side conflict detection** based on the version last served to the grant. This is a behavior change for any caller that writes without reading first; I'm treating MCP as pre-release so no compatibility shim is kept.
11. **`list_workspaces` is added** and `list_documents` gains an optional `workspaceId` filter. Both are additive changes.
12. **The membership mirror is updated by provider webhooks.** Revocation takes effect once the webhook lands (seconds), not instantly from the provider.

````

> Result: File created successfully at: <run>\builds\4-account-wide-agent-grant-new-opus2\work\docs\workspace-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/workspace-access.md`. I haven't committed it.

**Authorization**
- Every surface (web app and MCP) calls the same product functions, and all access checks happen inside them.
- A caller reaches a document in one of two ways: a live membership in its workspace (Owner, Editor or Viewer), or an individual share of that document. A share covers only that one document.
- Every call rechecks access, so removing someone from a workspace or a share affects existing agent connections on their next call. An organization claim in the token is never used to decide access.

**Agent connection (MCP)**
- One connection covers every workspace the user belongs to now or joins later, plus documents shared with them. That's what fixes the "reconnect per client" complaint, and the consent screen says so.
- There are two scopes: `documents:read` and `documents:write`.
- A per-workspace connection is left out for now. If a customer's policy requires it later, it can be added without a separate MCP address per workspace.

**Tools**
- **New `create_document { workspaceId, title, content }`:** the workspace ID is required, with no default and no lookup by name. That's the agent-side fix for documents landing in the wrong workspace.
  - Only Owners and Editors can create, and a share never allows it.
  - It checks the workspace owner's storage allowance first and only counts the storage once the document is saved.
  - Its description warns that retrying after a timeout can create a duplicate.
- **New `list_workspaces`:** the agent needs it to find workspace IDs, including for a new workspace with no documents yet.
- **`list_documents`:** covers all workspaces by default, newest changes first, and gains an optional `workspaceId` filter.
- **`update_document`:** now refuses to overwrite a document that changed since the agent last read it.
- A missing document and one the caller can't reach return the same "not found" error, so IDs can't be used to probe what exists.

**Library page**
- The header's active-workspace switcher is gone. `/library` lists documents from every workspace, sorted by most recent change, and each row shows its workspace or "Shared by …". That covers the "lose track of what changed across clients" feedback.
- The workspace filter, search, sort and the create dialog are all in the URL, so links and reloads restore the same view.
- Creating a document shows a required workspace picker. It's pre-filled only when the choice is obvious (the library is filtered to one workspace, or the user has only one), never from the last workspace used.
- A document lives at `/w/[workspaceId]/documents/[documentId]`.

**What I assumed** (the doc lists 12; these matter most)
1. Owner, Editor and Viewer are roles Alderdocs stores itself. The auth provider only knows "admin" (the Owner) and "member".
2. A share has its own role, Viewer or Editor, defaulting to Viewer. People with a share don't count toward the 25-member cap.
3. A new or edited document's storage counts against the workspace owner's plan.
4. Documents never move between workspaces. If they can, the document address should move out from under the workspace path so links don't break.
5. Making `update_document` refuse overwrites changes how it behaves for agents that write without reading first. I treated MCP as not yet released, so there's no compatibility mode.

**Session ended:** success, 8 turns, 135815 ms
