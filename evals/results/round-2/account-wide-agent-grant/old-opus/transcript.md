**Prompt:** Design the authorization model behind our MCP tools, including the create tool we still need, and the workspace handling on the library page. Write it to docs/workspace-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-old-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5601 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md agent-tool-design.md"}`

> Result: # Workspace Tenancy  When a product's collaboration model is workspaces, back every workspace with the auth provider's organization object, the user's first workspace included. One organization per workspace gives every workspace the same membership, invitation, role, and token contract from day one, and the provider's verified organization context becomes the one workspace authority every surfa [... 14276 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat auth.md app-surface.md routing.md query-state.md ids.md bootstrap.md"}`

> Result: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 26603 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat quota.md billing.md abuse-resistance.md data-model.md source-of-truth.md product-ux.md bulk-actions.md"}`

> Result: # Quota  Check quota before doing expensive work. Charge usage only after durable success.  - Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known. - For imported files, read metadata first and block early if it cannot fit. - For live capture where the final size is unknown, let work begin if time remains, warn near the limit, and st [... 16215 more characters]

**Tool call `Write`:** `<run>\builds\2-account-wide-agent-grant-old-opus\work\docs\workspace-access.md`

````text
# Workspace access

How Alderdocs decides who can do what to a document, from the app, the MCP server, and anything added later, and how the library page handles workspaces.

`docs/brief.md` takes precedence. If the two disagree, fix this document.

Status: draft, written while the owner was away. Every call that isn't already in the brief is listed under [Assumptions](#assumptions), and the ones that need an owner decision are listed under [Open questions](#open-questions).

## Summary

1. **One gate.** Every read and write goes through one backend authorization function. The app, the MCP server, and future surfaces call it. None of them has its own rules.
2. **No active workspace.** Workspace is a property of each document, not a mode the person is in. The library shows every document the person can reach, with its workspace visible. You pick a workspace when you create a document, every time it matters, and never by default.
3. **One agent connection covers every workspace.** A connected agent acts as the person across every workspace they belong to, plus documents shared with them. Each call is scoped by the document's own workspace, or, for create, by a required `workspaceId`. Nobody reconnects per client.

## Principals and resources

| Term | Meaning |
| --- | --- |
| Person | An app user, keyed by the auth provider's stable subject id. |
| Workspace | One auth-provider organization. Every workspace is the same kind of thing, including the one created at sign-up. |
| Membership | A person's role (Owner, Editor, or Viewer) in one workspace. The auth provider owns it. The database keeps a mirror updated by webhooks. |
| Document | Belongs to exactly one workspace (`workspaceId`). |
| Share | Gives one email address access to one document. Its fields are `documentId`, normalized `email`, `level` (`view` or `edit`), `sharedBy`, and `userId`. `userId` is filled in once someone with that verified email signs in. |
| Agent grant | An OAuth access token issued to an MCP client for one person. It carries scopes. It does not carry a workspace. |

## Capabilities

Every action maps to a named capability. A capability that isn't in the table, or isn't granted, is refused (fail closed).

| Capability | Granted by |
| --- | --- |
| `document.read` | Any membership in the document's workspace, or a claimed share at any level. |
| `document.update` | Owner or Editor in the document's workspace, or a claimed share at level `edit`. |
| `document.create` (in workspace W) | Owner or Editor of W. A share never grants create. |
| `document.share` | Owner or Editor in the document's workspace. A sharee can't re-share. |
| `document.delete` | Owner or Editor in the document's workspace. App only for now (see [MCP tools](#mcp-tools)). |
| `workspace.members.manage`, `workspace.settings`, `workspace.billing` | Owner. |

### Effective access

```text
allowed(person, capability, resource, token?) =
  capability is known
  AND person is live (exists, has no closure record)
  AND (role(person, resource.workspace) grants capability
       OR share(person, resource) grants capability)
  AND (token is absent OR token.scopes cover capability)
```

- **Role and share are combined with OR.** A share can only add access to one document. It never removes access from a member.
- **Token scope is combined with AND.** It can only narrow what the person could already do.
- **Scopes are minimal and enforced.** `documents:read` covers `document.read` and listing. `documents:write` covers `document.create` and `document.update`. Only these two are advertised, and both are required wherever they are advertised. A read-only agent connection is a real option.

### The one gate

