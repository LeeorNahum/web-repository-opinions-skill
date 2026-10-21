# Background Jobs

Provider-backed and long-running work runs as explicit jobs with explicit state, never as fire-and-forget calls scattered through route handlers.

Give every job a test for a provider success followed by a failed database write, for a row whose provider object is gone, and for a second start while one run is in flight.

User-facing job status stays coarse. Store the internal step and the raw provider detail as metadata for operators, and show the user a simple, honest state.

For work that can exceed one transaction or function budget, persist a phase and process bounded batches. Each invocation completes one small idempotent step, records progress, and schedules the next step. Repeated invocation resumes safely rather than restarting or duplicating effects.

Use generation or version tokens when newer state can supersede a scheduled job before it runs. The job verifies the token and exits without changing current data when it represents an older snapshot.
