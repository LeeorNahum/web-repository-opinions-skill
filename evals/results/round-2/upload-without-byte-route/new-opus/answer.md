I've written the design to `docs/upload-design.md` and rewritten the MCP tool to match it. Nothing is committed. I couldn't run a type check because the package has no tsconfig and zod isn't installed. I did check that the input-classifying logic handles the exact inputs from the bug reports.

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