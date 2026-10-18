I've written the design to `docs/workspace-access.md` but haven't committed it. The repo has no app code yet, so this is design only and nothing has been built or tested.

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