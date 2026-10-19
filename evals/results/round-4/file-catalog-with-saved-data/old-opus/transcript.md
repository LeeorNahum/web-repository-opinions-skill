**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-file-catalog-with-saved-data-old-opus/work\" && cat docs/brief.md && git ls-files"}`

> Result: # Fernpage  Fernpage hosts small interactive static sites that people's AI agents write for them: a wedding RSVP page, a team checklist, a recipe box. A site is HTML, CSS, JavaScript, and assets, served at its own URL.  ## Saved data  Sites can keep small saved data, such as RSVP entries, checklist state, and site settings. It is a few kilobytes to a few megabytes per site, stored in our reactive  [... 5643 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md agent-tool-design.md"}`

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat live-data.md ids.md workspace-tenancy.md data-deletion.md bulk-actions.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 8261 more characters]

> Result: # Live Data  Prefer a reactive backend whose queries push updates to the client, and wire it so the UI updates live. Convex is the default. Live updates are a core reason to choose a reactive backend, so realize that value rather than leaving it half-wired.  - Subscribe to data through the reactive client so a change on the backend reflects in every open view without a manual refetch or a page [... 13034 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat object-storage.md uploads.md abuse-resistance.md quota.md data-model.md source-of-truth.md"}`

> Result: # Object Storage  Large user files belong in object storage, not the database. Cloudflare R2 is the default. Any S3-compatible store fills the role.  The database is the source of truth for metadata, ownership, status, and permissions. It stores the object key and references the bytes. Object storage holds only the bytes.  - Keep large media in object storage and store only its key and metad [... 14136 more characters]

**Tool call `Bash`:** `{"command": "cd \"C:/tmp/wro-eval3/builds/3-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat http-apis.md naming.md agent-skills.md user-facing-errors.md path-display.md | head -400"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 11332 more characters]

**Tool call `Write`:** `C:\tmp\wro-eval3\builds\3-file-catalog-with-saved-data-old-opus\work\docs\mcp-tools.md`

````text
# Fernpage MCP tool catalog

This is the tool surface that AI agents use to build and maintain Fernpage sites. `docs/brief.md` wins over this document. If the two disagree, fix this document.

Calls the brief does not settle are marked **Assumed** where they come up, and they are all collected in [Assumptions to confirm](#assumptions-to-confirm) at the end.

## Server

- Endpoint: `https://mcp.<fernpage-domain>/mcp`, served by a separate `mcp` protocol app (official MCP SDK, web-standard transport on Hono). It is stateless, and each tool call gets a buffered JSON response.
- Every caller sees the same static catalog. Authorization runs on every call at the product boundary, the same one the browser app and the runtime SDK pass through. The tool list itself is not a security boundary.
- Authorization is standard MCP OAuth. **Assumed:** each grant is bound to one workspace, chosen on the consent screen. To work in a different workspace, the user authorizes again and picks that workspace. Tools therefore never take a `workspace_id`. They act in the workspace on the token. `get_workspace` tells the agent which workspace that is.
- Tools are thin adapters over shared product capabilities. Site, file, and data rules live in the backend, not in the MCP app.

## Conventions

**Names.** Tool names are `verb_noun` in snake_case. A singular noun means the tool acts on one item. A plural noun means it takes a list and returns one result per item.

**IDs.** Workspaces and sites use 12-character Base58 IDs (`id`). Saved-data entries are addressed by `collection` + `key`. Reads such as `list_sites` can match on a name. Anything that deletes or overwrites takes a stable ID, a path, or a key, never a title.

**Paths.** A file `path` is relative to the site root. It has no leading slash, uses `/` between segments, and is case-sensitive, for example `index.html` or `assets/logo.png`. Folders are implied by paths and do not exist on their own. Every path a tool returns can be passed straight back to another tool. File entries carry both `path` and `name`, where `name` is the last segment.

**Revisions.** Every file and every data entry has an opaque `revision` string, which changes on every write. Tools that overwrite take the revision the caller last saw. If the item has changed since, the call is refused with `revision_conflict` and the error includes the current state.

**Going live.** **Assumed:** there is no draft or publish step. Once a write lands, it is what visitors get. This follows from "one `index.html` is enough to publish a site".

