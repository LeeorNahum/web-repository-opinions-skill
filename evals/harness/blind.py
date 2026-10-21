"""Copy finished builds into lettered folders for blind grading.

Usage: python blind.py <round> <eval-name> <label> [<label> ...]
Copies EVAL_ROOT/builds/<label>/work, without the installed skill, dependencies, or build
output, to EVAL_ROOT/judge/<round>-<eval-name>/<letter>/work. Beside it goes the builder's
final message with lines naming a skill and any absolute path removed. The letter-to-label
key goes to key.json, which graders and critics never read. Also writes rules.json, the
eval's assertions from evals.json, for the grader.
"""
import json, os, pathlib, random, re, shutil, sys

ROOT = pathlib.Path(os.environ['EVAL_ROOT']).resolve()
EVALS = pathlib.Path(__file__).resolve().parent.parent / 'evals.json'
rnd, name, labels = sys.argv[1], sys.argv[2], sys.argv[3:]
dest = ROOT / 'judge' / f'{rnd}-{name}'
dest.mkdir(parents=True, exist_ok=True)
random.seed(f'{rnd}-{name}')
random.shuffle(labels)
skip = shutil.ignore_patterns('.claude', '.agents', 'node_modules', '.next', 'dist', 'out', '.turbo', '.vercel', '.git')


def final_message(b):
    t = b / 'last-message.txt'
    if t.exists():
        return t.read_text(encoding='utf-8', errors='replace')
    text = ''
    for line in (b / 'session.jsonl').read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('type') == 'result' and o.get('result'):
            text = o['result']
    return text


key = {}
for i, label in enumerate(labels):
    letter = 'ABCDEFGH'[i]
    b = ROOT / 'builds' / label
    shutil.copytree(b / 'work', dest / letter / 'work', ignore=skip)
    msg = '\n'.join(l for l in final_message(b).splitlines() if not re.search(r'skill|opinion', l, re.I))
    msg = re.sub(r'[A-Za-z]:[\\/]\S*|/(?:home|Users|tmp)/\S*', '<path>', msg).replace(label, '<build>')
    (dest / letter / 'builder-final-message.txt').write_text(msg, encoding='utf-8')
    key[letter] = label
(dest / 'key.json').write_text(json.dumps(key, indent=2), encoding='utf-8')

ev = next(e for e in json.loads(EVALS.read_text(encoding='utf-8'))['evals'] if e['name'] == name)
rules = [{'id': a['id'], 'reference': a['reference'], 'kind': a['kind'], 'rule': a['text'], 'check': a['check']} for a in ev['assertions']]
(dest / 'rules.json').write_text(json.dumps(rules, indent=1), encoding='utf-8')
(dest / 'prompt.txt').write_text(ev['prompt'], encoding='utf-8')
print(dest, sorted(key), len(rules), 'assertions')
