**Prompt:** Design how uploads and summaries are counted against the storage cap (see docs/brief.md), write it to docs/quota-accounting.md, and update packages/backend/src/uploads.ts to match. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Tool call `Skill`:** `{"skill": "web-repository-opinions"}`

> Result: Launching skill: web-repository-opinions

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work\" && git ls-files && cat docs/brief.md && cat packages/backend/src/uploads.ts"}`

> Result: .claude/skills/web-repository-opinions/SKILL.md .claude/skills/web-repository-opinions/assets/vercel.json .claude/skills/web-repository-opinions/references/abuse-resistance.md .claude/skills/web-repository-opinions/references/admin.md .claude/skills/web-repository-opinions/references/agent-plugins.md .claude/skills/web-repository-opinions/references/agent-skills.md .claude/skills/web-repository-op [... 6076 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/quota.md $R/uploads.md $R/abuse-resistance.md $R/failure-and-retries.md $R/billing.md; cat packages/backend/src/ctx.ts packages/backend/src/errors.ts packages/backend/package.json package.json"}`

> Result: # Quota  Check quota before doing expensive work, reserve it when concurrent requests could oversubscribe it, charge usage only after durable success, and release whatever the work did not use.  - Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known. - For imported files, read metadata first and block early if it cannot fit. - For li [... 12638 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/background-jobs.md $R/ai-model-routing.md $R/user-facing-errors.md $R/object-storage.md $R/bulk-actions.md $R/source-of-truth.md"}`

> Result: # Background Jobs  Provider-backed and long-running work runs as explicit jobs with explicit state, never as fire-and-forget calls scattered through route handlers.  Design every job around its failure point, not its happy path. Ask:  - What if the external call succeeds and the database update fails? - What if the row exists but the provider object does not? - What if the user closes the  [... 18538 more characters]

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work\" && R=.claude/skills/web-repository-opinions/references; cat $R/definition-of-done.md | head -60; cat $R/data-deletion.md | head -30"}`

> Result: # Definition Of Done  This is a completion summary across the skill. It is not the source of truth for the detailed rules below. Load the owning references for every category the work touches.  A feature is done only when its product contract, implementation, runtime, and verification agree. If one category is false or unknown, the work is locally edited, not done.  ## Product Contract  -  [... 4440 more characters]

**Assistant:** Now writing the code.

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work/packages/backend/src\" && cat > ctx.ts <<'EOF'\nexport type Ctx = {\n  accountId: string;\n  // Must provide `transaction(fn)` that serializes concurrent transactions touching the same\n  // account row (serializable isolation, or the account row locked for update). See docs/quota-accounting.md.\n  db: an [... 1848 more characters]`

