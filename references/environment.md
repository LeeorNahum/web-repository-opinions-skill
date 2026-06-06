# Environment

Env setup should be boring, explicit, and hard to drift. An env example is a contract, not a secret store and not a deployment database. Each runtime owns its own contract. Deployed environments supply values through their host or provider.

Env is for secrets and true environment variance, not a general settings file.

## Core Standard

- Put one committed `.env.example` beside each runtime that reads env.
- Put real local values in that runtime's `.env.local` and never commit it.
- Keep `.env.example` in the same key order and grouping as `.env.local`.
- Use the same key names across local, staging, and production. The store supplies different values.
- Do not create `LOCAL_*`, `DEV_*`, and `PROD_*` triples unless one process truly connects to multiple stages at once.
- Do not add a root `.env*` unless root code genuinely reads env at runtime. Package scripts, the monorepo tool, and workspace manifests do not justify it.
- Do not create host-specific example files by default. Add a mode-specific example only when the required key set genuinely differs or a specific build artifact requires a different file.

## Keep In Env

- Secrets and API keys
- Provider account IDs
- Deployment-specific service URLs
- Webhook signing secrets
- Public keys intentionally exposed to the browser
- Cross-app origins when staging differs from production

## Keep In Code

- Route paths and fixed auth route names
- Provider model names that should be reviewed in code
- Single-provider base URLs
- Plan names and quota constants
- Supported file formats
- User-facing copy and feature flags that are not actually environment-specific

If a value changes product behavior and should be reviewed, prefer code. If it changes by store or stage, prefer env.

## Stages

Three conceptual stages. Key names stay the same across all three; only the values change by store.

- `local`: values in `.env.local`, used from the developer machine.
- `staging`: deployed non-production values, in the hosting platform's staging scope and the dev/test tier of each provider.
- `production`: live values in the production host and provider environments.

When provider resources can mix between stages, identify the intended source before wiring values. Pointing the wrong stage at a production provider is a category of mistake worth catching explicitly.

## Gitignore Contract

```gitignore
.env
.env.*
!.env.example
!.env.*.example
```

Add project-specific secret patterns when relevant (`*credentials*.json`, `*.pem`). Never unignore a real env file to make a deploy easier.

## Runtime Ownership

Each runtime that reads env gets its own `.env.example` and `.env.local` pair:

```text
<surface-a>/.env.example      -> <surface-a>/.env.local
<surface-b>/.env.example      -> <surface-b>/.env.local
packages/backend/.env.example -> packages/backend/.env.local
```

Root package scripts, workspace manifests, and build orchestration tools do not justify a root env file.

## Provider Stores

Values live in exactly one durable store per stage:

| Store | Owns |
| --- | --- |
| `.env.example` | Committed contract and setup hints |
| `.env.local` | Developer-local real values, gitignored |
| Hosting platform env (staging scope) | Deployed non-production surface values |
| Hosting platform env (production scope) | Deployed production surface values |
| Backend deployment env | Secrets the backend functions read, per deployment |
| Provider dashboards | OAuth, webhooks, API keys, and provider-owned secrets |
| CI secrets | Automation-only values |

Inspect local and example files without printing secrets. Use provider CLIs or dashboards when available and safe. Ask for values only when they cannot be found or accessed.

## Public And Server-Only

Treat `NEXT_PUBLIC_*`, `VITE_*`, and similar prefixes as browser-exposed. Never put a secret behind a public prefix. Shared packages used by client bundles may read only public env. Framework-magic keys can be real even when no direct read appears in source; do not delete provider or framework keys just because grep does not find them.

## Cleanup Workflow

1. Inventory `.env*`, `.gitignore`, manifests, and env reads.
2. Identify runtimes and their env owners.
3. Align each `.env.example` with the real local file without copying secret values.
4. Remove root env files unless justified.
5. Remove unused or future-only keys unless clearly marked.
6. Replace hardcoded production URL fallbacks with required env, safe origin inference, or a documented constant.
7. Verify deployed stage separation for provider-backed services.
8. Report missing values as key names and store locations, never secret values.

If build or test output depends on env, update the build tool's task env inputs intentionally rather than adding a root env file as a workaround.

Ask before rotating a credential, moving a secret between provider stores, or deleting a key whose usage may be framework-magic or provider-magic.
