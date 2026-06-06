# AGENTS.md

Rules for editing the **web-repository-opinions** skill. User-facing opinions live in `SKILL.md` and `references/`. `README.md` is the human skim layer.

## File roles

| File | Role |
| --- | --- |
| `SKILL.md` | Trigger, default stack, reference-loading map, non-negotiables, audit |
| `references/*.md` | One single concept per file, named by paradigm |
| `assets/` | Copyable starter files that become files in a target repo |
| `README.md` | Short human summary |

One owner per opinion. Each reference owns its concept; other files use the term or shape without restating the rule. The reference-loading map lives in `SKILL.md` once; references assume the agent already loaded what their section needs.

## Editing

- Bump `metadata.version` with semver in the same change whenever behavior changes.
- Encode a default only when backed by user preference or real usage.
- Prefer deletion over caveats. More words is not better.
- One opinion per reference. When a new paradigm, way of thinking, service, or workflow is added, give it its own reference file and add it to the `SKILL.md` reference-loading map. Do not bolt a second unrelated concept onto an existing reference.
- When an existing concept grows, refactor its reference rather than scattering the idea across several files.
- **Opinionated and explicit.** State the preference clearly. This skill takes positions.
- **Paradigm-named, provider-stated.** File and section names describe the job, never the vendor. Inside a section, name the default tool as a swappable pick.
- **No sibling-skill pointers.** Do not reference other skills by name. Where another skill's domain touches a topic, state the web opinion inline and stop.
- **No project leakage.** Use placeholder repo, product, and domain names. Do not embed a real product's name, palette, routes, or credentials.
- **No em dashes.** Use commas, periods, parentheses, or "to".
- **Match depth to scope.** A single-concept reference stays short. Do not pad.
- **Capitalized bullets.** Start every bullet with a capital letter. Keep list voice consistent across all files.
- **Sparing examples.** Use a concrete example only to clarify a shape or structure, never to fix a naming choice. Do not anchor a name with an example token the reader could copy verbatim instead of choosing the most accurate name for their own case.
- **Positive rules.** State the action to take, not the mistake to avoid. Write "Use a role name for the integration" rather than "Do not name the integration after the vendor". A negative rule names the failure and quietly anchors it as the thing to copy; a positive rule points only at the correct move. A bare prohibition such as "Do not collapse the two surfaces" is weaker than "Keep each surface its own deployable". Reserve a "do not" only when no positive phrasing carries the same force, and never turn a banned example into a label the reader could lift verbatim.

Before finishing, confirm every `references/*.md` file appears in the `SKILL.md` reference-loading map, no reference names a tool in its title or restates another reference's rule, every bullet starts capitalized, `metadata.version` is bumped if behavior changed, and the README layout matches the actual files.
