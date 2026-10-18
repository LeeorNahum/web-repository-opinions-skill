**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-file-catalog-with-saved-data-new-opus/work && git ls-files && cat docs/brief.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5643 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references && cat model-context-protocol.md agent-tool-design.md"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 10497 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references && cat uploads.md ids.md workspace-tenancy.md data-deletion.md bulk-actions.md"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 15889 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references && cat live-data.md domains.md abuse-resistance.md social-metadata.md naming.md data-model.md source-of-truth.md user-facing-errors.md agent-skills.md"}`

> Result: # Live Data  Prefer a reactive backend whose queries push updates to the client, and wire it so the UI updates live. Convex is the default. Live updates are a core reason to choose a reactive backend, so realize that value rather than leaving it half-wired.  - Subscribe to data through the reactive client so a change on the backend reflects in every open view without a manual refetch or a page [... 25192 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-file-catalog-with-saved-data-new-opus/work/.claude/skills/web-repository-opinions/references && cat object-storage.md quota.md http-apis.md path-display.md modularity.md"}`

> Result: # Object Storage  Large user files belong in object storage, not the database. Cloudflare R2 is the default. Any S3-compatible store fills the role.  The database is the source of truth for metadata, ownership, status, and permissions. It stores the object key and references the bytes. Object storage holds only the bytes.  - Keep large media in object storage and store only its key and metad [... 16246 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/2-file-catalog-with-saved-data-new-opus/work && cat package.json pnpm-workspace.yaml AGENTS.md; ls docs"}`

> Result: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } packages:   - "apps/*"   - "packages/*" # Product repository  This TypeScript monorepo holds the product. `docs/brief.m [... 84 more characters]

**Assistant:** I've read the brief and the repo's tool-design guidance. Now I'm writing the catalog.

**Tool call `Write`:** `<run>\builds\2-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md`

````text
# Fernpage MCP tool catalog

