# Alderdocs

Alderdocs is a document editor for freelancers and small studios. A person usually belongs to several workspaces: their own, plus one per client or studio they work with.

## Decided

- Auth: managed provider, one provider organization per workspace, including the workspace created at sign-up. Roles: Owner, Editor, Viewer.
- Every document belongs to exactly one workspace.
- A document can also be shared with one person by email. That person sees that document only, not the rest of its workspace.
- Plans are priced by storage per paying owner. Each workspace has a member cap of 25 as an abuse limit, the same on every plan.

## What people have told us

- In the beta we had an active-workspace switcher in the header. People kept creating documents in the wrong workspace, and studio leads said they lose track of what changed across clients.
- Studio leads want to connect their AI agent to Alderdocs over MCP and have it work across their client workspaces. Having to reconnect per client was the most common complaint about a competitor.

## MCP tools that exist today

- `list_documents { query?, cursor? }`
- `read_document { id }`
- `update_document { id, content }`

We need a create tool and the authorization model behind all of them, and the library page needs its workspace handling settled.
