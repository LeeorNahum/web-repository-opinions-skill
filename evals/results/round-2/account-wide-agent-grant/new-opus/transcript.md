**Prompt:** Design the authorization model behind our MCP tools, including the create tool we still need, and the workspace handling on the library page. Write it to docs/workspace-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-new-opus/work\" && git ls-files | head -100 && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5601 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat workspace-tenancy.md model-context-protocol.md agent-tool-design.md"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat auth.md app-surface.md query-state.md routing.md bootstrap.md"}`

> Result: # Workspace Tenancy  Give a product workspaces when shared ownership, membership, or policy needs them now or is on the product's plan, because retrofitting an ownership boundary costs far more than carrying one early. A product whose data will only ever belong to one person keeps it on the user account, with no organization layer. When a product's collaboration model is workspaces, back every w [... 18176 more characters]

> Result: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 24170 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-account-wide-agent-grant-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat ids.md user-facing-errors.md quota.md | head -150"}`

> Result: # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.  ## Entity IDs  For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.  - Length: a fixed 12 characters. - Alphabet: Base58, the case-sensi [... 5895 more characters]

**Tool call `Write`:** `<run>\builds\2-account-wide-agent-grant-new-opus\work\docs\workspace-access.md`

````text
# Workspace Access

How Alderdocs decides who can do what to which document, from the web app and from an agent over MCP, and how the library page deals with workspaces. `docs/brief.md` holds the owner's decisions. This document builds on them, and the calls it makes beyond the brief are listed under [Assumptions](#assumptions-to-confirm).

## Principles

1. **One gate.** Every read and write goes through a single authorization module in the backend. The web app, the MCP server, and any later API all call it, and none of them keeps its own rules. The UI hides actions a person can't take, but the gate is still what enforces them.
2. **Check the target on every call.** Each call finds the document or workspace it touches and checks the caller's live access to it at that moment. No token, session, or UI state is trusted to have picked the workspace.
3. **The URL or an argument names the workspace, never ambient state.** No active workspace is stored in a session, cookie, or client memory. This is what fixes the beta problem of documents created in the wrong workspace.
4. **Fail closed.** No verified identity, unknown capability, or no access path means the call is refused with one product error.

## Principals and access paths

A caller is always a person: an Alderdocs user identified by the auth provider's stable subject ID. An agent acts as the person who connected it, limited by the token's scopes. It never has an identity of its own.

A person can reach a document in exactly two ways:

| Path | Comes from | Gives access to |
| --- | --- | --- |
| **Membership** | A live membership in the document's workspace, with a role | Every document in that workspace, as far as the role allows |
| **Share** | An individual share of that one document to the person's verified email, with a share role | That one document only. Not its workspace's other documents, member list, or settings |

If neither path covers the target, the person has no access. If both apply, the stronger one wins.

## Roles and capabilities

Every action is a named capability. Access to an action is the intersection of three things:

```
allowed = capability granted by (membership role ∪ share role on this document)
          ∩ capability allowed by the token's scopes (MCP / API callers only)
```

