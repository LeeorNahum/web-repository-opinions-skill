**Prompt:** Pro cancellations are starting to come in. Write docs/downgrade-policy.md: exactly what a cancelled user can and can't do with what they already have once the paid period ends, and how the backend enforces it. Use the typical case in docs/brief.md to check the rules. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and billing/access code, then write the policy with explicit assumptions and check it against the typical case. I’m using the web-repository-opinions skill for this repository work.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; rg --files -g AGENTS.md -g '*billing*' -g '*subscription*' -g '*plan*' -g '*entitle*' -g 'package.json' -g '*downgrade*'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18561 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/references/billing.md; Get-Content .agents/skills/web-repository-opinions/references/quota.md; Get-Content .agents/skills/web-repository-opinions/references/data-deletion.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; rg --files -g '"'!.agents/**'"'; git status --short"`

> Output: # Billing  Use a managed billing provider for subscriptions and payments. Stripe is the default. The billing provider owns subscription and payment truth. The app reads it rather than mirroring it as the authority.  Plan names and quota constants live in code, not env. They are product decisions that should be reviewed in code and reflected in stored metadata, not silently changed by a dashboa [... 23176 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/uploads.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/bulk-actions.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content package.json; Get-Content AGENTS.md'`

> Output: # Uploads  Do not proxy large files through an app server route. Upload bytes directly from the browser to object storage.  Flow:  ```text Browser asks the server for permission. Server validates auth, quota, and metadata. Server signs upload URLs. Browser uploads bytes directly to object storage. Browser asks the server to finalize. Server updates database state. ```  Use a single  [... 12487 more characters]

**Assistant:** The repository has a product brief but no backend implementation, so the document will specify the required enforcement. I’ll use the oldest 25 active books as the Free allowance, preserve all retained data, keep existing oversized photos usable in covered books, and block storage growth while over quota. I’ll label these choices as assumptions and spell out how Trash, restoration, and print orders behave.

**File change:** `[{"path": "<run>\\builds\\2-downgrade-overage-new-sol\\work\\docs\\downgrade-policy.md", "kind": "add"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "rg -n 'restor|displace|Assum|typical' docs/downgrade-policy.md; git diff --check; git status --short"`

> Output: 34:Listing unavailable books exposes management metadata only, without page content, photo thumbnails, or download links. An old content URL is not an exception to the coverage gate. Cleanup operations remain available regardless of coverage or storage overage. Permanent deletion is irreversible; moving to Trash is recoverable for 14 days from the deletion instant. At expiry the book cannot be res [... 4083 more characters]

**File change:** `[{"path": "<run>\\builds\\2-downgrade-overage-new-sol\\work\\docs\\downgrade-policy.md", "kind": "update"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --no-index --check -- NUL docs/downgrade-policy.md'`

> Output: warning: in the working copy of 'docs/downgrade-policy.md', LF will be replaced by CRLF the next time Git touches it 

**Assistant:** Created [docs/downgrade-policy.md](docs/downgrade-policy.md) with exact access rules, backend enforcement requirements, and explicit assumptions.

Checked the typical case: 25 books remain usable; all data stays retained; purging 300 MB of Trash still leaves storage 800 MB over Free.

No backend exists yet, so enforcement is specified, not implemented.
