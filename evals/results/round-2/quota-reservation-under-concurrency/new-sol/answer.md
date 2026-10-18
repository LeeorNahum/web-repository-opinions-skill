Implemented the design in [docs/quota-accounting.md](docs/quota-accounting.md) and updated the upload handlers and context contracts.

Uploads now reserve capacity atomically, charge verified bytes once, and create a durable summary job. Retries, expiry, cancellation, and ownership checks are covered.

Documented assumptions include decimal GB, one-hour reservations, and summaries excluded from storage usage with separate provider-spend controls.

All 13 tests and strict typechecking pass. Production adapters, worker wiring, and migration remain documented launch requirements; those components aren’t present in this repository.