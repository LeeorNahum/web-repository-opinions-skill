# Billing

Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth; the app reads it rather than mirroring it as the authority.

Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboard value.

Show usage against limits in clear, product-native language. A user should understand what they have used and what remains without seeing internal counters or provider identifiers.

Match billing mode to the stage: test mode for local and staging, live mode only on production. Never wire live billing into a non-production stage.

Ask before changing live billing mode, plan entitlements, or anything that affects what customers are charged.
