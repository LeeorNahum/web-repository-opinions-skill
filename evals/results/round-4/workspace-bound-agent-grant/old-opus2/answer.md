I've written the design to `docs/agent-access.md`. I haven't committed it, and nothing is built yet. The whole design depends on one thing I couldn't check: the auth provider must record which firm was chosen during sign-in inside the agent's access token. Someone needs to decode a real token and confirm that before building.

**How it works:**
- **One connection, one firm.** A connection is one consultant's agent, authorized into exactly one firm's workspace. The consultant picks the firm on the provider's consent screen. A consultant who works for three firms makes three connections, and each firm approves its own.
- **Admin approval.** A new connection is "pending" and can't read anything. The firm's Admins get an in-app notice and an email, and approve, approve as read-only, or deny on a settings page (`/w/[workspaceId]/settings/agent-connections`). Until then, the agent gets a plain message saying an Admin of that firm needs to approve it. Admins can revoke at any time. Connections are revoked automatically if the consultant leaves the firm, closes their account, or the workspace is deleted.
- **Keeping firms apart.** Every tool call is checked in one place. The firm comes only from the verified token, never from tool arguments. The check requires an approved connection and current membership. Every query runs inside that firm's data:
  - A workpaper ID from another firm returns the same "not found" as an ID that doesn't exist.
  - Paging positions from one firm's list don't work in another firm.
- **Audit.** Each firm gets an append-only log of connection requests, approvals, denials and revocations, plus a record of each tool call. Admins can export it. Note text and workpaper content are left out.
- **Tools.** All three existing tools stay the same for every caller, whatever the approval state. Results gain a `workspace: { id, name }` field so an agent can tell which firm a result came from.

**What I assumed (full list in the doc):**
- A new agent, a new firm, or reconnecting after a denial needs fresh approval. Token refreshes don't.
- Admins can narrow a request to read-only but can't grant more than was asked for.
- All three roles (Admin, Preparer, Reviewer) can read and annotate through an agent.
- A consultant who is also a firm's Admin can approve their own connection, and the log marks it as self-approved.
- Approvals don't expire on their own.
- Agent access is available on every plan.

**Questions for you:**
- If the provider can't tie a token to the chosen firm, the fallback is a weaker firm-selection step we'd build ourselves. I'd want your decision before taking that route.
- Some agent apps only allow one connection per server address. Consultants using those would switch firms by re-authorizing rather than staying connected to all of them. Is that acceptable?
- Should firms be able to require periodic re-approval, for example once per audit cycle?
- Should firms be able to block Admins from approving their own connections?