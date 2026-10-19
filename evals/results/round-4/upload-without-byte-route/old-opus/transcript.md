**Prompt:** Bug reports 412, 418, and 421 in docs/issues.md are all about getting images into Kitepost from agents. Work out how files should get into Kitepost from the MCP server, the HTTP API, and the CLI, write the design to docs/upload-design.md, and change packages/mcp/src/tools/upload-image.ts to match it. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work && git ls-files && cat docs/brief.md docs/issues.md"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6127 more characters]

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work && for f in package.json pnpm-workspace.yaml packages/mcp/package.json packages/mcp/src/*.ts packages/mcp/src/tools/*.ts; do echo \"=== $f\"; cat $f; done"}`

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/.claude/skills/web-repository-opinions/references && cat uploads.md model-context-protocol.md agent-tool-design.md"}`

> Result: === package.json {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } === pnpm-workspace.yaml packages:   - "apps/*"   - "packages/*" === packages/mcp/package.json {   "nam [... 1634 more characters]

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 10076 more characters]

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/.claude/skills/web-repository-opinions/references && cat http-apis.md abuse-resistance.md object-storage.md quota.md user-facing-errors.md"}`

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/.claude/skills/web-repository-opinions/references && cat definition-of-done.md modularity.md failure-and-retries.md runtime-truth.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 12225 more characters]

> Result: # Definition Of Done  This is a completion summary across the skill. It is not the source of truth for the detailed rules below. Load the owning references for every category the work touches.  A feature is done only when its product contract, implementation, runtime, and verification agree. If one category is false or unknown, the work is locally edited, not done.  ## Product Contract  -  [... 9562 more characters]

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/.claude/skills/web-repository-opinions/references && cat routing.md ids.md bulk-actions.md | head -150"}`

> Result: # Routing  Route paths are product architecture. They live in code and docs, never in env.  Use one canonical route model per concept. Do not keep a long path and a short path alive for the same thing.  ## Full Names And Collection Prefixes  A standalone page that is only ever itself gets a full, descriptive path. A surface that holds child pages or items gets a prefix, and the bare prefix [... 10724 more characters]

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/docs/upload-design.md`

````text
# Getting images into Kitepost: upload design

Status: proposed on 2026-10-18 while the owner was away. Covers bug reports 412, 418, and 421. Decisions I made on the owner's behalf are under "Assumptions and calls made" at the end.

## What went wrong

The MCP tool `upload_image` took a `path` and called `readFile` on it **on the Kitepost MCP server**. The MCP server is remote (`mcp.kitepost.example/mcp`). A path like `/mnt/data/photo.jpg` (412) or `sandbox:/workspace/out/chart.png` (418) points into the agent's own sandbox or chat app. The server cannot see that filesystem, and no path ever can. When the read failed, the tool:

1. swallowed the error and replaced the file with an empty buffer,
2. wrote zero bytes to object storage and recorded an image row anyway,
3. returned `ok: true` with "Uploaded photo.jpg".

So the cause of both bugs is that the tool takes an input the server can never honor, and the success message is hard-coded instead of coming from what was actually stored. It also wrote to storage directly from the MCP adapter, which skipped the type, size, and quota rules the browser path enforces.

421 (send base64) does not fix this. A language model writes base64 out one token at a time. A 6 MB photo is about 8 MB of base64, millions of tokens, far more than any context window. That is why the teammate's assistant ran out of context. Even a 1 MB image costs hundreds of thousands of tokens.

## Principles

- **Bytes go from the caller straight to object storage, never through a Kitepost app server.** The browser already does this: sign a PUT, upload, finalize. Every other surface uses the same flow.
- **One product capability, many thin adapters.** The product API owns the upload capability. It does authorization, type and size limits, quota, and the image record. The HTTP API, CLI, and MCP server only translate it for their protocol. (Brief: "Every surface goes through the same product API and the same authorization.")
- **A file path is only meaningful on the machine that reads it.** The CLI runs on the user's machine, so it accepts paths. The remote MCP server does not.
- **Success means the bytes landed and passed checks.** Every surface reports the image the product recorded as `ready`, never a message built from the caller's input.
- **Bytes travel out of band, not inline.** Callers get a URL the server fetches, or a signed PUT. No base64 field on any surface.

## Product capability (shared by every surface)

All three operations run in the product API under the caller's identity, with the same authorization as the browser.

### Start an upload

Input: `board_id`, `filename`, `content_type`, `size_bytes`.

1. Check that the caller can edit the board.
2. Check `content_type` is one of `image/png`, `image/jpeg`, `image/webp`, `image/gif`, and `size_bytes` is between 1 byte and 20 MB.
3. Check quota against `size_bytes`: fail before any bytes move if the account's 2 GB (free plan) cannot fit it. Quota is not charged yet.
4. Generate a fresh opaque storage key. The key never contains the filename.
5. In one transaction, create the image row with status `pending`, store the original filename as metadata, and register the key in the object-write ledger. The row and the ledger entry both exist before any bytes do.
6. Sign a single PUT to that key. The signature covers `Content-Type` and `Content-Length = size_bytes`, so storage rejects other bytes. It expires in 15 minutes.

Output: `upload_id`, `put_url`, `put_headers`, `expires_at`.

### Finish an upload

Input: `upload_id`.

1. Check that the caller owns the pending upload.
2. HEAD the object. Missing: `upload_missing` (the upload stays pending until it expires, so the caller can still PUT and then call finish again).
3. Check the stored size equals the declared size and is at most 20 MB. Read the first bytes and check the magic number matches the declared type. A mismatch fails the image, and the object is deleted through the ledger.
4. Mark the image `ready`, charge quota for the real size, and return the image.

Calling finish twice returns the same image and charges quota once.

If an upload is still `pending` after its URL expires plus a grace window (1 hour), the scheduled sweep marks it `failed + abandoned` and the ledger drain removes any bytes.

### Import from a URL

Input: `board_id`, `url`.

The product API fetches the image itself and then runs the same validation and finish steps. The fetch is a server-side fetch of an attacker-chosen URL, so it is hardened:

- `https` only, on the default port. No credentials in the URL.
- Resolve DNS and refuse loopback, private, link-local, CGNAT, multicast, and cloud metadata addresses. Connect to the IP that was checked, and check again on every redirect. At most 3 redirects.
- Stream the body and stop at 20 MB. Overall timeout 30 s.
- Judge the type by magic bytes, not by the response header.
- Quota: check against `Content-Length` when the server sends one, and always against the bytes actually received. Charge after success.

The bytes are written through the same ledger-first path as an upload.

### Image result (shared schema)

```json
{ "id": "Hq3k9TmPx2Ab", "board_id": "…", "status": "ready", "filename": "photo.jpg",
  "content_type": "image/jpeg", "size_bytes": 2483112, "url": "https://…" }
```

`id` is the 12-character Base58 entity ID. The HTTP API, CLI `--json` output, and MCP tool results all return this same shape.

### Typed failures

These codes are shared across surfaces. Each surface's message names what was measured and what to do next:

| Code | Next move |
| --- | --- |
| `board_not_found` | Check the board ID. The same code covers "no access", so it does not reveal which boards exist. |
| `unsupported_type` | Use PNG, JPEG, WebP, or GIF. |
| `too_large` | Keep images to 20 MB or less. The message quotes the measured size. |
| `quota_exceeded` | Free up space or upgrade. The message quotes the space used and the plan limit. |
| `upload_missing` | PUT the file to `put_url` first, then finish. |
| `upload_mismatch` | Bytes don't match the declared size or type. Start a new upload. |
| `upload_expired` | Start a new upload. |
| `url_blocked` / `url_unreachable` / `url_not_image` | Use a public https link straight to the image file. |

Raw storage, network, and provider errors stay in logs.

## HTTP API (`api.kitepost.example/v1`)

These routes go in the OpenAPI document before they are implemented:

```text
POST /v1/boards/{board_id}/uploads      start   -> 201 { upload_id, put_url, put_headers, expires_at }
PUT  <put_url>                          bytes go straight to object storage
POST /v1/uploads/{upload_id}/finish     finish  -> 200 { image }
POST /v1/boards/{board_id}/images       body { "url": "https://…" } -> 201 { image }
```

These are the same routes the browser's drag-and-drop uses. The API never takes image bytes in JSON or in a request body to a Kitepost server. Script callers do three calls (start, `curl -T file put_url`, finish) or one call for a URL. API keys authorize exactly what the owning user can do.

## CLI (`npx kitepost`)

The CLI runs on the user's machine or in CI, so paths make sense there.

```text
kitepost upload <file-or-url>... --board <board_id> [--json]
```

- Each argument is either a local path, which goes through start → PUT → finish, or an `https://` URL, which goes through import from URL.
- Before calling the API it checks type (magic bytes) and size locally, so it fails fast without a network round trip. The API still enforces every rule.
- Several files are uploaded independently, at most 4 at a time. Results print in input order, one per file, with failures inline. The exit code is non-zero if any file failed. `--json` prints one image result or typed failure per input.
- It authenticates with `KITEPOST_API_KEY` (or the stored login). It is a thin client over the HTTP API, with no rules of its own.

A coding agent running on the user's own machine (not in a hosted sandbox) should use the CLI for local files.

## MCP server (`mcp.kitepost.example/mcp`)

Most MCP callers run in a hosted sandbox or chat app, and the server can never read their files. The tools give them two ways in:

| Tool | For |
| --- | --- |
| `add_image_from_url` | The image is at a public https URL. One call. |
| `start_image_upload` → PUT → `finish_image_upload` | The image is a file in the agent's sandbox and the agent can run a shell or code with outbound network (coding agents, 418). |

- **No `path` argument, no base64 argument.** If a cached client still sends `path` or base64 data, the tool returns a teaching refusal that names the two supported routes. It never fakes success.
- `start_image_upload` returns the signed URL, the headers, and a ready-to-run `curl` command with the filename filled in. The agent runs it in its own sandbox, then calls `finish_image_upload`. The signed URL can write that one key only, and only for 15 minutes.
- The tools report success only from the product's `ready` image. `finish_image_upload` answers `upload_missing` with "PUT the file first", so an agent that skipped the PUT learns the next move.
- Annotations: none are read-only. `add_image_from_url` is open-world (it fetches an outside URL), not idempotent. `start_image_upload` is not idempotent. `finish_image_upload` is idempotent. None are destructive.
- The old `upload_image` tool is removed. It never worked for a remote caller (every call stored an empty image), so there is no behavior to stay compatible with. Clients re-list tools on reconnect and pick up the new catalog.

### Chat apps without network in the sandbox (412)

In 412 the file is a chat attachment at `/mnt/data/…`. These sandboxes usually have no outbound network, so the PUT route is not available, and the image is too large to go inline. After this change the assistant gets an honest refusal instead of a fake success, and it can tell the user to drop the image on the board in the browser or share a link. The real fix depends on the host. Some chat hosts can hand a user's attachment to a remote tool as a short-lived download URL (for example, the file-parameter support in OpenAI's Apps SDK). The MCP adapter can map that URL to import from URL, allowing that host's download domain. This is follow-up work, to be checked against each host's current documentation before it is built.

## Assumptions and calls made

1. **421: no base64 input on any surface, not even for tiny images.** The model pays the token cost before the server can refuse, so a size cap in the schema doesn't protect it. The small images that would fit, such as generated charts, mostly come from sandboxes that can run the PUT route. Easy to revisit with a separate small-image tool if real demand appears.
2. **Old `upload_image` removed, not kept as an alias.** Three tools with separate names are clearer to an agent than one tool whose valid arguments depend on where it runs.
3. **No caption on upload for now.** Captions stay a separate board edit, as before. A `caption` field can be added to start/import later without breaking anything.
4. **The product API already has (or will get) start/finish routes the browser uses.** I modeled the MCP package's `product.ts` client on them: `uploads.start`, `uploads.finish`, `images.importFromUrl`. If the browser's routes are named differently, the client should follow those names, not the other way round.
5. **Numbers I picked:** signed URLs expire in 15 minutes, abandoned uploads are swept after 1 hour, URL fetch allows 3 redirects and 30 s, the CLI runs 4 uploads at a time. None of these are product decisions in the brief, so they are easy to tune.
6. **`board_not_found` also covers "no access"**, so the response does not reveal which boards exist.
7. **Not done in this change:** the product API routes, OpenAPI entries, the URL fetcher, the CLI command, the ledger sweep, and host file-parameter support. Only the MCP tool adapter and its product-client stubs changed. `packages/mcp/src/storage.ts` is no longer used by the MCP package, because bytes no longer pass through it. I left it in place for the owner to remove.
8. **Existing broken images from 412/418** are zero-byte rows. A one-off cleanup should find `ready` images with size 0, mark them `failed + upload`, and tell the user to upload again. I did not run that, because it touches production data.

````

> Result: File created successfully at: C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/docs/upload-design.md (file state is current in your context — no need to Read it back)

**Assistant:** Design doc is written. Now the MCP adapter and its product client stubs.

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/packages/mcp/src/product.ts`

````text
// Client for the shared product API. Every surface (browser, HTTP API, CLI, MCP)
// calls these same capabilities, which own authorization, limits, and quota.
// See docs/upload-design.md.

export type Image = {
  id: string;
  board_id: string;
  status: "ready";
  filename: string;
  content_type: "image/png" | "image/jpeg" | "image/webp" | "image/gif";
  size_bytes: number;
  url: string;
};

export type UploadFailureCode =
  | "board_not_found"
  | "unsupported_type"
  | "too_large"
  | "quota_exceeded"
  | "upload_missing"
  | "upload_mismatch"
  | "upload_expired"
  | "url_blocked"
  | "url_unreachable"
  | "url_not_image";

/** Product-owned failure. `detail` carries measurements (sizes, limits), never raw provider errors. */
export type UploadFailure = { ok: false; code: UploadFailureCode; detail?: Record<string, number | string> };

