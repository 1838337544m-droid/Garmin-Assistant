# Copyright (c) 2026 1838337544m-droid. All rights reserved.
"""Local defaults; a repeated analysis never renews symptom timestamps."""
import json
from datetime import datetime, timezone, timedelta
from .research import atomic_json


def load_defaults(folder):
    path=folder/'dashboard-defaults.json'
    if not path.exists(): return {}
    try:
        value=json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value,dict) else {}
    except (ValueError,OSError):
        return {}


def save_defaults(folder,body,now=None):
    now=now or datetime.now(timezone.utc)
    previous=load_defaults(folder)
    subjective=body.get('subjective',{})
    swim=body.get('swimming_safety',{})
    stamps={}
    current={'subjective':{},'swimming_safety':{}}
    for group,values in (('subjective',subjective),('swimming_safety',swim)):
        for key,value in values.items():
            name=group+'.'+key
            prior=previous.get('field_recorded_at',{}).get(name,previous.get('state_recorded_at'))
            changed=key not in previous.get(group,{}) or previous[group][key]!=value or body.get('state_confirmed') is True
            stamp=now.isoformat() if changed else prior
            stamps[name]=stamp
            try:
                age=now-datetime.fromisoformat(stamp)
                if timedelta(0)<=age<=timedelta(hours=24): current[group][key]=value
            except (TypeError,ValueError):
                pass
    stamp=max((s for s in stamps.values() if s),default=None)
    value={'session_sport':body['session_sport'],'planned_km':body.get('planned_km'),
           'subjective':subjective,'swimming_safety':swim,'state_recorded_at':stamp,'field_recorded_at':stamps}
    atomic_json(folder/'dashboard-defaults.json',value)
    return value,current['subjective'],current['swimming_safety']
