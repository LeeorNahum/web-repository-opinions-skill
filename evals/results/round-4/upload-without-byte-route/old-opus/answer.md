I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. I haven't committed anything, and nothing has been type-checked or run: the repo has no installed dependencies or tsconfig, and the product API calls are stubs that only work once wired up.

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