**Prompt:** not recorded by this session. The case in the committed `evals.json` may have changed since.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-upload-without-byte-route-old-opus/work\" && git ls-files && cat docs/brief.md docs/issues.md && cat packages/mcp/src/tools/upload-image.ts"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6918 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-upload-without-byte-route-old-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/uploads.md $R/model-context-protocol.md $R/agent-tool-design.md; cat packages/mcp/src/product.ts packages/mcp/src/storage.ts packages/mcp/package.json package.json"}`

> Result: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 11103 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-upload-without-byte-route-old-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/abuse-resistance.md $R/http-apis.md $R/object-storage.md $R/quota.md $R/user-facing-errors.md $R/modularity.md"}`

> Result: # Abuse Resistance  A product reachable from the open internet is a target on day one. Bound what a single caller can cost the product before finding out the hard way.  ## Quota As Anti-Abuse Plumbing  Hold two different numbers, not one. A hidden internal quota, sized to the max load the product can absorb, applies to every account regardless of plan and stays invisible. A user-facing plan  [... 15789 more characters]

**Tool call `Write`:** `<run>\builds\1-upload-without-byte-route-old-opus\work\packages\mcp\src\product.ts`

````text
export const images = {
  /** Returns a fresh opaque storage key for a new image on a board the user can edit. */
  async allocateKey(userId: string, boardId: string): Promise<string> {
    throw new Error("wired to the product API at runtime");
  },
  /** Records a stored image on a board. */
  async create(input: { boardId: string; key: string; size: number }): Promise<void> {
    throw new Error("wired to the product API at runtime");
  },
};

export const ACCEPTED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp", "image/gif"] as const;
export type ImageContentType = (typeof ACCEPTED_IMAGE_TYPES)[number];
export const MAX_IMAGE_BYTES = 20 * 1024 * 1024;

/** The shared image resource returned by every surface. */
export type Image = {
  id: string;
  board_id: string;
  filename: string;
  content_type: ImageContentType;
  size_bytes: number;
  url: string;
};

export type UploadFailureCode =
  | "board_not_found"
  | "forbidden"
  | "too_large"
  | "unsupported_type"
  | "quota_exceeded"
  | "upload_not_found"
  | "upload_expired"
  | "bytes_missing"
  | "size_mismatch"
  | "type_mismatch"
  | "url_blocked"
  | "url_unreachable";

export type UploadFailure = {
  ok: false;
  code: UploadFailureCode;
  /** Product-owned, actionable copy. Never a raw provider or exception message. */
  message: string;
};

export type PendingUpload = {
  upload_id: string;
  put_url: string;
  required_headers: Record<string, string>;
  expires_at: string;
};

/**
 * Shared upload capability. The browser app, HTTP API, CLI, and MCP server all call these;
 * authorization, type and size limits, quota, and the storage write-ahead ledger live behind them.
 */
export const uploads = {
  /** Checks access, type, size, and quota, registers the key, and signs a single PUT for exactly these bytes. */
  async begin(input: {
    userId: string;
    boardId: string;
    filename: string;
    contentType: ImageContentType;
    sizeBytes: number;
  }): Promise<({ ok: true } & PendingUpload) | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
  /** Verifies the stored object (present, declared size, sniffed type), publishes the image, and charges quota. Idempotent. */
  async finalize(input: { userId: string; uploadId: string }): Promise<{ ok: true; image: Image } | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
  /** Server-side fetch of a public http(s) URL with SSRF, redirect, timeout, and size guards, then finalize. */
  async importFromUrl(input: {
    userId: string;
    boardId: string;
    url: string;
    filename?: string;
  }): Promise<{ ok: true; image: Image } | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
  /** Stores small inline bytes through the same begin/finalize rules. Callers enforce the inline cap. */
  async storeInline(input: {
    userId: string;
    boardId: string;
    filename: string;
    bytes: Uint8Array;
  }): Promise<{ ok: true; image: Image } | UploadFailure> {
    throw new Error("wired to the product API at runtime");
  },
};

