I've written the design to `docs/workspace-access.md` and haven't committed it. Assumptions and open questions for you are at the end of the doc.

**The main calls:**

- **One permission check for everything.** All reads and writes, from the app, the MCP tools and background jobs, go through one function in the backend. Access depends on the person's role in the workspace the document belongs to, or on a share they hold for that document.
- **No "active workspace" anywhere.** Each document's workspace is stored on the document. Nothing in the session decides it. The only time anyone picks a workspace is when creating a document.
- **One agent connection covers all of a person's workspaces.** The connection acts as the person. Each tool call is checked against their current role, so joining or leaving a client workspace takes effect on the agent's next call. The usual pattern is one workspace per connection, but your users named per-client reconnecting as their top complaint about a competitor, so I went against it. The cost is that a leaked connection reaches all of that person's workspaces, so the doc plans short-lived tokens and a way to revoke a connection from account settings.
- **New `create_document { workspace, title, content? }`.** The workspace ID is required and has no default, which is the agent version of the beta's wrong-workspace problem. I also added a read-only `list_workspaces` tool so an agent can find workspace IDs and see where it's allowed to create.
- **The library is one page across all workspaces, at `/documents`.** Changes from every workspace appear together, newest first, and each row shows its workspace. The sidebar holds filters, saved in the URL, instead of a switcher. The "new document" dialog requires choosing a workspace and only fills it in when there's no ambiguity. Documents get their own top-level URLs, so people a document is shared with open the same link as members. Workspace settings and members live under `/w/<id>/`.
- **Shared documents hide their workspace.** A missing document and one you can't access return the same "not found", so nobody can probe for document IDs.

**Assumptions most worth your review:**
- The all-workspaces agent connection described above.
- Shares come in two levels, view and edit, defaulting to view. Your brief doesn't say whether a person a document is shared with can edit it.
- I read "shared with one person by email" as "each share goes to one individual", with several shares allowed per document. If you meant at most one share per document, that's a single constant to change.
- Editors can create, edit and share documents. Only Owners manage the workspace and its members.
- Storage counts against the workspace owner, including what other members' agents write.
- Sharing isn't available to agents for now, since it sends access to an outside email address.

**Still unverified:** I haven't checked whether the auth provider can issue the read and write permission levels the design gives agent connections. The doc says to test that with a real token before building, and what to do if it can't.

The doc also lists open questions, including:
- whether a person can limit an agent connection to some of their workspaces;
- whether a workspace Owner can block members' agents;
- what happens when an agent overwrites a person editing the same document at the same moment.