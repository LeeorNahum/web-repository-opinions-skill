I've written the design to `docs/quota-accounting.md` and updated `packages/backend/src/uploads.ts` to match. To make it work I also had to change `ctx.ts` (new storage and database methods) and `errors.ts` (typed error codes). The new code compiles with `tsc --strict`, but there are no tests, nothing has run against a real database or storage, and nothing is committed.

**What was wrong before:**
- **Parallel uploads could overshoot the cap.** The CLI's 8 parallel uploads (or an agent over MCP) were each checked against the same usage figure, so all of them could pass and together go over 10 GB.
- **A retried finish counted twice.** A retried `finalizeUpload` added the file's size to usage a second time and queued a second paid summary.
- **Usage trusted the client.** It was charged from the size the client declared, which nothing enforced.
- **Abandoned uploads leaked.** An upload that was started but never finished could still land bytes in storage that were never counted.
- **Any caller could finalize anyone's upload.** There was no ownership check, so one account could charge another and trigger a paid summary.

**How it works now:**
- **Reservations.** Starting an upload reserves its declared size. The check is `used + open reservations + requested <= cap`, done in a single database operation per account so parallel starts are admitted one at a time. Reservations are worked out from in-progress upload records rather than kept as a running total, so an expired one stops counting immediately.
- **Expiry.** Each reservation expires after 1h15m. The upload link stops working 15 minutes earlier and locks the file length to the declared size.
- **Charging.** At finalize the server checks the stored file's actual size, refuses it if it's bigger than declared, and charges the actual size once. A repeated finalize charges nothing.
- **Retries.** `startUpload` accepts an optional `idempotencyKey`, so a CLI retry after a timeout gets the same reservation back instead of a second one.
- **Cleanup.** A new `expireAbandonedUploads` function marks expired uploads as failed and deletes any bytes that arrived late.

**Assumptions to confirm (also listed in the doc):**
1. **Summaries don't count against the storage cap.** They're small generated text, and counting them would push accounts over the cap after an upload was already accepted. Their cost is controlled by a separate per-account spend limit that users never see.
2. **That spend limit is US$3 per account per month.** This is a placeholder; please set the real number before launch.
3. **Each file is limited to 2 GiB.** That keeps uploads within a single request; anything larger needs a multipart upload flow.
4. **An account can have at most 16 uploads in progress at once.**
5. **Empty files are refused.**
6. **`idempotencyKey` is optional**, so existing clients keep working. Without it, a retried start holds an extra reservation until it expires; that can block uploads for a while but never overcharges. You may want to make it required before launch.
7. **"10 GB" means 10⁹ bytes per GB**, not GiB.

**Not built yet:**
- Nothing schedules `expireAbandonedUploads` yet.
- The summary job doesn't exist in the repo. The doc defines how it should reserve cost against the spend limit, record actual cost, never retry automatically, and ignore duplicate queue entries.
- Deleting files doesn't subtract from usage yet.
- The CLI and MCP clients don't send `idempotencyKey` yet, and they don't map the new error codes to user-facing messages.
- No tests have been written.
- The code assumes the database runs each account's reservation and finalize steps one after another, and that the storage layer can lock the upload length and look up a stored file's size. The doc lists exactly what's needed.