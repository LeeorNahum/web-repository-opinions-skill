# Quota

Check quota before doing expensive work. Record usage only after the work durably succeeds, not when it is requested.

- Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known.
- For imported files, read metadata first and block early if it cannot fit.
- For work whose final size is unknown until it ends, let it begin if allowance remains, warn near the limit, and stop at the limit.
- When a user selects a batch, check the whole batch against the remaining quota once before any item starts, then record usage per item as each one durably succeeds.

A quota stop names the quota and offers only a remedy that clears it.

Recording usage before success means a failed job can bill a user for nothing. Checking after expensive work means you pay a provider before discovering the user had no room. Order both correctly: check before, record after.
