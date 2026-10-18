I've written the design to `docs/quota-accounting.md` and rewritten `packages/backend/src/uploads.ts` to match, with supporting changes in `ctx.ts` and `errors.ts`. The code passes a strict TypeScript check. Nothing has been run: there are no tests and no real database or storage behind `Ctx`, and I haven't committed anything.

**What was broken, and what I changed:**
1. **Parallel uploads could go over the cap.** Eight CLI uploads started at once each saw the same usage and each passed. Starting an upload now reserves its size inside a transaction, and the cap check counts other uploads that have started but not finished. A reservation expires after 6 hours, and a new `cancelUpload` releases it immediately.
2. **Retrying finalize charged the user twice.** It also queued a second paid summary. Finalize now does nothing if the upload is already done, and the summary job is queued in the same transaction that marks the upload done, so each upload gets exactly one.
3. **Concurrent finalizes could lose an increment** to the account's usage. That update now happens inside the transaction.
4. **The client's declared size was trusted.** The signed upload URL is now locked to that exact size, and finalize charges the size actually stored, not the declared one.
5. **Bytes uploaded but never finalized stayed in storage forever without being charged.** A new `sweepUnfinalizedUploads` deletes them once the reservation has expired plus 24 hours. It is written so it can't race a late finalize.
6. **Anyone could finalize anyone's upload.** Finalize and cancel now check that the upload belongs to the caller.

**How summaries count:** they take no space against the storage cap. A summary is created only after a successful finalize, and failed summaries are never retried automatically.

**Assumptions to confirm:**
- `ctx.db.transaction` runs transactions one at a time against the same rows, retrying on conflict, and jobs queued inside it only run if it commits. That is how Convex mutations behave. I typed `Ctx` to say so and added `storage.head`, `storage.delete` and a size-locked `signPut`; the real adapters have to provide them.
- A reservation lasts 6 hours, and unfinished bytes are deleted 24 hours after that.
- The largest allowed file is 5 GiB, because that's the most one signed upload can carry. I set this from the storage limit, not as a product decision.
- Summary text doesn't count against the cap.
- Files in the trash count against the cap until they are permanently deleted. There is no delete code yet; the doc sets out the rules for it.
- `clientRequestId` on `startUpload` is optional, so existing clients keep working. It is what stops a retried start from holding a second reservation.

**Your call before launch:** uploading and deleting files in a loop never fills the cap, but each upload costs a paid summary. I recommend a hidden per-account limit on summaries plus rate limiting at the edge. How many summaries to allow is a cost decision, so I didn't pick a number.

**Still to do:**
- Schedule the sweep to run regularly, for example hourly.
- Update the CLI (not in this repo) to send a `clientRequestId` per file and reuse it on retries, and to call `cancelUpload` when interrupted.
- Make the summary job exit without doing anything when a summary already exists, so a manual retry can't bill twice.