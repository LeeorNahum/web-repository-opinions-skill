# Agent Tool Design

Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.

**Destructive scope is never controlled by an optional field.** An omitted argument must never widen what gets deleted or silently create a new resource. When one optional field would decide between editing and creating, or between one file and a whole resource, keep separate tools whose names carry the distinction.

**Prefer an extra tool over a conditional schema.** Agents pick wrong arguments more often than wrong tools. Keep destructive siblings independently understandable rather than using their descriptions to explain how they differ from each other.

**No confirmation arguments.** Tool annotations describe effects and may inform a host's approval decision, but they do not grant authority or enforce security. Enforce authorization at the server-side product boundary. Once the host has approved execution, a tool-level confirmation flag adds a retry without adding authority. Every tool is safe in an unattended scheduled run, and nothing requires a person mid-call.

**Annotations stay truthful against the worst supported effect.** An additive-only annotation is false for a tool that can refresh or replace existing state, even when replacement is uncommon. Where possible, derive annotation checks from the tool's declared result variants instead of restating the annotation in a nearby test.

**A write that can change identity returns the resulting identity.** Thread that identity from the same derivation that stored it, and verify it against durable state. A caller holding the previous name or handle otherwise misses its next name-addressed call.

**Reads may resolve names, while destructive operations take stable IDs.** Names collide and move. Enforce the distinction at the product gate and backend transaction, with a tool-side check as defense in depth. An ambiguous read returns each candidate with its stable ID.

**Batch bounds follow the surface's real budget.** A list-taking adapter may loop a single-item product operation so each item retains its own authorization, quota decision, and failure. Return one variant-typed result per item in input order, with failures inline. Set each surface's maximum from its context, payload, latency, and execution limits. Share a maximum with the product UI only when those constraints genuinely match. A local client may use a different bound when it issues separately rate-limited requests. Reads stay singular even beside batch writes, because a read returns content the model is about to use, and batching reads floods its context.

**HTTP acceptance is not durable landing.** Interpret success according to the endpoint contract. A synchronous success may report a landed mutation, while `202 Accepted` or a created background job proves only admission. Parse the success body instead of casting it, and verify job completion or durable state before reporting an asynchronous operation as landed. If a malformed success body prevents identifying the outcome, report an honest unknown outcome and name the read that disambiguates it. An authorization refusal aborts the whole call only while nothing has landed, through the path that carries the re-auth challenge. After any landing it reports inline, because work that happened must be reported.

**Teach on the error path.** Put discovery and correction into typed refusals that name what was measured and the next move. Error copy quotes the relevant measurement without echoing the whole rejected value.

**Optimize the text the host actually indexes.** When deferred tool search matches the opening sentence, make that sentence a compact retrieval document carrying the verbs callers reach for. Inspect context delivery for each supported host rather than assuming every host indexes the same field. Use imperative verb then noun and follow the server's own plurality convention.

**Keep derived keys printable.** Compose internal delimiters from characters a closed enum cannot contain. A raw control byte can make source and diffs render as binary, hiding a security-bearing handler from review.
