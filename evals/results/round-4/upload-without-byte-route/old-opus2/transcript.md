**Prompt:** Bug reports 412, 418, and 421 in docs/issues.md are all about getting images into Kitepost from agents. Work out how files should get into Kitepost from the MCP server, the HTTP API, and the CLI, write the design to docs/upload-design.md, and change packages/mcp/src/tools/upload-image.ts to match it. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-upload-without-byte-route-old-opus2/work\" && git ls-files && cat docs/brief.md docs/issues.md && cat packages/mcp/src/tools/upload-image.ts"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6918 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-upload-without-byte-route-old-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/uploads.md $R/model-context-protocol.md $R/agent-tool-design.md; cat packages/mcp/src/*.ts packages/mcp/package.json package.json"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 11103 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-upload-without-byte-route-old-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/http-apis.md $R/abuse-resistance.md $R/object-storage.md $R/quota.md $R/user-facing-errors.md $R/modularity.md"}`

> Result: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 15789 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-upload-without-byte-route-old-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/definition-of-done.md | head -80; grep -rn \"storage\\|product\" packages --include=*.ts | grep import"}`

> Result: # Definition Of Done  This is a completion summary across the skill. It is not the source of truth for the detailed rules below. Load the owning references for every category the work touches.  A feature is done only when its product contract, implementation, runtime, and verification agree. If one category is false or unknown, the work is locally edited, not done.  ## Product Contract  -  [... 3479 more characters]

**Assistant:** Now the design doc.

**Tool call `Write`:** `<run>\builds\4-upload-without-byte-route-old-opus2\work\docs\upload-design.md`

````text
# Getting images into Kitepost from agents, the HTTP API, and the CLI

Status: proposed, 2026-10-19. Covers bug reports 412, 418, and 421 in `docs/issues.md`.

## What went wrong

The MCP tool `upload_image` took `path`, a filesystem path, and read it with `readFile` **on the Kitepost MCP server**. The MCP server is remote (`mcp.kitepost.example/mcp`). The agent's file lives somewhere else: in the chat app's sandbox (`/mnt/data/photo.jpg`, 412) or in a coding agent's sandbox (`sandbox:/workspace/out/chart.png`, 418). The server can never see those paths.

The read failed, the tool swallowed the error (`.catch(() => Buffer.alloc(0))`), wrote a zero-byte object, created an image row, and reported "Uploaded photo.jpg". So there were two bugs:

1. **Wrong input shape.** A remote server cannot accept a path from the caller's machine. No fix to path handling makes that work.
2. **False success.** The tool reported success without checking that any bytes landed. It also wrote to object storage directly and skipped the product API's checks: size, type, quota, and the board authorization that `allocateKey` only partly covered. That breaks the decision that every surface goes through the same product API.

421 asks for base64 input. Inline bytes are the wrong main path for a language model. The model has to generate the encoded blob token by token, so it is slow and costly, and it is limited by the context window. A 6 MB photo is about 8 MB of base64, far more than any context window holds. That is the failure the teammate hit.

## Principles

- **Bytes go straight to object storage.** No Kitepost app server route accepts or relays image bytes. This is the flow the browser app already uses, and it works.
- **Every surface uses one product capability**, with the same authorization, limits, and quota. The MCP server, HTTP API, CLI, and browser app are thin adapters over it.
- **An upload counts as done only after finalize checks the stored object.** A request was accepted, or a URL was signed, is not enough.
- **Two ways in, picked by where the bytes live:**
  - The bytes are at a public URL: **Kitepost fetches them** (import from URL).
  - The bytes are local to the caller, and the caller can make an HTTP request: **the caller PUTs them to a signed URL**, then finalizes (upload session).
- No inline or base64 bytes on any surface (see "Decisions" for 421).

## Product capability (shared)

Three operations in the product API. Every adapter calls these and none of them re-implements the rules.

### `images.createUpload({ boardId, filename, contentType, sizeBytes })`

1. Authorize: the caller can add images to `boardId`.
2. Validate before any bytes move:
   - `contentType` is one of `image/png`, `image/jpeg`, `image/webp`, `image/gif`.
   - `sizeBytes` is between 1 and 20 MB (20 × 1024 × 1024).
   - Quota: the account's used storage plus `sizeBytes` fits the plan limit (2 GB on free) and the hidden internal ceiling.
3. Create a `pending` upload row, which also registers the object key in the write-ahead ledger, **before** signing. An interrupted upload then leaves a record we can recover or sweep, not an orphan byte. The key is opaque and random, and the filename is stored only as metadata.
4. Sign a single PUT URL bound to that key, `Content-Type`, and `Content-Length`. It expires after 15 minutes. One PUT is enough at 20 MB, so no multipart.
5. Return `{ uploadId, putUrl, putHeaders, expiresAt }`.

### `images.finalizeUpload({ uploadId })`

1. Authorize: the same caller and board as the upload.
2. HEAD the object. Refuse with a typed outcome if it is missing (`upload_missing_bytes`), if the size does not match the declared size (`upload_size_mismatch`), or if the session has expired (`upload_expired`).
3. Read the first bytes and check the magic number against the declared type (`upload_type_mismatch`). Never recompress, and keep the original bytes.
4. Mark the row `ready`, attach the image to the board, and **then** charge storage usage.
5. Return the shared `Image` resource.

Finalize is idempotent. Finalizing a `ready` upload again returns the same `Image`. That makes retries safe for agents.

### `images.importFromUrl({ boardId, sourceUrl })`

Server-side fetch with the same protections as any other server-side fetch:

- `https:` only. Resolve DNS and refuse loopback, private, link-local, CGNAT, and cloud metadata addresses. Re-check on every redirect, with at most 3 redirects. Send no cookies or credentials.
- Timeout of 20 s. Stream the body and abort once it passes 20 MB. If `Content-Length` is present and too large, refuse before reading.
- Check the authorization, type, and quota gates before the body is read, using `Content-Length` when present. Check the type again by magic number on the bytes received.
- Create the pending row first, write the bytes to storage, then run the same finalize steps.
- Synchronous: it returns the `Image` or a typed refusal. At 20 MB and 20 s this fits inside one request. If real imports turn out slower, switch it to a job and return the job state honestly (not "added").

### Typed outcomes

`board_not_found`, `forbidden`, `unsupported_type`, `too_large`, `quota_exceeded`, `url_not_allowed`, `url_unreachable`, `url_not_image`, `upload_not_found`, `upload_expired`, `upload_missing_bytes`, `upload_size_mismatch`, `upload_type_mismatch`. Each adapter turns these into product copy that states what was measured and what to do next. Raw provider or fetch errors stay in logs.

### Shared `Image` resource

`{ id, board_id, filename, content_type, size_bytes, url }`. The same shape is used in HTTP responses, MCP tool results, and CLI `--json` output.

## HTTP API (`api.kitepost.example/v1`)

| Method and path | Body | Result |
| --- | --- | --- |
| `POST /v1/boards/{board_id}/uploads` | `{ filename, content_type, size_bytes }` | `201 { upload: { id, put_url, put_headers, expires_at } }` |
| `POST /v1/uploads/{upload_id}/finalize` | none | `200 { image }` |
| `POST /v1/boards/{board_id}/image-imports` | `{ source_url }` | `201 { image }` |

The client PUTs the bytes to `put_url` with `put_headers`. There is no `/v1` route that takes image bytes, either as a multipart form or in JSON. API keys authorize the three calls above. The signed URL authorizes only the one PUT. Errors are stable typed bodies `{ error: { code, message } }` using the codes above. All three routes go into the OpenAPI document before they are implemented.

## CLI (`npx kitepost`)

The CLI runs on the user's machine or in CI, so it can read a local path. That is the one place a path input makes sense.

- `kitepost upload <board_id> <file...>`: for each file, it stats the file and sniffs its type locally to give fast feedback. Then it calls create upload, PUTs the file from a stream, and calls finalize. Each file gets its own result line, in input order, and a failure is reported inline without stopping the rest. The exit code is non-zero if any file failed. `--json` prints one `Image` or error per file.
- `kitepost import <board_id> <url>`: calls `image-imports`.
- It authenticates with the API key (`KITEPOST_API_KEY`). It is a thin client over the HTTP API with no rules of its own.

## MCP server (`mcp.kitepost.example/mcp`)

`upload_image { board_id, path }` is removed. It replaces with three tools whose names describe where the bytes come from:

| Tool | Input | For |
| --- | --- | --- |
| `add_image_from_url` | `board_id`, `url` | An image already at a public `https://` URL. Kitepost fetches it. One call. |
| `create_image_upload` | `board_id`, `filename`, `content_type`, `size_bytes` | A file in the agent's own sandbox or workspace (418). Returns a signed `put_url`, the headers to send, and a ready-made `curl` command. |
| `finalize_image_upload` | `upload_id` | After the PUT. Checks the bytes and returns the `Image`. Safe to repeat. |

Tool descriptions and schema hints say plainly:

- Local paths and `sandbox:` paths cannot be read by Kitepost. Upload the file with `create_image_upload`.
- Do not paste base64.
- Report an image as added only after `finalize_image_upload` or `add_image_from_url` returns the image.

Results:

- Success returns the shared `Image` resource and a message built from the stored filename and size, not from the caller's input.
- A refusal returns `isError` with copy that names the measurement and the next step. For example: "photo.heic is image/heic. Kitepost accepts PNG, JPEG, WebP, or GIF." Or: "Nothing was uploaded to this upload yet. PUT the file to put_url, then finalize."

Annotations:

- `add_image_from_url`: not read-only, not destructive, not idempotent, open-world.
- `create_image_upload`: not read-only, not destructive, not idempotent.
- `finalize_image_upload`: not read-only, not destructive, idempotent.

### How each reported case ends up

- **418 (coding agent, sandbox file):** `create_image_upload` → `curl -X PUT --data-binary @chart.png ...` from the sandbox shell → `finalize_image_upload`. This works whenever the sandbox can reach the storage upload host. The bytes never enter the model's context.
- **412 (chat assistant, attached photo):** if the chat app's code sandbox has outbound network, the 418 flow applies. Many chat sandboxes have none. In that case **no agent route exists** for a multi-megabyte attachment to reach a remote MCP server, because base64 would not fit in context (421). The tool descriptions then tell the assistant to ask the user to drop the photo onto the board in the Kitepost app. The point is that the assistant says "I couldn't add it" rather than claiming success.
- **421 (base64):** declined. See "Decisions".

## Decisions made without the owner (please review)

1. **No base64 or inline input, even for small images.** The skill guidance allows inline bytes for "genuinely tiny" content. But a 100 KB image is still about 35–50k tokens of base64, and adding it would not fix 412 for real photos. A smaller tool set made the call. This is easy to add later as a separate tool with a hard cap of about 64 KB if you want it.
2. **No byte-accepting route on the HTTP API.** API clients use the same signed-PUT flow as the browser. A `multipart/form-data` convenience route would be easier for one-line scripts, but it would route up to 20 MB through our server functions. The CLI gives scripts the one-liner instead.
3. **The `upload_image` name is retired**, not kept with a new schema. Clients that cached the old catalog will get an unknown-tool error. That is better than a silent broken upload. Previously "uploaded" zero-byte images from the old tool should be found (images with `size = 0`) and cleaned up. That cleanup is a separate, approval-gated data task and has not been done here.
4. **URL import is synchronous**, with a 20 s timeout and `https:` only.
5. **The signed URL expires after 15 minutes** and is bound to one key, type, and length. The URL appears in the model's context and transcript. That is acceptable for a short-lived, single-object, write-only capability.
6. **Captions are out of scope.** None of the new tools take a caption, the same as the old tool. Captions should be added to the shared capability as a follow-up so every surface gets them together.
7. **The MCP package no longer writes to object storage.** `packages/mcp/src/storage.ts` was only used by the old tool, so it was deleted. The MCP server holds no storage credentials.

## Open questions

- **Upload host reachability.** Sandboxes often allowlist outbound hosts. Should the bucket be served from a product-owned upload host (for example `uploads.kitepost.example`) so that one hostname can be allowlisted and the storage provider can be swapped without breaking sandboxes? Doing that needs a DNS change, so it needs your approval.
- **MCP file inputs.** Do any target MCP hosts support passing a user attachment to a remote server out of band, without the bytes going through the model? If one does, it would fix 412 properly. We should test this against each supported host.
- **Rate limits** for `create_image_upload` and `image-imports` belong at the edge. The numbers are not decided yet.

````

> Result: File created successfully at: <run>\builds\4-upload-without-byte-route-old-opus2\work\docs\upload-design.md (file state is current in your context — no need to Read it back)

**Assistant:** Now the product client and the tool.

**Tool call `Write`:** `<run>\builds\4-upload-without-byte-route-old-opus2\work\packages\mcp\src\product.ts`

````text
export const ACCEPTED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp", "image/gif"] as const;
export type ImageContentType = (typeof ACCEPTED_IMAGE_TYPES)[number];
export const MAX_IMAGE_BYTES = 20 * 1024 * 1024;

/** Shared image resource, same shape as the HTTP API and CLI. */
export type Image = {
  id: string;
  board_id: string;
  filename: string;
  content_type: ImageContentType;
  size_bytes: number;
  url: string;
};

