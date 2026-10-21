# Eval Harness

Runs clean-room agent sessions on the prompts in `../evals.json`, each in a copy of a fixture project from `../fixtures`, packages what each session left behind for blind critics, and records a graded round in `../results`. Maintainer-only. The cases are design and implementation requests a real owner would make, and every assertion is about the design a session produced, so a case shows a difference only when the skill changes what an agent decides.

## Needs

- The `claude` CLI signed in, for Opus sessions. A round's second subject arm is Sol through a signed-in `codex` CLI (`sol`), or a second, independent Opus arm (`opus2`) when only Opus is to be used.
- Python 3.11 or later and Git.

## Running a round

1. Pick a run folder outside the home folder, every Git repository, and every folder holding `.claude`, `.agents`, `CLAUDE.md`, or `AGENTS.md`, and export it as `EVAL_ROOT`. `run.py` refuses a folder inside any of them, because a session there could discover the owner's own skills or instructions. Keep spaces out of the path, since `batch.py` splits each job line on spaces. Run Python with `-B` so no bytecode lands beside the harness.
2. Commit the revision on its branch, then snapshot both arms from commits the same way: `git archive <base> | tar -x -C "$EVAL_ROOT/skill-old/web-repository-opinions"` for the base, and the same command with the revision's commit into `skill-new`. A snapshot from a commit is reproducible, and a copy of the working tree can pick up files that were never committed or miss ones that were.
3. Write a jobs file with one line per session, `<round>-<eval name>-<arm>-<model> <eval name> <opus|opus2|sol> <snapshot folder> 1200`, naming the arms `old` and `new`. `<round>` is a number, which `grade.py` requires.
4. `python -B batch.py <jobs file> 3` runs them, three at a time. Lower the number on a machine short of memory.
5. `python -B grade.py <jobs file> <round>` marks a missing or unfinished session as failing, reports a session that never opened the skill as a setup failure, lists the references each session read, and writes a blind package per eval under `$EVAL_ROOT/judge/<round>-<eval>`.
6. `python -B critics.py <round> 3 --second <sol|opus2>` gives `CRITIC.md` to one critic per subject arm per eval, each told the letters it judges. With `sol`, Sol grades the Opus-built letters and Opus grades Sol's, so no model grades its own work. With `opus2`, fresh Opus critic sessions grade every letter, and both `compare.py` and `record.py` need `--allow-same-model`, which makes the round's `SUMMARY.md` say so. They grade the semantic assertions and list blocking findings, and each critic's session id is saved beside its file for the answer round.
7. Answer every blocking finding against a new session in writing, resume the critic with the answers, and record how each settled in `critic-answers.json` in that judge folder. When a critic of the other model has regraded letters that a critic of their own model graded, delete the same-model critic file, since `compare.py` fails any letter that still carries a verdict from its own model.
8. Run the old arm again in the same round as the new one, so both arms share the same models, CLI versions, and case versions. A recorded earlier round is a reference, not the comparison's old arm. `python -B compare.py <jobs file> <round>` exits 0 only when every new session passes every assertion of every pressure case, no assertion an old session passed fails in a new session, and every blocking finding against a new session is withdrawn.
9. `python -B record.py <jobs file> <round> ../results/<round folder> <skill commit>` writes each session's answer, changes, condensed transcript, and grading into the eval area for local reading, redacted and size-capped. That folder is ignored. Add the round's per-case scores to `../results/SUMMARY.md`, which is the only result that is committed.
10. Delete `EVAL_ROOT`. Each session's `cfg` folder holds a copy of the CLI's credentials.

Each session gets a config folder of its own holding only the credentials and an allowlisted environment, so the owner's instruction files, memory, plugins, MCP servers, and exported keys are not configured for it. `result.json` records the model the CLI reports it served, the CLI version, and hashes of the installed skill, the fixture, `evals.json`, and the harness, so a later round can show it measured the same inputs. This is configuration isolation, not a file-system sandbox: the prompt keeps each session in its working folder, and the session records show what it read.

## Reading a result

Each case carries a `role`. A `pressure` case is one where the skill should change what an agent decides. A `restraint` case is one where a good decision must survive a rule being applied too broadly. A `control` case is one where the current skill already makes the deciding call, kept so a revision that breaks it shows up. Report gains from pressure cases only. In a restraint or control case, an assertion the old arm passed and the new arm fails is a regression, while one the old arm already failed is reported if a revision fixes it and does not block.

Design answers vary between runs, so one session per arm and model is a signal, not a measurement. Read the transcript of every failed assertion before changing the skill: a session that never opened the owning reference fails for a routing reason, and one that read it and decided otherwise fails for a wording reason. An assertion that passes in every arm of every round no longer discriminates and is a candidate to drop.
