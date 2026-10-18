"""Record a graded round into the eval area, so its results and transcripts can be committed.

Usage: python record.py <jobs file> <round> <destination folder> <skill commit>
Environment: EVAL_ROOT.

Run it after grade.py and after the critics have written their critic-*.json files. For every
session it writes <destination>/<eval>/<arm>-<model>/ holding answer.md (the final reply),
changes.diff (every change the session made), transcript.md (the condensed session), and
grading.json (each assertion's verdict, its evidence, and which critic gave it). It also writes
<destination>/summary.json and <destination>/SUMMARY.md with one row per assertion. Credentials
and the raw session records stay in EVAL_ROOT.
"""
import json, os, pathlib, re, shutil, subprocess, sys
from datetime import datetime

import transcript
from compare import critic_votes
from grade import diff_text, read
from run import digest

HERE = pathlib.Path(__file__).resolve().parent
EVALS = {e['name']: e for e in json.loads((HERE.parent / 'evals.json').read_text(encoding='utf-8'))['evals']}
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()
HOME = pathlib.Path.home()
FILE_LIMIT = 300_000
ROUND_LIMIT = 8_000_000
SECRET_NAME = re.compile(r'KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH', re.I)
SECRET_SHAPE = re.compile(r'sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}'
                          r'|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|xox[abpr]-[A-Za-z0-9-]{10,}')


def secret_values():
    """Values that must never be recorded: exported secrets and every string in the CLIs' credential files."""
    values = {v for k, v in os.environ.items() if SECRET_NAME.search(k) and len(v) >= 8}
    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and len(x) >= 16:
            values.add(x)
    for f in (HOME / '.claude/.credentials.json', HOME / '.codex/auth.json'):
        try:
            walk(json.loads(f.read_text(encoding='utf-8')))
        except (OSError, ValueError):
            pass
    return sorted(values, key=len, reverse=True)


def scrub(text, secrets, hits):
    """Redact secrets and credential-shaped strings, replace the owner's home and run paths, and cap the size."""
    for v in secrets:
        if v in text:
            hits.append('value')
            text = text.replace(v, '[REDACTED]')
    text, n = SECRET_SHAPE.subn('[REDACTED]', text)
    hits += ['shape'] * n
    for path, label in ((str(ROOT), '<run>'), (str(HOME), '<home>')):
        slash = path.replace('\\', '/')
        for form in {path, slash, path.replace('\\', '\\\\'), re.sub(r'^([A-Za-z]):', lambda m: '/' + m.group(1).lower(), slash)}:
            text = re.sub(re.escape(form), label, text, flags=re.I)
    if len(text) > FILE_LIMIT:
        text = text[:FILE_LIMIT] + f'\n\n[Recorded copy cut at {FILE_LIMIT} characters. The full record stays in the run folder.]\n'
    return text


def inputs(base, result):
    """What the session was given: the installed skill's hash, the Git tree of the starting project, and the harness's own hashes when run.py recorded them."""
    work = base / 'work'
    root = next((work / d / 'skills' for d in ('.claude', '.agents') if (work / d / 'skills').is_dir()), None)
    first = subprocess.run(['git', 'rev-list', '--max-parents=0', 'HEAD'], cwd=work, capture_output=True, text=True).stdout.strip()
    tree = subprocess.run(['git', 'rev-parse', f'{first}^{{tree}}'], cwd=work, capture_output=True, text=True).stdout.strip() if first else None
    return {'skill': digest(root) if root else None, 'starting_tree': tree, **{k: v for k, v in (result.get('digests') or {}).items() if k != 'skill'}}


