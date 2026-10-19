I wrote the design to `docs/upload-design.md` and rewrote `packages/mcp/src/tools/upload-image.ts` to match it. I didn't type-check anything: the repo has no installed dependencies or TypeScript config. I only ran a quick Node script to check the input sorting (results below). Nothing is committed.

## Why the bugs happened
The old tool ran `readFile` on the MCP server's own disk. The paths in 412 (`/mnt/data/...`) and 418 (`sandbox:/...`) only exist inside the caller's sandbox, so the read failed. The tool then stored an empty file and still reported success. It also skipped the type, size and quota checks. And it was a security hole: any caller could put a file from the server's disk onto a board.

## The design
Everything goes through two shared steps in the product API: a direct upload with a signed PUT, and a server-side fetch from a URL. Both end in the same finalize. Finalize checks the actual stored size and file type, charges storage once, and returns the image only after it really exists.

- **HTTP API:**
  - Start an upload with `POST /v1/boards/{id}/uploads`, which returns a signed PUT URL.
  - Send the bytes straight to storage with that PUT.
  - Finish with `POST /v1/uploads/{id}/complete`.
  - Import from a link with `POST /v1/boards/{id}/images {source_url}`.
  - Files are never base64-encoded into JSON.
- **CLI:** `kitepost upload <board_id> <file|url...>` uses those routes and reports each file separately. It also works inside an agent's sandbox if it has network access, which is the route for 418.
- **MCP:** `upload_image { board_id, url, filename? }` takes only `https://` URLs. Kitepost downloads the image itself, with the usual protections for fetching a URL someone hands us. Local paths, `sandbox:`/`file:` URIs and `data:`/base64 input are refused before anything happens. The error says why and lists what works instead: a URL, the CLI, or dragging the file into the browser app. A refusal never claims success. Tested inputs: `/mnt/data/photo.jpg`, `sandbox:/...`, `C:\...`, `~/...`, `file:` and `data:` are refused, `http:` gets a "wrong scheme" refusal, and `https:` goes through.

## What happens to each report
- **412:** The broken-image-plus-success-message bug is fixed. But chat attachments still can't reach Kitepost through MCP. That needs an adapter per chat host that turns its attachment into a URL we can fetch, and I haven't confirmed which hosts allow that. The tool has one place where such adapters can plug in.
- **418:** Fixed. The agent uses the CLI or HTTP API from its sandbox, or passes a URL.
- **421:** Declined. A 6 MB photo becomes about 8 MB of base64, which the model would have to write out token by token. That's how the teammate ran out of context.

## Assumptions to confirm
- **Chat attachments (412):** no adapter for any chat host yet. Which hosts matter most is your call.
- **API key in sandboxes:** agents using the CLI need a `KITEPOST_API_KEY`, because the MCP login isn't passed into the sandbox. Short-lived upload keys issued through MCP would be smoother but are deferred.
- **Numbers I picked (not in the brief):** URL import waits for the download to finish, with a 20-second timeout and up to 3 redirects. Upload slots and signed URLs expire after 15 minutes.
- **No `caption` argument** on the tool for now. Adding one later won't break anything.
- **MCP wrapper:** I assumed the code that registers tools (not in this repo) shows the tool's `{ ok: false, error }` result as a tool error.
- **`product.ts`:** I added `importFromUrl` and the result types there, alongside the existing placeholders. The real fetching, quota and finalize logic belongs in the product API, which isn't in this repo yet. The tool no longer calls `allocateKey`, `create` or `storage.put`, but I left them in place in case something else uses them.