# Harbor Ledger

Harbor Ledger keeps audit workpapers for regulated accounting firms. Each client firm is one workspace. Independent consultants often belong to several firms' workspaces at once.

## Decided

- Auth: managed provider, one provider organization per firm workspace. Roles: Admin, Preparer, Reviewer.
- Firm contracts require that data from one firm can never be reached through a connection authorized for another firm, and that a firm Admin approves each agent connection made into their workspace. Firms audit those approvals.
- A consultant's agent connects over MCP to read and annotate workpapers.
- Plans are per firm.

## MCP tools that exist today

- `list_workpapers { query?, cursor? }`
- `read_workpaper { id }`
- `annotate_workpaper { id, note }`