> Result: (Bash completed with no output)

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-new-opus\work\packages\backend\src\uploads.ts`

````text
// Storage accounting for uploads. The design and its assumptions live in docs/quota-accounting.md.
import type { Ctx } from "./ctx";
import {
  FileTooLarge,
  IdempotencyKeyReused,
  InvalidUploadSize,
  QuotaExceeded,
  TooManyOpenUploads,
  UploadExpired,
  UploadFailed,
  UploadNotFound,
  UploadNotReceived,
  UploadSizeMismatch,
} from "./errors";

export const MAX_FILE_BYTES = 2 * 1024 ** 3;
export const MAX_OPEN_UPLOADS = 16;
export const UPLOAD_URL_TTL_MS = 60 * 60 * 1000;
// A reservation outlives its signed URL by this much, so a PUT that lands just before the URL
// expires can still be finalized. No URL is ever signed past `expiresAt - FINALIZE_GRACE_MS`.
export const FINALIZE_GRACE_MS = 15 * 60 * 1000;
export const EXPIRE_BATCH_SIZE = 100;

type Upload = {
  id: string;
  accountId: string;
  name: string;
  // Declared size while pending; replaced by the measured stored size when ready.
  size: number;
  status: "pending" | "ready" | "failed";
  failure?: "abandoned" | "size_mismatch";
  summaryStatus?: "queued" | "running" | "ready" | "failed";
  idempotencyKey?: string;
  expiresAt: number;
};

export async function startUpload(
  ctx: Ctx,
  input: { name: string; size: number; idempotencyKey?: string },
) {
  if (!Number.isSafeInteger(input.size) || input.size <= 0) throw new InvalidUploadSize();
  if (input.size > MAX_FILE_BYTES) throw new FileTooLarge(MAX_FILE_BYTES);

  const now = Date.now();
  const upload: Upload = await ctx.db.transaction(async (tx: any) => {
    // Reading the account first makes this transaction conflict with every other reservation
    // or finalize on the same account, so concurrent starts cannot all pass the check.
    const account = await tx.accounts.get(ctx.accountId);

    if (input.idempotencyKey) {
      const existing: Upload | null = await tx.uploads.find({
        accountId: ctx.accountId,
        idempotencyKey: input.idempotencyKey,
      });
      if (existing) {
        if (existing.name !== input.name || (existing.status === "pending" && existing.size !== input.size)) {
          throw new IdempotencyKeyReused();
        }
        return existing;
      }
    }

    const open = (await tx.uploads.list({ accountId: ctx.accountId, status: "pending" })).filter(
      (u: Upload) => u.expiresAt > now,
    );
    if (open.length >= MAX_OPEN_UPLOADS) throw new TooManyOpenUploads();
    const reserved = open.reduce((sum: number, u: Upload) => sum + u.size, 0);
    if (account.used + reserved + input.size > account.cap) {
      throw new QuotaExceeded({ cap: account.cap, used: account.used, reserved, requested: input.size });
    }

    return tx.uploads.insert({
      accountId: ctx.accountId,
      name: input.name,
      size: input.size,
      status: "pending",
      idempotencyKey: input.idempotencyKey,
      expiresAt: now + UPLOAD_URL_TTL_MS + FINALIZE_GRACE_MS,
    });
  });

  // A replayed request for an upload that already finished returns its state and no new URL.
  if (upload.status === "ready") return { uploadId: upload.id, status: upload.status };
  if (upload.status === "failed") throw new UploadFailed(upload.failure ?? "unknown");
  const urlExpiresAt = upload.expiresAt - FINALIZE_GRACE_MS;
  if (urlExpiresAt <= now) throw new UploadExpired();

  const url = await ctx.storage.signPut(upload.id, { contentLength: upload.size, expiresAt: urlExpiresAt });
  return { uploadId: upload.id, status: upload.status, url, urlExpiresAt };
}

export async function finalizeUpload(ctx: Ctx, input: { uploadId: string }) {
  const upload: Upload | null = await ctx.db.uploads.get(input.uploadId);
  if (!upload || upload.accountId !== ctx.accountId) throw new UploadNotFound();

  if (upload.status === "ready") {
    // A retried finalize counts nothing twice. It only re-sends a summary job that may have been
    // lost between commit and enqueue; the job exits if the summary already left "queued".
    if (upload.summaryStatus === "queued") await ctx.jobs.enqueue("summarize", { uploadId: upload.id });
    return { uploadId: upload.id, status: upload.status, size: upload.size };
  }
  if (upload.status === "failed") throw new UploadFailed(upload.failure ?? "unknown");
  if (upload.expiresAt <= Date.now()) throw new UploadExpired();

  // Charge the measured stored size, never the declared one.
  const stored = await ctx.storage.head(upload.id);
  if (!stored) throw new UploadNotReceived();

  if (stored.size > upload.size) {
    await ctx.db.transaction(async (tx: any) => {
      const current: Upload = await tx.uploads.get(upload.id);
      if (current.status === "pending") await tx.uploads.patch(upload.id, { status: "failed", failure: "size_mismatch" });
    });
    await ctx.storage.delete(upload.id);
    throw new UploadSizeMismatch();
  }

  const result: Upload = await ctx.db.transaction(async (tx: any) => {
    const current: Upload = await tx.uploads.get(upload.id);
    if (current.status !== "pending") return current;
    if (current.expiresAt <= Date.now()) throw new UploadExpired();

    // The reservation already proved room for the declared size, and stored <= declared, so this
    // commit cannot push usage past the cap that admitted it.
    const account = await tx.accounts.get(current.accountId);
    await tx.accounts.patch(account.id, { used: account.used + stored.size });
    await tx.uploads.patch(current.id, { status: "ready", size: stored.size, summaryStatus: "queued" });
    return { ...current, status: "ready", size: stored.size, summaryStatus: "queued" };
  });

  if (result.status === "failed") throw new UploadFailed(result.failure ?? "unknown");
  if (result.summaryStatus === "queued") await ctx.jobs.enqueue("summarize", { uploadId: result.id });
  return { uploadId: result.id, status: result.status, size: result.size };
}

// Scheduled sweep. Expired reservations already stop counting the moment they expire; this marks
// them failed and deletes any bytes that landed late, so nothing stored goes uncounted.
export async function expireAbandonedUploads(ctx: Pick<Ctx, "db" | "storage">, now = Date.now()) {
  const stale: Upload[] = await ctx.db.uploads.list({
    status: "pending",
    expiresBefore: now,
    limit: EXPIRE_BATCH_SIZE,
  });
  for (const upload of stale) {
    const expired: boolean = await ctx.db.transaction(async (tx: any) => {
      const current: Upload = await tx.uploads.get(upload.id);
      if (current.status !== "pending" || current.expiresAt > now) return false;
      await tx.uploads.patch(current.id, { status: "failed", failure: "abandoned" });
      return true;
    });
    if (expired) await ctx.storage.delete(upload.id);
  }
  return { expired: stale.length, more: stale.length === EXPIRE_BATCH_SIZE };
}

````

> Result: The file <run>\builds\4-quota-reservation-under-concurrency-new-opus\work\packages\backend\src\uploads.ts has been updated successfully. (file state is current in your context — no need to Read it back)

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work/packages/backend/src\" && python - <<'EOF'\np='uploads.ts'; s=open(p).read()\ns=s.replace(\"\"\"  for (const upload of stale) {\n    const expired\"\"\",\"\"\"  let expiredCount = 0;\n  for (const upload of stale) {\n    const expired\"\"\")\ns=s.replace(\"\"\"    if (expired) await ctx.storage.delete(upl [... 424 more characters]`

