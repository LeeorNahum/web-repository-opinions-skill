**Prompt:** Design how uploads and summaries are counted against the storage cap (see docs/brief.md), write it to docs/quota-accounting.md, and update packages/backend/src/uploads.ts to match. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus2/work\" && git ls-files && cat docs/brief.md && cat packages/backend/src/uploads.ts"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6076 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/quota.md $R/uploads.md $R/billing.md $R/abuse-resistance.md $R/failure-and-retries.md; cat packages/backend/src/ctx.ts packages/backend/src/errors.ts packages/backend/package.json package.json"}`

> Result: # Quota  Check quota before doing expensive work, reserve it when concurrent requests could oversubscribe it, charge usage only after durable success, and release whatever the work did not use.  - Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known. - For imported files, read metadata first and block early if it cannot fit. - For li [... 12638 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/background-jobs.md $R/user-facing-errors.md | head -120; ls node_modules 2>&1 | head -3"}`

> Result: # Background Jobs  Provider-backed and long-running work runs as explicit jobs with explicit state, never as fire-and-forget calls scattered through route handlers.  Design every job around its failure point, not its happy path. Ask:  - What if the external call succeeds and the database update fails? - What if the row exists but the provider object does not? - What if the user closes the  [... 2994 more characters]

**Assistant:** Now writing the errors, ctx contract, and implementation.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus2/work/packages/backend/src\" && cat > errors.ts <<'EOF'\n// Expected failures carry a product-owned code. The presentation boundary maps\n// each code to copy; `message` stays internal.\nexport class ProductError extends Error {\n  constructor(readonly code: string, readonly details: Record<string, number> = { [... 2312 more characters]`

