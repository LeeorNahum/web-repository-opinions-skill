# Continuous Integration

Use GitHub Actions for repository verification by default. Keep deployment with the existing hosting integration when it already owns that job. Give each runtime and published artifact one publishing owner.

- Run lint, typecheck, contract, and unit tests on every push and every pull request. Pin the runtime and package manager and install from the frozen lockfile.
- Keep verification non-deploying and credential-free where possible. Give generation and deployment separate commands when generation contacts or changes a provider.
- Run live-service and installed-client checks explicitly, with bounded timeouts and scoped credentials. Report an unavailable check as unverified, not passed.
- Validate a release candidate before publishing it. Separately verify the published artifact and update channel afterward, so the pre-release gate never requires its own future release to exist.
- When shipping an installable package, validate the actual packaged files as well as the source.
- Use read-only workflow permissions by default. Grant release writes only to the release job, and keep secrets out of untrusted pull-request execution.
- Require successful checks before promotion. When the repo publishes a versioned artifact, publish it from the reviewed commit and verify that an existing installation can update to it.

## Artifact Workflows Follow The Deploy Gate

Expensive workflows trigger on the same branches the hosting config deploys, `main` and `preview`, never on every `dev` or feature-branch push. This covers any workflow that compiles installers, packages, or full production bundles. Runner minutes are metered, artifact storage is capped and its usage meter recalculates slowly, and a working branch that builds an installer per commit can exhaust the storage quota and block the release pipeline itself.

- Put the gate in the trigger of each release-candidate and artifact-producing workflow, with `workflow_dispatch` kept for manual runs:

  ```yaml
  on:
    workflow_dispatch:
    push:
      branches: [preview, main]
  ```

- Scope a release workflow that builds from version tags to those tags instead of `main`. The pre-release workflow then triggers on `preview` alone, because a `main` push would rebuild what the tag build already owns.
- Set `retention-days` to 7 or fewer on every non-release artifact upload. Only release artifacts earn long retention.

The gate lives in each workflow's own trigger lines, so it has no copyable asset. A repository with no artifact-building workflows has nothing to gate.

## Verify Against The Task Runner You Actually Have

A gate you run wrong is a gate you did not run, and the failure is silent: the command exits zero and you believe the check passed.

- **Know what your runner's cache flags mean before repeating them.** Check whether the invocation reads cached results, writes new entries, or does both. Use the runner's documented controls when a check must execute again, and confirm from its output that it did.
- **A flag on the workspace script is not always a flag on the runner.** Package managers forward extra arguments to the underlying script, so the same flag can land on the task runner in one invocation and on the tool inside a package in another, where it is an unknown option. Check where it landed rather than assuming.
- **A fresh worktree is not a working checkout.** Reviewing a snapshot in a detached worktree requires installing dependencies there first. Otherwise every gate fails for a reason that has nothing to do with the change, and the review reports on the runner instead of the code.

Prefer the smallest command that proves the thing, and read its output rather than its exit code.
