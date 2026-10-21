# Quota

Check quota before doing expensive work, reserve it when concurrent requests could oversubscribe it, record usage only after durable success, and release whatever the work did not use.

- Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known.
- For imported files, read metadata first and block early if it cannot fit.
- For work whose final size is unknown until it ends, let it begin if allowance remains, warn near the limit, and stop at the limit.
- When more than one request against the same allowance can be in flight, reserve atomically against remaining capacity, counting reservations already open, because a check alone lets parallel requests each pass and together exceed the limit. Give every reservation an expiry, so an abandoned one frees itself.
- When a user selects a batch, check and reserve the whole batch against the remaining quota once before any item starts, because a per-item check admits a batch the limit was written to prevent.
- Record usage once per operation, after the work durably succeeds, from the measured result such as the stored size, so a retried completion counts nothing twice. Refuse a completion whose measured size exceeds what it reserved.
- When deleted content stays recoverable, count it toward a storage allowance until it is permanently removed.

A quota stop names the quota and offers only a remedy that clears it: an upgrade only when a bigger plan raises that ceiling, otherwise freeing capacity.

Recording usage before success means a failed job can bill a user for nothing. Checking after expensive work means you pay a provider before discovering the user had no room. Order both correctly: check before, record after.
