**Prompt:** Design how uploads and summaries are counted against the storage cap (see docs/brief.md), write it to docs/quota-accounting.md, and update packages/backend/src/uploads.ts to match. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work\" && git ls-files && cat docs/brief.md && cat packages/backend/src/uploads.ts"}`

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6076 more characters]

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/quota.md $R/uploads.md $R/abuse-resistance.md $R/failure-and-retries.md $R/background-jobs.md; cat packages/backend/src/ctx.ts packages/backend/src/errors.ts packages/backend/package.json package.json"}`

> Result: # Quota  Check quota before doing expensive work. Charge usage only after durable success.  - Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known. - For imported files, read metadata first and block early if it cannot fit. - For live capture where the final size is unknown, let work begin if time remains, warn near the limit, and st [... 7109 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/billing.md $R/ai-model-routing.md $R/bulk-actions.md $R/definition-of-done.md $R/source-of-truth.md | head -300"}`

> Result: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 16573 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work\" && ls packages/backend; git log --stat -3 | head -30"}`

> Result: package.json src commit 736f0bc8e386b33e3865b560db86f8c8bb1e9982 Author: eval <eval@example.invalid> Date:   Mon Oct 19 08:20:10 2026 -0400      skill   .claude/skills/web-repository-opinions/SKILL.md    | 175 +++++++++++++++++++++  .../web-repository-opinions/assets/vercel.json     |  10 ++  .../references/abuse-resistance.md                 |  15 ++  .../web-repository-opinions/references/admin. [... 1279 more characters]

**Assistant:** Now writing the code.

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\packages\backend\src\ctx.ts`

````text
export type Ctx = {
  accountId: string;
  // `transaction` runs `fn` atomically and serializably (retrying on conflict), so a read-check-write inside it
  // cannot interleave with another one touching the same rows. See docs/quota-accounting.md.
  db: any & { transaction<T>(fn: (tx: any) => Promise<T>): Promise<T> };
  storage: {
    // The signature binds the exact Content-Length, so the store rejects a PUT of any other size.
    signPut(uploadId: string, opts: { contentLength: number; expiresInSeconds: number }): Promise<string>;
    head(uploadId: string): Promise<{ size: number } | null>;
    delete(uploadId: string): Promise<void>;
  };
  jobs: { enqueue(name: string, payload: unknown): Promise<void> };
};

````

> Result: The file <run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\packages\backend\src\ctx.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\packages\backend\src\errors.ts`

````text
export class QuotaExceeded extends Error {
  constructor(readonly requested: number, readonly available: number) {
    super("quota_exceeded");
  }
}
export class InvalidUploadSize extends Error {}
export class UploadNotFound extends Error {}
export class UploadNotReceived extends Error {}
export class UploadExpired extends Error {}
export class UploadSizeMismatch extends Error {}

````

> Result: The file <run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\packages\backend\src\errors.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work/packages/backend/src\" && cat > ctx.ts <<'EOF'\nexport type Ctx = {\n  accountId: string;\n  // Assumed contract: `db.transaction(fn)` runs `fn` atomically and serializably (retrying on conflict), so a\n  // read-check-write inside it cannot interleave with another touching the same rows. See docs/quota- [... 516 more characters]`

