**Prompt:** Bug reports 412, 418, and 421 in docs/issues.md are all about getting images into Kitepost from agents. Work out how files should get into Kitepost from the MCP server, the HTTP API, and the CLI, write the design to docs/upload-design.md, and change packages/mcp/src/tools/upload-image.ts to match it. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "git ls-files && cat docs/brief.md docs/issues.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6127 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references; cat uploads.md model-context-protocol.md agent-tool-design.md; cd ../../../..; cat packages/mcp/package.json packages/mcp/src/*.ts packages/mcp/src/tools/upload-image.ts package.json pnpm-workspace.yaml"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 16132 more characters]

**Tool call `Bash`:** `{"command": "cd .claude/skills/web-repository-opinions/references; cat abuse-resistance.md http-apis.md quota.md object-storage.md user-facing-errors.md"}`

> Result: # Abuse Resistance  A product reachable from the open internet is a target on day one. Bound what a single caller can cost the product before finding out the hard way.  ## Quota As Anti-Abuse Plumbing  Hold two different numbers, not one. A hidden internal quota, sized to the max load the product can absorb, applies to every account regardless of plan and stays invisible. A user-facing plan  [... 14077 more characters]

**Tool call `Bash`:** `{"command": "cd <run>/builds/4-upload-without-byte-route-new-opus2/work && cat .claude/skills/web-repository-opinions/references/failure-and-retries.md | head -40; git log --stat -3 | head -30"}`

> Result: # Failure And Retries  `failed` alone is not enough. Keep the user-facing status simple, but store the failure kind internally so the right recovery is offered.  ```text failed + upload failed + media_missing failed + quota_exceeded failed + processing failed + abandoned ```  Choose the recovery from the kind:  - Retry processing when the source media still exists - Ask the user to  [... 2719 more characters]

**Assistant:** Now the design doc.

**Tool call `Write`:** `<run>\builds\4-upload-without-byte-route-new-opus2\work\docs\upload-design.md`

````text
# Getting images into Kitepost

Status: proposed, 2026-10-19. Covers bug reports 412, 418, and 421 in `docs/issues.md`. Assumptions made while the owner was away are listed at the end.

## What went wrong

`upload_image` on the MCP server took a `path` and called `readFile` on it. The MCP server is remote (`mcp.kitepost.example/mcp`). It runs on our infrastructure, not where the agent runs. `/mnt/data/photo.jpg` (412) and `sandbox:/workspace/out/chart.png` (418) name files that only the agent's host can see. The read failed, the tool swallowed the failure and stored an empty buffer, recorded a zero-byte image, and reported "Uploaded photo.jpg". So each report has two bugs:

1. **Wrong route.** A path moves no bytes. A remote server cannot read a caller's filesystem.
2. **False success.** The tool reported an upload that never landed, skipped type and size validation, and skipped quota.

Base64 (421) is a real route in principle, but not for images. The model has to generate every base64 token of the image. A 6 MB photo is about 8 MB of base64, which is millions of tokens. That is slow and expensive, and it overflows the context window, which is exactly what the teammate hit.

## Principle

Each caller uses the route that actually moves bytes from where it runs. Every route goes through the same product capability, which does authorization, validation, quota, and a durable finalize before an image counts as added (brief: "Every surface goes through the same product API and the same authorization"). Bytes are stored exactly as received and never recompressed.

| Caller | Where the bytes are | Route |
| --- | --- | --- |
| Browser app | User's machine | Signed direct PUT, then finalize. Unchanged. |
| CLI (`npx kitepost`) | Local disk or CI workspace | Same signed direct PUT, then finalize, through the HTTP API |
| Script or integration (HTTP API) | Caller's process | Same signed direct PUT, then finalize. Or import from an HTTPS URL. |
| Remote agent (MCP) | Somewhere on the internet, or in the agent's host | Kitepost fetches an HTTPS URL. A host attachment reference is supported once that host documents it as fetchable. |
| Agent with a shell in a sandbox (418) | Sandbox filesystem | Run the CLI in the sandbox with an API key. The MCP tool's refusal says so. |

No route accepts image bytes as base64 inside JSON.

## Shared product capabilities

These live in the product API. Every surface calls them, and none of them reimplements their rules.

### `uploads.begin(user, board_id, { filename, content_type, size })`

- Authorizes "add image" on the board.
- Rejects `size > 20 MB`, and rejects any declared type other than `image/png`, `image/jpeg`, `image/webp`, or `image/gif`.
- Atomically reserves `size` against the account's storage allowance (2 GB free), counting reservations already open. The reservation expires after 1 hour.
- Creates a `pending` upload row with an opaque storage key. The key is registered in the object-write ledger before any byte moves. The filename is stored as metadata, never in the key.
- Returns `upload_id` and a signed single PUT URL that expires before the reservation does (15 min). The 20 MB cap keeps single PUT sufficient, so there is no multipart.

