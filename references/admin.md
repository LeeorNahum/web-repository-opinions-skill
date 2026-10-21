# Admin

Admin is a gated internal surface, not a hidden corner of the user app.

Grant admin through a staff-only grant that the server alone can write, held by the auth provider as membership in the product's internal staff organization or as server-only user metadata, and check that grant on the server. Keep it independent of every workspace and tenant role, since customers administer their own workspaces. Keep the list of who holds it in the provider, set per stage, and record the grant procedure in the repository.

What admin surfaces exist for:

- Inspecting job failures and raw provider detail kept out of the user UI
- Viewing usage and cost so thin margins stay visible
- Support actions on accounts and workspaces

The admin surface is where raw provider errors, job IDs, and storage keys are shown.

A non-admin sees no admin entry point, and an admin URL they open shows the product's not-found page.
