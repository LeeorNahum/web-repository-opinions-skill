# Eval Harness

Runs clean-room agent sessions on the prompts in `../evals.json`, each in a copy of a fixture project from `../fixtures`, packages what each session left behind for blind critics, and records a graded round in `../results`. Maintainer-only. The cases are design and implementation requests a real owner would make, and every assertion is about the design a session produced, so a case shows a difference only when the skill changes what an agent decides.

## Needs

- The `claude` CLI signed in, for Claude Opus sessions, and the `codex` CLI signed in, for GPT Sol sessions.
- Python 3.11 or later and Git.

## Running a round

1. Pick a run folder outside the home folder, every Git repository, and every folder holding `.claude`, `.agents`, `CLAUDE.md`, or `AGENTS.md`, and export it as `EVAL_ROOT`. `run.py` refuses a folder inside any of them, because a session there could discover the owner's own skills or instructions. Keep spaces out of the path, since `batch.py` splits each job line on spaces. Run Python with `-B` so no bytecode lands beside the harness.
2. Snapshot the skill under `EVAL_ROOT`: the base as committed (`git archive <base> | tar -x -C "$EVAL_ROOT/skill-old/web-repository-opinions"`) and, when measuring a change, the changed tree (`SKILL.md`, `references/`, and `assets/` copied into `$EVAL_ROOT/skill-new/web-repository-opinions`).
3. Write a jobs file with one line per session, `<round>-<eval name>-<arm>-<model> <eval name> <opus|sol> <snapshot folder> 1200`, naming the arms `old` and `new`. `<round>` is a number, which `grade.py` requires.
4. `python -B batch.py <jobs file> 3` runs them, three at a time. Lower the number on a machine short of memory.
5. `python -B grade.py <jobs file> <round>` marks a missing or unfinished session as failing, reports a session that never opened the skill as a setup failure, lists the references each session read, and writes a blind package per eval under `$EVAL_ROOT/judge/<round>-<eval>`.
6. `python -B critics.py <round> 3` gives `CRITIC.md` to one critic per provider per eval, each told the letters it judges: a GPT critic for the Claude-built letters and a Claude critic for the GPT-built ones, so no model grades its own family. They grade the semantic assertions and list blocking findings, and each critic's session id is saved beside its file for the answer round.
7. Answer every blocking finding against a new session in writing, resume the critic with the answers, and record how each settled in `critic-answers.json` in that judge folder.
8. `python -B compare.py <jobs file> <round>` exits 0 only when every new session passes every assertion, nothing every old session passed regresses, and every blocking finding against a new session is withdrawn.
9. `python -B record.py <jobs file> <round> ../results/<round folder> <skill commit>` copies each session's answer, changes, condensed transcript, and grading into the eval area, with `SUMMARY.md` and `summary.json`. It redacts exported secrets, every string in the CLIs' credential files, credential-shaped tokens, and the owner's home and run paths, cuts any file above 300,000 characters, and refuses a round above 8 MB. Read its redaction count, and search the folder for anything private, before committing it.
10. Delete `EVAL_ROOT`. Each session's `cfg` folder holds a copy of the CLI's credentials.

Each session gets a config folder of its own holding only the credentials and an allowlisted environment, so the owner's instruction files, memory, plugins, MCP servers, and exported keys are not configured for it. `result.json` records the model the CLI reports it served, the CLI version, and hashes of the installed skill, the fixture, `evals.json`, and the harness, so a later round can show it measured the same inputs. This is configuration isolation, not a file-system sandbox: the prompt keeps each session in its working folder, and the session records show what it read.

## Reading a result

Each case carries a `role`. A `pressure` case is one where the skill should change what an agent decides, and a `restraint` case is one where a good decision must survive a rule being applied too broadly, so report gains from pressure cases and treat any restraint failure as a regression.

Design answers vary between runs, so one session per arm and model is a signal, not a measurement. Read the transcript of every failed assertion before changing the skill: a session that never opened the owning reference fails for a routing reason, and one that read it and decided otherwise fails for a wording reason. An assertion that passes in every arm of every round no longer discriminates and is a candidate to drop.