> Result: (Bash completed with no output)

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\packages\backend\src\uploads.ts`

````text
import type { Ctx } from "./ctx";
import {
  InvalidUploadSize,
  QuotaExceeded,
  UploadExpired,
  UploadNotFound,
  UploadNotReceived,
  UploadRequestConflict,
  UploadSizeMismatch,
} from "./errors";

// Accounting rules live in docs/quota-accounting.md. In short: startUpload reserves the declared size, finalizeUpload
// converts the reservation into usage once the stored object is verified, and every counter change happens in the same
// transaction as the upload status change that justifies it.

// Hidden internal ceilings, not shown to users (see docs/quota-accounting.md, "Internal ceilings").
export const MAX_FILE_BYTES = 5 * 1024 ** 3;
export const SUMMARIES_PER_DAY = 500;

const SIGNED_URL_TTL_SECONDS = 60 * 60;
const RESERVATION_TTL_MS = 6 * 60 * 60 * 1000;
const DAY_MS = 24 * 60 * 60 * 1000;

type Upload = {
  id: string;
  accountId: string;
  name: string;
  size: number;
  requestId?: string;
  status: "pending" | "ready" | "failed";
  failureKind?: "abandoned" | "size_mismatch";
  reservationExpiresAt: number;
  summaryStatus?: "queued" | "running" | "ready" | "held" | "failed";
};

export async function startUpload(ctx: Ctx, input: { name: string; size: number; requestId?: string }) {
  if (!Number.isSafeInteger(input.size) || input.size <= 0 || input.size > MAX_FILE_BYTES) throw new InvalidUploadSize();
  const now = Date.now();

  const upload: Upload = await ctx.db.transaction(async (tx: any) => {
    // A retried startUpload (CLI timeout) carries the same requestId and gets the same reservation back.
    if (input.requestId) {
      const existing: Upload | null = await tx.uploads.findByRequestId(ctx.accountId, input.requestId);
      if (existing) {
        if (existing.name !== input.name || existing.size !== input.size) throw new UploadRequestConflict();
        if (existing.status === "failed") throw new UploadExpired();
        return existing;
      }
    }
    const account = await tx.accounts.get(ctx.accountId);
    const available = account.cap - account.used - account.reserved;
    if (input.size > available) throw new QuotaExceeded(input.size, Math.max(0, available));
    await tx.accounts.patch(account.id, { reserved: account.reserved + input.size });
    return tx.uploads.insert({
      accountId: ctx.accountId,
      name: input.name,
      size: input.size,
      requestId: input.requestId,
      status: "pending",
      reservationExpiresAt: now + RESERVATION_TTL_MS,
    });
  });

  if (upload.status !== "pending") return { uploadId: upload.id, status: upload.status, url: null };
  const url = await ctx.storage.signPut(upload.id, { contentLength: upload.size, expiresInSeconds: SIGNED_URL_TTL_SECONDS });
  return { uploadId: upload.id, status: upload.status, url };
}

export async function finalizeUpload(ctx: Ctx, input: { uploadId: string }) {
  const upload = await getOwnUpload(ctx, input.uploadId);
  if (upload.status === "ready") return settled(ctx, upload);
  if (upload.status === "failed") throw failureError(upload);

  // The stored object, not the client's claim, decides what is charged.
  const stored = await ctx.storage.head(upload.id);
  if (!stored) throw new UploadNotReceived();
  if (stored.size !== upload.size) {
    const failed = await failPending(ctx, upload.id, "size_mismatch");
    if (failed) await ctx.storage.delete(upload.id);
    throw new UploadSizeMismatch();
  }

  const result: Upload = await ctx.db.transaction(async (tx: any) => {
    // Re-read inside the transaction: a concurrent finalize or the expiry sweep may already have settled this upload.
    const current: Upload = await tx.uploads.get(upload.id);
    if (current.status !== "pending") return current;
    const account = await tx.accounts.get(current.accountId);
    const now = Date.now();
    const windowFresh = account.summaryWindowStart !== undefined && now - account.summaryWindowStart < DAY_MS;
    const summaryCount = windowFresh ? account.summaryCount : 0;
    const admitSummary = summaryCount < SUMMARIES_PER_DAY;
    await tx.accounts.patch(account.id, {
      reserved: account.reserved - current.size,
      used: account.used + current.size,
      summaryWindowStart: windowFresh ? account.summaryWindowStart : now,
      summaryCount: admitSummary ? summaryCount + 1 : summaryCount,
    });
    const summaryStatus = admitSummary ? "queued" : "held";
    await tx.uploads.patch(current.id, { status: "ready", summaryStatus });
    return { ...current, status: "ready", summaryStatus };
  });

  if (result.status === "failed") throw failureError(result);
  return settled(ctx, result);
}

// Explicit user action to summarize a document whose summary was held by the daily ceiling or failed.
// This is the only retry path for the paid summary; nothing retries it automatically.
export async function requestSummary(ctx: Ctx, input: { uploadId: string }) {
  const upload = await getOwnUpload(ctx, input.uploadId);
  if (upload.status !== "ready") throw new UploadNotFound();

  const result: Upload = await ctx.db.transaction(async (tx: any) => {
    const current: Upload = await tx.uploads.get(upload.id);
    if (current.summaryStatus !== "held" && current.summaryStatus !== "failed") return current;
    const account = await tx.accounts.get(current.accountId);
    const now = Date.now();
    const windowFresh = account.summaryWindowStart !== undefined && now - account.summaryWindowStart < DAY_MS;
    const summaryCount = windowFresh ? account.summaryCount : 0;
    if (summaryCount >= SUMMARIES_PER_DAY) return current;
    await tx.accounts.patch(account.id, {
      summaryWindowStart: windowFresh ? account.summaryWindowStart : now,
      summaryCount: summaryCount + 1,
    });
    await tx.uploads.patch(current.id, { summaryStatus: "queued" });
    return { ...current, summaryStatus: "queued" };
  });

  return settled(ctx, result);
}

// Scheduled sweep: releases reservations for uploads that were started but never finalized.
// Processes one bounded batch per run; safe to run repeatedly or concurrently with finalizeUpload.
export async function releaseExpiredReservations(ctx: Ctx, opts: { limit: number } = { limit: 100 }) {
  const now = Date.now();
  const expired: Upload[] = await ctx.db.uploads.findPendingExpiredBefore(now, opts.limit);
  let released = 0;
  for (const upload of expired) {
    if (await failPending(ctx, upload.id, "abandoned")) {
      // Bytes may have landed after the client gave up; they must not outlive the released reservation.
      await ctx.storage.delete(upload.id);
      released++;
    }
  }
  return { released, more: expired.length === opts.limit };
}

async function getOwnUpload(ctx: Ctx, uploadId: string): Promise<Upload> {
  const upload: Upload | null = await ctx.db.uploads.get(uploadId);
  if (!upload || upload.accountId !== ctx.accountId) throw new UploadNotFound();
  return upload;
}

// Moves a pending upload to failed and returns its reservation. Returns false if it was no longer pending.
async function failPending(ctx: Ctx, uploadId: string, failureKind: NonNullable<Upload["failureKind"]>) {
  return ctx.db.transaction(async (tx: any) => {
    const current: Upload = await tx.uploads.get(uploadId);
    if (current.status !== "pending") return false;
    const account = await tx.accounts.get(current.accountId);
    await tx.accounts.patch(account.id, { reserved: account.reserved - current.size });
    await tx.uploads.patch(current.id, { status: "failed", failureKind });
    return true;
  });
}

// The summarize job claims queued -> running atomically and exits otherwise, so enqueueing again for a still-queued
// summary (a retried finalize after enqueue failed or timed out) never starts a second paid run.
async function settled(ctx: Ctx, upload: Upload) {
  if (upload.summaryStatus === "queued") await ctx.jobs.enqueue("summarize", { uploadId: upload.id });
  return { uploadId: upload.id, status: upload.status, summaryStatus: upload.summaryStatus };
}

function failureError(upload: Upload) {
  return upload.failureKind === "size_mismatch" ? new UploadSizeMismatch() : new UploadExpired();
}

````

> Result: The file <run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\packages\backend\src\uploads.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "which tsc node 2>&1; ls \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work/node_modules\" 2>&1 | head -3"}`

