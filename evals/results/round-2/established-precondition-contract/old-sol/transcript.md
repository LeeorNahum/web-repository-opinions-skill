**Prompt:** Partners keep asking to change single rows (see docs/brief.md). Design the API addition and write it to docs/row-updates.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and existing API conventions, then write the row-update design with assumptions and open decisions noted. I’m using the web-repository-opinions skill for this API design work.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; rg --files -g AGENTS.md -g '*api*' -g '*row*' -g 'package.json' -g '*.md'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18323 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content AGENTS.md; Get-Content package.json; rg --files; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/routing.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md'`

> Output: # Product repository  This TypeScript monorepo holds the product. `docs/brief.md` is the source of truth for what the owner has decided about the product. {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "tu [... 32562 more characters]

**Assistant:** The key constraint is the published whole-document ETag contract. I’ll keep it for row updates too, so a row edit invalidates any older whole-list replacement. The design will reduce request size while retaining conflict detection, with a recovery flow for unattended syncs.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git status --short; Get-Content .agents/skills/web-repository-opinions/references/naming.md; Get-Content .agents/skills/web-repository-opinions/references/user-facing-errors.md'`

> Output: # Naming  Name by paradigm, not by provider. A thing is named for what it does so the name survives a tool swap.  | Identifier                                      | Convention      | Example                          | | ----------------------------------------------- | --------------- | -------------------------------- | | Repo and canonical folder                       | Title-Dash-Case |  [... 4793 more characters]

**File change:** `[{"path": "<run>\\builds\\2-established-precondition-contract-old-sol\\work\\docs\\row-updates.md", "kind": "add"}]`

**Assistant:** The draft keeps the existing GET/PUT contract and requires row edits to check the same document ETag atomically. It also defines retries that preserve concurrent edits. I’ve marked stable row IDs and shared revision handling as release checks because the brief doesn’t establish either.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; Get-Content docs/row-updates.md'`

> Output: ?? docs/row-updates.md # Single-row updates  Proposed API addition. [brief.md](brief.md) remains the source of truth for owner decisions; the choices and assumptions below are this design's recommendations.  ## Decision  Add `PATCH /v1/price-lists/{id}` to change fields on exactly one existing row. Require the **whole-document ETag** from `GET /v1/price-lists/{id}` in `If-Match`. Compare tha [... 11425 more characters]

**Assistant:** Created [docs/row-updates.md](docs/row-updates.md).

The design adds single-row PATCH updates using the existing whole-document ETag contract. It covers validation, atomic writes, errors, conflict recovery, and rollout checks, with assumptions explicitly noted.

Only the requested documentation file was added.
