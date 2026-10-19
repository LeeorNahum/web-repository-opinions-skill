"""Have fresh critic sessions grade the semantic assertions of a round, following CRITIC.md.

Usage: python critics.py <round> [max-concurrent] [--second opus2|sol]
Environment: EVAL_ROOT, the run folder grade.py packaged.

A round runs on Claude Opus and a second subject arm: GPT Sol through Codex (`sol`, the default), or a
second, independent Opus arm (`opus2`). With `sol`, Sol grades the Opus-built letters and Opus grades
Sol's, so no model grades its own work. With `opus2`, every letter is graded by a fresh Opus critic
session, one per subject arm per eval, and the round's summary says that both arms and all graders
are Opus. Each critic writes critic-<name>.json in the judge folder, and its session id is saved
beside it in critic-<name>.session so the builder can resume it with answers to its blocking
findings. Critics run with a config folder holding only the CLI's credentials and the sessions'
environment allowlist, so the owner's instructions, skills, plugins, and exported keys do not reach
them. Delete EVAL_ROOT/critic-cfg with the run folder.
A folder that already holds a critic's file is skipped for that critic.
"""
import concurrent.futures, json, os, pathlib, re, shutil, subprocess, sys

from run import ENV_ALLOW

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()
HOME = pathlib.Path.home()
OPUS = ['--model', 'opus', '--effort', 'high']
SOL = ['--model', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="high"']


def task(folder, critic, letters):
    return (f"Read {HERE / 'CRITIC.md'} and follow it exactly. Your folder is {folder}, and everything you need is inside it. "
            f"Judge only these letters: {', '.join(letters)}. Your provider name is {critic}, so write {folder / f'critic-{critic}.json'}. "
            "You are finished when that file parses and holds a verdict with evidence for every assertion in semantic.json for each of your letters.")


def isolated(folder, critic):
    """A config folder holding only the CLI's credentials, and the same environment allowlist sessions get.
    It is kept under EVAL_ROOT/critic-cfg so the critic can be resumed with the same configuration."""
    cfg = ROOT / 'critic-cfg' / f'{folder.name}-{critic}'
    cfg.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k.upper() in ENV_ALLOW}
    if critic == 'sol':
        shutil.copyfile(HOME / '.codex/auth.json', cfg / 'auth.json')
        env['CODEX_HOME'] = str(cfg)
    else:
        shutil.copyfile(HOME / '.claude/.credentials.json', cfg / '.credentials.json')
        env.update(CLAUDE_CONFIG_DIR=str(cfg), CLAUDE_CODE_DISABLE_AUTO_MEMORY='1', DISABLE_AUTOUPDATER='1')
    return env


def run(folder, critic, letters):
    out = folder / f'critic-{critic}.json'
    if out.exists():
        return f'{folder.name} {critic}: exists'
    env = isolated(folder, critic)
    if critic.startswith('opus'):
        args = [shutil.which('claude'), '-p', *OPUS, '--dangerously-skip-permissions', '--strict-mcp-config', '--output-format', 'json', task(folder, critic, letters)]
        r = subprocess.run(args, cwd=folder, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, encoding='utf-8', errors='replace')
        sid = (json.loads(r.stdout or '{}') if (r.stdout or '').strip().startswith('{') else {}).get('session_id')
    else:
        args = [shutil.which('codex'), 'exec', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox', *SOL,
                '-C', str(folder), '-o', str(folder / 'critic-sol.reply.txt'), task(folder, critic, letters)]
        r = subprocess.run(args, cwd=folder, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, encoding='utf-8', errors='replace')
        m = re.search(r'session id: (\S+)', (r.stdout or '') + (r.stderr or ''))
        sid = m.group(1) if m else None
    (folder / f'critic-{critic}.session').write_text(sid or '', encoding='utf-8')
    ok = out.exists()
    try:
        json.loads(out.read_text(encoding='utf-8')) if ok else None
    except ValueError:
        ok = False
    return f"{folder.name} {critic}: {'ok' if ok else 'NO VALID FILE, exit ' + str(r.returncode)}"


def main():
    args = sys.argv[1:]
    second = args[args.index('--second') + 1] if '--second' in args else 'sol'
    pos = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--second')]
    rnd = pos[0]
    n = int(pos[1]) if len(pos) > 1 else 3
    # Critic name per subject arm. With a second Opus arm, each arm gets its own fresh Opus critic.
    critic_for = {'opus': 'opus-for-opus', 'opus2': 'opus-for-opus2'} if second == 'opus2' else {'opus': 'sol', 'sol': 'opus'}
    jobs = []
    for folder in sorted((ROOT / 'judge').glob(f'{rnd}-*')):
        key = json.loads((ROOT / 'keys' / f'{folder.name}.json').read_text(encoding='utf-8'))
        for subject, critic in critic_for.items():
            letters = [l for l, label in key.items() if label.endswith(f'-{subject}')]
            if letters:
                jobs.append((folder, critic, letters))
    with concurrent.futures.ThreadPoolExecutor(n) as pool:
        for line in pool.map(lambda j: run(*j), jobs):
            print(line, flush=True)


if __name__ == '__main__':
    main()
