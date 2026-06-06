# Modularity

Build so the codebase is easy to change later. The cost that matters is not writing a feature once; it is swapping a system, adding a caller, or rerouting a flow a year from now. Design for that.

## Name By Role, Not Vendor

Name modules, functions, and folders after the capability they provide, not the provider behind it and not a forced generic placeholder. Choose the most accurate word for what the code actually does in this product, then keep the vendor name inside the adapter that talks to it. When the vendor changes, only the adapter changes, and every caller keeps working. Picking the truest concept name, rather than defaulting to either the vendor or a vague catch-all, is what keeps the boundary meaningful.

## Isolate Integrations Behind Adapters

Each external system sits behind one boundary that speaks the product's own vocabulary. Callers depend on the capability, not on the provider's response shape, error format, or SDK. Two levels of swap stay cheap:

- Swapping the vendor of one capability touches only that adapter.
- Swapping an entire system for another touches only the boundary, not the flows that use it.

Keep provider payloads, model names, and SDK types from leaking past the adapter into general app code.

## Make Capabilities Routable

When a flow takes an input through a system and produces an output, build the system as a callable capability, not as logic welded inside one button handler or one route. Then any trigger can drive the same capability and get the same result: a UI action, a server route, a scheduled job, a webhook, or a future client.

Prefer a shape where the trigger and the core are separable. The button calls the capability; an API endpoint can call the same capability; both produce the same output. This avoids rebuilding the logic the day a second entry point is needed.

## Think In The Whole Chain

Design each flow as a sequence of steps that can be reasoned about and connected cleanly, with attention to how systems hand off to each other and in what order. Many failures come from connection order, not from any single step being wrong. Make the handoffs explicit so a flow can be extended, reordered, or partially reused.

## Right-Size The Complexity

Modularity is for change that is plausible, not every change imaginable. Do not add layers, indirection, or seams for a swap that will never happen. Build the boundary where a real future swap or a real second caller is likely, and keep everything else direct. The goal is a clean chain that is easy to augment, not an over-engineered framework.