> Result: uploads.ts(2,26): error TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'. Did you mean './ctx.js'? uploads.ts(14,8): error TS2835: Relative import paths need explicit file extensions in ECMAScript imports when '--moduleResolution' is 'node16' or 'nodenext'. Did you mean './errors.js'? exit 2

**Assistant:** That's the pre-existing extensionless import style; checking with bundler resolution instead:

**Tool call `Bash`:** `{"command": "cd \"<run>/builds/4-quota-reservation-under-concurrency-new-opus/work/packages/backend/src\" && npx -y -p typescript@5.8 tsc --noEmit --strict --target es2022 --module esnext --moduleResolution bundler ctx.ts errors.ts uploads.ts; echo exit $?"}`

> Result: exit 0

**Assistant:** Now the design doc.

**Tool call `Write`:** `<run>\builds\4-quota-reservation-under-concurrency-new-opus\work\docs\quota-accounting.md`

````text
# Quota accounting

How uploads and AI summaries count against an account's storage cap. `docs/brief.md` remains the source of truth for product decisions. This document records the accounting design that follows from it. Each assumption the owner has not confirmed is marked **Assumption** and collected under [Open decisions](#open-decisions).

Implementation: `packages/backend/src/uploads.ts`.

## Problems with the flow before this change

1. **Concurrent uploads overshoot the cap.** `startUpload` only checked `used + size <= cap`, and `used` grows at finalize. The CLI's 8 parallel uploads (or any agent over MCP) each passed the check against the same `used` and together exceeded the cap.
2. **Retries double-count.** A retried `finalizeUpload` added the size to `used` a second time and queued a second paid summary.
3. **The declared size was trusted.** Usage was charged from the `size` the client declared, and the signed URL did not bind the length. A client could declare 1 byte and store gigabytes.
4. **Abandoned uploads were never resolved.** A started upload that was never finalized held no reservation. Its bytes could still land in storage without ever being counted.
5. **No ownership check at finalize.** Any caller could finalize any `uploadId`, which charged the owning account and started a paid summary.
6. **Read-modify-write on `used`.** Two finalizes at the same moment could each read the same `used` and lose one increment.

