**Prompt:** not recorded by this session. The case in the committed `evals.json` may have changed since.

**Assistant:** I’ll read the product brief and open issues, then write the metadata design with decisions and assumptions called out. I’m using the web-repository-opinions skill for the web product guidance.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; Get-Content docs/issues.md; rg --files -g AGENTS.md -g '*metadata*' -g 'package.json'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18891 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-ChildItem docs; Get-Content .agents/skills/web-repository-opinions/references/social-metadata.md; Get-Content .agents/skills/web-repository-opinions/references/public-discovery.md; Get-Content .agents/skills/web-repository-opinions/references/seo.md; Get-Content .agents/skills/web-repository-opinions/references/rendering.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/product-ux.md; Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/origins.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md; Get-Content .agents/skills/web-repository-opinions/references/routing.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md; Get-Content .agents/skills/web-repository-opinions/references/uploads.md; Get-Content .agents/skills/web-repository-opinions/references/data-deletion.md; Get-Content .agents/skills/web-repository-opinions/references/quota.md'`

> Output:      Directory: <run>\builds\1-embedded-page-metadata-old-sol\work\docs  Mode                 LastWriteTime         Length Name ----                 -------------         ------ ---- -a---          10/17/2026  8:05 PM            655 brief.md -a---          10/17/2026  8:05 PM            687 issues.md # Social Metadata  Every surface declares its identity for browsers and for the [... 68140 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/product-ux.md; Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content package.json; rg --files -g '"'!node_modules'"' -g '"'!.git'"' -g '"'!.agents/**'"'"`

> Output: # Background Jobs  Provider-backed and long-running work runs as explicit jobs with explicit state, never as fire-and-forget calls scattered through route handlers.  Design every job around its failure point, not its happy path. Ask:  - What if the external call succeeds and the database update fails? - What if the row exists but the provider object does not? - What if the user closes the  [... 33047 more characters]

**Assistant:** The bugs point to two boundaries: the wrapper must own browser metadata, and preview rendering must have no path to live writes. I’ll give public and unlisted pages rich previews, keep private previews generic, and allow private page titles and icons in the tab only after access is verified. A generated card will provide a fallback when a safe screenshot isn’t available.

**File change:** `[{"path": "<run>\\builds\\1-embedded-page-metadata-old-sol\\work\\docs\\metadata.md", "kind": "add"}]`

**Assistant:** The draft covers all four bugs, including access checks for old preview-image URLs after a page becomes private and a renderer that cannot submit votes. I’ve also documented the limit on revocation: Tessel can stop future delivery, but recipients may retain cards already fetched. I’m checking the file and diff now.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content docs/metadata.md; git diff --check; git status --short'`

> Output: # Page metadata  Design proposal, 2026-10-17. [brief.md](brief.md) remains the source of truth for owner decisions. This document makes implementation decisions for [issues #233, #240, #247, and #251](issues.md); assumptions beyond the brief are listed at the end. It specifies behavior, not an implemented feature.  ## The decision  Tessel owns the outer document and its browser metadata. The [... 20003 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -NoProfile -Command 'Get-Item docs/metadata.md | Select-Object FullName,Length; git diff --check; git status --short'`

> Output:  ?? docs/metadata.md FullName                                                                      Length --------                                                                      ------ <run>\builds\1-embedded-page-metadata-old-sol\work\docs\metadata.md  20265  

**Assistant:** Created [docs/metadata.md](docs/metadata.md) covering all four bugs.

The design includes visibility-specific icons, titles and previews; automatic preview images; rendering without live writes; private-data protection; and revocation behavior. Assumptions and implementation acceptance checks are documented.

Only `docs/metadata.md` changed.