### `uploads.complete(user, upload_id)`

- Reads the stored object's real size and first bytes.
- Refuses if the size exceeds the declared or reserved size or 20 MB, or if the magic bytes are not PNG, JPEG, WebP, or GIF (the declared content type is not trusted).
- Creates the image on the board, charges the measured size to usage once, releases the rest of the reservation, and marks the upload `complete`. A repeated `complete` returns the same image and charges nothing.
- Returns the shared image resource: `{ id, board_id, url, size, content_type, created_at }`.

### `images.importFromUrl(user, board_id, url)`

Used by MCP, and by the HTTP API for integrations that already hold a URL.

- Requires `https:`.
- Fetch hardening: resolve the host and refuse loopback, private, link-local, and cloud-metadata addresses, then connect only to the address that passed that check. Follow at most 3 redirects and recheck every hop. Use a 30 s total timeout. Stream with a hard cap at 20 MB and abort past it.
- Reserves quota from `Content-Length` when present. Otherwise it reserves 20 MB and settles to the measured size.
- Registers the key in the ledger, stores the bytes as received, validates the magic bytes, then finalizes exactly like `uploads.complete`.
- Returns a typed outcome: `added` with the image resource, or `refused` with one of `invalid_url`, `fetch_failed`, `too_large`, `unsupported_type`, `board_not_found`, `forbidden`, `quota_exceeded`. The raw fetch or provider error is logged and never returned.

Abandoned `pending` uploads expire with their reservation. A scheduled sweep drains their ledger entries and objects by age.

## HTTP API (`api.kitepost.example/v1`)

These are thin adapters over the capabilities above, published in the OpenAPI document.

```text
POST /v1/boards/{board_id}/uploads          { filename, content_type, size }
  201 { upload_id, put_url, put_headers, expires_at }
PUT  <put_url>                              raw bytes (to object storage, not the API)
POST /v1/uploads/{upload_id}/complete
  201 { image }

POST /v1/boards/{board_id}/images:import    { url }
  201 { image } | 4xx { error: { code, message } }
```

Image bytes never travel in a JSON body. Errors use the stable codes listed above.

## CLI (`npx kitepost`)

```text
npx kitepost upload <board_id> <file...>
```

- Reads each local file, sniffs its type, and calls `begin`, then PUT, then `complete` for each file. Authenticates with `KITEPOST_API_KEY`.
- Several files are handled as one loop. Each file gets its own authorization, quota decision, and result. Results print in input order, with failures inline. The exit code is non-zero if any file failed. `--json` prints the image resources.
- Reports a file as added only after `complete` returns the image.
- This is also the answer for agents that have a shell in a sandbox (418): `npx kitepost upload Hq3k9TmPx2Ab out/chart.png`.

## MCP (`mcp.kitepost.example/mcp`)

The tool is `upload_image { board_id, url }`. It is implemented in `packages/mcp/src/tools/upload-image.ts`.

- Takes a board's stable ID and a fetchable HTTPS URL, and calls `images.importFromUrl`.
- The description and schema hints say up front that the URL must be reachable from the internet. They also say that local paths, sandbox paths, `file:` URIs, and base64 or `data:` URLs cannot be read, and point to the CLI for files that exist only where the agent runs.
- Paths, `sandbox:`, `file:`, and `data:` values are refused before any work is done, with an error that names the routes that work. There is no silent empty upload.
- Reports "Added" only when the product returns the created image, and returns the image ID and URL. An unexpected failure is reported as an unknown outcome, with a request to check the board before retrying, because a retry can add a duplicate.
- Annotations: not read-only, not destructive (it only adds), not idempotent, and open-world (it fetches a caller-supplied URL).
- Staging and finalize are not separate MCP tools. They are plumbing that the HTTP API and CLI own.

### Host attachments (412)

Chat hosts that let a user attach a file can sometimes expose it to tools as a fetchable download URL, or as a file reference the host resolves. Support for this is added per host, as an adapter at the MCP protocol boundary that turns the host's reference into a URL for `importFromUrl`. It is added only after we verify that host's documented contract. Until a host is supported, the refusal tells the assistant that Kitepost cannot see its local attachment, and asks for a public HTTPS link or the web app's drag-and-drop instead.

## Answers to the reports

- **412:** Fixed as a false-success bug. A path is now refused with an explanation, instead of a broken image. A real fix for chat attachments depends on host attachment adapters (follow-up).
- **418:** Fixed as a false-success bug. The refusal points the coding agent to `npx kitepost upload`, which works from its sandbox, or to an HTTPS URL if it publishes the file.
- **421:** Declined for images. Base64 through the model is the cause of the context exhaustion, not a fix for it. URL import and the CLI cover the use case.

## Assumptions (to confirm)

