# Agent Tool Design

Apply these rules to any tool surface an agent calls, including MCP tools, function-calling schemas, and CLI subcommands an agent drives. Design against agent failure modes rather than assuming a person will repair ambiguous inputs mid-call.

**Required fields decide destructive scope.** An omitted argument keeps what gets deleted at its narrowest and creates no new resource. When one optional field would decide between editing and creating, or between one file and a whole resource, keep separate tools whose names carry the distinction.

**Prefer an extra tool over a conditional schema.** Agents pick wrong arguments more often than wrong tools. Each tool's description says what it does and what it changes, and names no other tool, so every destructive sibling is understandable on its own.

**Host approval is the only confirmation.** Tool annotations describe effects and may inform a host's approval decision, but they do not grant authority or enforce security. Once the host has approved execution, a tool-level confirmation flag adds a retry without adding authority. Every tool completes without a person approving it mid-call, so it is safe in an unattended scheduled run. A tool that needs outside input, such as a sign-in, asks for it through the protocol's input request, which the host can satisfy or fail.

**Annotations stay truthful against the worst supported effect.** Mark a tool that can refresh or replace existing state as destructive (in MCP, `destructiveHint: true`), even when replacement is uncommon. Where possible, derive annotation checks from the tool's declared result variants instead of restating the annotation in a nearby test.

**A write that can change identity returns the resulting identity.** Thread that identity from the same derivation that stored it, and verify it against durable state. A caller holding the previous name or handle otherwise misses its next name-addressed call.

**Reads may resolve names, while destructive operations take stable IDs.** Names collide and move. Enforce the distinction at the product gate and backend transaction, with a tool-side check as defense in depth. An ambiguous read returns each candidate with its stable ID.

**Batch bounds follow the surface's real budget.** A list-taking adapter may loop a single-item product operation so each item retains its own authorization, quota decision, and failure. Set each surface's maximum from its context, payload, latency, and execution limits. Share a maximum with the product UI only when those constraints genuinely match. A local client may use a different bound when it issues separately rate-limited requests. Reads stay singular even beside batch writes, because a read returns content the model is about to use, and batching reads floods its context.

**Report landing only when the endpoint contract proves it.** A synchronous success may report a landed mutation, while `202 Accepted` or a created background job proves only admission. Parse the success body instead of casting it, and verify job completion or durable state before reporting an asynchronous operation as landed. If a malformed success body prevents identifying the outcome, report an honest unknown outcome and name the read that disambiguates it. An authorization refusal aborts the whole call only while nothing has landed, through the path that carries the re-auth challenge. After any landing it reports inline, because work that happened must be reported.

**Teach on the error path.** Put discovery and correction into typed refusals that name what was measured and the next move. A validation refusal names the field, its limit, and what was received, and says what to send instead, without echoing the whole rejected value.

**Optimize the text the host actually indexes.** Measure what each supported host places in model context. Some inject a connected interface eagerly, while others defer tools behind search or another retrieval layer. When deferred tool search matches the opening sentence, make that sentence a compact retrieval document carrying the verbs callers reach for. Use imperative verb then noun and follow the server's own plurality convention. Favor an on-demand client, such as a command-line client over the product API, only when it proves cheaper and the value of a persistent surface does not justify its cost.
