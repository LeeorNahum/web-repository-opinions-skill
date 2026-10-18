import type { Ctx } from "./ctx";
import { QuotaExceeded } from "./errors";

export async function startUpload(ctx: Ctx, input: { name: string; size: number }) {
  const account = await ctx.db.accounts.get(ctx.accountId);
  if (account.used + input.size > account.cap) throw new QuotaExceeded();
  const upload = await ctx.db.uploads.insert({ accountId: ctx.accountId, name: input.name, size: input.size });
  return { uploadId: upload.id, url: await ctx.storage.signPut(upload.id) };
}

export async function finalizeUpload(ctx: Ctx, input: { uploadId: string }) {
  const upload = await ctx.db.uploads.get(input.uploadId);
  const account = await ctx.db.accounts.get(upload.accountId);
  await ctx.db.accounts.patch(account.id, { used: account.used + upload.size });
  await ctx.db.uploads.patch(upload.id, { status: "ready" });
  await ctx.jobs.enqueue("summarize", { uploadId: upload.id });
}
