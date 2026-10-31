"""Portable per-user settings; nothing private is stored in the source tree."""
import json
import os
import sys
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .research import atomic_json


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    timezone: str = 'UTC'
    goal_distance_km: float = 10
    goal_minutes: float = 60
    language: str | None = None

    @property
    def key_file(self):
        return Path(os.environ.get('GARMIN_ASSISTANT_KEY_FILE',str(self.data_dir/'api-key'))).expanduser().resolve()

    @property
    def goal(self):
        return {'distance_km':self.goal_distance_km,'minutes':self.goal_minutes}


def load_settings():
    override=os.environ.get('GARMIN_ASSISTANT_HOME')
    if override:folder=Path(override).expanduser()
    elif sys.platform=='win32':folder=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'GarminAssistantAPI'
    elif sys.platform=='darwin':folder=Path.home()/'Library/Application Support/GarminAssistantAPI'
    else:folder=Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))/'garmin-assistant-api'
    folder.mkdir(parents=True,exist_ok=True)
    if os.name!='nt':folder.chmod(0o700)
    folder=folder.resolve()
    path=folder/'settings.json'
    raw=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if raw.get('schema_version',1)!=1:raise ValueError('Unsupported settings schema; use a compatible release')
    settings=Settings(folder,timezone=raw.get('timezone','UTC'),goal_distance_km=raw.get('goal_distance_km',10),goal_minutes=raw.get('goal_minutes',60),language=raw.get('language'))
    validate(settings)
    return settings


def validate(settings):
    if settings.language not in (None,'zh','en'):raise ValueError('Language must be zh or en')
    try:ZoneInfo(settings.timezone)
    except (ZoneInfoNotFoundError,ValueError,TypeError):raise ValueError('Invalid IANA timezone') from None
    for name,value,limit in [('distance',settings.goal_distance_km,200),('minutes',settings.goal_minutes,1440)]:
        if type(value) not in (int,float) or not 0<value<=limit:raise ValueError(f'Invalid goal {name}')


def save_settings(settings,**changes):
    unknown=set(changes)-{'timezone','goal_distance_km','goal_minutes','language'}
    if unknown:raise ValueError('Unknown settings field')
    updated=replace(settings,**changes);validate(updated)
    atomic_json(settings.data_dir/'settings.json',{'schema_version':1,'timezone':updated.timezone,
        'goal_distance_km':updated.goal_distance_km,'goal_minutes':updated.goal_minutes,'language':updated.language})
    return updated


def local_today():
    return datetime.now(ZoneInfo(load_settings().timezone)).date().isoformat()


def save_api_key(settings,key):
    if not key or any(c.isspace() for c in key):raise ValueError('Expected one nonempty API key')
    settings.key_file.parent.mkdir(parents=True,exist_ok=True)
    settings.key_file.write_text(key.strip(),encoding='utf-8')
    if os.name!='nt':settings.key_file.chmod(0o600)
