I wrote the tool catalog to `docs/mcp-tools.md`. It has 19 tools, an argument schema for each, the shared data shapes, error codes, limits and example flows. I didn't commit it. It's built only from `docs/brief.md` and this repo's own MCP and tool-design guidelines.

**The tools:**
- **Workspaces and sites:** `list_workspaces`, `list_sites`, `get_site`, `create_site`, `delete_site`. Creating a site needs only `index.html` and either creates everything or nothing. Deleting moves the site to Trash and returns the link where the user can restore it in the browser app.
- **Files:** `list_files`, `read_file`, `create_files`, `replace_files`, `edit_file`, `delete_files`. Adding and replacing are separate tools, so an agent can't overwrite a file it thought was new. Replacing requires the file's current version. `edit_file` does small find-and-replace edits for the brief's "one small edit" case. Images and other binary files come in by URL rather than pasted into the call.
- **Saved data:** `get_data_rules`, `set_data_rules`, `list_entries` (with text search, for finding the misspelled RSVP), `get_entry`, `create_entries`, `update_entries`, `delete_entries`, `delete_all_entries`. Wiping a whole collection is its own tool, so a missing argument can never turn "delete these" into "delete everything".

**How agents work with saved data:**
- **Rules:** Each site has one rules document listing its collections. For each one it says whether any visitor, only the visitor who created an entry, or only the owner may read, create, update or delete. That covers both examples in the brief. Agents act for the owner, so the rules never block them.
- **Writing while visitors write:** Agents change one entry at a time, like visitors do, so every open page updates live. When updating an entry, the agent must either give the version it read (and get a conflict back with the current value if a visitor changed it) or explicitly choose to apply on top of whatever is there. An update only touches the fields it names, so a visitor's change to another field is kept.
- **Clearing a collection:** Visitor entries that arrive while it runs are kept.
- **Removing a collection from the rules:** This fails while it still has entries, so changing rules never deletes data.

**Main assumptions** (all 15 are listed at the end of the doc):
- Each connection acts in the one workspace the user picks when authorizing it.
- A site goes live as soon as it's created, with no draft or publish step.
- `index.html` can't be deleted on its own; removing a site goes through `delete_site`.
- Deleting a file or an entry is permanent. The brief only gives whole sites a Trash.
- The data rules are their own settings document, not a file in the site. "Site settings" in the brief's saved-data examples are ordinary entries, by convention `settings/main`.
- I added a read rule so RSVP details can stay private. The brief only mentions write rules.
- All size and count limits are placeholders.

**Open questions for you:**
- What a site's public URL looks like, and whether users choose their own address.
- Whether file changes should keep a history so a bad edit can be rolled back.
- Whether to add a tool for renaming or moving a file.
- Whether sites anyone can write to need per-visitor rate limits.
- Whether deleting saved data should be undoable for a short time.
- Whether to ship a step-by-step guide for agents (an Agent Skill) alongside the server.