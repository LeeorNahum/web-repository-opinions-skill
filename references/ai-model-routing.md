# AI Model Routing

Use a layered model stack. The Vercel AI SDK is the in-process TypeScript boundary for typed calls, schema-validated structured outputs, instrumentation, and middleware. Select a hosted routing gateway for the workload's hosting platform when it meets the product's routing, provider-policy, privacy, observability, and authoritative-cost needs. Choose another compatible gateway when it meets those needs better.

The AI SDK boundary is non-negotiable because the gateway and upstream providers must stay swappable. Keep direct provider adapters behind the same boundary as an explicit escape hatch when a pinned latency target or contractual requirement calls for a direct route.

## Production Routes

Build production routes from small, pinned model pools that have passed the product's evaluation. A pool is an approved set of exact model versions, eligible upstream providers, privacy requirements, and permitted fallback transitions tested against the same schemas, policies, and borderline inputs.

- Approve upstream provider routes by capability, reliability, retention, prompt-training use, region or residency, and contractual conditions. Enforce the approved provider set in gateway configuration.
- Let the gateway fail over only among approved upstream providers for the selected pinned model.
- Make fallback to a second pinned model an explicit application decision after that model passes the same evaluation.
- Keep fallback to a direct provider key explicit at the application layer.
- Log every fallback with the requested route, actual served model and upstream provider, reason, schema result, latency, native token usage, gateway request or generation identifier, and authoritative cost record.

Keep broad dynamic model fallback chains out of production. A substitute model changes behavior on borderline inputs even when it satisfies the same output schema.

## Cost And Free Routes

Use free-tier routed models only for development and evaluation. Never send production traffic to them.

Route usage-billed model work through a gateway or provider path that exposes an authoritative per-request cost record. Persist the requested route, actual served model and provider, gateway request or generation identifier, native token usage, latency, fallback data, and actual cost. Keep a charge pending for reconciliation if its authoritative cost arrives later. Published tariffs and token-derived estimates are admission, planning, and diagnostic inputs, never the final production billing ledger.