## Model

An account's storage position has two parts:

- **`used`**: bytes of files that finished uploading, charged from the **measured stored size**. It is a stored counter on the account, changed only inside a transaction together with the upload status change that justifies it.
- **reserved**: the sum of declared sizes of the account's uploads that are `pending` and not yet expired. It is **derived** from upload rows, not stored as a counter. An expired reservation stops counting the moment it expires, even before any sweep runs.

The admission rule for a new upload is:

```text
used + reserved + requested <= cap
```

The check and the insert of the new reservation happen in one transaction that conflicts with every other reservation or finalize on the same account. Parallel starts are therefore admitted one at a time, and the eighth CLI file is refused if the first seven have taken the room.

### Upload states

```text
pending ──finalize (stored <= declared)──▶ ready
   │  └──finalize (stored > declared)───▶ failed + size_mismatch   (bytes deleted)
   └──expiry sweep──────────────────────▶ failed + abandoned       (bytes deleted)
```

- `pending` holds a reservation of the declared size until `expiresAt`.
- `ready` is counted in `used` at the measured size. The reservation ends at the same moment, in the same transaction.
- `failed` counts nothing. The failure kind is stored so the client can tell the user to upload again rather than show a generic error.

## Flow

### `startUpload { name, size, idempotencyKey? }`

1. Validate the size: a positive safe integer no larger than the per-file limit (`MAX_FILE_BYTES`, 2 GiB).
2. In one transaction:
   - Read the account. This serializes the transaction against the account's other reservations and finalizes.
   - If `idempotencyKey` matches an existing upload on this account, return that upload. A timed-out CLI request that is retried gets the same reservation back instead of a second one. Reusing a key with a different name or size is refused.
   - Refuse with `too_many_open_uploads` if the account already has `MAX_OPEN_UPLOADS` (16) live reservations. This internal anti-abuse bound is never shown as a plan feature, and it is twice the CLI's concurrency.
   - Refuse with `quota_exceeded` if the upload does not fit. The error carries cap, used, reserved, and requested sizes so the surface can explain the stop.
   - Insert the `pending` row with `expiresAt = now + URL TTL (1 h) + finalize grace (15 min)`.
3. Sign a PUT URL that binds `Content-Length` to the declared size and expires at `expiresAt - grace`. **No URL outlives its reservation.** A replayed key re-signs a URL only while the reservation is still live. If it has expired, the replay fails with `upload_expired` and the client starts over with a new key.

The row is created before any byte moves, so it is the write-ahead record that can find and delete those bytes later.

### Client PUT

The client sends the bytes directly to object storage. Storage rejects a body whose length differs from the signed length.

### `finalizeUpload { uploadId }`

