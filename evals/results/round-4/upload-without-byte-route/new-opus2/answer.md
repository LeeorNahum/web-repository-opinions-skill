I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. Nothing has been typechecked or run: the repo has no tsconfig, no installed dependencies, and the product API behind the tool is still a stub. I haven't committed anything.

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