Implemented the design in [docs/quota-accounting.md](docs/quota-accounting.md) and updated [uploads.ts](packages/backend/src/uploads.ts).

The code now reserves capacity atomically, handles retries without duplicate charges or summary jobs, verifies uploaded size, and releases quota on failure, expiry, or deletion.

Documented assumptions: files and saved summaries count; each summary reserves 64 KiB; upload reservations expire after one hour.

Validation: strict TypeScript checking and all 17 tests pass.

Production integration remains: database/storage adapters, workers, cleanup scheduling, client request IDs, and separate AI spend controls. These requirements are documented.