1. Load the upload. If it does not exist or belongs to another account, return `upload_not_found`. The response does not distinguish the two cases.
2. If it is already `ready`, return it without charging anything. This is how a retried finalize is handled. If its summary is still `queued`, re-enqueue the summary job. This recovers from a crash between commit and enqueue. The job is idempotent and does nothing unless the summary is `queued`.
3. If it is `failed` or expired, refuse with the matching code.
4. `HEAD` the object. If it is missing, return `upload_not_received` and leave the reservation open so the client can finish the PUT and finalize again before expiry.
5. If stored size > declared size, mark it `failed + size_mismatch`, delete the bytes, and refuse. Storage should already prevent this through the signed length. This step is the backstop.
6. In one transaction, re-read the upload. If it is still `pending` and live, add the **stored** size to `used`, set `status = ready`, `size = stored size`, `summaryStatus = queued`. If another finalize won the race, return its result and charge nothing.
7. After commit, enqueue `summarize`.

No cap re-check is done at finalize. The reservation already proved there was room for the declared size, and the stored size is at most that. The commit therefore never pushes `used` past the cap that admitted the upload. A plan reduction between start and finalize honors the reservation that was already granted.

### Expiry sweep: `expireAbandonedUploads`

This is a scheduled, bounded batch of 100 per run that reports `more` when another run is needed. For each `pending` upload past `expiresAt`, it marks the upload `failed + abandoned` in a transaction and then deletes its object. Deleting a missing object is a no-op. The sweep does not change accounting, because expired reservations already stopped counting. It makes sure that bytes which landed late never sit in storage uncounted. The sweep and finalize both re-check status and expiry inside their transactions, so exactly one of them wins.

**Not wired yet:** a scheduler still has to call this function. The interval is 15 minutes or less (assumption).

## Summaries

**Assumption: summaries do not count against the storage cap.** A summary is small text that the product generates, not content the user stored. Counting it would make usage grow asynchronously after an upload had already been admitted. That could push an account over its cap through no action of its own, and the user would need to reserve room for output of unknown size. When a file is deleted, its summary goes with it.

Summaries cost real money, so they are governed by a **separate ledger**:

- **Per-account internal spend limit.** This is a hidden ceiling on provider cost for summaries. It applies to every plan, free included, and is never shown as a plan number. **Assumption: US$3 per account per calendar month** as the starting number. The owner needs to confirm it before launch.
- **Admission.** Before calling the provider, the summary job atomically reserves the attempt's estimated cost against that limit, counting other open reservations, in the same way storage reservations work. If the reservation does not fit, the summary goes to `failed` with a stored kind of `spend_limit` and the user sees a clear "summaries paused for this month" state. The file itself stays uploaded and counted.
- **Settlement.** The job records the authoritative provider cost of every attempt, failed ones included, and settles the reservation to it. A failed summary charges the user's storage allowance nothing.
- **Bounded input.** The job truncates or samples the document to a fixed token budget, so the per-summary cost estimate is bounded no matter how large the file is (2 GiB maximum).
- **No automatic retry.** A failed summary retries only when the user asks. The manual retry reuses the same job path and refuses to start while a run is already in flight.
- **Enqueue is idempotent.** The job acts only when `summaryStatus` is `queued` and moves it to `running` in a transaction, so a duplicate enqueue from a retried finalize does nothing.

**Not implemented in this change:** the summarize job does not exist in this repo yet. The rules above are its contract. `uploads.ts` only sets `summaryStatus = queued` and enqueues.

## Deletion and plan changes

These rules are specified here so the accounting stays whole. The corresponding code does not exist yet.

- Permanently deleting a file subtracts its stored size from `used`, in the same transaction that removes the row, and deletes the bytes afterwards. Files in any future trash keep counting until they are permanently removed.
- When an account is over its cap, for example after a plan reduction, existing files stay readable, downloadable, and deletable. Renames and other changes that do not grow storage stay allowed. New uploads are refused until usage is back under the cap.
- A file above a reduced per-file limit is kept and served unchanged. New files must meet the current limit.

## Error codes

Expected failures throw typed errors from `errors.ts`, each with a `code`. The presentation boundary (web, CLI, MCP) maps these codes to product copy and never shows the raw message.

