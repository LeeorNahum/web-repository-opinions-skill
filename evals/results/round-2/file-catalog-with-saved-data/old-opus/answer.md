I've written the tool catalog to `docs/mcp-tools.md`. It's a design doc, so nothing is built yet, and it isn't committed.

**The catalog: 21 tools**
- **Workspace and sites:** `get_workspace`, `list_sites`, `get_site`, `create_site`, `delete_site`. `create_site` requires an `index.html`. `delete_site` moves the site to Trash and returns the 30-day deadline plus a browser-app restore link. There's no restore tool, matching the brief.
- **Files:** `list_files`, `read_file`, `write_files`, `edit_file`, `import_file`, `start_file_upload` / `finish_file_upload`, `move_file`, `delete_files`.
  - `write_files` writes a set of files all at once or not at all, so a change to several files never goes live half-applied.
  - `edit_file` replaces one exact piece of text, which suits small edits.
  - Images and other assets come in from a URL or through a signed upload, so agents don't have to paste encoded file contents into the call.
- **Saved data:** `list_data_collections`, `list_data_entries`, `get_data_entry`, `add_data_entries`, `update_data_entries`, `delete_data_entries`, `clear_data_collection`. Adding, updating and deleting are separate tools, so a mistyped key can never quietly create or wipe an entry.

**How agents and visitors share saved data**
- Every entry has a revision that changes whenever it's written. An agent has to send the revision it last read to update or delete an entry.
- If a visitor changed the entry in the meantime, the agent gets the current entry back and nothing is overwritten. The agent then reapplies its fix and tries again.
- An agent's fix doesn't change who created the entry, so a visitor can still edit their own RSVP after the agent corrects the name.
- `clear_data_collection` only removes entries that existed when the call started, so RSVPs that arrive while it runs are kept.
- Agent changes show up live on every open page, the same as visitor changes.

**Calls I made where the brief is silent** (all listed at the end of the doc so you can confirm or change them):
1. **Access rules live in a reserved `fernpage.json` file in the site.** That file also declares the saved-data collections. This is the one most worth checking: the brief says rules come from the site's "settings". If you meant a separate settings record, it becomes a pair of read/update tools and nothing else changes.
2. **"Site settings" are just another collection** of saved data.
3. **Rules have three levels: anyone, the entry's creator, or the owner.** The owner and their agents can always do everything. A site without `fernpage.json` has no saved data.
4. **Each connection works in one workspace,** chosen when the person authorizes the agent, so no tool takes a workspace ID.
5. **Files go live as soon as they're written.** There are no drafts.
6. **`index.html` can't be deleted or moved.** To take a site down, the agent deletes the whole site.
7. **The server assigns each site's address,** on a domain separate from the product's own.
8. **All size and count limits are placeholders,** for example 64 KB per entry and 5 MB of saved data per site.
9. **There's no history or undo for saved data.**