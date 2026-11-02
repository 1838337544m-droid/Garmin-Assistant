"""Hash build outputs for GitHub Releases; does not include user state."""
import hashlib
import tomllib
from pathlib import Path

root=Path(__file__).resolve().parents[1]
folder=root/'dist'
version=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
files=[folder/f'garmin_assistant_api-{version}-py3-none-any.whl',
       folder/f'garmin_assistant_api-{version}.tar.gz',
       folder/f'Garmin-Assistant-{version}-Windows-Installer.zip']
if not all(p.is_file() for p in files):raise SystemExit('Expected matching wheel, source archive and Windows installer')
(folder/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files),encoding='utf-8')
print('Created SHA256SUMS.txt for wheel, source archive and Windows installer')
