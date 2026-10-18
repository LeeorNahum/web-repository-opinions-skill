**Prompt:** Design how uploads and summaries are counted against the storage cap (see docs/brief.md), write it to docs/quota-accounting.md, and update packages/backend/src/uploads.ts to match. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-quota-reservation-under-concurrency-new-opus/work\" && git ls-files && cat docs/brief.md && cat packages/backend/src/uploads.ts"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6076 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-quota-reservation-under-concurrency-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/quota.md $R/uploads.md $R/abuse-resistance.md $R/billing.md; cat packages/backend/src/ctx.ts packages/backend/src/errors.ts packages/backend/package.json package.json"}`

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-quota-reservation-under-concurrency-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/background-jobs.md $R/failure-and-retries.md $R/object-storage.md $R/ai-model-routing.md $R/data-deletion.md $R/source-of-truth.md $R/definition-of-done.md"}`

> Result: # Quota  Check quota before doing expensive work, reserve it when concurrent requests could oversubscribe it, charge usage only after durable success, and release whatever the work did not use.  - Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known. - For imported files, read metadata first and block early if it cannot fit. - For li [... 10505 more characters]

> Result: # Background Jobs  Provider-backed and long-running work runs as explicit jobs with explicit state, never as fire-and-forget calls scattered through route handlers.  Design every job around its failure point, not its happy path. Ask:  - What if the external call succeeds and the database update fails? - What if the row exists but the provider object does not? - What if the user closes the  [... 20849 more characters]

**Tool call `Write`:** `<run>/builds/2-quota-reservation-under-concurrency-new-opus/work/packages/backend/src/ctx.ts`

````text
export type UploadStatus = "pending" | "ready" | "cancelled" | "rejected" | "expired";

export type AccountRow = { id: string; cap: number; used: number };

export type UploadRow = {
  id: string;
  accountId: string;
  name: string;
  size: number;
  status: UploadStatus;
  clientRequestId?: string;
  createdAt: number;
  expiresAt: number;
  finalizedAt?: number;
  objectDeletedAt?: number;
};

// Everything inside one transaction commits or rolls back together, and concurrent
// transactions touching the same rows are serialized (retried on conflict).
export type Tx = {
  accounts: {
    get(id: string): Promise<AccountRow>;
    patch(id: string, fields: Partial<AccountRow>): Promise<void>;
  };
  uploads: {
    get(id: string): Promise<UploadRow | null>;
    insert(row: Omit<UploadRow, "id">): Promise<UploadRow>;
    patch(id: string, fields: Partial<UploadRow>): Promise<void>;
    listPending(accountId: string): Promise<UploadRow[]>;
    findByClientRequestId(accountId: string, clientRequestId: string): Promise<UploadRow | null>;
    // Rows that never became ready, whose object has not been deleted, with expiresAt < before.
    listUnfinalizedBefore(before: number, limit: number): Promise<UploadRow[]>;
  };
  // Enqueued only if the transaction commits.
  jobs: { enqueue(name: string, payload: unknown): Promise<void> };
};

export type Ctx = {
  accountId: string;
  db: { transaction<T>(fn: (tx: Tx) => Promise<T>): Promise<T> };
  storage: {
    // The signed PUT is bound to the exact Content-Length and expires at expiresAt.
    signPut(key: string, opts: { size: number; expiresAt: number }): Promise<string>;
    head(key: string): Promise<{ size: number } | null>;
    delete(key: string): Promise<void>;
  };
};

````

> Result: The file <run>/builds/2-quota-reservation-under-concurrency-new-opus/work/packages/backend/src/ctx.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>/builds/2-quota-reservation-under-concurrency-new-opus/work/packages/backend/src/errors.ts`

````text
export class QuotaExceeded extends Error {
  constructor(readonly detail: { cap: number; used: number; reserved: number; requested: number }) {
    super("quota_exceeded");
  }
}

export class InvalidUpload extends Error {
  constructor(readonly reason: "name" | "size" | "size_mismatch") {
    super("invalid_upload");
  }
}

export class UploadNotFound extends Error {}

// finalizeUpload was called before the bytes landed in storage. Retry after the PUT completes.
export class UploadNotReceived extends Error {}

// The upload was cancelled, rejected, or expired and swept. Start a new upload.
export class UploadClosed extends Error {}

// A clientRequestId was reused for a different file or after its upload closed.
export class UploadConflict extends Error {}

````

> Result: The file <run>/builds/2-quota-reservation-under-concurrency-new-opus/work/packages/backend/src/errors.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Write`:** `<run>/builds/2-quota-reservation-under-concurrency-new-opus/work/packages/backend/src/uploads.ts`

