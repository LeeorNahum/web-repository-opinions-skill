"""Install, build, lint, and typecheck a finished build, and record its layout.

Usage: python prepare.py <build-dir>
Reads <build-dir>/work, writes <build-dir>/prepare.json. Each step runs with a timeout and
records its exit code and the tail of its output. Skill folders the harness installed
(.claude, .agents) are excluded from the layout record.
"""
import json, os, pathlib, subprocess, sys, shutil

base = pathlib.Path(sys.argv[1])
work = base / 'work'
SKIP = {'node_modules', '.git', '.claude', '.agents', '.next', 'dist', 'out', 'build', '.turbo', '.vercel', 'coverage', '_generated'}


def tree(root, depth=4):
    lines = []
    def walk(d, level):
        if level > depth:
            return
        for p in sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if p.name in SKIP:
                continue
            lines.append('  ' * level + p.name + ('/' if p.is_dir() else ''))
            if p.is_dir():
                walk(p, level + 1)
    walk(root, 0)
    return lines


def run(cmd, cwd, timeout=600):
    shell = os.name == 'nt'
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=shell,
                           env={**os.environ, 'CI': '1', 'NEXT_TELEMETRY_DISABLED': '1'}, encoding='utf-8', errors='replace')
        return {'cmd': cmd, 'cwd': str(cwd.relative_to(work)), 'exit': r.returncode, 'tail': (r.stdout + r.stderr)[-2500:]}
    except subprocess.TimeoutExpired:
        return {'cmd': cmd, 'cwd': str(cwd.relative_to(work)), 'exit': 'timeout', 'tail': ''}


result = {'tree': tree(work), 'steps': [], 'env_files': [], 'packages': []}
for p in work.rglob('*'):
    if any(part in SKIP for part in p.relative_to(work).parts):
        continue
    if p.is_file() and p.name.startswith('.env'):
        result['env_files'].append(str(p.relative_to(work)))
    if p.is_file() and p.name == 'package.json':
        try:
            pk = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        result['packages'].append({'path': str(p.relative_to(work)), 'name': pk.get('name'), 'scripts': pk.get('scripts', {}),
                                   'dependencies': sorted(pk.get('dependencies', {})), 'devDependencies': sorted(pk.get('devDependencies', {})),
                                   'packageManager': pk.get('packageManager')})

CHECKS = ('typecheck', 'check-types', 'type-check', 'lint', 'build', 'test')


def manager(d):
    pk = json.loads((d / 'package.json').read_text(encoding='utf-8')) if (d / 'package.json').exists() else {}
    if (d / 'bun.lockb').exists() or (d / 'bun.lock').exists():
        return 'bun'
    if (d / 'yarn.lock').exists():
        return 'yarn'
    if (d / 'pnpm-lock.yaml').exists() or (d / 'pnpm-workspace.yaml').exists() or str(pk.get('packageManager', '')).startswith('pnpm'):
        return 'pnpm'
    return 'npm'


INSTALL = {'pnpm': 'pnpm install --frozen-lockfile=false', 'npm': 'npm install --no-audit --no-fund', 'yarn': 'yarn install', 'bun': 'bun install'}
nested = [work / pathlib.Path(p['path']).parent for p in result['packages'] if p['path'] != 'package.json']
if (work / 'package.json').exists():
    pm = manager(work)
    result['package_manager'] = pm
    result['steps'].append(run(INSTALL[pm], work, 900))
    root_scripts = json.loads((work / 'package.json').read_text(encoding='utf-8')).get('scripts', {})
    for name in CHECKS:
        if name in root_scripts:
            result['steps'].append(run(f'{pm} run {name}', work, 900))
    roots = []
elif nested:
    # No root manifest: each package is installed on its own.
    pm = None
    result['package_manager'] = 'per-package'
    roots = nested
else:
    result['package_manager'] = None
    roots = []
# Every package also runs its own checks, so a root script that covers only some packages
# cannot leave another unchecked.
for d in nested:
    scripts = json.loads((d / 'package.json').read_text(encoding='utf-8')).get('scripts', {})
    dpm = pm or manager(d)
    if d in roots:
        result['steps'].append(run(INSTALL[dpm], d, 900))
    for name in CHECKS:
        if name in scripts:
            result['steps'].append(run(f'{dpm} run {name}', d, 900))
if result['package_manager'] and not any(any(n in s['cmd'] for n in ('typecheck', 'check-types', 'type-check')) for s in result['steps']) and (work / 'tsconfig.json').exists():
    result['steps'].append(run('npx --no-install tsc --noEmit -p .', work, 600))

(base / 'prepare.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'build': base.name, 'pm': result['package_manager'], 'steps': [(s['cmd'], s['exit']) for s in result['steps']], 'env_files': result['env_files']}))
