# Deployment

Each deployable app owns one hosting project, its public domain, and its runtime environment contract. Shared packages do not own deployments.

Keep provider project boundaries aligned with deployable app boundaries. The common order is site, signed-in app, API, MCP, admin, webhooks, then dedicated job runtimes as the product proves it needs them. Every separate app must be able to deploy, roll back, and scale without coupling its release to another surface.

## Branch Deployment

Control branch deployment explicitly. Only `main` and `preview` auto-deploy by default. Block every other branch.

Each deployable app carries its own hosting config that gates deploys by branch. Apply the same branch policy to every app instead of configuring only the primary site. The exact starter file lives in `assets/vercel.json`; copy it rather than maintaining another inline version.

- `"*": false` blocks all branches by default, including `dev` and feature branches.
- List explicit branches first and the wildcard last. Order is cosmetic.
- Keep `$schema` for editor autocomplete; it is harmless at runtime.

See `assets/vercel.json` for a copyable starter.

## Runtime Configuration

Custom domains, branch domains, and env vars are dashboard concerns, not part of the deploy-gating config. Document them in the setup checklist.

Deploying is not releasing. When a change must ship before it is visible, gate the user-facing behavior behind a feature flag and switch it on once the runtime is ready, dark-launching a risky path by running it with its output withheld until verified.

Which branch is production is a dashboard setting, not part of the hosting config. Confirm `main` as the production branch once per project so the provider cannot silently select another branch.