This is the tool surface for agents that build and maintain Fernpage sites. `docs/brief.md` is the source of truth for product decisions. Where this document and the brief disagree, the brief wins and this document gets fixed. Calls made here that the brief does not settle are listed under [Assumptions](#assumptions) and [Open questions](#open-questions).

## Shape in one paragraph

An agent sees a site as **a tree of files**. Saved data shows up in the same tree under a reserved `@saved/` directory: one JSON file per entry, plus one settings file. Agents already know how to work with files: list, search, read, write whole files, make exact edits, delete. So agents use one set of verbs for both a stylesheet and a misspelled RSVP. Behind the file view, saved data stays one record per entry. A file operation on `@saved/` runs the same per-entry product mutation the visitor runtime SDK uses, with the same validation, quota, and live push to open pages. Replacing a whole entry file changes only that entry.

## Endpoint and posture

- Remote MCP at `https://mcp.<fernpage domain>/mcp`. It is a separate protocol app (`apps/mcp`, Hono plus the official MCP SDK web-standard transport). It returns buffered JSON responses and handles each request statelessly.
- OAuth through the auth provider. The MCP resource must be in the token audience, and any token without it is rejected. Each tool call checks that the caller has a live membership in the target workspace, so a revoked membership takes effect on existing tokens.
- **One static catalog for every caller.** Every caller sees all 12 tools, even one with no sites yet. A call the caller can't make comes back as a typed refusal.
- Every tool calls a shared product capability. The browser app and visitor SDK use those same capabilities. MCP adapts inputs and outputs but owns no rules.

## Catalog

| Tool | Does | readOnly | destructive | idempotent | openWorld |
| --- | --- | --- | --- | --- | --- |
| `list_workspaces` | List workspaces the user belongs to | yes | – | yes | no |
| `list_sites` | List or find sites by title | yes | – | yes | no |
| `get_site` | Get one site's details, saved-data summary, usage | yes | – | yes | no |
| `create_site` | Create a site in a workspace from initial files | no | no | **no** | yes¹ |
| `delete_site` | Move a whole site to Trash | no | yes | yes | no |
| `list_files` | List files, saved-data collections, and entries | yes | – | yes | no |
| `search_files` | Search file and saved-data contents by text or regex | yes | – | yes | no |
| `read_file` | Read one file or saved-data entry | yes | – | yes | no |
| `write_files` | Create or replace files or saved-data entries | no | yes | yes | yes¹ |
| `edit_file` | Make exact text replacements in one file or entry | no | yes | **no** | no |
| `delete_files` | Delete specific files or saved-data entries | no | yes | yes | no |
| `add_saved_entries` | Add new entries to a saved-data collection | no | no | **no** | no |

¹ Fetches a caller-supplied HTTPS URL when a file is given by `source_url`.

Annotations reflect the worst effect each tool can have. `write_files` replaces existing content, so it is marked destructive even though most calls only create files. Annotations only inform a host's approval prompt. Authorization is enforced on the server for every call. No tool takes a confirmation flag, and every tool is safe in an unattended run.

Naming: `verb_noun`, snake_case. The noun is plural exactly when the tool takes a list. Reads take one item. Writes may take several, and each item gets its own result.

## Paths

Every path is relative to the site root, with no leading slash. The server returns paths in a form you can pass straight back to another tool.

| Path | What it is |
| --- | --- |
| `index.html`, `css/site.css`, `img/fern.png` | Site files, served publicly at the site URL |
| `@saved/settings.json` | Site settings: setting values the page reads, plus write rules per collection |
| `@saved/<collection>/` | A saved-data collection, such as `@saved/rsvps/` |
| `@saved/<collection>/<entryId>.json` | One saved-data entry. `entryId` is a server-minted 12-char Base58 ID |

- `@saved/` is reserved. Site files can't be written there, and it is never served as a static file. Visitors reach saved data only through the runtime SDK.
- Paths are case-sensitive, and results show them exactly as stored.
- Refusals: `invalid_path` (`..`, empty segment, leading slash, control characters) and `reserved_path` (a site file under `@saved/`, or an unknown name directly under `@saved/`).

### How an entry looks as a file

An entry's file content is the entry's own value. It is rendered as JSON with 2-space indentation and keys in stored order. Rendering is deterministic, so text an agent copies from `read_file` will match in `edit_file`.

```json
{
  "name": "Jonh Smith",
  "attending": true,
  "guests": 2
}
```

Fields Fernpage owns come back next to the content in `entry` metadata, never inside it. That covers `created_by`, `created_at`, and `updated_at`. Agents never have to send them back. When the owner's agent edits an entry, the entry keeps its original creator, so a visitor can still edit their own RSVP afterwards.

### Settings file

```json
{
  "values": {
    "rsvpDeadline": "2027-05-01",
    "rsvpOpen": true
  },
  "collections": {
    "rsvps":     { "create": "anyone", "update": "creator", "delete": "creator" },
    "checklist": { "create": "owner",  "update": "anyone",  "delete": "owner" }
  }
}
```

- `values` holds the site settings the page reads through the SDK. Only owners can change them.
- `collections` declares each collection and the rules for who can write it. Rule values are `anyone`, `creator`, or `owner`. Owners can always write every entry. The rules decide what visitors can do. A collection must be declared here before it can hold entries.
- Every write to this file is validated as a whole. An invalid file is refused with `invalid_settings`, which names the failing key, and nothing changes. Removing a collection that still has entries is refused with `collection_not_empty`, which reports the entry count. Delete the entries first.

## Shared resource shapes

These are the same normalized shapes the browser app and any future HTTP API use.

```ts
type Workspace = { id: string; name: string; role: "admin" | "member" };

type Site = {
  id: string;                 // 12-char Base58, stable
  workspace_id: string;
  title: string;              // from index.html <title>
  description: string | null; // from index.html <meta name="description">
  favicon_url: string | null; // from index.html <link rel="icon">
  url: string;                // canonical visitor URL; assigned by Fernpage
  app_url: string;            // the site in the browser app
  updated_at: string;         // ISO 8601
};

type FileItem = {
  name: string;               // own leaf segment only
  path: string;               // full product path
  kind: "file" | "directory" | "collection" | "entry" | "settings";
  size: number | null;        // bytes; null for directories/collections
  entry_count?: number;       // collections and the @saved directory
  updated_at: string | null;
  entry?: EntryMeta;          // kind === "entry"
};

type EntryMeta = {
  created_by: "owner" | `visitor:${string}`; // per-site visitor pseudonym
  created_at: string;
  updated_at: string;
};

type Usage = {
  files_bytes: number;  files_limit_bytes: number;
  saved_bytes: number;  saved_limit_bytes: number;
};

type ToolError = { code: ErrorCode; message: string }; // product copy, never raw exceptions
```

## Tools

### `list_workspaces`

> List the workspaces you can create and edit Fernpage sites in.

Arguments: none.

Returns `{ workspaces: Workspace[] }`.

### `list_sites`

> List or find Fernpage sites by title across your workspaces.

```ts
{
  workspace_id?: string;   // limit to one workspace
  query?: string;          // case-insensitive match on title/description
  cursor?: string;         // opaque; default page 50, max 200
}
```

Returns `{ sites: Site[], next_cursor: string | null }`. Sites in Trash are excluded. Several matches for a title are all returned with their IDs. Every other tool takes `site_id`, never a title.

### `get_site`

> Get a Fernpage site's details, saved-data collections, and storage usage.

```ts
{ site_id: string }
```

Returns `{ site: Site, collections: { name: string; entry_count: number; rules: CollectionRules }[], usage: Usage }`.

A site in Trash returns `site_in_trash`, with `purge_after` and the browser-app link where a person can restore it.

### `create_site`

> Create a new Fernpage site in a workspace and publish it from its initial files, including index.html.

```ts
{
  workspace_id: string;
  files: FileInput[];      // 1..50 items; must include "index.html"
}

type FileInput =
  | { path: string; content: string }      // UTF-8 text, ≤ 512 KB each
  | { path: string; source_url: string };  // HTTPS URL Fernpage fetches; any type, ≤ 25 MB
```

- The site goes live at `url` as soon as it is created. There are no title, description, or favicon arguments. Fernpage reads them from `index.html`.
- Files whose path starts with `@saved/` are allowed here, so the settings file can go in up front: `@saved/settings.json`. Entries are added afterwards with `add_saved_entries`.
- Creation succeeds or fails as a whole. If any file fails, no site is created, and the response gives one result per file that says which file failed and why. That way the agent never holds a half-built site it doesn't know about.
- **A retry after a timeout can create a second site.** Check `list_sites` before retrying.

Returns `{ site: Site, files: FileResult[] }`.

### `delete_site`

> Delete a Fernpage site by moving it to Trash, where it is kept for 30 days.

```ts
{ site_id: string }
```

- The site stops being served right away. A person can restore it only from the browser app, so agents have no restore tool. After 30 days it is purged.
- Calling it on a site that is already in Trash returns `already_in_trash`, not an error.

Returns `{ site_id, state: "in_trash" | "already_in_trash", purge_after: string, app_trash_url: string }`.

### `list_files`

> List a Fernpage site's files, saved-data collections, and saved-data entries.

```ts
{
  site_id: string;
  path?: string;           // directory to list; default "" (site root)
  cursor?: string;         // default page 200, max 1000
}
```

- At the site root, the listing is recursive over site files. `@saved/` appears as one `directory` item with its entry count, so a busy RSVP list can't fill the response.
- `path: "@saved/"` lists `settings.json` and every collection with its `entry_count`.
- `path: "@saved/rsvps/"` lists entries, newest first, each with `entry` metadata. Use `created_at` and `created_by` to pick out test entries before launch.

Returns `{ items: FileItem[], next_cursor: string | null }`.

### `search_files`

> Search a Fernpage site's file and saved-data contents for text or a regular expression.

```ts
{
  site_id: string;
  pattern: string;
  regex?: boolean;          // default false (literal)
  case_sensitive?: boolean; // default false
  path?: string;            // limit to a directory or collection, e.g. "@saved/rsvps/"
  cursor?: string;          // default 50 matches, max 200
}
```

Searches text files and saved-data entries, not binary assets. Returns `{ matches: { path, line, column, text }[], next_cursor }`. Each match's `text` is cut to 200 characters. Matches are listed by location: the full `path` is the useful part. This is how an agent finds the misspelled RSVP: search for `Jonh` under `@saved/rsvps/`.

### `read_file`

> Read one file or saved-data entry from a Fernpage site.

```ts
{
  site_id: string;
  path: string;
  offset?: number;  // first line, 1-based; for long text files
  limit?: number;   // max lines; default whole file up to 256 KB
}
```

Returns one of:

```ts
| { path; kind: "file"; content: string; size; updated_at; truncated: boolean; total_lines: number }
| { path; kind: "binary"; media_type: string; size; updated_at; url: string } // no bytes in context
| { path; kind: "entry"; content: string; size; entry: EntryMeta }
| { path; kind: "settings"; content: string; size; updated_at }
```

A read records the revision this connection saw. `write_files` uses that record. See [Concurrent writers](#concurrent-writers).

### `write_files`

> Write files or saved-data entries to a Fernpage site, creating new files or replacing existing ones whole.

```ts
{
  site_id: string;
  files: FileInput[];   // 1..50 items, ≤ 2 MB inline text total per call
}
```

- **Site files:** a path that doesn't exist yet creates the file. An existing path is replaced.
- **Saved-data entries:** only existing entries can be replaced. Writing to an entry path that doesn't exist is refused with `entry_not_found`, which points to `add_saved_entries`. Fernpage mints entry IDs, and a typo in a path must not create a new entry. Entry content is inline JSON only (an object, ≤ 64 KB). `source_url` is refused.
- **Settings:** `@saved/settings.json` is replaced whole and validated (see above).
- **Bytes:** text goes inline in `content`. Images, fonts, and anything over 512 KB go by `source_url`: a public HTTPS URL, or an attachment URL the host documents as fetchable. A local file path or sandbox URI moves no bytes. It is refused with `unsupported_source`, which names the two routes that work. Fernpage never reports a write that did not land.
- Each item lands on its own. A failed item doesn't roll back the ones that succeeded.
- Writing the same content again returns `unchanged`. Retrying is safe.

Returns:

```ts
{
  files: FileResult[];        // one per input, in input order
  site?: Site;                // present when index.html changed: the new title/description/favicon
}

type FileResult =
  | { path: string; status: "created" | "replaced" | "unchanged"; size: number }
  | { path: string; status: "failed"; error: ToolError };
```

### `edit_file`

> Edit one file or saved-data entry on a Fernpage site by replacing exact text, without rewriting the whole file.

```ts
{
  site_id: string;
  path: string;
  edits: {                    // 1..20, applied in order, all or nothing
    old_text: string;         // must match exactly once, unless replace_all
    new_text: string;
    replace_all?: boolean;    // default false
  }[];
}
```

- This is the tool for small changes, such as one CSS rule, a typo in a guest name, or flipping `"rsvpOpen": true` to `false`.
- Edits run against the current stored content in one transaction. `old_text` has to match what is there now, so the edit doesn't need a separate fresh read. If a visitor changed a different field of the same entry in the meantime, the edit still applies and keeps the visitor's change.
- Errors: `edit_no_match` (it reports the line count and that the content may have changed, so re-read) and `edit_ambiguous` (it reports the number of matches and suggests more context or `replace_all`). For entries and settings, the result has to still be valid. Otherwise the edit is refused with `invalid_entry` or `invalid_settings`, and nothing changes.
- Not idempotent. A retry after a success fails with `edit_no_match` and changes nothing. Re-read to confirm.

Returns `{ path, status: "edited", size, site?: Site }`. `site` is included when `index.html` changed.

### `delete_files`

> Delete specific files or saved-data entries from a Fernpage site by exact path.

```ts
{
  site_id: string;
  paths: string[];   // 1..100 exact file or entry paths
}
```

- Only exact paths are accepted. Directory paths, collection paths, and wildcards are refused with `not_a_file`. Deletion is permanent.
- `index.html` can't be deleted, because a site needs it to be published. That refusal is `index_required`, and it points to `delete_site`. `@saved/settings.json` can't be deleted either. Edit it instead.
- Deleting a path that's already gone returns `already_absent`, so a retry is safe.
- Each item has its own result, in input order.

Returns `{ files: ({ path; status: "deleted" | "already_absent" } | { path; status: "failed"; error: ToolError })[] }`.

### `add_saved_entries`

> Add new entries to a saved-data collection on a Fernpage site, such as seeding checklist items.

```ts
{
  site_id: string;
  collection: string;        // declared in @saved/settings.json, e.g. "checklist"
  entries: object[];         // 1..100 JSON objects, each ≤ 64 KB
}
```

- Entries are created with `created_by: "owner"` and server-minted IDs. Open pages see them immediately.
- An undeclared collection is refused with `collection_not_declared`, which points to the `collections` key in settings.
- Each item lands on its own. Results come back in input order.
- **A retry after a timeout can add duplicates.** Check with `list_files` on the collection first.

Returns `{ entries: ({ index: number; status: "added"; path: string; entry: EntryMeta } | { index: number; status: "failed"; error: ToolError })[] }`.

## Concurrent writers

Visitors can be writing saved data while an agent edits it. Owners can also edit files in the browser app.

1. **Every agent write is a per-entry product mutation**, the same one the visitor SDK uses. The reactive database serializes it against visitor writes, and every open page gets the result live. No file-view operation touches more than one entry, except batches, where each item is its own mutation.
2. **Lost updates are guarded on the server, not with a token the agent must carry.** Every `read_file`, `write_files`, `create_site`, and `edit_file` records the revision this agent connection last saw for that path, keyed by OAuth grant, site, and path. Say `write_files` would replace an existing file or entry, and its current revision isn't one this connection saw (for example, a visitor updated the RSVP after the agent read it). Then that item is refused with `stale_read`, which asks for a fresh `read_file`. Creating a new site file needs no read.
3. **`edit_file` checks the current content directly** through its exact match, so it is the safer default for entries visitors can also touch.
4. **Delete wins against a racing visitor.** If a visitor's page writes to an entry the agent just deleted, the visitor gets the SDK's not-found result. Agents should clear test entries before sharing the URL, which is what the brief describes.

## Limits

| Limit | Value |
| --- | --- |
| Inline text per file | 512 KB |
| Fetched file (`source_url`) | 25 MB, HTTPS only, 10 s timeout, ≤ 3 redirects, private/loopback/metadata addresses refused |
| Site files total | 100 MB |
| Saved data total per site | 5 MB |
| One entry | 64 KB JSON object |
| `write_files` / `create_site` batch | 50 files, 2 MB inline total |
| `delete_files` batch | 100 paths |
| `add_saved_entries` batch | 100 entries |

Limits are checked before any bytes move. Usage is recorded only after a write lands, using the measured stored size. Hitting a limit returns `quota_exceeded`, which gives the measured usage and the limit (for example "saved data is 4.9 MB of 5 MB, and this entry needs 120 KB"), never the rejected content. A separate hidden ceiling and edge rate limiting apply to every account.

## Error codes

`not_found`, `forbidden`, `site_in_trash`, `invalid_path`, `reserved_path`, `not_a_file`, `index_required`, `entry_not_found`, `collection_not_declared`, `collection_not_empty`, `invalid_entry`, `invalid_settings`, `edit_no_match`, `edit_ambiguous`, `stale_read`, `unsupported_source`, `fetch_failed`, `too_large`, `quota_exceeded`, `rate_limited`, `internal`.

Messages are product copy. Each names what was measured and what to do next. Raw database, storage, or fetch errors stay in internal logs. An authorization failure fails the whole call only if nothing has landed yet. After anything has landed, it is reported per item.

## Typical flows

- **Build a site:** `list_workspaces` → `create_site` with `index.html`, `site.css`, `app.js`, `@saved/settings.json` → `add_saved_entries` to seed the checklist.
- **Small change:** `search_files` or `read_file` → `edit_file`.
- **Fix an RSVP name:** `search_files` with `pattern: "Jonh"` and `path: "@saved/rsvps/"` → `edit_file` on the matched entry.
- **Clear test entries before launch:** `list_files` with `path: "@saved/rsvps/"` → choose by `created_at` / `created_by` → `delete_files`.
- **Change a setting:** `edit_file` on `@saved/settings.json`.
- **Remove a file / the site:** `delete_files` / `delete_site`.

## Assumptions

Calls I made that the brief doesn't settle:

1. **Saved data is shown as files under a reserved `@saved/` directory** rather than a second set of record tools. I chose `@` so it can't clash with ordinary site folders such as `data/`. Site files can't use that prefix.
2. **"Site settings" are a single saved-data file** that holds both the setting values the page reads and the per-collection write rules. The brief says rules live in a site's settings and lists settings as saved data, so I treated them as one thing.
3. **Collections must be declared in settings before they hold entries.** This puts every collection's rules in one place.
4. **Owners can always write every entry. Rules only govern visitors.** An agent acts as the person who connected it, and any workspace member counts as an owner of that workspace's sites. Finer roles could come later in the product's own permission check.
5. **Entry IDs are minted by the server**, and entries are created only through `add_saved_entries`. Replacing an entry never creates one.
6. **Changes publish immediately.** The brief has no draft or preview step.
7. **Deleting a file or entry is permanent.** Only whole sites go to Trash, as the brief says. I assumed there is no file history.
8. **`index.html` can't be deleted on its own**, because the site's title and published state depend on it.
9. **Agent grants cover the whole account** (every workspace the user belongs to), and the target workspace is checked on every call.
10. **Fernpage assigns the site URL.** Agents can't choose a URL name. User HTML is served from a separate registrable domain, one subdomain per site, which the repo's hosting guidance calls for. That's outside this catalog.
11. **The numbers in Limits are placeholders** I picked to match "a few kilobytes to a few megabytes". Saved data is capped at 5 MB per site.
12. **No move/rename tool.** An agent writes the new path and then deletes the old one.
13. **No idempotency keys on `create_site` or `add_saved_entries`.** A duplicate is visible and cheap to undo. The descriptions say a retry can duplicate and name the read that checks.

## Open questions

- Should agents be able to choose a site's address, for example a readable name for a wedding page?
- Should visitors' SDK be able to read the `collections` rules, or only `values`?
- Is a preview/draft state wanted before a site's changes go live?
- Should file deletes and saved-data deletes keep a short undo history like Trash does for sites?
- Should collections get an optional field schema so `invalid_entry` can catch shape mistakes, not just non-objects and size?

````

> Result: File created successfully at: <run>\builds\2-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `<run>\builds\2-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md`

Replaced:

````text
type Usage = {
````

With:

````text
type Rule = "anyone" | "creator" | "owner";
type CollectionRules = { create: Rule; update: Rule; delete: Rule };

type Usage = {
````

> Result: The file <run>\builds\2-file-catalog-with-saved-data-new-opus\work\docs\mcp-tools.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** I've written the tool catalog to `docs/mcp-tools.md`. Nothing is committed.

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

**Session ended:** success, 11 turns, 235507 ms
