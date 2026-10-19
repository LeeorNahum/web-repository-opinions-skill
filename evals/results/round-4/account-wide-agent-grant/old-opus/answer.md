I wrote the design to `docs/workspace-access.md`. I haven't committed it, and no code exists yet; the repo is an empty scaffold.

**Decisions I made**

1. **One gate for everything.** The app and the MCP server both call a single `authorize(principal, capability, target)` check. An agent always acts as its person and can never do more than that person could. Every call re-checks:
   - the person's current role in the workspace, or a direct share on the document;
   - the connection's limits;
   - whether the workspace allows agents at all;
   - storage against the workspace owner's plan, for create and update.
2. **One agent connection covers all workspaces.** A studio lead connects once and reaches every workspace they belong to, including ones they join later. Each call works out its workspace from the document, or from an explicit workspace id, and checks it against real membership. Being removed from a client workspace cuts off their agent on its next call.
3. **Safeguards for the wider connection:**
   - Workspace owners get an "Allow members' connected agents" setting.
   - Each person gets a Connected agents page where they can limit a connection to some workspaces, make it read-only, or revoke it.
   - Every agent edit is recorded as "Name via Agent".
4. **Tools.**
   - New `list_workspaces`, so an agent can look up workspace ids.
   - New `create_document { workspace, title, content? }`. The workspace id is required, with no default and no matching by name, because creating in the wrong workspace was the beta's bug.
   - `list_documents` gets an optional workspace filter.
   - All results now say which workspace a document is in. People who were only sent a single document by email never see that workspace's name.
5. **Library page.**
   - The header workspace switcher is gone.
   - `/documents` shows one library across all workspaces plus "Shared with me", newest changes first, with a workspace badge on each row. The workspace filter lives in the URL.
   - The New document dialog has Workspace as its first field. It's only pre-filled when the choice is clear (the library is filtered to one workspace, or you can only create in one), never from "last used".
   - Documents get their own top-level link, `/documents/[id]`, so people sent a document by email never see a workspace link.

**Assumptions to confirm** (the doc's last section lists all ten)

- **The one-connection decision, above all.** It goes against our own skill's default of one connection per workspace, which I set aside because the brief's feedback says reconnecting per client was the top complaint. The main new risk is one agent session copying content from one client into another, for example if a document contains instructions aimed at the agent. The safeguards above limit this but don't prevent it. If you'd rather have one connection per workspace, the design switches over cleanly.
- **Agents are allowed by default** in workspaces the person doesn't own. Defaulting to off would protect clients more but bring back the per-client friction.
- **Email shares can be either view or edit.** The brief doesn't say.
- **Storage is charged to the workspace owner's plan**, not to whoever makes the edit.
- **The auth provider is Clerk.** That's the skill's default; the brief only says "managed provider". Before writing the token check, we still need to look at a real token to see what claims and scopes it carries.