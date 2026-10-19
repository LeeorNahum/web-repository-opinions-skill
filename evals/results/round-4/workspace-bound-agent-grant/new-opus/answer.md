I wrote the design to `docs/agent-access.md`. It's a design only: no code was written, nothing was tested against a real provider, and nothing is committed.

**What I decided:**
- **One connection reaches one firm.** When the consultant signs in to connect their agent, they pick one firm workspace. A consultant working for three firms makes three separate connections, and each firm's Admin approves its own. A single connection covering all of a consultant's firms would break the contract rule that one firm's connection can never reach another firm's data.
- **Same server address for every firm.** All connections use `https://mcp.<domain>/mcp`. The firm is fixed when the connection is authorized. It isn't part of the URL, it isn't a tool argument, and it doesn't follow whatever firm the consultant is viewing in the web app.
- **Admin approval.** A new connection starts as pending and every call is refused until a firm Admin approves it. The Admin can also approve it as read-only. Admins can deny or revoke a connection, consultants can revoke their own, and leaving the firm revokes it automatically. Each takes effect on the next call, because permissions are checked live on every call.
- **Permissions.** There are two: `workpapers:read` (list and read workpapers) and `workpapers:annotate`. A call goes through only if the consultant is still a member, their role allows the action, their consent and the Admin's approval both include it, and the connection is approved.
- **Firm separation in the tools.** All three existing tools only see the connection's firm. Asking for a workpaper id from another firm returns the same "not found" as an id that doesn't exist, so it doesn't reveal that the workpaper exists. Annotations record which connection made them.
- **Audit.** There's an append-only, per-firm log of approval events, plus one entry per tool call. Firm Admins can view and export both.

**One possible blocker:** this only works if the auth provider's access tokens record which firm the consultant chose and which authorization they belong to, and the server can verify both. Matching on the user and agent app alone isn't enough: one agent app connected to two firms would merge into a single connection. Someone needs to check this against a real token before building. If the provider can't do it, the doc says not to work around it by choosing the firm on the first call or from a tool argument, since both break the contract.

**Assumptions for you to confirm** (all listed at the end of the doc):
1. Admin, Preparer and Reviewer are roles the app manages itself, with the auth provider keeping only its own admin and member roles.
2. All three roles can read and annotate, and only Admins approve connections.
3. A consultant who is also an Admin of that firm can approve their own connection, and the log marks it as self-approved.
4. Approvals don't expire.
5. Agent access is allowed on every firm plan, and usage counts against the plan of the firm the connection belongs to.
6. I added the per-call access log; the brief only requires auditing approvals.
7. Annotating gets its own permission rather than a confirmation step.
8. Tokens are issued straight away and refused until an Admin approves, rather than making the sign-in wait.