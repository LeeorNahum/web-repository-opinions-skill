# Billing

Use a managed billing provider for subscriptions and payments. Stripe is the default.

Match billing mode to the stage: the provider's sandbox for local and staging, live mode only on production.

## Seats As A Value Metric

When a product's value scales with the size of a team rather than per-user usage, price on seats. It is a conditional choice, not a default: a product whose value scales on a different metric prices on that metric instead.

When you do price on seats:

- A free tier admits one member, the owner, so its workspaces have no invitations.
- The owner's subscription raises the seat count in every workspace they own. The owner pays, and invited members are free, up to the plan's included seats.
- Treat a plan's seats as an included batch at a flat price rather than a per-seat charge, so the entitlement's seat count comes from the plan, not a purchased quantity.
- Enforce the seat count at the one place a member is admitted, so a member beyond the plan's seats is refused rather than silently absorbed. An existing member or a role change never consumes a new seat.

## Losing Or Reducing A Plan

A plan can shrink: a subscriber cancels, or downgrades below what they already own. Resolve this without destroying anything they bought, and without a stored lock to reconcile.

- Derive coverage from the current plan at the gate, not a flag stamped on each resource. A resource the plan no longer covers keeps all its data and history and fails every gated operation with a clear, product-owned error, then works again the instant the plan covers it. When the plan covers only some of what the owner holds, a stable order decides which, such as the oldest within the allowance.
- Hold the plan limit in one entitlement check that every client's backend path calls, beside the authorization gate and separate from it, so the UI, the API, an agent surface, and a background job all read the same answer. An interface never grants what the plan does not cover just because its control was reachable.
- A size allowance, such as total storage or the largest file, follows its own rule instead of the coverage rule above: an owner over it, in total or in one item, keeps everything stored, can still read and delete, and is refused only further growth.
- Expose the limit where it is hit, not as a standing notice: the action or call that reaches an over-the-limit resource fails with a clear, product-owned error that names the limit and leaves the remedy to the surface that can act on it.

Ask before changing live billing mode, plan entitlements, or anything that affects what customers are charged.
