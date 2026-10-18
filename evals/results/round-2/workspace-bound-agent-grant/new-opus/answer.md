I've written the design to `docs/agent-access.md`. It isn't committed. One thing needs checking before anyone builds on it: whether our auth provider can tie an access token to the single firm the consultant picks (open question 1 below).

**Main decisions:**
- **One connection reaches one firm.** All agents use a single server address, `https://mcp.<domain>/mcp`. When a consultant connects, they pick one firm, and that connection can never act in another firm's workspace. To work with a second firm, they connect again, and that firm's Admin approves it separately. I ruled out a single connection covering all of a consultant's firms, because the firm contracts forbid it.
- **Admin approval is a record we own.** Connecting finishes straight away and creates a pending connection. The firm's Admins get an email and a request in workspace settings. Until one of them approves, the agent's calls are refused with a clear "waiting for approval" message. An Admin can approve, narrow the connection to read-only, deny it or revoke it later.
- **Every call is rechecked.** The server confirms the connection is approved, that the consultant is still a member of that firm, and that their role, the Admin's approval and the token's permissions all allow the action. The firm comes from the connection, never from what the agent sends. A workpaper ID from another firm gets the same "not found" as one that doesn't exist. Removing a consultant from a firm cuts off their connection on the next call.
- **Audit log.** There's a permanent, per-firm log of every request, approval, denial, expiry, revocation and permission change. I also added a log of what each connection accessed, though the brief only asks for approvals to be audited.

**Assumptions** (listed in the doc, each easy to reverse):
- Admin, Preparer and Reviewer are enforced by the product. In the auth provider, Admins are admins and everyone else is a plain member.
- All three roles can read and annotate; the Admin's approval is what narrows a connection.
- Refreshing a token doesn't need re-approval, but every new connection does.
- Pending requests expire after 7 days. Approvals don't expire.
- Any one Admin can approve. A consultant who is also an Admin can approve their own connection, and the log flags it.
- Agent access is on every plan.

**Open questions for you:**
1. **The provider check.** Before building, someone needs to inspect a real token and see what it carries. If the provider can't tie a token to one firm, the guarantee would rest on our own records rather than on the provider. In that case we'd need to decide between building our own token layer and changing providers. I stopped short of designing that layer.
2. Should firms be able to turn agent connections off entirely, or limit which agent apps are allowed?
3. Do firm contracts allow Admins to approve their own connections?
4. Some agent apps keep only one login per server address, so a consultant on one of them would have to reconnect each time they switch firms. That's the cost of keeping firms separate, and we should test the apps consultants actually use.