- `authorize(principal, capability, resource)` lives in a shared domain package. Every backend function that touches documents calls it inside the same transaction as the read or write. A check at the edge, or in the UI, is never the guarantee.
- The UI hides actions the person can't take. For example, a Viewer sees no edit affordance, and the create picker lists only workspaces where the person can create. Hiding is presentation only. The gate still re-checks every call.
- A document the person can't read returns the same `not found` as a document that doesn't exist. That way a probe can't learn which ids exist.
- Plan limits (storage) are a separate gate from authorization. Both run, and neither stands in for the other.

### Where membership comes from

- The auth provider owns membership and roles. The database mirror is updated from signature-verified, idempotent webhooks, and bootstrap reconciles it again on each app entry. The gate reads the mirror by the verified subject id.
- Removing a member deletes their mirror row. Their next call is refused, whether it comes from the app or from an agent token issued before the removal. The only lag is webhook delivery.
- A readable but unverified token body never selects or grants anything.

## MCP authorization

### One resource, one grant per person

- Endpoint: `https://mcp.<domain>/mcp`, as its own app (Hono plus the official MCP SDK). It serves one OAuth protected resource.
- The person consents once. The consent copy (product-owned, using the word "workspace") says that the agent can read and, with write scope, edit documents in **every workspace you belong to and documents shared with you**, limited by your role in each.
- The token names a person, never a workspace. **This deliberately departs from our usual default**, where consent picks one organization and switching workspaces means authorizing again. The brief records that per-client reconnection was the most common complaint about a competitor, and studio leads want one agent working across clients. If the provider's consent flow insists on choosing an organization, we ignore that claim for scoping, and scoping comes from the resource on every call. Before relying on this, check it against a real token from our provider.
- Per call: verify the token with the provider's backend SDK. Always enforce the issuer. Enforce the audience only if the minted token actually names one, and leave a code comment explaining why it's conditional. Check scopes and treat an empty list as no scopes. Resolve the person by subject id and check that they are live. Then pass the verified subject to backend functions, which run the gate. The MCP app carries no authorization rules of its own.
- Missing or insufficient scope gets the protocol's `insufficient_scope` challenge, so the host can re-authorize. Any other refusal is a normal tool error with instructive copy.
- Protected-resource metadata is served with `no-store` and points to the authorization server's own metadata URL. Enterprise-managed authorization is added only if the provider supports it natively.

### Blast radius, and what limits it

An account-wide grant reaches more than a per-workspace one. It is limited by:

- the person's own role in each workspace (a Viewer's agent can't edit),
- the token's scopes (an agent can be read-only),
- immediate effect of membership removal,
- revocation of the connection from the person's account settings, which lists connected agents,
- and an attribution trail: every write records the person plus "via agent" and the client name, so workspace owners can see what an agent changed.

## MCP tools

There is one static catalog for every caller, authorized per call. Tool descriptions open with verb then noun.

| Tool | Input | Capability | Annotations |
| --- | --- | --- | --- |
| `list_workspaces` | `{}` | membership (any) | read-only |
| `list_documents` | `{ query?, workspaceId?, cursor? }` | `document.read` per row | read-only |
| `read_document` | `{ id }` | `document.read` | read-only |
| `create_document` | `{ workspaceId, title, content? }` | `document.create` in `workspaceId` | not read-only, not destructive, not idempotent |
| `update_document` | `{ id, content }` | `document.update` | not read-only, **destructive** (replaces content), idempotent |

