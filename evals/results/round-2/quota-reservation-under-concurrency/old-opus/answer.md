I wrote the design to `docs/quota-accounting.md` and rewrote `packages/backend/src/uploads.ts` to match. `ctx.ts` and `errors.ts` changed too. A strict TypeScript check passes, but there are no tests and nothing has run against a real database or storage. Nothing is committed.

**Problems I found in the old flow:**
1. **Parallel uploads overshot the cap.** The CLI's 8 parallel uploads all checked against the same usage figure and all passed, because usage only went up at finalize.
2. **Retries were charged twice.** A retried finalize added the file size again and queued a second paid summary.
3. **The client's declared size was trusted.** It could declare 1 byte and upload gigabytes.
4. **Finalize didn't check ownership.** Any account could finalize another account's upload.
5. **Summaries had no limit.** That's the real cost risk once the free plan opens to everyone.

**How it works now:**
- **Reserve at start.** Starting an upload checks "used + all pending uploads + this file ≤ cap" and creates the pending upload in one transaction, so parallel starts take turns and can't overshoot.
- **Settle once at finalize.** Finalize checks that the stored file exists and matches the declared size, then marks it ready and adds its size to usage in one transaction. A repeated finalize changes nothing, and the summary job is queued in that same transaction, so it can't be queued twice or lost.
- **Releasing reservations.** A pending upload holds its space until it's finalized, cancelled (new `cancelUpload`), or cleaned up by a new sweep after 24 hours. If the sweep stops running, users get blocked rather than given free storage.
- **Retries of start.** Start accepts an optional `idempotencyKey`, so a retried start returns the same upload instead of reserving space again.

**Summaries:** they don't count against the storage cap, so "10 GB" means 10 GB of your files. They get their own hidden ceiling per account per 30 days, on every plan. If it's reached, the upload still succeeds and the summary is marked as failed for quota. Deleting a file doesn't give the summary back, so uploading and deleting the same file can't produce unlimited summaries.

**Assumptions to check (also listed in the doc):**
- **Summary ceiling.** I set 500 per 30 days as a placeholder. Please set the real number from what each summary costs.
- **Transactions.** The database runs transactions one at a time in effect (serializable), and queuing a job inside one only happens if it commits, as Convex does. If that isn't true, the cap check can still be raced.
- **Storage.** I added `head`, `delete` and a size-bound `signPut` to `ctx.ts`. They're standard on S3/R2, but the storage code still has to implement them.
- **Reservation window.** I set it to 24 hours, with signed upload links lasting 15 minutes.

**Still needed before launch:**
- **Schedule the sweep** (`sweepAbandonedUploads`). Until it runs, abandoned uploads never release their space.
- **Update the CLI and MCP tools** to send `idempotencyKey` and to call `cancelUpload` when they give up on a file.
- **Make delete reduce usage** in the same transaction that removes the file.
- **Add abuse limits:** a per-file size limit, a limit on pending uploads per account, and rate limiting.