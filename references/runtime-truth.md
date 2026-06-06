# Runtime Truth

A change is complete when the runtime it depends on is true, not when the code compiles or a branch is pushed.

The real product is code plus database schema, backend functions, object storage, provider dashboards, env values, webhooks, queues, scheduled jobs, deployed settings, and DNS. A feature touches several of these at once.

Design every provider workflow around its order of operations, not its happy path. The failure point, not the success path, decides whether the design is sound. Ask what happens if a step half-completes, if the user leaves mid-flow, or if a retry overlaps a running job, and make the answer explicit.

When the backend function shape changes, regenerate the clients and types before claiming the app is ready. Generated files are part of the runtime contract, not a build detail.

Saying done after a Git push while a runtime deploy, migration, or provider setting is still missing is not done. It is only locally edited.