| Capability | Owner | Editor | Viewer | Share: edit | Share: view |
| --- | :-: | :-: | :-: | :-: | :-: |
| `document.list` (see it in lists) | ✓ | ✓ | ✓ | ✓ (that document) | ✓ (that document) |
| `document.read` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `document.update` | ✓ | ✓ | – | ✓ | – |
| `document.create` (in the workspace) | ✓ | ✓ | – | – | – |
| `document.delete` | ✓ | ✓ | – | – | – |
| `document.share` | ✓ | ✓ | – | – | – |
| `workspace.members.manage` | ✓ | – | – | – | – |
| `workspace.settings.manage` | ✓ | – | – | – | – |
| `billing.manage` (owner's plan) | ✓ | – | – | – | – |

The capability map lives in code, in the shared authorization package. It is not stored in env or provider configuration.

### Mapping onto the auth provider

- **One provider organization per workspace,** including the one created at sign-up, as the brief already decides. The sign-up workspace gets a personalized name (for example "Dana's workspace") and has no special status after that. There's no "personal" flag, and it follows the same rules as every other workspace.
- **Personal-account (no-organization) mode is off,** so every session belongs to some workspace.
- **Provider roles stay at the built-in admin and member.** Owner maps to provider admin. Editor and Viewer are both provider members, and the product role is stored on Alderdocs's own membership row, which the gate reads. That way the gate owns the Owner/Editor/Viewer distinction, and changing auth provider doesn't change the role model.
- **Member cap of 25.** The gate enforces the cap when an invitation is sent. The cap is also mirrored onto the provider's per-organization membership limit, which counts pending invitations and blocks extra ones server-side. The instance default limit is 1, so a workspace whose mirror hasn't synced fails closed. Individual shares don't count against the cap, because sharing a document doesn't make someone a member.
- **Workspace creation is free,** limited only by a generous fixed provider limit to stop abuse. Plans are priced on storage, not workspaces.

## MCP authorization

### Grant scope: account-wide

An MCP connection is an **account-wide grant**: it covers every workspace the person belongs to now or later, plus every document shared with them individually. This is what studio leads asked for. The competitor's per-client reconnecting was the most common complaint, so a grant tied to one workspace would bring that problem back.

- The consent screen says so plainly: *"This agent will be able to act on your behalf in all your Alderdocs workspaces, including ones you join later, and on documents shared with you."*
- New workspaces don't need a reconnect. Leaving a workspace, losing a share, or being demoted takes effect on the next call with the existing token, because every call checks again.
- The token's organization claim, if the provider includes one, is ignored when choosing a target. It proves nothing about any other workspace.

### Token verification

- Endpoint: `https://mcp.<domain>/mcp`. MCP is its own Hono app (`apps/mcp`) on the official MCP SDK's web-standard transport. It is stateless, with buffered JSON responses.
- Tokens are verified directly with the auth provider's backend SDK, by signature for JWTs or by introspection or userinfo for opaque tokens. A token body that hasn't been verified is never used.
- The issuer is always enforced. The **audience must include the MCP resource** (`https://mcp.<domain>/mcp`), and the provider is configured to issue it. A token without that audience is refused.
- Scopes:
  - `documents:read`: `list_documents`, `read_document`, `list_workspaces`
  - `documents:write`: `create_document`, `update_document`

  Every advertised scope is enforced. A missing scope gets the protocol's insufficient-scope challenge, not a generic denial. If the provider can't issue custom scopes, scopes are not advertised, and that gap is written next to the verifier (see assumptions).
- Protected-resource metadata is served with `Cache-Control: no-store` and points to the authorization server's own metadata URL, not a proxied copy.
- Enterprise-managed authorization (ID-JAG) is added only if the provider supports it natively, and it comes on top of the standard OAuth flow, never instead of it.

### Per-call resolution

For every tool call, after the token is verified:

1. Resolve the user from the verified subject. A user that is closed or tombstoned is refused.
2. Find the target: the document by `id` for reads and updates, or the workspace by `workspace_id` for creates.
3. Load the caller's **live** membership in that workspace and any share of that document.
4. Check the capability against `role ∪ share` ∩ token scopes.
5. Act, inside the same backend transaction that did the check.

A missing document and a document the caller can't access give the **same** error, so an ID never reveals that a document exists.

### Tool catalog

All tools are advertised to every caller as one fixed catalog, and each call is authorized on its own. A Viewer still sees `create_document`. If they call it, the gate refuses with a message that explains why.

| Tool | Annotation | Scope | Capability |
| --- | --- | --- | --- |
| `list_workspaces {}` | read-only | `documents:read` | membership exists |
| `list_documents { query?, workspace_id?, cursor? }` | read-only | `documents:read` | `document.list` |
| `read_document { id }` | read-only | `documents:read` | `document.read` |
| `create_document { workspace_id, title, content? }` | not read-only, additive | `documents:write` | `document.create` in `workspace_id` |
| `update_document { id, content }` | not read-only, **destructive** (replaces content) | `documents:write` | `document.update` |

**`create_document` (new).**

- `workspace_id` is **required** and has no default. The server never falls back to the home workspace, the most recent workspace, or whatever the token's organization claim says. An omitted argument must never quietly create something somewhere, and that guess is exactly what produced documents in the wrong workspace in the beta.
- The caller needs Editor or Owner in that workspace. A person who can only reach a workspace's documents through shares can't create there.
- Storage quota for the workspace owner's plan is checked before the write and counted after the document is durably stored. Running out of storage gets its own error that names the owner's limit. It is never a generic failure.
- The result is the full document resource: `id`, `title`, `workspace { id, name }`, `updated_at`, and `url` (`https://app.<domain>/library/<id>`).
- A retry after a timeout can create a duplicate, and the tool description says so. It has no idempotency key, because a duplicate draft is cheap and easy to see. Revisit this if the tool ever has an expensive side effect.

**`list_workspaces` (new).** This is needed so an agent can find a valid `workspace_id` for `create_document`, including a workspace that has no documents yet. It returns `{ id, name, role }` for each live membership, and it never includes workspaces the person reaches only through shares.

**`list_documents` (changed).**

- With no `workspace_id`, it lists documents across all memberships plus individual shares. That's the cross-client view studio leads want.
- `workspace_id` only narrows the list. The server checks the membership. An unknown or non-member workspace gets the standard no-access error, not an empty list.
- Each result includes `access: "member" | "shared"`. Results from a membership include `workspace { id, name }`. Shared results leave the workspace out, so a share never reveals the workspace's identity or invites a create attempt there.
- Default order is most recently updated first, across all workspaces.

**`read_document` / `update_document` (unchanged signatures).** The workspace is always taken from the document itself, never from an argument. `update_document` replaces the whole content, so it is annotated destructive. The server refuses an update if the document changed after this caller's last read, with a conflict error that asks for a fresh read. That way an agent can't silently overwrite a teammate's edit, and callers never have to send a revision token.

### Errors (product-owned, protocol-neutral)

| Outcome | Message shape |
| --- | --- |
| `not_found_or_no_access` | "No document with id `X` is available to you. Call `list_documents` to find documents you can open." |
| `workspace_not_available` | "You're not a member of workspace `X`. Call `list_workspaces` for the workspaces you can create in." |
| `insufficient_role` | "Your role in Acme is Viewer, so you can read but not create or edit documents there." |
| `insufficient_scope` | Protocol insufficient-scope challenge naming `documents:write`. |
| `storage_limit_reached` | "Acme's owner has used their storage allowance (X of Y). Ask them to free space or upgrade." |
| `edit_conflict` | "This document changed after you last read it. Read it again, then retry the update." |

Errors never include raw provider, framework, or stack details.

### Attribution

Every write records the person who made it plus `via: "mcp"` and the grant (client) ID. Change history and the library can then show "Dana via Claude", which answers the studio-lead complaint about losing track of what changed.

## Library page

### No active workspace

The header has **no active-workspace switcher**. The library spans every workspace by design, so it doesn't need an active workspace.

### Routes

```text
/library                              all documents the person can reach (cross-workspace)
/library/<documentId>                 one document, whichever workspace it belongs to
/w/<workspaceId>                      resolves (history replace) to the workspace's settings
/w/<workspaceId>/members              workspace members (Owner manages)
/w/<workspaceId>/settings             workspace name, etc.
```

- Documents live at the top-level `/library/<id>`, not under the workspace prefix. A shared document's recipient can then open it without joining or activating its workspace, and links survive if moving documents between workspaces is ever allowed.
- `/w/...` is used only for things that really belong to a workspace. When the app reaches one of these pages it switches the provider's active organization to match the URL segment before rendering. The session follows the URL. A workspace segment that's unknown or not allowed shows a product "You don't have access to this workspace" screen.
- IDs are 12-character Base58 entity IDs from the shared helper.

### Query state

Fixed order, matching the visible controls: `q`, then `workspace`, then `sort`.

| Param | Values | Absent means |
| --- | --- | --- |
| `q` | free text | no search |
| `workspace` | a workspace `id`, or `shared` (documents shared with me) | all workspaces and shares |
| `sort` | `updated` (default), `title`, `created` | `updated` |

- `shared` can't collide with an ID, because IDs are exactly 12 characters.
- A `workspace` value the person isn't a member of gets the same no-access message inline. It doesn't silently show an empty list.
- "Load more" is not part of the URL.
- The filter is only a way of browsing. It never authorizes anything and never decides where a new document goes on the server.

### Rows

Each row shows the title, a **workspace badge** (or "Shared with you"), the last-updated time, and the last editor, including "via agent" when the edit came from one. With the default sort by updated time across all workspaces, a studio lead can see what changed for every client in one place.

### Creating a document

- "New document" opens a creation dialog that has its own URL: `/library?new=document` (with `&workspace=<id>` to preselect a workspace).
- The dialog has a **required workspace field** that lists only workspaces where the person is Owner or Editor.
  - Prefilled when the library is filtered to one workspace, or the `workspace` param names one, or the person can create in exactly one workspace.
  - Otherwise empty and must be chosen. Nothing is remembered from last time.
  - The submit button names the target: **"Create in Acme"**.
- The client always sends an explicit `workspaceId`, and the server runs the same `document.create` check that the MCP tool uses.

## Account and workspace lifecycle

- Revoking a membership or share takes effect immediately in the app and over MCP, because every call checks again.
- Deleting an account goes by membership. An owned workspace with no other active members is deleted along with its provider organization. One that other people still use stays, under an anonymized owner, until ownership is transferred.
- Closed accounts leave a hashed-subject record behind, so a token issued before closure can't recreate the user.

## Assumptions to confirm

These are calls I made where the brief was silent. Each can be changed without reworking the model.

1. **Account-wide MCP grant, with no per-workspace option at launch.** A workspace-bound grant option (consent chooses one workspace, the same OAuth resource) can be added later if a client studio requires that its connection never reaches other tenants.
2. **Shares have a role, view or edit**, picked by the sharer. The brief says a share covers one document but not what the recipient can do.
3. **Editors can create, delete, and share documents.** Only Owners manage members, settings, and billing. Sharing is the riskiest of these, because it sends a document outside the workspace. Restricting it to Owners would be a single change in the capability map.
4. **Exactly one Owner per workspace,** following "paying owner" in the brief. Ownership transfer is out of scope here.
5. **Viewers can't create.** Creating needs Editor or Owner, both in the app and over MCP.
6. **`list_workspaces` was added** as a fourth existing-style tool, because `create_document` needs a workspace ID that an agent otherwise can't find for an empty workspace.
7. **`list_documents` got an optional `workspace_id` filter,** and shared results don't reveal their workspace.
8. **`create_document` has no idempotency key.** Duplicate drafts after a retry are accepted, and the tool description warns about them.
9. **Storage quota is charged to the workspace owner's plan,** including for documents created by Editors or by agents.
10. **Library URLs:** `/library` and `/library/<id>`, with workspace pages under `/w/<id>/…`. The word "library" is the product's name for the page.
11. **The auth provider can issue custom scopes and an MCP audience.** I haven't checked this against a real token yet. Before shipping, decode a real token and confirm `aud` and the scopes. If either is missing, the verifier must record that gap rather than advertise a check it doesn't make.
12. The production domain is still a placeholder (`<domain>`).

````

> Result: File created successfully at: <run>\builds\2-account-wide-agent-grant-new-opus\work\docs\workspace-access.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/workspace-access.md` but haven't committed it. The repo has no app code yet, so this is design only and nothing has been built or tested.

**Authorization model**
- **One check for everything:** a single authorization module checks every action, for the web app and MCP alike. What a person can do comes from their role in the document's workspace (Owner, Editor, Viewer) or from a share of that one document. For an agent, it's also limited by the token's scopes.
- **Fresh check on every call:** every call looks up the target's live access again. Removing someone from a workspace or a share takes effect on tokens they already have.
- **Roles in the auth provider:** Owner is stored as the provider's admin role. Editor and Viewer are both provider members, and Alderdocs's own records hold the difference.
- **Member cap:** the 25-member limit is enforced by Alderdocs and copied onto the provider's own limit, so extra invitations are blocked. Document shares don't count toward it.

**MCP**
- **Account-wide connection:** one MCP connection covers all of a person's current and future workspaces plus documents shared with them. That directly answers the "reconnect per client" complaint, and the consent screen says it plainly.
- **Token checks:** the server only accepts tokens issued for it, and scopes are `documents:read` and `documents:write`.
- **`create_document { workspace_id, title, content? }`:** the workspace is required and has no fallback, so a document can't silently land in the wrong place. It needs Editor or Owner, and checks the owner's storage before writing.
- **New `list_workspaces` tool:** without it, an agent can't find the ID of a workspace that has no documents yet.
- **`list_documents` changes:** it gets an optional `workspace_id` filter that can only narrow the list.
- **`update_document` changes:** it refuses to overwrite a teammate's edit made since the agent last read the document.
- **Errors:** "doesn't exist" and "no access" return the same message, so IDs reveal nothing.
- **Edit history:** every edit records "via agent", so the library can show what an agent changed.

**Library page**
- **No workspace switcher:** the header has none, and `/library` lists documents from every workspace, newest first, each with a workspace badge.
- **Shareable filters:** search, workspace and sort are in the URL (`?q=…&workspace=<id>|shared&sort=…`). The filter only affects what you see, never where a new document goes.
- **Document links:** documents live at `/library/<id>`, so someone a document was shared with can open it without joining that workspace. Workspace pages are under `/w/<id>/…`.
- **New document dialog:** it has a required workspace field, the button reads "Create in Acme", and nothing is remembered from last time.

**Assumptions to confirm** (all twelve are listed at the end of the doc; these matter most):
- **Shares carry a role:** the person sharing picks view or edit.
- **Editors can share documents:** limiting sharing to Owners would be a one-line change.
- **One Owner per workspace,** and storage counts against that owner's plan.
- **No idempotency key on create:** a retry after a timeout can make a duplicate draft, and the tool description warns about it.
- **Not yet checked:** I haven't confirmed that the auth provider can issue custom scopes and tokens addressed to the MCP server. That needs a check against a real token before shipping.

**Session ended:** success, 8 turns, 131387 ms
