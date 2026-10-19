I wrote the design to `docs/workspace-access.md`. I haven't committed it and haven't changed `docs/brief.md`.

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