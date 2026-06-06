# Background Jobs

Provider-backed and long-running work runs as explicit jobs with explicit state, never as fire-and-forget calls scattered through route handlers.

Design every job around its failure point, not its happy path. Ask:

- What if the external call succeeds and the database update fails?
- What if the row exists but the provider object does not?
- What if the user closes the tab between steps?
- What if a retry starts while the previous run is still in flight?

Keep raw provider responses behind an adapter. Do not spread a provider's response shape through the app. The app speaks the product's own job vocabulary; the adapter translates.

User-facing job status stays coarse. Store the internal step and the raw provider detail as metadata for operators, and show the user a simple, honest state.

Route handlers must not own product rules for jobs. The same rule is needed by clients, server routes, jobs, and future clients, so it lives in shared logic.
