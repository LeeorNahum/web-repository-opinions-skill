**Prompt:** Look at the open bugs in docs/issues.md and design how page icons, tab titles, and link previews should work for public, unlisted, and private Tessel pages, including preview images. Write it to docs/metadata.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and open bugs, then write the metadata design with decisions and assumptions called out. I’m using the web repository skill for this product design work.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; Get-Content docs/issues.md; rg --files -g AGENTS.md -g '*metadata*' -g package.json"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 19141 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/social-metadata.md; Get-Content .agents/skills/web-repository-opinions/references/public-discovery.md; Get-Content .agents/skills/web-repository-opinions/references/rendering.md; Get-Content .agents/skills/web-repository-opinions/references/domains.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/seo.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/product-ux.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; rg --files docs; Get-Content package.json; git status --short'`

> Output: # Social Metadata  Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.  ## Favicon  Every surface ships a favicon. Set it deliberately rather than leaving the framewo [... 51308 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; Get-Content .agents/skills/web-repository-opinions/references/seo.md; Get-Content .agents/skills/web-repository-opinions/references/modularity.md; Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md'`

> Output: # Object Storage  Large user files belong in object storage, not the database. Cloudflare R2 is the default. Any S3-compatible store fills the role.  The database is the source of truth for metadata, ownership, status, and permissions. It stores the object key and references the bytes. Object storage holds only the bytes.  - Keep large media in object storage and store only its key and metad [... 21639 more characters]

**Assistant:** The bugs point to two boundaries: Tessel’s outer wrapper must own the browser and share metadata, and preview rendering must be unable to write data. I’ll give public and unlisted pages rich previews, keep private previews content-free, and allow page titles and icons in an authorized member’s tab. Preview images will prefer an image declared in the HTML, with automatic generation as the fallback.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/origins.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md; Get-Content .agents/skills/web-repository-opinions/references/data-deletion.md'`

> Output: # HTTP APIs  Give each public HTTP API one product-owned role subdomain and one canonical endpoint shape:  - HTTP API: `https://api.<domain>/v1` - OpenAPI document: `https://api.<domain>/openapi.json`  Deploy an API as its own protocol app when it needs independent compatibility, scaling, caching, rate limiting, or release control. Use Hono as the default HTTP framework for a TypeScript pro [... 9347 more characters]

**File change:** `[{"path": "<run>\\builds\\2-embedded-page-metadata-new-sol\\work\\docs\\metadata.md", "kind": "add"}]`

**Assistant:** The design is written in `docs/metadata.md`. It includes revision handling, revocation of old image URLs, private-tab behavior, and acceptance criteria for all four bugs. It also makes the key image tradeoff explicit: a page-specific card is always available, while screenshots remain disabled until rendering is unable to perform writes.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; Get-Item docs/metadata.md | Select-Object FullName, Length; Get-Content docs/metadata.md -Tail 16'`

> Output: ?? docs/metadata.md  FullName                                                                      Length --------                                                                      ------ <run>\builds\2-embedded-page-metadata-new-sol\work\docs\metadata.md  23167 - **247:** Publish a page that constructs its body only with JavaScript. A plain HTTP fetch must contain a full page-spe [... 3025 more characters]

**Assistant:** Created [docs/metadata.md](docs/metadata.md) covering all four bugs.

It defines icons, tab titles, and previews by visibility; image precedence and automatic generation; isolated rendering that cannot write data; cache revocation; and acceptance criteria. Assumptions are recorded explicitly.

Only `docs/metadata.md` was added.
