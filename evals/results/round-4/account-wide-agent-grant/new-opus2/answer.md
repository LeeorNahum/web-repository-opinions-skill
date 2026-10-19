I've written the design to `docs/workspace-access.md`. I haven't committed it.

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