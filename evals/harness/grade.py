"""Grade the check assertions of web-repository-opinions eval sessions, and package each eval for the critics.

Usage: python grade.py <jobs file> <round>
Environment: EVAL_ROOT, the run folder run.py used.

Every job in the jobs file of that round must have a session folder. A missing or unfinished session
is graded as failing every assertion, and a session that never opened the skill is reported as a
setup failure rather than a skill result. Each check assertion in ../evals.json maps to a function
in CHECKS by its id, and a check assertion with no function fails.

Writes EVAL_ROOT/grades-<round>.json and prints one line per session. Writes one blind package per
eval under EVAL_ROOT/judge/<round>-<eval>/: prompt.txt, semantic.json (the semantic assertions),
fixture/ (the starting project), and per letter answer.txt, diff.txt, and project/ (the whole
resulting project without .git or the installed skill). The letter-to-session key goes to
EVAL_ROOT/keys/<round>-<eval>.json, outside the folder critics work in. An existing
package folder is never overwritten.
"""
import json, os, pathlib, random, re, shutil, subprocess, sys

import transcript

HERE = pathlib.Path(__file__).resolve().parent
SPEC = json.loads((HERE.parent / 'evals.json').read_text(encoding='utf-8'))
EVALS = {e['name']: e for e in SPEC['evals']}
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()
SKIP = ('.claude/', '.agents/', '.git/')
LABEL = re.compile(r'(\d+)-(.+)-(old|new|none)-(opus|opus2|sol)$')

# Check assertions by id. Each takes the session's work folder and its changed paths.
CHECKS = {}


def git(work, *args):
    return subprocess.run(['git', *args], cwd=work, capture_output=True, text=True)


def read(folder, rel):
    p = pathlib.Path(folder) / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.is_file() else ''


def changed(work, baseline):
    names = git(work, 'diff', '--name-only', baseline).stdout.splitlines()
    names += git(work, 'ls-files', '--others', '--exclude-standard').stdout.splitlines()
    return sorted({n.strip().strip('"') for n in names if n.strip() and not n.strip('"').startswith(SKIP)})


def diff_text(work, baseline):
    diff = git(work, 'diff', '--no-color', baseline, '--', '.', ':!.claude', ':!.agents').stdout
    untracked = git(work, 'ls-files', '--others', '--exclude-standard').stdout.splitlines()
    return diff + ''.join(f'\n--- new file: {f}\n{read(work, f)}' for f in untracked if not f.startswith(SKIP))


def main():
    jobs_file, rnd = sys.argv[1], sys.argv[2]
    labels = [l.split()[0] for l in pathlib.Path(jobs_file).read_text().splitlines() if l.strip() and not l.startswith('#')]
    labels = [l for l in labels if l.startswith(f'{rnd}-')]
    rows = []
    for label in labels:
        m = LABEL.match(label)
        name, arm, model = m.group(2), m.group(3), m.group(4)
        base = ROOT / 'builds' / label
        work = base / 'work'
        result = json.loads(read(base, 'result.json') or '{}')
        ids = [a['id'] for a in EVALS[name]['assertions'] if a['kind'] == 'check']
        verdicts = {i: False for i in ids}
        ch, error = [], None
        finished = bool(result.get('completed')) and transcript.finished(base, model)
        if finished:
            try:
                ch = changed(work, result['baseline'])
            except Exception as e:
                error = repr(e)
            for i in ids:
                fn = CHECKS.get(i)
                try:
                    verdicts[i] = bool(fn(work, ch)) if fn else False
                except Exception as e:
                    verdicts[i], error = False, repr(e)
        rows.append({'build': label, 'eval': name, 'arm': arm, 'model': model, 'completed': finished,
                     'served_model': result.get('served_model') or transcript.served_model(base, model),
                     'timed_out': result.get('timed_out'), 'seconds': result.get('seconds'),
                     'skill_read': transcript.skill_read(base), 'references_read': transcript.references_read(base),
                     'usage': transcript.usage(base, model), 'changed': ch, 'checks': verdicts, 'error': error})
    (ROOT / f'grades-{rnd}.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    for r in rows:
        fails = [k for k, v in r['checks'].items() if not v]
        state = 'MISSING' if not r['completed'] else ('SETUP: skill not read' if not r['skill_read'] else ('ok' if not fails else 'FAIL ' + ','.join(fails)))
        print(f"{r['build']:58} refs={len(r['references_read']['full']):2} {state}{'  ' + r['error'] if r['error'] else ''}")
    rng = random.Random(f'{rnd}')
    for name in sorted({r['eval'] for r in rows}):
        folder = ROOT / 'judge' / f'{rnd}-{name}'
        if folder.exists():
            print(f'{folder} exists, left as is')
            continue
        sel = [r for r in rows if r['eval'] == name and r['completed']]
        rng.shuffle(sel)
        folder.mkdir(parents=True)
        (folder / 'prompt.txt').write_text(EVALS[name]['prompt'], encoding='utf-8')
        (folder / 'semantic.json').write_text(json.dumps([a for a in EVALS[name]['assertions'] if a['kind'] == 'semantic'], indent=2), encoding='utf-8')
        fixture = folder / 'fixture'
        shutil.copytree(HERE.parent / 'fixtures' / 'base', fixture)
        if EVALS[name]['fixture'] != 'base':
            shutil.copytree(HERE.parent / 'fixtures' / EVALS[name]['fixture'], fixture, dirs_exist_ok=True, ignore=shutil.ignore_patterns('REMOVE'))
        key = {}
        for i, r in enumerate(sel):
            letter = chr(ord('A') + i)
            base = ROOT / 'builds' / r['build']
            work = base / 'work'
            result = json.loads(read(base, 'result.json'))
            out = folder / letter
            shutil.copytree(work, out / 'project', ignore=shutil.ignore_patterns('.git', '.claude', '.agents'))
            (out / 'diff.txt').write_text(diff_text(work, result['baseline']), encoding='utf-8')
            (out / 'answer.txt').write_text(transcript.answer(base, r['model']), encoding='utf-8')
            key[letter] = r['build']
        (ROOT / 'keys').mkdir(exist_ok=True)
        (ROOT / 'keys' / f'{folder.name}.json').write_text(json.dumps(key, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
