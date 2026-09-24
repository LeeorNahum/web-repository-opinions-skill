# Continuous Integration

Use GitHub Actions for repository verification by default. Keep deployment with the existing hosting integration when it already owns that job. Give each runtime and published artifact one publishing owner.

- Run deterministic lint, type, contract, and test checks on pull requests. Pin the runtime and package manager and install from the frozen lockfile.
- Keep verification non-deploying and credential-free where possible. Give generation and deployment separate commands when generation contacts or changes a provider.
- Run live-service and installed-client checks explicitly, with bounded timeouts and scoped credentials. Report an unavailable check as unverified, not passed.
- Validate a release candidate before publishing it. Separately verify the published artifact and update channel afterward, so the pre-release gate never requires its own future release to exist.
- When shipping an installable package, validate the actual packaged files as well as the source.
- Use read-only workflow permissions by default. Grant release writes only to the release job, and keep secrets out of untrusted pull-request execution.
- Require successful checks before promotion. When the repo publishes a versioned artifact, publish it from the reviewed commit and verify that an existing installation can update to it.

Tests that compare documentation strings prove copy consistency. Features that depend on client discovery or cached installation state need fresh-client behavior tests too.

## Artifact Workflows Follow The Deploy Gate

Expensive workflows trigger on the same branches the hosting config deploys, `main` and `preview`, never on every `dev` or feature-branch push. This covers any workflow that compiles installers, packages, or full production bundles. Runner minutes are metered, artifact storage is capped and its usage meter recalculates slowly, and a working branch that builds an installer per commit can exhaust the storage quota and block the release pipeline itself.

- Run cheap correctness checks, lint, typecheck, and unit tests, on every branch. They are the point of per-push CI.
- Put the gate in the trigger of each candidate, acceptance, and artifact-producing workflow, with `workflow_dispatch` kept for manual runs:

  ```yaml
  on:
    workflow_dispatch:
    push:
      branches: [preview, main]
  ```

- Scope a release workflow that builds from version tags to those tags instead of `main`. Its candidate workflow then needs only the acceptance branch, because a `main` push would rebuild what the tag build already owns.
- Keep artifact retention short on candidate workflows. Only release artifacts earn long retention.

The gate lives in each workflow's own trigger lines, so it has no copyable asset. A repository with no artifact-building workflows has nothing to gate.
