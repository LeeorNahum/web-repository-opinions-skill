# AGENTS.md

Rules for editing the **web-repository-opinions** skill. User-facing opinions live in `SKILL.md` and `references/`. `README.md` is the human skim layer.

## File roles

| File | Role |
| --- | --- |
| `SKILL.md` | Trigger, default stack, reference-loading map, non-negotiables, audit |
| `references/*.md` | One single concept per file, named by paradigm |
| `assets/` | Exact copyable starter files governed by an owning reference |
| `scripts/check-layout.mjs` | The layout check an agent runs on its own served build, with `package.json` naming it for the remote route |
| `evals/` | Behavioral test briefs, their assertions, and the clean-room harness. Maintainer-only, never loaded at use time |
| `README.md` | Short human summary |

One owner per opinion. Each reference owns its concept. Other files use the term or shape without restating the rule. The reference-loading map lives in `SKILL.md` once. References assume the agent already loaded what their section needs.

`definition-of-done.md` is a summary index across owning references, not a second source of truth. It may name completion categories and representative checks, but detailed rules stay in their concept references.

When a reference has a copyable asset, the reference owns the decision and the asset owns the exact file bytes. Do not maintain a second complete copy of the asset inside the reference.

## Repository-Opinions Skill Layout

This skill follows the shared layout for repository-opinions skills. Keep that shape so the skill type stays consistent and grows cleanly:

- `SKILL.md` is a slim spine: a short thesis, a default-stack or default-toolchain table of swappable tool picks, the reference-loading map, the core non-negotiables, the repository audit, and a closing note that risky-change "Ask before" lines live in the references.
- `references/*.md` hold one concept each, named by paradigm, carrying the detailed opinions. Distribute each "Ask before" guardrail into the reference that owns its topic rather than a standalone section.
- `assets/` hold copyable starter configs that drop into a target repo. References explain the judgment. Assets are the copy-paste artifacts.
- `AGENTS.md` is this maintenance contract.
- `README.md` is the human skim layer.

A repository-opinions skill is opinionated and explicit, names its default tools as swappable picks, uses placeholder project names, and keeps one owner per opinion.

## Editing

- Bump `metadata.version` by the release-versioning skill's rules for skills.
- Encode a default only when backed by user preference or real usage.
- Treat criticism as evidence to reassess an opinion, not an automatic instruction to remove or preserve it.
- Admit an opinion only when its scope is clear and it improves decisions across multiple unrelated web products. Keep a proven project pattern out of the skill when its generality is still uncertain.
- Distinguish universal invariants, conditional patterns, product choices, and implementation details. State the condition for a conditional pattern instead of promoting it as a universal invariant.
- Give broad sections an attention budget. A batch of related additions must not dominate Core Non-Negotiables, the repository audit, or README coverage merely because they were edited together.
- Judge every addition against the whole file, not the size or focus of the current prompt. Give it only the heading level, repetition, and surrounding coverage its enduring importance warrants. Prefer fitting a narrow rule into its existing owner over creating a new section or widening several summary files around it.
- Preserve working wording outside the required change. Refactor or replace an existing sentence only when the new requirement makes that sentence inaccurate, misplaced, or genuinely weaker, and confirm that the replacement preserves its prior meaning.
- Prevent context residue while drafting. Before adding a detail, consider whether it is an enduring web opinion or just nearby context from the current repo, provider, incident, or prompt. Keep examples generic, and place narrow detail in the current owning concept without freezing today's reference layout unless the layout itself is being documented.
- Reserve Core Non-Negotiables for rules that should affect nearly every web repo. Keep narrower guidance in its owning reference.
- Keep the repository audit balanced across architecture, runtime, data, UX, operations, and release readiness. Fold new checks into an existing category when they do not deserve a permanent top-level audit step.
- Prefer deletion over caveats. More words is not better.
- One opinion per reference. When a new paradigm, way of thinking, service, or workflow is added, give it its own reference file and add it to the `SKILL.md` reference-loading map. Do not bolt a second unrelated concept onto an existing reference.
- When an existing concept grows, refactor its reference rather than scattering the idea across several files.
- **Opinionated and explicit.** State the preference clearly. This skill takes positions.
- **Paradigm-named, provider-stated.** File and section names describe the job, never the vendor. Inside a section, name the default tool as a swappable pick.
- **No sibling-skill pointers.** Do not reference other skills by name. Where another skill's domain touches a topic, state the web opinion inline and stop.
- **No cross-reference pointers.** A reference never links to or points at another reference. The `SKILL.md` reference-loading map is the only index, so a rename cannot leave a dead link and there is no second place to keep in sync. A reference assumes the agent already loaded what its section needs.
- **No project leakage.** Use placeholder repo, product, and domain names. Do not embed a real product's name, palette, routes, or credentials.
- **No em dashes.** Use commas, periods, parentheses, or "to".
- **Match depth to scope.** A single-concept reference stays short. Do not pad.
- **Capitalized bullets.** Start every bullet with a capital letter. Keep list voice consistent across all files.
- **Sparing examples.** Use a concrete example only to clarify a shape or structure, never to fix a naming choice. Do not anchor a name with an example token the reader could copy verbatim instead of choosing the most accurate name for their own case.
- **Positive rules.** State the action to take, not the mistake to avoid. Write "Use a role name for the integration" rather than "Do not name the integration after the vendor". A negative rule names the failure and quietly anchors it as the thing to copy. A positive rule points only at the correct move. A bare prohibition such as "Do not collapse the two surfaces" is weaker than "Keep each surface its own deployable". Reserve a "do not" only when no positive phrasing carries the same force, and never turn a banned example into a label the reader could lift verbatim.

