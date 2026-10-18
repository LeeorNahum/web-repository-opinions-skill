"""Decide whether a changed skill passes, from the check grades and the critics' verdicts.

Usage: python compare.py <jobs file> <round>
Environment: EVAL_ROOT.

Reads grades-<round>.json from grade.py, and from every judge/<round>-<eval> folder its key in keys/<round>-<eval>.json,
every critic-*.json, and critic-answers.json, which records how each blocking finding against a
new session settled: {"<letter>": {"<finding text>": "withdrawn|held"}}.

Prints a per-assertion table and the failures, and exits 0 only when:
- the round holds every eval with both arms and both models, and every job has a finished session that read the skill,
- every session has a verdict on exactly its eval's assertions,
- every new session passes every assertion of every pressure case,
- no assertion an old session passed fails in the paired new session, and
- every blocking finding against a new session is recorded as withdrawn.
"""
import json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
EVALS = {e['name']: e for e in json.loads((HERE.parent / 'evals.json').read_text(encoding='utf-8'))['evals']}
ROOT = pathlib.Path(os.environ.get('EVAL_ROOT', '')).resolve()


def critic_votes(rnd):
    """Every critic's verdicts by session label: {label: {assertion id: [(critic, pass?, evidence)]}}, and blocking findings."""
    votes, blocking = {}, {}
    for name in EVALS:
        folder = ROOT / 'judge' / f'{rnd}-{name}'
        if not folder.is_dir():
            continue
        key = json.loads((ROOT / 'keys' / f'{folder.name}.json').read_text(encoding='utf-8'))
        answers = json.loads((folder / 'critic-answers.json').read_text(encoding='utf-8')) if (folder / 'critic-answers.json').is_file() else {}
        for critic in sorted(folder.glob('critic-*.json')):
            if critic.name == 'critic-answers.json':
                continue
            provider = critic.stem.split('-', 1)[1]
            for letter, body in json.loads(critic.read_text(encoding='utf-8')).items():
                label = key.get(letter)
                if not label:
                    continue
                for aid, v in body.get('semantic', {}).items():
                    votes.setdefault(label, {}).setdefault(aid, []).append((provider, v.get('v') == 'pass' and bool(v.get('e')), v.get('e', '')))
                for finding in body.get('blocking', []):
                    blocking.setdefault(label, []).append((provider, finding, answers.get(letter, {}).get(finding)))
    return votes, blocking


def verdicts_for(rnd, grades):
    """Each session's verdict per assertion. A semantic assertion passes only when every critic that graded it passed it with evidence."""
    votes, blocking = critic_votes(rnd)
    verdict = {label: dict(g['checks']) for label, g in grades.items() if g['completed']}
    for label, by_id in votes.items():
        if label in verdict:
            for aid, vs in by_id.items():
                verdict[label][aid] = all(ok for _, ok, _ in vs)
    return verdict, {label: [(f, s) for _, f, s in fs] for label, fs in blocking.items()}


def main():
    jobs_file, rnd = sys.argv[1], sys.argv[2]
    labels = [l.split()[0] for l in pathlib.Path(jobs_file).read_text().splitlines() if l.strip() and not l.startswith('#')]
    labels = [l for l in labels if l.startswith(f'{rnd}-')]
    grades = {r['build']: r for r in json.loads((ROOT / f'grades-{rnd}.json').read_text(encoding='utf-8'))}
    problems = []
    expected = {f'{rnd}-{name}-{arm}-{model}' for name in EVALS for arm in ('old', 'new') for model in ('opus', 'sol')}
    for missing in sorted(expected - set(labels)):
        problems.append(f'{missing}: not in the jobs file')
    for label in labels:
        g = grades.get(label)
        if not g or not g['completed']:
            problems.append(f'{label}: no finished session')
        elif not g['skill_read']:
            problems.append(f'{label}: the session never opened the skill (setup failure)')
    for name in EVALS:
        for m in ('opus', 'sol'):
            pair = [grades.get(f'{rnd}-{name}-{arm}-{m}') for arm in ('old', 'new')]
            if all(pair) and pair[0].get('served_model') != pair[1].get('served_model'):
                problems.append(f'{rnd}-{name} {m}: arms ran on different models ({pair[0].get("served_model")} and {pair[1].get("served_model")}), so the pair is not comparable')
            if all(pair):
                results = [json.loads((ROOT / 'builds' / g['build'] / 'result.json').read_text(encoding='utf-8')) for g in pair]
                if len({r.get('requested_model') or r.get('model_id') for r in results}) > 1:
                    problems.append(f'{rnd}-{name} {m}: arms requested different models, so the pair is not comparable')
                inputs = [r.get('digests') or {} for r in results]
                for k in ('fixture', 'base_fixture', 'case'):
                    if inputs[0].get(k) != inputs[1].get(k):
                        problems.append(f'{rnd}-{name} {m}: arms saw different {k} inputs, so the pair is not comparable')
    verdict, blocking = verdicts_for(rnd, grades)
    votes, _ = critic_votes(rnd)
    for label, by_id in votes.items():
        if label.endswith('-opus') and any(c != 'codex' for vs in by_id.values() for c, _, _ in vs):
            problems.append(f'{label}: graded by a Claude critic, so it needs a Codex verdict before any comparison')
    for label, v in verdict.items():
        name = label[len(rnd) + 1:].rsplit('-', 2)[0]
        ids = {a['id'] for a in EVALS[name]['assertions']}
        if set(v) != ids:
            problems.append(f'{label}: verdicts for {sorted(set(v) ^ ids)} missing or unexpected')
    for name, spec in EVALS.items():
        for a in spec['assertions']:
            olds = [verdict.get(f'{rnd}-{name}-old-{m}', {}).get(a['id']) for m in ('opus', 'sol')]
            news = [verdict.get(f'{rnd}-{name}-new-{m}', {}).get(a['id']) for m in ('opus', 'sol')]
            print(f"{a['id']:48} old {''.join('P' if x else '.' for x in olds)}  new {''.join('P' if x else '.' for x in news)}")
            for m, x, old in zip(('opus', 'sol'), news, olds):
                # A restraint or control assertion the old arm already failed does not block, since no revision caused it.
                if x is False and (spec.get('role', 'pressure') == 'pressure' or old):
                    problems.append(f"{rnd}-{name}-new-{m}: fails {a['id']}" + (' (passed by every old session)' if all(olds) else ''))
    for label, findings in blocking.items():
        if '-new-' in label:
            for finding, settled in findings:
                if settled != 'withdrawn':
                    problems.append(f'{label}: blocking finding {settled or "unanswered"}: {finding[:160]}')
    for p in problems:
        print('FAIL', p)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
