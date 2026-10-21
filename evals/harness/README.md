# Eval Harness

Runs clean-room builds of the prompts in `../evals.json`, blinds them, and prepares them for grading. Maintainer-only. The skill's `AGENTS.md` says when to run it and what counts as a pass.

## Needs

- The `claude` CLI signed in, for Claude Opus builders, and the `codex` CLI signed in, for GPT Sol builders.
- Python 3.11 or later with Pillow, and Node.js 20 or later.
- `npm install` and `npx playwright install chromium` in this folder, once.

## Run

1. Pick a run folder outside the home folder and every Git repository, with no spaces in its path, and export it as `EVAL_ROOT`. `run.py` refuses anything else, because a builder there could discover the owner's own skills.
2. Snapshot the skill twice under `EVAL_ROOT`: as last committed (`git archive HEAD | tar -x -C "$EVAL_ROOT/skill-old"`) and as changed (a copy of the working tree).
3. Write each eval's `prompt` from `../evals.json` to a text file under `EVAL_ROOT`, then a jobs file with one line per build, `<round>-<eval>-<arm>-<model> skill <opus|sol> <prompt file> <snapshot folder> 1200`, naming the arms `old` and `new`. Add a `none` arm with `-` in place of the snapshot when measuring the skill against no skill.
4. `python batch.py <jobs file> 4` runs them, four at a time.
5. `python skillreads.py <snapshot folder> $EVAL_ROOT/builds/*` reports which skill files each session appears to have read, every other skill folder it touched, and every absolute `SKILL.md` path outside the build's own folder. Every skill build shows `SKILL.md`, no `none` build shows any skill file, and both lists stay empty. A heading match is a hint, so open the session record of any build that looks wrong. `timing.py` reports seconds and tokens per build.
6. For each eval, `python blind.py <round> <eval> <labels...>` makes `$EVAL_ROOT/judge/<round>-<eval>`. Give one grader `GRADER.md` and that folder. After it finishes, read `key.json` yourself and give `CRITIC.md` to two critics, each told the letters it judges: a GPT critic for the Claude-built letters and a Claude critic for the GPT-built ones, so every build is judged from the other provider. Grade a `none` arm in its own folder.
7. Record how each blocking critic finding against a new build settled in `critic-answers.json` in the judge folder, then run `python compare.py <round>-<eval> old new <changed assertion ids>`. It prints the lists the pass bar in `AGENTS.md` reads and exits 0 only when the comparison is complete, every new build passes every changed assertion, nothing regressed, and every blocking finding is settled.
8. Delete `EVAL_ROOT`. Each build's `cfg` folder holds a copy of the CLI's credentials.

Each builder gets a config folder of its own holding only the credentials, so no instruction file, memory, plugin, or MCP server of the owner's reaches it. Built-in CLI features and skills remain and are identical across arms. This is configuration isolation, not a file-system sandbox, so the prompt keeps each builder in its working folder.
