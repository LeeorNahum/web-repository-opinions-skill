**Prompt:** Look at the open bugs in docs/issues.md and design how page icons, tab titles, and link previews should work for public, unlisted, and private Tessel pages, including preview images. Write it to docs/metadata.md. I'm away until tomorrow, so make the calls you can and note what you assumed.

Work only inside the current directory.

**Assistant:** I’ll read the product brief and open bugs, then write the metadata design with decisions and assumptions in `docs/metadata.md`. I’m using the web repository skill for the web product design guidance.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command "Get-Content .agents/skills/web-repository-opinions/SKILL.md; Get-Content docs/brief.md; Get-Content docs/issues.md; rg --files -g AGENTS.md -g '*metadata*' -g package.json -g '*tessel*'"`

> Output: --- name: "web-repository-opinions" description: "Use for any web work: planning, deciding, designing, scaffolding, naming, reviewing, auditing, or implementing anything in a TypeScript or web-technology repo, including a marketing site, signed-in app, SaaS, extension, desktop or mobile surface, and backend-only pieces of a web product. Holds opinionated defaults for architecture, URLs, environm [... 18891 more characters]

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/social-metadata.md; Get-Content .agents/skills/web-repository-opinions/references/seo.md; Get-Content .agents/skills/web-repository-opinions/references/public-discovery.md; Get-Content .agents/skills/web-repository-opinions/references/rendering.md; Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/background-jobs.md; Get-Content .agents/skills/web-repository-opinions/references/auth.md; Get-Content .agents/skills/web-repository-opinions/references/data-model.md; Get-Content .agents/skills/web-repository-opinions/references/source-of-truth.md; rg --files docs; Get-Content package.json; Get-Content AGENTS.md'`

> Output: # Social Metadata  Every surface declares its identity for browsers and for the link preview cards that appear when a URL is pasted into a chat app, social platform, or document tool. Both the favicon and the preview card are easy to forget and are part of finishing a surface, not optional polish.  ## Favicon  Every surface ships a favicon. Set it deliberately rather than leaving the framewo [... 39264 more characters]

**Assistant:** The bugs point to one boundary: Tessel’s wrapper must own metadata and enforce visibility before exposing it. I’ll give public and unlisted pages rich previews, keep private previews content-free, and design preview rendering so it cannot cast votes or write page data. Signed-in members can still see a private page’s title and icon in their own tabs.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'Get-Content .agents/skills/web-repository-opinions/references/object-storage.md; Get-Content .agents/skills/web-repository-opinions/references/http-apis.md; Get-Content .agents/skills/web-repository-opinions/references/product-ux.md; Get-Content .agents/skills/web-repository-opinions/references/failure-and-retries.md; Get-Content .agents/skills/web-repository-opinions/references/abuse-resistance.md; Get-Content .agents/skills/web-repository-opinions/references/uploads.md; Get-Content .agents/skills/web-repository-opinions/references/routing.md; Get-Content .agents/skills/web-repository-opinions/references/ids.md; git status --short'`

> Output: # Object Storage  Large user files belong in object storage, not the database. Cloudflare R2 is the default. Any S3-compatible store fills the role.  The database is the source of truth for metadata, ownership, status, and permissions. It stores the object key and references the bytes. Object storage holds only the bytes.  - Keep large media in object storage and store only its key and metad [... 25874 more characters]

**File change:** `[{"path": "<run>\\builds\\2-embedded-page-metadata-old-sol\\work\\docs\\metadata.md", "kind": "add"}]`

**Assistant:** The draft now defines metadata precedence, preview-image generation and fallbacks, and how old asset URLs are revoked when a page becomes private. It also records a tradeoff for issue 251: page loads cannot write runtime data; mutations need a trusted interaction gate. I’m checking the design for contradictions and confirming that only `docs/metadata.md` changed.

**Shell:** `"<home>\\AppData\\Local\\Microsoft\\WindowsApps\\pwsh.exe" -Command 'git diff --check; git status --short; Get-Content docs/metadata.md | Measure-Object -Line -Word; rg -n "''^##|233|240|247|251|Assumptions|no-store|private" docs/metadata.md'`

> Output: ?? docs/metadata.md  3:Status: proposed implementation contract. `docs/brief.md` remains the source of truth for owner decisions. This design addresses open issues 233, 240, 247, and 251; it does not mark them fixed. 5:## Decisions 13:## Visibility contract 26:Private metadata must not identify the page, author, workspace, or members. The generic description is “Open pages on Tessel.” Use the sam [... 7138 more characters]

**Assistant:** Created [docs/metadata.md](docs/metadata.md) covering all four bugs.

The design defines page icons and tab titles, rich previews for public and unlisted pages, content-free private previews, automatic preview images, and rendering that cannot write page data. It also records assumptions, visibility-change behavior, cache limits, and acceptance checks.

Only the design document changed; runtime behavior remains unchanged.