export type UploadStart = {
  ok: true;
  upload_id: string;
  put_url: string;
  put_headers: Record<string, string>;
  expires_at: string;
};

export const uploads = {
  /** Validates board access, type, size, and quota, creates a pending image, and signs a direct PUT to storage. */
  async start(
    userId: string,
    input: { boardId: string; filename: string; contentType: string; sizeBytes: number },
  ): Promise<UploadStart | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
  /** Verifies the stored bytes, marks the image ready, and charges quota. Idempotent. */
  async finish(userId: string, uploadId: string): Promise<{ ok: true; image: Image } | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
};

export const images = {
  /** Fetches a public https image server-side (SSRF-guarded, 20 MB cap) and adds it to a board. */
  async importFromUrl(
    userId: string,
    input: { boardId: string; url: string },
  ): Promise<{ ok: true; image: Image } | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
};

````

> Result: The file C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/packages/mcp/src/product.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/packages/mcp/src/tools/upload-image.ts`

````text
import { z } from "zod";
import { images, uploads, type Image, type UploadFailure } from "../product";

// This server is remote. It can never read files on the caller's machine or sandbox,
// and inline base64 costs the model millions of tokens for an ordinary photo.
// Bytes arrive either from a URL the product fetches or through a signed PUT the caller runs.
// See docs/upload-design.md.

const MAX_BYTES = 20 * 1024 * 1024;
const CONTENT_TYPES = ["image/png", "image/jpeg", "image/webp", "image/gif"] as const;
const LOCAL_INPUT_KEYS = ["path", "file", "data", "base64", "data_base64", "bytes"];

const ROUTES_HINT =
  "Kitepost's server cannot read files from your machine or sandbox, and does not accept inline image data. " +
  "If the image is at a public https URL, call add_image_from_url. " +
  "If it is a file you can reach from a shell with network access, call start_image_upload, run the returned curl command, then call finish_image_upload.";

function refuseLocalInput(input: Record<string, unknown>) {
  const key = LOCAL_INPUT_KEYS.find((k) => k in input);
  return key ? { ok: false as const, code: "unsupported_input", message: `The "${key}" field is not supported. ${ROUTES_HINT}` } : null;
}

function formatMb(bytes: number | string | undefined) {
  return typeof bytes === "number" ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : "unknown size";
}

function failure(f: UploadFailure) {
  const d = f.detail ?? {};
  const messages: Record<UploadFailure["code"], string> = {
    board_not_found: "No board with that ID is available to you. Check the board_id.",
    unsupported_type: "Kitepost accepts PNG, JPEG, WebP, and GIF images only.",
    too_large: `The image is ${formatMb(d.size_bytes)}; the limit is 20 MB per image.`,
    quota_exceeded: `The account has ${formatMb(d.remaining_bytes)} of storage left, not enough for this image. The owner can free space or upgrade.`,
    upload_missing: "No file has been uploaded for this upload_id yet. Run the PUT from start_image_upload first, then call finish_image_upload again.",
    upload_mismatch: "The uploaded file does not match the declared size or type. Call start_image_upload again with the file's exact size_bytes and content_type.",
    upload_expired: "This upload expired before it was finished. Call start_image_upload again.",
    url_blocked: "That URL can't be fetched. Use a public https link to the image file.",
    url_unreachable: "Kitepost couldn't download that URL. Check that it is public and links straight to the image file.",
    url_not_image: "That URL didn't return a PNG, JPEG, WebP, or GIF image. Link straight to the image file, not a page that shows it.",
  };
  return { ok: false as const, code: f.code, message: messages[f.code] };
}

function added(image: Image) {
  return { ok: true as const, image, message: `Added ${image.filename} to board ${image.board_id} (image ${image.id}).` };
}

export const addImageFromUrl = {
  name: "add_image_from_url",
  description:
    "Add an image to a board from a public https URL. Kitepost downloads the file itself. PNG, JPEG, WebP, or GIF, up to 20 MB. " +
    "For a file in your own sandbox, use start_image_upload instead.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
  inputSchema: z
    .object({
      board_id: z.string().describe("ID of the board to add the image to"),
      url: z.string().url().describe("Public https URL that returns the image file itself"),
    })
    .passthrough(),
  async run(input: { board_id: string; url: string } & Record<string, unknown>, ctx: { userId: string }) {
    const refused = refuseLocalInput(input);
    if (refused) return refused;
    const result = await images.importFromUrl(ctx.userId, { boardId: input.board_id, url: input.url });
    return result.ok ? added(result.image) : failure(result);
  },
};

export const startImageUpload = {
  name: "start_image_upload",
  description:
    "Upload an image file from your sandbox to a board, step 1 of 2. Returns a signed URL and a curl command; " +
    "run it in your own shell to send the file, then call finish_image_upload. PNG, JPEG, WebP, or GIF, up to 20 MB.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
  inputSchema: z
    .object({
      board_id: z.string().describe("ID of the board to add the image to"),
      filename: z.string().min(1).describe("File name only, for example chart.png"),
      content_type: z.enum(CONTENT_TYPES),
      size_bytes: z.number().int().min(1).max(MAX_BYTES).describe("Exact file size in bytes, for example from `wc -c < file`"),
    })
    .passthrough(),
  async run(
    input: { board_id: string; filename: string; content_type: (typeof CONTENT_TYPES)[number]; size_bytes: number } & Record<string, unknown>,
    ctx: { userId: string },
  ) {
    const refused = refuseLocalInput(input);
    if (refused) return refused;
    const result = await uploads.start(ctx.userId, {
      boardId: input.board_id,
      filename: input.filename,
      contentType: input.content_type,
      sizeBytes: input.size_bytes,
    });
    if (!result.ok) return failure(result);
    const headers = Object.entries(result.put_headers)
      .map(([name, value]) => `-H '${name}: ${value}'`)
      .join(" ");
    return {
      ok: true as const,
      upload_id: result.upload_id,
      put_url: result.put_url,
      put_headers: result.put_headers,
      expires_at: result.expires_at,
      command: `curl -fsS -X PUT ${headers} --data-binary @'${input.filename}' '${result.put_url}'`,
      message:
        `Nothing is on the board yet. Run the command from the directory holding ${input.filename} before ${result.expires_at}, ` +
        `then call finish_image_upload with upload_id ${result.upload_id}.`,
    };
  },
};

export const finishImageUpload = {
  name: "finish_image_upload",
  description:
    "Finish an image upload, step 2 of 2: check the file sent to the signed URL from start_image_upload and add it to the board. Safe to call again.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  inputSchema: z.object({
    upload_id: z.string().describe("upload_id returned by start_image_upload"),
  }),
  async run(input: { upload_id: string }, ctx: { userId: string }) {
    const result = await uploads.finish(ctx.userId, input.upload_id);
    return result.ok ? added(result.image) : failure(result);
  },
};

export const uploadTools = [addImageFromUrl, startImageUpload, finishImageUpload];

````

> Result: The file C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/packages/mcp/src/tools/upload-image.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** A filename with a quote in it would break the generated curl command, so I'll restrict filenames.

**Tool call `Edit`:** `C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/packages/mcp/src/tools/upload-image.ts`

Replaced:

````text
      filename: z.string().min(1).describe("File name only, for example chart.png"),
````

With:

````text
      filename: z
        .string()
        .regex(/^[^/\\'"`$\x00-\x1f]{1,200}$/, "Use the file name only, without folders or quotes")
        .describe("File name only, for example chart.png"),
