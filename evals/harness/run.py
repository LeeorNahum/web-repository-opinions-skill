"""Run one clean-room builder session.

Usage: python run.py <label> <arm> <model> <prompt-file> <skill-dir or -> [timeout-seconds]
  arm:    none | skill
  model:  opus | sol
Environment: EVAL_ROOT, the run folder. It must sit outside the home folder and outside every
Git repository, because Claude Code discovers skills in the .claude folders of the working
directory's ancestors, and the home folder holds the owner's own.

Creates EVAL_ROOT/builds/<label>/work (the builder's working directory) and cfg (an isolated
config folder holding only a copy of the CLI's credentials, which the run folder's deletion
removes). The skill goes where each harness discovers project skills: .claude/skills for
Claude Code, .agents/skills for Codex. Writes session.jsonl, stderr.txt, and result.json.
"""
import json, os, pathlib, shutil, subprocess, sys, time

HOME = pathlib.Path.home()
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()
# Claude Code resolves the `opus` alias to the latest Opus. Codex has no family alias, so its
# current Sol identifier is pinned here and changes when Codex does.
MODELS = {'opus': 'opus', 'sol': 'gpt-6-sol'}
EFFORT = 'medium'
MAINTAINER_ONLY = shutil.ignore_patterns('.git', 'evals', 'README.md', 'AGENTS.md', 'node_modules')


def guard():
    if not os.environ.get('EVAL_ROOT'):
        sys.exit('Set EVAL_ROOT to a run folder outside the home folder and every Git repository.')
    if ROOT == HOME or HOME in ROOT.parents:
        sys.exit(f'{ROOT} is inside the home folder, whose .claude folder would leak into builds.')
    ROOT.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0:
        sys.exit(f'{ROOT} is inside the Git repository {r.stdout.strip()}.')


def skill_name(skill_dir):
    for line in (skill_dir / 'SKILL.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('name:'):
            return line.split(':', 1)[1].strip().strip('"')
    sys.exit('SKILL.md has no name')


def main():
    guard()
    label, arm, model, prompt_file = sys.argv[1:5]
    skill_dir = pathlib.Path(sys.argv[5]).resolve() if len(sys.argv) > 5 and sys.argv[5] != '-' else None
    timeout = int(sys.argv[6]) if len(sys.argv) > 6 else 1200
    base = ROOT / 'builds' / label
    if base.exists():
        sys.exit(f'{base} exists')
    work, cfg = base / 'work', base / 'cfg'
    work.mkdir(parents=True)
    cfg.mkdir()
    prompt = pathlib.Path(prompt_file).read_text(encoding='utf-8').strip()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('CLAUDE', 'CODEX', 'ANTHROPIC', 'OPENAI'))}
    if model == 'opus':
        shutil.copyfile(HOME / '.claude/.credentials.json', cfg / '.credentials.json')
        if arm == 'skill':
            shutil.copytree(skill_dir, work / '.claude/skills' / skill_name(skill_dir), ignore=MAINTAINER_ONLY)
        env.update(CLAUDE_CONFIG_DIR=str(cfg), CLAUDE_CODE_DISABLE_AUTO_MEMORY='1', DISABLE_AUTOUPDATER='1', DISABLE_TELEMETRY='1')
        args = [shutil.which('claude'), '-p', '--dangerously-skip-permissions', '--model', MODELS['opus'], '--effort', EFFORT,
                '--strict-mcp-config', '--no-chrome', '--output-format', 'stream-json', '--verbose', prompt]
    elif model == 'sol':
        shutil.copyfile(HOME / '.codex/auth.json', cfg / 'auth.json')
        if arm == 'skill':
            shutil.copytree(skill_dir, work / '.agents/skills' / skill_name(skill_dir), ignore=MAINTAINER_ONLY)
        env.update(CODEX_HOME=str(cfg))
        args = [shutil.which('codex'), 'exec', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox', '--ignore-rules',
                '-m', MODELS['sol'], '-c', f'model_reasoning_effort="{EFFORT}"', '--json', '-o', str(base / 'last-message.txt'), '-C', str(work), prompt]
    else:
        sys.exit('model must be opus or sol')
    start = time.time()
    completed = False
    with open(base / 'session.jsonl', 'w', encoding='utf-8') as out, open(base / 'stderr.txt', 'w', encoding='utf-8') as err:
        p = subprocess.Popen(args, cwd=work, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        # A session can finish its turn while a server it started keeps the process alive, so
        # the turn's completion event, not the process exit, marks the end of the build.
        while p.poll() is None and time.time() - start < timeout:
            time.sleep(5)
            text = (base / 'session.jsonl').read_text(encoding='utf-8', errors='replace')
            if '"type":"result"' in text or '"type":"turn.completed"' in text:
                completed = True
                seconds = round(time.time() - start, 1)
                time.sleep(5)
                break
        if p.poll() is None:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
            else:
                p.kill()
        code = 0 if completed else (p.returncode if p.returncode is not None else 124)
    if not completed:
        seconds = round(time.time() - start, 1)
        completed = code == 0
    result = {'label': label, 'arm': arm, 'model': model, 'prompt': pathlib.Path(prompt_file).stem,
              'skill': str(skill_dir) if skill_dir else None, 'exit': code, 'completed': completed, 'seconds': seconds}
    (base / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
