# Deployment

Control which branches deploy explicitly. Only `main` and `preview` should auto-deploy; everything else is blocked.

Each deployable app carries a hosting config that gates deploys by branch:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "git": {
    "deploymentEnabled": {
      "main": true,
      "preview": true,
      "*": false
    }
  }
}
```

- `"*": false` blocks all branches by default, including `dev` and feature branches.
- List explicit branches first and the wildcard last. Order is cosmetic.
- Keep `$schema` for editor autocomplete; it is harmless at runtime.

Which branch is production is a dashboard setting, not part of this config. Confirm the production branch is `main` once per project so the platform does not silently fall back to another branch.

Custom domains, branch domains, and env vars are dashboard concerns, not part of the deploy-gating config. Document them in the setup checklist.

When the app and site are separate deployables, they are separate hosting projects with their own domains and env, sharing the same backend.

See `assets/vercel.json` for a copyable starter.