````text
import type { Ctx, Tx, UploadRow } from "./ctx";
import { InvalidUpload, QuotaExceeded, UploadClosed, UploadConflict, UploadNotFound, UploadNotReceived } from "./errors";

// Accounting rules live in docs/quota-accounting.md.

// How long a started upload holds its bytes against the cap, and how long its signed URL lives.
export const RESERVATION_TTL_MS = 6 * 60 * 60 * 1000;
// How long after expiry the sweep waits before deleting unfinalized bytes, so a PUT that
// started just before the URL expired has finished landing.
export const SWEEP_GRACE_MS = 24 * 60 * 60 * 1000;
// Largest object a single signed PUT can carry on S3-compatible stores.
export const MAX_SINGLE_PUT_BYTES = 5 * 1024 ** 3;
export const MAX_NAME_LENGTH = 1024;

async function openReservedBytes(tx: Tx, accountId: string, now: number, excludeId?: string) {
  const pending = await tx.uploads.listPending(accountId);
  return pending
    .filter((u) => u.expiresAt > now && u.id !== excludeId)
    .reduce((sum, u) => sum + u.size, 0);
}

export async function startUpload(
  ctx: Ctx,
  input: { name: string; size: number; clientRequestId?: string },
) {
  if (typeof input.name !== "string" || input.name.length === 0 || input.name.length > MAX_NAME_LENGTH) {
    throw new InvalidUpload("name");
  }
  if (!Number.isSafeInteger(input.size) || input.size <= 0 || input.size > MAX_SINGLE_PUT_BYTES) {
    throw new InvalidUpload("size");
  }
  const now = Date.now();

  const upload = await ctx.db.transaction(async (tx): Promise<UploadRow> => {
    // A retried startUpload with the same clientRequestId gets the same reservation back.
    if (input.clientRequestId !== undefined) {
      const existing = await tx.uploads.findByClientRequestId(ctx.accountId, input.clientRequestId);
      if (existing) {
        const sameFile = existing.name === input.name && existing.size === input.size;
        if (sameFile && existing.status === "pending" && existing.expiresAt > now) return existing;
        throw new UploadConflict();
      }
    }

    const account = await tx.accounts.get(ctx.accountId);
    const reserved = await openReservedBytes(tx, ctx.accountId, now);
    if (account.used + reserved + input.size > account.cap) {
      throw new QuotaExceeded({ cap: account.cap, used: account.used, reserved, requested: input.size });
    }
    return tx.uploads.insert({
      accountId: ctx.accountId,
      name: input.name,
      size: input.size,
      status: "pending",
      clientRequestId: input.clientRequestId,
      createdAt: now,
      expiresAt: now + RESERVATION_TTL_MS,
    });
  });

  const url = await ctx.storage.signPut(upload.id, { size: upload.size, expiresAt: upload.expiresAt });
  return { uploadId: upload.id, url, expiresAt: upload.expiresAt };
}

type FinalizeOutcome =
  | { kind: "ready"; size: number }
  | { kind: "size_mismatch" }
  | { kind: "over_quota"; detail: QuotaExceeded["detail"] };

export async function finalizeUpload(ctx: Ctx, input: { uploadId: string }) {
  const upload = await ctx.db.transaction((tx) => tx.uploads.get(input.uploadId));
  if (!upload || upload.accountId !== ctx.accountId) throw new UploadNotFound();
  if (upload.status === "ready") return { uploadId: upload.id, size: upload.size };
  if (upload.status !== "pending") throw new UploadClosed();

  // Charge what storage actually holds, never what the client declared.
  const stored = await ctx.storage.head(upload.id);
  if (!stored) throw new UploadNotReceived();

  const outcome = await ctx.db.transaction(async (tx): Promise<FinalizeOutcome> => {
    const current = await tx.uploads.get(upload.id);
    if (!current) throw new UploadNotFound();
    // A concurrent or retried finalize already charged it and queued the summary.
    if (current.status === "ready") return { kind: "ready", size: current.size };
    if (current.status !== "pending") throw new UploadClosed();

    if (stored.size !== current.size) {
      await tx.uploads.patch(current.id, { status: "rejected" });
      return { kind: "size_mismatch" };
    }

    const now = Date.now();
    const account = await tx.accounts.get(current.accountId);
    // An unexpired reservation already holds this room. An expired one must win it again.
    if (current.expiresAt <= now) {
      const reserved = await openReservedBytes(tx, current.accountId, now, current.id);
      if (account.used + reserved + stored.size > account.cap) {
        return {
          kind: "over_quota",
          detail: { cap: account.cap, used: account.used, reserved, requested: stored.size },
        };
      }
    }

    await tx.accounts.patch(account.id, { used: account.used + stored.size });
    await tx.uploads.patch(current.id, { status: "ready", size: stored.size, finalizedAt: now });
    // Queued in the same transaction as the pending -> ready transition, so exactly once per upload.
    await tx.jobs.enqueue("summarize", { uploadId: current.id });
    return { kind: "ready", size: stored.size };
  });

  if (outcome.kind === "size_mismatch") throw new InvalidUpload("size_mismatch");
  if (outcome.kind === "over_quota") throw new QuotaExceeded(outcome.detail);
  return { uploadId: upload.id, size: outcome.size };
}

