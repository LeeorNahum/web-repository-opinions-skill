I wrote the design to `docs/quota-accounting.md` and rewrote `packages/backend/src/uploads.ts` to match. I had to extend `ctx.ts` and `errors.ts` too. The code passes a strict TypeScript check. There are no tests in the repo, so none of this has been run, and the storage adapter and summary job it relies on aren't in the repo either. Nothing is committed.

## What was wrong with the current flow
1. **Parallel uploads could go over the cap.** The CLI uploads 8 files at once. Each start checked `used` before any of them finished, so an account with 1 GB free could upload 8 GB.
2. **The size the client claimed was trusted.** The signed URL accepted any amount of data, and usage was charged with the claimed size. A caller could claim 1 byte and store 5 GB.
3. **A retried finalize counted twice.** When the CLI retried a timed-out finalize, the size was added again and a second paid summary was queued.
4. **Usage could be overwritten.** `used` was read and written back without a transaction, so two finalizes at once could lose one update.
5. **No ownership check on finalize.** Any account could finalize another account's upload.
6. **Summary cost had no limit.** Filling 10 GB with tiny files would mean millions of paid model calls.

## The design
- **Reserve, then charge.** `startUpload` checks `used + reserved + size <= cap` and adds the size to `reserved` in one transaction. Finalize moves it to `used` only after checking the stored file's real size. Every counter change happens in the same transaction as the upload status change it belongs to.
- **Signed URLs are tied to the exact size,** so storage rejects a file of any other size.
- **Retries are safe.** Finalizing an upload that's already finished just returns the same result. `startUpload` takes an optional `requestId`, so a retried start gets the same reservation back.
- **Abandoned uploads release their space.** A new job, `releaseExpiredReservations`, frees reservations still unfinished after 6 hours (signed URLs last 1 hour). It's safe to run while finalizes are happening.
- **Summaries are queued exactly once,** when the upload finishes. They have a hidden limit of 500 per account per day. A summary over the limit is marked `held`, and the user can start it with the new `requestSummary`. Summaries never retry automatically.

## Assumptions to confirm (also listed in the doc)
1. **Summaries don't count toward the 10 GB cap.** The cap stays "bytes of files you uploaded". This is the main call I made for you, and changing it is small.
2. **The database supports atomic transactions** (`ctx.db.transaction`), plus two lookups that need indexes.
3. **The storage service can sign a URL for an exact size, check a file's size, and delete files.** I added these to `Ctx.storage`.
4. **The numbers are mine:** 5 GB per file, 500 summaries a day, 1-hour URLs, 6-hour reservations. Empty files are rejected.

## Still to do
- Migrate existing accounts: add `reserved` and the summary counters, and recompute `used`, because the double-counting bug may have inflated it.
- Schedule `releaseExpiredReservations` (every 15 minutes is suggested).
- In the summary job (not in the repo), mark a queued summary as running atomically so duplicate queue entries are harmless.
- Make deletion reduce `used` (deletion doesn't exist yet).
- Have the CLI and MCP clients send a `requestId` for each file.
- Add per-request rate limits at the gateway before launch.
- Add tests for parallel uploads at the cap, double finalize, finalize racing the cleanup job, a size mismatch, and the summary limit.