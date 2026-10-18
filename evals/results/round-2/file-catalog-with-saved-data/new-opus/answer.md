I've written the tool catalog to `docs/mcp-tools.md`. Nothing is committed.

**The main design choice:** agents see a site as a tree of files, and saved data is part of that same tree. It lives under a reserved `@saved/` folder:
- **Entries:** each saved-data entry is one JSON file, for example `@saved/rsvps/<entryId>.json`.
- **Settings:** `@saved/settings.json` holds both the settings the page reads and the rules for who may write each collection.

Agents already know how to list, search, read, write and edit files, so they use the same tools for a stylesheet and an RSVP. Behind each file operation, a change to saved data is still a change to one entry, made the same way a visitor's browser makes it, with the same checks and limits. Every open page sees the change live.

**The 12 tools:**
- **Reads:** `list_workspaces`, `list_sites`, `get_site`, `list_files`, `search_files`, `read_file`
- **Changes:** `create_site`, `delete_site`, `write_files`, `edit_file`, `delete_files`, `add_saved_entries`

**Decisions worth checking:**
- **Visitors writing at the same moment:** agents don't have to pass a version number. Fernpage remembers what each agent connection last read. If an agent tries to replace a whole entry that a visitor changed since then, the write is refused and the agent is told to read it again. `edit_file` replaces exact text in what's stored now, so a visitor's change to a different field survives.
- **Removing things:** deleting takes exact paths only, never a folder or wildcard, so a missing or wrong argument can't delete more than intended. `delete_site` is a separate tool and moves the site to Trash for 30 days, as the brief says. Agents get no restore tool, because restoring happens in the browser app only.
- **New entries:** Fernpage creates entry IDs, and new entries only come from `add_saved_entries`. Writing to an entry path that doesn't exist is refused, so a typo can't create a stray RSVP.
- **Site details:** there are no title, description or favicon arguments; they come from `index.html`. Any change to `index.html` returns the updated title. `create_site` requires `index.html`, and `index.html` can't be deleted on its own.
- **Images and other large files:** they go in as a fetchable HTTPS URL, not inside the request. A local file path is refused with an error that says which routes work.

**What I assumed (all 13 are listed in the doc):**
- Collections must be declared in the settings file before they can hold entries.
- The owner can always write every entry; the rules only limit visitors. Any member of a workspace counts as an owner of its sites.
- Changes go live immediately, with no draft step.
- Deleting a file or entry is permanent; only whole sites go to Trash.
- Fernpage assigns the site's address; agents can't choose it.
- An agent's access covers all of the user's workspaces.
- The size limits are placeholders, including 5 MB of saved data per site.
- There's no move/rename tool.

**Questions for you:**
- Should agents be able to choose a site's address?
- Do you want a draft or preview step before changes go live?
- Should deleted files and entries have an undo period, like Trash for sites?
- Should visitors' pages be able to read the write rules, or only the settings values?
- Should collections get an optional field schema so wrongly shaped entries are caught?