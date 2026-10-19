I've written the design to `docs/upload-design.md` and rewritten the MCP tool to match it. Nothing has been compiled or run: the repo has no installed dependencies, `zod` isn't listed in `packages/mcp/package.json`, and there's no tsconfig or test setup. I haven't committed anything.

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