// Releases the reservation immediately. Any bytes already PUT are deleted by the sweep.
export async function cancelUpload(ctx: Ctx, input: { uploadId: string }) {
  await ctx.db.transaction(async (tx) => {
    const upload = await tx.uploads.get(input.uploadId);
    if (!upload || upload.accountId !== ctx.accountId) throw new UploadNotFound();
    if (upload.status === "ready") throw new UploadClosed();
    if (upload.status === "pending") await tx.uploads.patch(upload.id, { status: "cancelled" });
  });
}

// Scheduled. Deletes bytes of uploads that never became ready, so storage no account is
// charged for does not accumulate. Safe to run repeatedly and concurrently with finalize.
export async function sweepUnfinalizedUploads(ctx: Pick<Ctx, "db" | "storage">, limit = 100) {
  const cutoff = Date.now() - SWEEP_GRACE_MS;
  const candidates = await ctx.db.transaction((tx) => tx.uploads.listUnfinalizedBefore(cutoff, limit));
  let deleted = 0;
  for (const candidate of candidates) {
    // Close a still-pending row first so a late finalize cannot charge bytes we are deleting.
    const claimed = await ctx.db.transaction(async (tx) => {
      const row = await tx.uploads.get(candidate.id);
      if (!row || row.status === "ready" || row.objectDeletedAt !== undefined) return false;
      if (row.status === "pending") await tx.uploads.patch(row.id, { status: "expired" });
      return true;
    });
    if (!claimed) continue;
    await ctx.storage.delete(candidate.id);
    await ctx.db.transaction((tx) => tx.uploads.patch(candidate.id, { objectDeletedAt: Date.now() }));
    deleted++;
  }
  return { deleted, more: candidates.length === limit };
}

````

> Result: The file <run>/builds/2-quota-reservation-under-concurrency-new-opus/work/packages/backend/src/uploads.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-quota-reservation-under-concurrency-new-opus/work\" && ls node_modules 2>&1 | head -3; (command -v tsc || ls \"$APPDATA/npm\" 2>/dev/null | grep -i tsc) 2>&1 | head"}`

> Result: ls: cannot access 'node_modules': No such file or directory <home>/AppData/Local/pnpm/tsc

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-quota-reservation-under-concurrency-new-opus/work\" && tsc --version && tsc --noEmit --strict --target es2022 --module nodenext --moduleResolution nodenext packages/backend/src/*.ts; echo exit=$?"}`

