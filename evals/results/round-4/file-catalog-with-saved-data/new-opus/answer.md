I've written the tool catalog to `docs/mcp-tools.md`. It's a design document only: nothing is built yet and nothing is committed.

**The core decision: saved data uses the same file tools as everything else.** Agents see each site as a folder. Pages and assets are ordinary files. Saved data appears as JSON files in a reserved folder that visitors can't fetch: one file per collection (`.fernpage/saved/rsvps.json`) plus `.fernpage/settings.json` for the write rules and setting values. There are no separate tools for saved-data entries.

**Concurrent visitors.** When an agent writes a saved-data file, the server works out which entries changed and checks each one against the site's rules and size limits, the same way it would a visitor's write. It compares against what that agent last read in full:
- Entries the agent didn't touch keep any changes visitors made in the meantime, including new RSVPs and deletions.
- If the agent and someone else both changed the same entry, the write is refused as a conflict that names those entries, and the agent re-reads.
- If the agent never read the file, it can only add entries. So it can seed a checklist without reading first, but it can't silently overwrite visitor entries.

**Eleven tools:**
- **Reading:** `list_workspaces`, `list_sites`, `get_site`, `list_files`, `read_file`, `search_files`.
- **Creating and changing:**
  - `create_site` needs `index.html` among its files and publishes the site immediately.
  - `write_files` handles a batch, with one result per file.
  - `edit_file` replaces exact text, which covers one-line fixes like a misspelled RSVP name or changing a setting.
- **Removing:** `delete_files` takes exact paths only. `delete_site` moves the site to Trash for 30 days. There's no restore tool, since the brief says restoring happens only in the browser app.

The doc also gives argument schemas, result shapes, error codes with the next step for each, worked examples, and a list of things deliberately left out (publish step, upload staging, confirmation flags).

**Assumptions to review** (all 13 are listed at the end of the doc; these are the main ones):
1. The brief doesn't define how saved data is structured, so I assumed named collections of keyed JSON objects. Each entry carries read-only details (when it was created and by whom), which helps an agent spot test entries before launch.
2. Write rules use three levels: `anyone`, `author` (the visitor who created the entry) and `owner`. That covers both examples in the brief. A collection with no declared rules can be read by anyone but written only by the owner.
3. Agents act as the site owner. One sign-in covers all the user's workspaces, but `create_site` always needs an explicit `workspace_id`.
4. `index.html` can't be deleted, because the title, description and favicon come from it; taking a site down means deleting it. A site goes live on creation and has no unpublished state. Individually deleted files can't be recovered.
5. Site addresses are generated lowercase names on a separate domain. Site IDs can't be used because web addresses ignore case and the IDs don't. Neither domain is chosen, and whether users can pick their own address is still open.
6. Every size limit is a placeholder (for example 256 KB per inline file, 5 MB of saved data per site) and needs sizing against real budgets.
7. Whether some saved data, like RSVP details, should be hidden from visitors is still open. The rule format already allows owner-only reads.