# AI Model Routing

Use a layered model stack. The Vercel AI SDK is the in-process TypeScript boundary for typed calls, schema-validated structured outputs, instrumentation, and middleware. OpenRouter is the default hosted routing gateway beneath it, connected through its AI SDK provider adapter, for upstream provider failover, broad model access, and a native per-request cost ledger.

The AI SDK boundary is non-negotiable because the gateway must stay swappable. Keep direct provider adapters behind the same boundary as an escape hatch when a pinned latency target or contractual requirement calls for a direct route.

## Production Routes

Build production routes from small, pinned model pools that have passed the product's evaluation. A pool is an approved set of exact model versions and eligible provider routes tested against the same schemas, policies, and borderline inputs.

- Let the gateway fail over among approved upstream providers for the selected pinned model.
- Make fallback to a second pinned model an explicit application decision after that model passes the same evaluation.
- Keep fallback to a direct provider key explicit at the application layer.
- Log every fallback with the requested route, actual model and provider, reason, schema result, latency, token usage, and cost record.

Keep broad dynamic model fallback chains out of production. A substitute model changes behavior on borderline inputs even when it satisfies the same output schema.

## Cost And Free Routes

Use free-tier routed models only for development and evaluation. Never send production traffic to them.

Route usage-billed model work through the gateway and account from its actual per-request cost records. Persist the gateway request or generation identifier, actual model and provider, native token usage, and actual cost. Published tariffs and token-based estimates are planning inputs, never the billing ledger.
