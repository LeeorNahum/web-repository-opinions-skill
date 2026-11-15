# Web Repository Opinions

An opinionated, modular skill for building TypeScript web products and any repo built on web technology. It encodes durable preferences so web surfaces get built faster and more consistently across projects.

The opinions are paradigm-named and provider-stated: sections are named for what they do, and the default tool inside each is a swappable pick.

## Layout

- `SKILL.md` is the spine: thesis, default stack, the reference-loading map, and core non-negotiables.
- `references/` holds one single concept per file, loaded on demand. `references/catch-up.md` is Repository Catch-Up, the pass that checks a repository against these opinions.
- `assets/` holds copyable starter files for a target repo: hosting config and the folder publish workflow.
- `scripts/check-layout.mjs` is the layout check an agent runs on its served build, and `package.json` lets it run from GitHub.
- `AGENTS.md` is the editing and maintenance contract for this skill.

## Coverage

Architecture and identity, rendering and surfaces, link previews and badges, URL state, physical commerce, HTTP APIs, MCP and agent packaging, runtime and deployment, secrets, published folders, build caches, provider onboarding, custom-domain email, auth and data ownership, external integrations, storage and jobs, search, product interaction, responsive UI and motion, billing and administration, release readiness, and catching an existing repo up.

## Use

Auto-invokes on web-technology repo work, including backend-only pieces of a web product. Read `SKILL.md` first, then read in full every reference that could touch the task, including the adjacent ones.
