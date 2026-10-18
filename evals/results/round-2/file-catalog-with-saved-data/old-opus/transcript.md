**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-file-catalog-with-saved-data-old-opus/work\" && git ls-files && cat docs/brief.md", "description": "List repo files and read the brief"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 5643 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat model-context-protocol.md agent-tool-design.md", "description": "Read MCP and tool design references"}`

> Result: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 8261 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat ids.md data-deletion.md live-data.md workspace-tenancy.md bulk-actions.md object-storage.md uploads.md", "description": "Read adjacent references"}`

> Result: # IDs  Two ID families exist, and they never mix: identifiers for entities that appear in URLs, and identifiers for credentials. They have opposite rules because they live in opposite contexts.  ## Entity IDs  For any private app resource that appears in a route: workspaces, the core object, projects, notes, and similar.  - Length: a fixed 12 characters. - Alphabet: Base58, the case-sensi [... 21130 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat data-model.md source-of-truth.md quota.md abuse-resistance.md user-facing-errors.md failure-and-retries.md http-apis.md naming.md agent-skills.md", "description": "Read more adjacent references"}`

> Result: # Data Model  Model entities around the product's core object and the ownership boundary that protects them.  When many users can reference the same object, model the shared object separately from each user's relationship and relationship-owned metadata. Define object deletion independently from relationship deletion.  Value precedence is fixed: user-edited values outrank generated values, a [... 16426 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-file-catalog-with-saved-data-old-opus/work/.claude/skills/web-repository-opinions/references\" && cat domains.md routing.md origins.md modularity.md auth.md | head -300", "description": "Read domains, routing, origins, modularity, auth refs"}`

> Result: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 28399 more characters]

**Tool call `Write`:** `<run>/builds/2-file-catalog-with-saved-data-old-opus/work/docs/mcp-tools.md`

````text
# Fernpage MCP tool catalog

