"""Unblind a graded eval and compare the two snapshots assertion by assertion.

Usage: python compare.py <round>-<eval-name> <old-arm> <new-arm> [changed assertion ids...]
Arms are read from each build's label, <round>-<eval>-<arm>-<model>. The assertion set is the
one in rules.json. Refuses an incomplete comparison: an ungraded build, a missing Opus or Sol
build in either snapshot, an assertion with no grade, or a new build with no critic verdict.
Prints pass counts, then the lists the pass bar reads: changed assertions some new build did
not pass (not applicable counts as not passed), assertions every old build passed that some new
build did not, and assertions the new snapshot fixed. Every blocking critic finding against a
new build needs an entry in critic-answers.json, {"<label>": {"<finding text>": "withdrawn" or
"in old builds too"}}, recording how the critic's answer round settled it.
Exits 0 only when all of that holds.
"""
import json, os, pathlib, sys

ROOT = pathlib.Path(os.environ['EVAL_ROOT']).resolve()
j = ROOT / 'judge' / sys.argv[1]
old, new, changed = sys.argv[2], sys.argv[3], sys.argv[4:]
key = json.loads((j / 'key.json').read_text())
rules = [r['id'] for r in json.loads((j / 'rules.json').read_text(encoding='utf-8'))]
grading = json.loads((j / 'grading.json').read_text(encoding='utf-8'))['builds']
critic = {}
for f in j.glob('critic-*.json'):
    if f.name == 'critic-answers.json':
        continue
    critic.update(json.loads(f.read_text(encoding='utf-8'))['builds'])
answers = json.loads((j / 'critic-answers.json').read_text(encoding='utf-8')) if (j / 'critic-answers.json').exists() else {}
arm = {L: lab.split('-')[-2] for L, lab in key.items()}
olds = [L for L in key if arm[L] == old]
news = [L for L in key if arm[L] == new]
models = lambda Ls: {key[L].split('-')[-1] for L in Ls}
problems = []
if not {'opus', 'sol'} <= models(olds) or not {'opus', 'sol'} <= models(news):
    problems.append(f'each snapshot needs Opus and Sol builds: old {sorted(models(olds))}, new {sorted(models(news))}')
for L in olds + news:
    if L not in grading:
        problems.append(f'{key[L]} is not graded')
    else:
        missing = [rid for rid in rules if rid not in grading[L]['rules']]
        if missing:
            problems.append(f'{key[L]} has no grade for {missing}')
for L in news:
    c = critic.get(L, {})
    if c.get('verdict') not in ('pass', 'fail'):
        problems.append(f'no critic verdict for {key[L]}')
    elif c['verdict'] == 'fail' and not c.get('blocking'):
        problems.append(f'the critic failed {key[L]} without naming a blocking finding')
if problems:
    sys.exit('Incomplete comparison: ' + '; '.join(problems))

v = lambda L, rid: grading[L]['rules'][rid]['v']
for L in sorted(olds + news, key=lambda x: key[x]):
    vs = [v(L, rid) for rid in rules]
    print(f"{key[L]}: {vs.count('pass')} pass, {vs.count('fail')} fail, {vs.count('na')} na, critic {critic.get(L, {}).get('verdict')}")
unproven = [rid for rid in changed if any(rid not in rules or v(L, rid) != 'pass' for L in news)]
regressed = [rid for rid in rules if all(v(L, rid) == 'pass' for L in olds) and any(v(L, rid) != 'pass' for L in news)]
fixed = [rid for rid in rules if any(v(L, rid) == 'fail' for L in olds) and all(v(L, rid) == 'pass' for L in news)]
unanswered = [(key[L], b) for L in news for b in critic[L].get('blocking', []) if answers.get(key[L], {}).get(b) not in ('withdrawn', 'in old builds too')]
print('changed assertions not passed by every new build:', unproven)
print('regressed from old:', regressed)
print('fixed by new:', fixed)
for label, b in unanswered:
    print(f'unsettled critic blocking finding on {label}: {b}')
sys.exit(1 if unproven or regressed or unanswered else 0)
