# Modularity

Build the product as connected capabilities, not one long implementation welded to its first trigger and destination. The cost that matters is not writing a feature once. It is adding a caller, changing a provider, redirecting output, or repairing one section without breaking the whole flow.

Treat boundaries like standard pipe fittings. A capability should accept a product-shaped input, perform one owned job, and return a product-shaped output that another capability can consume. Its first caller and first destination are examples, not permanent parts of its identity.

## Name By Role, Not Vendor

Name modules, functions, and folders after the capability they provide, not the provider behind it and not a forced generic placeholder. Choose the most accurate word for what the code actually does in this product, then keep the vendor name inside the adapter that talks to it. When the vendor changes, only the adapter changes, and every caller keeps working. Picking the truest concept name, rather than defaulting to either the vendor or a vague catch-all, is what keeps the boundary meaningful.

## Isolate Integrations Behind Adapters

Each external system sits behind one boundary that speaks the product's own vocabulary. This is the ports and adapters (hexagonal) pattern: the product owns the port in its own terms, and each adapter translates one provider onto it, acting as an anti-corruption layer that keeps provider shapes out of the product's model. Callers depend on the capability, not on the provider's response shape, error format, or SDK. Two levels of swap stay cheap:

- Swapping the vendor of one capability touches only that adapter.
- Swapping an entire system for another touches only the boundary, not the flows that use it.

Migrate a replacement with the strangler fig pattern: stand the new adapter up beside the old one and route callers over once it covers every case, removing the old integration only after the new one is proven. Keep provider payloads, model names, and SDK types from leaking past the adapter into general app code.

## Make Capabilities Routable

When a flow takes an input through a system and produces an output, build the system as a callable capability rather than logic embedded in one button handler or route. Any authorized trigger can then drive the same capability: UI, public API, MCP, scheduled job, webhook, CLI, or a future client.

Keep trigger adapters, product rules, provider adapters, and destination adapters separately replaceable. The button and API endpoint translate their inputs into the same product command. The capability enforces the rules once. Each output adapter translates the result for its destination.

UI, public API, MCP, jobs, and webhooks call shared product capabilities. They adapt inputs and outputs for their protocol but do not reimplement product rules.

## Think In The Whole Chain

Design each flow as a sequence of explicit connections. Name what each step accepts, owns, returns, and may fail to produce. A flow should be extendable, reorderable, and partially reusable without copying its internal rules or breaking every caller.

## Right-Size The Complexity

Modularity is for plausible rerouting, not every imaginary variation. Add a boundary when a capability has multiple callers, multiple destinations, provider-owned behavior, independent failure handling, or a likely replacement. Keep one-off local transformations direct. The goal is a set of useful connection points, not an abstract framework.
