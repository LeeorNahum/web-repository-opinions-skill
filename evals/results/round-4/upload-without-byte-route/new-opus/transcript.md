**Prompt:** Bug reports 412, 418, and 421 in docs/issues.md are all about getting images into Kitepost from agents. Work out how files should get into Kitepost from the MCP server, the HTTP API, and the CLI, write the design to docs/upload-design.md, and change packages/mcp/src/tools/upload-image.ts to match it. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "git ls-files && cat docs/brief.md docs/issues.md && cat packages/mcp/src/tools/upload-image.ts"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6918 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references && cat uploads.md model-context-protocol.md agent-tool-design.md; cd ../../../..; cat packages/mcp/src/product.ts packages/mcp/src/storage.ts packages/mcp/package.json package.json"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 15301 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references && cat http-apis.md abuse-resistance.md object-storage.md quota.md user-facing-errors.md modularity.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 17641 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/4-upload-without-byte-route-new-opus/work && cat pnpm-workspace.yaml; ls node_modules 2>/dev/null | head"}`

> Result: packages:   - "apps/*"   - "packages/*"

**Assistant:** Now the design doc.

**Tool call `Write`:** `<run>\builds\4-upload-without-byte-route-new-opus\work\docs\upload-design.md`

````text
# Getting images into Kitepost

Status: proposed, 2026-10-19. Covers bug reports 412, 418, and 421 in `docs/issues.md`.

## What went wrong

The MCP tool `upload_image` took a `path` and called `readFile` on it. That has three problems:

1. **The path names a file the server can't see.** `/mnt/data/photo.jpg` (412) is in the chat host's sandbox, and `sandbox:/workspace/out/chart.png` (418) is in the coding agent's sandbox. The remote MCP server at `mcp.kitepost.example` runs somewhere else. A path or sandbox URI identifies a file to the caller only. It doesn't move any bytes.
2. **It claimed success when nothing was uploaded.** When the read failed, the tool stored a 0-byte buffer, created an image row, and returned `Uploaded photo.jpg`. Users saw a broken image on the board and a success message in the transcript.
3. **It read the server's own disk.** If a path did exist on the MCP host, the tool would have put that server file on the user's board, so any caller could read arbitrary files. It also skipped type checks, the 20 MB limit, and quota, and it wrote bytes before any record of them existed.

The rule from here on: **every caller uses a route that really moves bytes from where it runs.** If a caller has no such route, Kitepost refuses and names the routes that work. It never reports an upload that didn't land.

## One product capability, three adapters

Every surface goes through the same product API and the same authorization (brief, "Decided"). Uploading is one product capability with two ways in. Both end in the same finalize step.

### Product capability (`images` in the product API)

**Direct upload (caller holds the bytes):**

1. `images.beginUpload({ userId, boardId, filename, contentType, size })`
   - Checks the user can edit the board, the type is PNG/JPEG/WebP/GIF, and `size` ≤ 20 MB.
   - Atomically reserves `size` against the account's storage allowance (2 GB on free), counting reservations that are already open. Reservations expire after 15 minutes.
   - Writes a pending upload record and an object-write ledger entry for a fresh opaque key **before** any byte moves.
   - Returns `{ uploadId, putUrl, headers, expiresAt }`. `putUrl` is a single signed PUT bound to the key, content type, and content length. It expires no later than the reservation does. Multipart isn't needed at a 20 MB cap.
2. The caller PUTs the bytes straight to object storage.
3. `images.completeUpload({ userId, uploadId })` runs **finalize** (below).

**URL import (Kitepost fetches the bytes):**

`images.importFromUrl({ userId, boardId, url, filename? })` does the same checks, reservation, and ledger registration, then fetches the URL from the server. The fetch is hardened like every server-side fetch of a URL a caller supplies:
- Only `https:` URLs.
- Every host is resolved, and loopback, private, link-local, and cloud metadata addresses are refused. Kitepost connects only to the address that passed the check.
- At most 3 redirects, with every hop checked again.
- 20-second timeout. The body is streamed with a hard cap at 20 MB, and the fetch aborts once the cap is passed.
- The type is detected from the bytes received (magic bytes), not from `Content-Type` or the extension.

It then runs finalize.

**Finalize (shared by both routes, idempotent per upload):**
- Measures the stored object. If it's empty, larger than declared/reserved, or larger than 20 MB, the upload is refused.
- Sniffs the stored bytes and refuses anything that isn't PNG/JPEG/WebP/GIF.
- Creates the image row. It charges the measured size against the allowance **once**, releases the rest of the reservation, and returns the shared `Image` resource. Repeating finalize returns the first result.
- Bytes are stored exactly as uploaded and never recompressed (brief, "Decided").

Results are typed outcomes, not exceptions: `added`, or a refusal with a reason from `forbidden | board_not_found | unsupported_type | too_large | empty | quota_exceeded | url_not_allowed | fetch_failed | fetch_timeout`. A refusal includes the measured number when there is one, such as the size or the bytes remaining. Each surface turns these into its own Kitepost-written wording. Raw provider and exception text goes to logs only.

### Browser app

No change. Drag and drop already does sign → direct PUT → finalize. It moves onto `beginUpload`/`completeUpload` so it shares the same finalize.

### HTTP API (`api.kitepost.example/v1`, personal API keys)

| Step | Endpoint |
| --- | --- |
| Begin a direct upload | `POST /v1/boards/{board_id}/uploads` with `{ filename, content_type, size }` → `201 { upload_id, put_url, headers, expires_at }` |
| Send bytes | `PUT {put_url}` straight to object storage, with the returned headers |
| Finish | `POST /v1/uploads/{upload_id}/complete` → `201 Image` (repeat calls return the same `Image`) |
| Import from a URL | `POST /v1/boards/{board_id}/images` with `{ source_url, filename? }` → `201 Image` |

- File bytes are never base64-encoded into JSON. Files never pass through an API server route either.
- `201` means the image is on the board. URL import is synchronous because it's capped at 20 MB and a 20-second fetch. If that ever stops fitting the request budget, the endpoint switches to `202` with a job, and clients must poll the job before reporting success.
- Documented in the OpenAPI contract, with the same `Image` schema the MCP tool returns.

### CLI (`npx kitepost`)

- `kitepost upload <board_id> <file...>` reads local files and runs begin → PUT → complete for each one. It prints one line per file, in input order, showing that file's outcome. One file failing doesn't stop the others. The exit code is non-zero if any file failed.
- `kitepost upload <board_id> <https-url>` calls URL import, so nothing is downloaded locally.
- Auth: `KITEPOST_API_KEY` or `kitepost login`. The same commands work on a laptop, in CI, and **inside an agent sandbox that has a shell and network access**. That's the route for 418.

### MCP server (`mcp.kitepost.example/mcp`)

`upload_image { board_id, url, filename? }`

- `url` must be an `https://` URL that Kitepost can fetch. The tool calls `images.importFromUrl`, so it gets the same hardening and finalize.
- The tool **refuses before doing anything** if `url` is a local path (`/mnt/data/...`, `C:\...`, `~/...`), a sandbox or file URI (`sandbox:`, `file:`), or a `data:`/base64 payload. The refusal says the server can't see the caller's files and names the routes that work:
  1. pass a public or pre-signed HTTPS URL to the image;
  2. if the agent can run shell commands with network access, run `npx kitepost upload <board_id> <file>` (or use the HTTP API's direct upload);
  3. otherwise, the user can drag the file onto the board in the browser app.
- It returns the created `Image` (id, board id, filename, content type, size) only after finalize succeeds. It never reports a fake success again.
- Annotations: not read-only, not destructive (it only adds), **not idempotent** (calling again adds a second image, which the description says), open-world (it fetches an external URL).
- There's no separate tool for upload staging. Signed PUT URLs belong to the HTTP API and CLI, which can really send bytes. A chat model can't.

## Decisions on each report

- **412 (chat attachment path):** The tool now refuses a sandbox path with a clear error instead of making a broken image. It doesn't yet fix the underlying need, which is an attachment in a chat app. That needs a host-specific attachment adapter at the MCP boundary: code that turns a host's attachment reference into a URL Kitepost can fetch, for a host whose documentation says such references can be fetched. No adapter exists yet. The tool funnels every input through one `resolveSource` step so adapters can plug in there later without changing the product capability.
- **418 (coding agent sandbox):** Fixed by the routes above. If the sandbox has network access, the agent uses the CLI or HTTP API with an API key. If the chart is hosted somewhere, it passes the URL.
- **421 (base64 in the MCP tool): declined.** A model writes base64 out token by token. A 6 MB photo is about 8 MB of base64, millions of tokens. That's slow and expensive, and it overflows the context window, which is exactly what the teammate hit. Images aren't small text, so they don't qualify for an inline payload under any reasonable cap. The tool refuses `data:` URLs and points the agent at the routes above.

## Assumptions (to confirm)

1. **No host attachment adapter for now.** I haven't confirmed which chat hosts expose attachments as references Kitepost can fetch. Until we confirm one from its own documentation, chat attachments (412) can't be uploaded through MCP. Users get a clear refusal and the browser fallback. **Needs the owner's call:** which hosts matter most, so we can build adapters for them.
2. **Sandbox agents need an API key for the CLI route.** The MCP OAuth token isn't handed to the sandbox. The user (or the agent's environment) provides `KITEPOST_API_KEY`. Minting short-lived, board-scoped upload keys from the MCP session would be smoother, but it's a new credential type. Left for later.
3. **URL import is synchronous**, with a 20-second fetch timeout and at most 3 redirects. Those are my numbers, not the brief's.
4. **Upload reservations and signed PUT URLs expire after 15 minutes.** Also my number.
5. **No `caption` argument yet.** Captions stay a separate edit. Adding an optional `caption` later is additive.
6. **The tool's `{ ok: false, error }` result is shown as a tool error** (`isError: true`) by the MCP server wrapper that registers tools. That wrapper isn't in this repo.
7. **Product API stubs.** `packages/mcp/src/product.ts` gains `importFromUrl` alongside the existing stubs. Those stubs are wired to the product API at runtime. The real fetch hardening, ledger, quota, and finalize live in the product API, which isn't in this repo yet. The old `allocateKey`/`create` pair and `storage.put` are no longer used by the tool. I kept them because I can't see whether anything else uses them.

