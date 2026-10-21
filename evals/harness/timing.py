"""Tokens and duration per build, from its session output.
Usage: python timing.py <build-dir> [...]"""
import json, pathlib, sys
for b in map(pathlib.Path, sys.argv[1:]):
    r = json.loads((b / 'result.json').read_text())
    tokens = None
    for line in (b / 'session.jsonl').read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('type') == 'result' and 'usage' in o:
            u = o['usage']
            tokens = sum(u.get(k, 0) or 0 for k in ('input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'))
        if o.get('type') == 'turn.completed' and 'usage' in o:
            u = o['usage']
            tokens = (tokens or 0) + sum(v for k, v in u.items() if isinstance(v, int) and k in ('input_tokens', 'output_tokens'))  # input_tokens already includes the cached part
    print(json.dumps({'build': b.name, 'exit': r['exit'], 'seconds': r['seconds'], 'tokens': tokens}))
