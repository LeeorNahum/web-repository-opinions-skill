I wrote the design to `docs/agent-access.md`. It's not committed; I left that for you to review first.

**The design:**
- **One connection is tied to one firm, and that never changes.** An agent connection is identified by (consultant, firm workspace, agent client). The workspace is picked when the consultant authorizes the connection and comes from verified token data. It's never taken from whichever firm the consultant last had open in the app, because otherwise switching firms in a browser tab would point a running agent at another firm's data. A consultant in three firms has three connections, each approved separately.
- **One MCP endpoint for everyone:** `mcp.<domain>/mcp`, with no per-firm URL. There are two permission scopes, `workpapers:read` and `workpapers:annotate`, and the server only offers what it actually enforces.
- **Admin approval:** a new connection starts as pending. Every call is refused with a clear "waiting for an Admin of *Firm*" message until an Admin of that firm approves it. The Admin can approve with fewer permissions than requested, for example read-only. If the connection is denied or revoked, reconnecting needs a fresh approval. If the consultant leaves the firm, their connections into it are revoked.
- **Check on every call:**
  - The token is valid.
  - The connection is approved.
  - The consultant is still a member of the firm, with their current role.
  - What they can do is whatever their role, their token and the Admin's approval all allow.
  - Every query is limited to the connection's firm. A workpaper ID from another firm returns the same "not found" as an ID that doesn't exist, and list results can't be paged across firms.

  All of this runs in the same transaction as the read or write, so a revoke takes effect on the very next call.
- **Audit:** an append-only log of requests, approvals, denials and revocations, plus a log of every tool call. Admins can view and export both, and agent-written notes are traced back to the approval behind them.

**Needs checking before anyone builds it:** firm isolation works best if the auth provider's token carries the chosen firm as a verified value. I haven't confirmed that it does. Someone needs to get a real token from the provider and look at what's in it. If the firm isn't there, the doc has a fallback where the consultant picks the firm on a page in our app. That's weaker, because the token itself isn't tied to the firm and only our own records hold the link. The doc says so.

**Calls I made without you (listed in the doc so you can reverse them):**
- A connection keeps its approval when the token refreshes. A new agent client, or reconnecting after a revoke, needs a new approval.
- An Admin can approve their own agent; the log marks it as self-approved.
- Any one Admin of the firm can approve; no second sign-off.
- All three roles can read and annotate through an agent.
- Approvals don't expire on their own.
- Every tool call is logged, not just approvals.
- Agent access isn't tied to the firm's plan.

**Open questions for you:**
- Do approvals need to expire or be re-confirmed periodically?
- Should an Admin's own connection need a second Admin to approve it?
- How long must audit records be kept, and in what format?
- Should a firm be able to block agents entirely, or only allow certain ones?
- Can Reviewers annotate, or only read?
- Does our auth provider support enterprise-managed sign-in for agents yet?