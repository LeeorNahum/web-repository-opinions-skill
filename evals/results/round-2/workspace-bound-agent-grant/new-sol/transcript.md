**Prompt:** Consultants on Harbor Ledger belong to several firms' workspaces. Design how their agents' MCP connections are authorized, and write it to docs/agent-access.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and repository guidance, then write the authorization design with decisions, assumptions, and open questions. I’m using the web-repository-opinions skill for this web product design work.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; rg --files -g AGENTS.md -g '*agent*' -g '*auth*' -g '*mcp*' -g 'package.json' -g '*.md'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 23103 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content AGENTS.md; Get-Content package.json; Get-Content .agents/skills/web-repository-opinions/references/workspace-tenancy.md; Get-Content .agents/skills/web-repository-opinions/references/model-context-protocol.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/agent-tool-design.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md'`

> Output: # Product repository  This TypeScript monorepo holds the product. `docs/brief.md` is the source of truth for what the owner has decided about the product. {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "tu [... 40806 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/bootstrap.md; Get-Content .agents/skills/web-repository-opinions/references/billing.md; Get-Content .agents/skills/web-repository-opinions/references/product-ux.md; Get-Content .agents/skills/web-repository-opinions/references/integration-onboarding.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/user-facing-errors.md; Get-Content .agents/skills/web-repository-opinions/references/routing.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md; git status --short'`

> Output: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 34886 more characters]

**Assistant:** The brief requires a separate, Admin-approved grant for each firm connection. I’ll bind each grant to one workspace and keep the existing tools scoped to it. Switching firms in the browser or joining another firm won’t change an agent’s access. I’ll also define how approvals are audited and how revocation affects existing credentials.

**web_search:** `{"id": "exec-a9ca3b36-dbd2-4420-9f69-cff25992f2c5", "type": "web_search", "query": "site.modelcontextprotocol.io specification authorization resource audience PKCE OAuth", "action": {"type": "search", "query": "site.modelcontextprotocol.io specification authorization resource audience PKCE OAuth"}, "results": [{"type": "text_result", "domain": "github.com", "ref_id": "turn0search0", "snippet": "Th [... 10029 more characters]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "@'
# Agent access for Harbor Ledger

Status: design decision, 2026-10-18. [brief.md](brief.md) is the source of truth for owner decisions; this document supplies implementation choices and labels assumptions separately. This change designs access; it does not configure a provider or deploy an MCP server.

## Decision and security boundary

Each MCP connection is a delegation from one consultant to one agent client for exactly one firm workspace. A current Admin of that workspace must explicitly approve that connection before credentials can access workpapers. Membership in several firms never creates an account-wide agent grant.

A grant binds an immutable tuple: "'`(provider issuer, user subject, workspace ID, OAuth client ID, connection ID, approved scopes)`. A connection ID identifies one logical agent installation/configuration, not the entire OAuth application. Multiple consultants or installations using the same client each need their own approval. The firm is part of the grant'"'s authority, not a browsing preference.

A consultant working for firms A and B connects twice, with independently approved credentials and clearly named entries such as “Harbor Ledger — Firm A” and “Harbor Ledger — Firm B.” A connection for A cannot list, read, annotate, or discover B's workpapers, even when the consultant is an Admin of B. Joining firm C later grants no agent access to C. Revoking A's connection leaves B's independent connection intact.

Use one canonical MCP endpoint and OAuth resource, proposed as "'`https://mcp.<product-domain>/mcp`. The domain is a placeholder, not a deployment change. All firms use the same resource audience. Authorization selects the firm; do not create per-firm resource identifiers or MCP paths. Do not offer a `switch_workspace` tool or an account-wide credential.

## Principals, ownership, and capabilities

The managed identity provider owns authenticated identit [... 21111 more characters]`

> Output: 

**Assistant:** The draft covers firm-specific approval, token binding, checks on every tool call, revocation, and audit evidence. I’ve labeled the assumptions, including grant lifetimes and a proposed requirement for another Admin to approve an Admin’s own connection. The brief doesn’t name a provider or target agent hosts, so the design makes their ability to preserve these boundaries a rollout prerequisite.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; $document = Get-Content -Raw docs/agent-access.md; [pscustomobject]@{Lines = ($document -split "`n").Count; HasReplacementCharacter = $document.Contains([char]0xFFFD); HasSourceOfTruth = $document.Contains('"'[brief.md](brief.md)'); HasAllExistingTools = ("'$document.Contains('"'list_workpapers { query?, cursor? }') -and "'$document.Contains('"'read_workpaper { id }') -and "'$document.Contains('"'annotate_workpaper { id, note }'))}; Get-Content docs/agent-access.md -First 16; Get-Content docs/agent-access.md -Tail 15"`

> Output: ?? docs/agent-access.md  Lines HasReplacementCharacter HasSourceOfTruth HasAllExistingTools ----- ----------------------- ---------------- -------------------   145                   False             True                True # Agent access for Harbor Ledger  Status: design decision, 2026-10-18. [brief.md](brief.md) is the source of truth for owner decisions; this document supplies implement [... 3939 more characters]

**Assistant:** Created [docs/agent-access.md](docs/agent-access.md).

The design binds each MCP connection to one firm, requires that firm’s Admin approval, and defines per-call authorization, revocation, and audit evidence. It preserves the existing tool signatures and records assumptions, provider prerequisites, and implementation acceptance checks.

Only the requested document was added.
