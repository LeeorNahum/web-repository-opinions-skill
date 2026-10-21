# Admin

Admin is a gated internal surface, not a hidden corner of the user app. Gate it by an admin role checked on the server, never by an unlinked route or a client-only check.

Keep the operator and admin allowlist the server checks against in versioned code, reviewed in code review. Who counts as internal staff is a product decision, so it lives with the code alongside the other product constants. Keep it independent of every workspace and tenant role, since customers administer their own workspaces.

What admin surfaces exist for:

- Inspecting job failures and raw provider detail kept out of the user UI
- Viewing usage and cost so thin margins stay visible
- Support actions on accounts and workspaces

A non-admin sees no admin entry point, and an admin URL they open shows the product's not-found page.
