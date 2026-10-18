Created [docs/downgrade-policy.md](docs/downgrade-policy.md) with exact access rules, backend enforcement requirements, explicit assumptions, and a worked check against the typical cancellation.

Key choices: retain data, cover the oldest 25 books, gate oversized photos, and block storage growth while allowing cleanup.

No backend exists yet, so enforcement is specified rather than verified.