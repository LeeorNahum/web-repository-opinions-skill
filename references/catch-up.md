# Repository Catch-Up

A repository built under an earlier version of these opinions drifts behind them, because an agent applies the skill only to what it is building. Repository Catch-Up is the one whole-repository pass that checks a repository against these opinions. Any request to check the repository against them, find what it lacks or what is new in them, or bring it up to them starts it, and it ends with the gaps implemented, not with a list, unless the request asks only for a report.

1. Read every reference in full, since this pass is the one case that loads all of them, and the whole repository: its apps and packages, workflows, env contracts, setup documents, and the docs that record its decisions.
2. For each reference, decide first whether its condition holds in this repository, from what the repository and its providers show and what the user or its docs say is planned. A reference about a part the repository does not have, such as payments, a signed-in app, or an agent plugin, finds nothing to add.
3. Check each category below whose condition holds, and sort what it finds into missing, mismatched, and improvable. The owning references hold the rules each category checks.
   - Surfaces, when the repository serves pages: the public and signed-in split, rendering posture, a favicon and link preview card on every publicly reachable page, and the legal pages and contact address their conditions call for.
   - URLs, when it has routed views: IDs, route paths, query-state restoration, and link stability across reorganization.
   - Auth, when it signs people in: bootstrap, workspace creation where the product has workspaces, and permission-gated UI that hides unavailable actions.
   - Env, when a runtime reads env: per-runtime contracts, env files beside the runtimes that read them, the same key names across stages, and every value in the secrets store when the repository keeps one, has a remote, or has a production stage.
   - Data, when it stores or imports data: ownership boundaries, external sources, search scope, media storage, and bounded data work.
   - Interaction, when it has a UI: user-facing failures, partial results, feedback, and responsive interaction states.
   - Operations: branch roles and build-cache bounds, plus verification workflows when the repository has a remote.
   - Production, when it has a production stage: production provider resources, credentials, store environment, and backend deployment with its migrations and webhooks, each apart from dev/test and recorded in its setup document.
   - Deployment, when it deploys: the `preview` stage, with its own backend deployment where the repository has a backend, plus deploy gating and DNS records when a hosting project builds from it.
   - Release, when it ships a versioned artifact or a published folder: every version mention in sync, artifact workflows on their gate, and each published folder's publish workflow.
4. Keep every deliberate alternative. A different framework or tool, or a decision recorded in the repository's own docs, stands, and the opinions apply around it in that tool's terms. When a choice looks accidental but could be deliberate, ask.
5. Implement the rest, one category at a time, verifying each the way its owning reference says it is done, and honor every "Ask before" line on the way.
6. Report what was implemented, what was kept as a deliberate alternative, and what is deferred with its blocker, in the conversation rather than in a file in the repository, and never with a secret value.