export type UploadSession = {
  upload_id: string;
  put_url: string;
  put_headers: Record<string, string>;
  expires_at: string;
};

export type ImageRefusal =
  | { code: "board_not_found" }
  | { code: "forbidden" }
  | { code: "unsupported_type"; contentType: string }
  | { code: "too_large"; sizeBytes: number }
  | { code: "quota_exceeded"; neededBytes: number; remainingBytes: number }
  | { code: "url_not_allowed"; reason: "scheme" | "address" }
  | { code: "url_unreachable"; status?: number }
  | { code: "url_not_image"; detectedType?: string }
  | { code: "upload_not_found" }
  | { code: "upload_expired" }
  | { code: "upload_missing_bytes" }
  | { code: "upload_size_mismatch"; declaredBytes: number; storedBytes: number }
  | { code: "upload_type_mismatch"; declaredType: string; detectedType?: string };

export type Outcome<T> = { ok: true; value: T } | { ok: false; refusal: ImageRefusal };

type Caller = { userId: string };

export const images = {
  /** Authorizes, checks type, size, and quota, records a pending upload, and signs a single PUT. */
  async createUpload(
    caller: Caller,
    input: { boardId: string; filename: string; contentType: string; sizeBytes: number },
  ): Promise<Outcome<UploadSession>> {
    throw new Error("wired to the product API at runtime");
  },
  /** Verifies the stored object's size and type, attaches it to the board, charges usage. Idempotent. */
  async finalizeUpload(caller: Caller, input: { uploadId: string }): Promise<Outcome<Image>> {
    throw new Error("wired to the product API at runtime");
  },
  /** Fetches a public https URL server-side with SSRF and size protections, then finalizes it. */
  async importFromUrl(
    caller: Caller,
    input: { boardId: string; sourceUrl: string },
  ): Promise<Outcome<Image>> {
    throw new Error("wired to the product API at runtime");
  },
};