````

> Result: The file C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/packages/mcp/src/tools/upload-image.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/docs/upload-design.md`

Replaced:

````text
- **No `path` argument, no base64 argument.** If a cached client still sends `path` or base64 data, the tool returns a teaching refusal that names the two supported routes. It never fakes success.
````

With:

````text
- **No `path` argument, no base64 argument.** If an agent adds `path`, `file`, `data`, or a base64 field to either start tool anyway, the tool returns a teaching refusal that names the two supported routes. It never fakes success. A client that cached the old catalog and calls `upload_image` gets the SDK's unknown-tool error, and re-lists the tools.
````

> Result: The file C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/docs/upload-design.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/docs/upload-design.md`

Replaced:

````text
so there is no behavior to stay compatible with. Clients re-list tools on reconnect and pick up the new catalog.
````

With:

````text
so there is no behavior to stay compatible with. Some clients cache the tool list and will keep offering `upload_image` until they reconnect. Their calls fail loudly instead of storing an empty image, which is the fix that matters.
````

> Result: The file C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work/docs/upload-design.md has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd C:/tmp/wro-eval3/builds/3-upload-without-byte-route-old-opus/work && grep -rn \"uploadImage\\|storage\" packages --include=*.ts; ls node_modules 2>&1 | head -2; git status --short"}`

> Result: packages/mcp/src/product.ts:39:  /** Validates board access, type, size, and quota, creates a pending image, and signs a direct PUT to storage. */ packages/mcp/src/storage.ts:1:export const storage = { packages/mcp/src/storage.ts:2:  /** Writes bytes to object storage under an opaque key. */ packages/mcp/src/storage.ts:4:    throw new Error("wired to the object storage adapter at runtime"); packag [... 344 more characters]

**Assistant:** I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. I haven't committed anything, and nothing has been type-checked or run: the repo has no installed dependencies or tsconfig, and the product API calls are stubs that only work once wired up.

**What caused 412 and 418.** The MCP server is remote, but `upload_image` tried to read the caller's `path` on the server's own disk. Paths like `/mnt/data/photo.jpg` or `sandbox:/workspace/...` exist only in the agent's sandbox, so the read always failed. The tool hid the error, saved an empty image and reported "Uploaded photo.jpg". It also wrote to storage directly, skipping the type, size and quota checks.

**Why 421 (base64) isn't the fix.** The model has to write base64 out one token at a time. A 6 MB photo is about 8 MB of base64, which is millions of tokens. That's why the teammate's assistant ran out of context.

**The design.** One shared product flow, the same sign → PUT → finalize the browser already uses, with every check in the product API. Image bytes never pass through a Kitepost server and are never sent inline.
- **HTTP API:** `POST /v1/boards/{board_id}/uploads` returns a signed PUT URL, then `POST /v1/uploads/{upload_id}/finish`. Separately, `POST /v1/boards/{board_id}/images` with `{url}` has the server fetch the image, with protections against requests to internal addresses and the 20 MB cap.
- **CLI:** `kitepost upload <file-or-url>... --board <id> [--json]`. Local paths are fine here because the CLI runs on the user's machine. Multiple files get one result each, in input order.
- **MCP:** three tools replace `upload_image`:
  - `add_image_from_url`: for images at a public https URL.
  - `start_image_upload`: returns the signed URL plus a ready-to-run `curl` command.
  - `finish_image_upload`: checks the uploaded file and adds it to the board; safe to call again.

  If an agent sends `path` or base64 data, it gets a refusal that explains the supported routes. Success is only reported once the image has been stored and checked.

**Bug status:**
- **418 (coding agent):** fixed by the upload route, as long as its sandbox has network access.
- **412 (chat attachment):** now fails honestly but still can't succeed. Those sandboxes usually have no network, and the photo is too big to send inline. The real fix depends on each chat app, for example ones that can hand the tool a short-lived download link for an attachment. I've recorded that as follow-up work to check against each app's documentation.

**Calls I made without you** (all listed in the doc):
1. No base64 input anywhere, not even for small images, because the model pays the token cost before the server can refuse.
2. `upload_image` is removed rather than kept as an alias. It never worked for remote callers. Clients that cached the old tool list will get an error when they call it until they refresh.
3. No caption field on upload for now.
4. I assumed the product API's start/finish routes are the ones the browser uses, and modelled `product.ts` on that. I replaced `allocateKey`/`create` with `uploads.start`, `uploads.finish` and `images.importFromUrl`.
5. Numbers I picked: signed URLs last 15 minutes, abandoned uploads are cleaned up after 1 hour, URL fetches allow 3 redirects and 30 seconds, and the CLI runs 4 uploads at a time.

**Not done:** the product API routes and OpenAPI entries, the URL fetcher, the CLI command, and the cleanup job for abandoned uploads. Also not done: cleaning up the existing empty images from 412 and 418, because that touches production data. `packages/mcp/src/storage.ts` is now unused; I left it for you to delete.

**Session ended:** success, 16 turns, 223363 ms
