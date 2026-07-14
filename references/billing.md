# Billing

Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth; the app reads it rather than mirroring it as the authority.

Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboard value.

Show usage against limits in clear, product-native language. A user should understand what they have used and what remains without seeing internal counters or provider identifiers.

Match billing mode to the stage: test mode for local and staging, live mode only on production. Never wire live billing into a non-production stage.

## Ambient Usage Display

Show a hard ceiling only where it is load-bearing: near the ceiling, at the moment an action would cross it, or inside a settings or billing surface the user opens on purpose. Leave it out of routine, always-visible chrome, a list header, a persistent counter, while the account sits comfortably under it. A limit nobody is near is not information, it is a standing reminder of a ceiling that does not matter yet, and it reads as surveillance rather than help. A free tier should feel complete, not like a metered preview of a bigger product.

The surface that blocks at the ceiling names the limit and offers only remedies that actually clear it. Sell an upgrade there only when a bigger plan truly raises that ceiling. When every plan shares the ceiling, the honest remedy is freeing capacity, and an upgrade button would be a lie.

## Seats As A Value Metric

When a product's value scales with the size of a team rather than per-user usage, pricing on seats is one proven model (as many SaaS products do). It is a conditional choice, not a default: a product whose value scales on a different metric prices on that metric instead.

When you do price on seats:

- A free tier is solo: one member and no invites. With no shared organization to invite into, being solo is structural rather than a setting.
- Creating and subscribing a shared organization is the upgrade. The owner pays; invited members are free, up to the plan's included seats.
- Treat a plan's seats as an included batch at a flat price rather than a per-seat charge, so the entitlement's seat count comes from the plan, not a purchased quantity.
- Enforce the seat count at the one place a member is admitted, so a member beyond the plan's seats is refused rather than silently absorbed. An existing member or a role change never consumes a new seat.

Derive the active workspace server-side from the verified identity, never from a client-supplied id.

## Losing Or Reducing A Plan

A plan can shrink: a subscriber cancels, or downgrades below what they already own. Resolve this without destroying anything they bought, and without a stored lock to reconcile.

- Derive coverage from the current plan at the gate, not a flag stamped on each resource. A resource the plan no longer covers keeps all its data and history and fails every gated operation with a clear, product-owned error, then works again the instant the plan covers it. When the plan covers only some of what the owner holds, a stable order decides which, such as the oldest within the allowance.
- Hold the limit at the one gate every client crosses, so the UI, the API, an agent surface, and a background job all read the same answer. An interface never grants what the plan does not cover just because its control was reachable.
- Expose the limit where it is hit, not as a standing notice: the action or call that reaches an over-the-limit resource fails with a clear, product-owned error that names the limit and leaves the remedy to the surface that can act on it.

Ask before changing live billing mode, plan entitlements, or anything that affects what customers are charged.