## Behavioral Testing

A rule that shows up in what an agent builds, on screen, in the file layout, in config, or in the build output, is proven by clean-room builds before it is committed. Hold the whole change, including any edit to this process, to the monolith-audit skill, read from RemoteSkill or wherever it is installed. The steps:

1. Find the evals in `evals/evals.json` whose prompt exercises the rule, and give each an assertion that decides the rule from the build alone: a measurement and its threshold, or a file and what it holds. When no eval exercises it, add one: a request a real person would type, about an invented product, that never mentions the rule. The evals cover a public site, a signed-in app, a new repository, and an HTTP API with an MCP server, so a rule about billing, uploads, background jobs, or another surface they do not reach usually needs a new eval.
2. Snapshot the skill as last committed and as changed, outside any repository.
3. Build each affected eval with both snapshots in fresh sessions, following `evals/harness/README.md`: at least one Claude Opus and one GPT Sol build per snapshot, four at a time, 20 minutes each. Confirm from every session record that the skill loaded in its builds and that nothing else of the owner's did.
4. Blind the builds and grade every assertion of the affected evals as `evals/harness/GRADER.md` describes: install, build, serve the production build, capture and measure it at four widths, look at every capture, and use every action the prompt asks for.
5. Have critics judge the rendered builds blind as `evals/harness/CRITIC.md` describes, a GPT critic for the Claude-built builds and a Claude critic for the GPT-built ones, answer every finding in writing, and resume each critic with the answers until it withdraws or holds each one.
6. Pass when every changed-snapshot build passes each changed rule's assertions, a not-applicable grade counting as not passed, no assertion that every last-committed build passed fails in a changed build, and the critic holds no blocking finding against a changed build that the last-committed builds did not also have.
7. When it fails, rewrite the rule into something an agent can check against its own output, such as a number, a file, a named shape, or a line in the layout check, and run again. After four rounds, stop and report what still fails instead of committing it.
8. Leave the change uncommitted for the owner's review, with a proposed commit message that names the evals run, the builds per snapshot, and the pass counts. Commit only after the owner approves. Delete the run folder, which holds copied credentials, and confirm by listing that no copy remains.

A rule that needs live providers, DNS, real payments, or dashboards is not built. It gets a critic's review against the provider's first-party documentation instead.

## Compatibility Posture

Treat the current intended product contract as truth. Compatibility is never an automatic courtesy for unreleased, internal, or mistaken behavior.

Add compatibility only when an explicit supported contract, deployed client, public integration, durable user data, or approved rollout requires it. Name the preserved contract, its consumers, its removal condition if temporary, and the verification that proves both old and new behavior remain intentional.

Before finishing, confirm the behavioral tests above passed for every buildable rule the change touches, every `references/*.md` file appears in the `SKILL.md` reference-loading map, no reference names a tool in its title or restates another reference's rule, every bullet starts capitalized, `metadata.version` is bumped as the release-versioning skill requires, and the README layout matches the actual files.
