**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and backend code, then write the policy with concrete end-of-period rules, enforcement details, and explicit assumptions. I’m using the web-repository-opinions skill for this repository work.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; rg --files -g AGENTS.md -g '*billing*' -g '*subscription*' -g '*plan*' -g '*quota*' -g '*schema*' -g 'package.json'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18311 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/references/billing.md; Get-Content .agents/skills/web-repository-opinions/references/quota.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/data-deletion.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; rg --files -g '"'!node_modules'"' -g '"'!.git'"'"`

> Output: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 9886 more characters]

**Assistant:** The repository contains only the brief and workspace metadata; there’s no backend implementation to verify. I’ll make the document an enforcement specification and label the decisions the brief leaves open. The policy will retain existing data, use a stable order to determine book access, and gate storage growth and oversized photos separately.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/uploads.md; Get-Content .agents/skills/web-repository-opinions/references/user-facing-errors.md; Get-Content package.json; Get-Content AGENTS.md; git status --short'`

> Output: # Auth  Use a managed auth provider so identity, sessions, and social sign-in are never hand-rolled. Clerk is the default. You never store or handle raw passwords or emails yourself. The provider owns credential security.  Hold three postures throughout. Least privilege grants each caller the minimum scope it needs. Defense in depth re-verifies on the server even when the UI already hides an u [... 21825 more characters]

**File change:** `[{"path": "<run>\\builds\\2-downgrade-overage-old-sol\\work\\docs\\downgrade-policy.md", "kind": "add"}]`

**Assistant:** The draft checks the typical case: 25 of 40 books remain covered, all fifteen oversized photos become unavailable, and clearing the 300 MB in Trash still leaves storage 800 MB over Free’s limit. It also specifies upload, download, and queued-job checks at expiry, while preserving fulfillment of prints already paid for and accepted.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; Get-Content docs/downgrade-policy.md | Select-Object -First 12'`

> Output: ?? docs/downgrade-policy.md # Pro cancellation and downgrade policy  `docs/brief.md` is the source of truth for owner decisions. This document specifies the remaining policy choices made while the owner is away; those choices are assumptions listed below. It is a backend implementation contract, not a claim that enforcement already exists: this repository currently has no application backend.  [... 877 more characters]

**Assistant:** Created [docs/downgrade-policy.md](docs/downgrade-policy.md) with exact access rules, backend enforcement requirements, explicit assumptions, and a worked check against the typical cancellation.

Key choices: retain data, cover the oldest 25 books, gate oversized photos, and block storage growth while allowing cleanup.

No backend exists yet, so enforcement is specified rather than verified.
