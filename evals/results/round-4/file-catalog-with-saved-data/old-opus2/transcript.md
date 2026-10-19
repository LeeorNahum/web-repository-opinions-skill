**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-old-opus2/work\" && git ls-files && cat docs/brief.md"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5643 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md agent-tool-design.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 8261 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat ids.md bulk-actions.md data-deletion.md workspace-tenancy.md live-data.md"}`

> Result: # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.  ## Entity IDs  For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.  - Length: a fixed 12 characters. - Alphabet: Base58, the case-sensi [... 13034 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat uploads.md object-storage.md abuse-resistance.md quota.md user-facing-errors.md source-of-truth.md data-model.md naming.md agent-skills.md http-apis.md modularity.md"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 26630 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-old-opus2/work/.claude/skills/web-repository-opinions/references\" && cat domains.md routing.md failure-and-retries.md path-display.md | head -250"}`

> Result: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 13767 more characters]

**Tool call `Write`:** `<run>\builds\4-file-catalog-with-saved-data-old-opus2\work\docs\mcp-tools.md`

````text
# Fernpage MCP tool catalog

This is the tool surface that AI agents use to build and maintain Fernpage sites. Product decisions come from `docs/brief.md`, and that file wins if the two disagree. Anything this document decides that the brief does not decide is listed under [Assumptions](#assumptions-to-confirm).

## Endpoint and connection

- Remote MCP endpoint: `https://mcp.fernpage.com/mcp`, deployed as its own protocol app. Tool calls get buffered JSON responses, and the transport is stateless.
- The connection uses OAuth against one canonical resource. **During consent the user picks one of their workspaces**, and the token acts in that workspace only. To work in a different workspace, the agent authorizes the same resource again and picks the other workspace. No tool takes a `workspace_id`, so an agent can't write into the wrong workspace because it filled in an argument wrongly.
- Every caller sees the same catalog. Authorization is checked on every call at the product boundary, the same one the browser app goes through. A call the caller can't make returns a typed error with plain wording. Tools are never hidden.
- These tools are thin adapters over the same product capabilities the browser app uses. File and saved-data rules (paths, limits, access rules, versions) are enforced in those capabilities, not here.

## Conventions

- **Names** use the imperative form verb_noun. A tool that takes a list has a plural name (`write_files`). A tool that takes one item has a singular name (`read_file`).
- **IDs.** Sites have a 12-character Base58 `id`. Destructive tools take a site `id` only and never a title or address. `list_sites` is the read tool that turns a title or address into an id.
- **Paths** are product paths relative to the site root, for example `index.html` or `img/hero.jpg`. They use `/` as the separator. They have no leading slash, no `.` or `..` segments, no empty segments and no backslashes. They are case-sensitive and stored exactly as written. Every `path` a tool returns can be passed straight back to another tool.
- **Versions.** Every file and every saved-data entry has an opaque `version` string. Writes that could overwrite someone else's change take an `expected_version`. When it doesn't match, the write is refused and the result includes the current state.
- **Changes are live.** A successful file write is what visitors get on their next request. No separate publish step exists. Saved-data writes go through the same reactive backend as visitors' writes, so every open page updates live.
- **Batches.** Saved-data batches can partly succeed, because each entry is independent. They return one result per item in input order, and failures are reported inline. File batches are atomic, because together they make one site revision. Either every item lands or nothing does, and the result still reports each item.
- **Reads return one item.** No tool reads several files' contents in one call.
- **Errors** are typed codes with short copy that names what was measured and what to do next. Raw backend or provider messages are never returned. The codes are listed in [Error codes](#error-codes).
- **Starting limits.** These are product constants and can be tuned:

  | Limit | Value |
  | --- | --- |
  | One file | 10 MB |
  | All files in a site | 50 MB |
  | Inline `content` (UTF-8 text) per file | 512 KB |
  | Inline `content_base64` per file (decoded) | 64 KB |
  | Inline content per `write_files` call | 2 MB |
  | Files per `write_files` / `delete_files` call | 50 |
  | Saved data per site | 5 MB |
  | One entry `value` (serialized JSON) | 64 KB |
  | Entries per saved-data batch call | 100 |
  | `list_*` page size | default 50, max 200 |

## Shared schemas

The shapes below are written in TypeScript notation. Each tool's JSON Schema is generated from the same types.

```ts
type SiteId = string;           // 12-char Base58
type Version = string;          // opaque; compare for equality only

type Site = {
  id: SiteId;
  address: string;              // DNS label, e.g. "smith-wedding"
  url: string;                  // "https://smith-wedding.fernpage.site/"
  app_url: string;              // the site in the browser app
  title: string | null;         // from index.html <title>
  description: string | null;   // from index.html <meta name="description">
  favicon_url: string | null;   // from index.html <link rel="icon">, else null
  revision: number;             // increments on every file change
  created_at: string;           // ISO 8601
  updated_at: string;
};

type FileInfo = {
  path: string;                 // full product path, e.g. "img/hero.jpg"
  name: string;                 // last segment only, e.g. "hero.jpg"
  content_type: string;
  size: number;                 // bytes
  version: Version;
};

type Collection = {
  name: string;
  rules: CollectionRules;
  entry_count: number;
  size: number;                 // bytes used by this collection's entries
};

type Principal = "anyone" | "creator" | "owner";
type CollectionRules = { read: Principal; create: "anyone" | "owner"; update: Principal; delete: Principal };

type Entry = {
  collection: string;
  key: string;                  // 1–128 chars, [A-Za-z0-9_-]
  value: unknown;               // any JSON value
  version: Version;
  created_by: { kind: "visitor"; visitor_id: string } | { kind: "owner" };
  created_at: string;
  updated_at: string;
};
```

`title`, `description` and `favicon_url` are always read from the current `index.html` (as the brief decides) and never stored separately. Any write that touches `index.html` returns the updated `Site`, so the agent sees the new title right away.

### Saved data and access rules

Each site's saved data is organized into **collections**, and a collection holds **entries**. Each entry has a `key` and a JSON `value`. For example: collection `rsvps` has one entry per guest, `checklist` has one entry per item, and `settings` has one entry per setting. The runtime SDK in visitors' browsers reads and writes one entry at a time. These tools use the same model.

A site declares its collections and who may do what in a reserved root file, **`fernpage.json`**. The agent writes it with the normal file tools. It is never served to visitors.

```json
{
  "data": {
    "collections": {
      "rsvps":     { "read": "creator", "create": "anyone", "update": "creator", "delete": "creator" },
      "checklist": { "read": "anyone",  "create": "owner",  "update": "anyone",  "delete": "owner" },
      "settings":  { "read": "anyone",  "create": "owner",  "update": "owner",   "delete": "owner" }
    }
  }
}
```

- `owner` means the site's owner, meaning any member of the site's workspace. The owner may always do everything. `creator` means the visitor who created the entry, plus the owner. `anyone` means any visitor.
- Rules default to deny. Visitors can't touch a collection that isn't declared, and agent writes to it are refused with `collection_not_declared`.
- Writing `fernpage.json` checks it first. An invalid file refuses the whole `write_files` call with `rules_invalid`, and the error names the field. When a collection that still has entries is removed, its entries are kept and only become reachable again if the collection is declared again. `get_site` reports any such orphaned collections.
- **Agents act as the owner**, so access rules never block them. An agent's edit of a visitor's entry leaves `created_by` unchanged, which means the visitor can still edit their RSVP afterwards.

## Tools

| Tool | Read-only | Destructive | Idempotent | Open world |
| --- | --- | --- | --- | --- |
| `list_sites` | yes | | yes | |
| `get_site` | yes | | yes | |
| `read_file` | yes | | yes | |
| `list_data_entries` | yes | | yes | |
| `create_site` | | no | no | yes (`source_url`) |
| `write_files` | | yes | yes | yes (`source_url`) |
| `edit_file` | | yes | no | |
| `delete_files` | | yes | yes | |
| `delete_site` | | yes | yes | |
| `create_data_entries` | | no | yes | |
| `update_data_entries` | | yes | no | |
| `delete_data_entries` | | yes | yes | |

Each annotation describes the tool's worst supported effect. For example, `write_files` replaces existing files, so it is marked destructive even when it only adds new ones.

The first sentence of each description below is the text hosts index for tool search.

---

### `list_sites`

> List sites in the connected workspace and find a site's id by title or address.

```ts
input:  { query?: string; cursor?: string; limit?: number }
output: { workspace: { id: string; name: string }; sites: Site[]; next_cursor: string | null }
```

`query` matches the title or address case-insensitively, and the results are ordered by `updated_at` descending. Sites in Trash are not listed. Use this tool when the user names a site ("the wedding page"). If more than one site matches, every candidate is returned with its `id`, and the agent asks the user or picks by id. It never guesses.

### `get_site`

> Get a site's details, file list, and saved-data collections by site id.

```ts
input:  { site_id: SiteId }
output: {
  site: Site;
  files: FileInfo[];                        // every file, sorted by path
  collections: Collection[];                // declared in fernpage.json
  orphaned_collections: { name: string; entry_count: number }[];
  usage: { files_bytes: number; files_limit: number; data_bytes: number; data_limit: number };
}
```

The file list is metadata only. File contents are read with `read_file`.

### `read_file`

> Read one file's contents and version from a site.

```ts
input:  { site_id: SiteId; path: string }
output:
  | { kind: "text";   file: FileInfo; content: string }
  | { kind: "binary"; file: FileInfo; url: string }   // public URL of the file; bytes are not inlined
```

Text means UTF-8 files with a text content type, such as HTML, CSS, JS, JSON, SVG, TXT or MD. Use the returned `version` as `expected_version` in a later write.

### `create_site`

> Create a new site in the connected workspace with its initial files; one index.html is enough.

```ts
input: {
  files: FileInput[];          // 1–50 items, must include "index.html"
  address?: string;            // 3–40 chars, [a-z0-9-], no leading/trailing hyphen
}
type FileInput = { path: string } & (
  | { content: string }        // UTF-8 text, up to 512 KB
  | { content_base64: string } // tiny binaries only (e.g. a favicon), up to 64 KB
  | { source_url: string }     // https URL the server fetches; use for images and other assets
);
output: { site: Site; files: FileInfo[] }
```

- Each file needs exactly one of `content`, `content_base64` or `source_url`. For anything that isn't text, `source_url` is the main way in. Encoding large blobs inline is slow and expensive for a model. The server fetches the URL with SSRF protection, size caps and a timeout.
- If `address` is omitted, a random address is generated. An address that is taken returns `address_taken` together with an available suggestion.
- Creating the site and writing its files is one atomic step. If any file fails, no site is created, and the error lists each item's problem.
- Calling it twice creates two sites, so it is not idempotent. Before retrying after an unclear outcome, call `list_sites`.

### `write_files`

> Write files to a site, creating new files or replacing existing ones in full.

```ts
input: {
  site_id: SiteId;
  files: (FileInput & { expected_version?: Version | "absent" })[];  // 1–50 items
}
output:
  | { outcome: "applied"; site: Site; results: { path: string; status: "created" | "replaced" | "unchanged"; file: FileInfo }[] }
  | { outcome: "rejected"; results: ({ path: string; status: "ok" } | { path: string; status: "failed"; error: ErrorCode; message: string; current?: FileInfo })[] }
```

- Atomic. All files land in one new site revision, so visitors never see a half-applied change, such as a new `index.html` pointing to an image that hasn't arrived. If any item fails, nothing lands. The `rejected` result marks each item `ok` or `failed`, so the agent fixes only the failures and resends the batch.
- Each file replaces whatever is at its path. To change a few lines, use `edit_file`.
- `expected_version` is an optional guard. With a version, the write is refused if the file has changed since then. With `"absent"`, the write is refused if the file already exists. Leaving it out only skips the check. It never makes the write affect anything beyond the paths listed.
- Rewriting identical content returns `unchanged` and doesn't create a new revision.
- Writing `fernpage.json` validates the rules first, as described in [Saved data and access rules](#saved-data-and-access-rules).

### `edit_file`

> Edit part of one text file by replacing exact text, without resending the whole file.

```ts
input: {
  site_id: SiteId;
  path: string;
  expected_version?: Version;
  edits: { old_text: string; new_text: string }[];   // 1–20, applied in order
}
output: { site: Site; file: FileInfo }
```

- Each `old_text` has to appear **exactly once** in the file at the moment that edit runs. If it appears zero times, the tool returns `edit_no_match`. If it appears more than once, it returns `edit_ambiguous_match` with the match count, and the agent should add surrounding context. The edits to one file are atomic: they all apply or none do.
- Only existing text files can be edited. A missing file returns `file_not_found`, and the agent should use `write_files` to create it.

### `delete_files`

> Delete files from a site by path.

```ts
input:  { site_id: SiteId; paths: string[] }   // 1–50
output:
  | { outcome: "applied"; site: Site; results: { path: string; status: "deleted" | "not_found" }[] }
  | { outcome: "rejected"; results: ({ path: string; status: "ok" } | { path: string; status: "failed"; error: ErrorCode; message: string })[] }
```

- Atomic, in one revision. A path that is already gone reports `not_found`, which doesn't block the batch.
- `index.html` can't be deleted (`index_required`), because a site without it can't be served. To retire a site, use `delete_site`. To change the page, replace `index.html`.
- No folder or wildcard deletion exists. Every path is listed explicitly.

### `delete_site`

> Delete a site by id, moving it to Trash for 30 days.

```ts
input:  { site_id: SiteId }
output: { site_id: SiteId; status: "trashed" | "already_trashed"; purge_at: string; trash_url: string }
```

- A site in Trash stops serving immediately. Its files and saved data are kept until `purge_at`, which is 30 days later, and are then permanently removed by a bounded deletion job.
- **Only the browser app can restore a site.** No MCP tool exists for it. When the user wants a site back, the agent gives them `trash_url`.
- The tool takes a site id only. To find the id, use `list_sites` or `get_site` first.

### `list_data_entries`

> List saved-data entries in one collection of a site, with their values and versions.

```ts
input: {
  site_id: SiteId;
  collection: string;
  cursor?: string;
  limit?: number;
  order?: "created_asc" | "created_desc";   // default "created_asc"
}
output: { entries: Entry[]; next_cursor: string | null }
```

The page is a snapshot. Visitors may add or change entries between pages, so re-read before a write that depends on an exact value. The `version` of each entry is what the update and delete tools need.

### `create_data_entries`

> Create saved-data entries in a site, such as seeding checklist items or default settings.

```ts
input: {
  site_id: SiteId;
  entries: { collection: string; key?: string; value: unknown }[];   // 1–100
}
output: {
  results: (
    | { index: number; status: "created"; entry: Entry }
    | { index: number; status: "unchanged"; entry: Entry }          // key existed with an identical value
    | { index: number; status: "failed"; error: ErrorCode; message: string; current?: Entry }
  )[];
}
```

- This tool only adds entries. It never overwrites one. If the key already exists with a different value, the result is `entry_exists` with `current`, and the agent decides whether to call `update_data_entries`.
- If `key` is omitted, a key is generated (the same way the SDK's "add" does). Give explicit keys when seeding, so a retry is safe: rerunning the same seed returns `unchanged` and doesn't create duplicates.
- The entries created get `created_by: { kind: "owner" }`.

### `update_data_entries`

> Update saved-data entries in a site by key, such as fixing a misspelled RSVP name or changing a setting.

```ts
input: {
  site_id: SiteId;
  updates: {
    collection: string;
    key: string;
    expected_version: Version;   // required: from list_data_entries
    patch: unknown;              // JSON Merge Patch (RFC 7396) applied to the current value
  }[];                           // 1–100
}
output: {
  results: (
    | { index: number; status: "updated"; entry: Entry }
    | { index: number; status: "unchanged"; entry: Entry }
    | { index: number; status: "failed"; error: ErrorCode; message: string; current?: Entry }
  )[];
}
```

- `expected_version` is required because visitors may be writing at the same moment. If a visitor changed the entry after the agent read it, the item fails with `version_conflict` and the current entry. The agent reapplies its fix on top of that entry and retries only that item.
- A merge patch only touches the fields it names. For example, `{"name": "Ana Lima"}` fixes the name and leaves the guest's meal choice alone. A `null` removes a field. If the value isn't an object, the patch replaces it.
- `created_by` is never changed.

### `delete_data_entries`

> Delete saved-data entries from a site by key, such as clearing test RSVPs before launch.

```ts
input: {
  site_id: SiteId;
  deletes: { collection: string; key: string; expected_version: Version }[];   // 1–100
}
output: {
  results: (
    | { index: number; status: "deleted" }
    | { index: number; status: "not_found" }
    | { index: number; status: "failed"; error: ErrorCode; message: string; current?: Entry }
  )[];
}
```

- Every entry is named by key and version. No tool clears a whole collection, because a real visitor could submit an entry while a test cleanup is running, and an unconditional clear would delete it without anyone noticing. To clear test entries, the agent lists them, checks which ones are tests, and deletes those by key. If an entry changed after the agent read it, the item fails with `version_conflict`.
- Saved-data deletion can't be undone. Unlike deleting a site, entries don't go to Trash.

## Error codes

| Code | Meaning and next move |
| --- | --- |
| `not_authorized` | The token's workspace can't do this. Re-authorize and pick the right workspace. |
| `site_not_found` | No site with that id in this workspace, or the site is in Trash. Call `list_sites`. |
| `address_taken` | The address is in use. The error includes an available suggestion. |
| `address_invalid` | Names the rule that was broken (characters or length). |
| `path_invalid` | Names the rule that was broken (leading slash, `..`, backslash or empty segment). |
| `file_not_found` | The path doesn't exist. Use `write_files` to create it. |
| `index_required` | `create_site` needs `index.html`, and `delete_files` can't remove it. |
| `version_conflict` | Someone changed the item since it was read. `current` is included. Reapply the change and retry. |
| `edit_no_match` / `edit_ambiguous_match` | Says which edit failed and the match count. Add context to `old_text`. |
| `not_text` | `edit_file` was called on a binary file. Use `write_files`. |
| `file_too_large` / `inline_too_large` | Quotes the measured size and the limit. Use `source_url` for large files. |
| `site_storage_full` / `data_storage_full` | Quotes current usage and the limit. Remove something or reduce what is being written. |
| `fetch_failed` | The `source_url` couldn't be fetched (status, timeout or blocked address), or the response was over the size cap. |
| `rules_invalid` | `fernpage.json` didn't validate. Names the field. |
| `collection_not_declared` | Add the collection to `fernpage.json` first. |
| `entry_exists` / `entry_not_found` | `current` is included where an entry exists. |
| `value_too_large` | Quotes the entry's serialized size and the 64 KB limit. |
| `rate_limited` | Includes `retry_after_seconds`. |

## Typical workflows

- **Build a site:** `create_site` with `index.html`, `style.css` and `app.js`, plus `fernpage.json` if the site saves data. Then `create_data_entries` to seed checklist items or default settings. Give the user `site.url`.
- **Make a small change:** `get_site`, then `read_file` (keep its `version`), then `edit_file` with `expected_version`.
- **Fix a misspelled RSVP:** `get_site` to find the id, then `list_data_entries` on `rsvps`, then `update_data_entries` with `patch: {"name": "..."}` and the entry's version. On a `version_conflict`, re-read that entry and retry.
- **Clear test entries before launch:** `list_data_entries`, pick the test entries, then `delete_data_entries` with their keys and versions.
- **Change a setting:** `update_data_entries` on the `settings` collection. Open pages update live.
- **Remove a site:** `delete_site`. Tell the user it can be restored from `trash_url` for 30 days.

## Assumptions to confirm

The brief doesn't decide any of the following. Each was decided here so the catalog is complete, and each can be reversed.

1. **Domains.** The product is at `fernpage.com` and MCP is at `mcp.fernpage.com/mcp`. Sites are served from a **separate registrable domain**, `<address>.fernpage.site`. Sites run arbitrary JavaScript, so they must not share an origin or cookies with the app or with each other. That rules out path-based URLs on one host. The site's address isn't its 12-character id, because DNS labels are case-insensitive and Base58 ids are case-sensitive. A public, readable address is fine here because sites are public pages.
2. **Addresses are set at creation only.** Renaming an address breaks links that are already shared (invitations, for example), so it is left to the browser app. No MCP tool renames an address. Custom domains are out of scope.
3. **Workspace selection happens at OAuth consent**, and one token covers one workspace. The alternative was a `workspace_id` argument on every call. That was rejected because it lets one wrongly filled argument send writes to the wrong workspace.
4. **Access rules live in a reserved `fernpage.json` file.** The brief says rules are declared "in its settings". Here, "settings" in the saved-data sense means a site's own saved values (for example, whether RSVPs are open), and the rules are site configuration that goes out with the files. This was the biggest decision made here. The alternative is dedicated `get_data_rules` / `set_data_rules` tools.
5. **The saved-data model** is collections of keyed JSON entries. The rule principals are `anyone`, `creator` and `owner`, the owner can always do everything, and rules default to deny. Any member of the workspace counts as the owner. Visitor identity (`visitor_id`) is an anonymous per-browser id issued by the runtime SDK.
6. **Agents act as the owner.** They bypass access rules but go through the same versioned writes as visitors.
7. **File changes are live immediately.** There is no draft or publish step, and multi-file changes are atomic site revisions. Changes can't be rolled back through MCP (no revision history tools).
8. **No bulk clear of a collection,** and no file deletion by folder or wildcard. Every destructive call names each item. Saved-data deletes are permanent. Only deleting a whole site goes to Trash, as the brief decides.
9. **Sites in Trash** are hidden from `list_sites`, stop serving immediately, and return `site_not_found` to every tool.
10. **All limits** in [Conventions](#conventions) are starting values. They aren't decisions from the brief. The brief only says saved data is "a few kilobytes to a few megabytes per site".
11. **Leaving it out of v1:** there are no tools for revision history or rollback, custom domains, workspace members, or reading visitor analytics. An agent can't upload bytes from its own disk beyond the inline limits. It can only provide a URL. A signed-upload tool can be added if hosts that need it show up.

````

> Result: File created successfully at: <run>\builds\4-file-catalog-with-saved-data-old-opus2\work\docs\mcp-tools.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the MCP tool catalog to `docs/mcp-tools.md`. I didn't commit it.

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

**Session ended:** success, 9 turns, 190475 ms
