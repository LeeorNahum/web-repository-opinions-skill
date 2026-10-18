I wrote the design to `docs/agent-access.md`. One thing has to be checked before anyone builds it: keeping firms apart depends on our auth provider issuing an access token whose firm is fixed when the consultant connects. I haven't confirmed that the provider does this. The doc says to decode a real token first. If the firm isn't in the token, the server refuses every call rather than guessing, and the decision comes back to you.

**How it works:**
- **Each connection is tied to one firm.** There is one MCP endpoint, `mcp.<domain>/mcp`. The consultant picks a firm when they connect, and the server only ever reads the firm from the verified token. No tool takes a firm as an input, so a call can't reach into another firm.
- **An Admin approves each connection.** Connecting creates a pending approval record in that firm's workspace, and the firm's Admins are notified. Every tool call is refused with a clear "waiting for approval" message until an Admin approves. The Admin can approve all of what was asked or only part of it, deny it, or revoke it later. Changes apply on the next call.
- **Every call is checked again.** One gate checks the token, the firm, the consultant's current membership and role, and the approval status, then confirms the role, the approval and the token all allow the action. Queries are also filtered to that firm. A workpaper from another firm looks exactly like one that doesn't exist.
- **Firms can audit everything.** There is an append-only log of requests, approvals, denials and revocations. It also records each tool call (reads included) without copying workpaper content. Admins can export it. Notes written by an agent are labelled "<Consultant> via <agent>".

**What I assumed** (each is listed in the doc and easy to change):
1. Admin, Preparer and Reviewer can all both read and annotate through an agent.
2. "Each connection" means one consultant, using one agent, in one firm. Reconnecting the same agent needs no new approval. A new agent, or a request for more access, does.
3. An Admin may approve their own connection. It is marked as self-approval in the log.
4. Approvals don't expire. They last until revoked or until the consultant leaves the firm.
5. Agent access isn't tied to a paid plan.
6. In agent apps that allow only one connection per server address, a consultant works with one firm at a time and reconnects to switch.

Still open for you, besides the token check: whether self-approval should need a second Admin, whether approvals should be renewed periodically, and how long audit logs are kept. I haven't committed the file.