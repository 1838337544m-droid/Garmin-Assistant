"""Audit only git-visible release files. Never prints matched secret content."""
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def audit():
    output=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT)
    names=sorted(set(n for n in output.decode().split('\0') if n))
    forbidden={'API.txt','api-key','settings.json','menu-preferences.json','research.json','verification-report.json'}
    patterns=[re.compile(r'\bGCDC_[A-Za-z0-9_./+=-]{30,}'),
              re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{35,})'),
              re.compile(r'\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'),
              re.compile(r'(?:C:[/\\]Users[/\\]User[/\\]|D:[/\\]WpSystem[/\\])',re.I)]
    issues=[]
    for name in names:
        p=Path(name)
        if p.name in forbidden or p.suffix in ('.sqlite3','.db','.log') or any(part in ('.venv','reports','exports','private-data') for part in p.parts):
            issues.append((name,'private/generated file'));continue
        raw=(ROOT/p).read_bytes()
        try:text=raw.decode('utf-8-sig')
        except UnicodeDecodeError:
            issues.append((name,'unexpected binary file'));continue
        if any(pattern.search(text) for pattern in patterns):issues.append((name,'credential/private-path pattern'))
    version=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    init=(ROOT/'src/garmin_assistant/__init__.py').read_text(encoding='utf-8')
    if f'__version__ = "{version}"' not in init:issues.append(('pyproject.toml','version mismatch'))
    if not names:issues.append(('.','no release files'))
    if issues:
        for name,reason in issues:print(f'FAIL {name}: {reason}')
        return 1
    print(f'PASS {len(names)} git-visible text files; version {version}; no private file/known credential patterns found.')
    print('Pattern scanning is an extra check, not a guarantee against every possible secret.')
    return 0


if __name__=='__main__':sys.exit(audit())
