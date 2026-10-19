**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "git ls-files && cat docs/brief.md", "description": "List files and read the brief"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5643 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references && cat model-context-protocol.md agent-tool-design.md", "description": "Read MCP and tool design references"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 11720 more characters]

**Tool call `Bash`:** `{"command": "cat uploads.md workspace-tenancy.md ids.md data-deletion.md bulk-actions.md", "description": "Read upload, tenancy, ID, deletion, bulk references"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 15930 more characters]

**Tool call `Bash`:** `{"command": "cat domains.md naming.md user-facing-errors.md live-data.md object-storage.md abuse-resistance.md quota.md data-model.md source-of-truth.md path-display.md", "description": "Read domains, naming, errors, data, storage references"}`

> Result: <persisted-output> Output too large (29.7KB). Full output saved to: <run>\builds\4-file-catalog-with-saved-data-new-opus2\cfg\projects\C--tmp-wro-eval4-builds-4-file-catalog-with-saved-data-new-opus2-work\c6cbd42f-17e2-43c2-84d0-dd9fafc73f66\tool-results\b1ym8qjkg.txt  Preview (first 2KB): # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on th [... 1757 more characters]

**Tool call `Read`:** `{"file_path": "<run>\\builds\\4-file-catalog-with-saved-data-new-opus2\\cfg\\projects\\C--tmp-wro-eval4-builds-4-file-catalog-with-saved-data-new-opus2-work\\c6cbd42f-17e2-43c2-84d0-dd9fafc73f66\\tool-results\\b1ym8qjkg.txt"}`

> Result: 1	# Domains 2	 3	Lay out hosts around one canonical origin per surface, with the primary surface on the apex. 4	 5	- Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain.  [... 30793 more characters]

**Tool call `Bash`:** `{"command": "cat http-apis.md agent-skills.md failure-and-retries.md", "description": "Read HTTP API, agent skills, retry references"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 4791 more characters]

**Tool call `Write`:** `<run>\builds\4-file-catalog-with-saved-data-new-opus2\work\docs\mcp-tools.md`

````text
# Fernpage MCP tool catalog

The tools that agents use to build and maintain Fernpage sites. `docs/brief.md` takes precedence over this document. If they disagree, fix this document.

