**Prompt:** Bug reports 412, 418, and 421 in docs/issues.md are all about getting images into Kitepost from agents. Work out how files should get into Kitepost from the MCP server, the HTTP API, and the CLI, write the design to docs/upload-design.md, and change packages/mcp/src/tools/upload-image.ts to match it. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-upload-without-byte-route-new-opus/work\" && git ls-files && cat docs/brief.md docs/issues.md && cat packages/mcp/src/tools/upload-image.ts"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6918 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-upload-without-byte-route-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/uploads.md $R/model-context-protocol.md $R/agent-tool-design.md; cat packages/mcp/src/product.ts packages/mcp/src/storage.ts packages/mcp/package.json package.json"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 14079 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-upload-without-byte-route-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/abuse-resistance.md $R/http-apis.md $R/quota.md $R/user-facing-errors.md $R/object-storage.md"}`

> Result: # Abuse Resistance  A product reachable from the open internet is a target on day one. Bound what a single caller can cost the product before finding out the hard way.  ## Quota As Anti-Abuse Plumbing  Hold two different numbers, not one. A hidden internal quota, sized to the max load the product can absorb, applies to every account regardless of plan and stays invisible. A user-facing plan  [... 13399 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-upload-without-byte-route-new-opus/work\" && grep -rn \"storage\\|allocateKey\" packages --include=*.ts; git branch -a"}`