> Result: <home>/AppData/Local/pnpm/tsc /c/Program Files/nodejs/node ls: cannot access '<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work/node_modules': No such file or directory

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work/packages/backend/src\" && tsc --noEmit --strict --target es2022 --module nodenext --moduleResolution nodenext --skipLibCheck uploads.ts 2>&1 | head -20"}`

> Result: uploads.ts(1,26): error TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'. Did you mean './ctx.js'? uploads.ts(10,8): error TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'. Did you mean './errors.js'?

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-old-opus2/work/packages/backend/src\" && tsc --noEmit --strict --target es2022 --module esnext --moduleResolution bundler --skipLibCheck uploads.ts && echo OK"}`

> Result: OK

**Assistant:** The code typechecks under strict mode. Next I'm writing the design doc.

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\docs\quota-accounting.md`

````text
# Quota accounting

How uploads and summaries count against an account's storage cap. `docs/brief.md` is the owner's record. This doc is the design that implements it, in `packages/backend/src/uploads.ts`. Anything marked **Assumption** was decided without the owner and is listed again at the end.

## What was wrong

The flow in the brief checked the cap at `startUpload` and only added to usage at `finalizeUpload`. Once the free plan is open to everyone, these break it:

1. **Concurrent starts all pass the check.** The CLI starts 8 uploads at once. Each one reads `used` before any of them finalizes, so an account with 1 GB left can start eight 1 GB uploads and finish 8 GB over the cap.
2. **The declared size was trusted.** The cap was checked against `size` from the client, and the signed URL accepted any number of bytes. Usage was then charged with the declared size, not the stored one, so a caller could declare 1 byte and store 5 GB.
3. **Finalize was not idempotent.** The CLI retries a request that times out. A retried `finalizeUpload` added the size a second time and queued a second paid summary.
4. **Lost updates.** `used` was read, then written back as `used + size` outside any transaction, so two concurrent finalizes could overwrite each other. The count drifts in both directions.
5. **No ownership check on finalize.** Any account could finalize any `uploadId`, which charged the owner's account and started a summary on its document.
6. **Abandoned uploads.** Nothing cleaned up an upload that was started but never finalized. Once reservations exist, an abandoned upload would hold space forever.
7. **Summary cost had no bound.** Every document gets a paid summary. A 10 GB free cap filled with tiny files means millions of paid model calls per account.

## Model

Each account holds three byte counters:

| Field | Meaning |
| --- | --- |
| `cap` | The plan limit (10 GB on free). |
| `used` | Sum of `size` over the account's `ready` uploads. |
| `reserved` | Sum of `size` over the account's `pending` uploads. |

Admission rule: a new upload of `size` is admitted only if `used + reserved + size <= cap`.

Gate before, charge after. A reservation is a hold, not a charge: it only becomes `used` after the bytes are verified in storage. Every change to a counter happens **in the same transaction** as the upload status change that justifies it, so the invariants above hold by construction:

| Transition | Counter change |
| --- | --- |
| *(none)* → `pending` (start) | `reserved += size` |
| `pending` → `ready` (finalize, verified) | `reserved -= size`, `used += size` |
| `pending` → `failed` (abandoned / size mismatch) | `reserved -= size` |
| `ready` → deleted *(not built yet)* | `used -= size` |

`reserved` and `used` are stored counters rather than derived on read because admission must read them atomically on every start. They are a cache of the sums above. A reconciliation job can recompute them from the upload rows, and that recompute is the authority if they disagree.

## Upload flow

### `startUpload { name, size, requestId? }`

1. Reject `size` that is not a positive integer or exceeds `MAX_FILE_BYTES` (5 GB).
2. In one transaction: if `requestId` matches an earlier upload by this account, return that upload (same reservation) instead of creating another. Otherwise apply the admission rule, add `size` to `reserved`, and insert a `pending` upload with `reservationExpiresAt = now + 6h`.
3. Sign a PUT URL that is **bound to `Content-Length = size`** and valid for 1 hour. Storage refuses any other byte count.

`requestId` is how a CLI retry after a timeout avoids reserving twice. Clients generate one per file and reuse it on retry. Reusing a `requestId` with a different name or size is rejected. Without a `requestId`, a retried start makes a second reservation, and the sweep releases the extra one.

### `finalizeUpload { uploadId }`

1. Load the upload and require that `accountId` matches the caller. Otherwise answer "not found".
2. If it is already `ready`, return the same result. This is the idempotent retry path: nothing is charged twice.
3. `HEAD` the object. If it is missing, answer "not received". The reservation stays, so the client can PUT again and finalize again.
4. If the stored size differs from the reserved size, fail the upload (`size_mismatch`), release the reservation, and delete the object.
5. In one transaction, re-read the upload. If a concurrent finalize or the sweep already settled it, return that outcome. Otherwise move `reserved` to `used`, mark it `ready`, and admit the summary (see below).
6. After commit, enqueue `summarize` if the summary is `queued`.

### Expiry sweep: `releaseExpiredReservations`

This scheduled job (suggested every 15 min) works in bounded batches. It moves each `pending` upload past `reservationExpiresAt` to `failed + abandoned` in a transaction, releases its reservation, and only then deletes any bytes that landed. It re-checks status inside the transaction, so a finalize that commits first wins and the sweep skips that upload. A finalize that arrives after the sweep gets "upload expired", and the user uploads again.

The reservation lifetime (6 h) is longer than the URL lifetime (1 h) on purpose. A slow multi-GB PUT that started before the URL expired can still finish and be finalized.

## Summaries

**Summaries do not count against the storage cap** (**Assumption**). The summary is something the product generates, it is small next to the document, and it is deleted with the document. Charging it would make the cap a number the user can't predict from their own files. The cap stays "bytes of files you uploaded".

Summaries are paid model work, so they get their own controls:

- **Admission happens in the finalize transaction.** Only the single `pending → ready` transition can admit a summary, so retries and concurrent finalizes cannot queue a second run.
- **There is a hidden daily ceiling of `SUMMARIES_PER_DAY` (500) per account.** It is a rolling 24 h window that starts at the first summary. A document finalized past the ceiling is still stored and counted, but its summary is `held` rather than queued. This is anti-abuse plumbing, not a plan limit, and it is never shown as a number in routine UI.
- **Summaries never auto-retry.** `requestSummary { uploadId }` is the one user-initiated path. It re-admits a `held` or `failed` summary against the same ceiling.
- **Contract for the `summarize` job (not in this repo yet):** the job must claim `queued → running` atomically and exit if the claim fails. `finalizeUpload` and `requestSummary` re-enqueue whenever the summary is still `queued`, to recover from an enqueue that failed after commit. Duplicates are expected, and the claim is what makes them harmless. A summary failure is stored as `failed` with its internal kind and never touches the storage counters.

## Internal ceilings

These are hidden ceilings that apply to every plan. They live in code as product constants, not env:

| Constant | Value | Why |
| --- | --- | --- |
| `MAX_FILE_BYTES` | 5 GB | Largest single signed PUT. Larger files need multipart, which is out of scope here. |
| `SUMMARIES_PER_DAY` | 500 | Bounds model spend per free account. |

Request-rate limiting (per IP / per token) belongs at the gateway, not here, and is still needed before launch.

## User-facing states

| Error | Product meaning | Remedy offered |
| --- | --- | --- |
| `QuotaExceeded(requested, available)` | Not enough space for this file. In-flight uploads count. | Free up space, or upgrade only if a bigger plan exists. |
| `InvalidUploadSize` | File is empty or too large. | Pick another file. |
| `UploadNotReceived` | Bytes have not arrived yet. | Retry the upload. |
| `UploadSizeMismatch` / `UploadExpired` | Upload did not complete. | Upload again. |
| `UploadRequestConflict` | Client bug: `requestId` was reused for a different file. | Internal only. |
| summary `held` | Summary is waiting. | "Summarize" button → `requestSummary`. |

Copy for each is product-owned. Raw errors stay internal.

## Assumptions to confirm

1. **Summaries don't count toward the 10 GB cap.** If you want them counted, add their byte size to `used` when the summary is written and subtract it when the document is deleted.
2. **`db.transaction(fn)` is atomic and serializable** with retry on conflict (as Convex mutations are). The old `ctx.db` had no transaction API. The new code assumes `ctx.db.transaction`, plus `uploads.findByRequestId(accountId, requestId)` and `uploads.findPendingExpiredBefore(time, limit)`, which need indexes.
3. **Storage supports Content-Length-bound signed PUTs, `head`, and `delete`.** `Ctx.storage` was extended to match. The adapter isn't in this repo.
4. **The numbers are my picks:** 5 GB per file, 500 summaries/day, 1 h URL, 6 h reservation, sweep every 15 min.
5. **Empty (0-byte) files are rejected**, since there is nothing to summarize.
6. **An account over its cap** (after a downgrade or a cap change) keeps everything it has. Only new starts are refused.

## Not done yet / follow-ups

- **Migration:** add `reserved = 0`, `summaryWindowStart`, and `summaryCount` to existing accounts. Recompute `used` from `ready` uploads, because the old double-counting bug may have inflated it.
- **Wire the sweep** as a scheduled job, and write the `summarize` job's atomic claim.
- **Deletion** must decrement `used` in the same transaction as the row removal.
- **CLI and MCP clients** should send a `requestId` per file.
- **Tests:** there is no test harness in the repo. The behaviors that most need tests are concurrent starts at the cap edge, double finalize, finalize racing the sweep, a size mismatch, and the summary ceiling.
- **Gateway rate limits** are needed before launch.

````

> Result: File created successfully at: <run>\builds\4-quota-reservation-under-concurrency-old-opus2\work\docs\quota-accounting.md (file state is current in your context — no need to Read it back)

**Assistant:** I wrote the design to `docs/quota-accounting.md` and rewrote `packages/backend/src/uploads.ts` to match. I had to extend `ctx.ts` and `errors.ts` too. The code passes a strict TypeScript check. There are no tests in the repo, so none of this has been run, and the storage adapter and summary job it relies on aren't in the repo either. Nothing is committed.

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

**Session ended:** success, 15 turns, 186124 ms
