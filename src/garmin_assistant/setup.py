"""Local setup operations. Never put API key values in a client configuration."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tomllib
import tempfile
from pathlib import Path
from uuid import uuid4

from .config import save_api_key, save_settings, validate


def client_entry(settings):
    return {'command':sys.executable,'args':['-m','garmin_assistant','serve'],
            'env':{'GARMIN_ASSISTANT_HOME':str(settings.data_dir),
                   'GARMIN_ASSISTANT_KEY_FILE':str(settings.key_file)}}


def backup_file(path):
    if not path.exists():return None
    backup=path.with_name(path.name+'.'+uuid4().hex+'.bak')
    shutil.copy2(path,backup)
    if os.name!='nt':backup.chmod(0o600)
    return backup


def connect_claude(path,settings,replace=False):
    path=Path(path).expanduser()
    raw=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    if not isinstance(raw,dict) or not isinstance(raw.get('mcpServers',{}),dict):
        raise ValueError('Invalid client configuration')
    servers=raw.setdefault('mcpServers',{})
    if 'garmin-assistant' in servers and not replace:raise ValueError('Garmin entry already exists')
    mode=stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    backup=backup_file(path)
    servers['garmin-assistant']=client_entry(settings)
    path.parent.mkdir(parents=True,exist_ok=True)
    path=path.parent.resolve()/path.name
    fd,tmp_name=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
    tmp=Path(tmp_name)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            # mkstemp starts private; preserve the original config's access mode.
            os.chmod(tmp,mode)
            json.dump(raw,stream,ensure_ascii=False,indent=2)
        tmp.replace(path)
    finally:tmp.unlink(missing_ok=True)
    return backup


def connect_codex(settings,replace=False):
    executable=shutil.which('codex')
    if not executable:raise ValueError('Codex CLI is not installed or is not on PATH')
    path=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
    raw=tomllib.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if 'garmin-assistant' in raw.get('mcp_servers',{}) and not replace:
        raise ValueError('Garmin entry already exists')
    path.parent.mkdir(parents=True,exist_ok=True)
    backup=backup_file(path)
    entry=client_entry(settings)
    argv=[executable,'mcp','add','garmin-assistant']
    for name,value in entry['env'].items():argv+=['--env',f'{name}={value}']
    argv+=['--',entry['command'],*entry['args']]
    completed=subprocess.run(argv,capture_output=True,timeout=60)
    if completed.returncode:raise ValueError('Codex configuration failed; backup was retained')
    return backup


def configure(settings,language,timezone,distance,minutes,key):
    from dataclasses import replace
    changes=dict(language=language,timezone=timezone.strip(),goal_distance_km=float(distance),goal_minutes=float(minutes))
    validate(replace(settings,**changes))
    key=key.strip()
    if key and any(c.isspace() for c in key):raise ValueError('Expected one API key')
    if not key and not settings.key_file.is_file() and not os.environ.get('GARMIN_PERSONAL_API_KEY'):
        raise ValueError('Enter a Garmin Personal API key')
    if key:save_api_key(settings,key)
    return save_settings(settings,**changes)


def default_claude_path():
    if sys.platform=='win32':return Path(os.environ.get('APPDATA',str(Path.home()/'AppData/Roaming')))/'Claude/claude_desktop_config.json'
    if sys.platform=='darwin':return Path.home()/'Library/Application Support/Claude/claude_desktop_config.json'
    return Path.home()/'.config/Claude/claude_desktop_config.json'