> Result: Version 5.9.3 packages/backend/src/uploads.ts(1,41): error TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'. Did you mean './ctx.js'? packages/backend/src/uploads.ts(2,111): error TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext' [... 1040 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/2-quota-reservation-under-concurrency-new-opus/work\" && tsc --noEmit --strict --target es2022 --module esnext --moduleResolution bundler packages/backend/src/*.ts; echo exit=$?"}`

> Result: exit=0

**Assistant:** The backend code passes a strict typecheck. Next I'm writing the design doc.

**Tool call `Write`:** `<run>/builds/2-quota-reservation-under-concurrency-new-opus/work/docs/quota-accounting.md`

````text
# Quota accounting

How uploads and summaries count against an account's storage cap. `docs/brief.md` stays the source of truth for product decisions. This document is the design that follows from it. Where it assumes something the brief doesn't say, the "Assumptions" section says so. Implementation: `packages/backend/src/uploads.ts`.

## What was wrong

The old flow checked `used + size <= cap` in `startUpload` and added `size` in `finalizeUpload`. With the CLI uploading 8 files at once, retrying timed-out requests, and MCP agents calling the same API, that broke in six ways:

1. **Parallel starts oversubscribe the cap.** Each of 8 concurrent `startUpload` calls saw the same `used`, each passed, and together they went over the cap. The check ignored uploads already started but not yet finalized.
2. **Retried finalize double-charges.** `finalizeUpload` had no state check, so a retry after a timeout added the size again and queued a second paid summary.
3. **Concurrent finalizes lose updates.** `used` was read, then written back as `used + size` outside a transaction, so two finalizes landing together dropped one of the increments.
4. **The declared size was trusted.** The cap was checked and charged against the `size` the client claimed, and the signed URL didn't bind the size. A client could declare 1 byte and PUT gigabytes.
5. **Unfinalized bytes were free storage.** Bytes that were PUT but never finalized stayed in the bucket forever and weren't counted.
6. **No ownership check on finalize.** Any caller could finalize any `uploadId`, which charged another account and queued its summary.

## Model

The account has two ledgers:

- **Used** is `account.used`, the committed bytes. It is the sum of the measured sizes of the account's `ready` uploads, plus deleted content that hasn't been permanently removed yet (see Deletion). It is a counter kept in step transactionally, as an explicit cache of that sum.
- **Reserved** is the sum of `size` over the account's `pending` uploads whose `expiresAt` is still in the future. It is derived on every check, never stored, so an expired reservation stops counting at expiry without waiting for a job.

**Admission rule:** a new upload of `size` bytes is admitted only if `used + reserved + size <= cap`, evaluated inside a serializable transaction that also inserts the reservation. Concurrent starts therefore serialize, and the eighth file in a batch sees the first seven's reservations.

## Upload lifecycle

```text
startUpload ──► pending ──finalize──► ready      (charged, summary queued)
                   │
                   ├──cancelUpload──► cancelled  (reservation released now)
                   ├──size mismatch─► rejected   (never charged)
                   └──sweep after expiry + grace──► expired
