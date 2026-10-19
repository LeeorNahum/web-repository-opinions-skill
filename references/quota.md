# Quota

Check quota before doing expensive work, reserve it when concurrent requests could oversubscribe it, charge usage only after durable success, and release whatever the work did not use.

- Before moving large bytes or starting an expensive provider job, check the limit when size or duration is known.
- For imported files, read metadata first and block early if it cannot fit.
- For live capture where the final size is unknown, let work begin if time remains, warn near the limit, and stop when the limit is reached.
- When more than one request against the same allowance can be in flight, reserve atomically against remaining capacity, counting reservations already open. A check alone lets parallel requests each pass and together exceed the limit. Give every reservation an expiry, so an abandoned one frees itself.
- Record usage once per operation, after the work durably succeeds rather than when it is requested, from the measured result such as the stored size, so a retried completion counts nothing twice.

Never leave the user with a generic failure when the real cause is quota. A quota stop is a clear, explained state, not a mystery error.

Charging before success means a failed job can bill a user for nothing. Checking after expensive work means you pay a provider before discovering the user had no room. Order both correctly: gate before, charge after.

A product allowance and an external cost are separate ledgers. Failed work charges the user's allowance nothing, but a provider may still have billed the product for it. Count every attempt's provider cost, failed ones included, against a per-account internal spend limit with a concrete number from the first release, kept separate from the plan allowance and never shown to the user, stop admitting paid work at that limit, and record what each attempt cost, rather than treating failed work as free.
