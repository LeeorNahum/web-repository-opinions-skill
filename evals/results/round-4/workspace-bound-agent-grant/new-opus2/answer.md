I've written the design to `docs/agent-access.md`. It isn't committed yet. It's a design only: nothing is built, and none of it has been checked against a real token from our auth provider.

**The main decision:** each agent connection is bound to one firm for its whole life. A consultant who works for three firms makes three connections, and each one needs approval from that firm's Admin. I chose this because the brief says one firm's data can never be reached through a connection authorized for another firm, and because an Admin can only approve access to their own firm.

**What the doc covers:**
- **One server address for every firm:** `https://mcp.<domain>/mcp`. Connecting to another firm means authorizing again against the same address, not using a per-firm URL. No tool takes a firm argument, so an agent can't point a call at a different firm.
- **Connection states:** a connection starts unbound, then waits for approval, then is approved. Denied, revoked and ended are final, and a connection can never be moved to another firm. Until an Admin approves, calls return a plain message saying what's needed and no workpaper data.
- **Checks on every call:** the token must be valid and issued for our server, and the connection must be approved. The consultant must still be a member of the bound firm. What the agent can do is limited by three things at once: the consultant's current role, the token's permissions, and what the Admin approved. Workpaper lookups only search the bound firm. Another firm's workpaper looks exactly like one that doesn't exist, and list cursors don't work across firms.
- **Isolation tests** that prove the cross-firm guarantee.
- **The firm's audit trail:** a record of every request, approval, denial and revocation, plus a log of tool calls without workpaper content.
- **What happens when a consultant leaves a firm or closes their account,** and how the per-firm plans fit in.

**Assumptions** (the full list of 11 is at the end of the doc):
- **This one needs checking before anyone builds:** I assumed the auth provider gives each authorization a stable ID that is different for two firms authorized from the same agent. Without that ID, two connections from one agent can't be told apart. The doc gives a fallback if it doesn't exist.
- I assumed the provider's own sign-in consent can't pick a firm. So the design adds a Harbor Ledger page where the consultant picks the firm before any data flows. If the provider can pick the firm during sign-in, that page can go.
- All three roles (Admin, Preparer, Reviewer) can read and annotate.
- An Admin can approve their own connection, and the audit trail marks it as self-approved. Any one Admin can approve, and approvals don't expire.
- Agent access isn't limited by plan for now.

**Needs your answer:**
- How long tool-call logs are kept, which is probably set by firm contracts or regulation.
- Some agent apps allow only one connection per server address. Consultants using those can only work in one firm at a time and have to re-authorize to switch. I chose not to work around this with per-firm addresses.