````

> Result: The file <run>\builds\4-upload-without-byte-route-old-opus2\work\packages\mcp\src\product.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>\builds\4-upload-without-byte-route-old-opus2\work\packages\mcp\src\tools\upload-image.ts`

````text
import { z } from "zod";
import {
  ACCEPTED_IMAGE_TYPES,
  MAX_IMAGE_BYTES,
  images,
  type Image,
  type ImageRefusal,
  type Outcome,
} from "../product";

// Kitepost's MCP server is remote: it cannot read paths on the caller's machine or sandbox,
// and it never handles image bytes itself. Bytes reach storage by server-side URL fetch or
// by the caller PUTting to a signed URL. See docs/upload-design.md.

const MB = 1024 * 1024;
const ACCEPTED = "PNG, JPEG, WebP, or GIF";
const NO_ROUTE_HINT =
  "If you cannot make an HTTP request from where the file is, tell the user the image was not added and ask them to drop it onto the board in the Kitepost app.";

const boardId = z.string().min(1).describe("Board ID, for example Hq3k9TmPx2Ab");

type Ctx = { userId: string };

function formatMb(bytes: number) {
  return `${(bytes / MB).toFixed(1)} MB`;
}

function refusalMessage(r: ImageRefusal): string {
  switch (r.code) {
    case "board_not_found":
      return "No board with that ID is available to you. Check the board ID.";
    case "forbidden":
      return "You can view this board but not add images to it. Ask the board owner for edit access.";
    case "unsupported_type":
      return `The file is ${r.contentType}. Kitepost accepts ${ACCEPTED}.`;
    case "too_large":
      return `The image is ${formatMb(r.sizeBytes)}. The limit is ${formatMb(MAX_IMAGE_BYTES)} per image.`;
    case "quota_exceeded":
      return `The image needs ${formatMb(r.neededBytes)} but only ${formatMb(r.remainingBytes)} of storage is left. Remove images or upgrade the plan.`;
    case "url_not_allowed":
      return r.reason === "scheme"
        ? "Kitepost only fetches public https:// URLs. For a local or sandbox file, use create_image_upload."
        : "That URL points to a private or internal address. Use a public https:// URL, or upload the file with create_image_upload.";
    case "url_unreachable":
      return `Kitepost could not download the URL${r.status ? ` (HTTP ${r.status})` : ""}. Check that it is public, or upload the file with create_image_upload.`;
    case "url_not_image":
      return `The URL did not return a ${ACCEPTED} image${r.detectedType ? ` (got ${r.detectedType})` : ""}.`;
    case "upload_not_found":
      return "No upload with that ID. Start again with create_image_upload.";
    case "upload_expired":
      return "The upload URL expired before the file arrived. Start again with create_image_upload.";
    case "upload_missing_bytes":
      return "No file has arrived for this upload yet. PUT the file to put_url with put_headers, then call finalize_image_upload again.";
    case "upload_size_mismatch":
      return `The stored file is ${r.storedBytes} bytes but ${r.declaredBytes} were declared. Start again with create_image_upload using the file's exact size.`;
    case "upload_type_mismatch":
      return `The stored file is not ${r.declaredType}${r.detectedType ? ` (looks like ${r.detectedType})` : ""}. Start again with the correct content_type.`;
  }
}

