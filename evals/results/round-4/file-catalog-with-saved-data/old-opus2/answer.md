I wrote the MCP tool catalog to `docs/mcp-tools.md`. I didn't commit it.

**The 12 tools**
- **Sites:** `list_sites`, `get_site`, `create_site`, `delete_site`.
- **Files:** `read_file`, `write_files`, `edit_file`, `delete_files`.
- **Saved data:** `list_data_entries`, `create_data_entries`, `update_data_entries`, `delete_data_entries`.

Each tool has its argument and output schemas, annotations (read-only, destructive, idempotent), behavior, and typed error codes. The doc also includes example workflows such as fixing an RSVP or clearing test entries.

**How agents work with saved data**
- **Model:** saved data is organized into collections of keyed JSON entries. Agents act as the site owner, so access rules don't block them.
- **Concurrent visitors:** because visitors may be writing at the same moment, every update and delete must include the entry's current `version`. If a visitor changed the entry in between, that item fails with the current value so the agent can reapply its fix.
- **Partial updates:** updates change only the fields they name (JSON Merge Patch), so fixing a guest's name doesn't overwrite their meal choice.
- **Seeding:** creating entries never overwrites existing ones, and rerunning a seed with the same keys doesn't make duplicates.
- **No "clear collection" tool:** an unconditional clear could quietly delete a real RSVP that arrives during cleanup. Agents list entries and delete the test ones by key.

**File decisions**
- A multi-file write lands all at once or not at all, so visitors never see a half-applied change.
- `edit_file` makes small edits by exact text replacement; each piece of old text must appear exactly once.
- `index.html` can't be deleted on its own.
- Large or binary files are passed as a URL the server fetches, not as inline encoded data.
- `delete_site` moves the site to Trash and returns a link to the browser app for restoring, since restoring is browser-only per the brief.

**Assumptions to check** (all listed at the end of the doc):
1. **Access rules are in a reserved `fernpage.json` file.** The brief says rules are declared "in its settings", which could also mean saved data. This is the biggest call I made. The alternative is two dedicated tools for reading and setting rules.
2. **The workspace is picked when the user connects (OAuth consent).** One connection covers one workspace, and no tool takes a workspace argument. Switching workspaces means reconnecting.
3. **Sites are served at `<address>.fernpage.site`, a domain separate from the app.** Sites run arbitrary JavaScript, so they shouldn't share an origin with the app or each other. The address is chosen at creation, and MCP can't rename it.
4. **Changes go live immediately.** There's no publish step and no rollback or revision history.
5. **Deleting saved-data entries is permanent.** Only whole sites go to Trash.
6. **The limits are placeholders.** These are the file sizes, 5 MB of saved data per site and batch sizes; the brief doesn't set any of them.