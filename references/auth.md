# Auth

Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself; the provider owns credential security.

## One Auth Route

Authentication lives at a single route, `/auth`, handled by the provider's integration. Keep it as one route rather than separate sign-in, sign-up, and callback paths with redirect-back juggling. A single integrated route avoids the redirect dance and the post-login bounce, and it returns the user straight into the product.

Auth route structure is a product decision and lives in code, not env. Do not add sign-in and sign-up env keys out of habit.

## Disable Email And Password

Default to social sign-in with the providers you choose, and turn email and password off. With a managed provider you gain nothing by storing credentials, and an email and password path adds a surface to secure and support for little benefit.

Enable email and password only when you must serve users who lack every social provider you offer. Absent that need, disable email sign-up and sign-in in the provider dashboard, and keep any implication of it out of naming, UI, and env comments.

## Social Sign-In With Account Selection

Use custom OAuth credentials for each social provider, and enable the account-selector prompt so a user can switch accounts after signing out instead of being locked into the last session.

Some providers gate this behavior behind custom credentials. In Clerk specifically, the account-selector prompt can only be enabled once you supply your own OAuth client ID and secret; the shared development credentials do not expose it. Always create custom credentials so account switching works, even in development.

## Stage Separation

Use separate OAuth credentials per stage. Each auth instance issues a different redirect URI, and a credential validates the exact redirect URI on every login, so sharing one credential across dev and production widens the blast radius of a leak. Keep dev/test and production credentials separate, matching the two provider stages.

Integration contract names, such as a JWT template name, can be code conventions. Make them env only if deployments truly need different names.

## Identity And Deletion

Store the provider's stable subject identifier on the application user. Provider webhooks and account cleanup resolve by that subject, not mutable email, handle, or profile data.

Account deletion webhooks follow a strict contract:

- Verify the signature before trusting the payload.
- Deduplicate delivery by the provider event ID.
- Treat repeated delivery as successful completion.
- Enqueue bounded cleanup instead of deleting an account graph inside the HTTP request.
- Remove only user-owned relationships, deduplication rows, and private metadata.
- Delete the application user record last.
- Preserve shared objects the user referenced but did not own.

Ask before changing OAuth callback hosts or production auth settings.
