I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. Nothing has been typechecked or run: the repo has no dependencies installed, and the product functions the tools call are still stubs.

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