````

> Result: File created successfully at: <run>\builds\4-upload-without-byte-route-new-opus\work\docs\upload-design.md (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cat > packages/mcp/src/product.ts <<'EOF'\nexport type Image = {\n  id: string;\n  boardId: string;\n  filename: string;\n  contentType: \"image/png\" | \"image/jpeg\" | \"image/webp\" | \"image/gif\";\n  size: number;\n};\n\nexport type ImageRefusalReason =\n  | \"forbidden\"\n  | \"board_not_found\"\n  | \"unsupported_type\"\n  | \"too_large\"\n  | \"empty\"\n  | \"quota_exceeded\"\ [... 5889 more characters]`

> Result: warning: in the working copy of 'packages/mcp/src/product.ts', LF will be replaced by CRLF the next time Git touches it warning: in the working copy of 'packages/mcp/src/tools/upload-image.ts', LF will be replaced by CRLF the next time Git touches it  packages/mcp/src/product.ts            |  36 +++++++++++  packages/mcp/src/tools/upload-image.ts | 110 +++++++++++++++++++++++++++++----  2 files ch [... 41 more characters]

**Assistant:** Small fix: `sandbox:` and `file:` URIs should get the "local file" refusal, not the "wrong scheme" one.

**Tool call `Edit`:** `<run>\builds\4-upload-without-byte-route-new-opus\work\packages\mcp\src\tools\upload-image.ts`

Replaced:

````text
  // A Windows drive path like C:\x parses as a URL with a one-letter scheme.
  if (!parsed || /^[a-z]:$/i.test(parsed.protocol)) {
````

With:

````text
  // A Windows drive path like C:\x parses as a URL with a one-letter scheme.
  if (!parsed || /^([a-z]|sandbox|file):$/i.test(parsed.protocol)) {
````

> Result: The file <run>\builds\4-upload-without-byte-route-new-opus\work\packages\mcp\src\tools\upload-image.ts has been updated successfully.

**Tool call `Bash`:** `{"command": "node -e '\nfor (const v of [\"/mnt/data/photo.jpg\",\"sandbox:/workspace/out/chart.png\",\"C:\\\\x\\\\a.png\",\"~/a.png\",\"file:///a.png\",\"http://x/a.png\",\"data:image/png;base64,AA\",\"https://x.example/a.png\"]) {\n let p; try { p = new URL(v) } catch {}\n const local = !p || /^([a-z]|sandbox|file):$/i.test(p.protocol);\n console.log(v, /^data:/i.test(v) ? \"inline\" : local ? \ [... 64 more characters]`

> Result: Exit code 1 [eval]:2 for (const v of ["/mnt/data/photo.jpg","sandbox:/workspace/out/chart.png","C:\x\a.png","~/a.png","file:///a.png","http://x/a.png","data:image/png;base64,AA","https://x.example/a.png"]) {                                                                              ^^^^ Expected unicode escape  SyntaxError: Invalid hexadecimal escape sequence     at makeContextifyScript (n [... 214 more characters]

**Tool call `Bash`:** `{"command": "node -e '\nfor (const v of [\"/mnt/data/photo.jpg\",\"sandbox:/workspace/out/chart.png\",\"C:\"+String.fromCharCode(92)+\"a.png\",\"~/a.png\",\"file:///a.png\",\"http://x/a.png\",\"data:image/png;base64,AA\",\"https://x.example/a.png\"]) {\n let p; try { p = new URL(v) } catch {}\n const local = !p || /^([a-z]|sandbox|file):$/i.test(p.protocol);\n console.log(v, /^data:/i.test(v) ? \" [... 84 more characters]`

> Result: /mnt/data/photo.jpg local sandbox:/workspace/out/chart.png local C:\a.png local ~/a.png local file:///a.png local http://x/a.png scheme data:image/png;base64,AA inline https://x.example/a.png ok

**Assistant:** I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. I didn't type-check anything: the repo has no installed dependencies or TypeScript config. I only ran a quick Node script to check the input sorting (results below). Nothing is committed.

## Why the bugs happened
The old tool ran `readFile` on the MCP server's own disk. The paths in 412 (`/mnt/data/...`) and 418 (`sandbox:/...`) only exist inside the caller's sandbox, so the read failed. The tool then stored an empty file and still reported success. It also skipped the type, size and quota checks. And it was a security hole: any caller could put a file from the server's disk onto a board.

## The design
Everything goes through two shared steps in the product API: a direct upload with a signed PUT, and a server-side fetch from a URL. Both end in the same finalize. Finalize checks the actual stored size and file type, charges storage once, and returns the image only after it really exists.

- **HTTP API:**
  - Start an upload with `POST /v1/boards/{id}/uploads`, which returns a signed PUT URL.
  - Send the bytes straight to storage with that PUT.
  - Finish with `POST /v1/uploads/{id}/complete`.
  - Import from a link with `POST /v1/boards/{id}/images {source_url}`.
  - Files are never base64-encoded into JSON.
- **CLI:** `kitepost upload <board_id> <file|url...>` uses those routes and reports each file separately. It also works inside an agent's sandbox if it has network access, which is the route for 418.
- **MCP:** `upload_image { board_id, url, filename? }` takes only `https://` URLs. Kitepost downloads the image itself, with the usual protections for fetching a URL someone hands us. Local paths, `sandbox:`/`file:` URIs and `data:`/base64 input are refused before anything happens. The error says why and lists what works instead: a URL, the CLI, or dragging the file into the browser app. A refusal never claims success. Tested inputs: `/mnt/data/photo.jpg`, `sandbox:/...`, `C:\...`, `~/...`, `file:` and `data:` are refused, `http:` gets a "wrong scheme" refusal, and `https:` goes through.

## What happens to each report
- **412:** The broken-image-plus-success-message bug is fixed. But chat attachments still can't reach Kitepost through MCP. That needs an adapter per chat host that turns its attachment into a URL we can fetch, and I haven't confirmed which hosts allow that. The tool has one place where such adapters can plug in.
- **418:** Fixed. The agent uses the CLI or HTTP API from its sandbox, or passes a URL.
- **421:** Declined. A 6 MB photo becomes about 8 MB of base64, which the model would have to write out token by token. That's how the teammate ran out of context.

## Assumptions to confirm
- **Chat attachments (412):** no adapter for any chat host yet. Which hosts matter most is your call.
- **API key in sandboxes:** agents using the CLI need a `KITEPOST_API_KEY`, because the MCP login isn't passed into the sandbox. Short-lived upload keys issued through MCP would be smoother but are deferred.
- **Numbers I picked (not in the brief):** URL import waits for the download to finish, with a 20-second timeout and up to 3 redirects. Upload slots and signed URLs expire after 15 minutes.
- **No `caption` argument** on the tool for now. Adding one later won't break anything.
- **MCP wrapper:** I assumed the code that registers tools (not in this repo) shows the tool's `{ ok: false, error }` result as a tool error.
- **`product.ts`:** I added `importFromUrl` and the result types there, alongside the existing placeholders. The real fetching, quota and finalize logic belongs in the product API, which isn't in this repo yet. The tool no longer calls `allocateKey`, `create` or `storage.put`, but I left them in place in case something else uses them.

**Session ended:** success, 12 turns, 122894 ms
