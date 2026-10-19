**Prompt:** Design the authorization model behind our MCP tools, including the create tool we still need, and the workspace handling on the library page. Write it to docs/workspace-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5601 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md agent-tool-design.md"}`

> Result: # Workspace Tenancy  Give a product workspaces when shared ownership, membership, or policy needs them now or is on the product's roadmap, because retrofitting an ownership boundary costs far more than carrying one early. A product whose data will only ever belong to one person keeps it on the user account, with no organization layer. When a product's collaboration model is workspaces, back ever [... 19441 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat auth.md bootstrap.md routing.md query-state.md ids.md"}`

> Result: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 26788 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat app-surface.md product-ux.md data-model.md http-apis.md abuse-resistance.md billing.md quota.md"}`

> Result: # App Surface  The signed-in app owns the core workflow and private state. It should not carry public SEO routes without a deliberate reason.  Responsibilities:  - Authentication and session - Private data and product workflows - Account and billing - Admin - Provider-backed actions - Private routing  The app surface feels like its core object first. Secondary features attach to that  [... 16418 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat user-facing-errors.md search-indexing.md source-of-truth.md modularity.md"}`

> Result: # User-Facing Errors  Treat every provider, framework, transport, database, and backend error as internal data. Convert failures into product-owned outcomes before they reach visible UI.  ## Boundary  - Return typed outcome codes for expected failures. - Map outcome codes to concise, actionable copy at a shared presentation boundary. - Use one context-specific fallback for unexpected failu [... 9525 more characters]

**Tool call `Write`:** `<run>/builds/4-account-wide-agent-grant-new-opus/work/docs/workspace-access.md`

````text
# Workspace Access

How Alderdocs decides who can reach which documents, from the app and from an agent over MCP. It covers the authorization model, the MCP tool catalog with the new `create_document` tool, and how the library page handles workspaces.

