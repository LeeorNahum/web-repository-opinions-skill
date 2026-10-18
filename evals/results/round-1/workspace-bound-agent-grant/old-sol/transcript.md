**Assistant:** I’ll read the product brief and repository guidance, then write the authorization design with explicit assumptions and open decisions.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; rg --files -g AGENTS.md -g '*agent*' -g '*auth*' -g '*mcp*' -g 'package.json'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18570 more characters]

**Assistant:** I’m using the repository’s web-repository-opinions skill. The brief makes firm isolation and Admin approval mandatory, so I’ll bind each connection to one firm and make approval specific to that connection.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command '$refs = @('"'model-context-protocol','workspace-tenancy','auth','agent-tool-design','http-apis','modularity','data-model','source-of-truth','routing','ids','origins','bootstrap','integration-onboarding'); foreach ("'$ref in $refs) { Write-Output "REFERENCE: $ref"; Get-Content ".agents/skills/web-repository-opinions/references/$ref.md" }; Get-Content AGENTS.md; Get-ChildItem docs; Get-Content package.json; git status --short'`

> Output: REFERENCE: model-context-protocol # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens dire [... 52084 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/agent-tool-design.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md'`

> Output: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 23115 more characters]

**Assistant:** The main risk is a consultant’s agent inheriting whichever firm is active in their browser. The design will freeze the firm, user, client installation, and approved permissions into a connection grant. Each call will also check current membership and revocation; refresh and workspace switching cannot broaden the grant.

**File change:** `[{"path": "<run>\\builds\\1-workspace-bound-agent-grant-old-sol\\work\\docs\\agent-access.md", "kind": "add"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "git diff --check; git status --short; Get-Item docs/agent-access.md | Select-Object Name,Length; rg -n '"'^##|Assumptions|source of truth|workspace A'"' docs/agent-access.md"`

> Output: ?? docs/agent-access.md  3:Status: proposed authorization design. [brief.md](brief.md) remains the source of truth for owner decisions; assumptions below fill gaps for review. This document specifies behavior, not an implemented or provider-verified integration. 5:## Decision 11:> A credential issued for workspace A can only exercise its approved permissions in A, even if its user also belongs to [... 432 more characters]

**Assistant:** Created [docs/agent-access.md](docs/agent-access.md).

The design binds each connection to one firm, consultant, and installation, with explicit firm Admin approval. It covers per-call authorization, refresh, revocation, audit history, and cross-firm isolation checks.

Assumptions and unresolved provider requirements are documented. All work stayed inside the current directory.