| Code | Next step for the user |
| --- | --- |
| `quota_exceeded` | Free space (or upgrade, if a larger plan raises the cap). Show used, in-progress, and requested sizes. |
| `file_too_large` | Use a smaller file (per-file limit). |
| `invalid_upload_size` | Client bug: the declared size is not a positive integer. |
| `too_many_open_uploads` | Wait for in-progress uploads to finish. |
| `idempotency_key_reused` | Client bug: the same key was sent for a different file. |
| `upload_not_found` | Start the upload again. |
| `upload_not_received` | Finish sending the file, then finalize again. |
| `upload_expired` | Start the upload again. |
| `upload_size_mismatch` | Start the upload again. The file changed or the size was wrong. |
| `upload_failed` | Start the upload again. The stored kind says why. |

## Infrastructure contract this code relies on

- `ctx.db.transaction(fn)` serializes concurrent transactions that read the same account row, for example through serializable isolation (as in Convex mutations) or a `SELECT … FOR UPDATE` on the account. Without this, reservations are not atomic.
- `uploads` supports `find({ accountId, idempotencyKey })`, `list({ accountId, status })`, and `list({ status, expiresBefore, limit })`, each backed by an index.
- `storage.signPut(key, { contentLength, expiresAt })` produces a URL that binds the length and expires at the given time. `storage.head` returns the stored size. `storage.delete` is idempotent.
- The object key is the opaque upload id. The user's filename is stored only in the database.

## Assumptions made without the owner

1. Summaries are outside the storage cap and governed by a hidden spend limit instead (see above).
2. The spend limit is **US$3 per account per calendar month**. This is a placeholder that must be confirmed before launch.
3. The per-file limit is **2 GiB**. It stays below the 5 GiB single-PUT ceiling, so multipart upload is not needed yet. A larger limit requires multipart upload.
4. There are at most **16 open uploads per account**.
5. The upload URL TTL is **1 h**, plus **15 min** of finalize grace.
6. Empty (0-byte) files are refused.
7. `idempotencyKey` is **optional**, so existing clients keep working. The CLI and the MCP server should send one per file so that timeout retries reuse their reservation. Without a key, a retried start holds a duplicate reservation until it expires (1 h 15 min). That can block uploads temporarily but never over-charges.
8. `used` stays a stored counter for read speed. A periodic reconciliation that recomputes it from `ready` rows is recommended but not built.
9. Units are bytes, and 10 GB on the free plan means 10 × 10⁹ bytes unless the owner prefers GiB. The cap value itself is unchanged and still read from `account.cap`. It should derive from a plan constant in code.

## Open decisions

- Confirm or change assumptions 1–4 and 9. They affect what users can do and what the product pays.
- Decide whether `idempotencyKey` should become required before the public launch.

## Follow-up work

- Wire `expireAbandonedUploads` into a scheduler.
- Build the summarize job against the contract above, including the spend ledger.
- Implement deletion accounting.
- Add the db indexes listed above, plus a storage adapter for `signPut`, `head`, and `delete` with a bound length.
- Update the CLI and MCP clients to send `idempotencyKey`.
- Map the new error codes to copy in each client.
- Add tests for parallel starts at the cap boundary, duplicate finalize, a finalize racing the sweep, oversized stored bytes, and replayed idempotency keys.
- Add rate limiting at the edge. It is a separate gate from quota.

````

> Result: File created successfully at: <run>\builds\4-quota-reservation-under-concurrency-new-opus\work\docs\quota-accounting.md (file state is current in your context — no need to Read it back)

**Assistant:** I've written the design to `docs/quota-accounting.md` and updated `packages/backend/src/uploads.ts` to match. To make it work I also had to change `ctx.ts` (new storage and database methods) and `errors.ts` (typed error codes). The new code compiles with `tsc --strict`, but there are no tests, nothing has run against a real database or storage, and nothing is committed.

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

**Session ended:** success, 12 turns, 184505 ms
