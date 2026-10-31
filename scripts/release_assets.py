"""Hash build outputs for GitHub Releases; does not include user state."""
import hashlib
from pathlib import Path

folder=Path(__file__).resolve().parents[1]/'dist'
files=sorted([*folder.glob('*.whl'),*folder.glob('*.tar.gz')])
if len(files)!=2:raise SystemExit('Expected exactly one wheel and one source archive')
(folder/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files),encoding='utf-8')
print('Created SHA256SUMS.txt for wheel/source archive')
