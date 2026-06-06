# Environment

Env is for secrets and true environment variance. It is a contract per runtime, not a settings file and not a deployment database.

## Core Standard

- Put one committed `.env.example` beside each runtime that reads env.
- Put real local values in that runtime's `.env.local` and never commit it.
- Keep `.env.example` in the same key order and grouping as `.env.local`.
- Use the same key names across local, staging, and production. The store supplies different values.
- Do not create `LOCAL_*`, `DEV_*`, and `PROD_*` triples unless one process truly connects to multiple stages at once.
- Do not add a root `.env*` unless root code genuinely reads env at runtime. Package scripts, the monorepo tool, and workspace manifests do not justify it.

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

## Gitignore Contract

```gitignore
.env
.env.*
!.env.example
!.env.*.example
```

Add project-specific secret patterns when relevant (`*credentials*.json`, `*.pem`). Never unignore a real env file to make a deploy easier.

## Public And Server-Only

Treat `NEXT_PUBLIC_*`, `VITE_*`, and similar prefixes as browser-exposed. Never put a secret behind a public prefix. Shared packages used by client bundles may read only public env. Framework-magic keys can be real even when grep does not find them; do not delete provider or framework keys just because no direct read appears.

## Runtime Ownership

```text
apps/site/.env.example      -> apps/site/.env.local
apps/app/.env.example       -> apps/app/.env.local
packages/backend/.env.example -> packages/backend/.env.local
```

Beyond local files, values live in their store: the hosting platform's staging and production env, the backend deployment's env, and each provider dashboard. Provider function secrets belong in the backend deployment store, not in app env.

## Cleanup Workflow

1. Inventory `.env*`, `.gitignore`, manifests, and env reads.
2. Identify runtimes and their env owners.
3. Align each `.env.example` with the real local file without copying secret values.
4. Remove root env files unless justified.
5. Remove unused or future-only keys unless clearly marked.
6. Replace hardcoded production URL fallbacks with required env, safe origin inference, or a documented constant.
7. Report missing values as key names and store locations, never secret values.

If build or test output depends on env, update the build tool's task env inputs intentionally rather than adding a root env file as a workaround.

Ask before rotating a credential or moving a secret between provider stores.
