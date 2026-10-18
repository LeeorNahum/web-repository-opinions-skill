I wrote the design to `docs/workspace-access.md`. It's design only: the repo has no app code yet, so nothing is built or tested. I haven't committed it.

**The main decision:**

- **One agent connection covers all of a person's workspaces.** The skill's default is a connection limited to one workspace, where switching means connecting again. That would bring back the "reconnect per client" complaint from the brief, so I didn't follow it. Instead, the connection says who the person is, and each tool call names the workspace or document it acts on. Membership is checked live on every call. The downside is that a leaked token reaches more workspaces. To limit that:
  - a connection can be read-only;
  - a person can limit which workspaces each connection reaches;
  - each workspace Owner can turn off agent access for their workspace;
  - every agent edit is recorded as, for example, "Dana via Claude";
  - disconnecting takes effect immediately.

**Authorization:**

- Every surface (web app, MCP, background jobs) goes through one check. Access comes from your role in the document's workspace, or from an email share of that document.
- For agents, three more limits apply: the connection's read/write permissions, the workspace's agent setting, and which workspaces that connection may reach.
- Nothing ever holds a "current workspace."

**MCP tools:**

- **New `create_document { workspace, title, content? }`:** the workspace ID is required and there is no fallback to a default. This fixes the documents-in-the-wrong-workspace problem.
- **New `list_workspaces`:** lets the agent find workspace IDs.
- **`list_documents`:** gains an optional workspace filter.
- **All tools:** results now say which workspace each document is in and what access the person has.
- **Error messages:** each one tells the agent what to do next. "Not found" and "not a member" give the same answer, so workspace and document IDs can't be probed.

**Library page:**

- The header workspace switcher is gone.
- `/documents` shows everything you can reach, across all workspaces plus documents shared with you. It's sorted by last changed and shows who changed each one, so studio leads can see what changed across clients.
- Search, workspace filter and "shared with me" are kept in the URL.
- Document links are `/documents/<id>`, so they work the same for people a document was shared with.
- When creating a document, you have to pick the workspace. It's only filled in when there's no ambiguity: you can only create in one workspace, or the library is already filtered to one. There's no "last used" default.

**Assumptions to confirm** (all listed in the doc; the first three matter most):

1. One connection covers all workspaces, rather than one per workspace.
2. Agent access is on by default in each workspace. Off would mean every client Owner has to opt in first.
3. A connection automatically reaches workspaces you join later.
4. Shares are either view or edit, and default to view.
5. Editors can create and share documents; only Owners manage the workspace.
6. Documents have a title and don't move between workspaces.
7. Storage counts against the plan of the Owner of the workspace the document is in.

At the end of the doc I left three open questions:
- Should client Owners see which members have agents connected?
- Should `update_document` guard against overwriting someone's simultaneous edit?
- Should `create_document` prevent duplicates when an agent retries?