**Prompt:** not recorded by this session. The case in the committed `evals.json` may have changed since.

**Assistant:** I’ll read the hosting setup and product brief, then write a concrete beta hosting and origin plan with assumptions called out. I’m using the web-repository-opinions skill for this review.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; Get-Content docs/hosting.md'`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18563 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command "Get-ChildItem -Force; rg --files -g AGENTS.md -g '*.md' docs .agents/skills/web-repository-opinions/references"`

> Output:      Directory: <run>\builds\1-user-code-on-own-domain-old-sol\work  Mode                 LastWriteTime         Length Name ----                 -------------         ------ ---- d----          10/17/2026  8:28 PM                .agents d--h-          10/17/2026  8:28 PM                .git d----          10/17/2026  8:04 PM                apps d----          10/17/2026  8:05 PM  [... 4792 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command '$refs = '"'domains','origins','auth','http-apis','dns','deployment','branches','environment','object-storage','abuse-resistance','routing','provider-setup','runtime-truth','definition-of-done'; foreach ("'$ref in $refs) { Get-Content ".agents/skills/web-repository-opinions/references/$ref.md" }'`

> Output: # Domains  Lay out hosts around one canonical origin per surface, with the primary surface on the apex.  - Primary site on the apex: `example.com`. This is the default home. A product that pitches itself on a public site and does its work in a private signed-in workspace, which is nearly every SaaS, keeps the public site alone on the apex and the signed-in product on its role subdomain. The ap [... 63026 more characters]

**Assistant:** The current layout puts user JavaScript on sibling hosts that receive the product’s shared session cookie. Different origins alone don’t protect that cookie boundary. I’m working through a freeze-compatible option that preserves the short addresses, with explicit limits on app compatibility.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command 'Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/dns.md; Get-Content .agents/skills/web-repository-opinions/references/deployment.md; Get-Content .agents/skills/web-repository-opinions/references/branches.md; Get-Content .agents/skills/web-repository-opinions/references/environment.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; rg --files apps packages; git status --short'`

> Output: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 25061 more characters]

**web_search:** `{"id": "exec-b2f7a885-5a0d-41bf-b473-063028c5490b", "type": "web_search", "query": "site.developer.mozilla.org CSP sandbox allow-scripts localStorage opaque origin cookie domain subdomains SameSite ...", "action": {"type": "search", "queries": ["site.developer.mozilla.org CSP sandbox allow-scripts localStorage opaque origin cookie domain subdomains SameSite", "site.cheatsheetseries.owasp.org Cross [... 11641 more characters]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command 'rg --files apps packages; Get-Content package.json; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content AGENTS.md; git status --short'`

> Output: {   "name": "product-web",   "private": true,   "packageManager": "pnpm@10.4.0",   "scripts": {     "build": "turbo run build",     "lint": "turbo run lint",     "typecheck": "turbo run typecheck"   },   "devDependencies": {     "turbo": "^2.5.0",     "typescript": "^5.8.0"   } } # Object Storage  Large user files belong in object storage, not the database. Cloudflare R2 is the def [... 6334 more characters]

**web_search:** `{"id": "exec-b368bc9c-0fa4-435b-853b-4d28317f571f", "type": "web_search", "query": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/sandbox", "action": {"type": "open_page", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/sandbox"}, "results": [{"type": "text_result", "domain": "developer.mozilla.org",  [... 1111 more characters]`

**Assistant:** The freeze-compatible option is a restricted beta: keep the short addresses and run scripts in an opaque-origin sandbox. That disables native `localStorage`, so I’ll make that limitation explicit and defer apps that need it. The plan will also define private-app authorization and release checks; the current serving behavior should remain blocked until those checks pass.

**File change:** `[{"path": "<run>\\builds\\1-user-code-on-own-domain-old-sol\\work\\docs\\hosting-plan.md", "kind": "add"}]`

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command 'git diff --check; git status --short; Get-Content docs/hosting-plan.md -TotalCount 18; (Get-Content docs/hosting-plan.md | Measure-Object -Line -Word)'`

> Output: ?? docs/hosting-plan.md # Beta hosting and origin plan  Decision: ship a restricted, sandboxed app beta on the existing hosts. Preserve `<name>.plinth.example`, `app.plinth.example`, and the managed provider's shared session configuration. Do not serve uploaded documents with their normal origin privileges. Apps that need native `localStorage` cannot publish in this beta. If the sandbox and auth [... 2367 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command '$plan = Get-Content docs/hosting-plan.md; $badWhitespace = $plan | Select-String -Pattern '"'\\s+"'$'"'; if ("'$badWhitespace) { $badWhitespace; exit 1 }; $links = [regex]::Matches(($plan -join "`n"), '"'\\]\\((["'^)]+)'"\\)'); foreach ("'$link in $links) { $target = $link.Groups[1].Value; if ($target -notmatch '"'"'^https://'"' -and -not (Test-Path -LiteralPath (Join-Path docs "'$target))) { Write-Error "Missing relative link: $target"; exit 1 } }; Write-Output '"'Plan whitespace and relative links checked.'"`

> Output: Plan whitespace and relative links checked. 

**Assistant:** Wrote [docs/hosting-plan.md](docs/hosting-plan.md).

Recommends a restricted sandboxed beta that preserves short URLs during the freeze. Native `localStorage` apps must wait because restoring it would reopen the shared-cookie risk.

Includes private-access rules, release gates, post-freeze options and assumptions. Checked whitespace and local links. No infrastructure changed.