function toResult<T>(outcome: Outcome<T>, onOk: (value: T) => string) {
  if (!outcome.ok) {
    return { ok: false as const, code: outcome.refusal.code, message: refusalMessage(outcome.refusal) };
  }
  return { ok: true as const, message: onOk(outcome.value), result: outcome.value };
}

function added(image: Image) {
  return `Added ${image.filename} (${formatMb(image.size_bytes)}) to the board.`;
}

export const addImageFromUrl = {
  name: "add_image_from_url",
  description:
    "Add an image to a board from a public https URL; Kitepost downloads it. " +
    `Accepts ${ACCEPTED} up to ${formatMb(MAX_IMAGE_BYTES)}. ` +
    "Local paths, sandbox: paths, and base64 are not accepted; for a file you hold, use create_image_upload.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
  inputSchema: z.object({
    board_id: boardId,
    url: z
      .string()
      .url()
      .describe("Public https:// URL of the image. Not a local path, sandbox: path, or data: URL."),
  }),
  async run(input: { board_id: string; url: string }, ctx: Ctx) {
    const outcome = await images.importFromUrl(ctx, { boardId: input.board_id, sourceUrl: input.url });
    return toResult(outcome, added);
  },
};

export const createImageUpload = {
  name: "create_image_upload",
  description:
    "Start uploading an image file from your sandbox or workspace to a board. " +
    "Returns a signed put_url: PUT the raw file bytes there with put_headers (for example with the returned curl command), " +
    "then call finalize_image_upload. The image is not on the board until finalize succeeds. " +
    `Accepts ${ACCEPTED} up to ${formatMb(MAX_IMAGE_BYTES)}. Do not send base64. ${NO_ROUTE_HINT}`,
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
  inputSchema: z.object({
    board_id: boardId,
    filename: z.string().min(1).max(255).describe("File name to show on the board, for example chart.png"),
    content_type: z.enum(ACCEPTED_IMAGE_TYPES).describe("MIME type of the file"),
    size_bytes: z
      .number()
      .int()
      .positive()
      .max(MAX_IMAGE_BYTES)
      .describe("Exact file size in bytes, for example from `stat` or `wc -c`"),
  }),
  async run(
    input: { board_id: string; filename: string; content_type: string; size_bytes: number },
    ctx: Ctx,
  ) {
    const outcome = await images.createUpload(ctx, {
      boardId: input.board_id,
      filename: input.filename,
      contentType: input.content_type,
      sizeBytes: input.size_bytes,
    });
    if (!outcome.ok) return toResult(outcome, () => "");
    const session = outcome.value;
    const headerFlags = Object.entries(session.put_headers)
      .map(([k, v]) => `-H '${k}: ${v}'`)
      .join(" ");
    const curl = `curl -fsS -X PUT ${headerFlags} --data-binary @<path-to-file> '${session.put_url}'`;
    return {
      ok: true as const,
      message:
        `Upload ready, expires ${session.expires_at}. Nothing is on the board yet. ` +
        `PUT the file, then call finalize_image_upload with upload_id ${session.upload_id}.`,
      result: { ...session, curl },
    };
  },
};

