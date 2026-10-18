I wrote the design to `docs/quota-accounting.md` and rewrote `packages/backend/src/uploads.ts` to match. `uploads.ts` typechecks under strict TypeScript. Nothing has been run, and there are no tests: the backend package has no test runner or tsconfig. I haven't committed anything.

**What was broken in the current flow:**
- **Parallel uploads overshoot the cap.** `used` only grows at finalize, so all 8 CLI uploads could pass the cap check at once.
- **Retries count twice.** A retried `finalizeUpload` adds the bytes again and queues a second paid summary.
- **Concurrent finalizes lose updates.** Two finalizes can overwrite each other's change to `used`.
- **The size is never verified.** The client's declared size is trusted, so someone could declare 1 byte and upload gigabytes.
- **No ownership check.** Finalize doesn't check that the upload belongs to the caller, so anyone with an upload ID could charge another account.

**What the design does:**
- **Space is held at start.** Each account now tracks finalized bytes (`used`) and bytes held by unfinished uploads (`reserved`). `startUpload` rejects if `used + reserved + size > cap`, then holds the space. An optional `requestId` makes a retried start reuse its hold instead of taking a second one.
- **Finalize is safe to retry.** It checks ownership and does nothing if the upload is already finished. It also checks the real stored size and rejects a mismatch. On success it moves the bytes from `reserved` to `used` and queues exactly one summary.
- **Abandoned uploads are cleaned up.** A new function, `expireStaleUploads`, deletes uploads never finalized within 6 hours and gives their space back. Upload links stop working after 1 hour, so no upload can still land after cleanup.
- **Summaries don't count against the storage cap.** They're small generated text the user can't remove separately. Each upload gets one summary, and a failed one isn't retried automatically.

**What I assumed** (all listed in the doc):
- Each backend handler runs as one transaction, as in Convex. Without that, the counter updates have to become atomic increments.
- I added `head` and `delete` to the storage interface in `ctx.ts`, and `signPut` now takes the size and an expiry. Three new database lookups need indexes. The real storage and database code has to provide all of this.
- I picked the time limits and a cap of 32 unfinished uploads per account myself. They're constants in `uploads.ts`.
- `finalizeUpload` now returns `{ uploadId, status }` instead of nothing.

**Your decisions before the free launch:**
1. **Summary limit:** how many summaries an account can generate, separate from storage. This is the one that matters most. The storage cap doesn't limit summary spend, because someone can upload, delete and re-upload while staying under 10 GB and get unlimited paid summaries.
2. **Hidden storage ceiling:** a limit across all plans, as a safety net beneath the 10 GB plan cap.
3. **Rate limiting:** a limit on upload requests at the edge.
4. **Error wording:** the user-facing message for each new error.

**Not done:**
- The cleanup function isn't connected to a scheduler.
- The file-delete handler and the summary job don't exist in the repo yet. The doc says how they have to update the counters.
- To typecheck, I briefly wrote a config file to the system temp folder, outside this directory, then deleted it.