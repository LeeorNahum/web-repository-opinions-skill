# Billing

Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth; the app reads it rather than mirroring it as the authority.

Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboard value.

Show usage against limits in clear, product-native language. A user should understand what they have used and what remains without seeing internal counters or provider identifiers.

Match billing mode to the stage: test mode for local and staging, live mode only on production. Never wire live billing into a non-production stage.

## Seats As A Value Metric

When a product's value scales with the size of a team rather than per-user usage, pricing on seats is one proven model (as many SaaS products do). It is a conditional choice, not a default: a product whose value scales on a different metric prices on that metric instead.

When you do price on seats:

- A free tier is solo: one member and no invites. With no shared organization to invite into, being solo is structural rather than a setting.
- Creating and subscribing a shared organization is the upgrade. The owner pays; invited members are free, up to the plan's included seats.
- Treat a plan's seats as an included batch at a flat price rather than a per-seat charge, so the entitlement's seat count comes from the plan, not a purchased quantity.
- Enforce the seat count at the one place a member is admitted, so a member beyond the plan's seats is refused rather than silently absorbed. An existing member or a role change never consumes a new seat.

Derive the active workspace server-side from the verified identity, never from a client-supplied id.

## Losing Or Reducing A Plan

A plan can shrink: a subscriber cancels, or downgrades below what they already own. Resolve this without destroying anything they bought.

- Lock the resources the plan no longer covers rather than deleting them. A locked resource keeps all its data and history, refuses access at every gate, and becomes usable again the instant the plan covers it once more.
- For a partial downgrade, let the owner choose which resources stay active within the new allowance instead of silently picking for them. Default to a stable, explainable rule, such as keeping the oldest, and let them change it.
- Reconcile this from one place on every subscription change, so a subscribe, upgrade, downgrade, or cancellation always converges to the same correct, non-destructive state.
- Make the locked state legible: show what is locked, why, and the single action that restores it.

Ask before changing live billing mode, plan entitlements, or anything that affects what customers are charged.