> Result: (Bash completed with no output)

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-new-opus2\work\packages\backend\src\uploads.ts`

````text
import type { Ctx } from "./ctx";
import {
  InvalidUpload,
  QuotaExceeded,
  SummaryNotRetryable,
  TooManyOpenUploads,
  UploadFailed,
  UploadNotFound,
  UploadNotReceived,
  UploadTooLarge,
} from "./errors";

// Product limits. See docs/quota-accounting.md for why each value was chosen.
export const MAX_UPLOAD_BYTES = 5 * 1024 ** 3;
export const MAX_OPEN_UPLOADS = 16;
export const RESERVATION_TTL_MS = 2 * 60 * 60 * 1000;

// Internal per-account summary spend ceiling, in millionths of a US dollar per UTC
// calendar month. Never shown to users.
export const SUMMARY_SPEND_LIMIT_MICROS = 2_000_000;
export const SUMMARY_ATTEMPT_ESTIMATE_MICROS = 20_000;

type Upload = {
  id: string;
  accountId: string;
  name: string;
  size: number;
  status: "pending" | "ready" | "failed";
  expiresAt: number;
  clientRequestId?: string;
  storedSize?: number;
  summaryStatus?: "queued" | "ready" | "failed" | "paused";
  summaryAttemptId?: string;
};

type SummaryAttempt = {
  id: string;
  status: "reserved" | "succeeded" | "failed";
  estimatedMicros: number;
  costMicros?: number;
};

// Bytes held by open reservations that have not expired, optionally ignoring one upload.
async function liveReservedBytes(tx: any, accountId: string, now: number, exceptId?: string) {
  const pending: Upload[] = await tx.uploads.listPendingByAccount(accountId);
  const live = pending.filter((u) => u.expiresAt > now && u.id !== exceptId);
  return { count: live.length, bytes: live.reduce((total, u) => total + u.size, 0) };
}

export async function startUpload(
  ctx: Ctx,
  input: { name: string; size: number; clientRequestId?: string },
) {
  if (!Number.isSafeInteger(input.size) || input.size <= 0) throw new InvalidUpload();
  if (input.size > MAX_UPLOAD_BYTES) throw new UploadTooLarge({ maxBytes: MAX_UPLOAD_BYTES });

  const now = Date.now();
  const upload: Upload = await ctx.db.transaction(async (tx: any) => {
    // A retried request with the same id gets the same reservation back, not a second one.
    if (input.clientRequestId) {
      const existing: Upload | null = await tx.uploads.findByClientRequestId(ctx.accountId, input.clientRequestId);
      if (existing && existing.size === input.size && (existing.status === "ready" || existing.expiresAt > now)) {
        return existing;
      }
    }

    const account = await tx.accounts.get(ctx.accountId);
    const reserved = await liveReservedBytes(tx, ctx.accountId, now);
    if (reserved.count >= MAX_OPEN_UPLOADS) throw new TooManyOpenUploads({ maxOpen: MAX_OPEN_UPLOADS });
    if (account.used + reserved.bytes + input.size > account.cap) {
      throw new QuotaExceeded({ cap: account.cap, remaining: Math.max(0, account.cap - account.used - reserved.bytes) });
    }

    return tx.uploads.insert({
      accountId: ctx.accountId,
      name: input.name,
      size: input.size,
      status: "pending",
      expiresAt: now + RESERVATION_TTL_MS,
      clientRequestId: input.clientRequestId,
      createdAt: now,
    });
  });

  if (upload.status !== "pending") return { uploadId: upload.id, status: upload.status };
  if (upload.status === "pending" && upload.expiresAt <= now) throw new UploadFailed("abandoned");
  // The URL dies with the reservation and only accepts the declared size.
  const url = await ctx.storage.signPut(upload.id, { contentLength: upload.size, expiresAt: upload.expiresAt });
  return { uploadId: upload.id, status: upload.status, url, expiresAt: upload.expiresAt };
}

export async function finalizeUpload(ctx: Ctx, input: { uploadId: string }) {
  const upload: Upload | null = await ctx.db.uploads.get(input.uploadId);
  if (!upload || upload.accountId !== ctx.accountId) throw new UploadNotFound();

  // A retried finalize charges nothing again; it only makes sure the summary job was enqueued.
  if (upload.status === "ready") {
    await enqueueSummary(ctx, upload);
    return { uploadId: upload.id, status: upload.status };
  }
  if (upload.status === "failed") throw new UploadFailed((upload as any).failureKind ?? "abandoned");

  const stored = await ctx.storage.head(upload.id);
  if (!stored) {
    if (upload.expiresAt <= Date.now()) {
      await ctx.db.uploads.patch(upload.id, { status: "failed", failureKind: "abandoned" });
      throw new UploadFailed("abandoned");
    }
    throw new UploadNotReceived();
  }
  if (stored.size > upload.size || stored.size > MAX_UPLOAD_BYTES) {
    await ctx.db.uploads.patch(upload.id, { status: "failed", failureKind: "size_mismatch" });
    await ctx.storage.delete(upload.id);
    throw new UploadFailed("size_mismatch");
  }

  const outcome: "ready" | "quota_exceeded" = await ctx.db.transaction(async (tx: any) => {
    const current: Upload = await tx.uploads.get(upload.id);
    if (current.status === "ready") return "ready";
    if (current.status !== "pending") throw new UploadFailed((current as any).failureKind ?? "abandoned");

    const now = Date.now();
    const account = await tx.accounts.get(ctx.accountId);
    // A lapsed reservation no longer holds room, so the bytes must fit next to everyone else's.
    if (current.expiresAt <= now) {
      const others = await liveReservedBytes(tx, ctx.accountId, now, current.id);
      if (account.used + others.bytes + stored.size > account.cap) {
        await tx.uploads.patch(current.id, { status: "failed", failureKind: "quota_exceeded" });
        return "quota_exceeded";
      }
    }

    // Charge the measured size, once, in the same transaction that closes the reservation.
    await tx.accounts.patch(account.id, { used: account.used + stored.size });
    await tx.uploads.patch(current.id, { status: "ready", storedSize: stored.size, finalizedAt: now });
    await admitSummaryAttempt(tx, ctx.accountId, current.id, now);
    return "ready";
  });

  if (outcome === "quota_exceeded") {
    await ctx.storage.delete(upload.id);
    throw new UploadFailed("quota_exceeded");
  }
  await enqueueSummary(ctx, await ctx.db.uploads.get(upload.id));
  return { uploadId: upload.id, status: "ready" as const };
}

// Reserves one summary attempt's estimated cost against the account's internal monthly
// spend ceiling. Unsettled attempts count at their estimate, settled ones at their recorded cost.
async function admitSummaryAttempt(tx: any, accountId: string, uploadId: string, now: number) {
  const attempts: SummaryAttempt[] = await tx.summaryAttempts.listByAccountSince(accountId, startOfUtcMonth(now));
  const spent = attempts.reduce(
    (total, a) => total + (a.status === "reserved" ? a.estimatedMicros : (a.costMicros ?? a.estimatedMicros)),
    0,
  );
  if (spent + SUMMARY_ATTEMPT_ESTIMATE_MICROS > SUMMARY_SPEND_LIMIT_MICROS) {
    await tx.uploads.patch(uploadId, { summaryStatus: "paused", summaryFailureKind: "spend_limit" });
    return;
  }
  const attempt = await tx.summaryAttempts.insert({
    accountId,
    uploadId,
    status: "reserved",
    estimatedMicros: SUMMARY_ATTEMPT_ESTIMATE_MICROS,
    createdAt: now,
  });
  await tx.uploads.patch(uploadId, { summaryStatus: "queued", summaryAttemptId: attempt.id, summaryFailureKind: undefined });
}

async function enqueueSummary(ctx: Ctx, upload: Upload) {
  if (upload.summaryStatus !== "queued" || !upload.summaryAttemptId) return;
  // Keyed by attempt, so a retried finalize never starts a second paid run.
  await ctx.jobs.enqueue("summarize", { uploadId: upload.id, attemptId: upload.summaryAttemptId }, { key: upload.summaryAttemptId });
}

// User-initiated only. Paid summary work is never retried automatically.
export async function retrySummary(ctx: Ctx, input: { uploadId: string }) {
  const upload: Upload | null = await ctx.db.uploads.get(input.uploadId);
  if (!upload || upload.accountId !== ctx.accountId) throw new UploadNotFound();

  await ctx.db.transaction(async (tx: any) => {
    const current: Upload = await tx.uploads.get(upload.id);
    if (current.status !== "ready" || (current.summaryStatus !== "failed" && current.summaryStatus !== "paused")) {
      throw new SummaryNotRetryable();
    }
    await admitSummaryAttempt(tx, ctx.accountId, current.id, Date.now());
  });

  const current: Upload = await ctx.db.uploads.get(upload.id);
  await enqueueSummary(ctx, current);
  return { uploadId: current.id, summaryStatus: current.summaryStatus };
}

// Called by the summarize job when a provider attempt ends, successful or not. Records what
// the attempt actually cost; repeated calls for the same attempt change nothing.
export async function settleSummaryAttempt(
  ctx: Ctx,
  input: { attemptId: string; outcome: "succeeded" | "failed"; costMicros: number },
) {
  await ctx.db.transaction(async (tx: any) => {
    const attempt = await tx.summaryAttempts.get(input.attemptId);
    if (!attempt || attempt.status !== "reserved") return;
    await tx.summaryAttempts.patch(attempt.id, { status: input.outcome, costMicros: input.costMicros, settledAt: Date.now() });
    const upload: Upload | null = await tx.uploads.get(attempt.uploadId);
    if (upload?.summaryAttemptId === attempt.id) {
      await tx.uploads.patch(upload.id, {
        summaryStatus: input.outcome === "succeeded" ? "ready" : "failed",
        summaryFailureKind: input.outcome === "failed" ? "processing" : undefined,
      });
    }
  });
}

function startOfUtcMonth(now: number) {
  const d = new Date(now);
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1);
}

````

> Result: The file <run>\builds\4-quota-reservation-under-concurrency-new-opus2\work\packages\backend\src\uploads.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Edit`:** `<run>\builds\4-quota-reservation-under-concurrency-new-opus2\work\packages\backend\src\uploads.ts`