export const finalizeImageUpload = {
  name: "finalize_image_upload",
  description:
    "Finish an image upload after the file was PUT to its put_url: Kitepost checks the stored file and adds it to the board. " +
    "Safe to call again; returns the same image.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  inputSchema: z.object({
    upload_id: z.string().min(1).describe("upload_id returned by create_image_upload"),
  }),
  async run(input: { upload_id: string }, ctx: Ctx) {
    const outcome = await images.finalizeUpload(ctx, { uploadId: input.upload_id });
    return toResult(outcome, added);
  },
};

export const imageUploadTools = [addImageFromUrl, createImageUpload, finalizeImageUpload];

````

> Result: The file <run>\builds\4-upload-without-byte-route-old-opus2\work\packages\mcp\src\tools\upload-image.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-upload-without-byte-route-old-opus2/work\" && git rm -q packages/mcp/src/storage.ts && grep -rn \"storage\\\"\" packages; git status --short; ls node_modules 2>/dev/null | head"}`

> Result:  M packages/mcp/src/product.ts D  packages/mcp/src/storage.ts  M packages/mcp/src/tools/upload-image.ts ?? docs/upload-design.md

**Assistant:** I've written the design to `docs/upload-design.md` and rewritten the MCP tool to match it. Nothing has been compiled or run: the repo has no installed dependencies, `zod` isn't listed in `packages/mcp/package.json`, and there's no tsconfig or test setup. I haven't committed anything.

## What caused 412 and 418
The tool took a file path and read it on Kitepost's own MCP server, which is remote. It can never see a file in the agent's sandbox (`/mnt/data/...`, `sandbox:/...`). When the read failed, the tool quietly used an empty file, saved a zero-byte image to the board and reported success. It also wrote straight to storage, skipping the product API's size, type, quota and authorization checks, which breaks the brief's rule that every surface goes through the same product API.

## The design
- **No server route accepts image bytes.** Files get in one of two ways:
  - **From a public `https` URL:** Kitepost downloads the image itself, with protections against URLs that point at internal addresses, and a 20 MB / 20 s cap.
  - **From a file the caller holds:** the caller asks for a signed upload URL, sends the file there directly, then calls finalize. This is the same flow the browser app already uses.
- **The upload only counts once finalize checks it.** Finalize confirms the stored file exists and matches the declared size and type, adds it to the board, and only then charges storage. Calling it twice returns the same image.
- **HTTP API:** three routes:
  - `POST /v1/boards/{id}/uploads`
  - `POST /v1/uploads/{id}/finalize`
  - `POST /v1/boards/{id}/image-imports`
- **CLI:** `kitepost upload <board> <file...>` reads local files (the only place a path makes sense) and runs the same three steps, reporting each file separately. `kitepost import <board> <url>` covers URLs.
- **MCP:** `upload_image` is replaced by `add_image_from_url`, `create_image_upload` (returns the upload URL plus a ready-made `curl` command) and `finalize_image_upload`. The descriptions tell agents never to use local paths or base64, and to report an image as added only after the final call succeeds.

## Code changes
- **`packages/mcp/src/tools/upload-image.ts`:** now holds the three tools. Each calls the product API and turns its refusal codes into messages that say what was measured and what to do next.
- **`packages/mcp/src/product.ts`:** new placeholder functions (`createUpload`, `finalizeUpload`, `importFromUrl`), the shared image type and the refusal codes. Like the old ones, they still need wiring to the real product API.
- **`packages/mcp/src/storage.ts`:** deleted. Only the old tool used it, and the MCP server no longer needs storage access.

## Calls I made for you (also listed in the doc)
1. **421 is declined:** no base64 input, even for small images. A 100 KB image is still tens of thousands of tokens, and base64 wouldn't fix 412 for real photos anyway. A separate tool capped at about 64 KB could be added later.
2. **The HTTP API has no file-upload route.** API users use the signed upload like the browser does; the CLI gives scripts a one-line option.
3. **The `upload_image` name is retired.** Agents that remember the old tool will get an "unknown tool" error, which beats a fake success.
4. **Smaller defaults:**
   - URL import runs synchronously and only accepts `https`.
   - Signed upload URLs expire after 15 minutes.
   - Captions are out of scope for now.

## Still open
- **412 isn't fully fixed.** Many chat assistants' sandboxes have no internet access. For those, an attached photo can't reach Kitepost through the agent at all. The tools now make the assistant say the image wasn't added and ask the user to drop it on the board in the app. Whether any chat apps can hand an attachment to a remote MCP server without the model carrying the bytes still needs testing.
- **Broken images from the old tool need cleaning up.** They're the images with size 0. That's a data change I haven't touched; it needs your go-ahead.
- **Upload hostname:** should uploads go through a Kitepost-owned hostname like `uploads.kitepost.example`? Sandboxes that only allow listed hosts could then add one name. It needs a DNS change, so I left it for you.
- **Rate-limit numbers** for creating uploads and URL imports aren't set yet.

**Session ended:** success, 11 turns, 171780 ms