cancelled / rejected / expired ──sweep──► object deleted (objectDeletedAt set)
```

### `startUpload { name, size, clientRequestId? }`

- Validates the name (1 to 1024 characters) and the size (a positive integer, at most 5 GiB, the single-PUT limit).
- In one transaction, applies the admission rule and inserts a `pending` row with `expiresAt = now + 6h`. The row exists before any byte moves, so it is the write-ahead record the sweep uses to find and delete orphaned bytes.
- Signs a PUT bound to the exact `Content-Length` and expiring at `expiresAt`.
- **Idempotent retry:** if `clientRequestId` matches an open reservation for the same name and size, the same upload is returned with a fresh URL. No second reservation is made. A reused id for a different file, or for a closed upload, gets `UploadConflict`.
- Over the cap, it throws `QuotaExceeded { cap, used, reserved, requested }` so the surface can explain the limit and how much room is held by uploads still in progress.

### `finalizeUpload { uploadId }`

- Rejects an upload that belongs to another account (`UploadNotFound`, so it doesn't reveal that the upload exists).
- If the upload is already `ready`, it returns success and changes nothing. Retries are safe.
- Reads the stored object's real size from storage. If nothing has landed yet, it throws `UploadNotReceived`, and the client can retry after the PUT finishes.
- In one transaction: rechecks the status, rejects a size mismatch, adds the **measured** size to `used`, marks the upload `ready`, and enqueues `summarize`. The job is enqueued in the same transaction as the `pending → ready` transition, so each upload gets exactly one summary job however many times finalize runs.
- **Late finalize:** if the reservation has expired but the sweep hasn't claimed the upload yet, finalize is still allowed, but it has to pass the admission rule again, since its reserved room has been released. An **unexpired** reservation is always honored, even if the cap shrank in the meantime, because the bytes were admitted.

### `cancelUpload { uploadId }`

Releases the reservation immediately. The CLI should call it for every in-flight file when interrupted, so an aborted batch doesn't hold the cap for 6 hours. The bytes are deleted later by the sweep, because a PUT may still be landing.

### `sweepUnfinalizedUploads` (scheduled)

This finds uploads that never became `ready` and whose `expiresAt` is more than 24 hours past. The 24 hours lets a PUT that started just before the URL expired finish landing. For each one, the sweep first marks a still-`pending` row `expired` in a transaction, so a racing finalize can't charge bytes that are about to be deleted. It then deletes the object and records `objectDeletedAt`. The sweep runs in bounded batches, is idempotent, and is safe to run concurrently with finalize. Worst-case life of uncharged bytes: 6h TTL + 24h grace + one sweep interval.

**Needs wiring:** schedule this on a cron, for example hourly, re-running while `more` is true.

## Summaries

- **A summary's text does not count against the storage cap.** The product generates it, it is small and bounded, and the user can't choose its size. Counting it would mean an account filled to exactly its cap couldn't receive summaries for files it was allowed to upload. The cap measures the user's files.
- **Summary work is gated by the upload, not by bytes.** One summary job per upload, queued only after a durable, charged finalize, never at start. A failed or cancelled upload never costs a model call.
- **A summary is never auto-retried.** It is paid provider work, so a failed summary is retried only on explicit user action, through the same path, without starting a duplicate run. The `summarize` job has to exit without doing anything if the upload is no longer `ready` or already has a summary, so a manual retry racing an in-flight run doesn't bill twice.
- **Provider cost is a separate ledger from the storage cap.** The product pays per summary whether or not the user's storage allowance is touched. Uploading and deleting in a loop never exceeds the cap but does generate a summary each time. See the first open question.

## Deletion and plan changes (rules for code not yet written)

There is no delete path in the repo yet. When one is added:

- Moving a file to trash keeps its bytes counted. Permanent removal subtracts the upload's measured size from `used`, in the same transaction that marks it removed.
- When an account is over its cap, for example after a downgrade, existing files stay readable and deletable. Only `startUpload` (growth) is refused, which the admission rule already does.
- `used` is a cached counter. A periodic reconcile job should recompute it from `ready` and trashed uploads and alert on drift. It shouldn't silently rewrite the counter.

## Assumptions (made without the owner, please confirm)

1. **Transactions.** `ctx.db.transaction` runs serializably and retries on conflict, and `tx.jobs.enqueue` only takes effect if the transaction commits. This matches Convex mutation semantics. With another database, `listPending` + insert needs `SERIALIZABLE` isolation or a row lock on the account. `Ctx` in `ctx.ts` was typed to declare this, along with the new `storage.head` and `storage.delete` and the size-bound `signPut`. The real adapters need to implement them.
2. **Reservation TTL 6h, sweep grace 24h.** These are picked to cover a slow 5 GiB single PUT. If uploads move to multipart, the TTL should extend while parts keep arriving.
3. **5 GiB per-file maximum.** This comes from the single-PUT limit, not a product decision. Larger files need multipart upload, which is out of scope here.
4. **Summary text doesn't count against the cap** (reasoning above).
5. **`clientRequestId` is optional**, so existing clients keep working, but the CLI and MCP tool should send one per file. Without it, a retried `startUpload` holds a second reservation until it expires or is cancelled.
6. **Error shapes.** New error classes are in `errors.ts`. Mapping them to product-owned copy is the job of the API/MCP boundary, which isn't in this repo.

## Open questions for the owner

1. **Hidden per-account summary ceiling.** Opening the free plan to everyone makes upload-and-delete loops a way to spend the product's model budget without touching the cap. I recommend a hidden daily (or monthly) cap on summaries per account, sized to what the product can absorb, plus edge rate limiting on `startUpload`. The number is a cost decision, so I didn't invent one.
2. **Does content in trash count against the cap?** I assumed yes, until it is permanently removed.
3. **Should a summary's text count?** Answering yes reverses assumption 4 and adds a fixed per-summary charge at summary completion.

## Client changes needed (not in this repo)

- The CLI sends a stable `clientRequestId` per file and reuses it on timeout retries.
- The CLI calls `cancelUpload` for every in-flight file when interrupted.
- The CLI treats `UploadNotReceived` as "PUT not finished, retry finalize", and `QuotaExceeded` as a terminal, explained stop for that file.
- The MCP tool passes through the same fields and errors.

````

> Result: File created successfully at: <run>/builds/2-quota-reservation-under-concurrency-new-opus/work/docs/quota-accounting.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/quota-accounting.md` and rewritten `packages/backend/src/uploads.ts` to match, with supporting changes in `ctx.ts` and `errors.ts`. The code passes a strict TypeScript check. Nothing has been run: there are no tests and no real database or storage behind `Ctx`, and I haven't committed anything.

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

**Session ended:** success, 13 turns, 224950 ms