Replaced:

````text
  if (upload.status !== "pending") return { uploadId: upload.id, status: upload.status };
  if (upload.status === "pending" && upload.expiresAt <= now) throw new UploadFailed("abandoned");

````

With:

````text
  if (upload.status !== "pending") return { uploadId: upload.id, status: upload.status };

````

> Result: The file <run>\builds\4-quota-reservation-under-concurrency-new-opus2\work\packages\backend\src\uploads.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Assistant:** Now the design doc.

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-new-opus2\work\docs\quota-accounting.md`

````text
# Quota accounting

How uploads and AI summaries count against an account's storage cap and against Lanternfold's own costs. Implemented in `packages/backend/src/uploads.ts`.

## What was wrong

The old flow checked the cap in `startUpload` and added the size in `finalizeUpload`. That fails in four ways:

- **Concurrent uploads oversubscribe the cap.** The CLI starts 8 uploads at once. Each check sees the same `used`, so all 8 pass and together can go well over 10 GB.
- **Retries double-count.** A retried `finalizeUpload` added the size again and queued a second paid summary. A retried `startUpload` created a second upload.
- **The declared size was trusted.** The account was charged what the client *said* it would upload, and the signed URL accepted any number of bytes. A client could declare 1 byte and store 5 GB.
- **Lost updates.** `used` was read and then written back (`used + size`) outside a transaction, so two finalizes at the same moment could lose one charge.

Also: `finalizeUpload` did not check the upload belonged to the caller, and summaries had no cost limit at all.

## Two ledgers

1. **Storage allowance** (user-facing, 10 GB free). Counts the bytes of the user's documents.
2. **Summary spend** (internal, never shown). Counts what the model provider charges us per account.

### Do summaries count against the storage cap? No.

Summary text is small and Lanternfold generates it; the user didn't upload it. If it counted, the number the user sees would not match the files they uploaded, and an account near the cap could lose summaries on files it is allowed to store. What summaries really cost is provider spend, and the second ledger tracks that. **(Assumption, see below.)**

## Storage: reserve, then charge what was measured

```
account.used      bytes of finalized uploads (also counts trash, until permanently deleted)
open reservations sum of `size` over the account's uploads that are `pending` and not past `expiresAt`
```

**startUpload**, inside one transaction:

1. Reject a size that isn't a positive integer, or is over `MAX_UPLOAD_BYTES`.
2. If `clientRequestId` matches an existing upload that is still usable (same size, not expired or already ready), return that one. A timed-out request that the CLI retries gets the same reservation back, not a second one.
3. Reject if the account already has `MAX_OPEN_UPLOADS` live reservations.
4. Reject with `quota_exceeded` if `used + open reservations + size > cap`. The error includes `remaining`.
5. Insert the upload as `pending` with `expiresAt = now + RESERVATION_TTL_MS`. The upload row is the reservation.

Then sign a PUT URL that **expires at `expiresAt`** and **only accepts `Content-Length = size`**. No signed URL outlives its reservation.

Open reservations are worked out from the upload rows at read time. They are not kept as a separate counter, so an abandoned reservation stops counting once it expires, with no sweeper and no counter drift.

**finalizeUpload**:

1. The upload must belong to the caller.
2. Already `ready` → return success and charge nothing. Only make sure the summary job is enqueued (keyed, so it never runs twice). This covers a crash between commit and enqueue.
3. `head` the object to get the **measured** size. If nothing landed, return `upload_not_received` and leave it open until it expires (after that, it is `abandoned`). If the measured size is larger than declared (or larger than the per-item limit), fail it as `size_mismatch` and delete the object.
4. In one transaction: re-read the upload (a concurrent finalize may have won). If the reservation has lapsed, re-admit it only if the bytes still fit beside everyone else's live reservations; if they don't, fail it as `quota_exceeded` and delete the object. Otherwise do `used += measured size`, mark it `ready` with `storedSize`, and admit a summary attempt.

Charging happens once per upload, from the measured size, in the same transaction that closes the reservation.

### Over the cap

If usage is over the cap (because the plan shrank or the cap was lowered), every reservation is refused. Existing files stay readable and deletable. Deleting and permanent purging (not in this file) must subtract `storedSize` from `used` in the same transaction that removes the row. Trash counts toward the cap until it is purged.

## Summary spend: reserve, settle to actual cost

- When an upload finalizes, the same transaction admits one summary attempt. Spend for the current UTC month is the recorded cost of settled attempts plus the estimate of unsettled ones. If adding `SUMMARY_ATTEMPT_ESTIMATE_MICROS` would go over `SUMMARY_SPEND_LIMIT_MICROS`, the upload still succeeds, but its summary is `paused` (`spend_limit`) and no job is queued. Otherwise a `reserved` attempt row is inserted and the job is enqueued, keyed by attempt id.
- The summarize job calls `settleSummaryAttempt` with the real provider cost **whether it succeeded or failed**. A failed attempt costs the user's allowance nothing, but its cost is still counted against our spend. Settling twice does nothing.
- Unsettled attempts keep counting at their estimate until settled (they don't expire). A stuck job errs toward caution and frees up when the month rolls over.
- **No automatic retries of summaries.** `retrySummary` is user-initiated, only works from `failed` or `paused`, and goes through the same admission. The job runner must be set to zero automatic retries for `summarize`.

## Errors

Expected failures are `ProductError`s with a `code` (`errors.ts`). The presentation layer maps codes to copy. Suggested copy:

| code | user sees |
| --- | --- |
| `quota_exceeded` | "Not enough storage: this file needs X, you have Y free. Delete files to make room." (Only offer an upgrade if a bigger plan exists.) |
| `upload_too_large` | "Files can be up to 5 GB." |
| `too_many_open_uploads` | "Too many uploads in progress. Wait for some to finish." |
| `upload_not_received` | "The file didn't finish uploading. Try again." |
| `upload_failed:*` | Upload again (`abandoned`, `size_mismatch`) or free space (`quota_exceeded`) |
| summary `paused` | "Summary is paused for now. You can retry later." (Never mention the spend limit or its number.) |

## Storage, DB, and job contract this relies on

- `ctx.db.transaction(fn)` is **serializable** over everything `fn` reads and writes (Convex mutations are). Two concurrent `startUpload`s must not both see the same open reservations and both commit. On a database without this guarantee, lock the account row (`SELECT … FOR UPDATE`) first.
- `db.uploads`: `get`, `insert`, `patch`, `listPendingByAccount(accountId)`, `findByClientRequestId(accountId, id)` (returns the newest), indexed by `(accountId, status)` and `(accountId, clientRequestId)`.
- `db.summaryAttempts`: `get`, `insert`, `patch`, `listByAccountSince(accountId, ts)`, indexed by `(accountId, createdAt)`.
- `storage.signPut(id, { contentLength, expiresAt })` signs Content-Length into the URL (S3/R2 presigned PUT supports this). `storage.head` and `storage.delete` exist.
- `jobs.enqueue(name, payload, { key })` deduplicates by key.

## Assumptions to confirm

1. **Summaries don't count against the storage cap.** They count against an internal spend limit instead. If you'd rather count summary text as storage, add its byte length to `used` when it is settled.
2. **Per-file limit 5 GB** (`MAX_UPLOAD_BYTES`). This is the most a single signed PUT can take. Larger files need multipart, which isn't built yet. The brief gives no per-file limit.
3. **Reservation lifetime 2 hours** (`RESERVATION_TTL_MS`). That's long enough for 5 GB on a ~6 Mbps link. A slower upload expires, and its bytes still count if they fit when finalized.
4. **At most 16 open uploads per account** (`MAX_OPEN_UPLOADS`). That's twice the CLI's 8, to allow some retries.
5. **Internal spend limit $2.00 per account per UTC month, estimate $0.02 per summary**. Placeholders until real per-summary cost is known. They allow roughly 100 summaries a month on any plan. The summarize job should cap input length so one attempt can't cost far more than the estimate.
6. **`clientRequestId` is optional** for backward compatibility. The CLI and the MCP tool should always send one, a fresh value per file and the same value when retrying. Without it, a retried `startUpload` holds a duplicate reservation until it expires.
7. An expired, never-finalized upload whose bytes landed leaves an orphaned object behind. A periodic sweep should delete objects for `pending` uploads well past `expiresAt` and mark them `abandoned`. Quota stays correct without the sweep; it only reclaims storage that we pay for.
8. Not covered here: edge rate limiting, the delete/purge path, and the summarize job itself. All three must follow the contracts above.

````

> Result: File created successfully at: <run>\builds\4-quota-reservation-under-concurrency-new-opus2\work\docs\quota-accounting.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/quota-accounting.md` and rewrote `packages/backend/src/uploads.ts` to match. I also changed `ctx.ts` and `errors.ts`. Nothing has been compiled, typechecked or run: there's no `node_modules`, no tsconfig and no tests. The database, storage and job services are stand-ins, so this is code to review, not verified behavior. Nothing is committed.

