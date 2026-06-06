# Admin

Admin is a gated internal surface, not a hidden corner of the user app. Gate it explicitly by an admin role checked on the server, never by an unlinked route or client-only check.

What admin surfaces exist for:

- Inspecting job failures and raw provider detail kept out of the user UI
- Viewing usage and cost so thin margins stay visible
- Support actions on accounts and workspaces

Keep raw provider errors, job IDs, and storage keys here, where operators need them, and out of the user-facing product entirely.

Hide admin from users who lack the role rather than showing a forbidden screen. The absence of the entry point is the gate's visible form.