def main():
    jobs_file, rnd, final, commit = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]), sys.argv[4]
    # Build in the run folder and move into the eval area only when the round passes its size limit.
    dest = ROOT / 'recording' / final.name
    if dest.exists():
        shutil.rmtree(dest)
    labels = [l.split()[0] for l in pathlib.Path(jobs_file).read_text().splitlines() if l.strip() and not l.startswith('#')]
    labels = [l for l in labels if l.startswith(f'{rnd}-')]
    grades = {r['build']: r for r in json.loads((ROOT / f'grades-{rnd}.json').read_text(encoding='utf-8'))}
    votes, blocking = critic_votes(rnd)
    secrets, hits = secret_values(), []
    sessions, unfinished = [], []
    for label in labels:
        g = grades[label]
        if not g['completed']:
            failed = [e.get('error', {}).get('message', '') for e in transcript.events(ROOT / 'builds' / label) if e.get('type') == 'turn.failed']
            unfinished.append({'session': label, 'reason': scrub(failed[-1], [], []) if failed else ('no finished session' if (ROOT / 'builds' / label).exists() else 'not run yet')})
            continue
        name, arm, model = g['eval'], g['arm'], g['model']
        base = ROOT / 'builds' / label
        result = json.loads(read(base, 'result.json') or '{}')
        out = dest / name / f'{arm}-{model}'
        out.mkdir(parents=True, exist_ok=True)
        (out / 'answer.md').write_text(scrub(transcript.answer(base, model), secrets, hits), encoding='utf-8')
        if result.get('baseline'):
            (out / 'changes.diff').write_text(scrub(diff_text(base / 'work', result['baseline']), secrets, hits), encoding='utf-8')
        (out / 'transcript.md').write_text(scrub(transcript.condensed(base, model), secrets, hits), encoding='utf-8')
        verdicts = {a['id']: {'v': ('pass' if g['checks'].get(a['id']) else 'fail'), 'by': 'check'} for a in EVALS[name]['assertions'] if a['kind'] == 'check'}
        for aid, vs in votes.get(label, {}).items():
            verdicts[aid] = {'v': 'pass' if all(ok for _, ok, _ in vs) else 'fail', 'votes': [{'critic': c, 'v': 'pass' if ok else 'fail', 'e': scrub(e, secrets, hits)} for c, ok, e in vs]}
        notes = {'blocking': [f'[{c}] {scrub(f, secrets, hits)}' + (f' ({st})' if st else '') for c, f, st in blocking.get(label, [])], 'minor': []}
        row = {'session': label, 'eval': name, 'arm': arm, 'model': model, 'model_id': result.get('model_id'), 'effort': result.get('effort'),
               'served_model': result.get('served_model') or transcript.served_model(base, model),
               'requested_model': result.get('requested_model') or result.get('model_id'),
               'cli': result.get('cli'), 'inputs': inputs(base, result),
               'completed': g['completed'], 'timed_out': g['timed_out'], 'seconds': g['seconds'], 'skill_read': g['skill_read'],
               'references_read': g['references_read'], 'usage': g['usage'], 'changed': g['changed'], 'assertions': verdicts, **notes}
        (out / 'grading.json').write_text(json.dumps(row, indent=2), encoding='utf-8')
        sessions.append(row)
    total = sum(p.stat().st_size for p in dest.rglob('*') if p.is_file())
    if total > ROUND_LIMIT:
        sys.exit(f'The round holds {total} bytes, above the {ROUND_LIMIT} byte limit. It stays in {dest} and nothing was written to {final}.')
    same_family = sorted({s['session'] for s in sessions if s['model'] == 'opus' and any(
        v.get('critic') != 'codex' for a in s['assertions'].values() for v in a.get('votes', []))})
    shutil.copyfile(jobs_file, dest / 'jobs.txt')
    summary = {'round': rnd, 'recorded': datetime.now().astimezone().isoformat(timespec='seconds'), 'skill_commit': commit,
               'same_family_graded': same_family, 'unfinished': unfinished, 'sessions': sessions}
    (dest / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    cols = [(s['arm'], s['model']) for s in sessions]
    cols = sorted(set(cols), key=cols.index)
    note = (['Sessions in the round that did not finish, and are not recorded:', ''] + [f"- `{u['session']}`: {u['reason']}" for u in unfinished] + ['']) if unfinished else []
    note += [f'Claude critics graded {len(same_family)} Claude-built sessions because Codex was unreachable. They need a Codex verdict before any comparison.', ''] if same_family else []
    lines = [f'# Round {rnd}', '', f'Skill commit `{commit}`. One session per eval and column. P is a pass, F a fail, and a dash a missing verdict.', '', *note,
             '| Assertion | ' + ' | '.join(f'{a} {m}' for a, m in cols) + ' |', '| --- |' + ' :---: |' * len(cols)]
    by = {(s['eval'], s['arm'], s['model']): s for s in sessions}
    for name, spec in EVALS.items():
        if not any(s['eval'] == name for s in sessions):
            continue
        for a in spec['assertions']:
            cells = []
            for arm, model in cols:
                v = by.get((name, arm, model), {}).get('assertions', {}).get(a['id'], {}).get('v')
                cells.append({'pass': 'P', 'fail': 'F'}.get(v, '-'))
            lines.append(f"| `{a['id']}` | " + ' | '.join(cells) + ' |')
    lines += ['', '| Session | Finished | Skill read | References read | Seconds |', '| --- | :---: | :---: | ---: | ---: |']
    lines += [f"| `{s['session']}` | {'yes' if s['completed'] else 'no'} | {'yes' if s['skill_read'] else 'no'} | {len(s['references_read']['full'])} | {s['seconds']} |" for s in sessions]
    (dest / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if final.exists():
        shutil.rmtree(final)
    final.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(dest), str(final))
    print(f'recorded {len(sessions)} sessions in {final}, {total} bytes, {len(hits)} redactions')


if __name__ == '__main__':
    main()
