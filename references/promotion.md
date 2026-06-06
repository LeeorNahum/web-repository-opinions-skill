# Promotion

Promotion between stages includes durable runtime state, not just Git history.

Before promoting, identify what must move or already be aligned:

- Backend function deployments
- Schema migrations
- Generated backend clients
- Provider env vars
- Storage buckets
- Webhooks
- Scheduled jobs
- Platform settings

Safe non-production runtime updates can be part of a promotion when already authorized. Production updates need explicit approval when they touch secrets, billing, DNS, customer data, destructive migrations, or irreversible provider settings.

Promotion is not complete until Git, runtime state, and the target stage's checks are all updated or explicitly deferred. A merged branch with stale runtime behind it is a half-promotion.
