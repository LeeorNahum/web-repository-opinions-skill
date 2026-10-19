**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-new-opus/work\" && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5643 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md agent-tool-design.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 11720 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat uploads.md live-data.md data-deletion.md ids.md workspace-tenancy.md"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 15150 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat bulk-actions.md abuse-resistance.md domains.md user-facing-errors.md data-model.md source-of-truth.md object-storage.md"}`

> Result: # Bulk Actions  Design bulk work as independent per-item outcomes unless the operation is inherently atomic.  ## Result Contract  Return one structured result for every requested item. Include the stable input identity and a small product-level state such as completed, unchanged, or failed. Where the result shape is typed, give each state its own variant carrying exactly the facts it promise [... 22248 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references\" && cat naming.md http-apis.md agent-skills.md path-display.md quota.md"}`

> Result: # Naming  Name by paradigm, not by provider. A thing is named for what it does so the name survives a tool swap.  | Identifier                                      | Convention      | Example                          | | ----------------------------------------------- | --------------- | -------------------------------- | | Repo and canonical folder                       | Title-Dash-Case |  [... 11829 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-file-catalog-with-saved-data-new-opus/work\" && cat package.json pnpm-workspace.yaml AGENTS.md; ls docs"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*" # Product repository  This TypeScript monorepo holds the product. `docs/brief.m [... 84 more characters]

**Tool call `Write`:** `<run>\builds\4-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md`

````text
# Fernpage MCP tool catalog

These are the tools agents use to build and maintain Fernpage sites. `docs/brief.md` is the source of truth for product decisions. If this document disagrees with it, the brief wins and this document is the one that gets fixed.