````

> Result: The file <run>\builds\1-upload-without-byte-route-old-opus\work\packages\mcp\src\product.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>\builds\1-upload-without-byte-route-old-opus\work\packages\mcp\src\tools\upload-image.ts`

````text
import { z } from "zod";
import { ACCEPTED_IMAGE_TYPES, MAX_IMAGE_BYTES, uploads, type UploadFailure } from "../product";

// This server is remote. It cannot read files on the caller's machine or sandbox, so no tool
// takes a path. Bytes arrive by server-fetched URL, by a signed PUT the caller performs, or,
// for tiny images only, inline. See docs/upload-design.md.

/** Inline bytes are generated token by token, so they are reserved for genuinely tiny images. */
export const MAX_INLINE_BYTES = 64 * 1024;

type Ctx = { userId: string };

const boardId = z.string().describe("Stable ID of the board, e.g. Hq3k9TmPx2Ab");
const filename = z.string().min(1).max(255).describe("File name to show on the board, e.g. chart.png");

const NOT_A_PATH =
  "Kitepost's server cannot read files on your machine or sandbox. " +
  "If the file has a public https URL, pass that URL. Otherwise call create_image_upload, " +
  "PUT the file from where it lives, then call finalize_image_upload.";

function looksLikeLocalPath(value: string): boolean {
  return !/^https?:\/\//i.test(value);
}

function refuse(code: UploadFailure["code"], message: string): UploadFailure {
  return { ok: false, code, message };
}

export const addImageFromUrl = {
  name: "add_image_from_url",
  description:
    "Add an image to a board from a public http(s) URL. Kitepost downloads it server-side. " +
    "Preferred when the image is already online. PNG, JPEG, WebP, or GIF up to 20 MB. Not for local file paths.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
  inputSchema: z.object({
    board_id: boardId,
    url: z.string().describe("Public http or https URL of the image. Local paths and sandbox: links do not work."),
    filename: filename.optional(),
  }),
  async run(input: { board_id: string; url: string; filename?: string }, ctx: Ctx) {
    if (looksLikeLocalPath(input.url)) return refuse("url_blocked", NOT_A_PATH);
    return uploads.importFromUrl({
      userId: ctx.userId,
      boardId: input.board_id,
      url: input.url,
      filename: input.filename,
    });
  },
};

export const createImageUpload = {
  name: "create_image_upload",
  description:
    "Create an image upload for a board and get a signed URL to PUT the file to. " +
    "Use for a file on your machine or sandbox: PUT the raw bytes with the returned headers " +
    "(e.g. curl -T file -H ... put_url), then call finalize_image_upload. PNG, JPEG, WebP, or GIF up to 20 MB.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
  inputSchema: z.object({
    board_id: boardId,
    filename,
    content_type: z.enum(ACCEPTED_IMAGE_TYPES),
    size_bytes: z.number().int().positive().describe("Exact file size in bytes, e.g. from `wc -c < file`"),
  }),
  async run(
    input: { board_id: string; filename: string; content_type: (typeof ACCEPTED_IMAGE_TYPES)[number]; size_bytes: number },
    ctx: Ctx,
  ) {
    if (input.size_bytes > MAX_IMAGE_BYTES) {
      return refuse("too_large", `The file is ${input.size_bytes} bytes. Kitepost accepts images up to 20 MB.`);
    }
    const pending = await uploads.begin({
      userId: ctx.userId,
      boardId: input.board_id,
      filename: input.filename,
      contentType: input.content_type,
      sizeBytes: input.size_bytes,
    });
    if (!pending.ok) return pending;
    return {
      ...pending,
      next_step:
        "PUT the file's raw bytes (not base64, not multipart) to put_url with exactly required_headers " +
        "before expires_at, then call finalize_image_upload with upload_id. The image is not on the board until finalized.",
    };
  },
};

export const finalizeImageUpload = {
  name: "finalize_image_upload",
  description:
    "Finalize an image upload after its bytes were PUT to the signed URL, and add the image to the board. " +
    "Returns the image. Safe to call again for the same upload.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false },
  inputSchema: z.object({
    upload_id: z.string().describe("upload_id returned by create_image_upload"),
  }),
  async run(input: { upload_id: string }, ctx: Ctx) {
    return uploads.finalize({ userId: ctx.userId, uploadId: input.upload_id });
  },
};

export const uploadSmallImage = {
  name: "upload_small_image",
  description:
    "Upload a tiny image (64 KB or less) to a board as inline base64. " +
    "For anything larger use add_image_from_url or create_image_upload, which do not spend context on the bytes.",
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: false },
  inputSchema: z.object({
    board_id: boardId,
    filename,
    data_base64: z.string().describe("Base64 of the image bytes, 64 KB decoded at most"),
  }),
  async run(input: { board_id: string; filename: string; data_base64: string }, ctx: Ctx) {
    const encoded = input.data_base64.replace(/^data:[^,]*,/, "").replace(/\s+/g, "");
    if (!/^[A-Za-z0-9+/]*={0,2}$/.test(encoded) || encoded.length === 0) {
      return refuse("unsupported_type", "data_base64 is not valid base64. Pass only the base64 of the image file.");
    }
    const bytes = Buffer.from(encoded, "base64");
    if (bytes.length > MAX_INLINE_BYTES) {
      return refuse(
        "too_large",
        `The image is ${bytes.length} bytes; inline upload takes up to ${MAX_INLINE_BYTES}. ` +
          "Use create_image_upload and PUT the file, or add_image_from_url if it is online.",
      );
    }
    return uploads.storeInline({
      userId: ctx.userId,
      boardId: input.board_id,
      filename: input.filename,
      bytes,
    });
  },
};

export const imageUploadTools = [addImageFromUrl, createImageUpload, finalizeImageUpload, uploadSmallImage];

````

> Result: The file <run>\builds\1-upload-without-byte-route-old-opus\work\packages\mcp\src\tools\upload-image.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/1-upload-without-byte-route-old-opus/work/packages/mcp/src\" && sed -i 's/  | \"board_not_found\"/  | \"invalid_input\"\\n  | \"board_not_found\"/' product.ts && sed -i 's/return refuse(\"url_blocked\", NOT_A_PATH)/return refuse(\"invalid_input\", NOT_A_PATH)/; s/return refuse(\"unsupported_type\", \"data_base64/return refuse(\"invalid_input\", \"data_base6 [... 130 more characters]`

