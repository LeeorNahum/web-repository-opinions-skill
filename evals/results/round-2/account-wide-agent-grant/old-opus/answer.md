I wrote `docs/workspace-access.md`. Nothing is committed and no code changed yet.

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