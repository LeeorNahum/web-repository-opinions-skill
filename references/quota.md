# Quota

Check quota before doing expensive work. Charge usage only after durable success.

- Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known.
- For imported files, read metadata first and block early if it cannot fit.
- For live capture where the final size is unknown, let work begin if time remains, warn near the limit, and stop when the limit is reached.
- Record usage after the work durably succeeds, not when it is requested.

Never leave the user with a generic failure when the real cause is quota. A quota stop is a clear, explained state, not a mystery error.

Charging before success means a failed job can bill a user for nothing. Checking after expensive work means you pay a provider before discovering the user had no room. Order both correctly: gate before, charge after.