> Result: product.ts:27:  | "invalid_input" tools/upload-image.ts:41:    if (looksLikeLocalPath(input.url)) return refuse("invalid_input", NOT_A_PATH); tools/upload-image.ts:116:      return refuse("invalid_input", "data_base64 is not valid base64. Pass only the base64 of the image file.");

**Assistant:** No dependencies are installed (there's no zod or TypeScript in the repo), so I can't typecheck. Now the design doc:

**Tool call `Write`:** `<run>\builds\1-upload-without-byte-route-old-opus\work\docs\upload-design.md`

````text
# Getting images into Kitepost

Status: proposed 2026-10-17, addresses bug reports 412, 418, 421. Assumptions awaiting the owner are listed at the end.

## What went wrong

`upload_image { board_id, path }` called `readFile(path)` **on the MCP server**. The MCP server is remote (`mcp.kitepost.example/mcp`). The agent's file lives in a chat app's sandbox (`/mnt/data/photo.jpg`, 412) or a coding agent's sandbox (`sandbox:/workspace/out/chart.png`, 418), and our server cannot see either one. The read failed, the error was swallowed into an empty buffer, a 0-byte image was stored, and the tool reported `Uploaded photo.jpg`. Result: a broken image and a false success.

The same code was also an **arbitrary file read on the MCP host**: any path the server process could read, such as `/proc/self/environ` or a mounted secret, would be copied onto the caller's board. The rewrite removes it. See follow-ups.

421 (base64 input) is the opposite failure. An inline blob is generated token by token, so a 6 MB photo (about 8 MB of base64) cannot fit in context.

## Principles

1. **A remote server never takes a file path.** No surface except the CLI, which runs on the user's machine, reads a local path, and the CLI reads it locally.
2. **One upload capability, many adapters.** The browser flow the brief describes (sign a PUT, upload bytes directly to object storage, finalize) becomes the shared product capability `uploads.*`. The HTTP API, CLI, and MCP server translate to it. Authorization, the 20 MB / type limits, quota, and the storage ledger are enforced there once (brief: "every surface goes through the same product API and the same authorization").
3. **Bytes go out of band.** Primary inputs are a URL the server fetches, or a signed PUT straight to storage. Inline bytes are only for tiny images.
4. **Success means the image landed.** A tool or endpoint reports success only after finalize has confirmed the stored object is present, has the declared size, and sniffs as an accepted type. It returns the resulting image.
5. **Originals are stored as uploaded.** Nothing is recompressed or transcoded (brief).

## Shared product capability

Signatures are in `packages/mcp/src/product.ts` (stubs wired to the product API at runtime).

| Capability | Does |
| --- | --- |
| `uploads.begin(board, filename, content_type, size_bytes)` | Checks edit access, accepted type, size ≤ 20 MB, and quota headroom (gate before). Records the object key in the write-ahead ledger and creates a **pending** image row, then signs one PUT bound to that key, `Content-Type`, and `Content-Length`, valid for 15 minutes. Returns `upload_id`, `put_url`, `required_headers`, `expires_at`. |
| `uploads.finalize(upload_id)` | HEADs the object and checks that it exists and that its size equals the declared size. Sniffs the magic bytes against the declared type, marks the image ready, and charges quota (charge after). Idempotent: a second call returns the same image. |
| `uploads.importFromUrl(board, url, filename?)` | Server-side fetch, then the same begin/finalize rules. Guards: https/http only, DNS resolved and checked before connecting (no private, loopback, link-local, or metadata ranges, re-checked on each redirect), at most 3 redirects, 30 s total timeout, streamed with a hard 20 MB cut-off, `Content-Length` pre-checked against quota when present. Synchronous. Returns the landed image. |
| `uploads.storeInline(board, filename, bytes)` | Same rules for small bytes the server already holds. Callers cap the size. |

Pending rows are invisible on boards, so an abandoned upload never shows as a broken image. A sweep removes pending uploads older than 24 h, along with their objects, through the ledger.

Typed failure codes: `invalid_input`, `board_not_found`, `forbidden`, `too_large`, `unsupported_type`, `quota_exceeded`, `upload_not_found`, `upload_expired`, `bytes_missing`, `size_mismatch`, `type_mismatch`, `url_blocked`, `url_unreachable`. Each carries product-owned copy that names the measurement and the next step, for example "The file is 24117248 bytes. Kitepost accepts images up to 20 MB." Raw storage and fetch errors stay in logs.

## HTTP API (`api.kitepost.example/v1`)

Same flow as the browser, published in the OpenAPI contract:

```
POST /v1/boards/{board_id}/uploads        {filename, content_type, size_bytes}
  -> 201 {upload_id, put_url, required_headers, expires_at}
PUT  {put_url}   (raw bytes, straight to object storage, no API key needed)
POST /v1/uploads/{upload_id}/finalize
  -> 200 {image}

POST /v1/boards/{board_id}/images:import  {url, filename?}
  -> 201 {image}
```

**No byte-carrying route on the API.** No multipart or base64 body goes through `api.kitepost.example`. The signed PUT already gives HTTP clients a normal raw-file upload (`curl -T photo.jpg`) without proxying 20 MB bodies through serverless functions. This is a deliberate decision, not an omission.

## CLI (`npx kitepost`)

```
kitepost upload --board <board_id> <file>...     # local files
kitepost upload --board <board_id> --url <url>   # server-side import
```

- Thin client over the HTTP API, authenticated with `KITEPOST_API_KEY` or `kitepost login`.
- For each file it stats the file, sniffs the type locally, calls create, PUTs, and finalizes. It refuses wrong types or files over 20 MB before any network call.
- Several files run with concurrency 4. Each file gets its own result line in input order, failures are reported inline, and the exit code is non-zero if any file failed. `--json` prints one image or error object per file.
- This is the only surface that reads local paths, because it runs where the files are.

## MCP server (`mcp.kitepost.example/mcp`)

Implemented in `packages/mcp/src/tools/upload-image.ts`. There are four single-purpose tools rather than one tool with `path | url | base64` modes, because agents pick the wrong argument more often than the wrong tool.

| Tool | When the agent should use it |
| --- | --- |
| `add_image_from_url {board_id, url, filename?}` | The image is already at a public URL. Cheapest path. Non-http(s) input (`/mnt/...`, `sandbox:...`, `file:...`) is refused with copy that points to the upload tools. |
| `create_image_upload {board_id, filename, content_type, size_bytes}` | The file is in the agent's sandbox or on the user's machine and the agent can make an outbound HTTP request (shell, Python, code interpreter). Returns the signed PUT, its headers, and a `next_step` instruction. This fixes 418, and 412 wherever the chat sandbox has network egress. |
| `finalize_image_upload {upload_id}` | After the PUT. Returns the image. Idempotent. If the bytes never arrived it returns `bytes_missing` with instructions instead of creating a broken image. |
| `upload_small_image {board_id, filename, data_base64}` | Answer to 421: inline base64, capped at **64 KB decoded**. Over the cap, it is refused with the measured size and the alternatives. The description and schema hints steer agents to the out-of-band tools first. |

All four are annotated as non-read-only and non-destructive. They only add images. `add_image_from_url` is open-world. `finalize_image_upload` is idempotent. One static catalog is advertised to every caller, and authorization is enforced per call by the product API.

The signed `put_url` will appear in the agent transcript. It is a narrow bearer capability: one key, a fixed size and type, 15 minutes, and nothing is published without an authenticated finalize. That is acceptable.

## How each report resolves

- **412**: If the chat sandbox can reach the internet, the agent uses create → PUT → finalize. If it cannot, the PUT fails, finalize returns `bytes_missing`, and the agent tells the user truthfully that it could not upload, so the user can drag the file into the web app. In neither case does an empty image appear or a false success get reported.
- **418**: The coding agent has a shell, so it can `curl -T chart.png` to the signed URL, then finalize.
- **421**: Inline base64 is supported for images of 64 KB or less. A 6 MB photo goes through the signed PUT, which costs a few hundred tokens instead of millions.

## Assumptions made without the owner (please confirm)

1. **`upload_image` is removed outright**, with no deprecated alias. It never worked for remote callers, and it was a security hole. Clients that cached the old catalog will get "unknown tool" until they reconnect. The alternative is a stub that always returns guidance, which keeps a dead tool in the catalog.
2. **Inline cap of 64 KB decoded** (about 87 KB of base64, tens of thousands of tokens). It could be lower. Raising it brings back 421.
3. **No multipart/byte route on the HTTP API.** The signed PUT is the file-upload path for scripts too.
4. **URL import is synchronous** with a 30 s budget. That is enough for 20 MB from a reasonable host. If slow origins become common, it would become a background job that returns `202` plus a job to poll.
5. **Signed PUT lifetime of 15 min, pending-upload sweep at 24 h.**
6. **Quota is gated at begin and charged at finalize**, against the 2 GB free plan limit. Abandoned uploads are never charged.
7. **Some chat hosts' sandboxes have no network egress.** For those, no MCP design can move a large attached file, because MCP has no client-to-server file transfer today. The fallback is the web app. If a target host later exposes attachments as fetchable URLs, `add_image_from_url` covers it.
8. The existing direct `storage.put` from the MCP package is no longer used by the tool. All writes go through `uploads.*`.

## Follow-ups (not done, need the owner)

- **Audit MCP server logs** for `upload_image` calls whose `path` pointed anywhere other than an image (for example `/proc`, `/etc`, `.env`, or credential mounts). If any exist, treat it as a possible disclosure and rotate the secrets on that host.
- **Existing broken images**: image rows with `size = 0` created by the old tool. Proposed: delete them and notify the affected users. I did not touch this because it deletes user-visible rows.
- Implement `uploads.*` in the product API and move the browser app onto it. The browser flow is the same, so this is a refactor, not a behaviour change.
- Add the HTTP routes to the OpenAPI contract and add the CLI `upload` command.
- Test against each supported agent host: confirm that the agent picks `create_image_upload` for a sandbox file and that the PUT succeeds from that host's sandbox.

````

> Result: File created successfully at: <run>\builds\1-upload-without-byte-route-old-opus\work\docs\upload-design.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. Nothing has been typechecked or run: the repo has no dependencies installed, and the product functions the tools call are still stubs.

**What caused 412 and 418:** the MCP server is remote, but the old `upload_image` read `path` from the server's own disk. It could never see the agent's `/mnt/data/...` or `sandbox:/...` file. The read error was swallowed, so it stored an empty image and still reported success.

**Security problem in the old code:** because it read any path from the server's disk, a caller could have copied files like `/proc/self/environ` or a mounted secret onto their own board. The rewrite removes this. I recommend checking the MCP logs for `upload_image` calls whose `path` wasn't an image.

**The design:** every surface uses the browser app's existing flow (sign an upload, send the bytes straight to storage, then finalize) through one shared set of upload functions. Those enforce access, the 20 MB limit and accepted types, and the storage quota in one place. An image counts as added only after finalize confirms the bytes are stored, the size matches and the file really is an accepted type.

- **HTTP API:**
  - `POST /v1/boards/{id}/uploads` returns a signed upload URL.
  - The client `PUT`s the raw file to that URL.
  - `POST /v1/uploads/{id}/finalize` returns the image.
  - `POST /v1/boards/{id}/images:import {url}` adds an image from a URL, which Kitepost downloads with protections against fetching internal addresses.
  - No route carries file bytes through the API itself.
- **CLI:** `kitepost upload --board <id> <file...>` or `--url <url>`. It's the only surface that reads local paths, because it runs on the user's machine. It handles several files at once, reports each one, and exits non-zero if any failed.
- **MCP:** four separate tools instead of one tool with modes:
  - `add_image_from_url` for images already online.
  - `create_image_upload`, then `finalize_image_upload`, for a file in the agent's sandbox. The agent can send it with something like `curl -T`. This fixes 418, and 412 when the chat sandbox has internet access.
  - `upload_small_image` for base64 of up to 64 KB, which answers 421. Anything bigger gets an error giving the size and pointing to the other tools.

  Errors tell the agent what to do next. For example, passing a local path explains that the server can't read it.

I also added stub signatures for the shared upload functions, the limits and the image type to `packages/mcp/src/product.ts`. The tool no longer uses `storage.ts`.

**Calls I made that you should confirm:**
1. I removed `upload_image` with no deprecated alias. Clients that cached the old tool list will get "unknown tool" until they reconnect.
2. Inline base64 is capped at 64 KB.
3. The HTTP API has no byte-upload route; the signed upload is the only file path.
4. Importing from a URL waits for the download to finish, with a 30 s limit.
5. Signed upload URLs last 15 minutes, and unfinished uploads are cleaned up after 24 h.
6. Quota is checked when an upload starts and charged only after finalize, so abandoned uploads cost nothing.
7. Some chat apps' sandboxes have no internet access. There, no MCP design can move a large attached file, so the agent should say the upload failed and the user should drag the file into the web app.

**Not done, needs you:**
- Deciding what to do with the existing empty (0-byte) images from 412 and 418. I left them because removing them deletes rows users can see.
- Building the shared upload functions in the product API.
- The new HTTP routes in the OpenAPI document, and the CLI command.
- Testing with each supported agent app.

Nothing is committed.

**Session ended:** success, 10 turns, 453406 ms
