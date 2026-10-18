**Prompt:** Before the beta opens, review how we serve people's apps (docs/hosting.md) and write the hosting and origin layout we should ship to docs/hosting-plan.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll use the web-repository-opinions skill to review the hosting setup and product brief, then write a concrete plan with assumptions and any launch blockers called out.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; Get-Content docs/hosting.md'`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18813 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-ChildItem -Force; rg --files -g AGENTS.md -g '*.md' -g '*lock*' -g 'package.json'"`

> Output:      Directory: <run>\builds\2-user-code-on-own-domain-new-sol\work  Mode                 LastWriteTime         Length Name ----                 -------------         ------ ---- d----          10/18/2026  1:13 AM                .agents d--h-          10/18/2026  1:13 AM                .git d----          10/17/2026  8:04 PM                apps d----          10/17/2026  8:05 PM  [... 332 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command '$refs = @('"'domains','origins','auth','deployment','dns','environment','http-apis','object-storage','abuse-resistance','provider-setup','runtime-truth','definition-of-done','routing','social-metadata','branches'); foreach ("'$ref in $refs) { Write-Output "REFERENCE: $ref"; Get-Content ".agents/skills/web-repository-opinions/references/$ref.md" }'`

> Output: REFERENCE: domains # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its ro [... 72707 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/deployment.md; Get-Content .agents/skills/web-repository-opinions/references/dns.md; Get-Content .agents/skills/web-repository-opinions/references/provider-setup.md'`

> Output: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 16036 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/environment.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md; Get-Content .agents/skills/web-repository-opinions/references/runtime-truth.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md'`

> Output: # Environment  Env setup should be boring, explicit, and hard to drift. An env example is a contract, not a secret store and not a deployment database. Each runtime owns its own contract. Deployed environments supply values through their host or provider.  Env is for secrets and true environment variance, not a general settings file. This is the twelve-factor posture: configuration that varies [... 27234 more characters]

**Assistant:** The current setup runs user code on sibling hosts of a session shared across `plinth.example`. That puts the authentication boundary at risk. The freeze prevents adding a separate content domain, so I’m checking the sandbox fallback and its effect on apps that use `localStorage`.

**web_search:** `{"id": "exec-1638f869-6168-4a92-b385-19110e7c9278", "type": "web_search", "query": "site.html.spec.whatwg.org sandbox origin flag cookies localStorage Content-Security-Policy sandbox ...", "action": {"type": "search", "queries": ["site.html.spec.whatwg.org sandbox origin flag cookies localStorage Content-Security-Policy sandbox", "site.developer.mozilla.org Content-Security-Policy sandbox allow-sa [... 16787 more characters]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/environment.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/definition-of-done.md; git status --short; rg --files apps packages'`

> Output: # Environment  Env setup should be boring, explicit, and hard to drift. An env example is a contract, not a secret store and not a deployment database. Each runtime owns its own contract. Deployed environments supply values through their host or provider.  Env is for secrets and true environment variance, not a general settings file. This is the twelve-factor posture: configuration that varies [... 16064 more characters]

**web_search:** `{"id": "exec-7a3c798f-7b92-4494-bfb4-280ed83a9811", "type": "web_search", "query": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/sandbox", "action": {"type": "open_page", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/sandbox"}, "results": [{"type": "text_result", "domain": "developer.mozilla.org",  [... 1223 more characters]`

**web_search:** `{"id": "exec-3851363b-e0ae-475c-895d-48dce5914a74", "type": "web_search", "query": "https://w3c.github.io/webappsec-csp/#directive-sandbox", "action": {"type": "open_page", "url": "https://w3c.github.io/webappsec-csp/#directive-sandbox"}, "results": [{"type": "text_result", "domain": "w3c.github.io", "ref_id": "turn2view0", "snippet": "Total lines: 3802", "title": "Content Security Policy Level 3" [... 288 more characters]`

**Assistant:** An opaque sandbox blocks cookie access, but it also blocks `localStorage`. I’m writing the plan with a no-go for the advertised beta under the current freeze, a safe containment option, and a separate-domain layout that preserves the short addresses. The plan will make the storage limitation explicit.

**File change:** `[{"path": "<run>\\builds\\2-user-code-on-own-domain-new-sol\\work\\docs\\hosting-plan.md", "kind": "add"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; Get-Content docs/hosting-plan.md'`

> Output: ?? docs/hosting-plan.md # Hosting and origin plan  Decision date: 2026-10-18. This is a proposed shipping contract, not a record of deployed changes. [brief.md](brief.md) remains the source of truth for owner decisions; [hosting.md](hosting.md) describes the current implementation.  ## Decision  Keep `<name>.plinth.example` as each app's short, visible address and `app.plinth.example` as the [... 16617 more characters]

**Assistant:** Created [docs/hosting-plan.md](docs/hosting-plan.md) with the origin layout, private-app access flow, assumptions, and release gates.

Recommendation: preserve short addresses, isolate user code on a separate registrable domain, and delay the advertised beta under the freeze. The sandbox fallback blocks `localStorage`.

Only the plan document changed; no infrastructure changes were made.