**Problems in the old flow:**
- **Concurrent uploads:** the CLI's 8 parallel uploads each passed the cap check against the same usage figure, so together they could go well over 10 GB.
- **Retries:** a retried finalize charged the file again and queued a second paid summary. A retried start created a duplicate upload.
- **Trusted sizes:** the account was charged the size the client declared, and the signed URL accepted any number of bytes.
- **Lost charges:** usage was read and then written back outside a transaction, so one of two simultaneous finalizes could lose its charge.
- **Ownership:** finalize didn't check that the upload belonged to the caller.

**How it works now:**
- **Reserving space:** `startUpload` counts space already held by in-progress uploads, all in one transaction. Each upload's hold ends after 2 hours, and its signed URL expires at the same moment and only accepts the declared size.
- **Retried starts:** an optional `clientRequestId` makes a retried start return the same upload instead of holding space twice.
- **Finalizing:** `finalizeUpload` measures the stored file and charges that size exactly once. A retry charges nothing. It rejects files bigger than declared, deletes them, and fails uploads that never arrived.
- **Summaries:** each one is checked against a hidden monthly spend limit per account, and charged to it at what the provider actually billed, failed attempts included. Summaries are never retried automatically; `retrySummary` only runs when the user asks.
- **Errors:** failures carry a code that the app turns into its own wording, with suggested wording in the doc.

