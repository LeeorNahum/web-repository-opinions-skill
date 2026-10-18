I've written the design to `docs/upload-design.md` and rewritten the MCP tool to match it. Nothing has been typechecked or run: the repo has no installed dependencies, and `packages/mcp/package.json` doesn't list `zod`, which the tool imports. I haven't committed anything.

## What caused 412 and 418
The MCP server is remote, so `readFile(path)` looked on Kitepost's own server for `/mnt/data/photo.jpg` and `sandbox:/workspace/...`. Those paths only exist in the agent's sandbox. The tool turned the failed read into an empty file, saved zero bytes and still said "Uploaded". It also wrote to storage itself, skipping the product API's checks on access, file type, size and storage quota.

## The design
- **Bytes never pass through a Kitepost server, and no surface writes to storage directly.** One product capability offers two ways in:
  - **Signed upload:** request an upload, send the file straight to storage with a short-lived signed URL, then confirm. This is the browser flow customers already like.
  - **URL import:** Kitepost fetches a public `https` URL itself, with protections against being pointed at internal addresses.
- **Checks happen before any bytes move:** type, the 20 MB limit and storage quota. Confirming then checks the stored file is really there, is the declared size and really is an image. Quota is charged only after that succeeds.
- **HTTP API:** `POST /v1/boards/{id}/uploads`, then the upload to storage, then `POST /v1/uploads/{id}/complete`; plus `POST /v1/boards/{id}/images/imports` for URLs. There is no endpoint that takes the file bytes themselves.
- **CLI:** `kitepost upload <board> <file>...` reads local files (where paths are real) and runs the signed upload; `kitepost import <board> <url>`. Each file gets its own result.
- **MCP:** `upload_image` is replaced by three tools in `packages/mcp/src/tools/upload-image.ts`:
  - `upload_image_from_url`
  - `create_image_upload`, which returns a ready-to-run `curl` command so the agent sends the file from its own sandbox and the bytes never enter the model's context
  - `complete_image_upload`, which is safe to retry

  Only an image that has actually landed gets reported as added. If an agent passes something that looks like a file path, it gets an explanation of what to do instead.
- **Per report:**
  - **418** is fixed.
  - **412** is fixed only if the chat assistant's sandbox can reach the internet. If it can't, nothing on our side can reach the file, so the tool now says so and points the user to drag-and-drop in the browser app.
  - **421 (base64)** is declined: a 6 MB photo becomes about 8 MB of text, far more than the assistant's context can hold.

## Calls I made without you
These are listed in the doc:
- I removed `upload_image` with no compatibility shim, because it never worked for any remote caller.
- There is no base64 input on any surface, not even for tiny images.
- URL import accepts `https` only and runs while the caller waits: 15 s timeout, up to 5 redirects.
- Signed URLs last 15 minutes, and unfinished uploads are cleaned up after 1 hour.
- I replaced the stubs in `packages/mcp/src/product.ts` with the new upload calls and their error codes, and deleted `packages/mcp/src/storage.ts`, since the MCP server shouldn't touch storage.
- I assumed the browser's existing upload flow is the same capability; I couldn't check because `apps/` is empty.

## Questions for you
- Should uploads go to a Kitepost-owned host such as `uploads.kitepost.example`? Agent sandboxes often allow only listed domains, and one stable domain would be easier to allow. It needs a DNS change, so I left it.
- Should tiny images be allowed as base64?
- Should uploads accept a caption?

The product API routes, CLI and cleanup job are designed in the doc but not built; this repo only contains the MCP package.