1. **MCP `path` argument removed, not kept as an alias.** It never worked for a remote server, so no caller depends on working behavior. Clients with a cached catalog that still send `path` get a "url is required" validation error. If they then put the path in `url`, they get the instructive refusal.
2. **HTTPS only.** Plain `http:` URLs are refused for import.
3. **No small-text inline route.** Kitepost only accepts images, so there is no inline cap for small text anywhere.
4. **URL import is also exposed on the HTTP API**, because it is the same capability and integrations often hold URLs. Drop `images:import` from `/v1` if the owner wants the API to be signed-upload only.
5. **Limits:** 1 h reservation, 15 min signed PUT, 30 s fetch timeout, 3 redirects. These are my picks, not decisions in the brief.
6. **Caption** is not part of upload in any surface yet. The `images.create` stub has no caption field.
7. **No host attachment adapter shipped now.** I did not verify any specific host's attachment contract, so none is implemented.
8. **`images.importFromUrl` is a new product API capability.** It is declared as a stub in `packages/mcp/src/product.ts` alongside the existing stubs. Its implementation (fetch hardening, ledger, quota) belongs in the product API, which is not in this repo. The HTTP API and CLI described here are also not in this repo yet.

````

> Result: File created successfully at: <run>\builds\4-upload-without-byte-route-new-opus2\work\docs\upload-design.md (file state is current in your context — no need to Read it back)

**Assistant:** Now the product stub and the tool.

**Tool call `Bash`:** `{"command": "cat > packages/mcp/src/product.ts <<'EOF'\nexport type Image = {\n  id: string;\n  board_id: string;\n  url: string;\n  size: number;\n  content_type: \"image/png\" | \"image/jpeg\" | \"image/webp\" | \"image/gif\";\n  created_at: string;\n};\n\nexport type ImportRefusal =\n  | \"invalid_url\"\n  | \"fetch_failed\"\n  | \"too_large\"\n  | \"unsupported_type\"\n  | \"board_not_found\"\ [... 5120 more characters]`

> Result:  M packages/mcp/src/product.ts  M packages/mcp/src/tools/upload-image.ts ?? docs/upload-design.md

**Assistant:** I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. Nothing has been typechecked or run: the repo has no tsconfig, no installed dependencies, and the product API behind the tool is still a stub. I haven't committed anything.

## What was causing the bugs
The MCP server is remote, but `upload_image` called `readFile` on whatever path it was given. `/mnt/data/photo.jpg` (412) and `sandbox:/workspace/...` (418) are files only the agent's own environment can see, so the read failed. The tool hid that failure, saved an empty image, and reported "Uploaded". Each report is really two bugs: the wrong way of getting the file in, and a false success message.

## The design
Each surface gets the file in from wherever its caller has it. All of them go through the same product checks: permission, file type (checked from the actual bytes, not the declared type), the 20 MB limit, storage quota, and a final save before anything counts as added. Original bytes are never recompressed.
- **Browser:** unchanged.
- **HTTP API:** the caller asks for an upload and gets a signed URL, sends the bytes straight to storage, then calls a "complete" endpoint that returns the image. There's also an import-from-HTTPS-URL endpoint, which uses the same code as MCP. Image bytes never go inside JSON.
- **CLI:** `npx kitepost upload <board_id> <file...>` uses the same signed upload and reports each file separately. Coding agents that have a shell in a sandbox (418) should use this.
- **MCP:** `upload_image { board_id, url }`. Kitepost downloads the HTTPS URL itself, with protections against URLs that point at internal addresses, a 20 MB cap and a timeout. Local paths, `sandbox:`, `file:` and `data:`/base64 values are refused straight away, with a message pointing to the CLI or the web app. It only reports "Added" once an image actually exists, and returns its ID. If the outcome is unclear, it asks the agent to check the board before retrying, because a retry can add a duplicate.
- **421 (base64):** I declined it for images. A 6 MB photo comes to millions of tokens of base64, and that is what ran the assistant out of context.

To support the new tool, I also added `images.importFromUrl` and its result types as a stub in `packages/mcp/src/product.ts`, next to the existing stubs.

## Calls I made for you to confirm
1. I removed `path` rather than keeping it as an alias. Clients that cached the old tool list will get a "url required" error instead.
2. URL import accepts HTTPS only.
3. I exposed URL import on the HTTP API as well as MCP. Drop it if you want the API to accept signed uploads only.
4. The time limits are my own picks, not from the brief: 1-hour quota reservation, 15-minute signed upload URL, 30-second download timeout, 3 redirects.
5. Uploads don't take a caption on any surface yet.
6. I didn't build support for chat-app attachments. 412's real fix needs one adapter per chat app, and I haven't checked any app's documented attachment format. Until then, those users get a clear refusal instead of a broken image.
7. The product API side (downloading the URL safely, quota, the record of storage writes), the HTTP API endpoints and the CLI command are not in this repo. They are only designed, not built.

**Session ended:** success, 9 turns, 115983 ms