- **`list_workspaces`** is new. Create needs a `workspaceId`, and the agent needs a way to find one. It returns `id`, `name`, `role`, and `canCreate` for each membership.
- **`list_documents`** lists everything the person can read, including documents shared with them, sorted by most recently changed. `workspaceId` can only narrow the list. Each row returns `id`, `title`, `workspace { id, name }` (or `sharedWithYou: true` with who shared it), `updatedAt`, `updatedBy`, and `canEdit`. That lets an agent answer "what changed across my clients this week" in one call.
- **`read_document`** returns the document plus its workspace, the caller's effective capabilities, and `revision`.
- **`create_document`** requires `workspaceId`, with no default and no fallback to a "home" workspace. An omitted argument must never silently decide where a resource is created, and this is the same wrong-workspace failure the beta had. It returns `id`, `workspace { id, name }`, and the app URL for the new document. Possible refusals:
  - A workspace the person isn't a member of: "You're not a member of a workspace with that id. Call `list_workspaces` to see where you can create documents."
  - A Viewer role: "Your role in *Northwind* is Viewer, which can read documents but not create them."
  - Out of storage (see [Storage](#storage-on-create-and-update)).
- **`update_document`** is unchanged in shape. Its annotation is destructive because it replaces content. Refusals name the role, for example "Your access to this document is view-only."
- **Not exposed: delete and share.** The catalog stays as small as the brief needs. Sharing sends email to a third party, so it stays a deliberate in-app action for now.
- **Reads stay singular.** No batch tools for now. If batch writes come later, they loop the single-item operation and return one result per item.

## Storage on create and update

- Plans are priced by storage per paying owner, so the document's workspace owner is charged. Size is known before the write, so the gate checks the owner's remaining storage first and records usage only after the write lands.
- On refusal, the copy names the limit and a remedy that actually works. Owners get "free up space or move to a larger plan". Everyone else gets "ask *workspace owner* to free up space or upgrade".
- There is also a hidden internal ceiling on documents created per person per hour, plus edge rate limits on the MCP host. Both are anti-abuse measures, are never shown, and their numbers are still to be set.

## Workspaces and membership

- Every workspace is a provider organization, including the one created at sign-up, and none is special after creation. The provider's no-organization mode is turned off.
- **Member cap: 25 per workspace, the same on every plan** (from the brief). It is set as the provider's per-organization membership limit, which counts pending invitations, so the 26th invitation is refused when it is sent. The limit isn't plan-derived, so there is no seat mirror to sync. Sharees aren't members and don't count toward it.
- Creating a workspace is free, with a generous fixed anti-abuse limit.
- Provider components (organization profile, members, invitations) use the full provider string resource rewritten to say "workspace". A test proves no provider term survives.

## Sharing by email

- Owners and Editors can share a document with an email address at `view` (the default) or `edit`.
- The share is claimed on bootstrap, when a person signs in with a **verified** email that matches. Until then it grants nothing.
- A sharee sees that one document, under "Shared with you" in their library. They don't see its workspace's other documents, its member list, or (beyond its name, on the document) the workspace itself.
- Revoking a share takes effect on the next call. Deleting the document removes its shares.

## Library page

### What the beta taught us

- With an active-workspace switcher, people kept creating documents in the wrong workspace.
- Studio leads lost track of what changed across clients.

Both come from treating workspace as a hidden mode. So the library has no active workspace. Workspace becomes a visible filter, plus a field people fill in on create.

### Routes

```text
/documents                  library: everything you can read, across workspaces
/documents/[id]             one document (members and sharees use the same URL)
/w/[workspaceId]            resolves (history replace) to /documents?workspace=[workspaceId]
/w/[workspaceId]/settings   workspace name, members, invitations, billing (Owner)
```

- The library is at the top level because it spans workspaces.
- Documents are at the top level, not nested under the workspace, for two reasons. The link we email to a sharee has to open for someone who can't see the workspace. And a link must keep working if documents can later move between workspaces.
- Ids are 12-character Base58 entity ids. A workspace or document id in a URL never grants access, because the gate decides. A workspace id the person can't reach gets a product-owned "You don't have access to this workspace" screen.
- The provider's active-organization session state is never an authority. Workspace settings pages set it from the URL segment on entry, because the provider's components need it, and nothing else reads it.

### Query state

The order is fixed: `q`, then `workspace`, then `sort`.

- `q` is free-text search.
- `workspace` is a workspace id, or `shared` for "Shared with you". Workspace ids are always 12 characters, so they can't collide with `shared`. It is omitted when unfiltered.
- `sort` is `updated` (the default, omitted unless chosen explicitly), `title`, or `created`.
- "Load more" is view depth and stays out of the URL.
- Search and filter changes replace history entries rather than adding new ones.
- New-document dialog: `?new=document`, optionally with `&workspace=[id]` for prefill. Opening that URL reopens the dialog.
- Parsing and serialization live in shared domain code, with contract tests.

### What the page shows

- Rows sorted by most recently changed. Each shows the title, a **workspace label on every row** (or "Shared by *name*"), when it changed, and who changed it, including "via agent". This is the cross-client "what changed" view.
- A workspace filter in the toolbar, listing your workspaces plus "Shared with you". It filters the list only, and changes nothing else about the app.
- The list is live (reactive query), so agent edits show up without a refresh.

### Creating a document

- The "New document" dialog has a **required workspace field**. It lists only workspaces where you're Owner or Editor.
- The field is prefilled only when the choice is unambiguous: either the library is filtered to one workspace where you can create, or you can create in only one workspace. In every other case you pick.
- The chosen workspace stays visible in the dialog's primary button ("Create in *Northwind*").
- After creation, the document page shows its workspace in the header.

## Assumptions

1. **The agent grant is account-wide (all of a person's workspaces) instead of one per workspace.** This is the biggest call in this document. It's based on the studio-lead feedback in the brief.
2. **Shares have two levels, `view` (default) and `edit`.** The brief only says the person "sees that document". If shares should be view-only, drop `edit` and the `update` path for sharees.
3. **Sharees can't re-share or create, and only Owners and Editors can share.**
4. **The library has no active workspace and no header switcher.** Workspace URLs exist only for settings, and as a shortcut into the filtered library.
5. **Document URLs are top-level** (`/documents/[id]`), not nested under the workspace.
6. **Storage is charged to the owner of the document's workspace,** including for documents an agent or a sharee creates or edits.
7. **MCP leaves out delete and share,** and adds `list_workspaces`.
8. **`update_document` keeps its current shape.** I assumed it's unreleased enough that adding an optional `revision` later, to catch overwrites of concurrent human edits, is fine. Recommended as a follow-up.
9. **Membership mirror lag is acceptable.** Access changes take effect once the webhook arrives, not instantly at the provider.
10. **Bootstrap claims shares** by verified email on each authenticated entry, not only from a webhook.

## Open questions

1. **Can a workspace Owner block agent access to their workspace?** A client who owns a workspace may not want a studio lead's agent in it. The gate can support this as one more condition, a per-workspace `agents allowed` setting, without changing the tools. I didn't add it, so the default today is that agents act wherever their person can.
2. **Is "Shared by email, can edit" wanted at all** (see assumption 2)?
3. **What should the anti-abuse numbers be?** That means documents created per hour, the number of workspaces a person can create, and shares per document.
4. **Do documents ever move between workspaces?** The routes allow for it, but the brief's "exactly one workspace" doesn't say whether that can change.

````

> Result: File created successfully at: <run>\builds\2-account-wide-agent-grant-old-opus\work\docs\workspace-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote `docs/workspace-access.md`. Nothing is committed and no code changed yet.

**The main decision to confirm: one agent connection covers all of a person's workspaces.** Normally an agent would be authorized for one workspace at a time and would reconnect to switch. I went against that because the brief says reconnecting per client was the most common complaint about a competitor. Here, the agent acts as the person everywhere they're a member, plus on documents shared with them. Each call is scoped by the document's own workspace. Two things keep that in check:
- **Limits:** the person's role still applies in each workspace, and the agent can be connected read-only.
- **Tracking:** removing someone from a workspace cuts off their agent on its next call, people can revoke agents in account settings, and every agent edit is labelled "via agent".

**How authorization works:**
- **One rule set.** A single backend check sits behind the app and the MCP server alike. Access means the person's role (Owner, Editor or Viewer) or a share grants the action, and the agent's connection permits it.
- **Hidden documents.** A document someone can't see looks the same as one that doesn't exist.

**MCP tools:**
- **`create_document { workspaceId, title, content? }`:** the workspace is required and never defaults, since defaulting is exactly how the beta created documents in the wrong place. When it refuses, the message says why and what to do.
- **New `list_workspaces`:** gives the agent valid places to create documents.
- **`list_documents`:** gains an optional workspace filter and shows each document's workspace, last change and who made it. That covers "what changed across my clients".
- **Left out on purpose:** delete and share, because sharing emails a third party.

**Library page:**
- **No active-workspace switcher.** `/documents` shows everything you can see across workspaces, sorted by most recently changed, with a workspace label on every row and a workspace filter.
- **Document links:** documents live at `/documents/[id]`, so the link emailed to someone a document is shared with opens for them.
- **Creating a document:** you must pick a workspace, and it's pre-filled only when there's only one workspace that fits. The button reads "Create in *Workspace*".
- **Workspace settings:** these live at `/w/[id]/settings`.

**Other things I assumed** (all listed in the doc):
- Shares come in "view" (default) and "edit". The brief only says the person "sees" the document.
- Only Owners and Editors can share.
- Storage use is charged to the owner of the document's workspace.
- The 25-member limit is enforced by the sign-in provider and counts pending invitations.

**Questions for you:**
1. Should a workspace owner be able to keep other people's agents out of their workspace? A client might want that. The design has room for it, but I didn't add it.
2. Do you want "can edit" shares at all?
3. What should the abuse limits be: documents created per hour, workspaces per person, and shares per document?
4. Can a document ever move to another workspace?

**Session ended:** success, 8 turns, 162814 ms