`docs/brief.md` is the source of truth for owner decisions. If this document contradicts it, the brief wins and this document gets fixed. The calls made here without owner input are listed under [Assumptions to confirm](#assumptions-to-confirm).

## Principles

1. **The URL or the call names the target, and the server verifies it.** No surface keeps an "active workspace" as an authority. The header switcher from the beta is gone (see [Library page](#library-page)).
2. **One gate.** The app, the MCP server, and any future API or job call the same product capabilities, and those capabilities go through one authorization gate. Hiding a control in the UI and leaving a tool out of a catalog are conveniences. Neither is what keeps a caller out.
3. **Access is recomputed on every call.** Removing a member, changing a role, or revoking a share takes effect on the next request, including requests from agent tokens issued earlier.
4. **Fail closed.** No verified identity, or nothing that covers the target, means a refusal with a single product error.

## Identity and workspaces

- The managed auth provider (Clerk by default) owns identity and membership. Each workspace is one provider organization, including the one created at sign-up, as the brief requires.
- Personal-account mode (no organization) is turned off. Every session has at least one membership.
- **Home workspace.** At sign-up the first workspace is created as a real organization named "‹First name›'s workspace", or "My workspace" if no name is available. After that it has no special status: you can rename it, invite people, and it follows the same rules as every other workspace. No flag marks it as the first.
- **Roles.** The product roles are Owner, Editor, and Viewer. In the provider, Owner maps to the built-in administrator role. Editor and Viewer both map to the built-in member role. The Editor/Viewer distinction is stored in the app database on the membership row, and the gate reads it from there. This keeps capabilities in the product's own gate and leaves the provider's role model at its defaults.
- **Membership mirror.** The app database mirrors memberships from provider webhooks. Mirrors are idempotent, deduplicated by event ID, and also reconciled during bootstrap on every authenticated entry (user → home workspace → addressed workspace → data). The gate reads this mirror. The residual exposure is that a removal only takes effect once its webhook lands. That window is normally seconds. See [Residual exposure](#residual-exposure).
- **Member cap.** Every workspace has a cap of 25 members, the same on every plan. The cap is mirrored onto the provider's per-organization membership limit, so invitations past it are refused when they're sent, and pending invitations count toward it. The provider's instance default cap is set to 1, so a workspace whose cap hasn't been synced fails closed. The cap never grows with the plan, so the "workspace is full" message offers only remedies that actually work: remove a member or cancel a pending invitation. It never offers an upgrade.
- **Storage** is billed per paying owner. A workspace's documents count against the plan of its Owner. Above the allowance, existing documents stay readable and editable as long as an edit doesn't grow storage. New documents and edits that grow storage are refused until usage is back under the allowance. The gate derives this from the owner's current plan on every call. It is never stored as a flag on the workspace.

## Access sources

A caller reaches a document in one of two ways:

| Source | Grants |
| --- | --- |
| **Membership** in the document's workspace, with a role | Every document in that workspace, according to the role |
| **Share**: the document is shared with the caller's verified email, with a share role | That one document only. It does not grant the workspace's other documents, its member list, its name, or its settings |

A share is bound to an email address. When the recipient signs in with that address verified, the share resolves to their user. If someone is both a member and a share recipient, their effective access is the union of the two.

## Capabilities

Every action maps to a named capability. Access is the intersection of three things: what the caller's membership role or share role allows, the capability itself, and, for an agent token, the token's scopes.

| Capability | Owner | Editor | Viewer | Share: can edit | Share: can view | Token scope |
| --- | --- | --- | --- | --- | --- | --- |
| `workspace.list` (see own memberships) | yes | yes | yes | — (shares don't reveal workspaces) | — | `documents:read` |
| `document.list` | yes | yes | yes | that document | that document | `documents:read` |
| `document.read` | yes | yes | yes | yes | yes | `documents:read` |
| `document.update` | yes | yes | no | yes | no | `documents:write` |
| `document.create` (in a workspace) | yes | yes | no | no | no | `documents:write` |
| `document.share` | yes | yes | no | no | no | not exposed over MCP |
| `workspace.manage` (rename, members, invitations) | yes | no | no | no | no | not exposed over MCP |

The gate fails closed when a capability is unknown or missing. It lives in one module that every product capability (`listDocuments`, `readDocument`, `updateDocument`, `createDocument`, …) has to go through. The UI's backend functions and the MCP adapter call those capabilities and never re-check rules themselves. Plan limits such as storage are a separate check at the same boundary, not part of the role gate.

## Agent grant: account-wide

**Decision: an MCP connection is account-wide.** Studio leads asked for one connection that works across their client workspaces, and having to reconnect per client was the top complaint about a competitor. One OAuth authorization therefore covers:

- every workspace the person is a member of now or joins later, with whatever role they currently hold there, and
- every document shared with them individually.

The consent screen says this plainly. Suggested wording: *"‹Client› will be able to read and edit documents in all of your Alderdocs workspaces, including ones you join later, and documents shared with you. It can do only what your role allows in each workspace."*

The grant does not raise privileges. In each workspace the agent can do exactly what the person's role allows there, intersected with the token's scopes. If the person's role changes, the agent's access changes on the next call.

A workspace-bound mode (where consent picks one workspace) is not built now. If an enterprise customer later needs a policy that "this connection must never reach another client", it would be added as a separate authorization of the same MCP resource with a consent-time workspace choice, never as a second endpoint or a per-workspace path.

### Tokens

- The endpoint is `https://mcp.<domain>/mcp`. It is a separate Hono app (`apps/mcp`) that uses the official MCP SDK's web-standard transport, sends buffered JSON responses, and is stateless.
- The auth provider is the authorization server. The MCP server verifies every token through the provider's backend SDK: introspection for opaque tokens, signature and claims for JWTs. It never decodes and trusts an unverified token body.
- **Audience.** The provider is configured to put the MCP resource in each token's audience. The server rejects any token whose audience doesn't include it. Before writing this check, decode a real token from our provider instance to confirm the claim is actually present.
- **Scopes.** The two scopes are `documents:read` and `documents:write`. Both are advertised in protected-resource metadata and in the `WWW-Authenticate` challenge, and both are enforced: a write tool called without `documents:write` gets the protocol's insufficient-scope response, not a generic denial. An empty scope list counts as "no scopes", not as "scopes field missing".
- **The token's organization claim is ignored for authorization.** Under an account-wide grant, any active organization in the token proves nothing about the workspace being targeted. The target is resolved on every call from the tool arguments and checked against the membership mirror or a share.
- Protected-resource metadata is served with `Cache-Control: no-store` and points at the provider's own authorization server metadata URL. The server does not proxy that document.
- Enterprise-Managed Authorization (ID-JAG) is added only if the provider supports it natively, alongside ordinary OAuth. Recheck provider support whenever MCP authorization is touched. We build no custom exchange.

## MCP tool catalog

Every caller sees the same static catalog of five tools. A tool the caller can't use in a given workspace is still listed, and a call that the gate refuses returns an instructive error. The new tools are `create_document`, plus `list_workspaces`, which gives an agent the workspace IDs it needs for creating documents.

All results use one shared document shape:

```ts
type DocumentSummary = {
  id: string;                              // 12-char Base58 entity id
  title: string;
  workspace: { id: string; name: string } | null; // null when reached only through a share
  access: { via: "membership" | "share"; role: "owner" | "editor" | "viewer" };
  updatedAt: string;                       // ISO 8601
  url: string;                             // app URL, built by the origin helper
};
```

| Tool | Input | Returns | Capability | Annotations |
| --- | --- | --- | --- | --- |
| `list_workspaces` | `{}` | `{ workspaces: [{ id, name, role, canCreateDocuments }] }` | `workspace.list` | read-only |
| `list_documents` | `{ query?, workspace?, cursor? }` | `{ documents: DocumentSummary[], nextCursor? }` | `document.list` | read-only |
| `read_document` | `{ id }` | `DocumentSummary & { content }` | `document.read` | read-only |
| `update_document` | `{ id, content }` | `DocumentSummary` | `document.update` | destructive (replaces content), idempotent |
| `create_document` | `{ workspace, title, content? }` | `DocumentSummary` | `document.create` | not read-only, not destructive, not idempotent |

### `list_workspaces`

- Opening sentence: "List the workspaces you belong to, with your role and whether you can create documents in each."
- It returns memberships only. It never lists workspaces that the caller reaches only through a share.

### `list_documents`

- Opening sentence: "List and search documents across all your workspaces and documents shared with you."
- With no `workspace` argument it spans every membership and share. The new optional `workspace` argument is a browsing filter. If it names a workspace the caller isn't a member of, the call returns `workspace_not_found`. That argument narrows the results and never grants anything.
- `query` matches document titles. See the assumptions section.
- Results are sorted by `updatedAt`, newest first. `cursor` is opaque and pages are bounded (default 25, max 100).

### `read_document`

- Opening sentence: "Read a document's full content by id."
- The server records the document revision it returned to this grant. That record is the baseline that `update_document` compares against.

### `update_document`

- Opening sentence: "Replace a document's content by id."
- No revision token is required. The server guards against lost edits itself. If the document changed after this grant last read it in full, or if this grant has never read it, the call is refused with `conflict` and asks the agent to call `read_document` and reapply its change. A document this grant created through `create_document` counts as read at the revision that was created.
- The description says a retry is safe: the same content twice gives the same result.
- If the edit grows storage while the owner is over their allowance, it is refused with `storage_limit_reached`. Edits that shrink or keep size still pass.

### `create_document` (new)

- Opening sentence: "Create a new document in a workspace you can edit."
- **`workspace` is required.** There is no default, no "home workspace" fallback, and the server never infers it from a previous call or from the token's organization. This is the beta lesson from documents landing in the wrong workspace, and it follows the rule that leaving an argument out must never quietly decide where something gets created. It is a separate tool from `update_document`, so there's no argument that switches between editing and creating.
- The workspace must be named by its stable ID (from `list_workspaces` or from `workspace.id` on any document). The server does not resolve workspace names, because names collide across client workspaces ("Website", "Brand").
- The server checks membership with an Owner or Editor role, the `documents:write` scope, and the owner's storage allowance before it writes anything. Usage is recorded from the stored size after the write succeeds.
- The call returns the created `DocumentSummary`, including `workspace`, so the agent can confirm where the document landed.
- The description states: "Retrying after a timeout can create a duplicate. Call `list_documents` first to check." No idempotency key is required. A duplicate document is visible and easy to remove, so a required key would cost every call more than it protects.
- A share recipient can never create documents in the shared document's workspace.

### Errors

Errors are typed outcome codes, and each carries one plain sentence with the next step. They never include raw provider or framework text.

| Code | When | Message names |
| --- | --- | --- |
| `document_not_found` | The document doesn't exist, or the caller has neither a membership nor a share that covers it. These are deliberately the same, so no one can probe whether a document exists. | "Call `list_documents` to find documents you can open." |
| `workspace_not_found` | The workspace argument doesn't name a membership | "Call `list_workspaces` for valid IDs." |
| `role_insufficient` | The caller is a member or share recipient, but their role doesn't allow the action | The role they hold and the role required, e.g. "You're a Viewer in Acme; creating needs Editor or Owner." |
| `conflict` | `update_document` came after another change, or without a full read | "Read the document again, then reapply your change." |
| `storage_limit_reached` | Create, or an edit that grows storage, while the workspace owner is over their allowance | That the workspace owner's storage is full. Editing without growing storage still works. |
| insufficient scope (protocol) | The token is missing `documents:write` | The scope required, with the challenge that triggers re-consent |
| unauthenticated (protocol) | The token is missing, invalid, or has the wrong audience | The challenge only |

## Library page

The library is the one place in the app that lists documents. It spans all of a person's workspaces and their shares, so it doesn't need an active workspace.

### Routes

```text
/library                                   all documents the person can reach
/library?q=…&workspace=…&sort=…            filtered view (canonical parameter order)
/w/[workspaceId]                           resolves (history replace) to /library?workspace=[workspaceId]
/w/[workspaceId]/documents/[id]            a document
/w/[workspaceId]/settings                  workspace settings (Owner)
/w/[workspaceId]/members                   members and invitations (Owner)
```

- Every route that addresses a single workspace nests under `/w/[workspaceId]`. That segment is compressed because nobody reads it. The library spans workspaces, so it sits outside that prefix and carries its workspace filter in the query string.
- There is no separate per-workspace document list, because that would be a second route for the same concept. A bare workspace URL resolves to the library filtered to that workspace.
- **Query state:** `q` (title search), `workspace` (a workspace ID, or `shared` for "Shared with me"), and `sort` (`updated` by default, or `title`), serialized in that order. Untouched defaults are left out. A `workspace` value the person can't reach shows a clear "You don't have access to this workspace" state and never quietly falls back to everything. "Load more" is not stored in the URL.
- **Deep links.** Opening `/w/[id]/...` from a cold session switches the provider's active organization to match the URL when the person is a member. A share recipient opening a shared document's URL keeps their session organization as it was and doesn't join the workspace. The page shows the document and nothing else about the workspace: no name, no members, no sibling documents. A URL the person can't reach through a membership or a share shows a product-owned "no access" screen.

### Layout

- There is no workspace switcher in the header. Workspace is a filter on the library and a visible label on every row.
- Each row shows the title, a workspace label (or "Shared with you" for share-only documents), the last editor, and the last-edited time. The default sort is most recently edited across every workspace, which directly answers the studio leads' "what changed across my clients" complaint.
- The workspace filter lists the person's workspaces and "Shared with me". The filter only changes what is shown.

### Creating from the library

- "New document" opens a creation dialog that has its own URL (`/library?create=document`, plus the current filters) so it can be linked and restored.
- The dialog has a required, always-visible **Workspace** field. It is prefilled only when the choice is unambiguous: the person can create in exactly one workspace, or the library is currently filtered to one workspace they can create in. Otherwise it starts empty and must be chosen. After creating, the person lands on `/w/[workspaceId]/documents/[id]`, where the workspace name appears in the header.
- The field lists only workspaces where the person is Owner or Editor. If there are none (for example, a Viewer everywhere, or someone who only has shares), the button is hidden rather than disabled.
- The UI calls the same `createDocument` capability as the MCP tool, so the same workspace, role, and storage rules apply.

## Residual exposure

- **Webhook lag on removal.** The gate reads the membership mirror, so a member removed in the provider keeps access until the removal webhook lands, which is normally seconds. If this becomes unacceptable, have mutating capabilities confirm the membership live with the provider before writing.
- **Provider token features.** The audience binding and scope enforcement depend on what our provider instance actually mints. Verify against a real token before shipping, and record any gap here.

## Assumptions to confirm

1. **Account-wide grant, no workspace-bound option yet.** This is based on the studio-lead feedback. Add the workspace-bound mode when a customer requires tenant isolation per connection.
2. **One Owner per workspace.** "Storage per paying owner" reads as one billing owner per workspace. Ownership transfer and co-owners are out of scope.
3. **Editor and Viewer are app-side roles.** The provider only knows administrator (Owner) and member. The Editor/Viewer split lives in our database.
4. **Shares have a role:** "can view" (the default) or "can edit". The brief says only that a document is shared with one person, without specifying what they can do. Share recipients can never create, share, or see anything else about the workspace.
5. **A share is bound to an email address** and resolves when someone signs in with that email verified. If they're also a member, their access is the union of membership and share.
6. **Documents don't move between workspaces.** That's why document URLs nest under `/w/[workspaceId]`. If moving is ever added, documents should move to a top-level `/documents/[id]` route so shared links survive the move.
7. **`list_documents` searches titles only.** Full-content search brings indexing, privacy, and deletion obligations and should be decided on purpose.
8. **`list_workspaces` is a new tool.** Without it an agent couldn't find a workspace ID for `create_document` in a workspace that has no documents yet.
9. **`create_document` takes `{ workspace, title, content? }`** with a required title so agent-created documents are identifiable in the library. It has no idempotency key, and the retry-duplicate risk is stated in the tool description.
10. **Sharing and workspace management are not exposed over MCP** for now. These are the higher-risk actions, and no one asked for them.
11. **Creation dialog prefill.** The Workspace field is prefilled only in the two unambiguous cases above. If wrong-workspace creation reappears, drop the filter-based prefill.
12. **Membership mirror with webhook lag** is accepted for now, as described under Residual exposure.

````

> Result: File created successfully at: <run>/builds/4-account-wide-agent-grant-new-opus/work/docs/workspace-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/workspace-access.md`. I haven't committed it and haven't changed `docs/brief.md`.

**Agent connection: one connection covers every workspace.** Studio leads asked for this, and having to reconnect per client was the top complaint about a competitor. One authorization covers every workspace the person belongs to now or joins later, plus documents shared with them, and the consent screen says so. It never gives the agent more than the person has: the server works out the target workspace or document on every call. Access is whatever the person's role or share allows there, limited further by the connection's read and write permissions. So removing someone or revoking a share takes effect right away, even on connections made earlier.

**MCP tools:**
- **New `create_document { workspace, title, content? }`:** `workspace` is required. There's no default and nothing is inferred from earlier calls, which is aimed at the beta's documents-in-the-wrong-workspace problem. The workspace must be given by ID, not by name, since names like "Website" repeat across clients. The result says which workspace the document landed in.
- **New `list_workspaces`:** I added it so an agent can find a workspace ID even when that workspace has no documents yet.
- **`list_documents`:** gets an optional workspace filter. Each result says whether the person reached it as a member or through a share. Shared-only documents show no workspace information.
- **`update_document`:** refuses with a "read it again" error if the document changed since this connection last read it, so the agent can't overwrite someone else's edits.
- **Errors:** each one names the next step. A document someone can't access gives the same "not found" as one that doesn't exist, so nobody can probe for documents.

**Library page:**
- The header workspace switcher is gone.
- `/library` lists documents from all workspaces plus shares, newest edits first. That answers the "what changed across clients" complaint.
- Each row shows its workspace, or "Shared with you".
- The workspace filter is part of the URL (`?workspace=…` or `shared`). Opening a workspace's own address lands on the library filtered to that workspace.
- "New document" asks for a required, always-visible workspace. It's pre-filled only when the choice is obvious. People who can't create anywhere, like Viewers, don't see the button.

**Assumptions to check**, all listed at the end of the doc:
- Each workspace has exactly one Owner.
- Editor and Viewer are kept in our own database; the auth provider only knows administrator and member.
- Shares can be "can view" (the default) or "can edit".
- Documents never move between workspaces. If that changes, their addresses should change too, so shared links keep working.
- Search matches titles only.
- Sharing and member management stay out of MCP for now.
- After someone is removed, they keep access for the few seconds it takes the provider's notification to reach us.

Before building, decode a real token from our auth provider to confirm it carries what the access checks rely on.

**Session ended:** success, 9 turns, 175026 ms
