"""Run one clean-room session of a web-repository-opinions eval.

Usage: python run.py <label> <eval name> <model> <skill-dir or -> [timeout-seconds]
  model:  opus | opus2 (a second, independent Opus arm) | sol
Environment: EVAL_ROOT, the run folder. It must sit outside the home folder and outside every
Git repository, because Claude Code discovers skills in the .claude folders of the working
directory's ancestors, and the home folder holds the owner's own.

Builds EVAL_ROOT/builds/<label>/work from ../fixtures/base plus the eval's fixture overlay, as a
fresh Git repository with one commit, so grading reads the session's changes from Git. A
fixture's REMOVE file lists paths to delete from the base. The skill goes where each harness
discovers project skills: .claude/skills for Claude Code, .agents/skills for Codex. cfg holds
only a copy of the CLI's credentials, which deleting the run folder removes.
The CLI gets an allowlisted environment, so no exported credential reaches a session.
Writes session.jsonl, stderr.txt, and result.json, which records the start time and the
baseline commit grading compares against.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time

import transcript
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
EVALS = HERE.parent / 'evals.json'
FIXTURES = HERE.parent / 'fixtures'
HOME = pathlib.Path.home()
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()
# Sol is pinned because the codex CLI takes no family alias. Move the pin when a newer Sol ships.
MODELS = {'opus': 'opus', 'opus2': 'opus', 'sol': 'gpt-6.1-sol'}
CLAUDE_MODELS = ('opus', 'opus2')
EFFORT = 'medium'
MAINTAINER_ONLY = shutil.ignore_patterns('.git', 'evals', 'README.md', 'AGENTS.md', 'node_modules')
# Only what the CLIs need to start. Anything else the maintainer exported, such as API keys, never reaches a session.
ENV_ALLOW = {'PATH', 'PATHEXT', 'SYSTEMROOT', 'SYSTEMDRIVE', 'WINDIR', 'COMSPEC', 'TEMP', 'TMP', 'TMPDIR', 'HOME',
             'USERPROFILE', 'HOMEDRIVE', 'HOMEPATH', 'APPDATA', 'LOCALAPPDATA', 'PROGRAMDATA', 'PROGRAMFILES',
             'PROGRAMFILES(X86)', 'COMMONPROGRAMFILES', 'NUMBER_OF_PROCESSORS', 'PROCESSOR_ARCHITECTURE', 'OS',
             'USERNAME', 'LANG', 'LC_ALL', 'TERM', 'SHELL'}
GIT = ['git', '-c', 'user.name=eval', '-c', 'user.email=eval@example.invalid', '-c', 'core.autocrlf=false']


def guard():
    if not os.environ.get('EVAL_ROOT'):
        sys.exit('Set EVAL_ROOT to a run folder outside the home folder and every Git repository.')
    if ROOT == HOME or HOME in ROOT.parents:
        sys.exit(f'{ROOT} is inside the home folder, whose .claude folder would leak into sessions.')
    ROOT.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0:
        sys.exit(f'{ROOT} is inside the Git repository {r.stdout.strip()}.')
    # Both CLIs read instructions and skills from the working folder's ancestors.
    for folder in [ROOT, *ROOT.parents]:
        found = [n for n in ('.claude', '.agents', 'CLAUDE.md', 'AGENTS.md') if (folder / n).exists()]
        if found:
            sys.exit(f'{folder} holds {", ".join(found)}, which a session would discover.')


def digest(path):
    """One hash over every file under a folder, by relative path and bytes, with CRLF read as LF so a checkout's line-ending setting cannot change it."""
    h = hashlib.sha256()
    files = (p for p in pathlib.Path(path).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    for f in sorted(files):
        h.update(f.relative_to(path).as_posix().encode() + b'|' + f.read_bytes().replace(b'\r\n', b'\n') + b'|')
    return h.hexdigest()[:16]


def cli_version(exe):
    return subprocess.run([exe, '--version'], capture_output=True, text=True).stdout.strip()


def skill_name(skill_dir):
    for line in (skill_dir / 'SKILL.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('name:'):
            return line.split(':', 1)[1].strip().strip('"')
    sys.exit('SKILL.md has no name')


def build_fixture(fixture, work):
    shutil.copytree(FIXTURES / 'base', work)
    if fixture != 'base':
        overlay = FIXTURES / fixture
        remove = overlay / 'REMOVE'
        if remove.exists():
            for rel in remove.read_text(encoding='utf-8').split():
                target = work / rel
                shutil.rmtree(target) if target.is_dir() else target.unlink(missing_ok=True)
        shutil.copytree(overlay, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns('REMOVE'))
    subprocess.run([*GIT, 'init', '-q'], cwd=work, check=True)
    subprocess.run([*GIT, 'add', '-A'], cwd=work, check=True)
    subprocess.run([*GIT, 'commit', '-qm', 'fixture'], cwd=work, check=True)


def main():
    guard()
    label, name, model = sys.argv[1:4]
    skill_dir = pathlib.Path(sys.argv[4]).resolve() if len(sys.argv) > 4 and sys.argv[4] != '-' else None
    timeout = int(sys.argv[5]) if len(sys.argv) > 5 else 1200
    spec = next((e for e in json.loads(EVALS.read_text(encoding='utf-8'))['evals'] if e['name'] == name), None)
    if not spec:
        sys.exit(f'no eval named {name}')
    base = ROOT / 'builds' / label
    if base.exists():
        sys.exit(f'{base} exists')
    work, cfg = base / 'work', base / 'cfg'
    base.mkdir(parents=True)
    build_fixture(spec['fixture'], work)
    cfg.mkdir()
    prompt = spec['prompt']
    env = {k: v for k, v in os.environ.items() if k.upper() in ENV_ALLOW}
    if model in CLAUDE_MODELS:
        shutil.copyfile(HOME / '.claude/.credentials.json', cfg / '.credentials.json')
        if skill_dir:
            shutil.copytree(skill_dir, work / '.claude/skills' / skill_name(skill_dir), ignore=MAINTAINER_ONLY)
        env.update(CLAUDE_CONFIG_DIR=str(cfg), CLAUDE_CODE_DISABLE_AUTO_MEMORY='1', DISABLE_AUTOUPDATER='1', DISABLE_TELEMETRY='1')
        args = [shutil.which('claude'), '-p', '--dangerously-skip-permissions', '--model', MODELS[model], '--effort', EFFORT,
                '--strict-mcp-config', '--no-chrome', '--output-format', 'stream-json', '--verbose', prompt]
    elif model == 'sol':
        shutil.copyfile(HOME / '.codex/auth.json', cfg / 'auth.json')
        if skill_dir:
            shutil.copytree(skill_dir, work / '.agents/skills' / skill_name(skill_dir), ignore=MAINTAINER_ONLY)
        env.update(CODEX_HOME=str(cfg))
        args = [shutil.which('codex'), 'exec', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox', '--ignore-rules',
                '-m', MODELS['sol'], '-c', f'model_reasoning_effort="{EFFORT}"', '--json', '-o', str(base / 'last-message.txt'), '-C', str(work), prompt]
    else:
        sys.exit('model must be opus, opus2, or sol')
    # Installing the skill must not count as a change the session made. Grading compares the
    # project with this commit, so a session that commits its own work is still graded on it.
    subprocess.run([*GIT, 'add', '-A'], cwd=work, check=True)
    subprocess.run([*GIT, 'commit', '-qm', 'skill', '--allow-empty'], cwd=work, check=True)
    baseline = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=work, capture_output=True, text=True).stdout.strip()
    # Hash the inputs before the session starts, so a session that writes into its own skill copy cannot change the record.
    installed = work / ('.claude' if model in CLAUDE_MODELS else '.agents') / 'skills'
    # The case's own spec, not the whole file, so editing one case leaves every other case's pairs intact.
    case = json.dumps({k: spec[k] for k in ('prompt', 'fixture', 'assertions')}, sort_keys=True).encode()
    digests = {'skill': digest(installed) if skill_dir else None, 'fixture': digest(FIXTURES / spec['fixture']),
               'base_fixture': digest(FIXTURES / 'base'), 'case': hashlib.sha256(case).hexdigest()[:16],
               'harness': digest(HERE)}
    started = datetime.now().astimezone()
    start = time.time()
    with open(base / 'session.jsonl', 'w', encoding='utf-8') as out, open(base / 'stderr.txt', 'w', encoding='utf-8') as err:
        p = subprocess.Popen(args, cwd=work, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        # Wait for the process to exit on its own: work a session hands to a background agent is
        # part of its result, so nothing here ends a session that is still running before the timeout.
        while p.poll() is None and time.time() - start < timeout:
            time.sleep(5)
        timed_out = p.poll() is None
        if timed_out:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(p.pid), '/T', '/F'], capture_output=True)
            else:
                p.kill()
            p.wait()
    seconds = round(time.time() - start, 1)
    completed = transcript.finished(base, model) and not timed_out and p.returncode == 0
    result = {'label': label, 'eval': name, 'model': model, 'model_id': MODELS[model], 'effort': EFFORT,
              'skill': str(skill_dir) if skill_dir else None, 'exit': p.returncode, 'timed_out': timed_out,
              'completed': completed, 'seconds': seconds, 'started': started.isoformat(timespec='seconds'),
              'finished': datetime.now().astimezone().isoformat(timespec='seconds'), 'baseline': baseline,
              # Claude Code reports the model it served. Codex reports none, so its pinned request is recorded as such.
              'served_model': transcript.served_model(base, model), 'requested_model': MODELS[model],
              'cli': cli_version(args[0]), 'prompt': prompt, 'digests': digests}
    (base / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
