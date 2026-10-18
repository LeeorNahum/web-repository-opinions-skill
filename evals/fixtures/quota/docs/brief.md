# Lanternfold

Lanternfold is a file vault with AI summaries. Each account has a storage cap (10 GB on the free plan). Every uploaded document gets an AI summary, which calls a paid model provider.

## Upload flow today

1. The client calls `startUpload { name, size }`. The server checks the cap, then returns a signed URL.
2. The client PUTs the bytes straight to object storage.
3. The client calls `finalizeUpload { uploadId }`. The server adds the size to the account's usage and queues the summary job.

The CLI uploads up to 8 files at once and retries a request that times out. Agents connected over MCP upload through the same API.

## Request

We are opening the free plan to everyone next month, and storage accounting has never been reviewed. Get it right before then.
