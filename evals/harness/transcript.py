"""Read a session record written by run.py: final answer, usage, what the session read, and a condensed transcript.

Claude Code writes stream-json events (assistant, user, result). Codex writes --json events
(item.completed with agent_message, command_execution, file_change, and others, then turn.completed).
"""
import json, pathlib, re

SKILL = 'web-repository-opinions'


def events(base):
    out = []
    p = pathlib.Path(base) / 'session.jsonl'
    if not p.is_file():
        return out
    for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def _returned(evs):
    """Every piece of content returned to the model: tool results, command output, and injected skill text."""
    for e in evs:
        if e.get('type') == 'user':
            content = e.get('message', {}).get('content', [])
            for c in content if isinstance(content, list) else [{'type': 'text', 'text': content}]:
                body = c.get('content') if c.get('type') == 'tool_result' else c.get('text')
                if isinstance(body, list):
                    body = ' '.join(b.get('text', '') for b in body if isinstance(b, dict))
                if body:
                    yield str(body)
        item = e.get('item') or {}
        if e.get('type') == 'item.completed' and item.get('type') == 'command_execution':
            yield item.get('aggregated_output') or ''


def _norm(text):
    return re.sub(r'\s+', ' ', text)


def _signatures(path):
    """The opening and closing lines of a file's body. Both come back to the model only when the whole file was read."""
    lines = [l.strip() for l in path.read_text(encoding='utf-8', errors='replace').splitlines()]
    body = [l for l in lines if l and not l.startswith(('#', '---', 'name:', 'description:', 'metadata:', 'author:', 'version:', '|', '```'))]
    return (_norm(body[0])[:80], _norm(body[-1])[-80:]) if body else None


def _installed(base):
    work = pathlib.Path(base) / 'work'
    for d in ('.claude', '.agents'):
        root = work / d / 'skills' / SKILL
        if root.is_dir():
            return root
    return None


def _coverage(base, files):
    """For each named file, 'full' when its opening and closing lines both came back to the model, 'partial' when only one did."""
    returned = [_norm(t) for t in _returned(events(base))]
    out = {}
    for name, path in files.items():
        sig = _signatures(path)
        if not sig:
            continue
        hits = [any(part in t for t in returned) for part in sig]
        if all(hits):
            out[name] = 'full'
        elif any(hits):
            out[name] = 'partial'
    return out


def skill_read(base):
    """True when the whole body of the installed SKILL.md came back to the model, not when a path or a fragment was."""
    root = _installed(base)
    return bool(root) and _coverage(base, {'SKILL': root / 'SKILL.md'}).get('SKILL') == 'full'


def references_read(base):
    """Reference names read in full, then those only partly read, each in name order."""
    root = _installed(base)
    if not root:
        return {'full': [], 'partial': []}
    cov = _coverage(base, {p.stem: p for p in sorted((root / 'references').glob('*.md'))})
    return {'full': [n for n, v in cov.items() if v == 'full'], 'partial': [n for n, v in cov.items() if v == 'partial']}


def finished(base, model):
    """True when the session's last terminal event is a success: a non-error result for Claude Code, a completed turn and no failure for Codex."""
    evs = events(base)
    if model == 'sol':
        terminal = [e for e in evs if e.get('type') in ('turn.completed', 'turn.failed')]
        return bool(terminal) and terminal[-1].get('type') == 'turn.completed'
    results = [e for e in evs if e.get('type') == 'result']
    return bool(results) and results[-1].get('subtype') == 'success' and not results[-1].get('is_error')


def served_model(base, model):
    """The model the CLI reports it used, which an alias does not pin."""
    for e in events(base):
        if e.get('type') == 'system' and e.get('subtype') == 'init' and e.get('model'):
            return e['model']
        if e.get('type') == 'assistant' and e.get('message', {}).get('model'):
            return e['message']['model']
        if e.get('model'):
            return e['model']
    return None


def answer(base, model):
    base = pathlib.Path(base)
    if model == 'sol':
        p = base / 'last-message.txt'
        return p.read_text(encoding='utf-8', errors='replace') if p.is_file() else ''
    for e in reversed(events(base)):
        if e.get('type') == 'result':
            return e.get('result') or ''
    return ''


def usage(base, model):
    evs = events(base)
    if model == 'sol':
        total = {}
        for e in evs:
            if e.get('type') == 'turn.completed':
                for k, v in (e.get('usage') or {}).items():
                    total[k] = total.get(k, 0) + (v or 0)
        return total
    for e in reversed(evs):
        if e.get('type') == 'result':
            u = e.get('usage') or {}
            return {k: u.get(k) for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')} | {
                'total_cost_usd': e.get('total_cost_usd'), 'num_turns': e.get('num_turns')}
    return {}


def _clip(text, n):
    text = text if isinstance(text, str) else json.dumps(text)
    return text if len(text) <= n else text[:n] + f' [... {len(text) - n} more characters]'


def condensed(base, model, clip=400):
    """The session in order: every message the model wrote in full, every tool call, and each tool result clipped."""
    lines = []
    for e in events(base):
        t = e.get('type')
        if t == 'assistant':
            for c in e.get('message', {}).get('content', []):
                if c.get('type') == 'text' and c.get('text', '').strip():
                    lines.append(f"**Assistant:** {c['text'].strip()}\n")
                elif c.get('type') == 'tool_use':
                    inp = c.get('input', {})
                    name = c.get('name')
                    # Content the session wrote is the work being graded, so it is shown as text, not as escaped JSON.
                    if name == 'Write':
                        lines.append(f"**Tool call `Write`:** `{inp.get('file_path', '')}`\n\n````text\n{_clip(inp.get('content', ''), 100000)}\n````\n")
                    elif name == 'Edit':
                        lines.append(f"**Tool call `Edit`:** `{inp.get('file_path', '')}`\n\nReplaced:\n\n````text\n{_clip(inp.get('old_string', ''), 20000)}\n````\n\nWith:\n\n````text\n{_clip(inp.get('new_string', ''), 100000)}\n````\n")
                    else:
                        lines.append(f"**Tool call `{name}`:** `{_clip(json.dumps(inp), 100000 if name == 'MultiEdit' else clip)}`\n")
        elif t == 'user':
            content = e.get('message', {}).get('content', [])
            for c in content if isinstance(content, list) else []:
                if c.get('type') == 'tool_result':
                    body = c.get('content')
                    if isinstance(body, list):
                        body = ' '.join(b.get('text', '') for b in body if isinstance(b, dict))
                    lines.append(f"> Result: {_clip(str(body or '').replace(chr(10), ' '), clip)}\n")
        elif t == 'item.completed':
            item = e.get('item') or {}
            k = item.get('type')
            if k == 'agent_message':
                lines.append(f"**Assistant:** {item.get('text', '').strip()}\n")
            elif k == 'command_execution':
                lines.append(f"**Shell:** `{_clip(item.get('command', ''), 2000)}`\n")
                lines.append(f"> Output: {_clip((item.get('aggregated_output') or '').replace(chr(10), ' '), clip)}\n")
            elif k == 'file_change':
                lines.append(f"**File change:** `{_clip(json.dumps(item.get('changes')), 2000)}`\n")
            elif k not in ('reasoning',):
                lines.append(f"**{k}:** `{_clip(json.dumps(item), clip)}`\n")
        elif t == 'result':
            lines.append(f"**Session ended:** {e.get('subtype')}, {e.get('num_turns')} turns, {e.get('duration_ms')} ms\n")
    return '\n'.join(lines)
