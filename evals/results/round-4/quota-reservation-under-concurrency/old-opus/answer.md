I've written the accounting design to `docs/quota-accounting.md` and rewritten `packages/backend/src/uploads.ts` to match. The code passes a strict TypeScript check, but nothing has run against a real database or object storage, and there are no tests. I haven't committed anything.

**What was wrong before:**
- **Concurrent uploads could go over the cap.** The cap was checked when an upload started but only charged when it finished. The CLI's 8 parallel uploads all saw the same free space and could all pass.
- **Usage could drift low.** The finalize step read usage, added to it and wrote it back, so two uploads finishing together could lose one of the additions.
- **Retries were charged twice.** When the CLI retried a finalize that had actually succeeded, the size was added again and a second paid summary was queued.
- **Usage came from the size the client declared.** The client could declare 1 byte and store gigabytes.
- **Finalize didn't check ownership.** Anyone with an upload's ID could finalize another account's upload.

**How it works now:**
- **Starting an upload reserves space.** Each account has `used` and `reserved`, and their total can't exceed the cap. The check and the reservation happen together in one transaction, so parallel uploads that don't fit are refused before any bytes move.
- **The signed upload URL fixes the file's length.**
- **Finalize charges once, from the actual stored size.** It checks ownership and the size of the stored file, then moves the bytes from `reserved` to `used` and queues the summary in the same transaction. If the upload is already done, finalize does nothing more, so retries are safe.
- **Abandoned uploads give their space back.** A new scheduled cleanup, `releaseExpiredUploads`, releases reservations for uploads never finalized within about 75 minutes and deletes their bytes.
- **Summaries don't count against the storage cap.** Each upload queues one summary at most, and a failed summary is only retried when the user asks, because each one costs money.

**Assumptions** (full list in the doc):
- **Transactions:** the database's transactions are serializable and queuing the summary job commits along with them, as in Convex. If the real job queue doesn't work that way, the doc describes a fallback.
- **Storage:** I added `head` and `delete` to the storage interface. `signPut` now takes the file size and URL lifetime. The real storage adapter has to enforce the length in the signed URL.
- **Size mismatch:** if the stored file isn't exactly the declared size, the upload fails rather than being charged the actual size.
- **Timings and empty files:** URLs last 15 minutes plus a 1-hour grace period, and zero-byte files are rejected. Both are easy to change.
- **Data changes:** `accounts.reserved` and several upload fields are new and need indexes and a backfill. Existing `used` values may already be wrong because of the old bugs, so they should be recomputed from finished uploads before launch.

**Decisions for you:**
- **Summary spending limit.** The storage cap doesn't limit how many paid summaries an account can trigger. With a free plan open to everyone you need a separate hidden limit, plus rate limiting. I didn't pick numbers.
- **What "10 GB" means.** Is it 10×10⁹ or 10×2³⁰ bytes? The code just reads the stored cap.
- **Client update.** The CLI and MCP clients should send the new optional `clientRequestId` when starting an upload. Without it, a retried start holds an extra reservation until it expires, which can wrongly refuse uploads near the cap.
- **Deleting files.** There is no delete flow yet, so free users can't free up space. I wrote the accounting rule for when one is built.
- **Error messages.** The new error types still need user-facing wording.