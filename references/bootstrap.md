# Bootstrap

The auth provider's user and the app database's user can come into existence at different moments. A robust app bootstraps on every authenticated entry.

Order on any route that can be opened directly:

1. Read the provider identity.
2. Find or create the app user.
3. Ensure the default workspace or account exists.
4. Resolve the workspace the route addresses, when it addresses one.
5. Only then read protected data, gated by membership or by a share of the resource.

Find or create the app user and ensure the default workspace or account on every authenticated entry, and treat the signup webhook as an optimization. Webhooks can lag, fail, or arrive after the user first opens the app, so the webhook is never the source of the row.

A first sign-in reaches working data with no refresh. When one needs a refresh, the order of operations is wrong, not the timing.