**Errors.** Refusals come back as a typed `code`, a short message in plain language that names what was measured and the next step to take, and structured `details`. Raw backend or provider errors never reach the agent. The codes are listed in [Error codes](#error-codes).

**Annotations.** Each tool lists `readOnly`, `destructive`, `idempotent`, and `openWorld`. These describe the worst effect the tool can have. They are hints for the host's approval prompt. They do not grant permission. No tool has a confirmation argument, and every tool can run safely in an unattended scheduled session.

## Shared resource shapes

The HTTP API (if one is added) and the browser app use these same shapes.

```ts
type Workspace = {
  id: string;            // 12-char Base58
  name: string;
  role: "owner" | "admin" | "member";
  limits: Limits;
};

type Site = {
  id: string;            // 12-char Base58
  url: string;           // public address where the site is served
  title: string | null;        // from <title> in index.html
  description: string | null;  // from <meta name="description"> in index.html
  favicon_url: string | null;  // from <link rel="icon"> in index.html, resolved
  created_at: string;    // ISO 8601
  updated_at: string;
};

type FileEntry = {
  path: string;          // "assets/logo.png"
  name: string;          // "logo.png"
  content_type: string;
  size: number;          // bytes
  revision: string;
  updated_at: string;
};

type DataEntry = {
  collection: string;
  key: string;
  value: Record<string, unknown>; // JSON object
  revision: string;
  created_by: { kind: "visitor"; visitor_id: string } | { kind: "owner" };
  created_at: string;
  updated_at: string;
};
```

`title`, `description`, and `favicon_url` are always read from the current `index.html` and never stored separately, so no tool sets them. To change any of them, edit `index.html`.

## Saved data model

- A site's saved data is a set of named **collections** (for example `rsvps`, `checklist`, `settings`). Each collection holds **entries**. An entry has a `key` that is unique within its collection and a JSON object `value`.
- Visitors' browsers create, update, and delete entries one at a time through the runtime SDK. Agents use the tools below. Both go through the same backend mutations, so every open page updates live when an agent writes, just as it does when a visitor writes.
- **Who may write what** is set in the site's rules file, `fernpage.json` at the site root (**Assumed**: see below). The rules apply to visitors. An agent acts with the **site owner's** authority, so it can correct any entry, for example fix an RSVP that only its visitor and the owner may edit. An agent edit never changes `created_by`, so the original visitor can still edit their own entry afterward.
- **Assumed:** a collection must be declared in `fernpage.json` before it can hold entries. Visitor writes to an undeclared collection are refused, and so are agent writes (`collection_not_declared`). This keeps the data and the rules from drifting apart.
- **Assumed:** a key is either chosen by the writer (good for settings such as `rsvp_deadline` and for seeded checklist items) or generated by the server (the usual case for visitor entries). Keys never change. Renaming means creating a new entry and deleting the old one.
- **Visitors may be writing at the same moment.** Every overwrite of an entry checks `expected_revision`. On a conflict, the agent gets the current entry back, makes its change again on top of it, and retries. Creates never overwrite: if a key already exists, that item reports `already_exists`.
- **Assumed:** deleting an entry is permanent. Deleted entries do not go to Trash. Trash holds whole sites only.

### Rules file (`fernpage.json`)

**Assumed:** the rules live in a reserved file at the site root. They are written with the same file tools as everything else, so a rules change ships in the same edit as the code that depends on it. `fernpage.json` is never served to visitors. `write_file` and `edit_file` check it before it lands and refuse invalid rules with `invalid_rules`, giving the location of the problem. An example (the format has its own design, and this only shows the shape):

```json
{
  "data": {
    "collections": {
      "checklist": { "create": "owner", "update": "anyone", "delete": "owner" },
      "rsvps": { "create": "anyone", "update": "creator_or_owner", "delete": "creator_or_owner" },
      "settings": { "create": "owner", "update": "owner", "delete": "owner" }
    }
  }
}
```

## Catalog

The catalog has 18 tools.

| Tool | Area | readOnly | destructive | idempotent | openWorld |
| --- | --- | --- | --- | --- | --- |
| `get_workspace` | workspace | yes | no | yes | no |
| `list_sites` | sites | yes | no | yes | no |
| `get_site` | sites | yes | no | yes | no |
| `create_site` | sites | no | no | no | no |
| `delete_site` | sites | no | yes | yes | no |
| `read_file` | files | yes | no | yes | no |
| `write_file` | files | no | yes | no | no |
| `edit_file` | files | no | yes | no | no |
| `import_file` | files | no | yes | no | yes |
| `start_file_upload` | files | no | no | no | no |
| `finish_file_upload` | files | no | yes | yes | no |
| `delete_file` | files | no | yes | yes | no |
| `list_data_entries` | data | yes | no | yes | no |
| `get_data_entry` | data | yes | no | yes | no |
| `create_data_entries` | data | no | no | no | no |
| `update_data_entry` | data | no | yes | no | no |
| `delete_data_entries` | data | no | yes | yes | no |
| `clear_data_collection` | data | no | yes | yes | no |

Each description below begins with the sentence the tool advertises. That sentence is written for deferred tool search, so it leads with the verbs and nouns callers will search for.

---

### Workspace

#### `get_workspace`

> Get the connected Fernpage workspace: its id, name, your role, and its site, file, and saved-data limits.

```ts
{} // no arguments
```

Returns a `Workspace`. Agents call this first to learn where `create_site` will put a site and what the size limits are.

---

### Sites

#### `list_sites`

> List or find sites in the connected workspace by title, with their ids and public URLs.

```ts
{
  query?: string;  // case-insensitive match on title or URL; omit to list all
  cursor?: string; // from a previous page
  limit?: number;  // default 25, max 100
}
```

Returns `{ sites: Site[], next_cursor: string | null }`, newest-updated first. Sites in Trash are left out. When a name matches more than one site, every candidate is returned with its `id`, and the agent chooses.

#### `get_site`

> Get one site: its public URL, title, every file with size and revision, and a summary of its saved data.

```ts
{ site_id: string }
```

Returns:

```ts
{
  site: Site;
  files: FileEntry[];                   // whole manifest, sorted by path
  data: {
    collections: { name: string; entry_count: number; bytes: number }[];
    bytes_used: number;
    bytes_limit: number;
  };
}
```

Sites are small, so the full file list comes back in one call. **Assumed:** there is no separate `list_files` tool. Collections declared in `fernpage.json` are listed even when they have no entries yet.

#### `create_site`

> Create and publish a new site in the connected workspace from an index.html, and return its id and public URL.

```ts
{
  index_html: string; // full UTF-8 contents of index.html
}
```

Returns `{ site: Site, file: FileEntry }`. The site is live as soon as this returns. Its title, description, and favicon come from `index_html`. To add more files afterward, call `write_file` with the returned `site.id`.

Creating a site has its own tool. No file tool ever creates a site as a side effect. **Assumed:** the site's URL is assigned by Fernpage, and this tool takes no address or slug argument. Custom addresses, if they come later, will be set somewhere else.

#### `delete_site`

> Delete a site by id: it stops being served, and it moves to Trash with its files and saved data for 30 days.

```ts
{ site_id: string }
```

Returns `{ site_id: string, trashed_at: string, purge_at: string }`. A second call on a site already in Trash returns the same result (`already_trashed: true`). Restoring is only possible in the Fernpage browser app. No MCP tool restores a site, and the description tells the agent to send the user there. After 30 days a bounded, resumable deletion job permanently removes the files, saved data, and site record.

---

### Files

All file tools take `site_id` and refuse a site that is in Trash with `site_not_found`.

#### `read_file`

> Read one file from a site by path: text contents with its revision, or details and a URL for binary assets.

```ts
{ site_id: string; path: string }
```

Returns `{ file: FileEntry, content: string }` for text types (HTML, CSS, JS, JSON, SVG, plain text, and similar). Binary types return `{ file: FileEntry, url: string }` and no content. Text files over the inline read limit come back as `file_too_large`, which gives the size and the limit. `fernpage.json` can be read like any other file.

#### `write_file`

> Write a whole file to a site by path, creating it or replacing it, and publish it immediately.

```ts
{
  site_id: string;
  path: string;
  content: string;
  encoding?: "utf8" | "base64"; // default "utf8"; base64 only for small binaries (see limits)
  expected_revision: string | null; // null = the file must not exist yet
                                    // string = replace exactly this revision
}
```

Returns `{ file: FileEntry }` with the new revision. `expected_revision` is required, so the agent always says whether it means to create or to replace. A mismatch is refused (`file_exists` or `revision_conflict`, with the current revision) and the tool never falls back to the other action. The content type is inferred from the file extension.

Use this tool for new files and full rewrites. For small changes, use `edit_file`. For large binaries, use `import_file` or the upload pair, not base64.

#### `edit_file`

> Edit part of a text file in a site by replacing exact snippets, without resending the whole file.

```ts
{
  site_id: string;
  path: string;
  edits: {                // 1..50, applied in order
    old_text: string;     // must match exactly once in the current file
    new_text: string;
  }[];
  expected_revision?: string; // optional extra guard; the old_text match already acts as one
}
```

Returns `{ file: FileEntry }`. The edits succeed or fail together. If any `old_text` matches zero times or more than once, nothing is written, and the error names which edit failed and how many matches it found. The file must already exist (`file_not_found` points to `write_file`).

#### `import_file`

> Add or replace an asset in a site by having Fernpage fetch it from a public URL, such as an image or font.

```ts
{
  site_id: string;
  path: string;
  source_url: string; // https only
  expected_revision: string | null; // same meaning as write_file
}
```

Returns `{ file: FileEntry }` once the bytes have been saved. The server-side fetch is protected against SSRF (no private or link-local addresses, a limited number of redirects) and has size and time caps. Type and size are checked before the file is saved.

#### `start_file_upload`

> Start uploading a local file into a site: returns a signed URL to PUT the bytes to, then call finish_file_upload.

```ts
{
  site_id: string;
  path: string;
  size: number;          // bytes, checked against limits before a URL is issued
  content_type: string;
  expected_revision: string | null; // same meaning as write_file, checked again at finish
}
```

Returns `{ upload_id: string, upload_url: string, method: "PUT", headers: Record<string,string>, expires_at: string }`. This is for agents that have a shell and a local file, for example `curl -T`. Nothing is published until `finish_file_upload` succeeds.

#### `finish_file_upload`

> Finish an upload started with start_file_upload: checks the uploaded bytes and publishes the file.

```ts
{ upload_id: string }
```

Returns `{ file: FileEntry }`. The upload is only reported as done once the server has confirmed the stored object's size and type. If no bytes have arrived yet, it returns `upload_incomplete`. Calling it again after success returns the same file.

#### `delete_file`

> Delete one file from a site by path; the site stays published.

```ts
{ site_id: string; path: string }
```

Returns `{ path: string, deleted: true }`, or `{ path, deleted: false, reason: "not_found" }` when the file was already gone, so retries are safe. `index.html` cannot be deleted (`index_required`). The refusal says to replace it with `write_file`, or to remove the whole site with `delete_site`. **Assumed:** deleted files do not go to Trash.

---

### Saved data

All data tools take `site_id` and `collection`. A `collection` is a name declared in `fernpage.json`.

#### `list_data_entries`

> List saved data entries in a site's collection, such as RSVPs or checklist items, newest first, with values and revisions.

```ts
{
  site_id: string;
  collection: string;
  created_by?: "visitor" | "owner"; // filter
  created_after?: string;           // ISO 8601, e.g. to find test entries
  created_before?: string;
  cursor?: string;
  limit?: number;                   // default 50, max 200
}
```

Returns `{ entries: DataEntry[], next_cursor: string | null }`. A page also stops early at a total byte budget, which keeps large values from filling the agent's context. Paging is consistent while visitors write: entries created after the first page are not inserted into later pages.

#### `get_data_entry`

> Get one saved data entry by collection and key, with its current value and revision.

```ts
{ site_id: string; collection: string; key: string }
```

Returns `{ entry: DataEntry }`, or `entry_not_found`.

#### `create_data_entries`

> Create saved data entries in a site's collection, for example to seed a checklist or add settings; never overwrites.

```ts
{
  site_id: string;
  collection: string;
  entries: {                          // 1..100
    key?: string;                     // omit to have Fernpage generate one
    value: Record<string, unknown>;
  }[];
}
```

Returns one result per input, in input order:

```ts
{ results: (
  | { status: "created"; entry: DataEntry }
  | { status: "already_exists"; key: string; entry: DataEntry }   // untouched; use update_data_entry
  | { status: "failed"; index: number; key?: string; code: string; message: string }
)[] }
```

Each entry is created on its own. One failure does not undo the others. New entries record `created_by: { kind: "owner" }` and appear on every open page right away. A retry with explicit keys is safe, because entries created the first time come back as `already_exists`.

#### `update_data_entry`

> Update one saved data entry, for example to fix a misspelled RSVP name or change a setting, safely while visitors are writing.

```ts
{
  site_id: string;
  collection: string;
  key: string;
  expected_revision: string;            // from list_data_entries or get_data_entry
  patch: Record<string, unknown>;       // JSON Merge Patch (RFC 7396): fields to set; null removes a field
}
```

Returns `{ entry: DataEntry }` with the new revision. If a visitor changed the entry after the agent read it, the call returns `revision_conflict` with the current `entry`, so the agent can apply its patch again without another read. `created_by` and `created_at` are never changed. The resulting value must still pass the collection's shape checks in `fernpage.json`, if it has any.

Updates have only a single-entry form. Fixing data is occasional work, and making the agent handle each conflict one entry at a time is safer.

#### `delete_data_entries`

> Delete specific saved data entries from a site's collection by key, such as test RSVPs before launch.

```ts
{
  site_id: string;
  collection: string;
  entries: {                     // 1..100
    key: string;
    expected_revision?: string;  // optional guard: skip if a visitor changed it since
  }[];
}
```

Returns one result per input, in input order:

```ts
{ results: (
  | { status: "deleted"; key: string }
  | { status: "not_found"; key: string }
  | { status: "revision_conflict"; key: string; entry: DataEntry }
  | { status: "failed"; key: string; code: string; message: string }
)[] }
```

Only the listed keys are deleted. Leaving out `expected_revision` affects only how that one key is checked, never how many entries are removed.

#### `clear_data_collection`

> Delete every saved data entry in one collection of a site, for example to clear test data before launch; the collection stays declared.

```ts
{ site_id: string; collection: string }
```

Returns `{ collection: string, deleted_count: number, cleared_before: string }`. The tool removes entries that existed when the call started (`created_at` ≤ `cleared_before`). Entries visitors create while it runs are kept. It runs in bounded steps that can resume, and it returns only once those steps are done. Clearing a whole collection gets its own tool so that this scope is never the result of an omitted argument on `delete_data_entries`.

## Typical flows

- **New site:** `get_workspace` → `create_site(index_html)` → `write_file` for `styles.css`, `app.js`, and `fernpage.json` (each `expected_revision: null`) → `import_file` or the upload pair for images.
- **One small change:** `get_site` (find the path) → `read_file` → `edit_file`.
- **Change spread across files:** write new or renamed assets first, then the `index.html` that refers to them, so visitors never load a page pointing at a missing file. **Assumed:** there is no multi-file atomic publish for now.
- **Seed a checklist:** declare `checklist` in `fernpage.json` → `create_data_entries` with explicit keys.
- **Fix an RSVP name:** `list_data_entries(rsvps)` → `update_data_entry(key, expected_revision, { name: "…" })` → on `revision_conflict`, apply the patch again on top of the returned entry.
- **Change a setting:** `get_data_entry(settings, key)` → `update_data_entry`. If the setting does not exist yet, use `create_data_entries`.
- **Clear test entries before launch:** `clear_data_collection`, or `list_data_entries(created_before: launch time)` → `delete_data_entries`.
- **Remove a site:** `delete_site(site_id)`, then tell the user it can be restored from Trash in the browser app for 30 days.

## Error codes

| Code | Meaning and next step |
| --- | --- |
| `not_authorized` | The token's workspace or role cannot do this. Ask the user to re-authorize or to ask for access. |
| `site_not_found` | No live site with this id in the connected workspace (it may be in Trash). Use `list_sites`. |
| `file_not_found` | No file at this path. Use `get_site` for the list of files, or `write_file` to create it. |
| `file_exists` | `expected_revision: null`, but the file exists. The error gives its current revision. |
| `revision_conflict` | The file or entry changed since it was read. The error includes its current state. |
| `edit_no_match` / `edit_ambiguous` | An `old_text` matched 0 or more than 1 times. The error says which edit and how many matches. |
| `index_required` | `index.html` cannot be removed. Replace it, or use `delete_site`. |
| `invalid_path` | Path is empty, absolute, contains `..` or `//`, or is too long. |
| `invalid_rules` | `fernpage.json` failed validation. The error gives the location and the reason. |
| `collection_not_declared` | Declare the collection in `fernpage.json` first. |
| `entry_not_found` | No entry with this key in the collection. |
| `invalid_value` | The value is not a JSON object, or it breaks the collection's shape rules. |
| `file_too_large` / `entry_too_large` | The error gives the measured size and the limit. |
| `site_storage_full` / `data_storage_full` | The site has reached its file or saved-data limit. The error gives used and limit. Delete something or ask the user. |
| `unsupported_type` | The file type is not accepted. |
| `fetch_failed` | `import_file` could not fetch the URL, with the reason class (unreachable, too large, blocked address). |
| `upload_incomplete` / `upload_expired` | Bytes not received yet / call `start_file_upload` again. |
| `rate_limited` | Too many calls. The error says when to retry. |

## Limits

**Assumed** starting values. These are product constants in the domain package, and `get_workspace` reports the values in force. A separate internal anti-abuse ceiling applies on top of them.

| Limit | Value |
| --- | --- |
| Inline text write or read (`write_file` utf8, `read_file`) | 1 MB per file |
| Inline base64 write | 256 KB decoded |
| Single file (import or upload) | 25 MB |
| Files per site | 1,000 |
| Total file bytes per site | 100 MB |
| Saved data per site | 5 MB |
| One data entry value | 64 KB |
| Items per batch call | 100 |

## Assumptions to confirm

1. **Rules live in `fernpage.json` at the site root.** It is edited with the file tools, checked before it lands, and never served. The brief says rules are declared "in its settings", so the alternative is a dedicated settings record with its own `get_data_rules` and `set_data_rules` tools.
2. **Agents act with the site owner's authority over saved data.** They can edit any entry, and the rules govern visitors only. Any workspace member who can edit a site gets that authority through the agent.
3. **One workspace per authorization**, chosen at consent. Tools take no `workspace_id`.
4. **Every write is live immediately.** There is no draft, preview, or publish step, and no atomic publish across several files.
5. **Collections must be declared** before they can hold entries.
6. **Entry keys** are either chosen by the writer or generated by the server, and they never change. Values are JSON objects.
7. **Deleted files and data entries are permanent.** Only whole sites go to Trash.
8. **Site URLs are assigned by Fernpage.** `create_site` takes no address argument.
9. **The data model mirrors the runtime SDK** (collections, keys, revisions, `created_by`). The SDK's design has not been written down yet, so the two must be settled together.
10. **The limit values above** are placeholders.

Deliberately left out, to add when needed: `move_file`, an atomic multi-file `write_files`, a data export tool, restoring a site (browser app only, by decision), and site title or favicon setters (these come from `index.html`, by decision).

````

> Result: File created successfully at: C:\tmp\wro-eval3\builds\3-file-catalog-with-saved-data-old-opus\work\docs\mcp-tools.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the tool catalog to `docs/mcp-tools.md`. It defines 18 tools in four groups: workspace, sites, files and saved data. Each tool has its argument schema, what it returns, its approval hints (such as read-only or destructive), and the shared data shapes. The doc also covers error codes, starting limits, typical agent flows, and a list of what I assumed. I haven't committed it.

**The shape:**
- **Sites:** `create_site` requires the `index.html` contents and publishes immediately. `delete_site` moves the site and its saved data to Trash for 30 days, and there is no restore tool. Title, description and favicon are always read from `index.html`, so no tool sets them.
- **Files:** agents can write a whole file, edit part of one by replacing exact snippets, import from a URL, upload a local file, or delete one. `write_file` makes the agent say whether it is creating a new file or replacing a specific version, so it never silently overwrites. `index.html` can't be deleted on its own.
- **Saved data:** data lives in named collections (for example `rsvps`, `checklist`, `settings`), and each entry has a key and a version. Updates must name the version the agent last read, so a visitor writing at the same moment isn't overwritten. On a clash, the agent gets the current entry back and retries. Creating entries never overwrites an existing one. Clearing a whole collection is its own tool, so it can't happen by accident through the delete tool. Agent writes go through the same backend as visitors' writes, so open pages update live, and an agent edit never changes who created an entry.

**Calls I made that most need your review** (all are listed at the end of the doc):
1. **Where the write rules live:** I put them in a file at the site root, `fernpage.json`. It is edited like any other file, checked before it saves, and never served to visitors. The brief says rules are declared "in its settings", which could instead mean a separate settings record with its own tools. This is the biggest open call.
2. **Agent permissions:** agents act with the site owner's authority over saved data. That means they can fix any entry, including RSVPs that only the visitor and the owner may edit.
3. **One workspace per connection:** the user picks the workspace when they authorize the agent, so tools don't take a workspace ID. Working in another workspace means authorizing again.
4. **No publish step:** every write is live immediately. There is also no way to publish changes to several files at once, so the doc tells agents to write new assets before the `index.html` that uses them.
5. **Collections must be declared** in the rules before they can hold entries, and deleted files and entries are permanent. Only whole sites go to Trash.
6. **Placeholders:** the limits (for example 5 MB of saved data per site and 64 KB per entry) and the domain in the server address are stand-ins. The saved-data model also has to match the visitor-side SDK, which isn't designed yet.

I left out moving files, multi-file publish, data export and setters for title and favicon, and noted each so it can be added later.

**Session ended:** success, 9 turns, 188458 ms