Status: draft. Calls the owner has not made yet are marked **Assumed** and gathered in [Assumptions and open questions](#assumptions-and-open-questions).

## Shape in one paragraph

An agent sees a site as a folder of files. Site files (HTML, CSS, JS, assets) are ordinary files. Saved data appears as JSON files too: one file per collection under the reserved `.fernpage/` folder, plus one settings file. The agent reads, writes, edits, searches, and deletes all of them with the same small set of file tools. There are no separate record tools. When an agent writes a saved-data file, the server works out which entries changed and applies each change on its own, using the same rules, validation, and quota that apply when a visitor's browser writes one entry. Changes visitors made since the agent last read the file are kept.

## Server

- Endpoint: `https://mcp.<domain>/mcp`, deployed as its own protocol app (`apps/mcp`, Hono plus the official MCP SDK).
- Stateless requests with buffered JSON responses. No streaming or subscriptions: agents don't need live updates. Visitors' pages get those through the runtime SDK.
- Every caller sees the same static catalog. Authorization is checked on every call, and refusals are typed errors (see [Errors](#errors)).
- OAuth through the auth provider. The access token's audience must include the MCP resource. **Assumed:** grants are **account-wide**. A grant covers every workspace the user belongs to, because the brief says agents create sites "in one of the user's workspaces". On each call the server checks a live membership for the target site's workspace, so removing someone from a workspace cuts off their existing agent connections too.
- For rule purposes, the agent acts as the **site owner**. **Assumed:** any workspace member who can edit sites counts as owner. If a read-only role is added later, it gets a `forbidden` refusal on writes.

## Identifiers and paths

- `workspace_id`, `site_id`: 12-character Base58 entity IDs. Tools that create, write, or delete take IDs. Names are never accepted there. `list_sites` can search by title and returns candidates with their IDs.
- Site URL: `https://<address>.<content-domain>`, where `<content-domain>` is a separate registrable domain from the product's (user-supplied code never runs on the product's own domain). `<address>` is a generated lowercase label, separate from `site_id`, because hostnames are case-insensitive and can't carry a case-sensitive Base58 ID. **Assumed:** agents can't choose or change the address.
- Paths are relative to the site root, use `/`, are case-sensitive, have no leading `/`, no `.` or `..` segments, and no empty segments. Max 512 bytes. Every path a tool returns can be passed straight to another tool.
- Listings return `name` (the leaf) and `path` (full path from the site root).

### Reserved paths (never served to visitors)

| Path | What it is |
| --- | --- |
| `.fernpage/settings.json` | Site settings: per-collection write rules and site setting values. |
| `.fernpage/saved/<collection>.json` | One saved-data collection. `<collection>` matches `[a-z0-9][a-z0-9-]{0,62}`. |

Any other path under `.fernpage/` is refused with `reserved_path`. Every path outside `.fernpage/` is a site file, served as-is at the site URL.

## Saved data as files

### Collection file format

A collection file is a JSON object that maps entry keys to entries. Reads render it canonically, one entry per line in creation order, so line-based reads, exact edits, and search results line up with entries:

```json
{
  "k3Fq9TzP2mXa": {"name": "Ana Lopez", "guests": 2, "$meta": {"created": "2026-10-18T14:02:11Z", "updated": "2026-10-18T14:02:11Z", "by": "visitor:v_8fd2c1"}},
  "buy-flowers": {"label": "Buy flowers", "done": false, "$meta": {"created": "2026-10-19T09:00:00Z", "updated": "2026-10-19T09:00:00Z", "by": "owner"}}
}
```

- **Assumed:** each entry is a JSON object, the unit the visitor SDK reads and writes.
- Keys match `[A-Za-z0-9_-]{1,64}`. Keys minted by the SDK are 12-character Base58. Agents may pick readable keys when seeding (`buy-flowers`).
- `$meta` is read-only and owned by the server. `by` is `owner`, or `visitor:<pseudonym>`, where the pseudonym is derived per site so it can't follow a visitor across sites. A write may leave `$meta` out (the server fills it in for new entries and keeps it for existing ones) or send it back unchanged. Changing it is refused with `read_only_field`.
- Agents can use `$meta` to spot test entries before launch: entries created before a date, or by a specific visitor pseudonym.
- Limits (**Assumed** placeholder numbers): 32 KB per entry, 5 MB of saved data per site including settings.

### Settings file format

```json
{
  "collections": {
    "rsvps":     {"read": "anyone", "create": "anyone", "update": "author", "delete": "author"},
    "checklist": {"read": "anyone", "create": "owner",  "update": "anyone", "delete": "owner"}
  },
  "values": {"eventDate": "2027-05-01", "rsvpOpen": true}
}
```

- Each rule is one of `anyone`, `author` (the visitor who created the entry), or `owner`. The owner can always do everything.
- `values` holds the site's own settings. Visitors read them through the SDK, and only the owner writes them.
- A collection with no declared rules defaults to `read: anyone` and writes by `owner` only (**Assumed**: fail closed).
- For merging, each `collections.<name>` and each `values.<key>` is its own entry, so an agent changing one setting doesn't collide with someone changing another in the browser app.
- The settings file always exists and can't be deleted.

### How writes to saved data behave

The server remembers what it last served to each caller for each saved-data file. "Caller" means the OAuth grant (user plus client), because requests are stateless and carry no session. Only a **complete** read counts. A read cut short by `offset`/`limit` or by the size cap doesn't.

When a caller sends a whole-file write, the server compares it with that baseline:

1. Entries the caller added, changed, or removed relative to the baseline are applied one at a time. Each one goes through the collection's rules (as owner), validation, and quota.
2. Entries the caller left untouched keep whatever happened to them since, including new entries visitors added and entries visitors deleted.
3. If the caller changed or removed an entry that someone else also changed or removed since the baseline, the whole write is refused with `conflict`. The refusal lists those entry keys and asks for a fresh `read_file`. Nothing is applied.
4. With no complete read on record, the baseline is empty. So the write can **add** entries, but if it includes a key that already exists on the server with different content, that's a conflict. This lets an agent seed a collection without reading it first, and stops it from blindly overwriting visitor entries.

The result says which case happened:

- `stored`: the file now matches what was sent exactly. This becomes the caller's new baseline.
- `merged`: the caller's changes were applied and concurrent changes were kept. The file is not what the caller sent, so the caller's baseline is **not** moved to the merged state. The result gives counts (`added`, `updated`, `removed`, `kept_concurrent`) and says to `read_file` before reasoning about the current contents.

`edit_file` on a saved-data file is applied to the current stored text, so the exact `old_text` match is the guard. The edited result must parse, and each entry whose content changed then goes through the same per-entry rules. `delete_files` on a collection file removes every entry in the collection. Visitors may start a new one by writing again if the rules allow it.

All of this is atomic per call. Either every changed entry in a file lands, or none do.

## Site files

- Text files (`.html`, `.css`, `.js`, `.json`, `.svg`, `.txt`, `.md`, `.xml`, `.webmanifest`, and so on) can be sent inline as UTF-8, up to 256 KB per file and 1 MB per call.
- Binary files, and text over the inline cap, come in by `source_url`: an HTTPS URL the server fetches, or an attachment reference the host documents as fetchable. The fetch is hardened: byte cap at the file limit, timeout, at most 3 redirects with each hop rechecked, private, loopback, link-local, and metadata addresses refused, and the content type checked from the bytes received rather than the type the source claims. Local paths and sandbox URIs (`file://`, `/tmp/...`, `sandbox:`) are refused with `unreachable_source`, and the refusal names the routes that do work.
- Limits (**Assumed** placeholder numbers): 25 MB per file, 100 MB of site files per site, 2,000 files per site.
- Overwriting an existing site file requires a complete read of it first. If anyone else changed it since that read (another agent, or the browser app), the write is refused with `conflict`. The caller's own last write counts as a read.
- `index.html` is required and can't be deleted. The site's title, description, and favicon are always derived from it (brief: decided). Any write or edit that changes `index.html` returns the site's resulting `title`, `description`, and `favicon` in its result, so the caller doesn't hold stale values.

## Shared resource shapes

```ts
type Site = {
  id: string;                 // Base58, 12 chars
  workspace_id: string;
  url: string;                // https://<address>.<content-domain>/
  title: string | null;       // from index.html <title>
  description: string | null; // from index.html <meta name="description">
  favicon: string | null;     // path or URL from index.html <link rel="icon">
  created: string;            // ISO 8601
  updated: string;
  usage: { files: number; file_bytes: number; saved_bytes: number };
};

type FileEntry = {
  name: string;               // leaf segment
  path: string;               // from site root
  kind: "site_file" | "saved_data" | "settings";
  bytes: number;
  content_type: string;
  updated: string;
  entries?: number;           // saved_data only
};
```

The HTTP API, the browser app, and the agent skill use these same shapes.

## Tools

Ten tools. Names are imperative verb then noun. Plural nouns mean the tool takes a list.

| Tool | Read-only | Destructive | Idempotent | Open world |
| --- | --- | --- | --- | --- |
| `list_workspaces` | yes | no | yes | no |
| `list_sites` | yes | no | yes | no |
| `get_site` | yes | no | yes | no |
| `create_site` | no | no | no | yes |
| `list_files` | yes | no | yes | no |
| `read_file` | yes | no | yes | no |
| `search_files` | yes | no | yes | no |
| `write_files` | no | yes | no | yes |
| `edit_file` | no | yes | no | no |
| `delete_files` | no | yes | yes | no |
| `delete_site` | no | yes | yes | no |

That's eleven rows. `get_site` is the one read that could fold into `list_sites`, but it's kept separate so an agent holding an ID doesn't have to page through a list.

### `list_workspaces`

> List the workspaces this connection can create and edit sites in.

Arguments: none.

Returns `{ workspaces: { id, name, role }[] }`.

### `list_sites`

> List or find sites in a workspace by title.

```json
{
  "workspace_id": "string, required",
  "query": "string, optional: case-insensitive substring match on title",
  "cursor": "string, optional",
  "limit": "integer 1-100, default 50"
}
```

Returns `{ sites: Site[], next_cursor: string | null }`. Sites in Trash aren't listed. Several matches for `query` are returned as candidates, each with its `id`.

### `get_site`

> Get a site's URL, title, description, favicon, and usage.

```json
{ "site_id": "string, required" }
```

Returns `Site`. A site in Trash returns `in_trash` with its purge date and the browser-app link for restoring it.

### `create_site`

> Create a new site in a workspace and publish its first files.

```json
{
  "workspace_id": "string, required",
  "files": [
    { "path": "index.html", "content": "<!doctype html>..." },
    { "path": "img/hero.jpg", "source_url": "https://..." }
  ]
}
```

- `files`: required, 1 to 50 items, and must include `index.html`. Each item has `path` and exactly one of `content` (inline UTF-8 text) or `source_url`. Items may include `.fernpage/settings.json` and `.fernpage/saved/*.json` to set rules and seed data.
- The site is live at its URL as soon as this returns (brief: one `index.html` is enough to publish). There is no separate publish step.
- All or nothing: if any file fails, no site is created and the per-file reasons are returned.
- Not idempotent. Retrying after a timeout can create a second site, so call `list_sites` first to check.

Returns `{ site: Site }`.

### `list_files`

> List a site's files, saved-data collections, and settings.

```json
{
  "site_id": "string, required",
  "path_prefix": "string, optional, e.g. \"img/\" or \".fernpage/saved/\""
}
```

Returns `{ files: FileEntry[] }`, sorted by path. Not paginated: sites are capped at 2,000 files.

### `read_file`

> Read a site file, saved-data collection, or settings file.

```json
{
  "site_id": "string, required",
  "path": "string, required",
  "offset": "integer >= 1, optional: first line to return",
  "limit": "integer 1-5000, optional, default 2000 lines"
}
```

- Text returns `{ path, content, total_lines, complete }`. `complete` is `true` only when the whole file was returned. Only a complete read sets the baseline that writes are compared with.
- Binary returns `{ path, content_type, bytes, sha256, url }`. This counts as a complete read for overwrite checks.
- Saved-data files come back in the canonical one-entry-per-line form described above. Files larger than 256 KB of text are never returned whole: page through them with `offset`/`limit`, then use `edit_file` (which doesn't need a complete read), or refer to entries by key.

### `search_files`

> Search a site's files and saved data for text or a regular expression.

```json
{
  "site_id": "string, required",
  "pattern": "string, required",
  "mode": "\"text\" | \"regex\", default \"text\"",
  "case_sensitive": "boolean, default false",
  "path_prefix": "string, optional",
  "max_results": "integer 1-200, default 50"
}
```

Returns `{ matches: { path, line, column, text }[], truncated }`. `text` is the matching line, cut to 300 characters. For saved data, one line is one entry, so a match points at an entry. Binary files are skipped.

### `write_files`

> Write or replace files in a site: pages, assets, saved data, or settings.

```json
{
  "site_id": "string, required",
  "files": [
    { "path": "about.html", "content": "..." },
    { "path": "img/logo.png", "source_url": "https://..." },
    { "path": ".fernpage/saved/checklist.json", "content": "{ ... }" }
  ]
}
```

- `files`: 1 to 50 items, each with `path` and exactly one of `content` or `source_url`. A path that doesn't exist yet is created. This is the only way to add a file to an existing site.
- Each file is handled on its own. Results come back one per item, in input order:
  - `{ path, status: "created" }`
  - `{ path, status: "replaced" }`
  - `{ path, status: "unchanged" }`
  - `{ path, status: "stored", added, updated, removed }` (saved data)
  - `{ path, status: "merged", added, updated, removed, kept_concurrent }` (saved data)
  - `{ path, status: "failed", error }`
- If any item touched `index.html`, the result also carries `site: { title, description, favicon }`.
- Retrying is safe: it doesn't duplicate files or entries. A retried saved-data write after a timeout is checked against the same baseline.

### `edit_file`

> Replace exact text in a site file, saved-data collection, or settings file.

```json
{
  "site_id": "string, required",
  "path": "string, required",
  "old_text": "string, required, non-empty",
  "new_text": "string, required",
  "replace_all": "boolean, default false"
}
```

- Applied to the current stored text. With `replace_all: false`, `old_text` must occur exactly once. Zero matches is refused with `no_match`. More than one is refused with `ambiguous_match` and the count.
- Text files only. The edited file must still be valid (JSON for saved data and settings), and every changed entry passes rules and validation.
- Returns `{ path, status: "replaced" }`, plus `site` when it was `index.html`, or `entries_changed: string[]` for saved data.
- Not idempotent: replaying it after success usually returns `no_match`.

Typical saved-data fix (correct a misspelled RSVP name):

```json
{ "site_id": "Qm3x...", "path": ".fernpage/saved/rsvps.json",
  "old_text": "\"name\": \"Ana Lopze\"", "new_text": "\"name\": \"Ana Lopez\"" }
```

### `delete_files`

> Delete specific files or saved-data collections from a site.

```json
{
  "site_id": "string, required",
  "paths": ["string", "..."]
}
```

- `paths`: 1 to 50 exact file paths. A directory path, a glob, `index.html`, or `.fernpage/settings.json` is refused for that item. Nothing outside the named paths is removed.
- Deleting `.fernpage/saved/<collection>.json` removes all of that collection's entries. To remove only some entries (for example test RSVPs), use `write_files` without them, or `edit_file`.
- Results come back one per item, in input order: `deleted`, `not_found`, or `failed` with an error.
- Deleted site files are gone for good. **Assumed:** there is no per-file trash. Only whole sites go to Trash.

### `delete_site`

> Delete a whole site by moving it to Trash for 30 days.

```json
{ "site_id": "string, required" }
```

- The site goes offline at once and moves to Trash. It's purged after 30 days (brief: decided).
- Returns `{ site_id, status: "in_trash", purge_after, restore_url }`, where `restore_url` points to the site in the browser app. Restoring happens only in the browser app (brief: decided), so there's no restore tool.
- Calling it again on a site already in Trash returns the same result.

## Errors

Every refusal is `{ error: { code, message, ... } }`. The message is product copy in plain language that states what was measured and the next step, without echoing the rejected content.

| Code | When | Next step in the message |
| --- | --- | --- |
| `not_found` | Unknown or inaccessible workspace, site, or path | `list_sites` / `list_files` |
| `forbidden` | No live membership or share covers the target | Ask a workspace admin for access |
| `in_trash` | Site is in Trash | Restore it in the browser app (link) |
| `conflict` | Overwrite or entry collision since the caller's last complete read | `read_file`, then reapply. Includes `entry_keys` for saved data |
| `read_required` | Overwriting an existing site file with no read on record | `read_file` first |
| `no_match` / `ambiguous_match` | `edit_file` match count is not 1 | Widen `old_text` or set `replace_all` |
| `invalid_path` / `reserved_path` | Bad path syntax, or an unknown `.fernpage/` path | Valid patterns |
| `protected_file` | Deleting `index.html` or settings | Edit it instead, or `delete_site` |
| `invalid_json` / `read_only_field` / `invalid_entry` | Saved data or settings failed validation | Line and key of the problem |
| `rule_denied` | An entry change the rules forbid, even for the owner (reserved for future rule kinds) | The rule that refused it |
| `too_large` | Over an inline, file, entry, or site cap | The cap and the measured size, plus the `source_url` route for big files |
| `quota_exceeded` | Workspace allowance used up | What's using it, where to free space |
| `unreachable_source` | Local path, sandbox URI, or URL the server can't fetch | Use an HTTPS URL or a host attachment |
| `fetch_failed` | `source_url` fetch failed or bytes didn't match the type | Check the URL |
| `index_required` | `create_site` without `index.html` | Include it |

## Deliberately not tools

- **Separate record tools** (`get_entry`, `set_entry`, …): saved data goes through the file tools, which already apply per-entry rules and merging.
- **Publish**: a site is live once it has `index.html`.
- **Upload staging or finalizing**: `source_url` covers remote agents. The HTTP API and CLI handle signed uploads for callers that have local bytes.
- **Restore from Trash**: browser app only, per the brief.
- **Confirmation flags** on destructive tools: the host approves the call, and the server enforces authorization.
- **Required revision tokens or idempotency keys**: the server keeps each caller's read baseline itself.

## Typical flows

- **New RSVP site:** `list_workspaces`, then `create_site` with `index.html`, `style.css`, `app.js`, and `.fernpage/settings.json` declaring `rsvps` (`create: anyone`, `update/delete: author`).
- **Small copy change:** `edit_file` on `index.html`. The result includes the new title if it changed.
- **Seed a checklist:** `write_files` with `.fernpage/saved/checklist.json` holding the items. No read is needed when the collection is new.
- **Clear test entries before launch:** `read_file` on `.fernpage/saved/rsvps.json` (complete), then `write_files` with the test entries removed. RSVPs visitors submitted in the meantime are kept, and the result is `merged`.
- **Change a setting:** `edit_file` on `.fernpage/settings.json` (for example `"rsvpOpen": true` to `false`).
- **Take a site down:** `delete_site`.

## Assumptions and open questions

Calls made without the owner. Each one can be reversed before anything ships.

1. **Saved data lives under `.fernpage/`** (`settings.json`, `saved/<collection>.json`), is never served as a static file, and is reached only through the file tools. The `.fernpage/` name is a placeholder.
2. **Saved data is organized as named collections of keyed JSON-object entries.** The brief says "one entry at a time" but doesn't define the SDK's data model. If the SDK uses a different unit, the file format changes, but the merge rules don't.
3. **Write rules use three subjects, `anyone`, `author`, and `owner`, per operation**, enough for both examples in the brief. Undeclared collections are owner-write, public-read. Whether some collections should be private to visitors (owner-read only, for example RSVP details) is an open question. The rule vocabulary allows `read: "owner"`.
4. **"Site settings" in the brief covers two things,** write rules and site setting values. Both are put in one owner-only settings file.
5. **Agents act as the site owner** for rule purposes. Any workspace member who can edit sites qualifies.
6. **Grants are account-wide** across the user's workspaces. `create_site` always requires an explicit `workspace_id`, with no default workspace.
7. **The write baseline is kept per OAuth grant.** Two agent sessions sharing one grant share a baseline.
8. **`index.html` can't be deleted** while the site exists, because the site's identity is derived from it. Taking a site down is `delete_site`.
9. **No publish/unpublish state.** A site is live from creation until it's deleted.
10. **Site addresses are generated lowercase labels** on a separate content domain. Neither domain is chosen yet. Custom or chosen addresses are an open question.
11. **All numeric limits are placeholders** (inline 256 KB per file and 1 MB per call; files 25 MB; site files 100 MB and 2,000 files; entries 32 KB; saved data 5 MB; batches of 50). They need sizing against the hosting and database budgets. The hidden internal ceiling and any plan limits shown to users are a billing decision.
12. **Individually deleted files are not recoverable.** Only whole sites go to Trash.
13. **Binary reads return metadata and a URL**, not inline image content. Returning images as MCP image content can be added once target hosts are tested.

````

> Result: File created successfully at: <run>\builds\4-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `<run>\builds\4-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md`

Replaced:

````text
Ten tools. Names are imperative verb then noun. Plural nouns mean the tool takes a list.
````

With:

````text
Eleven tools. Names are imperative verb then noun. Plural nouns mean the tool takes a list.
````

> Result: The file <run>\builds\4-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `<run>\builds\4-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md`

Replaced:

````text

That's eleven rows. `get_site` is the one read that could fold into `list_sites`, but it's kept separate so an agent holding an ID doesn't have to page through a list.

````

With:

````text

````

> Result: The file <run>\builds\4-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** I've written the tool catalog to `docs/mcp-tools.md`. It's a design document only: nothing is built yet and nothing is committed.

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

**Session ended:** success, 12 turns, 213287 ms