**Calls I made that you should confirm:**
1. **Summaries don't count against the 10 GB cap.** They're small and generated by us; their real cost is provider spend, which the hidden limit tracks.
2. **Per-file limit of 5 GB**, the most a single signed upload can take. The brief doesn't set one.
3. **2-hour hold and 16 in-progress uploads per account**, which is twice the CLI's 8.
4. **Spend limit of $2 per account per month, at $0.02 per summary.** These are placeholders until we know what a summary actually costs.
5. **The database, storage and jobs must support what this relies on:**
   - Transactions that stop two simultaneous uploads from both claiming the same free space.
   - Signed URLs that only accept the declared size.
   - A storage size lookup.
   - Job queuing that won't run the same summary twice.

   I added these to the types in `ctx.ts`; the doc lists the exact methods.

**Still to build:**
- **CLI and MCP tool:** both should send a `clientRequestId`, a new one per file and the same one on a retry.
- **Summary job:** it must call `settleSummaryAttempt` with the real cost and have automatic retries turned off.
- **Delete and purge:** these must subtract the file's stored size from usage. Files in trash count until they're purged.
- **Orphaned-file sweep:** a periodic cleanup should delete files from uploads that were never finished. Quota stays correct without it; it just saves storage we pay for.
- **Rate limiting:** also not built.

**Session ended:** success, 10 turns, 178676 ms