Status: proposed design, not implemented yet. Anything the brief does not settle is marked **Assumed** and listed again in [Assumptions and open questions](#assumptions-and-open-questions).

## Shape of the catalog

Agents already know how to work with files: list, read, write, edit, search, and delete. Fernpage sites are files, and saved data is small enough to handle as files too. So the catalog is a file tool set, plus a few tools for workspaces and sites:

| Tool | What it does | Read-only | Destructive | Idempotent |
| --- | --- | --- | --- | --- |
| `list_workspaces` | List the workspaces the user can work in | yes | no | yes |
| `list_sites` | List or find sites in a workspace | yes | no | yes |
| `create_site` | Create a new, empty site in a workspace | no | no | no |
| `delete_site` | Move a whole site to Trash | no | yes | yes |
| `list_files` | List a site's files, data files included | yes | no | yes |
| `read_file` | Read one file | yes | no | yes |
| `search_files` | Search a site's files by text or regular expression | yes | no | yes |
| `write_files` | Create or replace whole files | no | yes | yes |
| `edit_file` | Make exact text replacements in one file | no | yes | no |
| `delete_files` | Delete specific files from a site | no | yes | yes |

That's ten tools. There are no record-level tools such as `update_record`. Saved data uses `read_file`, `edit_file`, `write_files`, and `search_files`, as described in [Saved data as files](#saved-data-as-files).

Why these tools are split where they are:

- `create_site` and `delete_site` are their own tools. A file write never creates a site, and a file delete never removes one. The tool name decides whether you are editing or creating, and whether you are deleting one file or a whole site. No argument decides either.
- `delete_files` is separate from `write_files`, so a delete is always explicit. A file that's missing from a write is never deleted.
- `edit_file` is separate from `write_files`. A small change doesn't require sending the whole file again, and the edit lands against the current content.
- There are no confirmation arguments. The host approves tool calls, and the server checks permission on every call. Every tool is safe to run unattended.

## Server

- Endpoint: `https://mcp.<fernpage-domain>/mcp`, a separate protocol app in `apps/mcp` built with Hono and the official MCP SDK. **Assumed**: the domain isn't chosen yet.
- Transport: stateless, with buffered JSON responses. Nothing here needs streaming.
- Authorization: MCP OAuth. Every token must name this server in its audience. **Assumed**: grants cover the whole account (every workspace the user belongs to, now or later), because the brief says "one of the user's workspaces" and people will want one connection for all of them. Every call resolves its target workspace or site and checks it on the server against a live membership. Revoking a membership takes effect on the next call.
- Catalog: every caller gets the same static list of tools. A call the caller can't make reaches the gate and comes back as a clear error. Tools never disappear from the list.

## Shared conventions

### Identifiers

- `workspaceId` and `siteId` are stable 12-character Base58 IDs, the same `id` the browser app uses in its URLs.
- Reads can find things by name: `list_sites` accepts a `query` that matches a site's title or address. If the query is ambiguous, every candidate comes back with its `siteId`.
- Every tool that changes something takes a `siteId` or `workspaceId`, never a name.

### Paths

- A path is relative to the site root, with forward slashes, no leading slash, and case-sensitive: `index.html`, `img/hero.jpg`, `.data/rsvps.json`.
- Every result returns paths in the same form, so a caller can pass them straight back. A listing entry carries `name` (the last segment) and `path` (the full path).
- Paths are refused if they contain empty segments, `.` or `..`, backslashes, or control characters, or if they name a directory.
- Two reserved names (**Assumed** names, see below):
  - `fernpage.json` at the root holds the site's settings: which saved-data collections exist and who may read or write them. It is never served to visitors.
  - `.data/` holds one data file per collection, `.data/<collection>.json`. These files aren't stored as files. They are live views of the saved data in the database, and visitors reach them only through the runtime SDK, never as static URLs.

### The site resource

Every tool that returns a site uses the same shape:

```json
{
  "id": "7Hq2mXpL9rTa",
  "workspaceId": "Bc4kN8vQw2Zs",
  "address": "lena-and-sam",
  "url": "https://lena-and-sam.<content-domain>",
  "title": "Lena & Sam — RSVP",
  "description": "Join us on June 14",
  "faviconPath": "favicon.png",
  "status": "live",
  "updatedAt": "2026-10-19T14:02:11Z"
}
```

- `title`, `description`, and `faviconPath` are derived from `index.html` on every read, as the brief decides. They aren't stored, and no tool sets them. To change them, edit `index.html`.
- `status` is `"live"` when `index.html` exists, and `"empty"` when it doesn't. One `index.html` is enough to publish.
- `url` is served on Fernpage's separate content domain, because sites run code their users wrote.

### Results and errors

- Writing to several files returns one result per file, in input order. Successes and failures appear side by side, and one failure doesn't undo the others.
- An expected refusal comes back as a typed `code` with a short, product-worded `message` that names what the server measured and what to do next. Raw database, storage, or provider errors never reach the caller.
- Shared codes: `not_found`, `forbidden`, `invalid_path`, `reserved_path`, `too_large`, `quota_exceeded`, `conflict`, `rule_violation`, `invalid_content`, `unsupported_source`, `site_in_trash`.

### Concurrency without version tokens

Visitors can be writing saved data while an agent edits it, and a person might be editing the same site in the browser app. The server guards against overwriting their changes, and no call has to carry a revision token:

- When `read_file` returns a whole file (`complete: true`), the server remembers which version it served to this caller. A whole-file write from `write_files` that the server stored exactly as sent also counts as a version the caller knows. A "caller" is one OAuth client acting for one user.
- `write_files` compares each file against the version this caller last knew:
  - **Site files**: if someone else changed the file since then, or the caller never saw the existing file at all, the write is refused with `conflict`. The message says to read the file again.
  - **Data files**: see [Concurrent writes to saved data](#concurrent-writes-to-saved-data). The server merges changes record by record, and refuses only real collisions.
- `edit_file` needs no prior read. Its `oldText` has to match the current content exactly, which is its own check, and the edit is applied in one transaction against the current content.
- A partial read (`complete: false`) never counts as a known version.

## Saved data as files

Each saved-data collection that `fernpage.json` declares appears as one JSON file at `.data/<collection>.json`. The file is a JSON object. Each top-level key is one entry's key, and its value is the entry's value:

```json
{
  "k3Fq9": { "name": "Jon Smiht", "guests": 2, "attending": true },
  "p8Lw2": { "name": "Ana Ruiz", "guests": 1, "attending": false }
}
```

- The server renders the file the same way every time: entries in creation order, 2-space indentation. So the text that `edit_file` matches is stable.
- A site-settings collection (for example `.data/settings.json`) has the same shape. Each top-level key is one setting.
- Entry keys match `[A-Za-z0-9_-]{1,64}`. Visitors' entries get keys the server generates. An agent seeding data can pick readable keys such as `"buy-flowers"`.
- The file shows only values. Who created an entry and when stay on the server, so the creator-based rules keep working and an agent can't forge them. **Assumed**; see the open questions.

How a write turns into entry changes: the server parses the new file, compares it with the version it is merging against, and handles each changed entry as one SDK-style operation:

- A key that's new in the file creates an entry.
- A key whose value changed updates that entry.
- A key that's missing from the file deletes that entry.
- A key whose value didn't change is left alone.

Each change passes the same rules, validation, and quota that a single SDK write would. The agent acts as the site owner, so it can edit or delete any entry, even under a "creator only" rule. Writes still have to fit the collection's declared limits.

Each data file is written all-or-nothing. If any entry change is refused, nothing in that file changes. The result lists the keys that were refused and why. Every subscribed page then updates live, exactly as it would after a visitor's write.

### Concurrent writes to saved data

A `write_files` call that includes a data file is merged against the last complete version this caller read:

- Entries the caller didn't change keep whatever other writers did to them since that read. That includes entries visitors added or deleted. A visitor's RSVP that arrived after the agent's read survives the agent's write.
- If the caller and someone else both changed the same entry since that read, the file is refused with `conflict`, and the message lists the colliding keys.
- If the caller has no complete read of the file and the collection already holds entries written by others, the file is refused with `conflict`. A first write to an empty collection doesn't need a read.

`edit_file` on a data file doesn't need a merge. The edit is applied to the current text inside the transaction, then the result is parsed and compared with that same text, so only the entries the edit touched change.

### Common saved-data tasks

| Task | How |
| --- | --- |
| Seed a checklist | Declare the collection in `fernpage.json`, then `write_files` `.data/checklist.json` with the starting entries |
| Fix a misspelled RSVP name | `search_files` for `"Smiht"`, then `edit_file` `.data/rsvps.json` with `oldText: "Jon Smiht"` |
| Clear test entries before launch | `read_file` `.data/rsvps.json`, then `write_files` it without the test keys. Only those keys are deleted, and real RSVPs that arrived meanwhile are kept |
| Clear a collection completely | `write_files` the data file with `{}` |
| Change a setting | `edit_file` `.data/settings.json`, or `write_files` it after a read |
| Change who may write what | `edit_file` `fernpage.json` |

`delete_files` refuses data files, because a data file is a whole collection. Delete entries with a write or an edit instead. To remove a collection, empty it first, then take it out of `fernpage.json`. The server refuses to drop a collection that still has entries.

### `fernpage.json` (rules)

**Assumed** shape. The real rules language will be specified elsewhere, and the tools only need it to exist and be validated on write:

```json
{
  "data": {
    "checklist": { "read": "anyone", "create": "owner", "update": "anyone", "delete": "owner" },
    "rsvps":     { "read": "creator", "create": "anyone", "update": "creator", "delete": "creator" },
    "settings":  { "read": "anyone", "write": "owner" }
  }
}
```

The allowed values are `anyone`, `creator` (the visitor who created the entry), and `owner` (members of the site's workspace). The site owner can always edit anything. A write to `fernpage.json` that is invalid JSON, uses an unknown value, or drops a collection that still has entries is refused with `invalid_content`, and the message points to the problem.

## Tools

The schemas below are JSON Schema for `inputSchema`. Each description's first sentence is written to be the text a host indexes in tool search.

### `list_workspaces`

> List the workspaces you can create and edit sites in, with each workspace's ID and your role.

```json
{ "type": "object", "properties": {}, "additionalProperties": false }
```

Returns `{ workspaces: [{ id, name, role }] }`. `role` is `"admin"` or `"member"`.

### `list_sites`

> List or find sites in a workspace by title or address, returning each site's ID, URL, and status.

```json
{
  "type": "object",
  "properties": {
    "workspaceId": { "type": "string", "description": "Workspace to list. Omit to list sites in every workspace you belong to." },
    "query": { "type": "string", "description": "Case-insensitive match on site title or address." },
    "cursor": { "type": "string" }
  },
  "additionalProperties": false
}
```

Returns `{ sites: [Site], nextCursor? }`, with up to 50 sites per page. Sites in Trash aren't listed. Leaving out `workspaceId` only widens a read.

### `create_site`

> Create a new, empty site in a workspace and return its ID and URL. Then add files with write_files.

```json
{
  "type": "object",
  "properties": {
    "workspaceId": { "type": "string", "description": "Workspace that will own the site. Get it from list_workspaces." },
    "address": {
      "type": "string",
      "pattern": "^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$",
      "description": "Subdomain label for the site's URL, such as \"lena-and-sam\". If omitted, Fernpage picks an available one."
    }
  },
  "required": ["workspaceId"],
  "additionalProperties": false
}
```

- Returns `{ site: Site }`, with `status: "empty"` until `index.html` is written.
- Retrying after a timeout can create a second site. Before retrying, check with `list_sites`.
- Refusals: `address_taken` (the message suggests available alternatives), `invalid_address`, `quota_exceeded`, `forbidden`.
- **Assumed**: the agent can pick the address only at creation. Changing it later happens in the browser app.

### `delete_site`

> Delete a site by moving it to Trash for 30 days. It stops serving, and only the browser app can restore it.

```json
{
  "type": "object",
  "properties": { "siteId": { "type": "string" } },
  "required": ["siteId"],
  "additionalProperties": false
}
```

- Returns `{ result: "moved_to_trash" | "already_in_trash", siteId, purgeAt, restoreUrl }`. `restoreUrl` is the site's Trash page in the browser app.
- There is no restore tool, as the brief decides.
- **Assumed**: a site in Trash stops serving, keeps its files and saved data until `purgeAt`, and refuses every write (`site_in_trash`).

### `list_files`

> List a site's files and saved-data files with their paths, sizes, and kinds.

```json
{
  "type": "object",
  "properties": {
    "siteId": { "type": "string" },
    "directory": { "type": "string", "description": "Only list files under this directory. Omit for the whole site." }
  },
  "required": ["siteId"],
  "additionalProperties": false
}
```

Returns:

```json
{
  "files": [{ "name": "rsvps.json", "path": ".data/rsvps.json", "kind": "data", "size": 4120, "entries": 37, "updatedAt": "…" }],
  "usage": { "filesBytes": 812331, "filesLimit": 52428800, "dataBytes": 4120, "dataLimit": 5242880 }
}
```

- `kind` is `"file"`, `"rules"` (for `fernpage.json`), or `"data"`. Data files also show their entry count.
- The list is flat and recursive, because sites are small.

### `read_file`

> Read one site file or saved-data file as text, or an image as an image.

```json
{
  "type": "object",
  "properties": {
    "siteId": { "type": "string" },
    "path": { "type": "string" },
    "offset": { "type": "integer", "minimum": 1, "description": "First line to return. Omit to start at line 1." },
    "limit": { "type": "integer", "minimum": 1, "description": "Maximum lines to return." }
  },
  "required": ["siteId", "path"],
  "additionalProperties": false
}
```

- Text returns `{ path, content, complete, totalLines, size, updatedAt }`.
- Output is capped at about 2,000 lines or 100 KB. Past the cap, `complete` is `false` and the message names the next `offset`.
- Only a `complete: true` read lets a later `write_files` overwrite the file. A partial read doesn't. `edit_file` works either way.
- Images under 1 MB come back as MCP image content. Other binary files return metadata and their public URL, not bytes.
- This tool reads one file per call. There is no batch read, because batched reads flood the model's context.

### `search_files`

> Search a site's files and saved data by plain text or regular expression, returning matching paths and lines.

```json
{
  "type": "object",
  "properties": {
    "siteId": { "type": "string" },
    "pattern": { "type": "string" },
    "regex": { "type": "boolean", "description": "Treat pattern as a regular expression. Default false: plain text." },
    "caseSensitive": { "type": "boolean", "description": "Default false." },
    "pathPrefix": { "type": "string", "description": "Only search under this path, such as \".data/\"." }
  },
  "required": ["siteId", "pattern"],
  "additionalProperties": false
}
```

- Returns `{ matches: [{ path, line, column, text }], truncated }`, with at most 200 matches.
- Data files are searched in the same text form that `read_file` returns, so a match's line can feed straight into `edit_file`.

### `write_files`

> Create or replace whole files on a site, including saved-data files. Text goes inline, and other files go as an HTTPS URL to fetch.

```json
{
  "type": "object",
  "properties": {
    "siteId": { "type": "string" },
    "files": {
      "type": "array",
      "minItems": 1,
      "maxItems": 20,
      "items": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "content": { "type": "string", "description": "UTF-8 text, at most 256 KB. Use for HTML, CSS, JS, SVG, JSON, and data files." },
          "sourceUrl": { "type": "string", "format": "uri", "description": "Public HTTPS URL Fernpage fetches the bytes from. Use for images, fonts, and other binary files. Never base64 inline." }
        },
        "required": ["path"],
        "oneOf": [{ "required": ["content"] }, { "required": ["sourceUrl"] }],
        "additionalProperties": false
      }
    }
  },
  "required": ["siteId", "files"],
  "additionalProperties": false
}
```

- Each file lands, or is refused, on its own. The result has one entry per input, in order:
  - `{ path, result: "created" | "replaced" | "unchanged", size }` for site files.
  - `{ path, result: "updated" | "unchanged", entries: { created, updated, deleted } }` for data files.
  - `{ path, result: "failed", code, message, keys? }` for refusals.
- Changes go live as soon as they land. **Assumed**: there's no draft or publish step.
- Writing a file at a new path creates it, and missing directories are implied.
- Retrying is safe. Re-sending the same content returns `unchanged`.
- Bytes have three routes:
  - Inline `content` for text.
  - `sourceUrl` for anything else. The server fetches it with a byte cap, a timeout, and limited redirects, refuses private and loopback addresses, and checks the bytes it actually received.
  - An attachment reference, where the host documents one as fetchable. The protocol adapter turns it into a URL fetch.
- A local file path or sandbox path moves no bytes. It is refused with `unsupported_source`, and the message names the routes that work. The tool never reports a file as written when it didn't land.
- Size, file count, type, and quota are checked before the bytes are fetched or stored. Usage is charged from the stored size after the file lands.
- Writing to `index.html` changes the derived title, description, and favicon. In that case the result includes the updated `site` resource.
- Refusals: `conflict` (see [Concurrency](#concurrency-without-version-tokens)), `rule_violation` and `invalid_content` for data and rules files, `too_large`, `quota_exceeded`, `invalid_path`, `reserved_path` (such as a `.data/` file for an undeclared collection), `unsupported_source`, `site_in_trash`.

### `edit_file`

> Edit one site file or saved-data file by replacing exact text, without resending the whole file.

```json
{
  "type": "object",
  "properties": {
    "siteId": { "type": "string" },
    "path": { "type": "string" },
    "edits": {
      "type": "array",
      "minItems": 1,
      "maxItems": 50,
      "items": {
        "type": "object",
        "properties": {
          "oldText": { "type": "string", "minLength": 1, "description": "Exact text to find. Must match once unless replaceAll is true." },
          "newText": { "type": "string" },
          "replaceAll": { "type": "boolean", "description": "Replace every occurrence. Default false." }
        },
        "required": ["oldText", "newText"],
        "additionalProperties": false
      }
    }
  },
  "required": ["siteId", "path", "edits"],
  "additionalProperties": false
}
```

- The edits are applied in order against the current content, in one transaction. Either all of them land or none do.
- Returns `{ path, result: "edited", size }`. For data files, it also returns `entries: { created, updated, deleted }`, and for `index.html` the updated `site`.
- Refusals:
  - `no_match` and `multiple_matches`. These say which edit failed and how many matches it found, without echoing the whole text.
  - `invalid_content`, when a data or rules file wouldn't parse afterwards. This gives the line and column.
  - `rule_violation`.
  - `not_found`, for a missing file. Create files with `write_files`.
- Not idempotent. A retry after a timeout that actually landed fails with `no_match`. Before retrying, check with `read_file` or `search_files`.
- Works only on text files.

### `delete_files`

> Delete specific files from a site by exact path. Directories and saved-data collections can't be deleted with this tool.

```json
{
  "type": "object",
  "properties": {
    "siteId": { "type": "string" },
    "paths": { "type": "array", "minItems": 1, "maxItems": 100, "items": { "type": "string" } }
  },
  "required": ["siteId", "paths"],
  "additionalProperties": false
}
```

- Returns one result per path, in order: `{ path, result: "deleted" | "not_found" }` or `{ path, result: "failed", code, message }`.
- Refuses with `invalid_path` any path that names a directory or uses a wildcard, and with `reserved_path` any `.data/` file or `fernpage.json`.
- Deleting `index.html` is allowed. The site goes to `status: "empty"` and stops serving a home page, and the result says so.
- **Assumed**: deleting files is permanent. Trash covers whole sites only.

## Limits

All numbers are **Assumed** defaults. They will live as constants in the domain package and should be revisited once real usage is seen.

| Limit | Value |
| --- | --- |
| Inline `content` per file | 256 KB |
| Fetched file (`sourceUrl`) | 25 MB |
| Files per `write_files` call | 20 |
| Paths per `delete_files` call | 100 |
| Edits per `edit_file` call | 50 |
| `read_file` output per call | 2,000 lines or 100 KB |
| `search_files` matches | 200 |
| Saved data per site | 5 MB, the upper end of the brief's "a few megabytes" |
| One saved-data entry | 64 KB |

Rate limits are applied at the edge, separately from quota.

## Assumptions and open questions

These are the calls I made where `docs/brief.md` is silent. Each one should be confirmed or overruled by adding a decision to the brief.

1. **Saved data is reached through file tools.** Each collection is a `.data/<collection>.json` file whose top-level keys are its entries. There are no separate record tools.
2. **Reserved names `fernpage.json` and `.data/`.** "Rules a site declares in its settings" is read as a rules file, `fernpage.json`. "Site settings" in the saved-data list is read as ordinary saved data, by convention a `settings` collection. If the brief means a single settings concept, the two should merge.
3. **The rules language** (`anyone` / `creator` / `owner`, plus read rules) is only sketched here. Read rules are included because RSVPs hold personal details, and the brief doesn't say who may read saved data.
4. **Entry metadata is hidden.** Data files show values only. Creator and timestamps stay on the server. If agents need `createdAt` to spot test entries, a read-only metadata view can be added later without changing writes.
5. **Agents act as the site owner** for rule purposes, and any workspace member can edit the workspace's sites. Finer roles would come later, at the product's own permission gate.
6. **Grants cover the whole account**, not one workspace.
7. **No draft or publish step.** Writes go live immediately, consistent with "one `index.html` is enough to publish". If half-finished sites going live is a problem, staging writes is the change to make, and it would add a `publish_site` tool.
8. **Overwrite protection is tracked per caller on the server, with no version tokens.** A "caller" is one OAuth client acting for one user. Two agent sessions on the same connection share what they've read.
9. **The site address** is chosen optionally at creation and changed only in the browser app. There are no custom domains in this catalog.
10. **Trash** stops serving the site, keeps its data, and refuses writes. Deleting individual files is permanent.
11. **Domains are placeholders.** Sites are served on a separate content domain, one subdomain per site, apart from the product domain.
12. **Left out on purpose:** renaming or moving files, restoring from Trash (browser app only, as the brief decides), batch reads, and record-level tools. A workflow skill that teaches agents these patterns would be a natural follow-up, built on this contract.

````

> Result: File created successfully at: <run>\builds\4-file-catalog-with-saved-data-new-opus2\work\docs\mcp-tools.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the catalog to `docs/mcp-tools.md`. It's a design only: nothing is implemented, and I haven't committed it.

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

**Session ended:** success, 10 turns, 192665 ms
