**Prompt:** Before the beta opens, review how we serve people's apps (docs/hosting.md) and write the hosting and origin layout we should ship to docs/hosting-plan.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll review the hosting docs and product brief, then write a hosting and origin plan with decisions and assumptions. I’m using the web-repository-opinions skill for this review.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; Get-Content docs/hosting.md; rg --files -g AGENTS.md -g '*hosting*' -g 'package.json' -g '*config*'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18602 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/domains.md; Get-Content .agents/skills/web-repository-opinions/references/origins.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/deployment.md; Get-Content .agents/skills/web-repository-opinions/references/dns.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/definition-of-done.md; rg --files docs; Get-Content package.json; git status --short'`

> Output: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 38493 more characters]

**Assistant:** The current layout puts arbitrary app JavaScript on subdomains that receive the shared production session cookie. Separate subdomains isolate `localStorage`, but they don’t isolate that parent-domain cookie.

I’ll keep the short addresses as required and spell out the execution boundary they need. The plan will also address whether that boundary can ship during the infrastructure freeze.

**web_search:** `{"id": "exec-16e597f0-63dd-4a65-9b15-2a68f623a321", "type": "web_search", "query": "site.developer.mozilla.org iframe sandbox allow-same-origin localStorage opaque origin ...", "action": {"type": "search", "queries": ["site.developer.mozilla.org iframe sandbox allow-same-origin localStorage opaque origin", "site.developer.mozilla.org cookies Domain subdomains SameSite site"]}, "results": [{"type": [... 11335 more characters]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md; Get-Content .agents/skills/web-repository-opinions/references/provider-setup.md; Get-Content .agents/skills/web-repository-opinions/references/runtime-truth.md; Get-Content .agents/skills/web-repository-opinions/references/environment.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/routing.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md'`

> Output: # Abuse Resistance  A product reachable from the open internet is a target on day one. Bound what a single caller can cost the product before finding out the hard way.  ## Quota As Anti-Abuse Plumbing  Hold two different numbers, not one. A hidden internal quota, sized to the max load the product can absorb, applies to every account regardless of plan and stays invisible. A user-facing plan  [... 26871 more characters]

**web_search:** `{"id": "exec-08715b1b-e40b-40b2-a921-113dc3b0132d", "type": "web_search", "query": "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe", "action": {"type": "open_page", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe"}, "results": [{"type": "text_result", "domain": "developer.mozilla.org", "ref_id": "turn1view0", "snippet": "Total lines: [... 1145 more characters]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/provider-setup.md; Get-Content .agents/skills/web-repository-opinions/references/branches.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/continuous-integration.md'`

> Output: # Provider Setup  Provider dashboards are part of the product. A setting that can break the app is product work, not a chore buried in chat history.  Provider resources should be understandable from the dashboard alone. Fill optional descriptions, labels, and tags with the product, operational purpose, and environment or shared scope. Use canonical names from the repo, and prefer concise metad [... 18678 more characters]

**Assistant:** An opaque-origin sandbox would keep app scripts away from the shared cookie, but it also disables native `localStorage`. Restoring the app’s origin under `plinth.example` would restore access to the cookie’s domain scope.

I’m recommending that the full app-hosting beta wait for a separate content domain. The plan preserves short addresses as trusted wrappers, covers private-app access, and makes browser storage verification a release gate.

**File change:** `[{"path": "<run>\\builds\\2-user-code-on-own-domain-old-sol\\work\\docs\\hosting-plan.md", "kind": "add"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; Get-Content docs/hosting-plan.md | Measure-Object -Line -Word'`

> Output: ?? docs/hosting-plan.md  Lines Words Characters Property ----- ----- ---------- --------    69  2705              

**Assistant:** Wrote [docs/hosting-plan.md](docs/hosting-plan.md).

The plan keeps short addresses as trusted wrappers and moves app execution to a separate content domain. It recommends delaying the full beta because the freeze blocks that isolation, and documents assumptions, private-app access, storage limitations, and release checks.

Only the plan file changed; no infrastructure settings were modified.
