# Bootstrap

Never assume the auth provider's user and the app database's user exist at the same moment. A robust app bootstraps on every authenticated entry.

Order on any route that can be opened directly:

1. Read the provider identity.
2. Find or create the app user.
3. Ensure the default workspace or account exists.
4. Resolve the active workspace.
5. Only then read protected, membership-gated data.

Do not rely only on a signup webhook to create user-owned rows. Webhooks can lag, fail, or arrive after the user first opens the app. The webhook is an optimization, not the source of the row.

If a first-login flow ever requires a refresh to work, the order of operations is wrong, not the timing.

Prefer workspaces and memberships from the start when personal accounts, future teams, sharing, or workspace billing are plausible. Retrofitting ownership later is far more expensive than carrying a workspace boundary early.
