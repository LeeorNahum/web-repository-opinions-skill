**Prompt:** Design the MCP tool catalog for agents that build and maintain Fernpage sites, using docs/brief.md: tool names, argument schemas, and what each tool does, including how agents work with saved data. Write it to docs/mcp-tools.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and repository guidance, then write the MCP catalog with argument schemas, saved-data workflows, and explicit assumptions. I’m using the web-repository-opinions skill for this design work.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; rg --files -g AGENTS.md -g '*mcp*' -g '*schema*' -g 'package.json' -g 'README*'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18908 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/model-context-protocol.md; Get-Content .agents/skills/web-repository-opinions/references/agent-tool-design.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/data-deletion.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/bulk-actions.md; Get-ChildItem docs; Get-Content package.json; git status --short'`

> Output: # Model Context Protocol  Give a remote MCP server one product-owned endpoint:  - Remote MCP: `https://mcp.<domain>/mcp`  Deploy MCP as its own protocol app when it needs independent compatibility, scaling, rate limiting, or release control. Use the official MCP SDK for protocol behavior, served through its web-standard transport on Hono. Verify tokens directly with the auth provider's backe [... 36012 more characters]

**Assistant:** The brief leaves the interface details open, so I’m designing around explicit file operations and individual saved-data entries. Each edit or deletion will require a revision from a prior read, so concurrent visitor changes produce a conflict. I’ll also spell out publishing, visitor permissions, and Trash behavior, and mark those design choices as assumptions.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/naming.md; Get-Content .agents/skills/web-repository-opinions/references/workspace-tenancy.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/live-data.md'`

> Output: # Naming  Name by paradigm, not by provider. A thing is named for what it does so the name survives a tool swap.  | Identifier                                      | Convention      | Example                          | | ----------------------------------------------- | --------------- | -------------------------------- | | Repo and canonical folder                       | Title-Dash-Case |  [... 21739 more characters]

**File change:** `[{"path": "<run>\\builds\\2-file-catalog-with-saved-data-old-sol\\work\\docs\\mcp-tools.md", "kind": "add"}]`

**Assistant:** The draft now covers the tool schemas and saved-data workflows, including conflict handling and test-entry cleanup. File writes leave saved data intact, small file edits require exact matches, and whole-site deletion moves the site to Trash. I’m checking the catalog for gaps and contradictions against the brief.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "git diff --check; git status --short; Get-Content docs/mcp-tools.md | Measure-Object -Line -Word; rg -n 'fernpage_|Assumptions|expectedRevision|Trash' docs/mcp-tools.md"`

> Output: ?? docs/mcp-tools.md  3:`docs/brief.md` is the product source of truth and wins over this design. This document proposes the first catalog; it does not describe an implemented server. Assumptions beyond the brief are recorded below. 11:Read tools have `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`. Create tools have `readOnlyHint: false`, `destructiveHint: false`, `idempot [... 7571 more characters]

**File change:** `[{"path": "<run>\\builds\\2-file-catalog-with-saved-data-old-sol\\work\\docs\\mcp-tools.md", "kind": "update"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --no-index --check -- NUL docs/mcp-tools.md'`

> Output: warning: in the working copy of 'docs/mcp-tools.md', LF will be replaced by CRLF the next time Git touches it 

**Assistant:** Created [docs/mcp-tools.md](docs/mcp-tools.md) with tool names, argument schemas, behavior, saved-data workflows, concurrency safeguards, and explicit assumptions.

It preserves HTML-derived metadata, single-file publishing, and 30-day site Trash with browser-only restoration. Whitespace checks found no errors.
