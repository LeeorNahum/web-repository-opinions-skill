# Deployment

Each deployable app owns one hosting project, its public domain, and its runtime environment contract. Shared packages do not own deployments.

Keep provider project boundaries aligned with deployable app boundaries. Split a surface into its own hosting project when the product needs it, usually in this order: site, signed-in app, API, MCP, admin, webhooks, then job runtimes. Every separate app must be able to deploy, roll back, and scale without coupling its release to another surface.

Host a commercial product, including any that takes payment or advertises something for sale, on a plan whose terms allow commercial use.

## Branch Deployment

Control branch deployment explicitly. Only `main` and `preview` auto-deploy by default. Block every other branch.

Each deployable app carries its own hosting config that gates deploys by branch. Apply the same branch policy to every app instead of configuring only the primary site. The exact starter file lives in `assets/vercel.json`. Copy it rather than maintaining another inline version.

- `"**": false` blocks every other branch by default, including `dev` and branch names with a slash such as `feature/x`, which `*` does not match. A branch that matches several rules deploys when any of them is `true`.
- List explicit branches first and the wildcard last. Order is cosmetic.
- Keep `$schema` for editor autocomplete. It is harmless at runtime.

## Runtime Configuration

Custom domains, branch domains, and env vars are dashboard concerns, not part of the deploy-gating config. Record them in the app's setup document.

Which branch is production is a dashboard setting, not part of the hosting config. Confirm `main` as the production branch once per project so the provider cannot silently select another branch. A host can promote a new project's first deployment to production whatever its branch, so make that first deployment come from `main` before production domains are attached.

Machine-facing apps skip the browser access gate that preview deployments carry, and only because that gate cannot work for them. An API, MCP, or webhook project answers programmatic requests directly, so confirm any interactive access protection (a hosting platform preview-protection or SSO gate that only a browser session can satisfy) is off for those projects. A blanket gate turns every machine call into an opaque auth failure the client cannot resolve, including on preview deployments. Replace it with a protection those clients can satisfy, such as a token, rather than leaving the surface open. An unauthenticated request to a protected machine route gets a 401 with a `WWW-Authenticate` challenge and a JSON body, never a sign-in page or redirect.

Disabling a host's browser-only protection is not permission to make preview a special exposure mode. Machine-facing preview deployments should expose the same protocol shape production will expose after promotion: same public routes, same discovery posture, same OAuth or token challenge behavior, and same authorization failures, with only stage-owned values such as origins, credentials, data, rate-limit buckets, and provider resources changing. If an endpoint or tool would be unacceptable to reveal in production, keep it out of preview too, or put it behind the same production-capable authorization and feature gate.

Treat unauthenticated discovery as public disclosure in every stage. Contracts, protocol metadata, tool catalogs, CLI help, and public examples expose only information acceptable to show in production. Keep internal names, unreleased promises, provider payloads, private identifiers, secret-shaped values, and undisclosed future work out of those surfaces. A credential-free program carries its full production posture from its first reachable preview deployment.

Private, experimental, and local-only protocol access uses an explicit private transport rather than a public preview endpoint. Use a provider-supported tunnel or private connector when a remote client must reach it.

## Dependent Service Deployment

A backend whose code lives in this repository is part of what a branch push ships, not a separate errand afterward. Wire it into the owning app's build so one push deploys the whole runtime for that stage. If deploying a stage still needs someone to run a command by hand, that is a defect in the pipeline.

Do this by overriding the app's build command to run the service's own deploy tool, giving it the app build as a command to run inside the deploy. Most such tools take exactly this shape. With Convex the build command becomes `convex deploy --cmd '<the app build>'`. It runs the app build first with the deployment's URL injected, so the client cannot be pointed at a different deployment than the one being pushed, then typechecks, regenerates code, and pushes the functions and schema. Put the build command in the repository, not in a hosting dashboard, so it is reviewable and cannot drift per project.

- Publish the frontend only after the backend push succeeds, because a frontend that ships first calls functions that do not exist yet. The host publishes a build's output only when the whole build command succeeds, so a deploy tool that wraps the app build gives this order for free, even though it builds the frontend before it pushes.
- When other services deploy independently against the same backend, prove the backend moved before publishing each of them. The backend exposes one unauthenticated query returning an exact per-generation marker value from the same source file the dependents pin. The preflight belongs in the build of each service that does not own the backend deployment, because the owning app's build runs before its own push. That preflight requires HTTP success, the exact success envelope, and the exact value, and fails on any other status, body, parse failure, timeout, or transport failure. Treat only the exact expected value as a pass.
- When the schema store validates every existing row on push, stage a newly required field. Ship it optional with an explicit safe reading for absence, backfill with a bounded resumable pass repeated to zero changes, and tighten to required only in a later release carrying the zero-change evidence.
- Fail the whole build when a dependency cannot publish. Publishing an app against a backend that never moved is worse than not deploying.
- Let the stage's credentials decide which instance a stage reaches, never the script. A build script that names a deployment can send the wrong stage to the wrong backend. One that reads a stage-scoped key cannot.
- Deploy the dependency from every deploying stage, including staging. A stage that builds this commit's frontend against a backend from some other commit is testing a combination that exists nowhere.
- Give each dependent service one deployment owner so parallel app builds cannot race to publish it.
- Keep local development commands for interactive work. Hosted promotion should use the automated path.
- Where a stage shares an instance with local development, it still deploys, and a build replaces what a developer pushed from their machine until their next local push. Prefer giving the stage its own instance, and treat sharing as the thing to fix rather than a reason to skip deploying.
- Give each parallel worktree or agent its own development backend deployment, because a push of the whole function set replaces whatever the others pushed.