Status: proposal, written from `docs/brief.md` while the owner was away. Where the brief does not decide something, the choice made here is listed under [Assumptions to confirm](#assumptions-to-confirm). If this document and the brief disagree, the brief wins and this document gets fixed.

## Who calls this

A person's AI agent, connected to Fernpage over MCP, builds and maintains that person's sites: it creates a site, writes and edits its files, reads and fixes its saved data, and removes files or whole sites. The agent may be running unattended, so no tool needs a person mid-call, and none takes a "confirm" argument. The host's approval prompt and the server's authorization gate are the controls.

## Server

- Endpoint: `https://mcp.<product domain>/mcp`, a remote MCP server deployed as its own protocol app. The product domain isn't decided yet.
- Auth: standard MCP OAuth. During consent the person picks **one workspace**, and the connection acts in that workspace only. To work in another workspace, the person authorizes again and picks that one.
- Every caller gets the same static catalog. Authorization is checked on every call at the shared product gate, the same one the browser app uses. These tools are thin adapters over product capabilities and don't hold rules of their own.
- Writes from these tools go through the same reactive backend that visitors' browsers use, so every open page of the site updates live when an agent changes saved data.
- The server's MCP `instructions` field carries a short primer: the site model, the runtime SDK snippet, the rules file format, and a link to full docs.

## Conventions

**IDs.** Workspaces and sites are identified by a stable 12-character Base58 `id`. Inside a site, a file's identity is its `path` and a saved-data entry's identity is `collection` + `key`.

**Revisions.** Every file and every saved-data entry carries an opaque `revision` that changes on every write. A tool that changes or removes existing saved data, or removes a file, requires the revision the agent last read. If the item has changed since, the call doesn't overwrite it and returns a `conflict` result with the current item instead. This is how agents and visitors can write at the same moment without overwriting each other's work silently.

**Reads are singular and paginated, and writes can be batched.** List tools page with an opaque `cursor`. Batch writes return one result per input item, in input order, and each result has a `status` that picks a typed variant. One item failing does not undo the others, except where a tool says it is atomic.

**Paths.** Relative, forward slashes, case-sensitive, no leading `/`, no `.` or `..` segments, at most 256 characters. `index.html` is the site root. `fernpage.json` is reserved for the site's settings (see [Saved data](#saved-data-model)) and is never served to visitors.

**Errors.** Errors are typed outcome codes with plain, product-owned text that names what was measured and what to do next, for example: `"oldText" matched 3 places in app.js; include more surrounding text so it matches exactly once.` Raw backend or provider errors are never returned. Shared codes:

| Code | Meaning and next move |
| --- | --- |
| `not_found` | No such site, file, collection, or entry in this workspace. Lists what does exist where that's cheap. |
| `site_in_trash` | The site is in Trash. Gives the browser-app link where the person can restore it. |
| `conflict` | The revision is stale. Returns the current item. Re-read, reapply the change, retry. |
| `invalid_path` | Says which path rule was broken. |
| `reserved_path` | The path is reserved and this tool can't use it. Names the tool that can. |
| `too_large` | Gives the measured size and the limit. |
| `quota_exceeded` | Gives the site's or workspace's usage and limit. Nothing was written. |
| `invalid_settings` | `fernpage.json` didn't validate. Gives the JSON pointer and the reason. |
| `undeclared_collection` | The collection isn't declared in `fernpage.json`. Lists the declared collections. |
| `not_authorized` | The connected person lacks this capability in this workspace. |

**Annotations.** `readOnlyHint`, `destructiveHint`, and `idempotentHint` describe each tool's worst supported effect. `openWorldHint` is false for every tool except `import_file`, which fetches a URL.

## Catalog at a glance

| Tool | Does | Read-only | Destructive |
| --- | --- | --- | --- |
| `get_workspace` | Show the connected workspace and its usage | yes | no |
| `list_sites` | List or search sites in the workspace | yes | no |
| `get_site` | Show one site | yes | no |
| `create_site` | Create and publish a site from files | no | no |
| `delete_site` | Move a site to Trash | no | yes |
| `list_files` | List a site's files | yes | no |
| `read_file` | Read one file | yes | no |
| `write_files` | Create or replace files, atomically | no | yes |
| `edit_file` | Replace one exact span of text in a file | no | yes |
| `import_file` | Fetch a URL into a site file | no | yes |
| `start_file_upload` | Get a signed URL to upload a local asset | no | no |
| `finish_file_upload` | Publish an uploaded asset at its path | no | yes |
| `move_file` | Rename or move a file | no | yes |
| `delete_files` | Remove specific files | no | yes |
| `list_data_collections` | Show saved-data collections, their rules, and sizes | yes | no |
| `list_data_entries` | Page through entries in a collection | yes | no |
| `get_data_entry` | Read one entry | yes | no |
| `add_data_entries` | Add new entries (seed data) | no | no |
| `update_data_entries` | Replace values of existing entries | no | yes |
| `delete_data_entries` | Remove specific entries | no | yes |
| `clear_data_collection` | Remove every entry in one collection | no | yes |

That makes 21 tools. There is deliberately no restore tool, because restoring from Trash happens in the browser app only.

## Shared resource shapes

These shapes are shared with the browser app and any future public API.

```ts
type Workspace = {
  id: string;            // 12-char Base58
  name: string;
  appUrl: string;        // the workspace in the browser app
  usage: { sites: number; storageBytes: number; dataBytes: number };
  limits: { sites: number; storageBytes: number; dataBytesPerSite: number };
};

type Site = {
  id: string;
  workspaceId: string;
  url: string;           // where visitors open it
  appUrl: string;        // the site in the browser app
  title: string | null;        // from index.html <title>
  description: string | null;  // from index.html <meta name="description">
  faviconPath: string | null;  // from index.html <link rel="icon">
  fileCount: number;
  storageBytes: number;
  dataBytes: number;
  createdAt: string;     // ISO 8601
  updatedAt: string;
};

type FileInfo = {
  path: string;
  revision: string;
  contentType: string;
  kind: "text" | "binary";
  sizeBytes: number;
  updatedAt: string;
};

type DataEntry = {
  collection: string;
  key: string;
  value: JsonValue;
  revision: string;
  createdBy: Actor;      // never changes after creation
  updatedBy: Actor;
  createdAt: string;
  updatedAt: string;
};

type Actor =
  | { type: "visitor"; visitorId: string }   // anonymous browser identity from the runtime SDK
  | { type: "owner"; userId: string; viaAgent: boolean };
```

`title`, `description`, and `faviconPath` are derived from `index.html` every time it changes. They aren't stored as separate settings, and no tool sets them. To change them, edit `index.html`.

## Workspace and sites

### `get_workspace`

Show the workspace this connection acts in, with its usage and limits. Takes no arguments. Returns `Workspace`. Read-only.

### `list_sites`

List sites in the workspace, newest first, optionally filtered by text found in the title or URL.

```ts
{ query?: string; cursor?: string; limit?: number /* default 25, max 100 */ }
→ { sites: Site[]; nextCursor: string | null }
```

Excludes sites in Trash. Read-only. This is how an agent turns "my wedding page" into a site `id`. When several sites match, it returns all of them, and the agent picks by `id`.

### `get_site`

Show one site. `{ siteId: string }` → `Site`. Read-only. Returns `site_in_trash` for a trashed site.

### `create_site`

Create a new site in the workspace from an initial set of files and publish it at its own URL.

```ts
{
  files: FileInput[];    // must include "index.html"; max 50 items, 4 MB total
}
→ { site: Site; files: FileInfo[] }

type FileInput =
  | { path: string; text: string }       // HTML, CSS, JS, JSON, SVG, etc.
  | { path: string; base64: string };    // tiny binaries only, max 100 KB each
```

Atomic: either the whole site is created or nothing is. It fails with `index_required` if `index.html` is missing. It always creates a new site and never touches an existing one. Not idempotent: calling it twice creates two sites. Larger assets are added afterwards with `import_file` or the upload pair.

### `delete_site`

Move a site to Trash. It stops being served right away and is permanently removed after 30 days unless the person restores it in the browser app.

```ts
{ siteId: string }
→ { status: "trashed"; siteId: string; purgeAt: string; restoreUrl: string }
```

Takes the stable `id` only, never a name. If the site is already in Trash, it returns the same result again (idempotent). Destructive. The agent should tell the person about `restoreUrl`.

## Files

### `list_files`

List every file in a site with its revision and size. `{ siteId: string }` → `{ files: FileInfo[] }`. Includes `fernpage.json` when present. Read-only. Sites are small, so there's no pagination. A site over 1,000 files returns `too_large` and asks the agent to add a `prefix`.

```ts
{ siteId: string; prefix?: string }
```

### `read_file`

Read one file.

```ts
{ siteId: string; path: string }
→ { file: FileInfo; text: string }                // kind "text"
| { file: FileInfo; url: string }                 // kind "binary": a short-lived URL, not the bytes
```

Text files over 512 KB return `too_large` with the size. Read-only.

### `write_files`

Create or replace whole files in a site. All the given files go live together in one step.

```ts
{ siteId: string; files: FileInput[] /* max 50, 4 MB total */ }
→ { files: Array<{ path: string; status: "created" | "replaced" | "unchanged"; file: FileInfo }> }
```

Atomic. If any item fails validation (a bad path, a size limit, quota, or an invalid `fernpage.json`), nothing is written, and the error names every failing item. It's atomic because a half-applied HTML and JS change breaks a live site. It's destructive because it replaces existing files. It's idempotent because writing the same content twice gives `unchanged`. This tool is the one place where `fernpage.json` is written, and the server validates it before anything lands.

### `edit_file`

Make one small edit to a text file: replace the exact text `oldText` with `newText`.

```ts
{ siteId: string; path: string; oldText: string; newText: string }
→ { file: FileInfo }
```

`oldText` must appear exactly once. Otherwise the call returns `text_not_found` or `text_ambiguous` with the match count. Because the match must be exact, a stale view of the file fails cleanly instead of overwriting newer work. Edits to `index.html` refresh the site's title, description, and favicon. Edits to `fernpage.json` are validated like `write_files`. Destructive.

### `import_file`

Fetch a public URL and store the response as a site file. This is the preferred way to add images and other assets, since it avoids encoding bytes into the call.

```ts
{ siteId: string; path: string; sourceUrl: string /* https only */ }
→ { status: "created" | "replaced"; file: FileInfo }
```

The server fetches with SSRF protections (no private or loopback addresses, a bounded number of redirects), a 25 MB cap, and a content-type allowlist. Replaces an existing file at `path`. Destructive and open-world.

### `start_file_upload` / `finish_file_upload`

These two tools upload a local asset that has no public URL, such as an image on the agent's machine.

```ts
start_file_upload { siteId: string; path: string; contentType: string; sizeBytes: number }
→ { uploadId: string; uploadUrl: string; method: "PUT"; headers: Record<string, string>; expiresAt: string }

finish_file_upload { uploadId: string }
→ { status: "created" | "replaced"; file: FileInfo }
```

`start_file_upload` checks the path, type, size, and quota before any bytes move, and records the pending upload. The agent then PUTs the bytes directly to `uploadUrl`, using a shell or HTTP tool. `finish_file_upload` verifies the bytes landed with the declared size and type, then publishes the file at `path`. Uploads that are never finished expire and are cleaned up. `start_file_upload` doesn't change the site, so it isn't destructive. `finish_file_upload` can replace a file, so it is.

### `move_file`

Rename or move one file.

```ts
{ siteId: string; fromPath: string; toPath: string }
→ { file: FileInfo }   // carries the new path
```

Refuses with `path_taken` if `toPath` exists, so it never overwrites. It doesn't rewrite references in other files: the agent updates those itself, and the tool description says so. Can't move `index.html` or `fernpage.json`. Destructive, because the old path stops resolving.

### `delete_files`

Remove specific files from a site.

```ts
{ siteId: string; files: Array<{ path: string; revision: string }> /* max 50 */ }
→ { results: Array<
    | { path: string; status: "deleted" }
    | { path: string; status: "conflict"; file: FileInfo }
    | { path: string; status: "not_found" }
    | { path: string; status: "refused"; code: "index_required" }
  > }
```

Each file is deleted independently. The required `revision` means the agent deletes the version it actually looked at. `index.html` can't be deleted, because a site without it can't be served. The refusal says to replace it with `write_files` or to remove the whole site with `delete_site`. Deleting `fernpage.json` is allowed and returns the site's saved data to its defaults (see below). Destructive.

## Saved data model

A site's saved data is a small set of **collections**, such as `rsvps`, `checklist`, or `settings`. Each collection holds **entries**, and each entry has a `key` and a JSON `value`. Visitors' browsers read and write entries one at a time through the runtime SDK, and every open page updates live.

Collections and their rules are declared in the site's `fernpage.json`, which sits next to the code that uses them and is written with the same file tools:

```json
{
  "data": {
    "checklist": { "read": "anyone", "create": "owner",  "update": "anyone",  "delete": "owner" },
    "rsvps":     { "read": "owner",  "create": "anyone", "update": "creator", "delete": "creator" },
    "settings":  { "read": "anyone", "create": "owner",  "update": "owner",   "delete": "owner" }
  }
}
```

- Each rule is `"anyone"`, `"creator"` (the visitor who created the entry), or `"owner"`. The site's owner, meaning members of its workspace and their agents, may always do everything, so rules only limit visitors.
- Writes to a collection that isn't declared are refused for both visitors and agents (`undeclared_collection`). A site with no `fernpage.json` has no saved data, which is enough for a site that is only `index.html`.
- Removing a collection from `fernpage.json` stops serving it. Its entries are kept until the agent runs `clear_data_collection` on it, so a typo in the rules file can't wipe data.
- Limits: 64 KB per entry value, 5 MB of saved data per site. Hitting either returns `too_large` or `quota_exceeded` with the measured numbers.

The full rule language belongs in its own spec. This catalog only depends on rules being declared per collection in `fernpage.json`.

### Agents and visitors at the same time

Visitors may be writing while an agent edits. The tools handle that like this:

- Updates and deletes require the entry's `revision`. If a visitor changed the entry after the agent read it, the agent gets `conflict` with the current entry, re-reads it, reapplies its fix, and retries. A visitor's newer RSVP edit is never silently overwritten.
- Adding entries can't conflict with visitors, except when the agent and a visitor pick the same key. That item then gets `key_taken` and its existing value is left alone.
- An agent update keeps `createdBy`, so correcting a misspelled RSVP name leaves the visitor who created it able to edit it.
- Agent writes show up live in every open page, just like visitor writes.

### `list_data_collections`

Show the collections declared for a site, with their rules and how much data each holds.

```ts
{ siteId: string }
→ { collections: Array<{
      name: string;
      declared: boolean;           // false = left over after being removed from fernpage.json
      rules: { read: Rule; create: Rule; update: Rule; delete: Rule } | null;
      entryCount: number;
      dataBytes: number;
    }>;
    dataBytes: number; dataBytesLimit: number }
```

Read-only.

### `list_data_entries`

Page through the entries of one collection, newest first.

```ts
{
  siteId: string;
  collection: string;
  createdBy?: "visitor" | "owner";   // narrow the list, e.g. to find test entries
  cursor?: string;
  limit?: number;                    // default 50, max 200; a page is also capped at 256 KB
}
→ { entries: DataEntry[]; nextCursor: string | null }
```

Read-only. Paging keeps large collections from flooding the agent's context.

### `get_data_entry`

Read one entry. `{ siteId: string; collection: string; key: string }` → `DataEntry`. Read-only.

### `add_data_entries`

Add new entries to a collection, for example to seed a checklist or a settings entry before launch.

```ts
{
  siteId: string;
  collection: string;
  entries: Array<{ key?: string; value: JsonValue }>;   // max 100; omitted key → server-generated
}
→ { results: Array<
    | { index: number; status: "added"; entry: DataEntry }
    | { index: number; status: "key_taken"; entry: DataEntry }
    | { index: number; status: "failed"; code: "too_large" | "quota_exceeded" }
  > }
```

Only ever adds. It never changes an existing entry, which is why it isn't destructive. Each item gets its own result, and results come back in input order. The entries are created as `{ type: "owner", viaAgent: true }`. Not idempotent when keys are left out, so agents should give keys for seed data they might re-run, such as `item-1`, `item-2`, or `main`.

### `update_data_entries`

Replace the value of existing entries, for example to fix a misspelled RSVP name or change a setting.

```ts
{
  siteId: string;
  collection: string;
  updates: Array<{ key: string; revision: string; value: JsonValue }>;   // max 100
}
→ { results: Array<
    | { key: string; status: "updated"; entry: DataEntry }
    | { key: string; status: "unchanged"; entry: DataEntry }
    | { key: string; status: "conflict"; entry: DataEntry }   // current entry, not changed
    | { key: string; status: "not_found" }
    | { key: string; status: "failed"; code: "too_large" | "quota_exceeded" }
  > }
```

Never creates an entry, so a mistyped key returns `not_found` rather than a new entry. Each update replaces the whole `value`, and the required revision is what keeps that safe. Destructive.

### `delete_data_entries`

Remove specific entries, for example the test RSVPs found with `list_data_entries`.

```ts
{
  siteId: string;
  collection: string;
  entries: Array<{ key: string; revision: string }>;   // max 100
}
→ { results: Array<
    | { key: string; status: "deleted" }
    | { key: string; status: "conflict"; entry: DataEntry }
    | { key: string; status: "not_found" }
  > }
```

Each entry is deleted independently, and only if it's unchanged since the agent read it. Removing an entry that's already gone returns `not_found`, which the agent can treat as done. Destructive.

### `clear_data_collection`

Remove every entry in one collection, for example to clear all test RSVPs right before launch.

```ts
{ siteId: string; collection: string }
→ { status: "cleared"; collection: string; deletedCount: number; cutoff: string }
```

Deletes every entry that existed when the call started (`cutoff`). Entries that visitors write while it runs survive, and the agent can check for them with `list_data_entries`. Both arguments are required. There's no "all collections" form, and to empty several collections the agent calls the tool once for each. It also works on collections no longer declared in `fernpage.json`, which is how leftover data gets removed. Runs to completion within the call, which the per-site data limit makes feasible. Destructive. Idempotent: clearing an empty collection returns `deletedCount: 0`.

## Typical flows

- **New site:** `create_site` with `index.html` (and `fernpage.json` plus CSS and JS if the site saves data), then `add_data_entries` to seed. Then give the person `site.url`.
- **Small change:** `list_sites` → `read_file` → `edit_file`.
- **Fix an RSVP name:** `list_data_entries` (`collection: "rsvps"`) → `update_data_entries` with the entry's `revision`. On `conflict`, reapply the fix to the returned entry and retry.
- **Clear test entries before launch:** `clear_data_collection` if everything goes. Otherwise `list_data_entries` with `createdBy: "owner"` (or by inspecting values), then `delete_data_entries`.
- **Add a new saved-data feature:** `write_files` with the updated `fernpage.json` and the JS that uses the new collection in one atomic call, so the rules and the code go live together.
- **Remove a site:** `list_sites` → confirm the right `id` with the person when the request is ambiguous → `delete_site` → pass on `restoreUrl`.

## Assumptions to confirm

These are the calls I made where the brief doesn't decide. Each one is easy to change before implementation.

1. **The rules live in a reserved `fernpage.json` file**, not in a separate settings store, and that file also declares the collections. Reason: agents already write files, the rules get deployed atomically with the code that depends on them, and the server can validate them on write. The brief says rules live in the site's "settings". If that means a separate settings record, replace the file with a `get_site_settings` / `update_site_settings` pair and keep everything else.
2. **"Site settings" saved data is just a collection**, such as `settings` with a `main` entry. It isn't a separate concept.
3. **Rules use three levels: `anyone`, `creator`, `owner`.** The owner and their agents bypass rules. Undeclared collections are closed. A site with no `fernpage.json` has no saved data.
4. **Each connection acts in one workspace, chosen at OAuth consent**, so no tool takes a `workspaceId`. If the owner wants one connection to span every workspace, add `list_workspaces` and a required `workspaceId` on `create_site` and `list_sites`.
5. **Files go live as soon as they're written.** There's no draft or publish step, and a site is live once `index.html` exists. `write_files` and `create_site` are atomic so that multi-file changes go live together. If there should be drafts or previews, that's a new `publish_site` tool and a change in what "live" means.
6. **`index.html` can't be deleted or moved.** Taking a site offline is done with `delete_site`.
7. **Agents don't choose a site's address.** The server assigns `url`, and it lives on a domain separate from the product so that user JavaScript never shares an origin with the app. Custom addresses, slugs, and custom domains are out of scope here, and a later rename tool would return the new `url`.
8. **No tool restores from Trash, lists Trash, or deletes permanently.** Restoring is browser-only, as decided, and permanent deletion only happens when the 30 days run out.
9. **The numbers are placeholders:** 50 files / 4 MB per write, 100 KB inline binary, 25 MB import or upload, 512 KB text read, 64 KB per entry, 5 MB saved data per site, 100 items per data batch, 200 entries per page. They should be set from real hosting and backend limits.
10. **Visitor identity** is an anonymous ID the runtime SDK keeps in the visitor's browser. That's what `creator` rules and `createdBy` refer to. Clearing the browser loses edit rights over your own RSVP, but the owner can still fix it.
11. **No data history or undo** in this version. Revisions are only used for concurrency checks. If agents should be able to undo a bad data fix, add per-entry history and a read tool for it.

````

> Result: File created successfully at: <run>/builds/2-file-catalog-with-saved-data-old-opus/work/docs/mcp-tools.md (file state is current in your context — no need to Read it back)

**Assistant:** Draft written. Next I'm fixing two inconsistencies: `list_files` mentions a `prefix` argument it doesn't declare, and some error codes the tools use are missing from the shared table.

**Tool call `Edit`:** `<run>/builds/2-file-catalog-with-saved-data-old-opus/work/docs/mcp-tools.md`

Replaced:

````text
List every file in a site with its revision and size. `{ siteId: string }` → `{ files: FileInfo[] }`. Includes `fernpage.json` when present. Read-only. Sites are small, so there's no pagination. A site over 1,000 files returns `too_large` and asks the agent to add a `prefix`.

```ts
{ siteId: string; prefix?: string }
```
````

With:

````text
List a site's files with their revisions and sizes.

```ts
{ siteId: string; prefix?: string /* e.g. "images/" */ }
→ { files: FileInfo[] }
```

Includes `fernpage.json` when present. Read-only. Sites are small, so there's no pagination. A listing over 1,000 files returns `too_large` with the count and asks the agent to narrow it with `prefix`.
````

> Result: The file <run>/builds/2-file-catalog-with-saved-data-old-opus/work/docs/mcp-tools.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `<run>/builds/2-file-catalog-with-saved-data-old-opus/work/docs/mcp-tools.md`

Replaced:

````text
| `not_authorized` | The connected person lacks this capability in this workspace. |
````

With:

````text
| `not_authorized` | The connected person lacks this capability in this workspace. |
| `index_required` | The call would leave the site without `index.html`. |
| `text_not_found` / `text_ambiguous` | `edit_file`'s `oldText` matched zero or several places. Gives the count. |
| `path_taken` | `move_file`'s target path already exists. |
| `key_taken` | `add_data_entries` was given a key that already exists. Returns the existing entry. |
````

> Result: The file <run>/builds/2-file-catalog-with-saved-data-old-opus/work/docs/mcp-tools.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** I've written the tool catalog to `docs/mcp-tools.md`. It's a design doc, so nothing is built yet, and it isn't committed.

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

**Session ended:** success, 11 turns, 199351 ms
