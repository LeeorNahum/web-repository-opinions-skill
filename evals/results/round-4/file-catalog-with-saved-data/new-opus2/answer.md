I've written the catalog to `docs/mcp-tools.md`. It's a design only: nothing is implemented, and I haven't committed it.

**The tools (10):** `list_workspaces`, `list_sites`, `create_site`, `delete_site`, `list_files`, `read_file`, `search_files`, `write_files`, `edit_file`, `delete_files`. The doc gives each one its argument schema, what it returns, how it can fail, whether a retry is safe, and whether it's read-only or destructive.

**How agents work with saved data:** through the same file tools, with no separate record tools.
- **Data files:** each data collection appears as `.data/<collection>.json`, a JSON object where each top-level key is one entry. Writing that file creates, updates or deletes entries, and each change goes through the same rules and limits as one visitor write. The agent counts as the site owner.
- **Writing while visitors write:** a write is compared with the version the agent last read in full. Entries the agent didn't touch keep whatever visitors did meanwhile, so a new RSVP isn't lost. If the agent and someone else changed the same entry, the write is refused and the agent is told to read again. No call has to carry a version token.
- **Small fixes:** `edit_file` replaces exact text against the current content, so fixing a misspelled RSVP name needs no prior read. The doc has a table of how to seed a checklist, clear test entries, change a setting, and change the rules.
- **Deleting:** `delete_files` takes a list of exact paths and refuses directories and data collections. Whole sites only go through `delete_site`, which moves them to Trash for 30 days, and the result links to the browser app for restoring.

**Calls I made where the brief is silent** (the full list is at the end of the doc):
1. Write rules live in a root file, `fernpage.json`. The "site settings" in the brief's saved-data list are treated as ordinary saved data (a `settings` collection). If the brief meant those to be one thing, they should be merged.
2. The rules language (`anyone` / `creator` / `owner`) is only a sketch. I added rules for who may *read* saved data, because RSVPs hold personal details.
3. There's no draft or publish step: writes go live immediately.
4. Data files show only entry values. Who created an entry and when stays on the server.
5. One connection covers all the user's workspaces, and any workspace member can edit its sites.
6. The site's address can be picked when the site is created and changed later only in the browser app.
7. A site in Trash stops serving and refuses writes. Deleting a single file is permanent.
8. Domains and the size, count and rate limits are placeholders.

The ones most worth your decision tomorrow are 1, 2 and 3, because they change the tool contract.