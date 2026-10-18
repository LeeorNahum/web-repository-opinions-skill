"""Have cross-provider critics grade the semantic assertions of a round, following CRITIC.md.

Usage: python critics.py <round> [max-concurrent]
Environment: EVAL_ROOT, the run folder grade.py packaged.

For every judge/<round>-<eval> folder, reads its key from keys/ and starts one critic per provider that has
letters to judge: a GPT critic (Codex) for the letters Claude sessions built, and a Claude critic
for the letters Codex sessions built, so no model grades its own family's work. Each critic writes
critic-codex.json or critic-claude.json in that folder, and its session id is saved beside it in
critic-<provider>.session so the builder can resume it with answers to its blocking findings. Critics
run with a config folder holding only the CLI's credentials and the sessions' environment allowlist,
so the owner's instructions, skills, plugins, and exported keys do not reach them. Delete
EVAL_ROOT/critic-cfg with the run folder.
A folder that already holds a critic's file is skipped for that critic.

When Codex is unreachable, `--same-family-fallback` has a Claude critic grade the Claude-built letters
too, writing critic-claude-fallback.json. That breaks the cross-family rule, so a round graded this way
says so in its summary and its Claude-built letters are regraded by Codex before any comparison.
"""
import concurrent.futures, json, os, pathlib, re, shutil, subprocess, sys

from run import ENV_ALLOW

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()
HOME = pathlib.Path.home()
MODELS = {'claude': ['--model', 'opus', '--effort', 'high'], 'claude-fallback': ['--model', 'opus', '--effort', 'high'], 'codex': ['--model', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="high"']}


def task(folder, provider, letters):
    return (f"Read {HERE / 'CRITIC.md'} and follow it exactly. EVAL_ROOT is {ROOT}. Your folder is {folder}. "
            f"Judge only these letters: {', '.join(letters)}. Your provider name is {provider}, so write {folder / f'critic-{provider}.json'}. "
            "You are finished when that file parses and holds a verdict with evidence for every assertion in semantic.json for each of your letters.")


def isolated(folder, provider):
    """A config folder holding only the CLI's credentials, and the same environment allowlist sessions get.
    It is kept under EVAL_ROOT/critic-cfg so the critic can be resumed with the same configuration."""
    cfg = ROOT / 'critic-cfg' / f'{folder.name}-{provider}'
    cfg.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if k.upper() in ENV_ALLOW}
    if provider == 'codex':
        shutil.copyfile(HOME / '.codex/auth.json', cfg / 'auth.json')
        env['CODEX_HOME'] = str(cfg)
    else:
        shutil.copyfile(HOME / '.claude/.credentials.json', cfg / '.credentials.json')
        env.update(CLAUDE_CONFIG_DIR=str(cfg), CLAUDE_CODE_DISABLE_AUTO_MEMORY='1', DISABLE_AUTOUPDATER='1')
    return env


def run(folder, provider, letters):
    out = folder / f'critic-{provider}.json'
    if out.exists():
        return f'{folder.name} {provider}: exists'
    env = isolated(folder, provider)
    if provider in ('claude', 'claude-fallback'):
        args = [shutil.which('claude'), '-p', *MODELS[provider], '--dangerously-skip-permissions', '--strict-mcp-config', '--output-format', 'json', task(folder, provider, letters)]
        r = subprocess.run(args, cwd=folder, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        sid = (json.loads(r.stdout or '{}') if r.stdout.strip().startswith('{') else {}).get('session_id')
    else:
        args = [shutil.which('codex'), 'exec', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox', *MODELS['codex'],
                '-C', str(folder), '-o', str(folder / 'critic-codex.reply.txt'), task(folder, provider, letters)]
        r = subprocess.run(args, cwd=folder, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        m = re.search(r'session id: (\S+)', r.stdout + r.stderr)
        sid = m.group(1) if m else None
    (folder / f'critic-{provider}.session').write_text(sid or '', encoding='utf-8')
    ok = out.exists()
    try:
        json.loads(out.read_text(encoding='utf-8')) if ok else None
    except ValueError:
        ok = False
    return f"{folder.name} {provider}: {'ok' if ok else 'NO VALID FILE, exit ' + str(r.returncode)}"


def main():
    flags = [a for a in sys.argv[1:] if a.startswith('--')]
    pos = [a for a in sys.argv[1:] if not a.startswith('--')]
    rnd = pos[0]
    n = int(pos[1]) if len(pos) > 1 else 3
    opus_critic = 'claude-fallback' if '--same-family-fallback' in flags else 'codex'
    jobs = []
    for folder in sorted((ROOT / 'judge').glob(f'{rnd}-*')):
        key = json.loads((ROOT / 'keys' / f'{folder.name}.json').read_text(encoding='utf-8'))
        for provider, family in ((opus_critic, 'opus'), ('claude', 'sol')):
            letters = [l for l, label in key.items() if label.endswith(f'-{family}')]
            if letters:
                jobs.append((folder, provider, letters))
    with concurrent.futures.ThreadPoolExecutor(n) as pool:
        for line in pool.map(lambda j: run(*j), jobs):
            print(line, flush=True)


if __name__ == '__main__':
    main()
