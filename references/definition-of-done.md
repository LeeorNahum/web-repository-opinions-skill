# Definition Of Done

A feature is done only when all of these hold:

1. The user flow works end to end.
2. The data state machine makes sense.
3. Provider state is aligned with the code.
4. Failure paths are explicit and actionable.
5. Env contracts match what the code actually reads.
6. Generated clients and types are current.
7. Builds and typechecks pass for every affected app and package.
8. Focused behavioral tests cover the changed contracts and failure paths.
9. Required migrations have been dry-run, executed in approved environments, and independently verified.
10. The target branch and its target runtime agree.
11. Deferred manual steps are named clearly.

If any are false, the work is not done. It is locally edited.

Verification before calling a repo ready:

- Search for stale names: old app folders, old package names, old env keys, old route shapes.
- Check every `.env.example` against real code reads.
- Confirm no unjustified root env files and that real local env files are ignored.
- Run typechecks, builds, and backend codegen.
- Run focused tests for partial success, all-failure, retries, stale jobs, repeated webhook delivery, and canonical URL state when those behaviors changed.
- Verify migrations against real non-production data before higher-stage rollout.
- Confirm docs and prompts match the current structure.

Only call it ready when code, env contracts, docs, and runtime all agree.