> Result: packages/mcp/src/product.ts:2:  /** Returns a fresh opaque storage key for a new image on a board the user can edit. */ packages/mcp/src/product.ts:3:  async allocateKey(userId: string, boardId: string): Promise<string> { packages/mcp/src/storage.ts:1:export const storage = { packages/mcp/src/storage.ts:2:  /** Writes bytes to object storage under an opaque key. */ packages/mcp/src/storage.ts:4:   [... 345 more characters]

**Assistant:** Now the design doc.

**Tool call `Write`:** `<run>\builds\2-upload-without-byte-route-new-opus\work\docs\upload-design.md`

````text
# Getting images into Kitepost

Status: proposed, written 2026-10-18 for bug reports 412, 418, and 421. The owner has not reviewed it yet. Calls made without the owner are listed under [Assumptions](#assumptions-to-confirm).

## What went wrong

The MCP tool `upload_image` took a `path` and called `readFile` on the MCP server. The MCP server runs at `mcp.kitepost.example`, so the file the user meant is never on that machine:

- 412: `/mnt/data/photo.jpg` is a path inside the chat assistant's own sandbox.
- 418: `sandbox:/workspace/out/chart.png` is a URI that only the coding agent's sandbox understands.

The read failed. The tool caught the error, replaced it with an empty buffer, stored a 0-byte object, created an image row, and reported "Uploaded photo.jpg". So there were two bugs:

1. **Wrong route.** A path names a file only the caller can see, and it moves no bytes to a remote server.
2. **Silent failure.** The tool said an upload had landed when it had not. That breaks the brief's rule that every surface goes through the same product API: this tool skipped type checks, size checks, quota, and finalize, and wrote to storage directly.

Request 421 (base64) is answered under [Base64](#base64-request-421).

## Principle

Each caller uses the route that actually moves bytes from where it runs. Every route ends in the same product capability, with the same authorization, type and size checks, quota, and durable finalize. Nothing counts as added until finalize has succeeded.

| Caller | Where the bytes are | Route |
| --- | --- | --- |
| Browser app | User's machine | Signed direct PUT to storage, then finalize (unchanged) |
| HTTP API client, script, integration | Caller's machine | Same staged upload: create upload, PUT bytes to the signed URL, finalize |
| CLI (`npx kitepost`) | Local disk or CI workspace | Same staged upload, run by the CLI for each file |
| Remote MCP agent | Wherever the host keeps them | An HTTPS URL that Kitepost fetches on the server |
| Agent with a shell in a sandbox (coding agents) | Sandbox disk | Run the CLI or the HTTP API from inside the sandbox |

## Shared product capabilities

These live in the product API, and every surface calls them. No surface writes to object storage itself.

### `uploads.create({ boardId, filename, contentType, size })`

1. Authorize: the caller can edit the board.
2. Validate the declared type (PNG, JPEG, WebP, GIF) and size (at most 20 MB, at least 1 byte).
3. Reserve quota atomically against the account's remaining storage (2 GB on the free plan), counting reservations already open. Each reservation expires, so an abandoned upload frees its space by itself.
4. Create the image row with status `pending`. Its storage key is opaque and random and contains no filename. Register the key in the object-write ledger in the same transaction, before any bytes move.
5. Return `{ uploadId, imageId, putUrl, headers, expiresAt }`. `putUrl` is a single signed PUT that is bound to the declared content type and length.

Images are capped at 20 MB, so a single signed PUT is enough. Kitepost does not use multipart upload.

### `uploads.finalize({ uploadId })`

1. HEAD the object and confirm it exists and its size matches the declared size.
2. Read the first bytes and confirm the magic number matches an accepted type. Trust the bytes, not the declared type.
3. Mark the image `ready`, record the measured size, charge quota from that size, and release the reservation.
4. Finalize is idempotent: finalizing a `ready` upload again returns the same image and charges nothing more.

If any check fails, the upload is marked `failed` with a typed reason, the reservation is released, and the object is deleted through the ledger. Pending and failed images never appear on the public share link.

### `images.importFromUrl({ boardId, url })`

This is the server-side fetch that agents use. It sits on the same staging: create the pending row, register the key, fetch the bytes into storage, then finalize. The fetch is hardened:

- HTTPS only.
- The host is resolved, and the fetch is refused if it resolves to a loopback, private, link-local, or cloud-metadata address. The connection goes only to the address that passed the check, so a DNS rebind cannot slip through.
- At most 3 redirects, and every hop is checked the same way.
- The download streams with a 20 MB byte cap and a 30 s total timeout. If `Content-Length` is present, it is checked before the body is read.
- The bytes are sniffed for type. `Content-Type` is never trusted.
- Quota is checked against `Content-Length` when present, and against the measured size before charging.

The original filename is taken from `Content-Disposition` or the last URL segment. It is stored as metadata only. Bytes are stored exactly as received and never recompressed.

All three capabilities return typed outcomes: `added`, `unsupported_type`, `too_large`, `empty_file`, `quota_exceeded`, `board_not_found`, `forbidden`, `url_not_allowed`, `fetch_failed`, `fetch_timeout`. Each surface maps these codes to Kitepost wording. Raw fetch, storage, or provider errors are never shown to users.

## HTTP API (`api.kitepost.example/v1`)

Authenticated with a personal API key. All endpoints go into the OpenAPI document before implementation.

```text
POST /v1/boards/{board_id}/uploads          -> uploads.create
     body: { filename, content_type, size }
     201: { upload_id, image_id, put_url, put_headers, expires_at }

PUT  {put_url}                               (straight to object storage, raw bytes, not JSON)

POST /v1/uploads/{upload_id}/finalize       -> uploads.finalize
     200: { image }  — image has status "ready"

POST /v1/boards/{board_id}/images/import    -> images.importFromUrl
     body: { url }
     201: { image }
```

- File bytes never travel inside JSON. There is no base64 field on any endpoint.
- `201` from create only means the request was accepted. The image is on the board only once finalize returns `200` with `status: "ready"`.
- Errors use the typed codes above with stable HTTP statuses: 400, 403, 404, 413, 415, 422, 507 for quota, and 502/504 for fetch failures.
- Storage CORS stays as the browser flow already needs it. Script and CLI callers are not subject to CORS.

## CLI (`npx kitepost`)

```text
npx kitepost upload <board_id> <file...>
npx kitepost upload <board_id> --url https://example.com/a.png
```

- For each file, the CLI reads it locally, checks its type and the 20 MB limit before contacting the server, then runs create, PUT, and finalize through the HTTP API.
- Uploads run one at a time by default, with a small concurrency option, and each file gets its own result. A failed file does not stop the others. Output is one line per file in input order, plus `--json` for CI. The exit code is non-zero if any file failed.
- The CLI authenticates with `KITEPOST_API_KEY` or a stored login.
- The CLI is a thin client over the HTTP API. Validation is repeated on the client only to fail early. The server stays authoritative.

## MCP (`mcp.kitepost.example/mcp`)

`upload_image` is renamed in its description to say it adds an image from a URL. The tool name stays the same so cached catalogs and existing prompts keep working.

Input:

```text
board_id: string            board to add the image to
url:      string (https)    a URL Kitepost can download the image from
```

Behavior:

- The tool calls `images.importFromUrl`. It does no file I/O and never writes to storage.
- Local paths (`/mnt/data/...`, `C:\...`, `~/...`), `file:`, `sandbox:`, other non-HTTPS schemes, and `data:` URIs are refused before any call is made. The refusal names the routes that work: a public or signed HTTPS URL, or, for an agent with a shell, `npx kitepost upload` or the HTTP API run from the agent's own environment.
- Success is reported only when the product returns an image with status `ready`. The tool then returns the image ID, board ID, size, and type. It returns no other success message.
- Annotations: not read-only, not destructive (it only adds), not idempotent (a retry adds a second copy, and the description says so), open-world (it fetches an external URL).

The description and schema hints tell callers which route to use, so agents choose correctly from the start. The tool is not split into two tools. Staging is plumbing and gets no tool of its own.

### Host attachment references

Some hosts give a chat attachment a fetchable reference, such as a short-lived download URL. Support for each host is a small adapter at the protocol boundary. The adapter turns that host's documented reference into an HTTPS URL for `importFromUrl`. Kitepost adds an adapter only after checking a host's documentation and observing its behavior. None is shipped yet (see assumptions). Until then, an attachment that the host exposes only as a sandbox path gets the refusal described above, never a false success.

### Base64 (request 421)

Declined for images. A model writes base64 one token at a time. A 6 MB photo is about 8 MB of base64, which is millions of tokens, far beyond any context window. That is exactly the failure the teammate hit. Even small images make the call slow and expensive. The tool does not accept inline bytes. Agents that have the file in a sandbox should use the CLI or the HTTP API from there. Agents in a chat app need an attachment the host exposes as a URL.

## Cleanup of existing bad data

Bugs 412 and 418 left image rows that point to 0-byte objects. Proposed one-off job: find images with `size = 0`, remove them and their objects through the ledger, and recompute storage usage for each affected account. The job deletes user-visible rows, so it waits for the owner's go-ahead. It is not done in this change.

## Implemented in this change

- `packages/mcp/src/tools/upload-image.ts` now takes `url`, refuses paths and non-HTTPS input with guidance, calls `images.importFromUrl`, and reports only an image that actually landed.
- `packages/mcp/src/product.ts` declares `images.importFromUrl` and its typed outcome, and the unused `allocateKey` and `create` stubs are removed. The real implementation (fetch hardening, staging, finalize) belongs in the product API, which is not in this repository.
- `packages/mcp/src/storage.ts` is deleted. The MCP server no longer has any route to write bytes into storage.

Not yet built, because the code is not in this repo: the HTTP endpoints, the CLI command, the product-side fetcher and finalize, and the cleanup job.

## Assumptions to confirm

1. **No base64 for images, at any size.** The brief does not decide this. It is my call, based on 421 itself.
2. **The tool name `upload_image` stays and `path` is removed, with no deprecation period.** The `path` field never worked for remote callers, so no caller depends on working behavior. Clients with a cached old schema that still send `path` get a validation error asking for `url`.
3. **Server-side URL fetch is acceptable.** It adds outbound fetching to Kitepost's attack surface, mitigated by the hardening above. The import endpoint is also exposed on the HTTP API, because integrations often have URLs rather than bytes.
4. **Single signed PUT, no multipart**, because of the 20 MB limit. Revisit if the limit grows past about 100 MB.
5. **Fetch limits are 3 redirects and a 30 s timeout.** These are my numbers. The brief does not specify them.
6. **No host attachment adapter ships yet.** I did not verify any host's attachment reference contract, so 412 (a chat attachment) is fixed to fail honestly, not to succeed. Making it succeed needs an adapter for that host.
7. **Pending uploads expire after 1 hour**, and their quota reservation is released at the same time.
8. **Cleaning up the 0-byte images needs the owner's approval** before anything is deleted.

````

> Result: File created successfully at: <run>\builds\2-upload-without-byte-route-new-opus\work\docs\upload-design.md (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>\builds\2-upload-without-byte-route-new-opus\work\packages\mcp\src\product.ts`

````text
export type ImportedImage = {
  id: string;
  boardId: string;
  status: "pending" | "ready" | "failed";
  size: number;
  contentType: string;
  filename: string | null;
};

export type ImportOutcome =
  | { kind: "added"; image: ImportedImage }
  | { kind: "unsupported_type"; detectedType: string | null }
  | { kind: "too_large"; size: number; limit: number }
  | { kind: "empty_file" }
  | { kind: "quota_exceeded"; needed: number; remaining: number }
  | { kind: "board_not_found" }
  | { kind: "forbidden" }
  | { kind: "url_not_allowed" }
  | { kind: "fetch_failed"; status: number | null }
  | { kind: "fetch_timeout" };

export const images = {
  /**
   * Fetches an HTTPS URL on the server (hardened: private-address refusal, bounded redirects,
   * byte cap, timeout, type sniffing), stages it, and finalizes it on a board the user can edit.
   * Returns "added" only once the image is durably ready.
   */
  async importFromUrl(input: { userId: string; boardId: string; url: string }): Promise<ImportOutcome> {
    throw new Error("wired to the product API at runtime");
  },
};

````

> Result: The file <run>\builds\2-upload-without-byte-route-new-opus\work\packages\mcp\src\product.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>\builds\2-upload-without-byte-route-new-opus\work\packages\mcp\src\tools\upload-image.ts`

````text
import { z } from "zod";
import { images, type ImportOutcome } from "../product";

const MB = 1024 * 1024;

const OTHER_ROUTES =
  "Pass an https:// URL Kitepost can download, such as a public or signed link to the image. " +
  "If you can run commands where the file is, use `npx kitepost upload <board_id> <file>` " +
  "or the Kitepost HTTP API from there instead.";

export const uploadImage = {
  name: "upload_image",
  description:
    "Add an image to a board from an HTTPS URL. Kitepost downloads the URL itself; PNG, JPEG, WebP, or GIF up to 20 MB. " +
    "Local paths, sandbox paths, and base64 are not accepted: this server cannot see your files. " +
    "Retrying after a success adds a second copy.",
  annotations: {
    readOnlyHint: false,
    destructiveHint: false,
    idempotentHint: false,
    openWorldHint: true,
  },
  inputSchema: z.object({
    board_id: z.string().describe("ID of the board to add the image to"),
    url: z
      .string()
      .describe("https:// URL Kitepost can download the image from. Not a local or sandbox path."),
  }),
  async run(input: { board_id: string; url: string }, ctx: { userId: string }) {
    const refusal = refuseUnreachable(input.url);
    if (refusal) return refusal;

    const outcome = await images.importFromUrl({
      userId: ctx.userId,
      boardId: input.board_id,
      url: input.url,
    });

    if (outcome.kind === "added" && outcome.image.status === "ready") {
      const { image } = outcome;
      return {
        ok: true,
        image: {
          id: image.id,
          board_id: image.boardId,
          size: image.size,
          content_type: image.contentType,
          filename: image.filename,
        },
        message: `Added ${image.filename ?? "image"} (${formatSize(image.size)}) to board ${image.boardId}.`,
      };
    }
    if (outcome.kind === "added") {
      return {
        ok: false,
        code: "unknown_outcome",
        message: "The image was accepted but is not ready yet. List the board's images to check whether it landed before retrying.",
      };
    }
    return { ok: false, code: outcome.kind, message: describeRefusal(outcome) };
  },
};

function refuseUnreachable(value: string) {
  const trimmed = value.trim();
  let parsed: URL | null = null;
  try {
    parsed = new URL(trimmed);
  } catch {
    parsed = null;
  }

  // Windows drive letters parse as a URL scheme ("c:"), so treat a single-letter scheme as a path.
  if (!parsed || /^[a-z]:$/i.test(parsed.protocol)) {
    return {
      ok: false,
      code: "local_path",
      message: `That looks like a file path. Kitepost runs remotely and cannot read files on your machine or in your sandbox. ${OTHER_ROUTES}`,
    };
  }
  if (parsed.protocol === "data:") {
    return {
      ok: false,
      code: "inline_bytes",
      message: `Inline image data is not accepted, because it is too large to send through a tool call. ${OTHER_ROUTES}`,
    };
  }
  if (parsed.protocol !== "https:") {
    return {
      ok: false,
      code: "unsupported_scheme",
      message: `Only https:// URLs can be downloaded (got ${parsed.protocol}). Paths such as sandbox: or file: exist only where you run. ${OTHER_ROUTES}`,
    };
  }
  return null;
}

function describeRefusal(outcome: Exclude<ImportOutcome, { kind: "added" }>): string {
  switch (outcome.kind) {
    case "unsupported_type":
      return `The file is not a PNG, JPEG, WebP, or GIF${outcome.detectedType ? ` (it looks like ${outcome.detectedType})` : ""}. Convert it to one of those formats and try again.`;
    case "too_large":
      return `The image is ${formatSize(outcome.size)}, over the ${formatSize(outcome.limit)} limit. Use a smaller image.`;
    case "empty_file":
      return "The URL returned an empty file. Check that the link points to the image itself.";
    case "quota_exceeded":
      return `Not enough storage left: the image needs ${formatSize(outcome.needed)} and ${formatSize(outcome.remaining)} remains. Delete images or upgrade the plan.`;
    case "board_not_found":
      return "No board with that ID was found. List boards to get the right ID.";
    case "forbidden":
      return "You don't have permission to add images to that board.";
    case "url_not_allowed":
      return "That URL points to an address Kitepost will not download from. Use a publicly reachable https:// link.";
    case "fetch_failed":
      return `Kitepost could not download the URL${outcome.status ? ` (it responded ${outcome.status})` : ""}. Check that the link is public or signed and not expired.`;
    case "fetch_timeout":
      return "Downloading the URL took too long. Try again, or use a faster host for the image.";
  }
}

function formatSize(bytes: number): string {
  return bytes >= MB ? `${(bytes / MB).toFixed(1)} MB` : `${Math.ceil(bytes / 1024)} KB`;
}

````

> Result: The file <run>\builds\2-upload-without-byte-route-new-opus\work\packages\mcp\src\tools\upload-image.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-upload-without-byte-route-new-opus/work\" && git rm -q packages/mcp/src/storage.ts && node -e \"for (const s of ['/mnt/data/photo.jpg','sandbox:/workspace/out/chart.png','C:\\\\\\\\x\\\\\\\\a.png','https://a.b/c.png','data:image/png;base64,AA','file:///a']) { let p; try{p=new URL(s).protocol}catch{p=null}; console.log(s,p) }\""}`

> Result: Exit code 1 [eval]:1 for (const s of ['/mnt/data/photo.jpg','sandbox:/workspace/out/chart.png','C:\x\a.png','https://a.b/c.png','data:image/png;base64,AA','file:///a']) { let p; try{p=new URL(s).protocol}catch{p=null}; console.log(s,p) }                                                                              ^^^^ Expected unicode escape  SyntaxError: Invalid hexadecimal escape sequence  [... 244 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-upload-without-byte-route-new-opus/work\" && git status --short && node -e 'for (const s of [\"/mnt/data/photo.jpg\",\"sandbox:/workspace/out/chart.png\",\"C:/x/a.png\",\"https://a.b/c.png\",\"data:image/png;base64,AA\",\"file:///a\",\"~/a.png\"]) { let p; try{p=new URL(s).protocol}catch{p=null}; console.log(s,p) }'"}`

> Result:  M packages/mcp/src/product.ts D  packages/mcp/src/storage.ts  M packages/mcp/src/tools/upload-image.ts ?? docs/upload-design.md /mnt/data/photo.jpg null sandbox:/workspace/out/chart.png sandbox: C:/x/a.png c: https://a.b/c.png https: data:image/png;base64,AA data: file:///a file: ~/a.png null

**Assistant:** I've written the design to `docs/upload-design.md` and rewritten the MCP tool to match it. Nothing is committed. I couldn't run a type check because the package has no tsconfig and zod isn't installed. I did check that the input-classifying logic handles the exact inputs from the bug reports.

**What caused 412 and 418:** `upload_image` read the `path` on Kitepost's remote MCP server. The file was actually in the assistant's own sandbox, so the read failed. The tool then stored an empty file, created the image anyway, and reported success. That explains both broken images.

**The design:** each caller sends the image by a route that can actually carry the bytes from where it runs, and every route ends in the same product step (permission, type and size checks, storage quota, then a final "finalize" step). An image only counts as added after finalize succeeds.
- **HTTP API:**
  - Ask the server to start an upload and get back a signed upload link.
  - Send the raw file to that link.
  - Call finalize.

  There's also an endpoint that imports an image from a URL. Image data never goes inside the JSON request.
- **CLI:** `npx kitepost upload <board_id> <file...>` checks each file locally, then runs those same three steps. Each file gets its own result, and the command fails if any file failed.
- **MCP:** the tool now takes an `https://` URL, and Kitepost downloads it itself. Downloads are protected against being pointed at internal addresses, and capped in size, redirects and time. Coding agents that have a shell in their sandbox should use the CLI or HTTP API from there.
- **421 (base64):** declined. An assistant writes base64 out piece by piece in its reply, and a 6 MB photo is far more than its context can hold. That's exactly what failed for your teammate.

**Code changes:**
- `packages/mcp/src/tools/upload-image.ts`:
  - It no longer reads files or writes to storage.
  - It refuses local paths, `sandbox:`, `file:`, `data:` and anything that isn't `https`, with a message saying what to do instead.
  - It reports success only once the image is actually ready on the board, and returns its ID, size and type.
  - Other failures (wrong type, too large, out of storage, no permission) get clear messages.
  - Its description says that retrying adds a second copy.
- `packages/mcp/src/product.ts`: replaced the old stubs with a declaration for the URL-import step and its list of possible results.
- `packages/mcp/src/storage.ts`: deleted, so the MCP server has no way to write files into storage.

**Not built yet**, because that code isn't in this repo: the HTTP endpoints, the CLI command, and the server-side download and finalize logic.

**Calls I made that you should confirm** (the full list is at the end of the doc):
1. No base64 for images at any size.
2. The tool keeps the name `upload_image` and drops `path` immediately, with no transition period. It never worked for remote callers, so nobody relied on it.
3. Kitepost downloads URLs on the server, and the HTTP API offers that import too.
4. One signed upload per file, with no multi-part uploads, because of the 20 MB limit.
5. Download limits of 3 redirects and 30 seconds, and unfinished uploads expire after 1 hour. These numbers are mine; the brief doesn't set them.
6. 412 now fails with a clear message instead of reporting false success, but it won't actually work yet. That needs support for the chat app's file attachments, and I didn't check how any app exposes them.

**Needs your go-ahead:** the earlier bugs left empty images on users' boards. The doc proposes a one-off job to delete them and recalculate each affected account's storage use. I didn't run it because it deletes things users can see.

**Session ended:** success, 12 turns, 144048 ms
