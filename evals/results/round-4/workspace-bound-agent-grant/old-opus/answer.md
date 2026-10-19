I've written the design to `docs/agent-access.md`. Nothing is committed yet, and none of it is built or tested; the document is the design only.

**How it works:**
- **One MCP server, one firm per connection.** All agents use a single server address. When a consultant signs in, they pick one firm, and the token they get is tied to that firm. A consultant in three firms makes three separate connections.
- **The firm comes only from the token.** No tool takes a firm as an argument. Every lookup is filtered to the token's firm. Asking for a workpaper that belongs to another firm returns the same "not found" as one that doesn't exist, so it doesn't even confirm the workpaper is there. This is what keeps one firm's data out of another firm's connection.
- **An Admin approves each connection.** A connection's first call creates a pending request and is refused with a clear "waiting for a firm Admin" message. The firm's Admins are notified, then approve it (read-only, or read plus annotate) or deny it. Any Admin can revoke it later, and so can the consultant.
- **Every call is rechecked.** Each call confirms the consultant is still a member of the firm, still has their role, the connection is still approved, and the token allows the action. A revocation or removal from the firm takes effect on the next call, not when the token expires.
- **Approvals are auditable.** Requests, approvals, denials and revocations go into a log that is never edited, and each firm's Admins can export their own firm's entries. Annotations are recorded as made by the consultant through that connection.

**Assumptions I made, which you can change:**
1. **The provider can tie a token to one firm.** This is the one the whole design depends on. Before building, someone needs to look inside a real token and confirm the firm is in it. If it isn't, I recommend not shipping agent access rather than letting the agent say which firm it means. Agent apps often reuse one registration across connections, so nothing else would reliably tell the firms apart.
2. The managed auth provider is Clerk, the repo's default.
3. Admins, Preparers and Reviewers can all read and annotate through an agent.
4. An Admin can approve their own connection, and the log marks it as self-approved. You may prefer to require a second Admin, which needs a rule for firms that have only one Admin.
5. Approvals don't expire; they last until revoked or until the consultant leaves the firm.
6. Agent access is not tied to a firm's plan.
7. A connection is one sign-in from one agent app, not one agent. Two agents sharing the same sign-in count as one connection.
8. Admins are notified by email and in the app.