"""Report which skill files each build's session actually read, from its session records.
A file counts as read, as a hint rather than proof, when its opening heading line appears in
the session's recorded tool traffic.
Usage: python skillreads.py <skill-dir> <build-dir> [...]"""
import json, pathlib, posixpath, re, sys

skill = pathlib.Path(sys.argv[1])
skill_name = next((l.split(':', 1)[1].strip().strip('"') for l in (skill / 'SKILL.md').read_text(encoding='utf-8').splitlines() if l.startswith('name:')), skill.name)
heads = {}
for f in [skill / 'SKILL.md', *sorted((skill / 'references').glob('*.md'))]:
    for line in f.read_text(encoding='utf-8').splitlines():
        if line.startswith('# '):
            heads[f.name] = line.strip()
            break


def texts(b):
    for f in [b / 'session.jsonl', *sorted((b / 'cfg').rglob('*.jsonl'))]:
        if not f.exists():
            continue
        for line in f.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                o = json.loads(line)
            except Exception:
                continue
            yield from strings(o)


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


for b in map(pathlib.Path, sys.argv[2:]):
    blob = '\n'.join(texts(b)).replace('\r', '')
    read = [n for n, h in heads.items() if re.search('^' + re.escape(h) + '$', blob, re.M)]
    # Every skill folder whose SKILL.md path appears in the session, other than the one under test,
    # and every absolute SKILL.md path outside the build's own working folder, same-name copies included.
    others = sorted(set(re.findall(r'skills[\\/]+([A-Za-z0-9_.-]+)[\\/]+SKILL\.md', blob)) - {skill.name, skill_name})
    own = str((b / 'work').resolve()).replace('\\', '/').lower().rstrip('/') + '/'
    outside = set()
    for hit in re.finditer(r'skills[\\/]+[A-Za-z0-9_.-]+[\\/]+SKILL\.md', blob):
        # The path starts at the nearest drive letter before the match on the same line and
        # within the same quotes, which keeps paths with spaces whole; otherwise at the start of
        # the token, where a leading slash marks an absolute path.
        window = blob[max(0, hit.start() - 300):hit.start()]
        line = window[window.rfind('\n') + 1:]
        quote = max(line.rfind(c) for c in '"\'`')
        if quote >= 0 and line[:quote].count(line[quote]) % 2 == 0:
            head = line[quote + 1:]  # inside quotes, the whole quoted text is the path
        else:
            drives = [m for m in re.finditer(r'[A-Za-z]:[\\/]', line) if not re.search('["\'`]', line[m.start():])]
            head = line[drives[-1].start():] if drives else re.split(r'[\s(=<>|"\'`]', line)[-1]
        path = (head + blob[hit.start():hit.end()]).replace('\\\\', '/').replace('\\', '/')
        if re.match(r'([A-Za-z]:/|/)', path):
            path = posixpath.normpath(path)  # resolve any .. that leaves the build folder
            if not (path.lower() + '/').startswith(own):
                outside.add(path)
    outside = sorted(outside)
    print(json.dumps({'build': b.name, 'files_read': len(read), 'read': read, 'other_skills': others, 'outside_paths': outside}))
